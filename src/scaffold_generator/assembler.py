"""File assembler — replaces ASSEMBLE markers in templates with component fragments."""

import re

from scaffold_generator.filesystem import FileSystem, RealFileSystem
from scaffold_generator.resolver import ComponentResult, Placeholder, ResolvedComponent

# Markdown templates use HTML-comment markers: <!-- ASSEMBLE:arch -->
_HTML_MARKER_PATTERN = re.compile(r"<!-- ASSEMBLE:([\w-]+) -->")

# YAML templates use comment-line markers (HTML comments are not valid YAML).
# The marker must be the only content on its line: # ASSEMBLE:ci
_YAML_MARKER_PATTERN = re.compile(r"^[ \t]*# ASSEMBLE:([\w-]+)[ \t]*$", re.MULTILINE)

# Fragment filenames for each marker type.
_FRAGMENT_FILENAME: dict[str, str] = {
    "arch": "arch.md",
    "reliability": "reliability.md",
    "security": "security.md",
    "agents": "agents.md",
    "ci": "ci.yml",
}

_MD_PLACEHOLDER_TEMPLATE = """\
### {name} ⚠️ No module found

No module exists for `{name}`. Complete this section before implementing
any feature that touches this component.

To add a reusable module, follow the guide in `MODULE_AUTHORING.md`
in the component library.
"""

# Injected into YAML templates, so every line must be a YAML comment.
_YAML_PLACEHOLDER_TEMPLATE = """\
# {name} — no module found
# No module exists for `{name}`. Add CI steps for this component before
# implementing any feature that touches it.
# To add a reusable module, follow the guide in `MODULE_AUTHORING.md`
# in the component library.
"""


class FileAssembler:
    """Assembles a template file by replacing ASSEMBLE markers with component fragments."""

    def __init__(self, fs: FileSystem | None = None) -> None:
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()

    def assemble(self, template: str, components: list[ComponentResult]) -> str:
        """Replace every ASSEMBLE marker in *template*.

        For each marker:
        - ResolvedComponent: read the fragment file for the marker type and inject it.
        - Placeholder: inject a clearly-marked placeholder block, styled to match the
          marker context (Markdown prose or YAML comments).

        Markers for unknown fragment types are left unchanged.

        Raises:
            ValueError: if a ResolvedComponent is missing the expected fragment file.
        """

        def _replace(match: re.Match[str], placeholder_template: str) -> str:
            fragment_type = match.group(1)
            filename = _FRAGMENT_FILENAME.get(fragment_type)
            if filename is None:
                return match.group(0)  # unknown marker type — leave intact
            return self._collect(components, filename, placeholder_template)

        result = _HTML_MARKER_PATTERN.sub(lambda m: _replace(m, _MD_PLACEHOLDER_TEMPLATE), template)
        return _YAML_MARKER_PATTERN.sub(lambda m: _replace(m, _YAML_PLACEHOLDER_TEMPLATE), result)

    def _collect(
        self,
        components: list[ComponentResult],
        filename: str,
        placeholder_template: str,
    ) -> str:
        parts: list[str] = []
        for component in components:
            if isinstance(component, Placeholder):
                parts.append(placeholder_template.format(name=component.name))
            elif isinstance(component, ResolvedComponent):
                fragment_path = component.module_path / filename
                if not self._fs.exists(fragment_path):
                    raise ValueError(
                        f"Component '{component.name}' is missing fragment file: {filename}. "
                        f"Expected at: {fragment_path}"
                    )
                parts.append(self._fs.read_text(fragment_path))
        return "\n".join(parts)
