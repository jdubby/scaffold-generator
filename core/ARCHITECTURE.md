# Architecture

## Stack components

One section per declared stack component, contributed by its library module.
Complete any placeholder section before building features that touch it.

<!-- ASSEMBLE:arch -->

## Dependency rules

- Dependencies flow in one direction only; a lower layer never imports from a
  higher one.
- Define this project's layer boundaries here as the codebase takes shape, and
  keep this document in sync with the code.
- Record significant architectural decisions in `docs/design-docs/`.

## File size

Source files over 400 lines are a signal to extract a submodule. Small files keep
the codebase navigable to both agents and humans.
