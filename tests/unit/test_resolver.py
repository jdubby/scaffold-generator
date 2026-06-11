"""Unit tests for the component resolver (scaffold_generator.resolver)."""

from pathlib import Path

from scaffold_generator.filesystem import InMemoryFileSystem
from scaffold_generator.resolver import ComponentResolver, Placeholder, ResolvedComponent
from scaffold_generator.spec import StackSpec

COMPONENTS_DIR = Path("components")


def _resolver_with_modules(*modules: str) -> ComponentResolver:
    """A resolver over a library containing the given 'category/name' modules."""
    fs = InMemoryFileSystem(dirs=tuple(f"components/{module}" for module in modules))
    return ComponentResolver(components_dir=COMPONENTS_DIR, fs=fs)


class TestComponentResolverResolve:
    def test_known_component_returns_resolved_component(self) -> None:
        resolver = _resolver_with_modules("frontend/react-native")

        spec = StackSpec(name="test", platform="mobile", frontend=["react-native"])
        result = resolver.resolve(spec)

        assert len(result) == 1
        assert isinstance(result[0], ResolvedComponent)
        assert result[0].category == "frontend"
        assert result[0].name == "react-native"
        assert result[0].module_path == COMPONENTS_DIR / "frontend" / "react-native"

    def test_unknown_component_returns_placeholder(self) -> None:
        resolver = _resolver_with_modules()

        spec = StackSpec(name="test", platform="mobile", database=["supabase"])
        result = resolver.resolve(spec)

        assert len(result) == 1
        assert isinstance(result[0], Placeholder)
        assert result[0].category == "database"
        assert result[0].name == "supabase"

    def test_mixed_known_and_unknown_components(self) -> None:
        resolver = _resolver_with_modules("backend/fastapi")

        spec = StackSpec(name="test", platform="mobile", backend=["fastapi"], database=["supabase"])
        result = resolver.resolve(spec)

        assert len(result) == 2
        resolved = [r for r in result if isinstance(r, ResolvedComponent)]
        placeholders = [r for r in result if isinstance(r, Placeholder)]
        assert len(resolved) == 1
        assert len(placeholders) == 1
        assert resolved[0].name == "fastapi"
        assert placeholders[0].name == "supabase"

    def test_empty_spec_returns_empty_list(self) -> None:
        resolver = _resolver_with_modules()

        spec = StackSpec(name="empty", platform="backend")
        result = resolver.resolve(spec)

        assert result == []

    def test_category_order_is_frontend_backend_database_inference(self) -> None:
        resolver = _resolver_with_modules("inference/tensorflow", "frontend/react-native")

        spec = StackSpec(
            name="test",
            platform="mobile",
            frontend=["react-native"],
            inference=["tensorflow"],
        )
        result = resolver.resolve(spec)

        assert result[0].category == "frontend"
        assert result[1].category == "inference"

    def test_multiple_components_in_same_category(self) -> None:
        resolver = _resolver_with_modules("database/postgres", "database/redis")

        spec = StackSpec(name="test", platform="web", database=["postgres", "redis"])
        result = resolver.resolve(spec)

        assert len(result) == 2
        assert all(isinstance(r, ResolvedComponent) for r in result)
        assert result[0].name == "postgres"
        assert result[1].name == "redis"
