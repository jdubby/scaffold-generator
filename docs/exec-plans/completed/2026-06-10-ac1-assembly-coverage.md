# Close the AC-1 assembly coverage gap

**Status:** Completed 2026-06-10
**Started:** 2026-06-10
**Debt item:** QUALITY_SCORE.md gap log → "[2026-06-10] Feature file covers a subset
of AC-1"

## Goal

Make every AC-1 requirement in `docs/product-specs/scaffold-generation.md`
exercisable by the BDD suite:

1. Per-component sections in docs/RELIABILITY.md and docs/SECURITY.md — already
   supported by the assembler, just never asserted. Test-only work.
2. Per-component job blocks in ci.yml and repository-map rows in AGENTS.md — **not
   implemented**. New `ci` and `agents` fragment types; ci.yml needs a YAML-comment
   marker (`# ASSEMBLE:ci`) since HTML comments are not valid YAML, and its
   placeholder text must be YAML comments. The contract validator must require
   ci.yml and detect unresolved YAML-style markers.

## Approach

1. Extend the AC-1 Gherkin scenario: section asserts for docs/RELIABILITY.md and
   docs/SECURITY.md, job-block asserts for ci.yml, repo-map-row asserts for
   AGENTS.md. Run → fail.
2. Failing unit tests: assembler (`# ASSEMBLE:` marker, `ci`/`agents` fragment
   types, YAML-comment placeholder, missing-fragment error), validator (ci.yml
   required, unresolved `# ASSEMBLE:` flagged).
3. Implement minimum in `assembler.py` and `validator.py`.
4. Update step-def fixtures (core templates gain markers + ci.yml; library modules
   gain `agents.md` and `ci.yml` fragments).
5. Gates, evaluator pass, resolve the gap-log entry, move plan to completed.

## Out of scope

- Authoring a real component library / core templates (tracked separately as an
  open question — the repo ships neither).
