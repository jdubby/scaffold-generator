"""Gate baseline — runs a generated scaffold's declared gates and classifies each result.

A gate that fails against a fresh scaffold is working: it demands behavior nobody
has built yet. A gate that *passes* against a scaffold with no implementation in it
is asserting nothing, and will go on asserting nothing. This module produces the
evidence; it does not judge.
"""

import shlex
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from scaffold_generator.filesystem import FileSystem, RealFileSystem
from scaffold_generator.gates import Gate, parse_rendered
from scaffold_generator.runner import DEFAULT_TIMEOUT_S, CommandRunner, RealCommandRunner

AGENTS_FILENAME = "AGENTS.md"

# A scaffold is content that may have come from anywhere, so none of it is handed to
# a shell. A command carrying shell syntax cannot run as an argument vector and is
# reported instead of executed.
_SHELL_SYNTAX = ("&&", "||", ";", "|", ">", "<", "`", "$(")


class Outcome(StrEnum):
    """What happened when a gate was run."""

    PASSED = "passed"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    TIMED_OUT = "timed out"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class GateOutcome:
    """One gate and what running it produced."""

    gate: Gate
    outcome: Outcome
    detail: str = ""


class BaselineRunner:
    """Reads a scaffold's declared gates and runs them in that scaffold."""

    def __init__(
        self,
        fs: FileSystem | None = None,
        runner: CommandRunner | None = None,
        timeout_s: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()
        self._runner: CommandRunner = runner if runner is not None else RealCommandRunner()
        self._timeout_s = timeout_s

    def gates(self, project_dir: Path) -> list[Gate]:
        """The gates *project_dir* declares.

        Raises:
            ValueError: if the directory has no AGENTS.md, or one with no gates section.
        """
        agents_md = project_dir / AGENTS_FILENAME
        if not self._fs.is_file(agents_md):
            raise ValueError(f"not a generated scaffold: no {AGENTS_FILENAME} in {project_dir}")
        try:
            return parse_rendered(self._fs.read_text(agents_md))
        except ValueError as exc:
            raise ValueError(f"{agents_md}: {exc}") from exc

    def run(self, project_dir: Path) -> list[GateOutcome]:
        """Run every declared gate in *project_dir* and classify each result."""
        return [self._run_gate(gate, project_dir) for gate in self.gates(project_dir)]

    def _run_gate(self, gate: Gate, project_dir: Path) -> GateOutcome:
        found = next((syntax for syntax in _SHELL_SYNTAX if syntax in gate.run), None)
        if found is not None:
            return GateOutcome(
                gate,
                Outcome.SKIPPED,
                f"contains shell syntax {found!r}; baseline never invokes a shell",
            )
        try:
            args = shlex.split(gate.run)
        except ValueError as exc:
            return GateOutcome(gate, Outcome.SKIPPED, f"command could not be parsed: {exc}")
        if not args:
            return GateOutcome(gate, Outcome.SKIPPED, "command is empty")

        result = self._runner.run(args, project_dir, self._timeout_s)
        if result.not_found:
            return GateOutcome(gate, Outcome.UNAVAILABLE, f"{args[0]!r} is not installed")
        if result.timed_out:
            return GateOutcome(gate, Outcome.TIMED_OUT, f"exceeded {self._timeout_s:g}s")
        if result.exit_code == 0:
            return GateOutcome(gate, Outcome.PASSED, "exit 0")
        return GateOutcome(gate, Outcome.FAILED, _summary_line(result.output, result.exit_code))


def _summary_line(output: str, exit_code: int) -> str:
    """A one-line reason for a failing gate, for the results table.

    The *last* non-blank line, not the first: test runners and linters open with a
    banner and close with the verdict ("no tests ran", "Found 3 errors").
    """
    for line in reversed(output.splitlines()):
        if line.strip():
            return f"exit {exit_code}: {line.strip()}"
    return f"exit {exit_code}"
