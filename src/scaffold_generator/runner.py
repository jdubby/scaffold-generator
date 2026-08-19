"""Command boundary — the single substitutable interface for running a command.

Mirrors the ``FileSystem`` boundary: production code uses ``RealCommandRunner``,
module unit tests substitute ``FakeCommandRunner``, so the no-subprocess rule in
AGENTS.md holds for everything below the acceptance layer.
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

DEFAULT_TIMEOUT_S = 300.0

# Captured output is for diagnosis, not archival; keep reports readable.
_MAX_OUTPUT_CHARS = 2000


@dataclass(frozen=True)
class CommandResult:
    """The outcome of running one command."""

    exit_code: int
    output: str
    timed_out: bool = False
    not_found: bool = False


class CommandRunner(Protocol):
    """Runs an argument vector in a working directory. Never invokes a shell."""

    def run(self, args: list[str], cwd: Path, timeout_s: float) -> CommandResult: ...


class RealCommandRunner:
    """CommandRunner backed by subprocess, with no shell and a hard timeout."""

    def run(self, args: list[str], cwd: Path, timeout_s: float) -> CommandResult:
        try:
            completed = subprocess.run(  # noqa: S603 - argument vector, shell=False
                args,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                shell=False,
                check=False,
            )
        except FileNotFoundError as exc:
            return CommandResult(exit_code=127, output=str(exc), not_found=True)
        except subprocess.TimeoutExpired:
            return CommandResult(
                exit_code=124, output=f"timed out after {timeout_s:g}s", timed_out=True
            )
        output = (completed.stdout + completed.stderr).strip()
        return CommandResult(exit_code=completed.returncode, output=output[:_MAX_OUTPUT_CHARS])


@dataclass
class FakeCommandRunner:
    """CommandRunner that returns scripted results and records what it was asked to run.

    Results are keyed by the command's first argument; anything unscripted returns
    the ``default`` result.
    """

    results: dict[str, CommandResult] = field(default_factory=dict)
    default: CommandResult = CommandResult(exit_code=1, output="")
    calls: list[tuple[list[str], Path]] = field(default_factory=list)

    def run(self, args: list[str], cwd: Path, timeout_s: float) -> CommandResult:
        self.calls.append((args, cwd))
        return self.results.get(args[0], self.default)
