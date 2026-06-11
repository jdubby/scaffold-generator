# Grow the component library: nextjs, postgres, pytorch

**Status:** Completed 2026-06-10
**Started:** 2026-06-10
**Grounding:** product spec AC-7 ("at least react-native, fastapi, firebase" — this
extends coverage to all four categories).

## Goal

Every spec category has at least one bundled module: nextjs (frontend), postgres
(database), pytorch (inference) join the existing react-native, fastapi, firebase.

## Approach

1. Add a BDD scenario under AC-7: a web-platform spec declaring nextjs, fastapi,
   postgres, and pytorch generates warning-free from the bundled directories with
   sections, job blocks, and repo-map rows present. Run → fails (placeholders).
2. Add a standing guard: a CLI-level test that discovers every module in
   `components/`, declares them all in one spec, and generates with the bundled
   defaults asserting exit 0 and no warnings. Catches incomplete fragments for any
   future module automatically.
3. Author the three modules per `components/MODULE_AUTHORING.md` — five fragments
   each (arch, reliability, security, agents row, `<name>-checks:` CI job).
4. Update README's bundled-module list and the example spec's inference comment to
   reference a real module.
5. Gates, evaluator pass, commit, push, confirm CI green, archive this plan.
