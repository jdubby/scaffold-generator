"""Unit tests for the command boundary (scaffold_generator.runner)."""

from pathlib import Path

from scaffold_generator.runner import CommandResult, FakeCommandRunner


class TestFakeCommandRunner:
    def test_scripted_result_is_returned_for_a_known_command(self) -> None:
        runner = FakeCommandRunner(results={"pytest": CommandResult(exit_code=0, output="ok")})

        assert runner.run(["pytest"], Path("project"), 1.0).exit_code == 0

    def test_unscripted_command_falls_back_to_the_default(self) -> None:
        runner = FakeCommandRunner(default=CommandResult(exit_code=3, output="boom"))

        assert runner.run(["ruff", "check", "."], Path("project"), 1.0).exit_code == 3

    def test_calls_are_recorded_with_their_working_directory(self) -> None:
        runner = FakeCommandRunner()

        runner.run(["pytest", "-q"], Path("project"), 1.0)

        assert runner.calls == [(["pytest", "-q"], Path("project"))]
