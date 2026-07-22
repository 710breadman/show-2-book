# Show2Book

A local-first system for turning a show or movie into a carefully edited picture book while preserving emotional weight, exact important quotes, visual timing, and story complexity.

The repository contains the working Bluey-first proof of concept plus the new autonomous v2 plan. Licensed media, transcripts, frames, generated books, research caches, and local library indexes are intentionally excluded.

## Direction

`video → subtitles/transcription → complete scene map → cited research → master dossier → recommended book blueprint → ranked source frames → pages → specialist reviews → final editor → PDF`

The approved books remain the visual quality floor. The v2 work focuses on making the path to that quality repeatable, traceable, resumable, and simple to operate.

## Autonomous target

- Windows 11
- Ollama `gemma4:12b`
- exact 62,768-token context window
- one fresh `codex exec --ephemeral` context per sprint
- maximum eight files per child task by default
- one local model request at a time
- two attempts per repeated blocker, then log and continue independent work

## Key files

- `AGENTS.md` — autonomous operating contract
- `PROJECT_STATUS.md` — compact durable state
- `SPRINT_STATE.json` — machine-readable current sprint
- `ROADMAP.md` — milestone roadmap
- `SPRINTS.md` — implementation catalog
- `sprints/manifest.json` — machine-readable sprint dependencies
- `docs/AUTONOMOUS_V2_PLAN.md` — architecture, crew, tools, privacy, workflow, and acceptance principles
- `project/MASTER_BRIEF.md` — legacy editorial foundation
- `project/EDITORIAL_AND_DESIGN_STANDARD.md` — established visual/editorial rules
- `tools/build_episode_storybook.py` — current JSON-driven builder

The standalone starter pack contains the full acceptance criteria, self-contained sprint packets, bootstrap scripts, starter code, tests, and XLSX tracker.

## Product rules

- Source media and derived images stay local.
- Optional cloud AI is off by default, budget-limited, and restricted to public text/research.
- Important dialogue is exact or flagged; invented quotations are forbidden.
- Full scene analysis and a cited dossier come before page planning.
- Fan discussion guides emotional emphasis but cannot override the actual source.
- Story complexity controls length; protected beats cannot be removed to hit a page target.
- Complex stories do not receive a forced moral.
- Actual source frames are used; reversible crop, cleanup, and upscale are allowed, but generative replacement art is not.
- Routine human review focuses on the page plan and key quotes.
- Serious unresolved issues may produce a clearly marked draft; a clean final requires approval.

## Local starter pack

The complete Windows/Gemma starter ZIP and sprint workbook are generated outside the repository so they do not add binaries to Git history. Extract the starter into `V:\AI\book maker`, run `scripts\bootstrap.ps1`, then `scripts\run-autonomous.ps1`.

## Rights

This code can support original or licensed works. Adaptations using copyrighted characters, frames, or dialogue should be treated as private family-use work unless appropriate permission is obtained.
