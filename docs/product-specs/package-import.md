# Product Spec: Scaffold package import

**Status:** Active
**Feature file:** `tests/features/package_import.feature`

## Goal

Upstream tools (e.g. product-laboratory) deliver a *scaffold package*: a
directory containing a `stack-spec.yml` plus content files — product specs,
execution plans, Gherkin feature files, and a domain map — already laid out in
their final scaffold-relative locations. Today a user must generate the
scaffold from the spec, then hand-copy every content file into place, create
directories the generator never wrote (`tests/features/`,
`docs/exec-plans/active/`), add an index row in `docs/product-specs/index.md`,
and merge the domain map table into `ARCHITECTURE.md`. Each step is manual and
error-prone. The generator should accept the package directory itself and do
all of this in one command.

## Scope

### In scope

- Passing a package directory (a directory containing `stack-spec.yml`) as the
  positional argument generates the scaffold from that spec and overlays every
  other content file in the package into the output, creating intermediate
  directories as needed.
- Files placed under `docs/product-specs/` are added as rows to the generated
  `docs/product-specs/index.md`.
- A package `docs/domain-map.md` is consumed: its table rows are merged into
  the **Domain map** section of the generated `ARCHITECTURE.md` instead of the
  file being copied.
- Every generated scaffold (with or without a package) includes the
  `tests/features/` and `docs/exec-plans/active/` directories the core
  workflow documents refer to.
- The warning for an unknown component names the available modules in that
  category, so spec authors can correct near-miss names.
- The command finishes with a summary of what was generated and overlaid.

### Out of scope

- Changes to product-laboratory's export format (tracked separately upstream).
- Importing a package into an *existing* scaffold (the output directory must
  not exist, as with plain generation).
- Validating package content files beyond placing them.

## Acceptance criteria

### AC-1: Package directory as input

Given a directory containing a valid `stack-spec.yml` and content files, when
the user runs the generator with that directory as the positional argument,
then the scaffold is generated from the spec and every content file in the
package appears at the same relative path in the output, with intermediate
directories created. `stack-spec.yml` itself and hidden files (e.g.
`.DS_Store`) are not copied.

### AC-2: Product specs are indexed

Given a package containing `docs/product-specs/<name>.md`, when the package is
imported, then `docs/product-specs/index.md` in the output lists that spec
(linked, status Active) in place of the `_none yet_` placeholder row.

### AC-3: Domain map is merged

Given a package containing `docs/domain-map.md` with a Markdown table, when
the package is imported, then the table's data rows replace the placeholder
row in the **Domain map** section of the generated `ARCHITECTURE.md`, and
`docs/domain-map.md` is not copied into the output. If no table can be found,
the file is copied verbatim instead and the summary says so.

### AC-4: Directory without a spec fails clearly

Given a directory with no `stack-spec.yml`, when the user passes it as the
positional argument, then the generator exits non-zero with an error naming
the missing file, and writes nothing.

### AC-5: Scaffolds always include the workflow directories

Given any valid spec, when a scaffold is generated, then `tests/features/` and
`docs/exec-plans/active/` exist in the output.

### AC-6: Unknown component warnings name the alternatives

Given a spec declaring a component with no matching module, when the scaffold
is generated, then the placeholder warning lists the module names available in
that category.

### AC-7: Import summary

Given a package import, when generation succeeds, then the output lists each
overlaid file and notes the index rows added and whether the domain map was
merged.

## Open questions

- Should the consumed `stack-spec.yml` be copied into the scaffold root for
  provenance? Current default: no — regeneration into an existing directory is
  unsupported, so the copy would only drift.
