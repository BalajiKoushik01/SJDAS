# SJDAS release and loom qualification evidence

## Current engineering baseline

The repository contains a PyQt6 design application, FastAPI back-end, image-processing/export logic and a test suite. The GitHub `quality.yml` workflow runs Python tests headlessly and checks web lint/build. Earlier dated reports contain point-in-time UI/import checks, not proof of a fully validated industrial release.

## Acceptance gates for production/pilot

| Gate | Evidence needed |
| --- | --- |
| Clean installation | OS, Python/node versions, pinned dependencies, install commands and reproducible first launch |
| Unit and integration tests | Exact commit SHA, pass/fail/skipped counts, warnings and coverage; failures must not be hidden |
| Designer workflows | Open, edit, undo/redo, motif reconstruction, export and reopen across representative sample sets |
| File compatibility | Indexed BMP pixel/palette checks, repeat widths, float constraints and hash-verified saved artifacts |
| Physical loom | Named controller/firmware, isolated test setup, operator-approved test plan, verified output and safety interlocks |
| Background AI | Required model files/provider keys, explicit fallback behavior, performance on representative designs |
| Data security | Authentication, authorization, secret storage, tenant/job isolation, upload limits, log retention, backups |
| Performance | Measured CPU/GPU usage, memory, response time, long-running/large-image handling, regression thresholds |
| Rollback and support | Installation rollback, issue triage, failure reports and designated owner |

## Scope of earlier reports

`STABILITY_REPORT.md` (30 March 2026) describes a 16-case UI and controller verification snapshot. `docs/INTEGRATION_TEST_REPORT.md` (29 December 2025) describes historic import/startup checks. They are useful development records, but do not certify current code or industrial equipment.

**Current claim boundary:** SJDAS is an active engineering prototype. A CI success does not imply 100% test coverage or controller compatibility. Until an operator signs off real loom trials, do not market exports as factory-qualified.
