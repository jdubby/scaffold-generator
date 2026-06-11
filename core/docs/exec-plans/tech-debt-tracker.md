# Technical Debt Tracker

Known technical debt, organized by priority. Add entries here from
`docs/QUALITY_SCORE.md` when a remediation plan is ready. Update grades in
`docs/QUALITY_SCORE.md` as items are resolved.

## High priority

Debt that degrades reliability, correctness, or security. Address before
shipping new features.

_None identified yet._

## Medium priority

Debt that slows development velocity or degrades maintainability. Address on a
regular cadence.

_None identified yet._

## Low priority

Debt that is cosmetic or has low impact. Address opportunistically.

_None identified yet._

---

## Resolved

Move items here when addressed, with the resolution date and a brief note.

_None resolved yet._

---

## Entry template

```
### [YYYY-MM-DD] <Short description>
- **Priority:** High / Medium / Low
- **Domain:** <domain from QUALITY_SCORE.md>
- **Description:** <what the problem is>
- **Impact:** <what degrades if left unaddressed>
- **Remediation:** <what needs to happen>
- **Resolved:** <!-- date and how it was fixed, once done -->
```
