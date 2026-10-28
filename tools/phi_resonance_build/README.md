# φ-Entrainment page pipeline

Created: 2026-10-28
Last updated: 2026-10-28
Version: 1.0

These files build the two φ-Entrainment pages on fractalreality.ca: the sound lab, `docs/phi_resonance.html`, and its Composer edition, `docs/phi_resonance_composer.html`. The paid Android app, Phi Resonance (FractalGaming `phi_resonance/`), is built in turn from the Composer page.

## Build

```bash
python tools/phi_resonance_build/build.py
```

It builds both pages in a temporary folder and copies them into `docs/` only when every step passes:

1. Copy the base page, `phi_resonance_before_redesign.html`, in as `phi_resonance.html`.
2. `redesign_patch.py` gives it the Last Ship Sailing interface and every later change, one section at a time. Every anchor must match exactly, or the build stops.
3. `build_composer.py` makes the Composer edition from it.
4. `check_page.py` checks each page: its script passes `node --check`, every id the script looks up is in the page or made by the script, and no id is used twice.

A build that stops leaves `docs/` as it was and says where its work so far is. Both pages are rewritten from scratch every time, so never edit them by hand.

## Changing a page

- **Both pages** (most changes): add a section at the end of `redesign_patch.py`, one `rep(old, new)` per edit. Each section opens with a comment saying what changed, why and when; the owner's words go in quotes.
- **The Composer edition only**: `build_composer.py` (its header comment carries the Composer page's version and revision history), or the `composer_*` pieces.
- **Look and layout**: `shell.css`, `shell_body.html`, `shell.js` and `breath.js` for both pages; `composer_shell.css` and `composer_tab.html` for the Composer.

Then test both pages, deploy by pushing `main` (`deploy-docs.yml` publishes `docs/`), and bring the change into the app from FractalGaming `phi_resonance/`:

```bash
python scripts/build_page.py ../../Fractal_Reality/docs/phi_resonance_composer.html
```

## Files

| File | What it is |
|---|---|
| `build.py` | Runs the whole build |
| `phi_resonance_before_redesign.html` | The base page: `docs/phi_resonance.html` at commit 60e3fae5, the last version before the redesign |
| `redesign_patch.py` | The interface and every change since, in dated sections |
| `build_composer.py` | Makes the Composer edition from the lab page |
| `check_page.py` | Checks a built page |
| `shell.css`, `shell_body.html`, `shell.js` | The Last Ship Sailing interface: style, page body, interface code |
| `breath.js` | The breath guide |
| `composer_engine.js`, `composer_ui.js`, `composer_shell.css`, `composer_tab.html` | The Composer: its music engine, its controls, their style and its tab |

## Line endings

Every file here uses Unix line endings (LF), as the two pages do. The base page is read byte for byte, so a copy with Windows line endings (CRLF), which git on Windows writes when `core.autocrlf` is on (it is on this machine), stops the build at a multi-line anchor; this was tested on 2026-10-28. `.gitattributes` (`* -text`) has git keep every file here exactly as it is, on any machine.

## Where it came from

The pipeline was written in Claude Code sessions from 2026-10-18, when the redesign landed (commit 8c8db9b3), and lived in one session's temporary folder until 2026-10-28, after its base page had gone missing from there once. The base was restored from git, and the unchanged pipeline rebuilt both live pages from it byte for byte before the move.

## Revision history

- 2026-10-28 v1.0: initial: the pipeline moved here from a session's temporary folder; `build.py` builds in a temporary folder and writes `docs/` only when every step passes; `build_composer.py` and `check_page.py` find their files without a folder argument; `check_page.py` stops the build on a broken page
