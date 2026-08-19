# Exec Plan: Executable quality gates

**Spec:** `docs/product-specs/executable-gates.md`
**Started:** 2026-08-19

## Why

A module's gate commands exist only inside its `ci.yml`, embedded in GitHub Actions
YAML. The generated `AGENTS.md` tells an agent to "run every gate this project
defines" without saying what they are — and `scaffold-generation.md` AC-1 has always
promised those commands are there. Declaring gates as data closes that unmet clause,
lets drift between a module's stated gates and its CI be detected, and gives a later
`--baseline` increment something executable to run.

## Steps

Two commits, not the three first planned. Commits 1 and 2 had to merge: landing the
fragment before backfilling the library left every bundled module warning "declares no
quality gates", which is a red suite, and committing red is worse than a coarser split.
The migration window the split existed to protect turned out to be zero commits long.

### Commit 1 — the fragment, optional

1. **BDD** — scenarios in `tests/features/executable_gates.feature`, one per AC:
   gates assembled into `AGENTS.md` (AC-2), drift warning (AC-3), gate counts in
   `--list-components` (AC-4), missing `checks.yml` warns but generates (AC-5),
   malformed `checks.yml` fails with a field-naming error (AC-1).
2. **Failing unit tests** — `tests/unit/test_gates.py` for parsing, validation,
   dedup, and drift; additions to `test_assembler.py` for the `gates` marker and
   `test_cli.py` for the listing and warnings.
3. **Implement**
   - `src/scaffold_generator/gates.py` — `Gate` dataclass, `load_gates` (parse and
     validate one module's `checks.yml`), `render` (grouped, deduped Markdown), and
     `drift_warnings` (declared command absent from the module's `ci.yml`).
   - `assembler.py` — route the `gates` marker to the renderer instead of the
     verbatim fragment join.
   - `cli.py` — echo drift and missing-fragment warnings; gate counts in
     `--list-components`.
   - `core/AGENTS.md` — a `## Quality gates` section carrying
     `<!-- ASSEMBLE:gates -->`, and step 6 pointing at it.
   - `spec.py` — promote `_SLUG_PATTERN` to `SLUG_PATTERN` so gate names are held to
     the same rule as component names.
4. **Docs** — `MODULE_AUTHORING.md` gains the fragment (marked optional for now),
   `ARCHITECTURE.md` gains the Gates domain and layering row, `README.md` notes the
   new warnings.

### Commit 2 — backfill the bundled library

5. Write `checks.yml` for all seven modules, lifting the commands already present in
   each `ci.yml` so the drift check passes. Confirm no scenario reports drift and the
   assembled `AGENTS.md` stays within its 120-line limit for the widest bundled stack.

### Commit 3 — promote to required

6. Make the fragment required: a declared module missing `checks.yml` fails
   generation like any other missing fragment (AC-6). Remove the AC-5 warning path
   and its scenario, update `MODULE_AUTHORING.md` to six required fragments, and
   reword `scaffold-generation.md` AC-1 to name the gates marker.

## Decisions

- **`gates.py` is a new layer between Resolver and Assembler.** It reads module
  fragments through the `FileSystem` boundary and returns data; the assembler asks it
  to render. Keeps the assembler's generic marker path — read fragment, join verbatim
  — intact for the five existing fragment types.
- **The `gates` marker cannot use the generic path.** Every other marker injects its
  fragment verbatim; this one transforms YAML data into Markdown. That is why the
  marker is special-cased rather than added to `_FRAGMENT_FILENAME`.
- **Drift is a substring check against the raw `ci.yml` text**, not a parse. A gate
  command legitimately appears inside a larger shell line (`ruff check . && ruff
  format --check .`), so containment is the honest test; anything stricter would
  produce false drift.
- **Duplicate commands are listed once, first module wins.** Two backend modules can
  declare `pytest`; the agent should be told to run it once. The rendering groups by
  module, and a command already listed under an earlier module is skipped.
- **A gate carries a `name` as well as a `run`.** The name is the label in the
  generated list (`lint — \`ruff check .\``), which is what makes the section readable
  rather than a wall of commands.
- **Not in this plan:** executing the gates. That is `--baseline`, it needs a
  `CommandRunner` boundary to honor the no-subprocess mocking rule, and it gets its
  own spec.

## Outcome

- The 120-line `AGENTS.md` cap held: the widest possible stack (all seven bundled
  modules) generates 105 lines, with command deduplication buying the headroom. The
  spec's open question is answered by measurement.
- Backfilling surfaced a case the spec had not anticipated: `postgres` has no runnable
  gates of its own, because migrations and integration tests are project-specific. That
  produced the empty-declaration rule — `gates: []` states "none of my own" and is
  silent, while an absent fragment is an incomplete module and fails generation. AC-5
  was rewritten around it.
- Closes the `scaffold-generation.md` AC-1 drift logged on 2026-08-19: the criterion
  promised gate commands in `AGENTS.md` that no component had ever contributed.
