"""Executable bindings for tests/features/gate_baseline.feature.

These scenarios drive the real CommandRunner: the point of a baseline is that
something actually ran, so the acceptance layer must not substitute a fake.
"""

from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from pytest_bdd import given, parsers, scenarios, then, when

from scaffold_generator.cli import main

scenarios("gate_baseline.feature")

REPO_ROOT = Path(__file__).parent.parent.parent

# The file a "writer" gate creates, used to prove --dry-run executed nothing.
TRACE_FILENAME = "gate-ran.txt"


@dataclass
class BaselineRun:
    """State shared across the steps of one scenario."""

    project_dir: Path
    gates: list[tuple[str, str]] = field(default_factory=list)
    result: Result | None = None


@pytest.fixture
def run(tmp_path: Path) -> BaselineRun:
    return BaselineRun(project_dir=tmp_path / "project")


def _result(run: BaselineRun) -> Result:
    assert run.result is not None, "Scenario has no CLI invocation result yet."
    return run.result


def _write_scaffold(run: BaselineRun) -> None:
    """Write the minimum a scaffold needs for the baseline to read its gates."""
    lines = "\n".join(f"- {name} — `{command}`" for name, command in run.gates)
    run.project_dir.mkdir(parents=True, exist_ok=True)
    (run.project_dir / "AGENTS.md").write_text(
        f"# Agent Workflow\n\n## Quality gates\n\n**stack**\n{lines}\n\n## Repository map\n"
    )


def _gate_row(run: BaselineRun, name: str) -> str:
    for line in _result(run).output.splitlines():
        if line.strip().startswith(f"{name} "):
            return line
    raise AssertionError(f"No row for gate {name!r} in:\n{_result(run).output}")


# --- Given ---------------------------------------------------------------


@given("a scaffold generated from the bundled library")
def generated_scaffold(run: BaselineRun, tmp_path: Path) -> None:
    spec_path = tmp_path / "stack.yml"
    spec_path.write_text(
        yaml.safe_dump({"name": "baselined", "platform": "backend", "backend": ["fastapi"]})
    )
    result = CliRunner().invoke(
        main,
        [
            str(spec_path),
            "--output",
            str(run.project_dir),
            "--components-dir",
            str(REPO_ROOT / "components"),
            "--core-dir",
            str(REPO_ROOT / "core"),
        ],
    )
    assert result.exit_code == 0, result.output


@given(parsers.parse('a scaffold declaring a gate "{name}" running "{command}"'))
def scaffold_with_gate(run: BaselineRun, name: str, command: str) -> None:
    run.gates.append((name, command))
    _write_scaffold(run)


@given(parsers.parse('a scaffold gate "{name}" running "{command}"'))
def scaffold_also_with_gate(run: BaselineRun, name: str, command: str) -> None:
    run.gates.append((name, command))
    _write_scaffold(run)


@given(parsers.parse('a scaffold declaring a gate "{name}" that would create a file when run'))
def scaffold_with_writer_gate(run: BaselineRun, name: str) -> None:
    run.gates.append((name, f"python3 -c \"open('{TRACE_FILENAME}', 'w')\""))
    _write_scaffold(run)


@given("a directory that is not a generated scaffold")
def not_a_scaffold(run: BaselineRun) -> None:
    run.project_dir.mkdir(parents=True)


# --- When ----------------------------------------------------------------


@when("the user runs the baseline")
def run_baseline(run: BaselineRun) -> None:
    run.result = CliRunner().invoke(main, ["--baseline", str(run.project_dir)])


@when("the user runs the baseline with --dry-run")
def run_baseline_dry(run: BaselineRun) -> None:
    run.result = CliRunner().invoke(main, ["--baseline", str(run.project_dir), "--dry-run"])


# --- Then ----------------------------------------------------------------


@then("the generator exits successfully")
def exits_successfully(run: BaselineRun) -> None:
    result = _result(run)
    assert result.exit_code == 0, result.output


@then("the generator exits with a non-zero code")
def exits_nonzero(run: BaselineRun) -> None:
    assert _result(run).exit_code != 0


@then(parsers.parse('the baseline lists the gate command "{command}"'))
def baseline_lists_command(run: BaselineRun, command: str) -> None:
    assert command in _result(run).output


@then("the baseline reports that nothing ran")
def baseline_reports_nothing_ran(run: BaselineRun) -> None:
    assert "Nothing ran." in _result(run).output


@then(parsers.parse('the gate "{name}" is reported as "{outcome}"'))
def gate_reported_as(run: BaselineRun, name: str, outcome: str) -> None:
    assert outcome in _gate_row(run, name)


@then("the baseline explains that a passing gate deserves scrutiny")
def baseline_explains_passes(run: BaselineRun) -> None:
    assert "asserting nothing" in _result(run).output


@then("the skip reason mentions shell syntax")
def skip_reason_mentions_shell(run: BaselineRun) -> None:
    assert "shell" in _result(run).output


@then("the gate left no trace in the scaffold")
def gate_left_no_trace(run: BaselineRun) -> None:
    assert not (run.project_dir / TRACE_FILENAME).exists()


@then("the gate left its trace in the scaffold")
def gate_left_trace(run: BaselineRun) -> None:
    assert (run.project_dir / TRACE_FILENAME).is_file()


@then(parsers.parse('an error mentions "{text}"'))
def error_mentions(run: BaselineRun, text: str) -> None:
    assert text in _result(run).stderr
