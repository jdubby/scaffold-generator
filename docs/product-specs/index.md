# Product Specifications

This directory contains feature specifications that define user-facing behavior.
Each spec drives the BDD scenarios in `tests/features/`.

## Index

| Spec | Feature file | Status |
|------|-------------|--------|
| [Scaffold generation](./scaffold-generation.md) | `tests/features/scaffold_generation.feature` | Active |

## How to write a spec

A product spec defines:

1. **Goal** — what user problem this solves
2. **Scope** — what is in and out of scope for this increment
3. **Acceptance criteria** — the testable conditions for "done" (map directly to
   Gherkin scenarios)
4. **Open questions** — anything that needs resolution before implementation starts

Name the file `<feature-slug>.md` and add a row to the index table above.
