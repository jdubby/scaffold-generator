# Product Spec: Scaffold Generation

**Status:** Active  
**Feature file:** `tests/features/scaffold_generation.feature`

---

## Goal

Enable a developer to generate a complete, BDD/TDD-ready project scaffold by
supplying a structured YAML stack spec. The scaffold must be customised for the
declared stack components without compromising the core tenets that apply to every
project: the BDD/TDD delivery loop, evaluation protocol, design quality criteria
(for frontend stacks), and contract validation.

---

## Scope

### In scope

- Shipping a starter component library (`components/`) and core templates (`core/`)
  in this repository, used by default when `--components-dir`/`--core-dir` are not
  given, plus a `MODULE_AUTHORING.md` guide for adding modules
- Accepting a YAML stack spec file as the primary input
- Resolving each declared component to a pre-authored module in the component library
- Assembling stack-agnostic core files verbatim into the output directory
- Assembling stack-specific files (ARCHITECTURE.md, RELIABILITY.md, SECURITY.md,
  AGENTS.md, ci.yml) by injecting component fragments at assembly markers
- Producing clearly-marked placeholder sections for components with no matching module
- Emitting a warning (stdout) for each unknown component, not a fatal error
- Validating the spec against a schema before any filesystem operation
- Rejecting an invalid spec with a clear error message identifying the offending field
- A `--validate` flag to check a spec without generating output
- A `--list-components` flag to list all available modules by category
- Running contract validation on the generated output and reporting failures

### Out of scope

- Generating component module content via LLM (modules are pre-authored)
- Modifying an existing project in-place (output directory must not already exist)
- Supporting spec formats other than YAML

---

## Acceptance criteria

These map directly to Gherkin scenarios in `tests/features/scaffold_generation.feature`.

### AC-1: Valid spec generates a complete scaffold

Given a valid stack spec with at least one known component per declared category,
when the generator runs, the output directory is created and contains:
- All core tenet files (AGENTS.md, EVALUATOR.md, QUALITY_SCORE.md, DESIGN.md,
  RELIABILITY.md, SECURITY.md,
  design-docs/core-beliefs.md, exec-plans/tech-debt-tracker.md,
  product-specs/index.md)
- ARCHITECTURE.md with one section per declared component
- RELIABILITY.md with one section per declared component
- SECURITY.md with one section per declared component
- AGENTS.md with quality gate commands and repository map rows from each component
- ci.yml with one job block per component

### AC-2: Unknown component produces a placeholder, not a failure

Given a stack spec that includes a component name with no matching module directory,
when the generator runs, a warning is printed to stdout naming the unknown component,
the scaffold is still written, and the affected sections contain clearly-marked
placeholder text directing the developer to MODULE_AUTHORING.md.

### AC-3: Invalid spec produces a clear error

Given a stack spec that fails schema validation (e.g. missing required `name` field,
invalid `platform` value, or a component name that is not a plain slug and could be
interpreted as a filesystem path), when the generator runs, it exits with a non-zero
code, prints an error to stderr identifying the offending field, and writes no
output files.

### AC-4: --validate checks a spec without generating output

Given a valid spec file, `--validate` exits zero and prints no errors.
Given an invalid spec file, `--validate` exits non-zero and reports the schema error.
In both cases, no output directory is created.

### AC-5: --list-components lists available modules by category

Running `--list-components` prints each available module grouped by category
(frontend, backend, database, inference) and exits zero.

### AC-6: Unwritable output path fails before generation

Given a valid spec and an output path whose nearest existing ancestor directory is
not writable, when the generator runs, it exits with a non-zero code, prints an
error to stderr identifying the output path, and writes no output files. The check
happens before component resolution and assembly begin.

### AC-7: Bundled library generates a contract-clean scaffold out of the box

The repository ships `core/` templates and a `components/` library covering at
least react-native (frontend), fastapi (backend), and firebase (database). Given a
spec declaring those components, generating with the bundled directories exits
zero, prints no warnings of any kind, and produces a scaffold that passes contract
validation: all required files present, one section per component in
ARCHITECTURE.md / RELIABILITY.md / SECURITY.md, a job block per component in
ci.yml, a repository-map row per component in AGENTS.md, and AGENTS.md within its
line limit. Placeholder text in generated output references the bundled
`MODULE_AUTHORING.md`.

---

## Open questions

- **Existing output directory:** if the output directory already exists, should the
  generator fail immediately or offer a `--force` flag to overwrite? Decision pending
  — default to fail-fast for now and add `--force` only when a test requires it.
- **AGENTS.md line limit enforcement:** the generator should enforce the 120-line
  limit on the assembled AGENTS.md as part of contract validation. If a component
  module contributes enough rows to breach the limit, should it fail or warn?
  Decision: fail with an actionable error naming the offending components.
