from __future__ import annotations

import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


QUOTE_RE = re.compile(r'"([^"]+)"')
WORD_RE = re.compile(r"\b[\w']+\b")
TAG_RE = re.compile(r"<[^>]+>")
CONTRACTIONS = {
    r"\byou are\b": "you're",
    r"\bdo not\b": "don't",
    r"\bdoes not\b": "doesn't",
    r"\bwill not\b": "won't",
    r"\bit is\b": "it's",
    r"\bshe is\b": "she's",
    r"\bhe is\b": "he's",
    r"\bwe are\b": "we're",
    r"\bthey are\b": "they're",
    r"\bI am\b": "I'm",
    r"\bI will\b": "I'll",
    r"\bcannot\b": "can't",
    r"\bdid not\b": "didn't",
    r"\bcould not\b": "couldn't",
    r"\bwould not\b": "wouldn't",
    r"\bshould not\b": "shouldn't",
    r"\bhas not\b": "hasn't",
    r"\bhave not\b": "haven't",
    r"\bhad not\b": "hadn't",
    r"\bwas not\b": "wasn't",
    r"\bwere not\b": "weren't",
}


def normalize(text: str) -> str:
    text = TAG_RE.sub("", text).replace("-\n", "")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"\[[^]]+]", " ", text)
    text = re.sub(r"[^a-z0-9']+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def subtitle_cues(path: Path) -> list[str]:
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig", errors="replace"))
    cues = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines()]
        spoken = [line.lstrip("-").strip() for line in lines if line and "-->" not in line and not line.isdigit()]
        raw = " ".join(spoken)
        if normalize(raw):
            cues.append(raw)
    return cues


def match_score(candidate: str, source: str) -> float:
    if candidate in source or source in candidate:
        return 1.0
    return SequenceMatcher(None, candidate, source).ratio()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("subtitles", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--threshold", type=float, default=0.85)
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    cues = subtitle_cues(args.subtitles.resolve())
    windows = []
    for size in range(1, 7):
        for index in range(len(cues) - size + 1):
            raw = " ".join(cues[index : index + size])
            windows.append((normalize(raw), raw))

    dialogue = []
    contraction_flags = []
    page_words = []
    missing_alt = []
    missing_frames = []
    approved = {value.lower() for value in spec.get("approved_dialogue_additions", [])}
    intentional_full_forms = {value.lower() for value in spec.get("intentional_full_forms", [])}

    for physical_page, page in enumerate(spec["pages"], 1):
        text = "".join(fragment for _, fragment in page.get("parts", []))
        page_words.append(len(WORD_RE.findall(text)))
        if not page.get("alt", "").strip():
            missing_alt.append(physical_page)
        frame_values = page.get("frames") or ([page["frame"]] if page.get("frame") else [])
        for value in frame_values:
            path = Path(value)
            if not path.is_absolute():
                path = spec_path.parent / path
            if not path.exists():
                missing_frames.append(str(path.resolve()))

        for pattern, suggestion in CONTRACTIONS.items():
            for hit in re.finditer(pattern, text, flags=re.IGNORECASE):
                if any(phrase in text.lower() and hit.group(0).lower() in phrase for phrase in intentional_full_forms):
                    continue
                contraction_flags.append(
                    {"physical_page": physical_page, "phrase": hit.group(0), "suggestion": suggestion}
                )

        for quote in QUOTE_RE.findall(text):
            candidate = normalize(quote)
            if len(candidate.split()) < 2:
                continue
            if quote.lower() in approved:
                dialogue.append({
                    "physical_page": physical_page,
                    "book_dialogue": quote,
                    "status": "approved_book_addition",
                    "score": None,
                    "best_subtitle_window": None,
                })
                continue
            best_norm, best_raw = max(
                windows,
                key=lambda pair: match_score(candidate, pair[0]),
            )
            score = match_score(candidate, best_norm)
            dialogue.append({
                "physical_page": physical_page,
                "book_dialogue": quote,
                "status": "matches_subtitles" if score >= args.threshold else "manual_review",
                "score": round(score, 3),
                "best_subtitle_window": best_raw,
            })

    report = {
        "title": spec["book"]["title"],
        "physical_pages": len(spec["pages"]),
        "story_words": sum(page_words),
        "estimated_minutes_130_wpm": round(sum(page_words) / 130, 1),
        "page_words": page_words,
        "max_page_words": max(page_words),
        "quoted_passages": len(dialogue),
        "dialogue_manual_review": sum(item["status"] == "manual_review" for item in dialogue),
        "minimum_dialogue_match": min((item["score"] for item in dialogue if item["score"] is not None), default=None),
        "contraction_flags": contraction_flags,
        "missing_alt_pages": missing_alt,
        "missing_frame_files": missing_frames,
        "dialogue": dialogue,
    }
    report["pass"] = not any(
        [report["dialogue_manual_review"], contraction_flags, missing_alt, missing_frames]
    )
    summary = {key: value for key, value in report.items() if key not in {"dialogue", "page_words"}}
    print(json.dumps(summary, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
