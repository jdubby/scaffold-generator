"""Unit tests for the scaffold writer (scaffold_generator.writer)."""

from pathlib import Path

import pytest

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.writer import ScaffoldWriter

OUTPUT_DIR = Path("my-project")


class TestScaffoldWriter:
    def test_write_creates_output_directory(self) -> None:
        fs = InMemoryFileSystem()
        ScaffoldWriter(fs).write(OUTPUT_DIR, {"AGENTS.md": "# Agent Workflow\n"})

        assert fs.is_dir(OUTPUT_DIR)

    def test_write_creates_files_with_correct_content(self) -> None:
        fs = InMemoryFileSystem()
        content = "# Agent Workflow\n\nSome content.\n"
        ScaffoldWriter(fs).write(OUTPUT_DIR, {"AGENTS.md": content})

        assert fs.read_text(OUTPUT_DIR / "AGENTS.md") == content

    def test_write_creates_nested_directory_structure(self) -> None:
        fs = InMemoryFileSystem()
        ScaffoldWriter(fs).write(OUTPUT_DIR, {"docs/EVALUATOR.md": "# Evaluation Protocol\n"})

        assert fs.is_file(OUTPUT_DIR / "docs" / "EVALUATOR.md")

    def test_write_multiple_files_in_one_call(self) -> None:
        fs = InMemoryFileSystem()
        files = {
            "AGENTS.md": "# Agents\n",
            "docs/EVALUATOR.md": "# Evaluator\n",
            "docs/design-docs/core-beliefs.md": "# Core Beliefs\n",
        }
        ScaffoldWriter(fs).write(OUTPUT_DIR, files)

        assert fs.is_file(OUTPUT_DIR / "AGENTS.md")
        assert fs.is_file(OUTPUT_DIR / "docs" / "EVALUATOR.md")
        assert fs.is_file(OUTPUT_DIR / "docs" / "design-docs" / "core-beliefs.md")

    def test_write_raises_file_exists_error_when_output_dir_exists(self) -> None:
        fs = InMemoryFileSystem(dirs=("my-project",))

        with pytest.raises(FileExistsError, match="my-project"):
            ScaffoldWriter(fs).write(OUTPUT_DIR, {"AGENTS.md": "# Agents\n"})


class TestScaffoldWriterPreflight:
    """Output paths are validated as writable before generation, per docs/SECURITY.md."""

    def test_preflight_accepts_creatable_nested_path(self) -> None:
        fs = InMemoryFileSystem()

        ScaffoldWriter(fs).preflight(Path("new/nested/my-project"))

    def test_preflight_raises_when_output_dir_exists(self) -> None:
        fs = InMemoryFileSystem(dirs=("my-project",))

        with pytest.raises(FileExistsError, match="my-project"):
            ScaffoldWriter(fs).preflight(OUTPUT_DIR)

    def test_preflight_raises_permission_error_for_unwritable_ancestor(self) -> None:
        fs = InMemoryFileSystem(dirs=("locked",), unwritable_dirs=("locked",))

        with pytest.raises(PermissionError, match="not writable"):
            ScaffoldWriter(fs).preflight(Path("locked/deep/my-project"))
