"""Unit tests for module-declared quality gates (scaffold_generator.gates)."""

from pathlib import Path

import pytest

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.gates import Gate, GateCollector, parse_rendered
from scaffold_generator.resolver import ComponentResult, Placeholder, ResolvedComponent

PLACEHOLDER = "### {name} — no module\n"


def _component(name: str, category: str = "backend") -> ResolvedComponent:
    return ResolvedComponent(
        category=category, name=name, module_path=Path(f"components/{category}/{name}")
    )


def _collector(files: dict[str, str]) -> GateCollector:
    return GateCollector(fs=InMemoryFileSystem(files=files))


def _module_files(name: str, checks: str | None, ci: str = "") -> dict[str, str]:
    base = f"components/backend/{name}"
    files = {f"{base}/ci.yml": ci}
    if checks is not None:
        files[f"{base}/checks.yml"] = checks
    return files


TWO_GATES = "gates:\n  - name: lint\n    run: ruff check .\n  - name: test\n    run: pytest\n"
TWO_GATES_CI = "  api-checks:\n    steps:\n      - run: ruff check . && pytest\n"
ONE_GATE = "gates:\n  - name: build\n    run: npm run build\n"


class TestLoad:
    def test_declared_gates_are_parsed_in_order(self) -> None:
        collector = _collector(_module_files("api", TWO_GATES))

        assert collector.load(_component("api")) == [
            Gate(name="lint", run="ruff check ."),
            Gate(name="test", run="pytest"),
        ]

    def test_module_without_checks_yml_declares_no_gates(self) -> None:
        assert _collector(_module_files("api", None)).load(_component("api")) == []

    def test_unparseable_checks_yml_names_the_module(self) -> None:
        collector = _collector(_module_files("api", "gates: [unclosed\n"))

        with pytest.raises(ValueError, match="api"):
            collector.load(_component("api"))

    @pytest.mark.parametrize(
        ("checks", "expected_field"),
        [
            ("gates: not-a-list\n", "gates"),
            ("- name: lint\n  run: pytest\n", "gates"),
            ("gates:\n  - pytest\n", "gates[0]"),
            ("gates:\n  - name: lint\n", "gates[0]"),
            ("gates:\n  - run: pytest\n", "gates[0]"),
            ("gates:\n  - name: not a slug\n    run: pytest\n", "gates[0].name"),
            ("gates:\n  - name: lint\n    run: '   '\n", "gates[0].run"),
        ],
    )
    def test_malformed_checks_yml_names_module_and_field(
        self, checks: str, expected_field: str
    ) -> None:
        collector = _collector(_module_files("api", checks))

        with pytest.raises(ValueError) as caught:
            collector.load(_component("api"))

        assert "api" in str(caught.value)
        assert expected_field in str(caught.value)


class TestRender:
    def test_gates_are_grouped_under_their_module(self) -> None:
        rendered = _collector(_module_files("api", TWO_GATES)).render(
            [_component("api")], PLACEHOLDER
        )

        assert "**api**" in rendered
        assert "- lint — `ruff check .`" in rendered
        assert "- test — `pytest`" in rendered

    def test_a_command_declared_twice_is_listed_once(self) -> None:
        files = {**_module_files("api", TWO_GATES), **_module_files("cli", TWO_GATES)}
        rendered = _collector(files).render([_component("api"), _component("cli")], PLACEHOLDER)

        assert rendered.count("`pytest`") == 1
        assert "**cli**" in rendered

    def test_module_declaring_an_empty_gate_list_says_so(self) -> None:
        rendered = _collector(_module_files("api", "gates: []\n")).render(
            [_component("api")], PLACEHOLDER
        )

        assert "**api**" in rendered
        assert "no gates of its own" in rendered

    def test_module_without_checks_yml_fails_like_a_missing_fragment(self) -> None:
        collector = _collector(_module_files("api", None))

        with pytest.raises(ValueError, match="missing fragment file: checks.yml"):
            collector.render([_component("api")], PLACEHOLDER)

    def test_placeholder_component_renders_the_placeholder_block(self) -> None:
        rendered = _collector({}).render(
            [Placeholder(category="database", name="supabase")], PLACEHOLDER
        )

        assert "supabase" in rendered
        assert "no module" in rendered


class TestWarnings:
    def test_gate_absent_from_ci_is_reported(self) -> None:
        collector = _collector(_module_files("api", TWO_GATES, ci="  api-checks:\n"))

        messages = collector.warnings([_component("api")])

        assert any("lint" in m and "api" in m for m in messages)
        assert any("test" in m for m in messages)

    def test_gate_inside_a_larger_command_is_not_drift(self) -> None:
        collector = _collector(_module_files("api", TWO_GATES, ci=TWO_GATES_CI))

        assert collector.warnings([_component("api")]) == []

    def test_explicitly_empty_gates_list_is_not_reported(self) -> None:
        collector = _collector(_module_files("api", "gates: []\n"))

        assert collector.warnings([_component("api")]) == []

    def test_module_without_checks_yml_yields_no_drift_warning(self) -> None:
        # Absence is a missing required fragment, reported at render time, not drift.
        assert _collector(_module_files("api", None)).warnings([_component("api")]) == []

    def test_missing_ci_yml_does_not_report_every_gate_as_drift(self) -> None:
        collector = _collector({"components/backend/api/checks.yml": TWO_GATES})

        assert collector.warnings([_component("api")]) == []

    def test_placeholder_components_are_not_reported(self) -> None:
        assert _collector({}).warnings([Placeholder(category="database", name="supabase")]) == []


class TestCount:
    def test_count_reports_declared_gates(self) -> None:
        assert (
            _collector(_module_files("api", TWO_GATES)).count(Path("components/backend/api")) == 2
        )

    def test_count_is_zero_without_checks_yml(self) -> None:
        assert _collector(_module_files("api", None)).count(Path("components/backend/api")) == 0


class TestParseRendered:
    """parse_rendered is the inverse of render; the round trip keeps them honest."""

    def test_round_trip_recovers_every_rendered_gate(self) -> None:
        files = {**_module_files("api", TWO_GATES), **_module_files("web", ONE_GATE)}
        components: list[ComponentResult] = [_component("api"), _component("web")]
        rendered = _collector(files).render(components, PLACEHOLDER)

        parsed = parse_rendered(f"# Agent Workflow\n\n## Quality gates\n\n{rendered}\n")

        assert parsed == [
            Gate(name="lint", run="ruff check ."),
            Gate(name="test", run="pytest"),
            Gate(name="build", run="npm run build"),
        ]

    def test_a_module_with_no_gates_contributes_nothing(self) -> None:
        rendered = _collector(_module_files("api", "gates: []\n")).render(
            [_component("api")], PLACEHOLDER
        )

        assert parse_rendered(f"## Quality gates\n\n{rendered}\n") == []

    def test_content_after_the_section_is_ignored(self) -> None:
        document = (
            "## Quality gates\n\n**api**\n- test — `pytest`\n\n"
            "## Repository map\n\n- other — `not a gate`\n"
        )

        assert parse_rendered(document) == [Gate(name="test", run="pytest")]

    def test_document_without_the_section_is_an_error(self) -> None:
        with pytest.raises(ValueError, match="Quality gates"):
            parse_rendered("# Agent Workflow\n\n## Repository map\n")
