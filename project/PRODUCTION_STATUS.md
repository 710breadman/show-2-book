# Bluey picture-book production status

Updated 20 June 2026. This file is the continuity ledger for long-running production and chat handoffs.

## Completed and verified

### The Magic Xylophone — S01E01

- PDF: `output/pdf/Bluey_S01E01_The_Magic_Xylophone_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S01E01_The_Magic_Xylophone_Picture_Book_Polished.docx`
- 21 pages; 785 words; final PDF and structural DOCX QA passed.

### Sleepytime — S02E26

- Spec: `project/episodes/sleepytime/book_spec.json`
- PDF: `output/pdf/Bluey_S02E26_Sleepytime_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S02E26_Sleepytime_Picture_Book_Polished.docx`
- 24 pages; 541 audited words; 16/16 spoken passages matched embedded subtitles; no contraction flags.
- PDF: 24/24 pages rendered and visually inspected; all image objects 2560 × 1440; all nonstandard fonts embedded.
- DOCX: 24 inline images, complete alt text, 23 page breaks, 0 accessibility findings.
- Canonical DOCX rendering unavailable because LibreOffice is not installed; PDF rendering and DOCX structural QA passed.

### Camping — S01E43

- Spec: `project/episodes/camping/book_spec.json`
- PDF: `output/pdf/Bluey_S01E43_Camping_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S01E43_Camping_Picture_Book_Polished.docx`
- 24 pages; 647 audited words; 36/36 spoken passages matched embedded subtitles at 0.931 similarity or better; no contraction flags.
- PDF: 24/24 pages rendered and visually inspected; final cover, names/goodbye, and sprout/running spread individually rechecked; all image objects 2560 × 1440; all nonstandard fonts embedded.
- DOCX: 24 inline images, complete alt text, 23 page breaks, 0 accessibility findings.
- Canonical DOCX rendering unavailable because LibreOffice is not installed; PDF rendering and DOCX structural QA passed.

### Baby Race — S02E49 (local file S02E50)

- Spec: `project/episodes/baby_race/book_spec.json`
- PDF: `output/pdf/Bluey_S02E49_Baby_Race_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S02E49_Baby_Race_Picture_Book_Polished.docx`
- 24 pages; 767 audited words; 60/60 spoken passages matched embedded subtitles exactly; intentional subtitle full forms documented; no contraction flags.
- PDF: 24/24 pages rendered and visually inspected; story-opening trio frame corrected and rerendered; all image objects 2560 × 1440; all nonstandard fonts embedded.
- DOCX: 24 inline images, complete alt text, 23 page breaks, 0 accessibility findings.
- Canonical DOCX rendering unavailable because LibreOffice is not installed; PDF rendering and DOCX structural QA passed.

### Granny Mobile — S03E33

- Spec: `project/episodes/granny_mobile/book_spec.json`
- PDF: `output/pdf/Bluey_S03E33_Granny_Mobile_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S03E33_Granny_Mobile_Picture_Book_Polished.docx`
- 24 pages; 772 audited words; 90/90 spoken passages matched embedded subtitles exactly; intentional subtitle full forms documented; no contraction flags.
- PDF: 24/24 pages rendered and visually inspected; character centering and every sound-effect placement refined and rerendered; all image objects 2560 × 1440; all nonstandard fonts embedded.
- DOCX: 24 inline image placements (23 unique media assets because Word deduplicated a repeated frame), complete alt text, 23 page breaks, 0 accessibility findings.
- Canonical DOCX rendering unavailable because LibreOffice is not installed; PDF rendering and DOCX structural QA passed.

### Fairytale — S03E26

- Spec: `project/episodes/fairytale/book_spec.json`
- PDF: `output/pdf/Bluey_S03E26_Fairytale_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S03E26_Fairytale_Picture_Book_Polished.docx`
- 26 pages; 850 audited words; 63/63 spoken passages matched embedded subtitles exactly; no contraction flags.
- PDF: 26/26 pages rendered and visually inspected; sibling group shots, chase centering, rescue sequence, and sound-effect attribution refined and rerendered; all image objects 2560 × 1440; all nonstandard fonts embedded.
- DOCX: 26 inline images, complete alt text, 25 page breaks, 0 accessibility findings.
- Canonical DOCX rendering unavailable because LibreOffice is not installed; PDF rendering and DOCX structural QA passed.

### Flat Pack — S02E24

- Spec: `project/episodes/flat_pack/book_spec.json`
- PDF: `output/pdf/Bluey_S02E24_Flat_Pack_Picture_Book_Polished.pdf`
- DOCX: `output/docx/Bluey_S02E24_Flat_Pack_Picture_Book_Polished.docx`
- 24 pages; 700 audited words; 48/48 retained spoken passages matched embedded subtitles exactly; no contraction flags.
- PDF: 24/24 pages rendered and visually inspected; snow, cave, builder-transition, and spaceship frames refined and rerendered; all image objects 2560 × 1440; all nonstandard fonts embedded.
- DOCX: 24 inline images, complete alt text, 23 page breaks, 0 accessibility findings.
- Canonical DOCX rendering unavailable because LibreOffice is not installed; PDF rendering and DOCX structural QA passed.

## Priority queue

1. The Creek — next up; preflight complete
2. Onesies — preflight complete
3. Cricket — source needed
4. The Sign — source needed

After the verified priority set, continue through the local library using a popularity-weighted order based on current IMDb votes/ratings, broad editorial lists, official prominence, and community discussion. Never let popularity replace close episode review.

## Reusable production system

- `tools/build_episode_storybook.py` — data-driven frame preparation, composites, baked sound effects, PDF, DOCX, and build report.
- `tools/audit_episode_spec.py` — subtitle-fidelity, contraction, word-density, alt-text, and frame-reference audit.
- `tools/final_qa.py` — PDF font/image/page checks, DOCX image/alt/page-break checks, and rendered-page checks.
- `project/episodes/EPISODE_TEMPLATE.json` — evidence and beat-map schema.

## Non-negotiable gate for every episode

1. Verify local file by embedded title.
2. Read official synopsis; review embedded subtitles and the whole visual sequence; sample community interpretation.
3. Write thesis, emotional hinge, subtlety note, and final-message candidates before drafting.
4. Select frames that depict the same action/emotion as the adjoining text.
5. Audit every quoted line against subtitles and audit expanded contractions.
6. Build PDF and DOCX with 2560 × 1440 shared image assets and meaningful alt text.
7. Render every PDF page, inspect every page, correct defects, and rerender.
8. Run PDF/DOCX structural and DOCX accessibility checks before marking complete.
