# Project status

**Architecture:** approved  
**Target model:** Ollama `gemma4:12b`  
**Context:** 62,768 tokens  
**Current sprint:** S000 — Sanitize and simplify repository  
**Overall status:** autonomous v2 foundation ready to begin

## Locked decisions

- Universal engine, developed Bluey-first.
- Public code; private licensed assets and generated books.
- Deterministic media/layout pipeline plus specialist editorial agents.
- JSON is authoritative; Markdown is readable; SQLite/FTS5 is searchable cache/index.
- One recommended edition with optional shorter, extended, and younger cuts.
- Complexity and protected beats control length.
- Important quotes are exact or flagged.
- Complete scene map and cited master dossier precede page planning.
- Actual source frames only; reversible cleanup/crop/upscale is allowed.
- Guided GUI with advanced controls hidden.
- Page plan and key quotes are the routine review gate.
- Errors are non-blocking where dependencies allow; serious unresolved issues export draft only.
- Independent specialist reviews feed a final editor.
- Preference learning is visible, scoped, versioned, and reversible.
- English output only for v1; meaningful foreign-language dialogue is preserved.
- Local-only mode is complete; optional cloud text/research support is opt-in.

## Existing proof of concept

Current scripts already prove JSON-driven frame extraction, PDF/DOCX building, quote audits, contact sheets, and final QA. Preserve and characterize them before modularizing. Do not start with a renderer rewrite.

## Immediate next action

Execute S000 from `sprints/manifest.json`. Do not begin media or GUI implementation first.
