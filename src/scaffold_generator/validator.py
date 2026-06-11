"""Contract validator — checks a generated scaffold satisfies structural requirements."""

from dataclasses import dataclass
from pathlib import Path

from scaffold_generator.filesystem import FileSystem, RealFileSystem

AGENTS_MAX_LINES = 120

REQUIRED_FILES = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    "README.md",
    "ci.yml",
    "docs/EVALUATOR.md",
    "docs/DESIGN.md",
    "docs/QUALITY_SCORE.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/design-docs/core-beliefs.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/product-specs/index.md",
)

_UNRESOLVED_MARKERS = ("<!-- ASSEMBLE:", "# ASSEMBLE:")
_CHECKED_SUFFIXES = {".md", ".yml"}


@dataclass
class ValidationError:
    """A single contract violation found in the generated scaffold."""

    message: str


class ContractValidator:
    """Validates a generated scaffold directory against the structural contract."""

    def __init__(self, fs: FileSystem | None = None) -> None:
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()

    def validate(self, project_dir: Path) -> list[ValidationError]:
        """Return all contract violations found in *project_dir*.

        An empty list means the scaffold passed all checks.
        """
        errors: list[ValidationError] = []
        errors.extend(self._check_required_files(project_dir))
        errors.extend(self._check_agents_line_count(project_dir))
        errors.extend(self._check_unresolved_markers(project_dir))
        return errors

    def _check_required_files(self, project_dir: Path) -> list[ValidationError]:
        errors = []
        for required in REQUIRED_FILES:
            if not self._fs.is_file(project_dir / required):
                errors.append(ValidationError(f"Required file missing: {required}"))
        return errors

    def _check_agents_line_count(self, project_dir: Path) -> list[ValidationError]:
        agents_md = project_dir / "AGENTS.md"
        if not self._fs.is_file(agents_md):
            return []
        line_count = len(self._fs.read_text(agents_md).splitlines())
        if line_count > AGENTS_MAX_LINES:
            return [
                ValidationError(
                    f"AGENTS.md has {line_count} lines (limit: {AGENTS_MAX_LINES}). "
                    "Keep AGENTS.md as a navigator pointing to docs/, not a manual."
                )
            ]
        return []

    def _check_unresolved_markers(self, project_dir: Path) -> list[ValidationError]:
        errors = []
        for path in self._fs.walk_files(project_dir):
            if path.suffix not in _CHECKED_SUFFIXES:
                continue
            text = self._fs.read_text(path)
            if any(marker in text for marker in _UNRESOLVED_MARKERS):
                relative = path.relative_to(project_dir)
                errors.append(ValidationError(f"Unresolved assembly marker in: {relative}"))
        return errors
