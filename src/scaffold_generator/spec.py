"""Spec loader — reads a YAML stack spec file and validates it against a JSON schema."""

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as SchemaValidationError
from jsonschema.exceptions import best_match

from scaffold_generator.filesystem import FileSystem, RealFileSystem

VALID_PLATFORMS = {"mobile", "web", "hybrid", "backend"}

# Plain slug: no path separators, no leading dot. Spec values are matched against
# the module library by name and must never be usable as raw filesystem paths.
_SLUG_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]*$"

_COMPONENT_LIST: dict[str, Any] = {
    "type": ["array", "null"],
    "items": {"type": "string", "pattern": _SLUG_PATTERN},
}

SPEC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["name", "platform"],
    "properties": {
        "name": {"type": "string", "pattern": _SLUG_PATTERN},
        "platform": {"enum": sorted(VALID_PLATFORMS)},
        "frontend": _COMPONENT_LIST,
        "backend": _COMPONENT_LIST,
        "database": _COMPONENT_LIST,
        "inference": _COMPONENT_LIST,
    },
}


@dataclass
class StackSpec:
    """Validated, typed representation of a stack spec YAML file."""

    name: str
    platform: str
    frontend: list[str] = field(default_factory=list)
    backend: list[str] = field(default_factory=list)
    database: list[str] = field(default_factory=list)
    inference: list[str] = field(default_factory=list)


def _render_path(path: Sequence[str | int]) -> str:
    """Render a schema error path like ['backend', 0] as ``backend[0]``."""
    rendered = ""
    for part in path:
        if isinstance(part, int):
            rendered += f"[{part}]"
        elif rendered:
            rendered += f".{part}"
        else:
            rendered = str(part)
    return rendered or "spec"


def _format_schema_error(error: SchemaValidationError) -> str:
    """Translate a schema error into a message naming the field with a remediation hint."""
    if error.validator == "required":
        missing = error.message.split("'")[1]
        return f"Spec is missing required field: '{missing}'. Add it to the spec file."
    field_path = _render_path(list(error.absolute_path))
    if field_path == "platform":
        return (
            f"Invalid 'platform' value: {error.instance!r}. "
            f"Must be one of: {sorted(VALID_PLATFORMS)}"
        )
    if error.validator == "pattern":
        return (
            f"Invalid spec field '{field_path}': {error.instance!r} is not a plain slug. "
            "Use a library module name (letters, digits, '.', '_', '-'; no path separators)."
        )
    return f"Invalid spec field '{field_path}': {error.message}. Fix it in the spec file."


class SpecLoader:
    """Loads a YAML stack spec file and returns a validated StackSpec."""

    def __init__(self, fs: FileSystem | None = None) -> None:
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()

    def load(self, path: Path) -> StackSpec:
        """Read, parse, and schema-validate the spec at *path*.

        Raises:
            FileNotFoundError: if the file does not exist.
            ValueError: if the spec fails JSON-schema validation.
        """
        if not self._fs.exists(path):
            raise FileNotFoundError(f"Spec file not found: {path}")

        data: Any = yaml.safe_load(self._fs.read_text(path)) or {}

        error = best_match(Draft202012Validator(SPEC_SCHEMA).iter_errors(data))
        if error is not None:
            raise ValueError(_format_schema_error(error))

        return StackSpec(
            name=data["name"],
            platform=data["platform"],
            frontend=data.get("frontend") or [],
            backend=data.get("backend") or [],
            database=data.get("database") or [],
            inference=data.get("inference") or [],
        )
