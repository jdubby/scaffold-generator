# Exec Plan: Gate baseline

**Spec:** `docs/product-specs/gate-baseline.md`
**Started:** 2026-08-19

## Why

Gates are data now, so they can finally be run. A gate that passes against a
scaffold with no implementation asserts nothing and will keep asserting nothing;
`--baseline` is how that is caught on day one.

## Steps

1. **BDD** — `tests/features/gate_baseline.feature`, one scenario per AC.
2. **Failing unit tests** — `tests/unit/test_runner.py` (the boundary and its fake),
   `tests/unit/test_baseline.py` (classification, shell-syntax refusal, dry run,
   missing-section errors), and a round-trip test in `tests/unit/test_gates.py`.
3. **Implement**
   - `src/scaffold_generator/runner.py` — `CommandResult`, the `CommandRunner`
     protocol, `RealCommandRunner` (subprocess, `shell=False`, timeout) and
     `FakeCommandRunner` (scripted, records calls).
   - `gates.py` — `parse_rendered`, the inverse of `render`, so the format lives in
     one module and a round-trip test can pin it.
   - `src/scaffold_generator/baseline.py` — read the scaffold's gates, classify each
     command, run what is safe to run, return results.
   - `cli.py` — `--baseline DIR` and `--dry-run`.
4. **Docs** — `SECURITY.md` gains the execution rule, `ARCHITECTURE.md` the two new
   layers, `README.md` the command.
5. Quality gates, evaluator pass, close out.

## Decisions

- **The scaffold's own `AGENTS.md` is the source, not the component library.**
  `--baseline` should work on any generated scaffold without the library that
  produced it, and it verifies the artifact actually shipped. The cost is a parser
  coupled to a rendering format; a round-trip test (`render` → `parse_rendered` →
  same gates) is what makes that coupling safe, and both live in `gates.py`.
- **No shell, ever.** Commands are split with `shlex.split` and executed as an
  argument vector. A scaffold may have come from anywhere, and `SECURITY.md` already
  forbids spec-derived values reaching a shell; a gate command is the same category
  of input. A command containing shell syntax is skipped and reported rather than
  executed — which also pushes module authors toward one runnable command per gate.
- **`--baseline` never fails on gate outcomes.** It is a diagnostic. Exit non-zero
  only when the target cannot be read (AC-5). A `--strict` mode is deferred until
  something wants to consume it as a check.
- **`CommandRunner` mirrors `FileSystem`.** Protocol plus a real and a fake
  implementation in `src/`, injected from the CLI composition root, so unit tests
  honor the no-subprocess rule. The BDD layer exercises the real one.

## Outcome

- The feature earned its keep on the first real run. Against a freshly generated
  `python-cli` scaffold, `ruff check .` and `ruff format --check .` both **pass** —
  on a tree containing zero Python files. They are not broken gates, but they assert
  nothing until code exists, and that is precisely the state `--baseline` exists to
  make visible on day one instead of a year in.
- With no virtualenv on PATH the same scaffold reports all four gates as
  `unavailable`, which is the honest answer and doubles as a list of the tooling the
  stack still needs. Worth considering later whether a scaffold should ship setup
  instructions naming that tooling; out of scope here.
- Probing changed one design detail: a failing gate's one-line reason is now the
  **last** non-blank output line, not the first. Runners open with a banner and close
  with the verdict — `pytest` reported `==== test session starts ====` before the
  change and `no tests ran in 0.01s` after it.
- Python 3.14's deferred annotations (PEP 649) hid a real ordering bug: a module-level
  function annotated `list[Gate]` was defined above `Gate`. It ran fine in the local
  3.14 venv and would have failed at import on the CI's Python 3.11. `ruff` caught it
  (F821) where the test suite could not — a reminder that a green suite on one
  interpreter is not the contract.
