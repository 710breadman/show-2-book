from __future__ import annotations

import argparse
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ffmpeg_runtime import get_ffmpeg_exe


def timestamp(seconds: float) -> str:
    minutes = int(seconds // 60)
    return f"{minutes:02d}:{seconds - minutes * 60:05.2f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a timestamped frame-review contact sheet.")
    parser.add_argument("video", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--end", type=float, required=True)
    parser.add_argument("--step", type=float, default=0.5)
    parser.add_argument("--columns", type=int, default=6)
    parser.add_argument("--name", default="frames")
    args = parser.parse_args()

    if args.end <= args.start or args.step <= 0:
        raise ValueError("end must be greater than start and step must be positive")

    video = args.video.resolve()
    output = args.output_dir.resolve()
    frames_dir = output / f"{args.name}_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg = get_ffmpeg_exe()
    pattern = frames_dir / "frame_%03d.jpg"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{args.start:.3f}",
            "-i",
            str(video),
            "-t",
            f"{args.end - args.start:.3f}",
            "-vf",
            f"fps=1/{args.step}",
            "-q:v",
            "2",
            str(pattern),
        ],
        check=True,
    )

    frames = sorted(frames_dir.glob("frame_*.jpg"))
    thumb_w, thumb_h, label_h, gap = 320, 180, 34, 8
    rows = math.ceil(len(frames) / args.columns)
    sheet = Image.new(
        "RGB",
        (gap + args.columns * (thumb_w + gap), gap + rows * (thumb_h + label_h + gap)),
        "#20242b",
    )
    draw = ImageDraw.Draw(sheet)
    font_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    font = ImageFont.truetype(str(font_path), 18) if font_path.exists() else ImageFont.load_default()

    for index, frame_path in enumerate(frames):
        row, column = divmod(index, args.columns)
        x = gap + column * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)
        with Image.open(frame_path) as source:
            frame = source.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(frame, (x, y))
        draw.text((x + 5, y + thumb_h + 6), timestamp(args.start + index * args.step), fill="white", font=font)

    sheet_path = output / f"{args.name}_sheet.jpg"
    sheet.save(sheet_path, quality=94, subsampling=0)
    print(f"frames={len(frames)}")
    print(f"sheet={sheet_path}")


if __name__ == "__main__":
    main()
