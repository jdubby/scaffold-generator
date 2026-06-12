# Exec Plan: Scaffold package import

**Spec:** `docs/product-specs/package-import.md`
**Started:** 2026-06-12

## Why

Product-laboratory exports a package (stack-spec.yml + content files in final
scaffold-relative layout). Users currently hand-copy files, create missing
directories, edit the product-specs index, and merge the domain map. One
command should do all of it.

## Steps

1. BDD scenarios in `tests/features/package_import.feature` (one per AC).
2. Failing unit tests: `tests/unit/test_importer.py`, CLI additions in
   `tests/unit/test_cli.py`, validator additions for required directories.
3. Implement:
   - `src/scaffold_generator/importer.py` — `PackageImporter` reads the
     package via the `FileSystem` boundary and applies the overlay to the
     assembled files dict (index rows, domain-map merge, verbatim copies).
   - `cli.py` — directory positional argument triggers package mode; print
     import summary; unknown-component warning lists available category
     modules.
   - `core/ARCHITECTURE.md` — add a Domain map section with a placeholder row.
   - `core/tests/features/.gitkeep`, `core/docs/exec-plans/active/.gitkeep` —
     every scaffold gets the workflow directories.
   - `validator.py` — require `tests/features/` and `docs/exec-plans/active/`.
4. Step definitions in `tests/step_defs/test_package_import.py`.
5. Docs: README usage, AGENTS.md repo map row, ARCHITECTURE.md domain map +
   layering entry for the importer.
6. Quality gates; verify end-to-end against a real product-laboratory package.

## Decisions

- Package mode is the same positional argument (a directory), not a separate
  subcommand — one mental model.
- The overlay is applied to the in-memory files dict before the single
  `ScaffoldWriter.write`, so package mode keeps the all-or-nothing write and
  the existing preflight.
- On path collision the package file wins (it is user content); the
  product-specs index and ARCHITECTURE.md are then post-processed.
- Domain-map merge extracts the first Markdown table; data rows replace the
  `_none yet_` placeholder row. No table → copy verbatim + summary note.
