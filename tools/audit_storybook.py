from __future__ import annotations

import argparse
import importlib.util
import re
from difflib import SequenceMatcher
from pathlib import Path


TAG_RE = re.compile(r"<[^>]+>")
QUOTE_RE = re.compile(r'"([^"]+)"')
WORD_RE = re.compile(r"\b[\w']+\b")
FORMAL_CONTRACTIONS = {
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
INTENTIONAL_FULL_FORMS = {
    "i will now play for you the rondo 'alla turca,'": "Dad's mock-formal concert announcement matches the subtitle's 'I will'.",
    "there you are!": "Dad's exclamation is idiomatic; 'there you're' would be incorrect.",
}
APPROVED_BOOK_ADDITIONS = {
    "mwa-ha-ha!": "Visualized comic laughter requested for read-aloud energy.",
}


def normalize(text: str) -> str:
    text = TAG_RE.sub("", text).replace("-\n", "")
    text = re.sub(r"\[[^]]+]", " ", text)
    text = re.sub(r"[^a-z0-9']+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def subtitle_cues(path: Path) -> list[str]:
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig", errors="replace"))
    cues = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines()]
        spoken = [line.lstrip("-").strip() for line in lines if line and "-->" not in line and not line.isdigit()]
        cleaned = normalize(" ".join(spoken))
        if cleaned:
            cues.append(cleaned)
    return cues


def load_pages(builder: Path) -> list[dict]:
    spec = importlib.util.spec_from_file_location("storybook_builder", builder)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {builder}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PAGES


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("builder", type=Path)
    parser.add_argument("subtitles", type=Path)
    args = parser.parse_args()

    pages = load_pages(args.builder.resolve())
    cues = subtitle_cues(args.subtitles.resolve())
    windows = []
    for size in (1, 2, 3, 4):
        windows.extend(" ".join(cues[i : i + size]) for i in range(len(cues) - size + 1))

    total_words = 0
    low_matches = []
    formal_hits = []
    intentional_full_forms = []
    approved_additions = []
    print("PAGE WORDS")
    for physical_page, page in enumerate(pages, 1):
        text = "".join(part for _, part in page.get("parts", []))
        words = len(WORD_RE.findall(text))
        total_words += words
        if page.get("kind", "story") == "story":
            print(f"{physical_page:02d}: {words:3d}")

        for pattern, suggestion in FORMAL_CONTRACTIONS.items():
            for hit in re.finditer(pattern, text, flags=re.IGNORECASE):
                matching_exception = next(
                    (phrase for phrase in INTENTIONAL_FULL_FORMS if phrase in text.lower() and hit.group(0).lower() in phrase),
                    None,
                )
                if matching_exception:
                    intentional_full_forms.append(
                        (physical_page, hit.group(0), INTENTIONAL_FULL_FORMS[matching_exception])
                    )
                    continue
                formal_hits.append((physical_page, hit.group(0), suggestion))

        for quote in QUOTE_RE.findall(text):
            candidate = normalize(quote)
            if len(candidate.split()) < 3:
                continue
            if quote.lower() in APPROVED_BOOK_ADDITIONS:
                approved_additions.append(
                    (physical_page, quote, APPROVED_BOOK_ADDITIONS[quote.lower()])
                )
                continue
            best = max(SequenceMatcher(None, candidate, window).ratio() for window in windows)
            if best < 0.62:
                low_matches.append((physical_page, best, quote))

    print(f"total_story_words={total_words}")
    print(f"estimated_read_minutes_130wpm={total_words / 130:.1f}")
    print("FORMAL CONTRACTION FLAGS")
    if formal_hits:
        for page, phrase, suggestion in formal_hits:
            print(f"page {page}: {phrase!r} -> consider {suggestion!r}")
    else:
        print("none")
    print("INTENTIONAL FULL-FORM EXCEPTIONS")
    if intentional_full_forms:
        for page, phrase, reason in intentional_full_forms:
            print(f"page {page}: {phrase!r} - {reason}")
    else:
        print("none")
    print("LOW SUBTITLE MATCHES")
    if low_matches:
        for page, score, quote in low_matches:
            print(f"page {page}: {score:.2f} {quote}")
    else:
        print("none")
    print("APPROVED BOOK-ONLY DIALOGUE/EFFECTS")
    if approved_additions:
        for page, phrase, reason in approved_additions:
            print(f"page {page}: {phrase!r} - {reason}")
    else:
        print("none")


if __name__ == "__main__":
    main()
