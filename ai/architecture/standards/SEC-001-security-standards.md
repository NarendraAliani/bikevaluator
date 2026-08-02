# SEC-001 — Security Standards

| Field | Value |
|---|---|
| Document ID | SEC-001 |
| Version | 1.0 |
| Status | Needs Review |
| Owner | Architecture AI |
| Reviewer | Human (architect) |
| Created | 2026-08-02 |
| Last Updated | 2026-08-02 |
| Related Documents | API-000, LOG-001, `ai/agents/security.md`, `ai/architecture/gov/` |
| Next Documents | API Security Standard (endpoint-level, once FS-003 Authentication is scoped) |

Baseline security standards. No implementation yet — this is the
conventions layer future FS/API documents must follow.

## Authentication & Authorization

- All API endpoints require authentication except a small, explicitly
  documented public allowlist (none identified yet).
- Authorization is enforced at the API layer, not only the UI — per
  Constitution/SDD-000 (Dealers cannot access pricing-write endpoints
  regardless of client-side restrictions).

## Data Protection

- PII fields (flagged in each `DD-<Entity>.md`) are identified before
  implementation, not discovered after.
- Encryption at rest for any field flagged "Encrypted" in its Data
  Dictionary entry; TLS in transit for all API traffic, no exceptions.

## Input Validation

- All validation happens at the API boundary (system boundary, per this
  repository's general engineering norms) — the Flutter client's
  validation is a UX convenience, never the authority.

## Secrets Management

- No secrets in source control (enforced by `.gitignore`, Constitution
  Rule 1 spirit extended to secrets) — environment variables or a
  secrets manager only.

## Dependency Security

- New dependencies reviewed for known vulnerabilities before adoption
  (security agent's responsibility — `ai/agents/security.md`).

## OWASP Top 10 Baseline

- Standard mitigations apply (injection, broken auth, sensitive data
  exposure, etc.) — detailed per-module treatment deferred to each
  module's FS/API document as it's drafted; this document is the
  baseline checklist referenced, not restated, each time.

## Open Items

- Formal threat model deferred until FS-001/FS-003 scope authentication
  and data flows concretely — not blocking approval of this baseline.
