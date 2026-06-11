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

Every module ships exactly these five files. Generation fails with a clear error
if a declared module is missing one.

| Fragment         | Assembled into            | Marker it fills        |
|------------------|---------------------------|------------------------|
| `arch.md`        | `ARCHITECTURE.md`         | `arch`                 |
| `reliability.md` | `docs/RELIABILITY.md`     | `reliability`          |
| `security.md`    | `docs/SECURITY.md`        | `security`             |
| `agents.md`      | `AGENTS.md`               | `agents`               |
| `ci.yml`         | `ci.yml`                  | `ci`                   |

## Writing each fragment

- **arch.md / reliability.md / security.md** — one Markdown section starting with
  a `### <module-name> …` heading, then a handful of concrete, checkable rules.
  Write standards an agent can verify, not aspirations.
- **agents.md** — exactly one repository-map table row in the form
  `| <module-name> (<category>) | <where the code lives> — <what is there> |`.
- **ci.yml** — one CI job keyed `<module-name>-checks:`, indented two spaces so
  it lands inside the assembled `jobs:` mapping. Comment-only content is also
  valid YAML if the module has no automatable checks yet.

## Checklist before publishing a module

1. All five fragment files exist and are non-empty.
2. `scaffold --list-components` shows the module under its category.
3. Generate a scaffold from a spec declaring the module and confirm the run
   prints **no warnings** — placeholder warnings mean a name mismatch, contract
   warnings mean a broken fragment.
4. The assembled `AGENTS.md` stays within its 120-line contract limit.
