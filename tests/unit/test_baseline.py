"""Unit tests for the gate baseline (scaffold_generator.baseline)."""

from pathlib import Path

import pytest

from scaffold_generator.baseline import BaselineRunner, GateOutcome, Outcome
from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.gates import Gate
from scaffold_generator.runner import CommandResult, FakeCommandRunner

PROJECT_DIR = Path("project")


def _agents_md(*rendered_gates: str) -> str:
    body = "\n".join(rendered_gates)
    return f"# Agent Workflow\n\n## Quality gates\n\n**api**\n{body}\n\n## Repository map\n"


def _runner(
    agents_md: str, commands: FakeCommandRunner | None = None, timeout_s: float = 5.0
) -> BaselineRunner:
    return BaselineRunner(
        fs=InMemoryFileSystem(files={"project/AGENTS.md": agents_md}),
        runner=commands if commands is not None else FakeCommandRunner(),
        timeout_s=timeout_s,
    )


class TestGates:
    def test_declared_gates_are_read_from_the_scaffold(self) -> None:
        runner = _runner(_agents_md("- test — `pytest`"))

        assert runner.gates(PROJECT_DIR) == [Gate(name="test", run="pytest")]

    def test_directory_without_agents_md_is_an_error(self) -> None:
        runner = BaselineRunner(fs=InMemoryFileSystem(files={}), runner=FakeCommandRunner())

        with pytest.raises(ValueError, match="no AGENTS.md"):
            runner.gates(PROJECT_DIR)

    def test_agents_md_without_a_gates_section_is_an_error(self) -> None:
        runner = _runner("# Agent Workflow\n\n## Repository map\n")

        with pytest.raises(ValueError, match="Quality gates"):
            runner.gates(PROJECT_DIR)


class TestRun:
    def test_exit_zero_is_a_pass(self) -> None:
        commands = FakeCommandRunner(results={"pytest": CommandResult(exit_code=0, output="")})

        outcomes = _runner(_agents_md("- test — `pytest`"), commands).run(PROJECT_DIR)

        assert outcomes[0].outcome is Outcome.PASSED

    def test_non_zero_exit_is_a_failure_carrying_the_summary_line(self) -> None:
        # Runners open with a banner and close with the verdict, so the last
        # non-blank line is the useful one.
        commands = FakeCommandRunner(
            results={
                "pytest": CommandResult(
                    exit_code=5, output="==== test session starts ====\n\nno tests ran\n"
                )
            }
        )

        outcomes = _runner(_agents_md("- test — `pytest`"), commands).run(PROJECT_DIR)

        assert outcomes[0].outcome is Outcome.FAILED
        assert outcomes[0].detail == "exit 5: no tests ran"

    def test_failure_without_output_still_reports_the_exit_code(self) -> None:
        commands = FakeCommandRunner(results={"pytest": CommandResult(exit_code=2, output="  \n")})

        outcomes = _runner(_agents_md("- test — `pytest`"), commands).run(PROJECT_DIR)

        assert outcomes[0].detail == "exit 2"

    def test_missing_executable_is_unavailable(self) -> None:
        commands = FakeCommandRunner(
            results={"mypy": CommandResult(exit_code=127, output="", not_found=True)}
        )

        outcomes = _runner(_agents_md("- types — `mypy .`"), commands).run(PROJECT_DIR)

        assert outcomes[0].outcome is Outcome.UNAVAILABLE
        assert "mypy" in outcomes[0].detail

    def test_timeout_is_reported_with_the_limit(self) -> None:
        commands = FakeCommandRunner(
            results={"sleep": CommandResult(exit_code=124, output="", timed_out=True)}
        )

        outcomes = _runner(_agents_md("- slow — `sleep 999`"), commands, timeout_s=5.0).run(
            PROJECT_DIR
        )

        assert outcomes[0].outcome is Outcome.TIMED_OUT
        assert "5s" in outcomes[0].detail

    def test_command_is_run_as_an_argument_vector_in_the_scaffold(self) -> None:
        commands = FakeCommandRunner()

        _runner(_agents_md("- lint — `ruff check .`"), commands).run(PROJECT_DIR)

        assert commands.calls == [(["ruff", "check", "."], PROJECT_DIR)]

    def test_every_gate_runs_even_when_an_earlier_one_fails(self) -> None:
        commands = FakeCommandRunner(default=CommandResult(exit_code=1, output="nope"))

        outcomes = _runner(
            _agents_md("- lint — `ruff check .`", "- test — `pytest`"), commands
        ).run(PROJECT_DIR)

        assert [o.gate.name for o in outcomes] == ["lint", "test"]


class TestShellSyntaxIsNeverExecuted:
    @pytest.mark.parametrize(
        "command",
        [
            "ruff check . && pytest",
            "pytest || true",
            "make build; make test",
            "cat x | grep y",
            "pytest > out.txt",
            "echo `whoami`",
            "echo $(whoami)",
        ],
    )
    def test_shell_syntax_is_skipped_and_nothing_runs(self, command: str) -> None:
        commands = FakeCommandRunner()

        outcomes = _runner(_agents_md(f"- gate — `{command}`"), commands).run(PROJECT_DIR)

        assert outcomes[0].outcome is Outcome.SKIPPED
        assert "shell" in outcomes[0].detail
        assert commands.calls == []

    def test_unbalanced_quotes_are_skipped_not_executed(self) -> None:
        commands = FakeCommandRunner()

        outcomes = _runner(_agents_md('- gate — `pytest "unclosed`'), commands).run(PROJECT_DIR)

        assert outcomes[0].outcome is Outcome.SKIPPED
        assert commands.calls == []


class TestGateOutcome:
    def test_outcome_carries_the_gate_it_describes(self) -> None:
        outcome = GateOutcome(Gate(name="test", run="pytest"), Outcome.PASSED)

        assert outcome.gate.name == "test"
        assert outcome.detail == ""
