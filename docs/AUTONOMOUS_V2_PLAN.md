# Autonomous v2 implementation plan

## Product goal

Create a local-first engine that turns a locally owned show or movie into a polished picture book while preserving emotional weight, exact important quotes, source timing, quiet moments, reveals, callbacks, and story complexity. The existing approved books are the visual and editorial quality floor.

## Pipeline

```text
local media
  → ffprobe identity and stream inventory
  → embedded/external subtitles or local faster-whisper fallback
  → complete scene/shot map
  → reproducible frame index and contact sheets
  → cited official/editorial/community research
  → exact quote archive
  → exhaustive versioned JSON dossier + generated Markdown view
  → one recommended adaptive-length book blueprint + optional cuts
  → ranked source-frame candidates
  → restrained page layouts
  → PDF/page images/editable package
  → independent review board + adversarial red team
  → final editor
  → marked draft or approved clean final
```

## Storage

- **Versioned JSON:** authoritative source of truth.
- **Generated Markdown:** readable dossier and reports; not independently edited.
- **SQLite + FTS5:** rebuildable search/index/cache for research, runs, and preferences.
- **Private binary root:** video, audio, frames, transcripts, renders, and benchmark pages; ignored by Git.

Each pipeline stage records input hashes, configuration hash, output hashes, status, retries, and blockers. Changes invalidate only dependent stages. A quote correction should not force new media probing or unrelated research.

## Specialist crew

Production specialists:

- Source Ingestor
- Quote Archivist
- Story Cartographer
- Reception Researcher
- Screen-to-Page Adapter
- Picture-Book Editor
- Developmental & Emotional Reader
- Cultural/Context Reader
- Frame Director
- Layout Designer

Independent reviewers:

- story continuity;
- emotional fidelity;
- quote accuracy;
- research/source fidelity;
- frame/action agreement;
- pacing and page turns;
- readability and age fit;
- accessibility;
- layout and print safety;
- repetition and visual variety;
- adversarial red team.

Reviewers return typed findings and never edit artifacts directly. They work independently before the final editor sees their conclusions. “Psychology” is limited to non-clinical editorial review of age fit, emotional clarity, fear, repair, ambiguity, and over-explanation; agents may not diagnose characters or viewers.

The final editor groups duplicate findings, protects source truth and locked choices, resolves low-risk conflicts, escalates only high-impact disagreements, and proposes explicit preference records. Preference scope is `edition → series → content type → audience → global`. No learning silently rewrites an existing edition.

## Research policy

Authority order:

1. actual video/audio/subtitles;
2. official creator/context sources for factual intent;
3. reliable recaps and reviews for cross-checking;
4. broad public discussion for emotional reception.

Each finding stores URL, title, source layer, retrieval date, concise paraphrase, confidence, interpretation class, affected scenes, and whether it changed the plan. Interpretations are labeled consensus, plausible, disputed, or speculative. Disputed readings require review; speculative readings remain notes only. Fan response may influence emphasis, pacing, quote selection, and framing but cannot replace canon.

Research providers are pluggable: manual URLs first, optional SearXNG JSON search, static HTTP/text extraction, and Playwright browser fallback. Reddit is not a mandatory API dependency. Store source URLs and concise paraphrases rather than copied discussion archives.

## Toolchain

- Python 3.12 and uv for a reproducible Windows environment and lockfile.
- Pydantic v2 for strict models, JSON validation, and schema export.
- Typer + Rich for a stable headless CLI.
- SQLite/FTS5 for local search and rebuildable caches.
- Ollama `gemma4:12b` with exact `num_ctx=62768`.
- Codex CLI `exec --ephemeral` as the local coding tool harness.
- FFmpeg/ffprobe for streams, subtitles, audio, and exact frames.
- PySceneDetect for multiple scene-boundary strategies.
- faster-whisper for local transcription fallback.
- pysubs2 for SRT/VTT/ASS normalization.
- Pillow and headless OpenCV for frame analysis, crops, composites, and contact sheets.
- ReportLab for deterministic PDF construction.
- PyMuPDF for rendering every PDF page during QA.
- python-docx for optional editable editions.
- NiceGUI for a simple local/native interface.
- Playwright for browser fallback and GUI end-to-end tests.
- Ruff, mypy, pytest, pre-commit, and GitHub Actions for quality gates.

CrewAI and LangChain are deliberately deferred. An explicit small orchestrator consumes less context, keeps every contract visible, and avoids hidden memory/tool abstractions. Add a framework later only if benchmark evidence justifies it.

## Exact context protocol

The 62,768-token budget is fixed:

| Segment | Tokens |
|---|---:|
| Operating contract | 5,000 |
| Current task | 7,000 |
| Exact target files | 21,000 |
| Tests/errors | 8,000 |
| Previous handoff/state | 6,000 |
| Output reserve | 8,000 |
| Safety buffer | 7,768 |

Every sprint starts in a fresh ephemeral session, reads at most eight task files by default, and writes a handoff of at most 1,200 words. Full logs, whole-repository scans, binaries, and all research sources never enter a coding context. The context builder fails rather than silently truncating required information.

Local “parallel” agents are queued sequentially because one Gemma request runs at a time. Deterministic media work may use bounded CPU concurrency. Optional cloud text-only reviewers may run in parallel only when explicitly enabled and within budget.

## Blockers and unattended work

A repeated blocker receives two attempts. Then the runner records evidence, the smallest human action, and affected dependencies; it continues any independent work. It never invents uncertain quotes or facts. Serious unresolved issues may produce a clearly watermarked draft, but a clean final requires approval. Fixes rerun only affected stages/pages.

## GUI

The normal path contains five screens:

1. Add story
2. What matters
3. Book plan and key quotes
4. Fix problems
5. Export

Advanced dossier, emotional timeline, scene map, frame comparison, review board, edition manager, preferences, and queue views remain collapsed. One primary action appears per screen. Every automated choice supports “Why this?”

## Privacy and rights

Cloud providers accept only public-text request objects. There is no code path that serializes local media, local transcripts, private book text, or benchmark pages into a cloud request. Shareable archives use an allowlist and exclude all private roots.

Do not commit source media, extracted frames, full licensed transcripts, generated licensed books, local path indexes, research page bodies, API keys, cookies, browser profiles, or preference history. Licensed adaptations are private family-use work unless permission is obtained.

## Benchmark plan

Register approved local copies of *The Magic Xylophone* and *Camping* without storing their pages in Git. Extract only non-copyright metrics: quote fidelity, protected-beat coverage, setup/payoff preservation, page density, read-aloud duration, repetition, frame quality, overflow, reviewer severity, conflict rate, and redo/override rate. Scores surface regressions; they do not replace editorial judgment.
