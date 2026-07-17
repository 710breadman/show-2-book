# Final QA report — The Magic Xylophone

Verified 20 June 2026.

## Deliverables

- PDF: `output/pdf/Bluey_S01E01_The_Magic_Xylophone_Picture_Book_Polished.pdf`
  - 19,639,132 bytes
  - SHA-256: `120E2CF3BE32FAD6B92EAFA18DAD6CB74E908A1E34AEFD3E9317F415AD3A5797`
- DOCX: `output/docx/Bluey_S01E01_The_Magic_Xylophone_Picture_Book_Polished.docx`
  - 15,117,766 bytes
  - SHA-256: `0CB24042AF265DD509346A07652C53E59A5469E233CA16D91588BED48A32CB18`

## Editorial checks

- 21 physical pages: cover, 19 story pages, and one closing-message page.
- 785 story words: about 6.0 minutes at 130 words per minute or 7.9 minutes at a gentler 100 words per minute.
- Longest page: 65 words; it is the deliberately slower two-panel Bingo turn-taking scene.
- 54 quoted passages checked against embedded subtitles.
  - 53 matched at or above the 0.85 review threshold.
  - 0 require manual subtitle review.
  - 1 approved book-only addition: Dad's requested `Mwa-ha-ha!` comic laugh.
- Expanded-form contraction audit found no inappropriate `you are`, `do not`, `will not`, `I am`, or related constructions.
- Two full forms are intentional:
  - `I will now play...` preserves Dad's mock-formal concert announcement and the subtitle.
  - `There you are!` is idiomatic; contracting it would be ungrammatical.

## Requested scene and placement checks

- Physical page 10 uses the 03:33 hair-plucking frame rather than a kissing frame; `PLUCK!` is placed at Mum's paw.
- Physical page 14 has no words over the picture; the text ends with the sisters “never noticing Dad hiding above them.”
- Physical page 17 uses a two-panel sequence: Bingo hesitates, briefly unfreezes Bluey, refreezes her, and explains how taking every turn makes her feel.
- Physical page 18 places `DING!` over Bluey on the left.
- Physical page 19 places `BLUB! BLUB!` over Dad on the right.
- Physical page 20 shows Bluey and Bingo smiling during the xylophone handoff.
- Physical page 21 omits the personal-adaptation line and gives the researched closing message the visual emphasis.

## File and visual checks

- PDF: 21/21 pages rendered and visually inspected at 170 dpi; all pages are 11 × 8.5 inch landscape.
- PDF: 21 image objects, all 2560 × 1440 pixels; all nonstandard fonts are embedded. The only non-embedded resource is standard Base-14 Helvetica.
- DOCX: 21 inline images, all 2560 × 1440 pixels; 20 explicit page breaks; every image has alt text.
- DOCX accessibility audit: 0 high, 0 medium, and 0 low findings.
- The canonical DOCX renderer could not run because LibreOffice is not installed in this environment. Structural OOXML and accessibility checks passed, and the DOCX uses the same 21 page images and dimensions as the fully rendered PDF.

Machine-readable details are in `final_qa_report.json`, `dialogue_fidelity.json`, and `docx_a11y_audit.json`.

## Series preflight

- Eight of the ten queued episodes now have extracted embedded subtitles, scene candidates, eight-second timeline samples, contact sheets, and individual source dossiers under `project/episode_work/`.
- `Cricket` and `The Sign` are correctly marked `source_needed`; the indexed Season 3 library ends at local file E37.
- `Baby Race` is verified as local file S02E50 despite its official Episode 49 label.
