# Technical Debt Tracker

Known technical debt, organized by priority. Add entries here from
`docs/QUALITY_SCORE.md` when a remediation plan is ready. Update grades in
`docs/QUALITY_SCORE.md` as items are resolved.

## High priority

Debt that degrades reliability, correctness, or security. Address before shipping
new features.

_None open._

## Medium priority

Debt that slows development velocity or degrades maintainability. Address on a
regular cadence.

_None open._

## Low priority

Debt that is cosmetic or has low impact. Address opportunistically.

_None identified yet._

---

## Resolved

### [2026-08-19] Shipped modules declare CI gates that cannot fail
- **Priority:** High
- **Domain:** CI / automation
- **Description:** Three `ci.yml` fragments contain steps whose command is a bare `echo`
  and therefore always exit 0: `components/database/postgres/ci.yml` (migration and
  integration-test steps), `components/inference/pytorch/ci.yml` (model evaluation gate),
  and `core/ci.yml` (project-wide quality-gate step). `components/MODULE_AUTHORING.md`
  explicitly permits it today.
- **Impact:** Every project generated from those modules gets a green CI badge while
  executing zero assertions for the affected gates — false confidence in an unverified
  stack. `validator.py` cannot detect it: the contract covers required files, the
  `AGENTS.md` line limit, and unresolved assembly markers, but not whether a declared
  gate is capable of failing.
- **Remediation:** Three parts, in order.
  1. Convert the unfilled gates from `echo "Replace with…"` to `exit 1` plus a TODO
     comment, so an unwired gate fails loudly instead of passing silently. The TODO is
     legitimate at generation time; the exit code is what is wrong today.
  2. Add `_check_unfillable_gates` to `src/scaffold_generator/validator.py`, alongside
     `_check_unresolved_markers`, surfaced as a CLI warning (the precedent set by the
     unknown-component warning) rather than a hard failure.
  3. Amend `components/MODULE_AUTHORING.md` to require that an unautomated gate fail
     rather than pass, and add the rule to the pre-publish checklist.
- **Resolved:** 2026-08-19 — implemented as specified. `validator.py` gained
  `_check_unfillable_gates`, which parses the assembled `ci.yml` and reports any step
  whose commands are all no-ops (`echo`, `true`, `:`); unparseable YAML is reported
  rather than skipped, since skipping would have made the new check one that cannot
  fail. The four offending steps now carry a TODO comment plus `exit 1`, verified by
  executing the generated run block rather than reading it (exit code 1).
  `MODULE_AUTHORING.md` no longer sanctions comment-only gates and the pre-publish
  checklist covers it. Plan:
  `docs/exec-plans/completed/2026-08-19-gates-that-cannot-fail.md`.

Move items here when addressed, with the resolution date and a brief note.

### [2026-05-12] Replace live-filesystem unit tests with boundary doubles
- **Priority:** Medium
- **Domain:** Test coverage (unit)
- **Description:** Unit tests relied on `tmp_path` file creation across the loader,
  resolver, assembler, validator, writer, and CLI tests.
- **Impact:** The suite verified behavior but did not enforce the repo's
  boundary-mocking standard for filesystem-facing code.
- **Remediation:** Add injectable filesystem-facing collaborators or existing interface
  doubles where needed, then migrate the affected tests off live writes.
- **Resolved:** 2026-06-10 — added the `FileSystem` protocol
  (`scaffold_generator/filesystem.py`) with real and in-memory implementations,
  injected it into all five modules (CLI is the composition root), and migrated the
  spec, resolver, assembler, validator, and writer unit tests to the in-memory
  double. BDD scenarios and CLI-level tests stay on real `tmp_path` sandboxes by
  documented policy (AGENTS.md mocking rules). Unused conftest fixtures removed.
  Plan: `docs/exec-plans/completed/2026-06-10-filesystem-boundary-doubles.md`.

### [2026-05-12] Reconcile dependency pinning policy
- **Priority:** Medium
- **Domain:** Security
- **Description:** The security standard promises exact dependency pinning, but
  `pyproject.toml` uses ranged minimum versions.
- **Impact:** Dependency resolution is less reproducible than the policy implies, and
  security reviews do not have a single locked baseline to inspect.
- **Remediation:** Decide whether this project will use exact pins, a lockfile-driven
  policy, or relaxed ranges; then update `pyproject.toml` and/or `docs/SECURITY.md`
  so the implementation and policy agree.
- **Resolved:** 2026-06-10 — adopted exact pins matching the tested `.venv` baseline
  (click 8.3.3, pyyaml 6.0.3, jsonschema 4.26.0, pytest 9.0.3, pytest-bdd 8.1.0,
  pytest-mock 3.15.1; dev: mypy 2.1.0, ruff 0.15.12, type stubs). SECURITY.md now
  documents the deliberate-upgrade policy. Install and all gates verified green.

### [2026-05-12] Align validation and CLI failures with the documented contract
- **Priority:** High
- **Domain:** Security / Reliability
- **Description:** The implementation had not reached the documented contract for
  schema-based validation, output-path preflight checks, and stderr-only invalid-spec
  messaging.
- **Impact:** The generator's public failure behavior was weaker and less predictable
  than the product and security documents said it was.
- **Remediation:** Implement the documented checks and error channel behavior, then
  add automated tests for invalid schemas, unwritable paths, and stderr routing.
- **Resolved:** 2026-06-10 — in three parts: (1) stderr routing for CLI errors with
  unit tests (done alongside the BDD bindings work); (2) JSON-schema validation in
  `spec.py` with slug patterns for `name`/component values and structured
  field-plus-hint error messages; (3) `ScaffoldWriter.preflight` writability check
  wired into the CLI before resolution/assembly. Product spec gained AC-6 and an
  AC-3 extension; two new BDD scenarios and eight new unit tests cover the branches.
  Plan: `docs/exec-plans/completed/2026-06-10-validation-contract.md`.

### [2026-05-12] Make scaffold-generation BDD scenarios executable
- **Priority:** High
- **Domain:** Test coverage (BDD)
- **Description:** The active scaffold-generation feature file is not bound to
  pytest-bdd scenarios or step definitions, so acceptance criteria do not run in CI.
- **Impact:** Product behavior can regress while the primary workflow still appears
  "covered" in documentation only.
- **Remediation:** Add executable pytest-bdd scenario modules and step definitions for
  the active feature, then confirm `pytest` collects and passes them.
- **Resolved:** 2026-06-10 — Added `tests/step_defs/test_scaffold_generation.py`
  binding all six scenarios in `scaffold_generation.feature`; `pytest` collects and
  passes them in the standard quality gate. Making the two stderr scenarios pass
  required routing CLI error messages to stderr (`cli.py`), covered by three new
  unit tests. Plan: `docs/exec-plans/completed/2026-06-10-executable-bdd-scenarios.md`.

---

## Entry template

```
### [YYYY-MM-DD] <Short description>
- **Priority:** High / Medium / Low
- **Domain:** <domain from QUALITY_SCORE.md>
- **Description:** <what the problem is>
- **Impact:** <what degrades if left unaddressed>
- **Remediation:** <what needs to happen>
- **Resolved:** <!-- date and how it was fixed, once done -->
```
