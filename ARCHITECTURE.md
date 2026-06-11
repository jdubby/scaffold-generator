# Architecture

## Domain map

| Domain              | Responsibility                                              | Primary modules              |
|---------------------|-------------------------------------------------------------|------------------------------|
| CLI                 | Entry point, argument parsing, user-facing output           | `cli.py`                     |
| Spec                | Load, parse, and validate the YAML stack spec               | `spec.py`                    |
| Resolver            | Map spec components to module directories or placeholders   | `resolver.py`                |
| Assembler           | Combine core templates and component fragments into files   | `assembler.py`               |
| Writer              | Write assembled files to the output directory               | `writer.py`                  |
| Validator           | Check the output scaffold satisfies the contract rules      | `validator.py`               |
| Filesystem          | Substitutable boundary for all filesystem access            | `filesystem.py`              |

## Package layering

Dependencies flow in one direction only. A lower layer must never import from a higher one.

```
Spec → Resolver → Assembler → Writer
                            ↘
                          Validator
CLI → (orchestrates all layers)
```

| Layer     | Responsibility                                        | May depend on              |
|-----------|-------------------------------------------------------|----------------------------|
| Spec      | YAML parsing, schema validation, typed spec model     | nothing                    |
| Resolver  | Component lookup, placeholder generation              | Spec                       |
| Assembler | Template loading, marker replacement, fragment join   | Spec, Resolver             |
| Writer    | Filesystem writes, directory creation                 | Assembler                  |
| Validator | Contract assertions on the written output             | nothing (reads filesystem) |
| CLI       | Orchestration, error formatting, exit codes           | all layers                 |

## Key interfaces

Each layer exposes a narrow interface that test doubles can substitute:

- **`SpecLoader`** — reads a path, returns a validated `StackSpec` dataclass
- **`ComponentResolver`** — given a `StackSpec`, returns `list[ResolvedComponent]`
  (each either a real module path or a `Placeholder`)
- **`FileAssembler`** — given a template and components, returns assembled file content
- **`ScaffoldWriter`** — given an output directory and assembled content, writes files
- **`ContractValidator`** — given an output directory, returns `list[ValidationError]`
- **`FileSystem`** — protocol behind all filesystem access; `RealFileSystem` in
  production, `InMemoryFileSystem` in module unit tests. Each collaborator above
  accepts an optional `fs` argument; the CLI is the composition root that constructs
  the real one.

## Dependency rules

- No circular imports anywhere in `src/`.
- No lower layer may import from a higher layer.
- No production code may live in `tests/`.
- All filesystem reads and writes in production code go through the `FileSystem`
  boundary in `filesystem.py` — no bare `open()` or direct `pathlib` I/O calls in
  other modules.
- `validator.py` reads the filesystem but never writes. It is invoked by the CLI
  after the writer completes, not by the writer itself.

## Naming conventions

| Thing                  | Convention              |
|------------------------|-------------------------|
| Modules                | `snake_case`            |
| Public classes         | `PascalCase`            |
| Public functions/vars  | `snake_case`            |
| Constants              | `UPPER_SNAKE_CASE`      |
| Unit test files        | `test_<module>.py`      |
| BDD feature files      | `<feature>.feature`     |

## File size

Source files over 400 lines are a signal to extract into a submodule. Keeping files
small makes the codebase navigable to both agents and humans.

## Design decisions

Significant architectural decisions are recorded in `docs/design-docs/`. Reference
the index at `docs/design-docs/index.md` before making changes that cross domain or
layer boundaries.