# AI Engineering Framework — BIKEVALUATOR

## Purpose

This folder contains the **AI collaboration framework** for the BIKEVALUATOR
repository: the constitution, decision log, task tracker, changelog, session
state, prompt library, and review log used to run development as a
controlled loop-engineering workflow between humans and AI assistants.

## How it should be used

- Every AI session should **start** by reading, in order:
  1. `ai/constitution/constitution.md`
  2. `ai/decisions/decisions.md`
  3. `ai/todo/todo.md`
  4. `ai/session/session-state.md`
  5. `ai/prompts/prompt-index.md`
- Every AI session should **end** by updating: `todo.md`, `session-state.md`,
  `changelog.md`, and logging any new decisions in `decisions.md`.
- New prompts used to drive significant work should be saved under
  `ai/prompts/` and registered in `ai/prompts/prompt-index.md`.
- Architecture, product, or implementation choices of consequence must be
  logged in `ai/decisions/decisions.md` before or immediately after being
  acted on.

## Separation from production code

This entire `ai/` directory is **documentation and process tooling only**.
It must never be imported, bundled, deployed, or otherwise depended upon by
production/runtime code (see Constitution Rule 1). It is version-controlled
alongside the code it documents, but excluded from build/deploy artifacts.

See `ai/constitution/constitution.md` for the full rule set.
