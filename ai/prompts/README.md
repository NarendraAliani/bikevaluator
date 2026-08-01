# Prompts — BIKEVALUATOR

This folder stores every significant prompt used to drive AI-assisted work
on this repository, so results are reproducible and auditable.

## Conventions

- One file per prompt: `ai/prompts/AEP-<NNNN>-<kebab-title>.md`.
- `AEP` = "AI Engineering Prompt". IDs are sequential and never reused.
- Every prompt file must include: prompt id, version, date, purpose, output
  expectation, and linked decision ids (see
  `ai/templates/prompt-template.md`).
- Register every prompt in `ai/prompts/prompt-index.md` when created, and
  update its status as it moves through draft → active → superseded.
- If a prompt is revised, bump its version (e.g. `1.0` → `1.1`) rather than
  editing history away; keep prior versions in the same file under a
  "Revision history" section or as a new file if the change is substantial.

## This file

`AEP-001` (this repository bootstrap) is the first registered prompt — see
`ai/prompts/prompt-index.md`.
