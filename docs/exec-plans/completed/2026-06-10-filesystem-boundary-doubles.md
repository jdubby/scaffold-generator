# Migrate unit tests to filesystem boundary doubles

**Status:** Completed 2026-06-10
**Started:** 2026-06-10
**Debt item:** tech-debt-tracker.md → "Replace live-filesystem unit tests with
boundary doubles" (Medium)

## Goal

Make the filesystem an explicit, substitutable boundary so module unit tests run
against an in-memory double, per the AGENTS.md mocking rules and the RELIABILITY.md
standard ("filesystem reads are wrapped behind interfaces that can be substituted
in tests").

## Design

- `src/scaffold_generator/filesystem.py`: a `FileSystem` Protocol (exists, is_file,
  is_dir, read_text, write_text, list_dir, walk_files, is_writable_dir) plus
  `RealFileSystem`.
- `tests/fakes.py`: `InMemoryFileSystem` test double.
- `SpecLoader`, `ComponentResolver`, `FileAssembler`, `ContractValidator`, and
  `ScaffoldWriter` accept an optional `fs` collaborator (default `RealFileSystem`).
- The CLI is the composition root: it constructs one `RealFileSystem` and passes it
  down; `--list-components` and core-template traversal go through it too.

## Test policy decision

Module unit tests (spec, resolver, assembler, validator, writer) migrate to the
in-memory fake. BDD scenarios and CLI-level tests deliberately stay on real
filesystem `tmp_path` sandboxes: they are the end-to-end proof that real
filesystem behavior works — the evaluator protocol warns against acceptance tests
that mock the part that would fail in production. AGENTS.md's mocking rules are
amended to state this exception explicitly.

## Steps

1. Add `filesystem.py` and `tests/fakes.py`.
2. Migrate module unit tests to inject the fake (fails until injection exists).
3. Implement injection in the five modules and wire the CLI.
4. Quality gates; update AGENTS.md mocking rules and ARCHITECTURE.md repo map.
5. Resolve the tracker item; evaluator pass; move this plan to completed.
