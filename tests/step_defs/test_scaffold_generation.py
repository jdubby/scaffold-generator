"""Executable bindings for tests/features/scaffold_generation.feature."""

from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from pytest_bdd import given, parsers, scenarios, then, when

from scaffold_generator.cli import main

scenarios("scaffold_generation.feature")

REPO_ROOT = Path(__file__).parent.parent.parent

_FRAGMENT_FILENAMES = ("arch.md", "reliability.md", "security.md")

# Library layout used by the Background step: module name -> category.
_MODULE_CATEGORIES = {
    "react-native": "frontend",
    "fastapi": "backend",
    "firebase": "database",
}

# Minimal core templates covering every file the scenarios and the
# contract validator expect in a generated scaffold.
_CORE_TEMPLATES = {
    "AGENTS.md": (
        "# Agent Workflow\n\n| What | Where |\n|------|-------|\n<!-- ASSEMBLE:agents -->\n"
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
    "docs/product-specs/index.md": "# Product Specs\n",
}


@dataclass
class GeneratorRun:
    """State shared across the steps of one scenario."""

    components_dir: Path
    core_dir: Path
    output_dir: Path
    spec_path: Path
    spec_fields: dict[str, str] = field(default_factory=dict)
    spec_components: dict[str, list[str]] = field(default_factory=dict)
    placeholder_file: Path | None = None
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


def _write_spec(run: GeneratorRun) -> None:
    data: dict[str, object] = {**run.spec_fields, **run.spec_components}
    run.spec_path.write_text(yaml.safe_dump(data))


def _scaffold_file(run: GeneratorRun, filename: str) -> Path:
    path = run.output_dir / filename
    assert path.is_file(), f"Expected scaffold file is missing: {filename}"
    return path


# --- Given ---------------------------------------------------------------


@given(
    parsers.parse('the component library contains modules for "{first}", "{second}", and "{third}"')
)
def component_library(run: GeneratorRun, first: str, second: str, third: str) -> None:
    for name in (first, second, third):
        category = _MODULE_CATEGORIES[name]
        module_dir = run.components_dir / category / name
        module_dir.mkdir(parents=True)
        for filename in _FRAGMENT_FILENAMES:
            section = filename.removesuffix(".md")
            (module_dir / filename).write_text(f"### {name} {section}\n")
        (module_dir / "agents.md").write_text(f"| {name} | components/{category}/{name} |\n")
        (module_dir / "ci.yml").write_text(f"  {name}-checks:\n    run: {name} quality gates\n")


@given(parsers.parse('a valid stack spec with name "{name}", platform "{platform}"'))
def valid_spec(run: GeneratorRun, name: str, platform: str) -> None:
    run.spec_fields = {"name": name, "platform": platform}


@given(parsers.parse('the spec declares {category} component "{name}"'))
def declare_component(run: GeneratorRun, category: str, name: str) -> None:
    run.spec_components.setdefault(category, []).append(name)


@given(parsers.parse('a stack spec file missing the required "{field_name}" field'))
def spec_missing_field(run: GeneratorRun, field_name: str) -> None:
    fields = {"name": "some-app", "platform": "web"}
    fields.pop(field_name)
    run.spec_fields = fields


@given(parsers.parse('a stack spec file with an invalid platform value "{platform}"'))
def spec_invalid_platform(run: GeneratorRun, platform: str) -> None:
    run.spec_fields = {"name": "bad-app", "platform": platform}


@given("the component library and core templates bundled with this repository")
def bundled_library(run: GeneratorRun) -> None:
    run.components_dir = REPO_ROOT / "components"
    run.core_dir = REPO_ROOT / "core"


@given("the output path is inside an unwritable directory")
def unwritable_output_path(run: GeneratorRun, request: pytest.FixtureRequest) -> None:
    locked_dir = run.output_dir.parent
    locked_dir.mkdir(parents=True)
    locked_dir.chmod(0o500)
    request.addfinalizer(lambda: locked_dir.chmod(0o700))


# --- When ----------------------------------------------------------------


@when("the user runs the scaffold generator with the spec")
def run_generate(run: GeneratorRun) -> None:
    _write_spec(run)
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


@when("the user runs the scaffold generator with --validate")
def run_validate(run: GeneratorRun) -> None:
    _write_spec(run)
    run.result = CliRunner().invoke(main, ["--validate", str(run.spec_path)])


@when("the user runs the scaffold generator with --list-components")
def run_list_components(run: GeneratorRun) -> None:
    run.result = CliRunner().invoke(
        main,
        ["--components-dir", str(run.components_dir), "--list-components"],
    )


# --- Then ----------------------------------------------------------------


@then("the output directory is created")
def output_directory_created(run: GeneratorRun) -> None:
    assert run.output_dir.is_dir()


@then("no output directory is created")
def no_output_directory(run: GeneratorRun) -> None:
    assert not run.output_dir.exists()


@then(parsers.parse('the scaffold contains "{filename}"'))
def scaffold_contains(run: GeneratorRun, filename: str) -> None:
    _scaffold_file(run, filename)


@then(parsers.parse('"{filename}" contains a section for "{component}"'))
def file_contains_section(run: GeneratorRun, filename: str, component: str) -> None:
    content = _scaffold_file(run, filename).read_text()
    assert component in content


@then(parsers.parse('"{filename}" contains a job block for "{component}"'))
def file_contains_job_block(run: GeneratorRun, filename: str, component: str) -> None:
    content = _scaffold_file(run, filename).read_text()
    assert f"{component}-checks:" in content


@then(parsers.parse('"{filename}" contains a repository map row for "{component}"'))
def file_contains_repo_map_row(run: GeneratorRun, filename: str, component: str) -> None:
    content = _scaffold_file(run, filename).read_text()
    assert f"| {component} " in content


@then(parsers.parse('"{filename}" contains placeholder text for "{component}"'))
def file_contains_placeholder(run: GeneratorRun, filename: str, component: str) -> None:
    path = _scaffold_file(run, filename)
    content = path.read_text()
    assert "No module found" in content
    assert component in content
    run.placeholder_file = path


@then(parsers.parse('the placeholder references "{reference}"'))
def placeholder_references(run: GeneratorRun, reference: str) -> None:
    assert run.placeholder_file is not None, "No placeholder was located by a prior step."
    assert reference in run.placeholder_file.read_text()


@then("the generator exits successfully")
def exits_successfully(run: GeneratorRun) -> None:
    result = _result(run)
    assert result.exit_code == 0, result.output


@then("the generator exits with a non-zero code")
def exits_nonzero(run: GeneratorRun) -> None:
    assert _result(run).exit_code != 0


@then("no warnings are printed")
def no_warnings_printed(run: GeneratorRun) -> None:
    output = _result(run).output
    assert "Warning" not in output, output
    assert "warnings" not in output, output


@then(parsers.parse('a warning is printed for unknown component "{name}"'))
def warning_for_unknown_component(run: GeneratorRun, name: str) -> None:
    output = _result(run).output
    assert "Warning" in output
    assert name in output


@then(parsers.parse('an error is printed to stderr mentioning "{text}"'))
def stderr_mentions(run: GeneratorRun, text: str) -> None:
    assert text in _result(run).stderr


@then(parsers.parse('the output lists "{module}" under "{category}"'))
def output_lists_module_under_category(run: GeneratorRun, module: str, category: str) -> None:
    lines = _result(run).output.splitlines()
    assert f"{category}:" in lines, f"Category header '{category}:' not found."
    section_start = lines.index(f"{category}:") + 1
    section: list[str] = []
    for line in lines[section_start:]:
        if not line.startswith("  "):
            break
        section.append(line.strip())
    assert f"- {module}" in section
