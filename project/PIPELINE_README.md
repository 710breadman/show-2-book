# Episode-to-picture-book production pipeline

This workspace is organized so each episode is researched, transcribed, edited, framed, built, and audited through the same gates. The process is intentionally editorial: automation proposes scenes and checks consistency; a human review decides what the episode is actually about and whether each picture carries the intended beat.

## Production order

1. **Verify the file.** Run `tools/index_bluey_library.py`; match by embedded title, not filename alone. Record official and local numbering separately.
2. **Build the source dossier.** Read the official episode page, verify IMDb metadata, review the episode and embedded subtitles, then sample community discussion for moments viewers found resonant. Community interpretation is evidence of resonance, not canon.
3. **Write the episode thesis.** Define the playful surface, emotional hinge, understated subtext, and two or three candidate final messages before selecting frames.
4. **Extract evidence.** Normalize subtitle cues, detect scene changes, and create contact sheets. Every planned page must point to subtitle cues and a visual timestamp.
5. **Make the page map.** Allocate pages by narrative beats. Keep spoken words close to the subtitles, use natural contractions, identify speakers, and add only enough narration to describe visible action or bridge time.
6. **Select frames by action.** Prefer readable expressions and decisive action over merely pretty shots. Verify that the selected instant depicts the same beat as the adjoining text.
7. **Design and build.** Upscale source frames once, keep crops composition-aware, place sound effects at their physical sources, use light page borders, and preserve a stable type/color system.
8. **Audit.** Run subtitle-fidelity, contraction, speaker, page-density, frame-resolution, effect-placement, PDF rendering, and DOCX accessibility checks. Visually inspect every rendered page at full size.
9. **Proof in the real format.** Make one private family proof and read it aloud before adjusting pacing or committing to a print run.

## Core files

- `MASTER_BRIEF.md` — refined project prompt and acceptance criteria.
- `EDITORIAL_AND_DESIGN_STANDARD.md` — voice, typography, page, frame, and QA rules.
- `RESEARCH_AND_MARKET_VIABILITY.md` — age/length comparisons, printing paths, and legal/market conclusion.
- `library_index.json` / `.csv` — verified local episode inventory.
- `NEXT_EPISODE_MANIFEST.json` — research thesis, source status, and page budgets for the next ten books.
- `episodes/EPISODE_TEMPLATE.json` — per-episode evidence and production schema.
- `episode_work/` — extracted subtitles, candidate frames, contact sheets, and a source dossier for every queued episode available locally.

## Current tools

```powershell
$python = 'C:\Users\Media\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python tools\index_bluey_library.py
& $python tools\preflight_series.py project\NEXT_EPISODE_MANIFEST.json project\episode_work --workers 2
& $python tools\analyze_episode.py '<episode.mkv>' '<source-review-folder>'
& $python tools\build_storyboard_candidates.py '<episode.mkv>' '<storyboard-folder>'
& $python tools\frame_sheet.py --help
& $python tools\build_picture_book.py '<storyboard-frames-folder>' '<output-folder>'
& $python tools\audit_storybook.py tools\build_picture_book.py '<subtitles.srt>'
& $python tools\dialogue_fidelity.py tools\build_picture_book.py tmp\bluey_s01e01\subtitles_en.srt
& $python tools\final_qa.py '<book.pdf>' '<book.docx>' '<rendered-pages-folder>'
```

The final Bluey-derived books are for private family use. A commercial version of this system should use wholly original characters, art, names, dialogue, and stories unless a written license has been obtained.
