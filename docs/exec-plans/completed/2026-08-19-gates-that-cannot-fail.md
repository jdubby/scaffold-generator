# Exec Plan: Gates that cannot fail

**Debt item:** `docs/exec-plans/tech-debt-tracker.md` — [2026-08-19] Shipped modules
declare CI gates that cannot fail
**Spec:** `docs/product-specs/scaffold-generation.md` (AC-7 today; AC-8 added by this plan)
**Started:** 2026-08-19

## Why

Three shipped `ci.yml` fragments declare gate steps whose command is a bare `echo`,
so the step always exits 0: `components/database/postgres/ci.yml` (migration and
integration-test steps), `components/inference/pytorch/ci.yml` (model evaluation
gate), and `core/ci.yml` (project-wide quality-gate step) — the last of which lands
in *every* generated scaffold. A project generated from these gets a green CI badge
while executing zero assertions for the affected gates: false confidence, which is
worse than shipping no job at all.

`components/MODULE_AUTHORING.md` currently sanctions this ("Comment-only content is
also valid YAML if the module has no automatable checks yet"), and `validator.py`
cannot detect it — the contract covers required files, the `AGENTS.md` line limit,
and unresolved assembly markers, but never whether a declared gate is capable of
failing.

The fix is not to remove the TODO. An unwired gate is legitimate at generation time;
the user is expected to fill it in. What is wrong is the exit code. `exit 1` with a
TODO comment keeps CI red until a human wires the real command, which is the correct
signal for work that has not been done.

## Steps

1. **Spec** — add AC-8 to `docs/product-specs/scaffold-generation.md`: a generated
   `ci.yml` step whose only command is an `echo` (or `true`, or `:`) produces a
   warning naming the file and the step, and the bundled library produces none.
   AC-7's existing "prints no warnings of any kind" then covers the library itself.
2. **BDD (the scenario that must exist)** — add one scenario to
   `tests/features/scaffold_generation.feature`: a spec declaring a module whose
   `ci.yml` gate is a bare `echo` generates successfully **and** prints a warning
   naming the module and step. Bind it in `tests/step_defs/test_scaffold_generation.py`
   using a fabricated component library, as the existing non-bundled scenarios do.

   This scenario is the load-bearing one. The three existing AC-7 scenarios
   (lines 93, 115, 136) only assert that *no* warning appears on clean input — they
   would all pass against a check that never fires. Without a positive-detection
   scenario, this increment could ship a check that cannot fail, which is the exact
   defect it exists to remove.
3. **Failing unit tests** — `tests/unit/test_validator.py`:
   - a `ci.yml` whose step `run` is a single `echo` yields a finding naming the step;
   - `echo` combined with a real command in the same `run` block yields nothing;
   - `true` and `:` as sole commands yield findings;
   - a `ci.yml` that is not parseable YAML yields its own distinct finding;
   - the bundled `core/ci.yml`, post-fix, yields nothing.
4. **Implement** — add `_check_unfillable_gates` to
   `src/scaffold_generator/validator.py` alongside `_check_unresolved_markers`. Parse
   the generated `ci.yml` with `yaml.safe_load` (pyyaml is already a pinned
   dependency), walk `jobs.<job>.steps[].run`, and flag any step whose commands, after
   stripping comments and blank lines, are all no-ops. Run the suite and confirm the
   three AC-7 scenarios now **fail** — that failure is the proof the check works
   against real library content.
5. **Fix the library** — only after step 4 is red. Convert the four offending steps
   from `echo "Replace with…"` to `exit 1` with the same text as a TODO comment:
   `core/ci.yml`, `components/database/postgres/ci.yml` (x2),
   `components/inference/pytorch/ci.yml`. Re-run; the three AC-7 scenarios go green.
6. **Docs** — amend `components/MODULE_AUTHORING.md`: replace the comment-only
   allowance with the rule that an unautomated gate must fail rather than pass, and
   add "no gate in `ci.yml` exits 0 without asserting anything" to the pre-publish
   checklist. Update `README.md` only if the warning list it documents changes.
7. **Quality gates** — `pytest`, `ruff check .`, `ruff format --check .`,
   `mypy src tests`.
8. **Close out** — apply `docs/EVALUATOR.md`; mark the debt item resolved; restore
   CI / automation to B in `docs/QUALITY_SCORE.md` and refresh the scenario/test
   counts; move this plan to `docs/exec-plans/completed/`.

## Decisions

- **Warning, not failure — and it needs no new machinery.** `cli.py` already prints
  `ContractValidator` findings under "Contract validation warnings:" without touching
  the exit code, so adding a check to the validator yields warning semantics for free.
  (Note in passing: the class is named `ValidationError` while the CLI calls the
  findings warnings. Pre-existing naming drift, deliberately not touched here.)
- **Parse the YAML, do not regex it.** Detection needs step boundaries, and `run`
  blocks are multi-line. A parse failure therefore gets its own finding rather than a
  silent skip — skipping on unparseable input would itself be a check that cannot
  fail, which is the defect under repair.
- **Validate the assembled output, not the fragments.** A bad fragment surfaces in the
  assembled `ci.yml`, so one check in `validator.py` covers both the bundled library
  and any user-supplied `--components-dir`. No separate authoring-time lint.
- **Order matters: check before fix.** Fixing the fragments first would keep the three
  AC-7 scenarios green throughout and destroy the evidence that the new check does
  anything. Land the check, watch them fail, then fix.
- **`true` and `:` are in scope; a bare comment-only `run` is not.** A step that runs
  nothing at all is a different (and rarer) shape; leave it until a real module
  produces one.
- **Out of scope, found while planning:** `scaffold-generation.md` AC-1 promises
  "AGENTS.md with quality gate commands and repository map rows from each component",
  but no component contributes gate commands — `core/AGENTS.md` carries only the
  `ASSEMBLE:agents` marker for repository-map rows, and the feature file asserts only
  those rows. That clause of AC-1 has never been implemented or tested. It is the
  same ground `docs/product-specs/executable-gates.md` covers, so it belongs to that
  increment, not this one; it needs its own gap-log entry.
