"""Component resolver — maps StackSpec components to module paths or placeholders."""

from dataclasses import dataclass
from pathlib import Path

from scaffold_generator.filesystem import FileSystem, RealFileSystem
from scaffold_generator.spec import StackSpec

# Categories are always resolved in this order so assembled files are consistent.
CATEGORY_ORDER = ("frontend", "backend", "database", "inference")


@dataclass
class ResolvedComponent:
    """A declared component that has a matching module directory."""

    category: str
    name: str
    module_path: Path


@dataclass
class Placeholder:
    """A declared component with no matching module directory."""

    category: str
    name: str


ComponentResult = ResolvedComponent | Placeholder


class ComponentResolver:
    """Resolves each component in a StackSpec to a module path or a Placeholder."""

    def __init__(self, components_dir: Path, fs: FileSystem | None = None) -> None:
        self.components_dir = components_dir
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()

    def resolve(self, spec: StackSpec) -> list[ComponentResult]:
        """Return one result per declared component, in category order.

        Known components (module directory exists) → ResolvedComponent.
        Unknown components (no directory found) → Placeholder.
        """
        category_components: dict[str, list[str]] = {
            "frontend": spec.frontend,
            "backend": spec.backend,
            "database": spec.database,
            "inference": spec.inference,
        }
        results: list[ComponentResult] = []
        for category in CATEGORY_ORDER:
            for name in category_components[category]:
                module_path = self.components_dir / category / name
                if self._fs.is_dir(module_path):
                    results.append(
                        ResolvedComponent(category=category, name=name, module_path=module_path)
                    )
                else:
                    results.append(Placeholder(category=category, name=name))
        return results
