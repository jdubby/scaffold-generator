# Module Authoring Guide

How to add a reusable component module to this library. Placeholder sections in
generated scaffolds point here when a spec declares a component that has no
module yet.

## Layout

```
components/<category>/<module-name>/
```

- `<category>` is one of: `frontend`, `backend`, `database`, `inference`.
- `<module-name>` is a plain slug (letters, digits, `.`, `_`, `-`; no path
  separators, no leading dot) — it must match the name used in stack specs.

## Required fragments

Every module ships exactly these six files. Generation fails with a clear error
if a declared module is missing one.

| Fragment         | Assembled into              | Marker it fills |
|------------------|-----------------------------|-----------------|
| `arch.md`        | `ARCHITECTURE.md`           | `arch`          |
| `reliability.md` | `docs/RELIABILITY.md`       | `reliability`   |
| `security.md`    | `docs/SECURITY.md`          | `security`      |
| `agents.md`      | `AGENTS.md`                 | `agents`        |
| `ci.yml`         | `ci.yml`                    | `ci`            |
| `checks.yml`     | `AGENTS.md` (Quality gates) | `gates`         |

## Writing each fragment

- **arch.md / reliability.md / security.md** — one Markdown section starting with
  a `### <module-name> …` heading, then a handful of concrete, checkable rules.
  Write standards an agent can verify, not aspirations.
- **agents.md** — exactly one repository-map table row in the form
  `| <module-name> (<category>) | <where the code lives> — <what is there> |`.
- **checks.yml** — the gate commands an agent must run, as data:

  ```yaml
  gates:
    - name: lint
      run: ruff check .
    - name: test
      run: pytest
  ```

  Each `name` is a plain slug used as the label in the generated `AGENTS.md`;
  each `run` is the command itself. Every declared command must appear in this
  module's `ci.yml` — one source of truth, checked at generation time — so
  declare the commands the CI job already runs rather than aspirational ones.
  A module whose checks are inherently project-specific declares `gates: []`,
  which states "none of my own" rather than leaving the fragment out.
- **ci.yml** — one CI job keyed `<module-name>-checks:`, indented two spaces so
  it lands inside the assembled `jobs:` mapping. Every step must be able to fail.
  A gate you cannot automate yet is written to fail, not to pass:

  ```yaml
      - name: Integration tests
        run: |
          # TODO: replace with the project's integration test command.
          exit 1
  ```

  A step whose commands are all no-ops (`echo`, `true`, `:`) always exits 0, so it
  reports success for work nobody has done — a green badge over zero assertions is
  worse than no CI job at all. Contract validation reports these; see the checklist
  below.

## Checklist before publishing a module

1. All six fragment files exist and are non-empty.
2. `scaffold --list-components` shows the module under its category.
3. Generate a scaffold from a spec declaring the module and confirm the run
   prints **no warnings** — placeholder warnings mean a name mismatch, contract
   warnings mean a broken fragment.
4. No gate in `ci.yml` exits 0 without asserting something. Unwired gates fail
   with a TODO until their real command is written.
5. `checks.yml` declares every gate the CI job runs, and `scaffold
   --list-components` shows the module with the expected gate count.
6. The assembled `AGENTS.md` stays within its 120-line contract limit.
