# Sprint catalog

The machine-readable dependency, deliverable, acceptance, and verification details are in `sprints/manifest.json`. The standalone starter ZIP also contains one self-contained Markdown packet per sprint and an XLSX sprint workbook.

| ID | Phase | Sprint |
|---|---|---|
| S000 | Foundation | Sanitize and simplify repository |
| S001 | Foundation | Bootstrap the Windows toolchain |
| S002 | Foundation | Configuration and privacy boundary |
| S003 | Foundation | Canonical schemas |
| S004 | Foundation | Context-safe sprint state |
| S005 | Core Engine | Structured logging and failure ledger |
| S006 | Core Engine | Resumable stage graph |
| S007 | Core Engine | Stable CLI surface |
| S008 | Core Engine | SQLite catalog and FTS5 |
| S009 | Core Engine | Quality gates and CI |
| S010 | Media | Media probe and identity |
| S011 | Media | Subtitle extraction and normalization |
| S012 | Media | Transcription fallback |
| S013 | Media | Scene and shot detection |
| S014 | Media | Frame index and contact sheets |
| S015 | Research | Research provider contracts |
| S016 | Research | Evidence collection and citation ledger |
| S017 | Research | Reception and interpretation synthesis |
| S018 | Research | Quote archive and verifier |
| S019 | Research | Master story dossier |
| S020 | Agents | Structured Ollama client |
| S021 | Agents | Agent registry and task packets |
| S022 | Agents | Story and audience specialists |
| S023 | Agents | Independent review board |
| S024 | Agents | Final editor and preference learner |
| S025 | Adaptation | Book blueprint and adaptive length |
| S026 | Adaptation | Semantic frame ranking |
| S027 | Adaptation | Layout system |
| S028 | Adaptation | Export engine |
| S029 | Adaptation | Automated book QA |
| S030 | GUI | Guided local GUI shell |
| S031 | GUI | Plan, quote, and frame review |
| S032 | GUI | Non-blocking queue and drafts |
| S033 | GUI | Editions, overrides, and preferences |
| S034 | Autonomy | Headless autonomous runner |
| S035 | Benchmarks | Gold-standard baseline importer |
| S036 | Benchmarks | Regression scoring |
| S037 | Release | Windows packaging |
| S038 | Release | Security, documentation, and v1 release |

## Advancement rule

The next sprint is the lowest-numbered `not_started` sprint whose dependencies are complete. A blocked sprint remains current only when no independent sprint is available. The runner may not skip acceptance criteria to advance.
