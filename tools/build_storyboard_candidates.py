from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ffmpeg_runtime import get_ffmpeg_exe


BEATS = [
    ("cover", 117.0),
    ("01_piano", 35.0),
    ("02_turns", 63.0),
    ("03_discovery", 103.0),
    ("04_first_freeze", 113.0),
    ("05_mischief", 135.0),
    ("06_moustache", 161.0),
    ("07_chase", 181.0),
    ("08_bingo_left_out", 187.0),
    ("09_garden_dressup", 215.0),
    ("10_mums_lesson", 224.0),
    ("11_bingos_turn", 250.0),
    ("12_dad_chases", 262.0),
    ("13_squabble", 289.0),
    ("14_dad_wins", 299.0),
    ("15_garden_gnome", 318.0),
    ("16_bingo_speaks", 349.0),
    ("17_the_trick", 382.0),
    ("18_water_fountain", 393.0),
    ("19_sharing", 405.0),
    ("back", 419.0),
]


def timestamp(seconds: float) -> str:
    return f"{int(seconds // 60):02d}:{seconds % 60:05.2f}"


def extract(ffmpeg: str, video: Path, t: float, out: Path) -> None:
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{t:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out),
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    video = args.video.resolve()
    out = args.output.resolve()
    frames_dir = out / "frames"
    sheets_dir = out / "sheets"
    frames_dir.mkdir(parents=True, exist_ok=True)
    sheets_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg = get_ffmpeg_exe()
    offsets = (-1.5, -0.75, 0.0, 0.75, 1.5)
    font = ImageFont.load_default()

    rows = []
    for name, center in BEATS:
        beat_frames = []
        for i, offset in enumerate(offsets, 1):
            t = max(0.0, center + offset)
            target = frames_dir / f"{name}_{i}_{t:07.2f}.jpg"
            extract(ffmpeg, video, t, target)
            beat_frames.append((target, t))
        rows.append((name, beat_frames))

    cols, rows_per_sheet = 5, 4
    thumb_w, thumb_h, label_h, gap = 240, 135, 24, 10
    sheet_w = gap + cols * (thumb_w + gap)
    sheet_h = gap + rows_per_sheet * (thumb_h + label_h + gap)
    for page_no, start in enumerate(range(0, len(rows), rows_per_sheet), 1):
        sheet = Image.new("RGB", (sheet_w, sheet_h), "#20242b")
        draw = ImageDraw.Draw(sheet)
        for row_index, (name, beat_frames) in enumerate(rows[start : start + rows_per_sheet]):
            for col_index, (path, t) in enumerate(beat_frames):
                x = gap + col_index * (thumb_w + gap)
                y = gap + row_index * (thumb_h + label_h + gap)
                with Image.open(path) as src:
                    frame = src.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                sheet.paste(frame, (x, y))
                label = f"{name} | {timestamp(t)}"
                draw.text((x + 3, y + thumb_h + 6), label, fill="white", font=font)
        sheet.save(sheets_dir / f"choices_{page_no:02d}.jpg", quality=90)

    print(f"beats={len(BEATS)}")
    print(f"sheets={len(list(sheets_dir.glob('choices_*.jpg')))}")


if __name__ == "__main__":
    main()
