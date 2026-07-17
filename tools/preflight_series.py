from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


WORD_RE = re.compile(r"\b[\w']+\b")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def subtitle_stats(path: Path) -> tuple[int, int]:
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig", errors="replace"))
    cues = 0
    words = 0
    for block in blocks:
        lines = [line.strip() for line in block.splitlines()]
        spoken = [
            line
            for line in lines
            if line and "-->" not in line and not line.isdigit() and not line.startswith("[")
        ]
        if spoken:
            cues += 1
            words += len(WORD_RE.findall(" ".join(spoken)))
    return cues, words


def write_dossier(episode: dict, record: dict, output: Path) -> None:
    sources = episode.get("sources", {})
    community = "\n".join(f"  - {url}" for url in sources.get("community", [])) or "  - none recorded"
    page_range = episode.get("target_story_pages", [None, None])
    word_range = episode.get("target_words", [None, None])
    stats = (
        f"- Duration: {record.get('duration_seconds')} seconds\n"
        f"- Spoken subtitle cues: {record.get('subtitle_cues')}\n"
        f"- Spoken subtitle words: {record.get('subtitle_words')}\n"
        f"- Automated scene candidates: {record.get('scene_candidates')}\n"
        f"- Eight-second timeline samples: {record.get('timeline_samples')}"
        if record["status"] == "preflight_complete"
        else "- Local source is not present; subtitle and frame work is blocked until the episode is added."
    )
    text = f"""# {episode['title']} — source dossier

## Identity and status

- Rank: {episode['rank']}
- Official label: Season {episode['official']['season']}, Episode {episode['official']['episode']}
- Local file episode: {episode['local'].get('file_episode')}
- Status: {record['status']}
- Local source: {episode['local'].get('path')}

## Evidence pack

{stats}

- Official: {sources.get('official')}
- IMDb: {sources.get('imdb')}
- Community interpretation samples:
{community}

## Editorial starting point

- Story thesis: {episode.get('story_thesis')}
- Editorial care: {episode.get('editorial_care')}
- Final-message seed (not final copy): {episode.get('final_message_seed')}
- Working story-page budget: {page_range[0]}–{page_range[1]}
- Working word budget: {word_range[0]}–{word_range[1]}

## Gates before drafting

- [ ] Watch the episode closely and mark the playful surface, emotional hinge, climax, and landing.
- [ ] Cross-check every retained spoken line against the embedded subtitle cues and audio delivery.
- [ ] Review all candidate sheets; select expressions/actions that depict the same beat as the text.
- [ ] Record community-resonant moments without treating popularity as canon.
- [ ] Test two or three final messages; keep only the one earned by the episode.
- [ ] Build the beat map in `EPISODE_TEMPLATE.json` before writing full pages.
"""
    (output.parent / "SOURCE_DOSSIER.md").write_text(text, encoding="utf-8")


def preflight(episode: dict, root: Path, analyzer: Path) -> dict:
    rank = int(episode["rank"])
    title = episode["title"]
    output = root / f"{rank:02d}_{slugify(title)}" / "source_review"
    output.mkdir(parents=True, exist_ok=True)
    local = episode["local"]
    source = local.get("path")
    if not source:
        record = {
            "rank": rank,
            "title": title,
            "status": "source_needed",
            "output": str(output),
        }
        write_dossier(episode, record, output)
        return record

    subtitles = output / "subtitles_en.srt"
    index = output / "scene_index.csv"
    if not subtitles.exists() or not index.exists():
        subprocess.run(
            [sys.executable, str(analyzer), source, str(output)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    cue_count, subtitle_words = subtitle_stats(subtitles)
    scene_count = max(0, len(index.read_text(encoding="utf-8").splitlines()) - 1)
    sample_count = len(list((output / "timeline_samples").glob("*.jpg")))
    record = {
        "rank": rank,
        "title": title,
        "status": "preflight_complete",
        "local_source": source,
        "duration_seconds": local.get("duration_seconds"),
        "subtitle_cues": cue_count,
        "subtitle_words": subtitle_words,
        "scene_candidates": scene_count,
        "timeline_samples": sample_count,
        "output": str(output),
    }
    write_dossier(episode, record, output)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.resolve().read_text(encoding="utf-8"))
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    analyzer = Path(__file__).with_name("analyze_episode.py")
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(preflight, episode, root, analyzer) for episode in manifest["episodes"]]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"[{result['rank']:02d}] {result['title']}: {result['status']}", flush=True)
    results.sort(key=lambda item: item["rank"])
    report = {
        "manifest": str(args.manifest.resolve()),
        "available_preflights": sum(item["status"] == "preflight_complete" for item in results),
        "source_needed": sum(item["status"] == "source_needed" for item in results),
        "episodes": results,
    }
    report_path = root / "preflight_summary.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"summary={report_path}")


if __name__ == "__main__":
    main()
