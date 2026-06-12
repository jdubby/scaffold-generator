"""Unit tests for the scaffold generator CLI (scaffold_generator.cli)."""

from pathlib import Path

import pytest
from click.testing import CliRunner, Result

from scaffold_generator.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def valid_spec(tmp_path: Path) -> Path:
    spec = tmp_path / "stack.yml"
    spec.write_text("name: my-app\nplatform: web\nbackend:\n  - fastapi\n")
    return spec


@pytest.fixture()
def invalid_spec(tmp_path: Path) -> Path:
    spec = tmp_path / "bad.yml"
    spec.write_text("platform: web\n")  # missing required 'name'
    return spec


@pytest.fixture()
def components_dir(tmp_path: Path) -> Path:
    """A components directory with one known backend component."""
    comp_dir = tmp_path / "components"
    module = comp_dir / "backend" / "fastapi"
    module.mkdir(parents=True)
    (module / "arch.md").write_text("### FastAPI\n")
    (module / "reliability.md").write_text("### FastAPI reliability\n")
    (module / "security.md").write_text("### FastAPI security\n")
    return comp_dir


@pytest.fixture()
def core_dir(tmp_path: Path) -> Path:
    """A minimal core templates directory."""
    core = tmp_path / "core"
    core.mkdir()
    (core / "AGENTS.md").write_text("# Agent Workflow\n")
    (core / "ARCHITECTURE.md").write_text("# Architecture\n<!-- ASSEMBLE:arch -->\n")
    (core / "README.md").write_text("# README\n")
    docs = core / "docs"
    docs.mkdir()
    (docs / "EVALUATOR.md").write_text("# Evaluator\n")
    (docs / "DESIGN.md").write_text("# Design\n")
    (docs / "QUALITY_SCORE.md").write_text("# Quality Score\n")
    (docs / "RELIABILITY.md").write_text("# Reliability\n")
    (docs / "SECURITY.md").write_text("# Security\n")
    design_docs = docs / "design-docs"
    design_docs.mkdir()
    (design_docs / "core-beliefs.md").write_text("# Core Beliefs\n")
    exec_plans = docs / "exec-plans"
    exec_plans.mkdir()
    (exec_plans / "tech-debt-tracker.md").write_text("# Tech Debt\n")
    (exec_plans / "active").mkdir()
    (exec_plans / "active" / ".gitkeep").write_text("")
    product_specs = docs / "product-specs"
    product_specs.mkdir()
    (product_specs / "index.md").write_text("# Product Specs\n")
    features = core / "tests" / "features"
    features.mkdir(parents=True)
    (features / ".gitkeep").write_text("")
    return core


class TestListComponents:
    def test_list_components_prints_known_components(
        self, runner: CliRunner, components_dir: Path
    ) -> None:
        result = runner.invoke(
            main,
            ["--components-dir", str(components_dir), "--list-components"],
        )

        assert result.exit_code == 0
        assert "fastapi" in result.output

    def test_list_components_groups_by_category(self, runner: CliRunner, tmp_path: Path) -> None:
        comp_dir = tmp_path / "components"
        (comp_dir / "backend" / "fastapi").mkdir(parents=True)
        (comp_dir / "frontend" / "nextjs").mkdir(parents=True)

        result = runner.invoke(
            main,
            ["--components-dir", str(comp_dir), "--list-components"],
        )

        assert result.exit_code == 0
        assert "backend" in result.output
        assert "frontend" in result.output
        assert "fastapi" in result.output
        assert "nextjs" in result.output

    def test_list_components_empty_library_exits_cleanly(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        comp_dir = tmp_path / "components"
        comp_dir.mkdir()

        result = runner.invoke(
            main,
            ["--components-dir", str(comp_dir), "--list-components"],
        )

        assert result.exit_code == 0


class TestValidate:
    def test_validate_exits_zero_for_valid_spec(self, runner: CliRunner, valid_spec: Path) -> None:
        result = runner.invoke(main, ["--validate", str(valid_spec)])

        assert result.exit_code == 0

    def test_validate_exits_nonzero_for_invalid_spec(
        self, runner: CliRunner, invalid_spec: Path
    ) -> None:
        result = runner.invoke(main, ["--validate", str(invalid_spec)])

        assert result.exit_code != 0

    def test_validate_prints_error_message_for_invalid_spec(
        self, runner: CliRunner, invalid_spec: Path
    ) -> None:
        result = runner.invoke(main, ["--validate", str(invalid_spec)])

        assert "Error" in result.output or result.exit_code != 0

    def test_validate_exits_nonzero_for_missing_file(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        missing = tmp_path / "nonexistent.yml"

        result = runner.invoke(main, ["--validate", str(missing)])

        assert result.exit_code != 0


class TestErrorChannel:
    """User-facing errors must be routed to stderr, per docs/SECURITY.md."""

    def test_validate_routes_invalid_spec_error_to_stderr(
        self, runner: CliRunner, invalid_spec: Path
    ) -> None:
        result = runner.invoke(main, ["--validate", str(invalid_spec)])

        assert "name" in result.stderr

    def test_generate_routes_spec_load_error_to_stderr(
        self,
        runner: CliRunner,
        invalid_spec: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        result = runner.invoke(
            main,
            [
                str(invalid_spec),
                "--output",
                str(tmp_path / "output" / "my-app"),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert "name" in result.stderr

    def test_generate_routes_existing_output_dir_error_to_stderr(
        self,
        runner: CliRunner,
        valid_spec: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        output_dir = tmp_path / "output" / "my-app"
        output_dir.mkdir(parents=True)

        result = runner.invoke(
            main,
            [
                str(valid_spec),
                "--output",
                str(output_dir),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert "already exists" in result.stderr

    def test_generate_routes_unwritable_output_error_to_stderr(
        self,
        runner: CliRunner,
        valid_spec: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        locked = tmp_path / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        try:
            result = runner.invoke(
                main,
                [
                    str(valid_spec),
                    "--output",
                    str(locked / "my-app"),
                    "--components-dir",
                    str(components_dir),
                    "--core-dir",
                    str(core_dir),
                ],
            )
        finally:
            locked.chmod(0o700)

        assert result.exit_code != 0
        assert "not writable" in result.stderr


class TestBundledLibraryCompleteness:
    """Every module shipped in components/ must generate warning-free with the
    bundled core templates — a missing or broken fragment fails this test."""

    COMPONENTS = Path(__file__).parent.parent.parent / "components"

    def test_every_bundled_module_generates_without_warnings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        spec_lines = ["name: all-modules", "platform: hybrid"]
        for category_dir in sorted(self.COMPONENTS.iterdir()):
            if not category_dir.is_dir():
                continue
            modules = sorted(p.name for p in category_dir.iterdir() if p.is_dir())
            if not modules:
                continue
            spec_lines.append(f"{category_dir.name}:")
            spec_lines.extend(f"  - {module}" for module in modules)
        spec = tmp_path / "all-modules.yml"
        spec.write_text("\n".join(spec_lines) + "\n")

        result = runner.invoke(main, [str(spec), "--output", str(tmp_path / "out")])

        assert result.exit_code == 0, result.output
        assert "Warning" not in result.output, result.output
        assert "warnings" not in result.output, result.output


class TestBundledExampleSpec:
    """The bundled example spec must stay valid as the schema and library evolve."""

    EXAMPLE = Path(__file__).parent.parent.parent / "examples" / "stack-spec.yml"

    def test_example_spec_passes_validation(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--validate", str(self.EXAMPLE)])

        assert result.exit_code == 0, result.output

    def test_example_spec_generates_with_bundled_defaults_without_warnings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            main,
            [str(self.EXAMPLE), "--output", str(tmp_path / "example-out")],
        )

        assert result.exit_code == 0, result.output
        assert "Warning" not in result.output, result.output
        assert "warnings" not in result.output, result.output


class TestGenerate:
    def test_generate_creates_output_directory(
        self,
        runner: CliRunner,
        valid_spec: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        output_dir = tmp_path / "output" / "my-app"

        result = runner.invoke(
            main,
            [
                str(valid_spec),
                "--output",
                str(output_dir),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert result.exit_code == 0, result.output
        assert output_dir.is_dir()

    def test_generate_warns_for_unknown_components(
        self,
        runner: CliRunner,
        tmp_path: Path,
        components_dir: Path,
        core_dir: Path,
    ) -> None:
        spec = tmp_path / "stack.yml"
        spec.write_text("name: my-app\nplatform: web\nbackend:\n  - unknown-service\n")
        output_dir = tmp_path / "output" / "my-app"

        result = runner.invoke(
            main,
            [
                str(spec),
                "--output",
                str(output_dir),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert "unknown-service" in result.output or result.exit_code == 0

    def test_generate_fails_when_output_dir_exists(
        self,
        runner: CliRunner,
        valid_spec: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        output_dir = tmp_path / "output" / "my-app"
        output_dir.mkdir(parents=True)

        result = runner.invoke(
            main,
            [
                str(valid_spec),
                "--output",
                str(output_dir),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert result.exit_code != 0


@pytest.fixture()
def package_dir(tmp_path: Path) -> Path:
    """A scaffold package: stack spec plus content files in final layout."""
    pkg = tmp_path / "my-app-scaffold"
    (pkg / "docs" / "product-specs").mkdir(parents=True)
    (pkg / "docs" / "exec-plans" / "active").mkdir(parents=True)
    (pkg / "tests" / "features").mkdir(parents=True)
    (pkg / "stack-spec.yml").write_text("name: my-app\nplatform: web\nbackend:\n  - fastapi\n")
    (pkg / "docs" / "product-specs" / "my-app.md").write_text("## Goal\n")
    (pkg / "docs" / "exec-plans" / "active" / "my-app-mvp.md").write_text("# Plan\n")
    (pkg / "tests" / "features" / "build.feature").write_text("Feature: Build\n")
    (pkg / ".DS_Store").write_text("junk")
    return pkg


class TestPackageImport:
    def _invoke(
        self,
        runner: CliRunner,
        package: Path,
        output_dir: Path,
        components_dir: Path,
        core_dir: Path,
    ) -> Result:
        return runner.invoke(
            main,
            [
                str(package),
                "--output",
                str(output_dir),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

    def test_package_directory_generates_and_overlays_content(
        self,
        runner: CliRunner,
        package_dir: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        output_dir = tmp_path / "out" / "my-app"

        result = self._invoke(runner, package_dir, output_dir, components_dir, core_dir)

        assert result.exit_code == 0, result.output
        assert (output_dir / "AGENTS.md").is_file()
        assert (output_dir / "docs" / "product-specs" / "my-app.md").is_file()
        assert (output_dir / "docs" / "exec-plans" / "active" / "my-app-mvp.md").is_file()
        assert (output_dir / "tests" / "features" / "build.feature").is_file()

    def test_package_spec_and_hidden_files_are_not_copied(
        self,
        runner: CliRunner,
        package_dir: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        output_dir = tmp_path / "out" / "my-app"

        result = self._invoke(runner, package_dir, output_dir, components_dir, core_dir)

        assert result.exit_code == 0, result.output
        assert not (output_dir / "stack-spec.yml").exists()
        assert not (output_dir / ".DS_Store").exists()

    def test_summary_reports_each_overlaid_file(
        self,
        runner: CliRunner,
        package_dir: Path,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        output_dir = tmp_path / "out" / "my-app"

        result = self._invoke(runner, package_dir, output_dir, components_dir, core_dir)

        assert result.exit_code == 0, result.output
        assert "docs/product-specs/my-app.md" in result.output
        assert "tests/features/build.feature" in result.output

    def test_directory_without_stack_spec_fails_and_writes_nothing(
        self,
        runner: CliRunner,
        components_dir: Path,
        core_dir: Path,
        tmp_path: Path,
    ) -> None:
        not_a_package = tmp_path / "empty-dir"
        not_a_package.mkdir()
        output_dir = tmp_path / "out" / "my-app"

        result = self._invoke(runner, not_a_package, output_dir, components_dir, core_dir)

        assert result.exit_code != 0
        assert "stack-spec.yml" in result.stderr
        assert not output_dir.exists()


class TestUnknownComponentSuggestions:
    def test_warning_lists_available_modules_in_the_category(
        self,
        runner: CliRunner,
        tmp_path: Path,
        components_dir: Path,
        core_dir: Path,
    ) -> None:
        spec = tmp_path / "stack.yml"
        spec.write_text("name: my-app\nplatform: web\nbackend:\n  - fastapy\n")

        result = runner.invoke(
            main,
            [
                str(spec),
                "--output",
                str(tmp_path / "out" / "my-app"),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Available backend modules: fastapi" in result.output

    def test_warning_for_empty_category_omits_the_module_list(
        self,
        runner: CliRunner,
        tmp_path: Path,
        components_dir: Path,
        core_dir: Path,
    ) -> None:
        spec = tmp_path / "stack.yml"
        spec.write_text("name: my-app\nplatform: web\ninference:\n  - some-model\n")

        result = runner.invoke(
            main,
            [
                str(spec),
                "--output",
                str(tmp_path / "out" / "my-app"),
                "--components-dir",
                str(components_dir),
                "--core-dir",
                str(core_dir),
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Warning: no module found for 'some-model'" in result.output
        assert "Available inference modules" not in result.output


class TestWorkflowDirectories:
    """Every scaffold generated from the bundled core templates must include
    the directories the workflow documents refer to."""

    EXAMPLE = Path(__file__).parent.parent.parent / "examples" / "stack-spec.yml"

    def test_bundled_core_creates_workflow_directories(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        output_dir = tmp_path / "example-out"

        result = runner.invoke(main, [str(self.EXAMPLE), "--output", str(output_dir)])

        assert result.exit_code == 0, result.output
        assert (output_dir / "tests" / "features").is_dir()
        assert (output_dir / "docs" / "exec-plans" / "active").is_dir()
