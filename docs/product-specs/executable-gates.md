# Product Spec: Executable quality gates

**Status:** Draft
**Feature file:** `tests/features/executable_gates.feature`

## Goal

A generated scaffold tells its agent to "run every gate this project defines
(test runner, linter, formatter, type checker)" — but nothing in the scaffold
says what those commands actually are. The commands exist only inside each
module's `ci.yml`, embedded in GitHub Actions YAML, where nothing but GitHub can
read them. Three consequences follow:

- `AGENTS.md` step 6 is unactionable without the agent reverse-engineering the
  CI file, so the delivery loop's most mechanical step is the one most open to
  interpretation.
- Nothing can verify that a module's stated gates and its CI file agree. They
  drift silently.
- The generator has no way to *run* a scaffold's gates, so it cannot answer the
  one question that matters about a fresh scaffold: do these gates execute, and
  can they fail? (See "Out of scope" — executing them is the next increment,
  and it is blocked on this one.)

Modules should declare their gate commands as data. The declaration becomes the
concrete gate list in the generated `AGENTS.md`, is checked against the module's
own `ci.yml` for drift, and gives a later increment something executable to run.

## Scope

### In scope

- A sixth module fragment, `checks.yml`, declaring named gate commands.
- Assembly of the declared gates into the generated `AGENTS.md` quality-gate
  step, behind a new `gates` marker.
- A contract check that every declared gate command appears in the module's
  `ci.yml`, reported as a warning naming the module and the missing command.
- `scaffold --list-components` reporting which modules declare gates.
- A migration path: `checks.yml` is optional on landing, the seven bundled
  modules are backfilled, and it becomes required in a separate change.

### Out of scope

- **Executing** the declared gates. `scaffold --baseline` is the next increment;
  it needs a `CommandRunner` boundary (mirroring `FileSystem`) so unit tests
  honor the no-subprocess mocking rule, and it deserves its own spec.
- **Generating `ci.yml` from the declaration.** Reversing the dependency was
  considered and rejected for this increment: the bundled modules' CI jobs carry
  stack-specific structure that a gate list cannot express — `postgres` needs a
  `services:` block with a health-check probe, `pytorch` needs a CPU-wheel extra
  index URL, and the Node modules need `setup-node` plus `npm ci`. Modeling all
  of that in `checks.yml` would rebuild GitHub Actions in YAML for no gain.
  `ci.yml` stays hand-authored; AC-3's drift check is what keeps the two honest.
  Revisit once a second CI target (or `--baseline`) makes the abstraction pay.
- Changing what the gates themselves are for any existing module. This
  increment makes existing commands legible, it does not add or alter gates.

## Acceptance criteria

### AC-1: Modules declare gates as data

Given a component module directory, when it contains `checks.yml` declaring a
list of gates — each with a `name` (a plain slug) and a `run` (the shell command
to execute) — then the generator parses it and associates those gates with the
module. A `checks.yml` that is not a valid gate list fails generation with an
error naming the module and the offending field, consistent with the existing
fragment-error contract.

### AC-2: Declared gates appear in the generated AGENTS.md

Given a spec declaring modules that between them declare gates, when a scaffold
is generated, then the quality-gate step in the generated `AGENTS.md` lists each
gate as a runnable command grouped under its module, in place of the current
generic prose. Identical commands declared by more than one module are listed
once. The assembled file must still satisfy the 120-line contract limit, so the
gate list is commands only — no per-gate explanation.

### AC-3: Declared gates are checked against the module's CI

Given a module declaring a gate whose `run` command does not appear anywhere in
that module's `ci.yml`, when a scaffold is generated from a spec including that
module, then generation succeeds and the run prints a warning naming the module,
the gate, and the missing command. This is a warning, not a failure — the same
treatment the unknown-component case already receives.

### AC-4: The component listing reports gate coverage

Given the bundled library, when the user runs `scaffold --list-components`, then
each module is shown with the number of gates it declares, and modules declaring
none are visibly marked as such.

### AC-5: A module without checks.yml still generates

Given a module with no `checks.yml`, when a scaffold is generated from a spec
including it, then generation succeeds and the run prints a warning naming the
module and pointing at `components/MODULE_AUTHORING.md`. The generated
`AGENTS.md` falls back to the current generic gate prose for that module.

### AC-6: The fragment becomes required once the library is clean

Given every bundled module declares `checks.yml`, when that backfill has landed,
then a follow-up change promotes the fragment to required — a declared module
missing it fails generation with the same clear error as any other missing
fragment, and `MODULE_AUTHORING.md` lists six required fragments rather than
five. AC-5's warning path is removed in the same change.

## Open questions

- Should a gate carry an optional `blocking: false` for gates that are advisory
  in CI but not in the delivery loop? No bundled module needs it today; adding
  the field later is backward compatible, so the default is to omit it.
- `AGENTS.md` is capped at 120 lines and a four-module stack could declare a
  dozen gates. If a realistic stack breaches the cap, the fallback is to move
  the gate list to `docs/QUALITY_GATES.md` and leave a pointer in `AGENTS.md` —
  which is the navigator role that file is supposed to play anyway. Decide when
  a real spec breaches it, not before.
- Should `core/` declare project-wide gates the same way, rather than only
  modules? Probably yes, and it would give `core/ci.yml`'s currently-unfillable
  quality-gate step something real to hold — but it is entangled with the
  tech-debt item on gates that cannot fail, so it is deliberately left out here.
