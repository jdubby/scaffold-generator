# Bundle the component library and core templates in this repo

**Status:** Completed 2026-06-10
**Started:** 2026-06-10
**Gap:** QUALITY_SCORE.md gap log → "[2026-06-10] The repo ships no component
library or core templates". Decision (owner, 2026-06-10): they live in this repo.

## Goal

Make `scaffold spec.yml` work out of the box: the CLI's default `--components-dir`
and `--core-dir` point at real, contract-clean content shipped with the repo.

## Deliverables

1. `core/` — all twelve files the contract validator requires, with ASSEMBLE
   markers: AGENTS.md (`agents` rows, stays ≤120 lines assembled), ARCHITECTURE.md
   (`arch`), ci.yml (`ci`, YAML-comment marker inside the `jobs:` mapping),
   docs/RELIABILITY.md (`reliability`), docs/SECURITY.md (`security`), plus README,
   EVALUATOR, DESIGN, QUALITY_SCORE, core-beliefs, tech-debt-tracker, and
   product-specs/index as marker-free templates.
2. `components/` — starter modules matching the feature file's Background:
   frontend/react-native, backend/fastapi, database/firebase. Five fragments each:
   arch.md, reliability.md, security.md, agents.md (one repo-map row), ci.yml
   (one `<name>-checks:` job).
3. `components/MODULE_AUTHORING.md` — the guide placeholder text already points to.

## Approach

1. Add AC-7 to the product spec; add a BDD scenario that generates using the
   bundled directories and asserts success with **no warnings** (no unknown
   components, no contract violations). Run → fail (directories absent).
2. Author the content. No production-code changes expected.
3. Gates, evaluator pass, resolve the gap-log entry, update README and the repo
   map, move this plan to completed.
