"""Command-line interface for the scaffold generator."""

from pathlib import Path

import click

from scaffold_generator.assembler import FileAssembler
from scaffold_generator.filesystem import FileSystem, RealFileSystem
from scaffold_generator.gates import GATES_FILENAME, GateCollector
from scaffold_generator.importer import SPEC_FILENAME, ImportResult, PackageImporter
from scaffold_generator.resolver import ComponentResolver, Placeholder
from scaffold_generator.spec import SpecLoader
from scaffold_generator.validator import ContractValidator
from scaffold_generator.writer import ScaffoldWriter

_DEFAULT_COMPONENTS_DIR = Path(__file__).parent.parent.parent / "components"
_DEFAULT_CORE_DIR = Path(__file__).parent.parent.parent / "core"


@click.command()
@click.argument("spec_file", required=False, type=click.Path(path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Destination directory for the generated scaffold.",
)
@click.option(
    "--components-dir",
    type=click.Path(path_type=Path),
    default=_DEFAULT_COMPONENTS_DIR,
    show_default=True,
    help="Path to the component module library.",
)
@click.option(
    "--core-dir",
    type=click.Path(path_type=Path),
    default=_DEFAULT_CORE_DIR,
    show_default=True,
    help="Path to the core template files.",
)
@click.option(
    "--list-components",
    is_flag=True,
    default=False,
    help="Print all available component modules and exit.",
)
@click.option(
    "--validate",
    "validate_spec",
    type=click.Path(path_type=Path),
    default=None,
    help="Validate a stack spec file and exit.",
)
def main(
    spec_file: Path | None,
    output: Path | None,
    components_dir: Path,
    core_dir: Path,
    list_components: bool,
    validate_spec: Path | None,
) -> None:
    """Generate a project scaffold from a YAML stack spec.

    SPEC_FILE is either a spec file or a scaffold package directory: a
    directory holding a stack-spec.yml plus content files (product specs,
    exec plans, feature files, a domain map) at their final scaffold-relative
    paths. Package content is overlaid onto the generated scaffold.
    """
    fs = RealFileSystem()

    if list_components:
        _cmd_list_components(components_dir, fs)
        return

    if validate_spec is not None:
        _cmd_validate(validate_spec, fs)
        return

    if spec_file is None:
        raise click.UsageError(
            "SPEC_FILE is required when not using --list-components or --validate."
        )

    _cmd_generate(spec_file, output, components_dir, core_dir, fs)


def _cmd_list_components(components_dir: Path, fs: FileSystem) -> None:
    """Print all available component modules grouped by category."""
    if not fs.is_dir(components_dir):
        click.echo(f"Components directory not found: {components_dir}")
        return

    found_any = False
    for category_dir in fs.list_dir(components_dir):
        if not fs.is_dir(category_dir):
            continue
        modules = sorted(p.name for p in fs.list_dir(category_dir) if fs.is_dir(p))
        if not modules:
            continue
        click.echo(f"{category_dir.name}:")
        collector = GateCollector(fs)
        for module in modules:
            click.echo(f"  - {module} ({_gate_summary(collector, category_dir / module)})")
        found_any = True

    if not found_any:
        click.echo("No component modules found.")


def _cmd_validate(spec_path: Path, fs: FileSystem) -> None:
    """Load and validate a stack spec file; exit non-zero on failure."""
    try:
        SpecLoader(fs).load(spec_path)
        click.echo("Spec is valid.")
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc


def _cmd_generate(
    spec_file: Path,
    output: Path | None,
    components_dir: Path,
    core_dir: Path,
    fs: FileSystem,
) -> None:
    """Resolve, assemble, overlay any package content, write, and validate."""
    # 0. A directory argument is a scaffold package: its stack spec drives
    # generation and its content files are overlaid before writing
    importer: PackageImporter | None = None
    if fs.is_dir(spec_file):
        importer = PackageImporter(spec_file, fs)
        if not fs.is_file(importer.spec_path):
            click.echo(
                f"Error: not a scaffold package: no {SPEC_FILENAME} found in {spec_file}",
                err=True,
            )
            raise SystemExit(1)
        spec_file = importer.spec_path

    # 1. Load spec
    try:
        spec = SpecLoader(fs).load(spec_file)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error loading spec: {exc}", err=True)
        raise SystemExit(1) from exc

    # 2. Determine output directory and preflight writability before any
    # generation work begins
    dest = output if output is not None else Path.cwd() / spec.name
    writer = ScaffoldWriter(fs)
    try:
        writer.preflight(dest)
    except (FileExistsError, PermissionError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    # 3. Resolve components
    resolver = ComponentResolver(components_dir, fs)
    components = resolver.resolve(spec)

    # Warn for placeholders
    for component in components:
        if isinstance(component, Placeholder):
            message = (
                f"Warning: no module found for '{component.name}' "
                f"({component.category}). A placeholder will be inserted."
            )
            available = _available_modules(components_dir, component.category, fs)
            if available:
                message += f" Available {component.category} modules: {', '.join(available)}."
            click.echo(message)

    # Warn where a module declares no gates, or declares one its own CI never runs
    try:
        for message in GateCollector(fs).warnings(components):
            click.echo(message)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    # 4. Assemble files from core templates
    assembler = FileAssembler(fs)
    files: dict[str, str] = {}

    if fs.is_dir(core_dir):
        try:
            for template_path in fs.walk_files(core_dir):
                relative = str(template_path.relative_to(core_dir))
                template_content = fs.read_text(template_path)
                files[relative] = assembler.assemble(template_content, components)
        except ValueError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise SystemExit(1) from exc
    else:
        click.echo(f"Warning: core templates directory not found: {core_dir}")

    # 5. Overlay package content onto the assembled files
    import_result: ImportResult | None = None
    if importer is not None:
        import_result = importer.apply(files)

    # 6. Write scaffold
    try:
        writer.write(dest, files)
    except (FileExistsError, PermissionError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc

    # 7. Validate contract
    errors = ContractValidator(fs).validate(dest)
    if errors:
        click.echo("Contract validation warnings:")
        for error in errors:
            click.echo(f"  - {error.message}")

    if import_result is not None:
        _echo_import_summary(import_result)
    click.echo(f"Scaffold generated at: {dest}")


def _available_modules(components_dir: Path, category: str, fs: FileSystem) -> list[str]:
    """Module names available in *category*, for unknown-component warnings."""
    category_dir = components_dir / category
    if not fs.is_dir(category_dir):
        return []
    return sorted(p.name for p in fs.list_dir(category_dir) if fs.is_dir(p))


def _gate_summary(collector: GateCollector, module_path: Path) -> str:
    """How a module's declared gate count is shown in --list-components."""
    try:
        count = collector.count(module_path)
    except ValueError:
        return f"invalid {GATES_FILENAME}"
    if count == 0:
        return "no gates declared"
    return f"{count} gate{'s' if count > 1 else ''}"


def _echo_import_summary(result: ImportResult) -> None:
    if result.overlaid:
        click.echo("Package content imported:")
        for relative in result.overlaid:
            click.echo(f"  - {relative}")
    for relative in result.indexed_specs:
        click.echo(f"Indexed in docs/product-specs/index.md: {relative}")
    if result.domain_map_merged:
        click.echo("Domain map merged into ARCHITECTURE.md.")
    for note in result.notes:
        click.echo(f"Note: {note}")
