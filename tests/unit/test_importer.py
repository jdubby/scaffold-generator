"""Unit tests for the package importer (scaffold_generator.importer)."""

from pathlib import Path

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.importer import PackageImporter

PACKAGE_DIR = Path("pkg")

SPEC_INDEX_TEMPLATE = (
    "# Product Specs\n\n## Index\n\n| Spec | Status |\n|------|--------|\n| _none yet_ | — |\n"
)

ARCHITECTURE_TEMPLATE = (
    "# Architecture\n"
    "\n"
    "## Domain map\n"
    "\n"
    "| Domain | Responsibility | Primary modules |\n"
    "|--------|---------------|-----------------|\n"
    "| _none yet_ | — | — |\n"
)

DOMAIN_MAP_WITH_TABLE = (
    "# Domain Map\n"
    "\n"
    "Copy the rows in the table below into the **Domain map** section of\n"
    "`ARCHITECTURE.md` after running the scaffold scripts.\n"
    "\n"
    "| Domain | Responsibility | Primary modules |\n"
    "|--------|---------------|-----------------|\n"
    "| SnapSell Core | Owns the business logic | <fill in> |\n"
    "| SnapSell API | HTTP interface | <fill in> |\n"
    "\n"
    "Selected architecture: B — Hybrid Mobile Approach\n"
)


def _generated_files() -> dict[str, str]:
    """Assembled scaffold files as they exist just before writing."""
    return {
        "ARCHITECTURE.md": ARCHITECTURE_TEMPLATE,
        "README.md": "# README\n",
        "docs/product-specs/index.md": SPEC_INDEX_TEMPLATE,
    }


def _importer(package_files: dict[str, str]) -> PackageImporter:
    files = {f"pkg/{path}": content for path, content in package_files.items()}
    return PackageImporter(PACKAGE_DIR, fs=InMemoryFileSystem(files=files))


class TestOverlay:
    def test_content_files_land_at_their_package_relative_paths(self) -> None:
        files = _generated_files()
        importer = _importer(
            {
                "stack-spec.yml": "name: app\nplatform: web\n",
                "tests/features/build.feature": "Feature: Build\n",
                "docs/exec-plans/active/mvp.md": "# Plan\n",
            }
        )

        result = importer.apply(files)

        assert files["tests/features/build.feature"] == "Feature: Build\n"
        assert files["docs/exec-plans/active/mvp.md"] == "# Plan\n"
        assert "tests/features/build.feature" in result.overlaid
        assert "docs/exec-plans/active/mvp.md" in result.overlaid

    def test_stack_spec_is_not_copied(self) -> None:
        files = _generated_files()
        _importer({"stack-spec.yml": "name: app\nplatform: web\n"}).apply(files)

        assert "stack-spec.yml" not in files

    def test_hidden_files_are_not_copied(self) -> None:
        files = _generated_files()
        importer = _importer(
            {
                "stack-spec.yml": "name: app\nplatform: web\n",
                ".DS_Store": "junk",
                "docs/.DS_Store": "junk",
            }
        )

        result = importer.apply(files)

        assert ".DS_Store" not in files
        assert "docs/.DS_Store" not in files
        assert result.overlaid == []

    def test_package_file_wins_on_collision_with_generated_file(self) -> None:
        files = _generated_files()
        _importer({"README.md": "# SnapSell\n"}).apply(files)

        assert files["README.md"] == "# SnapSell\n"


class TestProductSpecIndexing:
    def test_spec_replaces_index_placeholder_row(self) -> None:
        files = _generated_files()
        result = _importer({"docs/product-specs/snapsell.md": "## Goal\n"}).apply(files)

        index = files["docs/product-specs/index.md"]
        assert "| [snapsell](./snapsell.md) | Active |" in index
        assert "_none yet_" not in index
        assert files["docs/product-specs/snapsell.md"] == "## Goal\n"
        assert result.indexed_specs == ["docs/product-specs/snapsell.md"]

    def test_spec_title_comes_from_first_heading(self) -> None:
        files = _generated_files()
        _importer(
            {"docs/product-specs/snapsell.md": "# Product Spec: SnapSell\n\n## Goal\n"}
        ).apply(files)

        assert (
            "| [Product Spec: SnapSell](./snapsell.md) | Active |"
            in (files["docs/product-specs/index.md"])
        )

    def test_multiple_specs_are_all_indexed(self) -> None:
        files = _generated_files()
        _importer(
            {
                "docs/product-specs/listing.md": "# Listing\n",
                "docs/product-specs/valuation.md": "# Valuation\n",
            }
        ).apply(files)

        index = files["docs/product-specs/index.md"]
        assert "| [Listing](./listing.md) | Active |" in index
        assert "| [Valuation](./valuation.md) | Active |" in index

    def test_index_without_placeholder_is_left_alone_with_a_note(self) -> None:
        files = _generated_files()
        files["docs/product-specs/index.md"] = "# Product Specs\n"
        result = _importer({"docs/product-specs/snapsell.md": "## Goal\n"}).apply(files)

        assert files["docs/product-specs/index.md"] == "# Product Specs\n"
        assert any("index" in note for note in result.notes)


class TestDomainMapMerge:
    def test_table_rows_replace_architecture_placeholder(self) -> None:
        files = _generated_files()
        result = _importer({"docs/domain-map.md": DOMAIN_MAP_WITH_TABLE}).apply(files)

        architecture = files["ARCHITECTURE.md"]
        assert "| SnapSell Core | Owns the business logic | <fill in> |" in architecture
        assert "| SnapSell API | HTTP interface | <fill in> |" in architecture
        assert "| _none yet_ | — | — |" not in architecture
        assert result.domain_map_merged

    def test_merged_domain_map_is_not_copied(self) -> None:
        files = _generated_files()
        _importer({"docs/domain-map.md": DOMAIN_MAP_WITH_TABLE}).apply(files)

        assert "docs/domain-map.md" not in files

    def test_domain_map_without_table_is_copied_verbatim_with_a_note(self) -> None:
        files = _generated_files()
        result = _importer({"docs/domain-map.md": "No table here.\n"}).apply(files)

        assert files["docs/domain-map.md"] == "No table here.\n"
        assert not result.domain_map_merged
        assert any("domain map" in note.lower() for note in result.notes)

    def test_architecture_without_placeholder_copies_verbatim_with_a_note(self) -> None:
        files = _generated_files()
        files["ARCHITECTURE.md"] = "# Architecture\n"
        result = _importer({"docs/domain-map.md": DOMAIN_MAP_WITH_TABLE}).apply(files)

        assert files["docs/domain-map.md"] == DOMAIN_MAP_WITH_TABLE
        assert not result.domain_map_merged
        assert any("domain map" in note.lower() for note in result.notes)
