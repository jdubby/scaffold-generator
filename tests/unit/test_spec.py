"""Unit tests for the spec loader (scaffold_generator.spec)."""

from pathlib import Path

import pytest

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.spec import SpecLoader, StackSpec

SPEC_PATH = Path("stack.yml")


def _loader_for(spec_content: str) -> SpecLoader:
    return SpecLoader(fs=InMemoryFileSystem(files={"stack.yml": spec_content}))


class TestSpecLoaderLoad:
    def test_load_valid_spec_returns_stack_spec(self) -> None:
        loader = _loader_for(
            "name: vocal-app\n"
            "platform: mobile\n"
            "frontend:\n"
            "  - react-native\n"
            "backend:\n"
            "  - fastapi\n"
            "database:\n"
            "  - firebase\n"
            "inference:\n"
            "  - pytorch-mobile\n"
        )
        spec = loader.load(SPEC_PATH)

        assert isinstance(spec, StackSpec)
        assert spec.name == "vocal-app"
        assert spec.platform == "mobile"
        assert spec.frontend == ["react-native"]
        assert spec.backend == ["fastapi"]
        assert spec.database == ["firebase"]
        assert spec.inference == ["pytorch-mobile"]

    def test_load_spec_with_no_optional_categories(self) -> None:
        loader = _loader_for("name: api-only\nplatform: backend\n")
        spec = loader.load(SPEC_PATH)

        assert spec.name == "api-only"
        assert spec.frontend == []
        assert spec.backend == []
        assert spec.database == []
        assert spec.inference == []

    def test_load_missing_name_raises_value_error(self) -> None:
        loader = _loader_for("platform: mobile\n")

        with pytest.raises(ValueError, match="name"):
            loader.load(SPEC_PATH)

    def test_load_invalid_platform_raises_value_error(self) -> None:
        loader = _loader_for("name: my-app\nplatform: tablet\n")

        with pytest.raises(ValueError, match="platform"):
            loader.load(SPEC_PATH)

    def test_load_nonexistent_file_raises_file_not_found(self) -> None:
        loader = SpecLoader(fs=InMemoryFileSystem())

        with pytest.raises(FileNotFoundError):
            loader.load(Path("does-not-exist.yml"))


class TestSpecSchemaValidation:
    """The spec is validated against a JSON schema, per docs/SECURITY.md."""

    def test_load_path_like_component_name_raises_value_error(self) -> None:
        loader = _loader_for("name: my-app\nplatform: web\nbackend:\n  - ../../etc/passwd\n")

        with pytest.raises(ValueError, match="backend"):
            loader.load(SPEC_PATH)

    def test_load_path_like_project_name_raises_value_error(self) -> None:
        loader = _loader_for("name: ../evil\nplatform: web\n")

        with pytest.raises(ValueError, match="name"):
            loader.load(SPEC_PATH)

    def test_load_non_list_category_raises_value_error(self) -> None:
        loader = _loader_for("name: my-app\nplatform: web\nbackend: fastapi\n")

        with pytest.raises(ValueError, match="backend"):
            loader.load(SPEC_PATH)

    def test_schema_error_names_field_and_carries_hint(self) -> None:
        loader = _loader_for("name: my-app\nplatform: web\nbackend:\n  - ../../etc/passwd\n")

        with pytest.raises(ValueError) as exc_info:
            loader.load(SPEC_PATH)

        message = str(exc_info.value)
        assert "backend[0]" in message
        assert "slug" in message
