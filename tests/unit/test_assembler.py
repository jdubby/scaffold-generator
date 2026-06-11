"""Unit tests for the file assembler (scaffold_generator.assembler)."""

from pathlib import Path

import pytest

from scaffold_generator.assembler import FileAssembler
from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.resolver import Placeholder, ResolvedComponent


def _component(category: str, name: str) -> ResolvedComponent:
    return ResolvedComponent(
        category=category, name=name, module_path=Path("components") / category / name
    )


def _assembler(fragments: dict[str, str] | None = None) -> FileAssembler:
    """An assembler over a library holding the given 'category/name/fragment' files."""
    files = {f"components/{path}": content for path, content in (fragments or {}).items()}
    return FileAssembler(fs=InMemoryFileSystem(files=files))


class TestFileAssemblerMarkdownFragments:
    def test_marker_replaced_with_component_fragment(self) -> None:
        assembler = _assembler(
            {"backend/fastapi/arch.md": "### FastAPI\n\nFastAPI owns the HTTP layer.\n"}
        )
        template = "# Architecture\n\n<!-- ASSEMBLE:arch -->\n"

        result = assembler.assemble(template, [_component("backend", "fastapi")])

        assert "<!-- ASSEMBLE:arch -->" not in result
        assert "### FastAPI" in result
        assert "FastAPI owns the HTTP layer." in result

    def test_placeholder_produced_for_unknown_component(self) -> None:
        placeholder = Placeholder(category="database", name="supabase")
        template = "# Architecture\n\n<!-- ASSEMBLE:arch -->\n"

        result = _assembler().assemble(template, [placeholder])

        assert "supabase" in result
        assert "⚠️" in result

    def test_placeholder_references_module_authoring(self) -> None:
        placeholder = Placeholder(category="inference", name="custom-model")
        template = "<!-- ASSEMBLE:arch -->"

        result = _assembler().assemble(template, [placeholder])

        assert "MODULE_AUTHORING.md" in result

    def test_multiple_components_concatenated_in_resolver_order(self) -> None:
        assembler = _assembler(
            {
                "frontend/react-native/arch.md": "### React Native\n",
                "backend/fastapi/arch.md": "### FastAPI\n",
            }
        )
        template = "<!-- ASSEMBLE:arch -->"

        result = assembler.assemble(
            template,
            [_component("frontend", "react-native"), _component("backend", "fastapi")],
        )

        assert result.index("React Native") < result.index("FastAPI")

    def test_template_with_no_marker_returned_unchanged(self) -> None:
        assembler = _assembler({"backend/fastapi/arch.md": "### FastAPI\n"})
        template = "# Architecture\n\nNo markers here.\n"

        result = assembler.assemble(template, [_component("backend", "fastapi")])

        assert result == template

    def test_missing_fragment_file_raises_value_error(self) -> None:
        # Library contains the module directory but no arch.md fragment.
        assembler = _assembler({"backend/fastapi/reliability.md": "### FastAPI reliability\n"})
        template = "<!-- ASSEMBLE:arch -->"

        with pytest.raises(ValueError, match="arch.md"):
            assembler.assemble(template, [_component("backend", "fastapi")])

    def test_agents_marker_replaced_with_repo_map_rows(self) -> None:
        assembler = _assembler({"backend/fastapi/agents.md": "| fastapi | src/api/ |\n"})
        template = "| What | Where |\n|------|-------|\n<!-- ASSEMBLE:agents -->\n"

        result = assembler.assemble(template, [_component("backend", "fastapi")])

        assert "<!-- ASSEMBLE:agents -->" not in result
        assert "| fastapi | src/api/ |" in result

    def test_multiple_markers_in_same_template_each_replaced(self) -> None:
        assembler = _assembler(
            {
                "backend/fastapi/arch.md": "### FastAPI arch\n",
                "backend/fastapi/reliability.md": "### FastAPI reliability\n",
            }
        )
        template = "<!-- ASSEMBLE:arch -->\n\n<!-- ASSEMBLE:reliability -->"

        result = assembler.assemble(template, [_component("backend", "fastapi")])

        assert "FastAPI arch" in result
        assert "FastAPI reliability" in result
        assert "<!-- ASSEMBLE:" not in result


class TestFileAssemblerYamlFragments:
    """ci.yml assembly uses YAML-comment markers, since HTML comments are not valid YAML."""

    def test_yaml_marker_replaced_with_ci_fragment(self) -> None:
        assembler = _assembler({"backend/fastapi/ci.yml": "  fastapi-checks:\n    run: pytest\n"})
        template = "jobs:\n# ASSEMBLE:ci\n"

        result = assembler.assemble(template, [_component("backend", "fastapi")])

        assert "# ASSEMBLE:ci" not in result
        assert "fastapi-checks:" in result

    def test_yaml_placeholder_is_comment_only(self) -> None:
        placeholder = Placeholder(category="database", name="supabase")
        template = "jobs:\n# ASSEMBLE:ci\n"

        result = _assembler().assemble(template, [placeholder])

        assert "supabase" in result
        assert "MODULE_AUTHORING.md" in result
        injected = [line for line in result.splitlines() if line not in ("jobs:", "")]
        assert injected, "placeholder text was not injected"
        for line in injected:
            assert line.startswith("#"), f"non-comment line in YAML placeholder: {line!r}"

    def test_missing_ci_fragment_raises_value_error(self) -> None:
        assembler = _assembler({"backend/fastapi/arch.md": "### FastAPI\n"})
        template = "# ASSEMBLE:ci"

        with pytest.raises(ValueError, match="ci.yml"):
            assembler.assemble(template, [_component("backend", "fastapi")])

    def test_yaml_marker_only_matches_whole_line(self) -> None:
        assembler = _assembler({"backend/fastapi/arch.md": "### FastAPI\n"})
        template = "# This doc mentions # ASSEMBLE:ci mid-line, which is not a marker.\n"

        result = assembler.assemble(template, [_component("backend", "fastapi")])

        assert result == template
