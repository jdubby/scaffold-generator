# Agent Workflow: Scaffold Generator

## Core mandate

Behavior first, tests second, implementation third. Do not write or modify production
code until the expected behavior is defined and at least one failing automated test
exists for the next increment.

## Delivery loop

0. **Plan** — For new features: check `docs/product-specs/` for an existing spec.
   If none exists, write one before any Gherkin is written. A spec defines what users
   can do and what "done" looks like — not how the code is structured. See
   `docs/product-specs/index.md` for the template. For bug fixes and refactors: skip
   to step 1.
1. **BDD first** — Write or update a Gherkin scenario in `tests/features/` before
   implementation begins. Scenarios must be grounded in a product spec.
2. **TDD second** — Write one failing unit test in `tests/unit/`. Run `pytest` and
   show the failure.
3. **Implement minimum** — Write only enough code to make the active failing test pass.
4. **Refactor** — Clean up only after the test suite is green.
5. **Quality gates** — All must pass before evaluation:
   - `pytest`
   - `ruff check .`
   - `ruff format --check .`
   - `mypy src tests`
6. **Evaluate** — Apply the evaluation protocol in `docs/EVALUATOR.md` before marking
   the task complete. If any criterion falls below B, return to step 3 and revise.

## Python environment

- Use a project-local virtual environment named `.venv`.
- Create it with `python3 -m venv .venv` if it does not exist.
- Activate `.venv` before installing dependencies or running Python commands.
- Do not install dependencies into the system interpreter.

## Mocking rules

- Module unit tests make no live filesystem writes, network calls, or subprocess
  invocations. Substitute the `FileSystem` boundary
  (`src/scaffold_generator/filesystem.py`) with `InMemoryFileSystem`.
- Exception: BDD scenarios and CLI-level tests are the end-to-end proof layer. They
  exercise the real filesystem inside pytest `tmp_path` sandboxes — an acceptance
  test that mocks the filesystem cannot prove the scaffold is actually written.
- Every external boundary (filesystem read, schema validation, component lookup) needs
  at least one failure-path test.

## Repository map

| What                    | Where                          |
|-------------------------|--------------------------------|
| CLI entry point         | `src/scaffold_generator/cli.py`      |
| Spec loader & validator | `src/scaffold_generator/spec.py`     |
| Component resolver      | `src/scaffold_generator/resolver.py` |
| File assembler          | `src/scaffold_generator/assembler.py`|
| Output writer           | `src/scaffold_generator/writer.py`   |
| Contract validator      | `src/scaffold_generator/validator.py`|
| Filesystem boundary     | `src/scaffold_generator/filesystem.py`|
| Component module library| `components/` (guide: `components/MODULE_AUTHORING.md`) |
| Core scaffold templates | `core/`                        |
| BDD scenarios           | `tests/features/`              |
| Step definitions        | `tests/step_defs/`             |
| Unit tests              | `tests/unit/`                  |

Do not create alternative locations without updating `ARCHITECTURE.md`.

## Knowledge base

The `docs/` directory is the system of record. Pull in context before starting
non-trivial work. Anything not in the repository is invisible to the agent.

| Context                          | Location                                   |
|----------------------------------|--------------------------------------------|
| Agent-first operating principles | `docs/design-docs/core-beliefs.md`         |
| Architecture, domain map, layers | `ARCHITECTURE.md`                          |
| Product specs (feature scope)    | `docs/product-specs/`                      |
| Quality grades by domain         | `docs/QUALITY_SCORE.md`                    |
| Evaluation protocol              | `docs/EVALUATOR.md`                        |
| In-flight execution plans        | `docs/exec-plans/active/`                  |
| Known technical debt             | `docs/exec-plans/tech-debt-tracker.md`     |
| Documentation principles         | `docs/DESIGN.md`                           |
| Reliability and error-handling   | `docs/RELIABILITY.md`                      |
| Security rules                   | `docs/SECURITY.md`                         |

For complex tasks: create a plan file in `docs/exec-plans/active/` before
implementation. Move it to `docs/exec-plans/completed/` when done.

## README maintenance

`README.md` is part of the product. Update it in the same task whenever setup,
commands, structure, or visible behavior changes. See `docs/DESIGN.md` for
documentation principles. Do not leave stale instructions.

## Change discipline

Do not add frameworks, infrastructure, or abstractions until tests justify them.
State assumptions in task summaries. If the correct approach is uncertain, write a
plan in `docs/exec-plans/active/` first.
