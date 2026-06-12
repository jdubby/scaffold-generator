"""Executable bindings for tests/features/package_import.feature."""

from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner, Result
from pytest_bdd import given, parsers, scenarios, then, when

from scaffold_generator.cli import main

scenarios("package_import.feature")

_FRAGMENT_FILENAMES = ("arch.md", "reliability.md", "security.md")

# Library layout used by the Background step: module name -> category.
_MODULE_CATEGORIES = {
    "react-native": "frontend",
    "fastapi": "backend",
    "firebase": "database",
}

# Minimal core templates satisfying the scaffold contract, including the
# placeholder rows the package importer fills in.
_CORE_TEMPLATES = {
    "AGENTS.md": (
        "# Agent Workflow\n\n| What | Where |\n|------|-------|\n<!-- ASSEMBLE:agents -->\n"
    ),
    "ARCHITECTURE.md": (
        "# Architecture\n"
        "\n"
        "## Domain map\n"
        "\n"
        "| Domain | Responsibility | Primary modules |\n"
        "|--------|---------------|-----------------|\n"
        "| _none yet_ | — | — |\n"
        "\n"
        "<!-- ASSEMBLE:arch -->\n"
    ),
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
    "docs/product-specs/index.md": (
        "# Product Specs\n\n## Index\n\n| Spec | Status |\n|------|--------|\n| _none yet_ | — |\n"
    ),
    "tests/features/.gitkeep": "",
}

_DOMAIN_MAP_TEMPLATE = (
    "# Domain Map\n"
    "\n"
    "Copy the rows in the table below into the **Domain map** section of\n"
    "`ARCHITECTURE.md` after running the scaffold scripts.\n"
    "\n"
    "| Domain | Responsibility | Primary modules |\n"
    "|--------|---------------|-----------------|\n"
    "| {domain} | Owns the business logic | <fill in> |\n"
)


@dataclass
class ImportRun:
    """State shared across the steps of one scenario."""

    components_dir: Path
    core_dir: Path
    output_dir: Path
    package_dir: Path
    spec_path: Path
    spec_fields: dict[str, str] = field(default_factory=dict)
    spec_components: dict[str, list[str]] = field(default_factory=dict)
    result: Result | None = None


@pytest.fixture
def run(tmp_path: Path) -> ImportRun:
    core_dir = tmp_path / "core"
    for relative, content in _CORE_TEMPLATES.items():
        target = core_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    return ImportRun(
        components_dir=tmp_path / "components",
        core_dir=core_dir,
        output_dir=tmp_path / "generated" / "scaffold",
        package_dir=tmp_path / "package",
        spec_path=tmp_path / "stack.yml",
    )


def _result(run: ImportRun) -> Result:
    assert run.result is not None, "Scenario has no CLI invocation result yet."
    return run.result


def _add_module(run: ImportRun, category: str, name: str) -> None:
    module_dir = run.components_dir / category / name
    module_dir.mkdir(parents=True)
    for filename in _FRAGMENT_FILENAMES:
        section = filename.removesuffix(".md")
        (module_dir / filename).write_text(f"### {name} {section}\n")
    (module_dir / "agents.md").write_text(f"| {name} | components/{category}/{name} |\n")
    (module_dir / "ci.yml").write_text(f"  {name}-checks:\n    run: {name} quality gates\n")


def _write_package_file(run: ImportRun, relative: str, content: str) -> None:
    target = run.package_dir / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def _invoke(run: ImportRun, spec_argument: Path) -> None:
    run.result = CliRunner().invoke(
        main,
        [
            str(spec_argument),
            "--output",
            str(run.output_dir),
            "--components-dir",
            str(run.components_dir),
            "--core-dir",
            str(run.core_dir),
        ],
    )


# --- Given ---------------------------------------------------------------


@given(
    parsers.parse('the component library contains modules for "{first}", "{second}", and "{third}"')
)
def component_library(run: ImportRun, first: str, second: str, third: str) -> None:
    for name in (first, second, third):
        _add_module(run, _MODULE_CATEGORIES[name], name)


@given(parsers.parse('the component library also contains inference module "{name}"'))
def inference_module(run: ImportRun, name: str) -> None:
    _add_module(run, "inference", name)


@given(parsers.parse('a scaffold package with a valid stack spec named "{name}"'))
def scaffold_package(run: ImportRun, name: str) -> None:
    spec = {
        "name": name,
        "platform": "hybrid",
        "frontend": ["react-native"],
        "backend": ["fastapi"],
        "database": ["firebase"],
    }
    _write_package_file(run, "stack-spec.yml", yaml.safe_dump(spec))


@given(parsers.parse('the package contains "{relative}"'))
def package_contains(run: ImportRun, relative: str) -> None:
    _write_package_file(run, relative, f"Content of {relative}\n")


@given(parsers.parse('the package contains a hidden file "{filename}"'))
def package_contains_hidden(run: ImportRun, filename: str) -> None:
    _write_package_file(run, filename, "junk")


@given(parsers.parse('the package contains a domain map with a row for "{domain}"'))
def package_contains_domain_map(run: ImportRun, domain: str) -> None:
    _write_package_file(run, "docs/domain-map.md", _DOMAIN_MAP_TEMPLATE.format(domain=domain))


@given("a directory that is not a scaffold package")
def not_a_package(run: ImportRun) -> None:
    run.package_dir.mkdir(parents=True)


@given(parsers.parse('a valid stack spec with name "{name}", platform "{platform}"'))
def valid_spec(run: ImportRun, name: str, platform: str) -> None:
    run.spec_fields = {"name": name, "platform": platform}


@given(parsers.parse('the spec declares {category} component "{name}"'))
def declare_component(run: ImportRun, category: str, name: str) -> None:
    run.spec_components.setdefault(category, []).append(name)


# --- When ----------------------------------------------------------------


@when("the user runs the scaffold generator with the package directory")
def run_with_package(run: ImportRun) -> None:
    _invoke(run, run.package_dir)


@when("the user runs the scaffold generator with the spec")
def run_with_spec(run: ImportRun) -> None:
    data: dict[str, object] = {**run.spec_fields, **run.spec_components}
    run.spec_path.write_text(yaml.safe_dump(data))
    _invoke(run, run.spec_path)


# --- Then ----------------------------------------------------------------


@then("the generator exits successfully")
def exits_successfully(run: ImportRun) -> None:
    result = _result(run)
    assert result.exit_code == 0, result.output


@then("the generator exits with a non-zero code")
def exits_nonzero(run: ImportRun) -> None:
    assert _result(run).exit_code != 0


@then(parsers.parse('the scaffold contains "{filename}"'))
def scaffold_contains(run: ImportRun, filename: str) -> None:
    assert (run.output_dir / filename).is_file(), f"Expected scaffold file missing: {filename}"


@then(parsers.parse('the scaffold does not contain "{filename}"'))
def scaffold_does_not_contain(run: ImportRun, filename: str) -> None:
    assert not (run.output_dir / filename).exists(), f"Unexpected scaffold file: {filename}"


@then(parsers.parse('the scaffold has directory "{dirname}"'))
def scaffold_has_directory(run: ImportRun, dirname: str) -> None:
    assert (run.output_dir / dirname).is_dir(), f"Expected scaffold directory missing: {dirname}"


@then(parsers.parse('"docs/product-specs/index.md" links to "{filename}"'))
def index_links_to(run: ImportRun, filename: str) -> None:
    index = (run.output_dir / "docs" / "product-specs" / "index.md").read_text()
    assert f"(./{filename})" in index, index


@then(parsers.parse('"docs/product-specs/index.md" does not contain "{text}"'))
def index_does_not_contain(run: ImportRun, text: str) -> None:
    index = (run.output_dir / "docs" / "product-specs" / "index.md").read_text()
    assert text not in index, index


@then(parsers.parse('"ARCHITECTURE.md" contains a domain map row for "{domain}"'))
def architecture_contains_domain_row(run: ImportRun, domain: str) -> None:
    content = (run.output_dir / "ARCHITECTURE.md").read_text()
    assert f"| {domain} |" in content, content


@then(parsers.parse('an error is printed to stderr mentioning "{text}"'))
def stderr_mentions(run: ImportRun, text: str) -> None:
    assert text in _result(run).stderr


@then("no output directory is created")
def no_output_directory(run: ImportRun) -> None:
    assert not run.output_dir.exists()


@then(parsers.parse('a warning is printed for unknown component "{name}"'))
def warning_for_unknown_component(run: ImportRun, name: str) -> None:
    output = _result(run).output
    assert "Warning" in output
    assert name in output


@then(parsers.parse('the warning suggests available inference module "{name}"'))
def warning_suggests_module(run: ImportRun, name: str) -> None:
    assert f"Available inference modules: {name}" in _result(run).output


@then(parsers.parse('the output reports overlaid file "{relative}"'))
def output_reports_overlaid(run: ImportRun, relative: str) -> None:
    assert relative in _result(run).output


@then("the output reports the domain map was merged")
def output_reports_domain_map_merged(run: ImportRun) -> None:
    assert "Domain map merged into ARCHITECTURE.md." in _result(run).output
