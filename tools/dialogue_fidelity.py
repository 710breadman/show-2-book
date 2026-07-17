from __future__ import annotations

import argparse
import importlib.util
import json
import re
from difflib import SequenceMatcher
from pathlib import Path


QUOTE_RE = re.compile(r'"([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")
APPROVED_ADDITIONS = {"mwa-ha-ha!"}


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
        text = " ".join(spoken)
        if normalize(text):
            cues.append(text)
    return cues


def pages(path: Path) -> list[dict]:
    spec = importlib.util.spec_from_file_location("builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PAGES


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("builder", type=Path)
    parser.add_argument("subtitles", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--review-threshold", type=float, default=0.85)
    args = parser.parse_args()

    cues = subtitle_cues(args.subtitles.resolve())
    windows = []
    for size in (1, 2, 3, 4):
        for i in range(len(cues) - size + 1):
            raw = " ".join(cues[i : i + size])
            windows.append((normalize(raw), raw))

    results = []
    for physical_page, page in enumerate(pages(args.builder.resolve()), 1):
        text = "".join(fragment for _, fragment in page.get("parts", []))
        for quote in QUOTE_RE.findall(text):
            candidate = normalize(quote)
            if len(candidate.split()) < 2:
                continue
            if quote.lower() in APPROVED_ADDITIONS:
                results.append({
                    "physical_page": physical_page,
                    "book_dialogue": quote,
                    "status": "approved_book_addition",
                    "score": None,
                    "best_subtitle_window": None,
                })
                continue
            best_norm, best_raw = max(
                windows,
                key=lambda pair: SequenceMatcher(None, candidate, pair[0]).ratio(),
            )
            score = SequenceMatcher(None, candidate, best_norm).ratio()
            results.append({
                "physical_page": physical_page,
                "book_dialogue": quote,
                "status": "matches_subtitles" if score >= args.review_threshold else "manual_review",
                "score": round(score, 3),
                "best_subtitle_window": best_raw,
            })

    numeric = [item for item in results if item["score"] is not None]
    report = {
        "quoted_passages": len(results),
        "matched_at_or_above_threshold": sum(item["status"] == "matches_subtitles" for item in results),
        "manual_review": sum(item["status"] == "manual_review" for item in results),
        "approved_book_additions": sum(item["status"] == "approved_book_addition" for item in results),
        "minimum_match_score": min(item["score"] for item in numeric),
        "review_threshold": args.review_threshold,
        "results": results,
    }
    for item in sorted((r for r in results if r["status"] == "manual_review"), key=lambda r: r["score"]):
        print(f"page {item['physical_page']:02}: {item['score']:.3f} {item['book_dialogue']!r}")
        print(f"  source: {item['best_subtitle_window']}")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
