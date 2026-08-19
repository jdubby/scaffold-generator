"""Contract validator — checks a generated scaffold satisfies structural requirements."""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

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

# Directories the workflow documents refer to; they must exist even when empty.
REQUIRED_DIRS = (
    "tests/features",
    "docs/exec-plans/active",
)

_UNRESOLVED_MARKERS = ("<!-- ASSEMBLE:", "# ASSEMBLE:")
_CHECKED_SUFFIXES = {".md", ".yml"}

# Shell commands that succeed without asserting anything. A gate built only from
# these always exits 0, so it reports success for work nobody has done.
_NO_OP_COMMANDS = frozenset({"echo", "true", ":"})
_COMMAND_SEPARATORS = re.compile(r"&&|\|\||;")


def _mapping_items(document: object, key: str) -> list[tuple[str, object]]:
    """The ``key`` mapping of *document* as (name, value) pairs, or empty if absent."""
    if not isinstance(document, dict):
        return []
    section = document.get(key)
    if not isinstance(section, dict):
        return []
    return list(section.items())


def _is_no_op(command: str) -> bool:
    """True when *command* is one of the shell no-ops that always succeed."""
    stripped = command.strip()
    if not stripped:
        return True
    return stripped.split(maxsplit=1)[0] in _NO_OP_COMMANDS


def _runs_only_no_ops(run_block: str) -> bool:
    """True when every command in a step's ``run`` block is a no-op.

    A block with no commands at all (empty, or only comments) is not reported:
    an unwritten step is a different shape from a step that pretends to work.
    """
    found_command = False
    for raw_line in run_block.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        for segment in _COMMAND_SEPARATORS.split(line):
            if not segment.strip():
                continue
            found_command = True
            if not _is_no_op(segment):
                return False
    return found_command


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
        errors.extend(self._check_required_dirs(project_dir))
        errors.extend(self._check_agents_line_count(project_dir))
        errors.extend(self._check_unresolved_markers(project_dir))
        errors.extend(self._check_unfillable_gates(project_dir))
        return errors

    def _check_required_files(self, project_dir: Path) -> list[ValidationError]:
        errors = []
        for required in REQUIRED_FILES:
            if not self._fs.is_file(project_dir / required):
                errors.append(ValidationError(f"Required file missing: {required}"))
        return errors

    def _check_required_dirs(self, project_dir: Path) -> list[ValidationError]:
        errors = []
        for required in REQUIRED_DIRS:
            if not self._fs.is_dir(project_dir / required):
                errors.append(ValidationError(f"Required directory missing: {required}"))
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

    def _check_unfillable_gates(self, project_dir: Path) -> list[ValidationError]:
        """Report ci.yml gate steps that cannot fail.

        An unwired gate is legitimate in a fresh scaffold; an unwired gate that
        *passes* is not. Unparseable YAML is reported rather than skipped —
        skipping it would make this check one that cannot fail.
        """
        ci_yml = project_dir / "ci.yml"
        if not self._fs.is_file(ci_yml):
            return []
        try:
            document = yaml.safe_load(self._fs.read_text(ci_yml))
        except yaml.YAMLError as exc:
            reason = str(exc).replace("\n", " ")
            return [ValidationError(f"ci.yml could not be parsed as YAML: {reason}")]

        errors = []
        for job_id, job in _mapping_items(document, "jobs"):
            steps = job.get("steps") if isinstance(job, dict) else None
            if not isinstance(steps, list):
                continue
            for position, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    continue
                run_block = step.get("run")
                if not isinstance(run_block, str) or not _runs_only_no_ops(run_block):
                    continue
                label = step.get("name") or f"step {position}"
                errors.append(
                    ValidationError(
                        f"Gate cannot fail in ci.yml: job '{job_id}', step '{label}' runs "
                        "only no-op commands. A gate that always exits 0 reports success "
                        "for work nobody has done — use 'exit 1' with a TODO comment until "
                        "the real command is wired."
                    )
                )
        return errors
