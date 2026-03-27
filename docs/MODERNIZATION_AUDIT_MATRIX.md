# SJDAS Modernization Audit Matrix

This matrix captures outdated patterns, security gaps, and contract inconsistencies across backend, web, and desktop.
All remediation is additive to preserve existing behavior.

## Backend

| Area | Current state | Risk | Recommended additive strategy |
|---|---|---|---|
| Auth | Mock token and default credentials in `backend/routers/auth.py` | Critical | Add JWT auth service with role claims; keep legacy token path temporarily behind compatibility switch |
| Sensitive routes | Decode async auth commented out; Jules execution endpoint exposed | Critical | Enforce auth dependency and admin role checks; gate maintenance route in production |
| CORS/config | Wildcard default origins with credentials in `backend/main.py` | High | Add strict env validation and explicit origin allowlist |
| Error handling | Broad exception handling and fallback mock responses | High | Add structured error model and centralized handlers; keep fallbacks behind explicit dev mode |
| Route design | Prefix duplication risk with router-level and app-level version paths | High | Introduce versioned API router and migrate endpoints via compatibility aliases |
| Observability | Print-based logging in API paths | Medium | Add structured logger, request IDs, and operation audit events |

## Web

| Area | Current state | Risk | Recommended additive strategy |
|---|---|---|---|
| API endpoint config | Hardcoded localhost URLs in decode and studio flows | High | Centralize API/WS base URLs with env-aware helpers |
| Contract consistency | UI assumptions may drift from backend payload shape | High | Add typed shared contracts and normalization adapters |
| Feature depth | Monitor/analytics/library/settings mostly placeholders | High | Add real data views and B2B admin/approval workflows |
| Quality gates | Limited test scripts and no E2E baseline | Medium | Add lint+typecheck+smoke test scripts and CI checks |

## Desktop

| Area | Current state | Risk | Recommended additive strategy |
|---|---|---|---|
| Cloud compatibility | Service calls and auth contract are loosely aligned with web/backend evolution | High | Introduce shared domain schema and compatibility wrappers |
| Enterprise controls | Limited tenant-aware role enforcement in client actions | Medium | Add role-aware capability checks and server-driven entitlements |
| Diagnostics | Logs exist but not standardized for supportability | Medium | Add structured support diagnostics bundle export |

## Cross-System Contract Gaps

| Domain | Gap | Additive strategy |
|---|---|---|
| Auth claims | Missing unified role/tenant/session envelope | Create shared auth models consumed by backend/web/desktop |
| Decode results | Potential snake/camel mismatch | Normalize at API boundary and expose typed client utilities |
| Job lifecycle | Task states differ across websocket/polling paths | Define single job status contract and map legacy states |
| Auditability | No immutable event schema | Add append-only audit event model and logging utility |

## Priority Order

1. Security hardening and route normalization
2. Shared contract package and compatibility adapters
3. Premium B2B modules (admin, approvals, audit, collaboration)
4. Observability, tests, CI/CD, and deployment standards
