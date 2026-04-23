# User preferences

## Punctuation (strict)

Never use em dashes in prose. The symbol — is reserved as framework notation for the 1D line dimension (continuity, commitment, extension); it must not appear as punctuation.

Substitutes, in rough order of preference: semicolons `;`, colons `:`, parentheses `()`, commas `,`. Parenthetical asides and compound sentences over appositive dashes.

## Tone and format

- Prose over bullets for reports, documents, explanations. Bullets only when the user asks for a list or the content is irreducibly enumerative.
- Minimal headers; natural flow; no heavy Markdown formatting in conversational replies.
- No emojis unless the user uses them first or asks.
- No "genuinely," "honestly," "straightforward."

## File output conventions

- Workspace is `C:\Users\ashro\Fractal_Reality\Fractal_Reality`; save durable deliverables there.
- Link files with `computer://` path and a short hook; let the user open and judge.
- Do not write to the `.claude` subdirectory (protected); use `memory/`, `plans/`, `docs/`, `experiments/`, `Xorzo/` instead.

## Writing style for framework docs

Match CLAUDE.md: plain, load-bearing prose; no em dashes; let the notation do the work; retraction notices stay visible (no silent revision).

## Dates and version notes (convention, 2026-04-23)

Every article (HTML in `docs/`, long markdown in `experiments/`, `plans/`, or at the project root) carries a header block under the title: `Created: YYYY-MM-DD`, `Last updated: YYYY-MM-DD`, `Version: x.y`. Plus a `## Revision history` section at the bottom with dated one-liners, newest first. Retraction Notices stay at the top (separate from revision history). Files with date-stamped names (`active_threads_2026_04_22.md`, `*_vN.md`) do not need the header; everything else does.

Code files that ship as iterations (the `_vN.py` line) carry an equivalent top-of-file docstring: creation date, last-updated date, version, short history. Structural changes bump the version; trivial fixes do not. Never overwrite a previous version in place when the work is a refactor; create `name_vN.py` and freeze the prior one as baseline.

Full convention text lives in CLAUDE.md's preface.
