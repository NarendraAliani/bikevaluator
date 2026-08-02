# Engineering Principles — BIKEVALUATOR

Operational philosophy, distinct from the Constitution (which holds
binding governance rules). This document can evolve more freely than the
Constitution, which is now considered largely stable (per AR-001).

1. **Reference, don't restate.** Business rules live in BRR-001, field
   definitions in Data Dictionaries, API conventions in API-000 — every
   other document points to these, never re-derives them.
2. **Standards before implementation.** A module's FS is not written
   until the naming/style/testing/logging/security standards it depends
   on exist (NS-001, CSS-001, TEST-001, LOG-001, SEC-001).
3. **Additive history.** Decisions, rules, and traceability entries are
   never deleted — superseded and linked forward instead.
4. **Small, reviewable increments.** Each prompt produces a bounded set
   of documents with a clear review package, not a sprawling mixed
   change.
5. **The domain is not guessed.** Open business questions are logged as
   open questions, not silently assumed.
