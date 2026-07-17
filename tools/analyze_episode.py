from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ffmpeg_runtime import get_ffmpeg_exe


PTS_RE = re.compile(r"pts_time:([0-9.]+)")


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def stamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes:02d}m{secs:05.2f}s"


def contact_sheets(images: list[tuple[Path, str]], output_dir: Path, prefix: str) -> None:
    if not images:
        return
    output_dir.mkdir(parents=True, exist_ok=True)
    cols, rows = 4, 4
    thumb_w, thumb_h, label_h, gap = 320, 180, 28, 12
    sheet_w = gap + cols * (thumb_w + gap)
    sheet_h = gap + rows * (thumb_h + label_h + gap)
    font = ImageFont.load_default()
    for page_no, offset in enumerate(range(0, len(images), cols * rows), 1):
        sheet = Image.new("RGB", (sheet_w, sheet_h), "#20242b")
        draw = ImageDraw.Draw(sheet)
        batch = images[offset : offset + cols * rows]
        for i, (path, label) in enumerate(batch):
            row, col = divmod(i, cols)
            x = gap + col * (thumb_w + gap)
            y = gap + row * (thumb_h + label_h + gap)
            with Image.open(path) as src:
                frame = src.convert("RGB")
                frame.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (thumb_w, thumb_h), "black")
                canvas.paste(frame, ((thumb_w - frame.width) // 2, (thumb_h - frame.height) // 2))
                sheet.paste(canvas, (x, y))
            draw.text((x + 4, y + thumb_h + 7), label, fill="white", font=font)
        sheet.save(output_dir / f"{prefix}_{page_no:02d}.jpg", quality=90)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--scene-threshold", type=float, default=0.18)
    args = parser.parse_args()

    video = args.video.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_exe()

    subtitles = out / "subtitles_en.srt"
    run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-map", "0:s:0", str(subtitles)])

    scenes_dir = out / "scene_candidates"
    scenes_dir.mkdir(exist_ok=True)
    scene_pattern = scenes_dir / "scene_%03d.jpg"
    vf = f"select='gt(scene,{args.scene_threshold})',showinfo,scale=960:-2"
    proc = run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-i",
            str(video),
            "-vf",
            vf,
            "-fps_mode",
            "vfr",
            "-q:v",
            "2",
            str(scene_pattern),
        ],
        capture=True,
    )
    times = [float(m.group(1)) for line in proc.stderr.splitlines() if (m := PTS_RE.search(line))]
    scene_files = sorted(scenes_dir.glob("scene_*.jpg"))
    index_rows: list[tuple[str, float, str]] = []
    renamed: list[tuple[Path, str]] = []
    for i, path in enumerate(scene_files):
        t = times[i] if i < len(times) else -1.0
        new_path = path.with_name(f"scene_{i + 1:03d}_{stamp(t) if t >= 0 else 'unknown'}.jpg")
        path.rename(new_path)
        label = f"{i + 1:03d}  {stamp(t) if t >= 0 else 'unknown'}"
        index_rows.append((new_path.name, t, label))
        renamed.append((new_path, label))

    with (out / "scene_index.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["filename", "seconds", "label"])
        writer.writerows(index_rows)
    contact_sheets(renamed, out / "contacts", "scenes")

    samples_dir = out / "timeline_samples"
    samples_dir.mkdir(exist_ok=True)
    sample_pattern = samples_dir / "sample_%03d.jpg"
    run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            "fps=1/8,scale=640:-2",
            "-q:v",
            "3",
            str(sample_pattern),
        ]
    )
    samples = sorted(samples_dir.glob("sample_*.jpg"))
    sample_labeled = []
    for i, path in enumerate(samples):
        t = i * 8.0
        new_path = path.with_name(f"sample_{i + 1:03d}_{stamp(t)}.jpg")
        path.rename(new_path)
        sample_labeled.append((new_path, f"{stamp(t)}"))
    contact_sheets(sample_labeled, out / "contacts", "timeline")

    print(f"subtitles={subtitles}")
    print(f"scene_candidates={len(renamed)}")
    print(f"timeline_samples={len(sample_labeled)}")


if __name__ == "__main__":
    main()
