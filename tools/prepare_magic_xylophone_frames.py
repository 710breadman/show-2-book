from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from ffmpeg_runtime import get_ffmpeg_exe


def extract_frame(ffmpeg: str, video: Path, seconds: float, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "1",
            str(output),
        ],
        check=True,
    )


def build_bingo_sequence(first_path: Path, second_path: Path, output: Path) -> None:
    with Image.open(first_path) as first_source, Image.open(second_path) as second_source:
        first = first_source.convert("RGB")
        second = second_source.convert("RGB")

        # The two portrait crops turn a change of action into a clean comic-book beat:
        # Bingo holds back with the xylophone, then tells Bluey how she feels.
        left_crop = first.crop((180, 0, 820, 720)).resize((636, 720), Image.Resampling.LANCZOS)
        right_crop = second.crop((320, 0, 960, 720)).resize((636, 720), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (1280, 720), "#F7F2EA")
        canvas.paste(left_crop, (0, 0))
        canvas.paste(right_crop, (644, 0))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((636, 0, 643, 719), fill="#FFF8ED")
        draw.line((639, 0, 639, 719), fill="#DCCEF5", width=2)
        canvas.save(output, quality=96, subsampling=0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("frames_dir", type=Path)
    args = parser.parse_args()

    video = args.video.resolve()
    frames_dir = args.frames_dir.resolve()
    ffmpeg = get_ffmpeg_exe()
    exact_frames = {
        "09_hair_pluck_0213.00.jpg": 213.00,
        "13_dad_overhead_0293.50.jpg": 293.50,
        "16_bingo_hesitates_0334.75.jpg": 334.75,
        "16_bingo_feelings_0348.25.jpg": 348.25,
        "19_sharing_smiles_0406.00.jpg": 406.00,
    }
    for filename, seconds in exact_frames.items():
        extract_frame(ffmpeg, video, seconds, frames_dir / filename)

    build_bingo_sequence(
        frames_dir / "16_bingo_hesitates_0334.75.jpg",
        frames_dir / "16_bingo_feelings_0348.25.jpg",
        frames_dir / "16_bingo_turns_composite.jpg",
    )
    print(f"prepared={len(exact_frames) + 1}")
    print(f"frames_dir={frames_dir}")


if __name__ == "__main__":
    main()
