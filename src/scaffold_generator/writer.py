"""Scaffold writer — writes assembled file content to the output directory."""

from pathlib import Path

from scaffold_generator.filesystem import FileSystem, RealFileSystem


class ScaffoldWriter:
    """Writes a set of named files into a new output directory."""

    def __init__(self, fs: FileSystem | None = None) -> None:
        self._fs: FileSystem = fs if fs is not None else RealFileSystem()

    def preflight(self, output_dir: Path) -> None:
        """Validate that *output_dir* can be created, before any generation work.

        Raises:
            FileExistsError: if *output_dir* already exists.
            PermissionError: if the nearest existing ancestor directory is not
                writable, so the output directory could not be created.
        """
        if self._fs.exists(output_dir):
            raise FileExistsError(
                f"Output directory already exists: {output_dir}. "
                "Remove it or choose a different output path."
            )
        ancestor = output_dir.parent
        while not self._fs.exists(ancestor) and ancestor != ancestor.parent:
            ancestor = ancestor.parent
        if not self._fs.is_writable_dir(ancestor):
            raise PermissionError(
                f"Output path is not writable: {output_dir} "
                f"(cannot create directories under: {ancestor}). "
                "Choose a writable output path."
            )

    def write(self, output_dir: Path, files: dict[str, str]) -> None:
        """Create *output_dir* and write each entry in *files* to it.

        Args:
            output_dir: Destination directory. Must not already exist.
            files: Mapping of relative path strings to file content strings.

        Raises:
            FileExistsError: if *output_dir* already exists.
            PermissionError: if the destination is not writable.
        """
        self.preflight(output_dir)
        for relative_path, content in files.items():
            self._fs.write_text(output_dir / relative_path, content)
