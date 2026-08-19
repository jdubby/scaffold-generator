"""Executable bindings for tests/features/executable_gates.feature."""

from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from pytest_bdd import given, parsers, scenarios, then, when

from scaffold_generator.cli import main

scenarios("executable_gates.feature")

_FRAGMENT_FILENAMES = ("arch.md", "reliability.md", "security.md")

# Core templates: the same shape the bundled core ships, reduced to what these
# scenarios read. AGENTS.md carries the gates marker under test.
_CORE_TEMPLATES = {
    "AGENTS.md": (
        "# Agent Workflow\n\n## Quality gates\n\n<!-- ASSEMBLE:gates -->\n\n"
        "## Repository map\n\n| What | Where |\n|------|-------|\n<!-- ASSEMBLE:agents -->\n"
    ),
    "ARCHITECTURE.md": "# Architecture\n\n<!-- ASSEMBLE:arch -->\n",
    "README.md": "# README\n",
    "ci.yml": "jobs:\n# ASSEMBLE:ci\n",
    "docs/EVALUATOR.md": "# Evaluator\n",
    "docs/DESIGN.md": "# Design\n",
    "docs/QUALITY_SCORE.md": "# Quality Score\n",
    "docs/RELIABILITY.md": "# Reliability\n\n<!-- ASSEMBLE:reliability -->\n",
    "docs/SECURITY.md": "# Security\n\n<!-- ASSEMBLE:security -->\n",
    "docs/design-docs/core-beliefs.md": "# Core Beliefs\n",
    "docs/exec-plans/tech-debt-tracker.md": "# Tech Debt\n",
    "docs/exec-plans/active/.gitkeep": "",
    "docs/product-specs/index.md": "# Product Specs\n",
    "tests/features/.gitkeep": "",
}

_CI_RUNNING_BOTH_GATES = (
    "  {name}-checks:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - name: Lint\n"
    "        run: ruff check .\n"
    "      - name: Unit tests\n"
    "        run: pytest\n"
)
_TWO_GATES = "gates:\n  - name: lint\n    run: ruff check .\n  - name: test\n    run: pytest\n"


@dataclass
class GeneratorRun:
    """State shared across the steps of one scenario."""

    components_dir: Path
    core_dir: Path
    output_dir: Path
    spec_path: Path
    spec_fields: dict[str, str] = field(default_factory=dict)
    spec_components: dict[str, list[str]] = field(default_factory=dict)
    result: Result | None = None


@pytest.fixture
def run(tmp_path: Path) -> GeneratorRun:
    core_dir = tmp_path / "core"
    for relative, content in _CORE_TEMPLATES.items():
        target = core_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    return GeneratorRun(
        components_dir=tmp_path / "components",
        core_dir=core_dir,
        output_dir=tmp_path / "generated" / "scaffold",
        spec_path=tmp_path / "stack.yml",
    )


def _result(run: GeneratorRun) -> Result:
    assert run.result is not None, "Scenario has no CLI invocation result yet."
    return run.result


def _write_module(run: GeneratorRun, name: str, ci_yml: str, checks_yml: str | None) -> None:
    module_dir = run.components_dir / "backend" / name
    module_dir.mkdir(parents=True, exist_ok=True)
    for filename in _FRAGMENT_FILENAMES:
        section = filename.removesuffix(".md")
        (module_dir / filename).write_text(f"### {name} {section}\n")
    (module_dir / "agents.md").write_text(f"| {name} (backend) | src/{name} |\n")
    (module_dir / "ci.yml").write_text(ci_yml)
    if checks_yml is not None:
        (module_dir / "checks.yml").write_text(checks_yml)


def _agents_md(run: GeneratorRun) -> str:
    path = run.output_dir / "AGENTS.md"
    assert path.is_file(), "AGENTS.md is missing from the generated scaffold."
    return path.read_text()


# --- Given ---------------------------------------------------------------


@given(parsers.parse('a module "{name}" declaring gates its CI runs'))
def module_with_matching_gates(run: GeneratorRun, name: str) -> None:
    _write_module(run, name, _CI_RUNNING_BOTH_GATES.format(name=name), _TWO_GATES)


@given(parsers.parse('a module "{name}" declaring a gate its CI does not run'))
def module_with_drift(run: GeneratorRun, name: str) -> None:
    ci_yml = f"  {name}-checks:\n    steps:\n      - name: Lint\n        run: ruff check .\n"
    _write_module(run, name, ci_yml, _TWO_GATES)


@given(parsers.parse('a module "{name}" declaring no gates'))
def module_without_gates(run: GeneratorRun, name: str) -> None:
    _write_module(run, name, f"  {name}-checks:\n    steps:\n      - run: pytest\n", None)


@given(parsers.parse('a module "{name}" declaring an empty gate list'))
def module_with_empty_gates(run: GeneratorRun, name: str) -> None:
    ci_yml = f"  {name}-checks:\n    steps:\n      - run: pytest\n"
    _write_module(run, name, ci_yml, "gates: []\n")


@given(parsers.parse('a module "{name}" whose checks.yml declares a gate name that is not a slug'))
def module_with_malformed_checks(run: GeneratorRun, name: str) -> None:
    checks = "gates:\n  - name: not a slug\n    run: pytest\n"
    _write_module(run, name, f"  {name}-checks:\n    steps:\n      - run: pytest\n", checks)


@given(parsers.parse('a stack spec declaring backend component "{name}"'))
def spec_declaring(run: GeneratorRun, name: str) -> None:
    run.spec_fields = {"name": "gated-app", "platform": "backend"}
    run.spec_components.setdefault("backend", []).append(name)


@given(parsers.parse('the spec also declares backend component "{name}"'))
def spec_also_declaring(run: GeneratorRun, name: str) -> None:
    run.spec_components.setdefault("backend", []).append(name)


# --- When ----------------------------------------------------------------


@when("the user generates the scaffold")
def generate(run: GeneratorRun) -> None:
    run.spec_path.write_text(yaml.safe_dump({**run.spec_fields, **run.spec_components}))
    run.result = CliRunner().invoke(
        main,
        [
            str(run.spec_path),
            "--output",
            str(run.output_dir),
            "--components-dir",
            str(run.components_dir),
            "--core-dir",
            str(run.core_dir),
        ],
    )


@when("the user lists components")
def list_components(run: GeneratorRun) -> None:
    run.result = CliRunner().invoke(
        main, ["--components-dir", str(run.components_dir), "--list-components"]
    )


# --- Then ----------------------------------------------------------------


@then("the generator exits successfully")
def exits_successfully(run: GeneratorRun) -> None:
    result = _result(run)
    assert result.exit_code == 0, result.output


@then("the generator exits with a non-zero code")
def exits_nonzero(run: GeneratorRun) -> None:
    assert _result(run).exit_code != 0


@then("no output directory is created")
def no_output_directory(run: GeneratorRun) -> None:
    assert not run.output_dir.exists()


@then("no warnings are printed")
def no_warnings(run: GeneratorRun) -> None:
    output = _result(run).output
    assert "Warning" not in output, output
    assert "warnings" not in output, output


@then(parsers.parse('"AGENTS.md" lists the gate command "{command}"'))
def agents_lists_command(run: GeneratorRun, command: str) -> None:
    assert f"`{command}`" in _agents_md(run)


@then(parsers.parse('"AGENTS.md" lists the gate command "{command}" exactly once'))
def agents_lists_command_once(run: GeneratorRun, command: str) -> None:
    content = _agents_md(run)
    assert content.count(f"`{command}`") == 1, content


@then(parsers.parse('"AGENTS.md" groups the gate commands under "{module}"'))
def agents_groups_under_module(run: GeneratorRun, module: str) -> None:
    content = _agents_md(run)
    assert f"**{module}**" in content, content
    assert content.index(f"**{module}**") < content.index("`ruff check .`")


@then(parsers.parse('a warning names "{name}" and "{detail}"'))
def warning_names(run: GeneratorRun, name: str, detail: str) -> None:
    output = _result(run).output
    assert "Warning" in output, output
    assert name in output and detail in output, output


@then(parsers.parse('an error names "{name}" and "{detail}"'))
def error_names(run: GeneratorRun, name: str, detail: str) -> None:
    stderr = _result(run).stderr
    assert name in stderr and detail in stderr, stderr


@then(parsers.parse('the listing shows "{module}" with "{summary}"'))
def listing_shows(run: GeneratorRun, module: str, summary: str) -> None:
    output = _result(run).output
    assert f"- {module} ({summary})" in output, output
