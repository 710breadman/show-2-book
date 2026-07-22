# Autonomous agent contract

## Mission

Build Show2Book as a local-first story adaptation engine. Preserve story complexity, emotional timing, exact important dialogue, and strong source frames. The approved finished books are the quality floor; the system should make that quality repeatable.

## Absolute rules

1. Work on one sprint only. Do not begin future sprint work.
2. Start by reading `AGENTS.md`, `SPRINT_STATE.json`, `PROJECT_STATUS.md`, and the current sprint record from `sprints/manifest.json`.
3. Read additional files only when added to `autonomy/CONTEXT_MANIFEST.json` with a reason.
4. Default maximum: eight files read or changed per child task.
5. Use a fresh context for every sprint. Never depend on chat history.
6. One Ollama/Gemma request may run at a time. Parallel reviewers are logical fan-out jobs queued sequentially locally.
7. Never accept malformed JSON, missing evidence, failed tests, or unverified artifacts as success.
8. Preserve raw model output when validation fails.
9. Retry the same blocker at most twice. Then log it and continue independent work.
10. Never upload video, audio, frames, transcripts, unfinished books, or local benchmark pages to cloud services.
11. Never invent a quote. Important dialogue must be exact or marked for review.
12. Never silently remove a protected emotional beat to meet a page target.
13. Never force a moral onto a complex story.
14. Do not diagnose characters or viewers. Emotional-development review is editorial, not clinical.
15. Do not claim a sprint complete until its acceptance criteria and verification commands pass.

## Context budget: exactly 62,768 tokens

| Segment | Maximum |
|---|---:|
| Operating contract | 5,000 |
| Current sprint/task packet | 7,000 |
| Target source files | 21,000 |
| Test/error output | 8,000 |
| Previous handoff/state | 6,000 |
| Response/patch reserve | 8,000 |
| Safety buffer | 7,768 |
| **Total** | **62,768** |

The context pack builder must refuse an oversized packet. Summarize logs before inclusion. Never load the whole repository.

## Sprint procedure

1. Confirm dependencies are complete.
2. Record exact context files and reasons.
3. Write a five-line plan in `autonomy/CURRENT_TASK.md`.
4. Implement the smallest complete vertical slice.
5. Run focused tests, then every verification command in the sprint record.
6. Write `artifacts/handoffs/S###.md`, maximum 1,200 words, containing files, commands/results, decisions, blockers, and exact next sprint.
7. Update `PROJECT_STATUS.md` and atomically update `SPRINT_STATE.json`: mark complete, increment revision, select the next dependency-ready sprint, and record verification.
8. Commit only scoped files with `S###: <title>`.
9. Do not begin the next sprint in this context.

## Blocker protocol

Record blockers with evidence and the smallest required human action. Mark only affected stages blocked. Use placeholders only when explicit, reversible, and impossible to mistake for verified quotes or facts. After two unsuccessful attempts, stop retrying and continue dependency-independent work.

## File limits

- Soft code-file limit: 400 lines.
- Hard code-file limit: 600 lines.
- Handoff: 1,200 words maximum.
- Full logs stay outside context; include concise summaries and paths.
- Persisted JSON is versioned, deterministic, and schema validated.

## Editorial authority

1. Actual episode/movie: video, audio, subtitles.
2. Official creator/context sources for factual intent.
3. Reliable recaps/reviews for cross-checking.
4. Broad community discussion for emotional reception.

Community interpretation may alter emphasis, pacing, quote choice, or framing, but cannot invent or override source events.

## Overrides and learning

Manual choices are locked, versioned overrides. Regeneration preserves them and may show a new recommendation beside them. Preference scope is:

`edition → series → content type → audience → global`

No learned preference may silently rewrite an existing edition.
