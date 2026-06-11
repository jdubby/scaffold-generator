"""Filesystem boundary — the single substitutable interface for filesystem access."""

import os
from pathlib import Path
from typing import Protocol


class FileSystem(Protocol):
    """Narrow filesystem interface. Production code uses RealFileSystem; tests
    substitute InMemoryFileSystem."""

    def exists(self, path: Path) -> bool: ...

    def is_file(self, path: Path) -> bool: ...

    def is_dir(self, path: Path) -> bool: ...

    def read_text(self, path: Path) -> str: ...

    def write_text(self, path: Path, content: str) -> None:
        """Write *content* to *path*, creating parent directories as needed."""
        ...

    def list_dir(self, path: Path) -> list[Path]:
        """Immediate children of *path*, sorted."""
        ...

    def walk_files(self, root: Path) -> list[Path]:
        """All files anywhere under *root*, sorted."""
        ...

    def is_writable_dir(self, path: Path) -> bool:
        """True if entries can be created inside the directory at *path*."""
        ...


class RealFileSystem:
    """FileSystem backed by the operating system."""

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    def read_text(self, path: Path) -> str:
        return path.read_text()

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def list_dir(self, path: Path) -> list[Path]:
        return sorted(path.iterdir())

    def walk_files(self, root: Path) -> list[Path]:
        return sorted(p for p in root.rglob("*") if p.is_file())

    def is_writable_dir(self, path: Path) -> bool:
        return os.access(path, os.W_OK | os.X_OK)


class InMemoryFileSystem:
    """FileSystem double holding files as a path→content mapping.

    Used by unit tests so module behavior is exercised without live filesystem
    access. Directories exist implicitly as ancestors of files, or explicitly
    via *dirs*. Paths are normalised to POSIX strings internally.
    """

    def __init__(
        self,
        files: dict[str, str] | None = None,
        dirs: tuple[str, ...] = (),
        unwritable_dirs: tuple[str, ...] = (),
    ) -> None:
        self.files: dict[str, str] = {Path(p).as_posix(): c for p, c in (files or {}).items()}
        self._explicit_dirs = {Path(d).as_posix() for d in dirs}
        self._unwritable = {Path(d).as_posix() for d in unwritable_dirs}

    def _dirs(self) -> set[str]:
        dirs = set()
        for key in self._explicit_dirs:
            dirs.add(key)
            dirs.update(self._ancestors(Path(key)))
        for key in self.files:
            dirs.update(self._ancestors(Path(key)))
        return dirs

    @staticmethod
    def _ancestors(path: Path) -> set[str]:
        ancestors = set()
        parent = path.parent
        while parent != parent.parent:
            ancestors.add(parent.as_posix())
            parent = parent.parent
        return ancestors

    def exists(self, path: Path) -> bool:
        return self.is_file(path) or self.is_dir(path)

    def is_file(self, path: Path) -> bool:
        return path.as_posix() in self.files

    def is_dir(self, path: Path) -> bool:
        return path.as_posix() in self._dirs()

    def read_text(self, path: Path) -> str:
        key = path.as_posix()
        if key not in self.files:
            raise FileNotFoundError(key)
        return self.files[key]

    def write_text(self, path: Path, content: str) -> None:
        self.files[path.as_posix()] = content

    def list_dir(self, path: Path) -> list[Path]:
        key = path.as_posix()
        entries = {k for k in self.files} | self._dirs()
        return sorted(Path(e) for e in entries if Path(e).parent.as_posix() == key)

    def walk_files(self, root: Path) -> list[Path]:
        prefix = root.as_posix() + "/"
        return sorted(Path(k) for k in self.files if k.startswith(prefix))

    def is_writable_dir(self, path: Path) -> bool:
        return path.as_posix() not in self._unwritable
