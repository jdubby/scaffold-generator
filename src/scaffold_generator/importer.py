"""Package importer — overlays scaffold-package content files onto assembled output."""

from dataclasses import dataclass, field
from pathlib import Path

from scaffold_generator.filesystem import FileSystem, RealFileSystem

SPEC_FILENAME = "stack-spec.yml"

_ARCHITECTURE_PATH = "ARCHITECTURE.md"
_DOMAIN_MAP_PATH = "docs/domain-map.md"
_DOMAIN_MAP_PLACEHOLDER = "| _none yet_ | — | — |"
_SPEC_INDEX_PATH = "docs/product-specs/index.md"
_SPEC_INDEX_PLACEHOLDER = "| _none yet_ | — |"
_PRODUCT_SPECS_PREFIX = "docs/product-specs/"


@dataclass
class ImportResult:
    """What applying a package changed in the assembled files."""

    overlaid: list[str] = field(default_factory=list)
    indexed_specs: list[str] = field(default_factory=list)
    domain_map_merged: bool = False
    notes: list[str] = field(default_factory=list)


class PackageImporter:
    """Overlays a scaffold package's content files onto the assembled files mapping.

    A scaffold package is a directory holding a stack spec (``stack-spec.yml``)
    plus content files already laid out at their final scaffold-relative paths
    (product specs, exec plans, feature files, a domain map). The spec drives
    generation; everything else is overlaid onto the generated files before
    they are written, so package mode keeps the writer's all-or-nothing output.
    """

    def __init__(self, package_dir: Path, fs: FileSystem | None = None) -> None:
        self.package_dir = package_dir
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()

    @property
    def spec_path(self) -> Path:
        """Where the package's stack spec must live."""
        return self.package_dir / SPEC_FILENAME

    def apply(self, files: dict[str, str]) -> ImportResult:
        """Overlay every content file in the package onto *files*.

        The stack spec and hidden files are skipped. ``docs/domain-map.md`` is
        consumed: its table rows replace the Domain map placeholder row in
        ``ARCHITECTURE.md`` rather than the file being copied. Files under
        ``docs/product-specs/`` are additionally indexed in
        ``docs/product-specs/index.md``. On a path collision the package file
        wins — it is user content; the generated file is boilerplate.
        """
        result = ImportResult()
        spec_index_rows: list[str] = []

        for path in self._fs.walk_files(self.package_dir):
            relative = path.relative_to(self.package_dir).as_posix()
            if relative == SPEC_FILENAME or _is_hidden(relative):
                continue
            content = self._fs.read_text(path)

            if relative == _DOMAIN_MAP_PATH:
                if self._merge_domain_map(content, files):
                    result.domain_map_merged = True
                    continue
                result.notes.append(
                    "The domain map could not be merged into ARCHITECTURE.md; "
                    f"{_DOMAIN_MAP_PATH} was copied as-is. Merge its table into "
                    "the Domain map section by hand."
                )

            files[relative] = content
            result.overlaid.append(relative)

            if relative.startswith(_PRODUCT_SPECS_PREFIX) and relative != _SPEC_INDEX_PATH:
                spec_index_rows.append(_spec_index_row(relative, content))
                result.indexed_specs.append(relative)

        if spec_index_rows:
            index = files.get(_SPEC_INDEX_PATH, "")
            if _SPEC_INDEX_PLACEHOLDER in index:
                files[_SPEC_INDEX_PATH] = index.replace(
                    _SPEC_INDEX_PLACEHOLDER, "\n".join(spec_index_rows)
                )
            else:
                result.indexed_specs = []
                result.notes.append(
                    f"{_SPEC_INDEX_PATH} has no placeholder row; add the imported "
                    "product specs to its index table by hand."
                )

        return result

    def _merge_domain_map(self, content: str, files: dict[str, str]) -> bool:
        """Replace the ARCHITECTURE.md Domain map placeholder with the package's
        table rows. Returns False when either side lacks its expected shape."""
        rows = _table_data_rows(content)
        architecture = files.get(_ARCHITECTURE_PATH, "")
        if not rows or _DOMAIN_MAP_PLACEHOLDER not in architecture:
            return False
        files[_ARCHITECTURE_PATH] = architecture.replace(_DOMAIN_MAP_PLACEHOLDER, "\n".join(rows))
        return True


def _is_hidden(relative: str) -> bool:
    return any(part.startswith(".") for part in Path(relative).parts)


def _table_data_rows(content: str) -> list[str]:
    """Data rows of the first Markdown table in *content* (header and separator
    excluded). Empty when no table with data rows is present."""
    table: list[str] = []
    for line in content.splitlines():
        if line.lstrip().startswith("|"):
            table.append(line.strip())
        elif table:
            break
    return table[2:] if len(table) > 2 else []


def _spec_index_row(relative: str, content: str) -> str:
    filename = Path(relative).name
    title = Path(relative).stem
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return f"| [{title}](./{filename}) | Active |"
