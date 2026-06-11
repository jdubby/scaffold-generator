# Quality Score

> **Last reviewed:** 2026-06-10

This document grades each product domain and architectural layer. Update grades as
work progresses. Add gap entries when deficiencies are found. A recurring review of
this document keeps debt visible and prevents silent accumulation.

## Domain grades

| Domain                | Grade | Notes                                                                 |
|-----------------------|-------|-----------------------------------------------------------------------|
| Test coverage (BDD)   | B     | All nine scaffold-generation scenarios run via pytest-bdd and pass, including out-of-the-box generation from the bundled library. |
| Test coverage (unit)  | B     | 57 unit tests; module tests run against the in-memory filesystem double. |
| Type safety           | B     | `mypy src tests` passes under strict configuration.                  |
| Documentation         | B     | Core docs and README are maintained; remaining status gaps are tracked below. |
| CI / automation       | B     | Workflow runs all four gates plus knowledge-base checks; verified locally, executes on push once a remote exists. |
| Security              | B     | Schema validation, slug-constrained spec values, and output-path preflight are implemented and tested. Dependency pinning mismatch still tracked. |
| Reliability           | B     | Error paths are schema-structured, stderr-routed, and covered end-to-end. Boundary-double migration still tracked. |

## Grade definitions

| Grade | Meaning                                                            |
|-------|--------------------------------------------------------------------|
| A     | Exceeds target. No known gaps. Mechanical checks in place.         |
| B     | Meets target. Minor gaps identified and tracked.                   |
| C     | Below target. Known gaps actively being addressed.                 |
| D     | Significant gaps. Remediation required before this is reliable.    |
| —     | Not yet evaluated.                                                 |

## Gap log

Add gap entries here as they are discovered. Promote to
`docs/exec-plans/tech-debt-tracker.md` when a remediation plan is ready.

<!--
### [YYYY-MM-DD] <Short description>
- **Domain:** <domain name>
- **Gap:** <what is missing or wrong>
- **Impact:** <what degrades or breaks if left unaddressed>
- **Action:** <what needs to happen to resolve it>
-->

### [2026-05-12] BDD scenarios are descriptive, not executable
- **Domain:** Test coverage (BDD)
- **Gap:** `tests/features/scaffold_generation.feature` exists, but pytest currently
  collects only unit tests; no step definitions bind the scenarios to executable
  checks.
- **Impact:** Product acceptance criteria can drift from implementation without a
  failing end-to-end test.
- **Action:** Add pytest-bdd scenario bindings and step definitions for the active
  scaffold-generation feature, then require those scenarios in the quality gate.
- **Resolved:** 2026-06-10 — `tests/step_defs/test_scaffold_generation.py` binds all
  six scenarios; `pytest` collects and passes them as part of the standard gate.

### [2026-06-10] Feature file covers a subset of AC-1
- **Domain:** Test coverage (BDD)
- **Gap:** `docs/product-specs/scaffold-generation.md` AC-1 requires per-component
  sections in RELIABILITY.md and SECURITY.md and per-component job blocks in ci.yml,
  but `scaffold_generation.feature` only asserts sections in ARCHITECTURE.md.
- **Impact:** Those assembly targets could regress without a failing scenario.
- **Action:** Extend the AC-1 scenario (or add scenarios) to assert RELIABILITY.md,
  SECURITY.md, and ci.yml assembly, then bind them in the existing step definitions.
- **Resolved:** 2026-06-10 — AC-1 scenario now asserts per-component sections in
  docs/RELIABILITY.md and docs/SECURITY.md, job blocks in ci.yml, and repository-map
  rows in AGENTS.md. Required implementing `ci`/`agents` fragment types with a
  YAML-comment marker (`# ASSEMBLE:type`), YAML-safe placeholders, and contract
  validation for ci.yml. Plan: `docs/exec-plans/completed/2026-06-10-ac1-assembly-coverage.md`.

### [2026-06-10] The repo ships no component library or core templates
- **Domain:** Documentation / Reliability
- **Gap:** The CLI's default `--components-dir` and `--core-dir` point at `components/`
  and `core/` at the repo root, but neither directory exists. Out of the box,
  `scaffold spec.yml` cannot generate anything; every test fabricates its own library
  and templates. `MODULE_AUTHORING.md`, referenced by placeholder text, also does not
  exist anywhere.
- **Impact:** The product is not usable end-to-end without externally supplied
  content, and nothing documents where that content should come from.
- **Action:** Decide whether the library and core templates live in this repo or
  elsewhere. Either author them (with `MODULE_AUTHORING.md`) or document the external
  location and make the CLI defaults fail with a helpful message.
- **Resolved:** 2026-06-10 — decision (owner): they live in this repo. Authored
  `core/` (all twelve contract files with assembly markers), `components/` with
  react-native, fastapi, and firebase modules (five fragments each), and
  `components/MODULE_AUTHORING.md`. Covered by product-spec AC-7 and a BDD scenario
  generating with the bundled defaults and asserting a warning-free, contract-clean
  scaffold. Plan: `docs/exec-plans/completed/2026-06-10-bundled-library.md`.

### [2026-06-10] Spec file format was undocumented
- **Domain:** Documentation
- **Gap:** Nothing user-facing documented the stack-spec YAML format; the only
  references were the JSON schema in `spec.py` and the test fixtures.
- **Impact:** New users could not write a spec without reading source code.
- **Action:** Add a spec-format guide to the README and ship a runnable example.
- **Resolved:** 2026-06-10 — README gained a "Spec format" section with the field
  reference and validation rules; `examples/stack-spec.yml` ships as an annotated,
  runnable example. Two CLI-level tests validate and generate from the example with
  the bundled defaults, so it cannot silently drift from the schema or the library.

### [2026-06-10] Quality gates run locally only — no CI pipeline
- **Domain:** CI / automation
- **Gap:** The four quality gates are defined and pass locally, but the project has no
  CI configuration (and is not currently a git repository), so nothing enforces them
  mechanically.
- **Impact:** A regression can land silently if a contributor skips the gates.
- **Action:** Initialise version control if intended, then add a CI workflow that runs
  `pytest`, `ruff check`, `ruff format --check`, and `mypy src tests`.
- **Resolved:** 2026-06-10 — correction: a workflow already existed at
  `.github/workflows/ci.yml` (all four gates plus a knowledge-base structure check,
  including the AGENTS.md 120-line limit) but was inert without version control.
  `git init` has now been run; the workflow's checks were verified to pass against
  the current tree (AGENTS.md at 98 lines, knowledge base complete, YAML valid).
  The workflow targets Python 3.11 — the `requires-python` floor — complementing
  local testing on 3.14. It executes once the repo is pushed to a GitHub remote.

### [2026-05-12] Validation and error-channel guarantees are not yet aligned
- **Domain:** Security / Reliability
- **Gap:** The product and security docs promise schema-backed validation before
  filesystem work, writable output-path validation, and stderr for invalid-spec
  errors. The current implementation performs manual field checks and does not
  preflight writability. (Stderr routing for CLI errors was implemented and tested
  on 2026-06-10; schema-backed validation and writability preflight remain open.)
- **Impact:** The documented safety contract is stronger than the implementation, and
  callers cannot rely on the described failure behavior.
- **Action:** Implement the documented schema validation and output-path checks, and
  cover each branch with automated tests.
- **Resolved:** 2026-06-10 — `spec.py` validates against a JSON schema (slug patterns
  for `name` and component values, structured errors with field path and hint);
  `writer.py` preflights output-path writability before generation; CLI routes all
  failures to stderr. Covered by unit tests and BDD scenarios (AC-3 extension, AC-6).

### [2026-05-12] Automated tests still use live filesystem writes
- **Domain:** Test coverage (unit)
- **Gap:** Multiple unit tests and helpers write through `tmp_path`, despite the repo
  standard requiring external boundaries to be replaced by test doubles.
- **Impact:** The suite currently validates behavior, but it does not yet prove the
  intended substitution boundaries for filesystem-facing collaborators.
- **Action:** Introduce or expand boundary doubles around spec loading, template reads,
  validation reads, and scaffold writes so tests exercise the contracts without live
  filesystem writes.
- **Resolved:** 2026-06-10 — `scaffold_generator/filesystem.py` introduces a
  `FileSystem` protocol with `RealFileSystem` and `InMemoryFileSystem`; all five
  modules accept an injected `fs` and their unit tests run on the in-memory double.
  BDD scenarios and CLI-level tests intentionally stay on real `tmp_path` sandboxes
  as the end-to-end layer — the exception is codified in AGENTS.md.

### [2026-05-12] Dependency policy is documented more strictly than configured
- **Domain:** Security
- **Gap:** `docs/SECURITY.md` says dependencies are pinned to specific versions, while
  `pyproject.toml` currently uses lower-bound ranges such as `click>=8.1.0`.
- **Impact:** Reproducibility and vulnerability review are weaker than the documented
  policy suggests.
- **Action:** Choose and document the intended dependency strategy, then either pin the
  project dependencies or revise the security standard to match the approved model.
- **Resolved:** 2026-06-10 — chose exact pinning to match the documented policy.
  `pyproject.toml` pins every runtime and dev dependency to the tested baseline
  versions; `docs/SECURITY.md` now documents the deliberate-upgrade expectation.
