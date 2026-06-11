# Quality Score

> **Last reviewed:** (set the date when grading for the first time)

This document grades each product domain and architectural layer. Update grades
as work progresses; add gap entries when deficiencies are found. A recurring
review keeps debt visible and prevents silent accumulation.

## Domain grades

| Domain                | Grade | Notes                       |
|-----------------------|-------|-----------------------------|
| Test coverage (BDD)   | —     | Not yet evaluated.          |
| Test coverage (unit)  | —     | Not yet evaluated.          |
| Type safety           | —     | Not yet evaluated.          |
| Documentation         | —     | Not yet evaluated.          |
| CI / automation       | —     | Not yet evaluated.          |
| Security              | —     | Not yet evaluated.          |
| Reliability           | —     | Not yet evaluated.          |

## Grade definitions

| Grade | Meaning                                                          |
|-------|------------------------------------------------------------------|
| A     | Exceeds target. No known gaps. Mechanical checks in place.       |
| B     | Meets target. Minor gaps identified and tracked.                 |
| C     | Below target. Known gaps actively being addressed.               |
| D     | Significant gaps. Remediation required before this is reliable.  |
| —     | Not yet evaluated.                                               |

## Gap log

Add entries here as gaps are discovered. Promote them to
`docs/exec-plans/tech-debt-tracker.md` once a remediation plan exists. Each entry
records: date, domain, the gap, its impact, and the action that resolves it.
