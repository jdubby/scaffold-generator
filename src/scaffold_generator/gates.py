"""Quality gates — the runnable commands each component module declares.

A module's gate commands used to exist only inside its ``ci.yml``, where nothing
but a CI runner could read them. Declaring them as data in ``checks.yml`` lets the
generated ``AGENTS.md`` name the commands an agent must run, and lets drift between
a module's stated gates and its own CI be detected.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from scaffold_generator.filesystem import FileSystem, RealFileSystem
from scaffold_generator.resolver import ComponentResult, Placeholder, ResolvedComponent
from scaffold_generator.spec import SLUG_PATTERN

GATES_FILENAME = "checks.yml"
CI_FILENAME = "ci.yml"

_SLUG = re.compile(SLUG_PATTERN)


# The heading the rendered gate list lives under in a generated AGENTS.md, and the
# shape of one rendered gate. parse_rendered is the inverse of _render_module, so
# the two must change together; test_gates.py pins the round trip.
@dataclass(frozen=True)
class Gate:
    """One runnable quality-gate command declared by a module."""

    name: str
    run: str


GATES_HEADING = "## Quality gates"
_RENDERED_GATE = re.compile(r"^- ([A-Za-z0-9][A-Za-z0-9._-]*) — `(.+)`$")
_NEXT_HEADING = re.compile(r"^## ", re.MULTILINE)


def parse_rendered(agents_md: str) -> list[Gate]:
    """The gates listed in a generated AGENTS.md Quality gates section.

    Raises:
        ValueError: if the document has no Quality gates section.
    """
    start = agents_md.find(GATES_HEADING)
    if start == -1:
        raise ValueError(f"no '{GATES_HEADING}' section found")
    body = agents_md[start + len(GATES_HEADING) :]
    next_heading = _NEXT_HEADING.search(body)
    if next_heading is not None:
        body = body[: next_heading.start()]
    return [
        Gate(name=match.group(1), run=match.group(2))
        for match in (_RENDERED_GATE.match(line.strip()) for line in body.splitlines())
        if match is not None
    ]


class GateCollector:
    """Reads module-declared gates, renders them, and reports what does not add up."""

    def __init__(self, fs: FileSystem | None = None) -> None:
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()
        self._cache: dict[Path, list[Gate]] = {}

    def load(self, component: ResolvedComponent) -> list[Gate]:
        """Gates declared by *component*, or an empty list when it declares none.

        Raises:
            ValueError: if ``checks.yml`` exists but is not a valid gate list. The
                message names the module and the offending field.
        """
        if component.module_path in self._cache:
            return self._cache[component.module_path]
        gates = self._parse(component.module_path, component.name)
        self._cache[component.module_path] = gates
        return gates

    def count(self, module_path: Path) -> int:
        """How many gates the module at *module_path* declares."""
        return len(self._parse(module_path, module_path.name))

    def render(self, components: list[ComponentResult], placeholder_template: str) -> str:
        """The Markdown gate list for the ``gates`` marker, grouped by module.

        A command already listed under an earlier module is not repeated: the agent
        should be told to run it once.
        """
        parts: list[str] = []
        listed: set[str] = set()
        for component in components:
            if isinstance(component, Placeholder):
                parts.append(placeholder_template.format(name=component.name))
                continue
            parts.append(self._render_module(component, listed))
        return "\n".join(parts)

    def declares(self, component: ResolvedComponent) -> bool:
        """Whether *component* ships a checks.yml at all.

        An empty ``gates: []`` is a deliberate statement that the module has no
        runnable gates of its own; a missing file is an incomplete module, and
        generation fails on it like any other missing fragment.
        """
        return self._fs.is_file(component.module_path / GATES_FILENAME)

    def warnings(self, components: list[ComponentResult]) -> list[str]:
        """Warnings for gates a module declares but its own ci.yml never runs."""
        messages: list[str] = []
        for component in components:
            if not isinstance(component, ResolvedComponent):
                continue
            gates = self.load(component)
            ci_path = component.module_path / CI_FILENAME
            if not self._fs.is_file(ci_path):
                # A missing ci.yml is a missing required fragment; assembly reports
                # it. Calling every gate "drift" here would bury that message.
                continue
            ci_text = self._fs.read_text(ci_path)
            for gate in gates:
                if gate.run not in ci_text:
                    messages.append(
                        f"Warning: module '{component.name}' declares gate "
                        f"'{gate.name}' ({gate.run!r}) but its {CI_FILENAME} never runs it."
                    )
        return messages

    # --- internals -------------------------------------------------------

    def _render_module(self, component: ResolvedComponent, listed: set[str]) -> str:
        if not self.declares(component):
            raise ValueError(
                f"Component '{component.name}' is missing fragment file: {GATES_FILENAME}. "
                f"Expected at: {component.module_path / GATES_FILENAME}"
            )
        lines = [f"**{component.name}**"]
        gates = self.load(component)
        fresh = [gate for gate in gates if gate.run not in listed]
        if not gates:
            lines.append("- no gates of its own; wire this component's checks in `ci.yml`")
        elif not fresh:
            lines.append("- covered by the commands above")
        else:
            for gate in fresh:
                listed.add(gate.run)
                lines.append(f"- {gate.name} — `{gate.run}`")
        return "\n".join(lines) + "\n"

    def _parse(self, module_path: Path, module_name: str) -> list[Gate]:
        path = module_path / GATES_FILENAME
        if not self._fs.is_file(path):
            return []
        try:
            document = yaml.safe_load(self._fs.read_text(path))
        except yaml.YAMLError as exc:
            raise self._invalid(
                module_name, f"it is not parseable YAML ({exc.__class__.__name__})"
            ) from exc
        if not isinstance(document, dict) or not isinstance(document.get("gates"), list):
            raise self._invalid(module_name, "'gates' must be a list of gate mappings")
        return [
            self._parse_gate(module_name, position, entry)
            for position, entry in enumerate(document["gates"])
        ]

    def _parse_gate(self, module_name: str, position: int, entry: object) -> Gate:
        field = f"gates[{position}]"
        if not isinstance(entry, dict):
            raise self._invalid(module_name, f"{field} must be a mapping with 'name' and 'run'")
        for key in ("name", "run"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise self._invalid(module_name, f"{field}.{key} must be a non-empty string")
        name, run = entry["name"].strip(), entry["run"].strip()
        if not _SLUG.match(name):
            raise self._invalid(module_name, f"{field}.name {name!r} is not a plain slug")
        return Gate(name=name, run=run)

    @staticmethod
    def _invalid(module_name: str, detail: str) -> ValueError:
        return ValueError(f"Component '{module_name}' has an invalid {GATES_FILENAME}: {detail}")
