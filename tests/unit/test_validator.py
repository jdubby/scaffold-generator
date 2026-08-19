"""Unit tests for the contract validator (scaffold_generator.validator)."""

from pathlib import Path

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.validator import (
    AGENTS_MAX_LINES,
    REQUIRED_DIRS,
    REQUIRED_FILES,
    ContractValidator,
)

PROJECT_DIR = Path("project")


def _scaffold_files() -> dict[str, str]:
    """File contents for a minimal valid scaffold under PROJECT_DIR."""
    files = {f"project/{required}": "# placeholder\n" for required in REQUIRED_FILES}
    files.update({f"project/{required}/.gitkeep": "" for required in REQUIRED_DIRS})
    files["project/AGENTS.md"] = "# Agent Workflow\n"  # must stay within the line limit
    return files


def _validate(files: dict[str, str]) -> list[str]:
    errors = ContractValidator(fs=InMemoryFileSystem(files=files)).validate(PROJECT_DIR)
    return [e.message for e in errors]


class TestContractValidator:
    def test_validate_passes_for_complete_scaffold(self) -> None:
        assert _validate(_scaffold_files()) == []

    def test_validate_fails_when_required_file_missing(self) -> None:
        files = _scaffold_files()
        del files["project/docs/EVALUATOR.md"]

        assert any("EVALUATOR.md" in message for message in _validate(files))

    def test_validate_fails_when_workflow_directory_missing(self) -> None:
        files = _scaffold_files()
        del files["project/tests/features/.gitkeep"]
        del files["project/docs/exec-plans/active/.gitkeep"]

        messages = _validate(files)
        assert any("tests/features" in message for message in messages)
        assert any("docs/exec-plans/active" in message for message in messages)

    def test_validate_fails_when_agents_md_exceeds_line_limit(self) -> None:
        files = _scaffold_files()
        files["project/AGENTS.md"] = "\n".join(f"line {i}" for i in range(AGENTS_MAX_LINES + 1))

        assert any("AGENTS.md" in m and "lines" in m for m in _validate(files))

    def test_validate_fails_when_unresolved_marker_in_md_file(self) -> None:
        files = _scaffold_files()
        files["project/ARCHITECTURE.md"] = "# Arch\n\n<!-- ASSEMBLE:arch -->\n"

        assert any("ARCHITECTURE.md" in message for message in _validate(files))

    def test_validate_fails_when_unresolved_marker_in_yml_file(self) -> None:
        files = _scaffold_files()
        files["project/.github/workflows/ci.yml"] = "<!-- ASSEMBLE:ci-jobs -->\n"

        assert any("ci.yml" in message for message in _validate(files))

    def test_validate_fails_when_ci_yml_missing(self) -> None:
        files = _scaffold_files()
        del files["project/ci.yml"]

        assert any("ci.yml" in message for message in _validate(files))

    def test_validate_fails_when_unresolved_yaml_marker_in_yml_file(self) -> None:
        files = _scaffold_files()
        files["project/ci.yml"] = "jobs:\n# ASSEMBLE:ci\n"

        assert any("ci.yml" in m and "marker" in m.lower() for m in _validate(files))

    def test_validate_returns_all_errors_not_just_first(self) -> None:
        files = _scaffold_files()
        del files["project/docs/EVALUATOR.md"]
        del files["project/ARCHITECTURE.md"]

        assert len(_validate(files)) >= 2


def _with_ci(ci_yml: str) -> list[str]:
    """Validate an otherwise-complete scaffold whose ci.yml is *ci_yml*."""
    files = _scaffold_files()
    files["project/ci.yml"] = ci_yml
    return _validate(files)


def _ci_with_run(run_value: str) -> str:
    """A ci.yml with one job whose single step runs *run_value* (a YAML scalar)."""
    return (
        "name: ci\n"
        "jobs:\n"
        "  stub-checks:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Integration tests\n"
        f"        run: {run_value}\n"
    )


def _ci_with_run_block(lines: list[str]) -> str:
    """A ci.yml with one job whose single step runs a multi-line block of *lines*."""
    body = "\n".join(f"          {line}" for line in lines)
    return (
        "name: ci\n"
        "jobs:\n"
        "  stub-checks:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Integration tests\n"
        "        run: |\n"
        f"{body}\n"
    )


class TestUnfillableGates:
    """AC-8: a gate that always exits 0 asserts nothing and must be reported."""

    def test_gate_running_only_echo_is_reported(self) -> None:
        messages = _with_ci(_ci_with_run('echo "Replace with the real command."'))

        assert len(messages) == 1
        assert "cannot fail" in messages[0]
        assert "stub-checks" in messages[0]
        assert "Integration tests" in messages[0]

    def test_gate_combining_echo_with_a_real_command_is_allowed(self) -> None:
        assert _with_ci(_ci_with_run('echo "running" && pytest')) == []

    def test_quoted_true_is_reported(self) -> None:
        # Bare `run: true` is a YAML boolean, not a command — an invalid workflow
        # rather than a no-op gate. These are the forms that actually occur.
        assert len(_with_ci(_ci_with_run('"true"'))) == 1

    def test_true_in_a_block_scalar_is_reported(self) -> None:
        assert len(_with_ci(_ci_with_run_block(["true"]))) == 1

    def test_colon_is_reported(self) -> None:
        assert len(_with_ci(_ci_with_run(":"))) == 1

    def test_multiline_gate_of_only_no_ops_is_reported(self) -> None:
        messages = _with_ci(_ci_with_run_block(['echo "step one"', 'echo "step two"']))

        assert len(messages) == 1

    def test_multiline_gate_with_one_real_command_is_allowed(self) -> None:
        assert _with_ci(_ci_with_run_block(['echo "starting"', "pytest -q"])) == []

    def test_comment_only_gate_is_not_reported(self) -> None:
        assert _with_ci(_ci_with_run_block(["# TODO: wire the migration command"])) == []

    def test_job_without_steps_is_not_reported(self) -> None:
        assert _with_ci("name: ci\njobs:\n  stub-checks:\n    run: quality gates\n") == []

    def test_boolean_run_value_is_not_reported(self) -> None:
        # `run: true` is a YAML boolean, so there is no command to judge. An
        # invalid workflow is a different defect from a gate that cannot fail.
        assert _with_ci(_ci_with_run("true")) == []

    def test_jobs_as_a_list_is_not_reported(self) -> None:
        assert _with_ci("name: ci\njobs:\n  - stub-checks\n") == []

    def test_step_that_is_not_a_mapping_is_not_reported(self) -> None:
        assert _with_ci("name: ci\njobs:\n  stub-checks:\n    steps:\n      - pytest\n") == []

    def test_ci_yml_without_jobs_is_not_reported(self) -> None:
        assert _with_ci("name: ci\non: push\n") == []

    def test_unparseable_ci_yml_is_reported(self) -> None:
        messages = _with_ci("jobs: [unclosed\n")

        assert len(messages) == 1
        assert "parse" in messages[0].lower()

    def test_every_offending_step_is_reported(self) -> None:
        ci_yml = (
            "name: ci\n"
            "jobs:\n"
            "  stub-checks:\n"
            "    steps:\n"
            "      - name: Migrations\n"
            '        run: echo "todo"\n'
            "      - name: Integration tests\n"
            '        run: echo "todo"\n'
            "      - name: Unit tests\n"
            "        run: pytest\n"
        )

        assert len(_with_ci(ci_yml)) == 2
