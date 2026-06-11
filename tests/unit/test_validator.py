"""Unit tests for the contract validator (scaffold_generator.validator)."""

from pathlib import Path

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.validator import AGENTS_MAX_LINES, REQUIRED_FILES, ContractValidator

PROJECT_DIR = Path("project")


def _scaffold_files() -> dict[str, str]:
    """File contents for a minimal valid scaffold under PROJECT_DIR."""
    files = {f"project/{required}": "# placeholder\n" for required in REQUIRED_FILES}
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
