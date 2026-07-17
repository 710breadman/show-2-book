from __future__ import annotations

import argparse
import csv
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from ffmpeg_runtime import get_ffmpeg_exe


EPISODE_RE = re.compile(r"\.S(?P<season>\d{2})E(?P<episode>\d{2})\.", re.IGNORECASE)
DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):([\d.]+)")
TAG_RE = re.compile(r"<[^>]+>")
TIMING_RE = re.compile(r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}")


def clean_subtitles(raw: str) -> str:
    text = html.unescape(TAG_RE.sub("", raw))
    lines = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if not stripped or stripped.isdigit() or TIMING_RE.fullmatch(stripped):
            continue
        lines.append(stripped)
    return re.sub(r"\s+", " ", " ".join(lines)).strip()


def discover_title(subtitle_text: str) -> str | None:
    patterns = [
        r"This episode of\s+[\"']?Bluey[\"']?\s+is called\s+[\"']?(.+?)(?:[.!?][\"']?|\[|$)",
        r"This episode is called\s+[\"']?(.+?)(?:[.!?][\"']?|\[|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, subtitle_text, flags=re.IGNORECASE)
        if match:
            title = match.group(1).strip(" .!\"'")
            return re.sub(r"\s+", " ", title)
    return None


def duration_seconds(stderr: str) -> float | None:
    match = DURATION_RE.search(stderr)
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def inspect_episode(ffmpeg: str, path: Path) -> dict:
    filename_match = EPISODE_RE.search(path.name)
    season = int(filename_match.group("season")) if filename_match else None
    episode = int(filename_match.group("episode")) if filename_match else None
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "info",
        "-i",
        str(path),
        "-map",
        "0:s:0",
        "-f",
        "srt",
        "-",
    ]
    try:
        result = subprocess.run(command, capture_output=True, timeout=40)
        raw = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        cleaned = clean_subtitles(raw)
        return {
            "season": season,
            "file_episode": episode,
            "title": discover_title(cleaned),
            "duration_seconds": duration_seconds(stderr),
            "subtitle_available": bool(cleaned),
            "path": str(path.resolve()),
            "filename": path.name,
            "inspection_error": None if result.returncode == 0 else f"ffmpeg exit {result.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {
            "season": season,
            "file_episode": episode,
            "title": None,
            "duration_seconds": None,
            "subtitle_available": False,
            "path": str(path.resolve()),
            "filename": path.name,
            "inspection_error": "timed out",
        }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Index a Bluey video library using embedded title-card subtitles.")
    parser.add_argument("library", type=Path)
    parser.add_argument("output_json", type=Path)
    args = parser.parse_args()

    library = args.library.resolve()
    videos = sorted(library.rglob("*.mkv"), key=lambda p: p.name.lower())
    ffmpeg = get_ffmpeg_exe()
    episodes = []
    for index, video in enumerate(videos, 1):
        row = inspect_episode(ffmpeg, video)
        episodes.append(row)
        print(f"[{index:03d}/{len(videos):03d}] S{row['season']}E{row['file_episode']}: {row['title'] or 'UNKNOWN'}", flush=True)

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "library": str(library),
        "episode_count": len(episodes),
        "episodes": episodes,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_path = args.output_json.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        fields = [
            "season",
            "file_episode",
            "title",
            "duration_seconds",
            "subtitle_available",
            "path",
            "filename",
            "inspection_error",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(episodes)
    print(f"json={args.output_json.resolve()}")
    print(f"csv={csv_path.resolve()}")


if __name__ == "__main__":
    main()
