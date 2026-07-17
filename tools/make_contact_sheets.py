from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create labeled contact sheets from rendered book pages.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--glob", default="page-*.jpg")
    parser.add_argument("--per-sheet", type=int, default=8)
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--thumb-width", type=int, default=720)
    parser.add_argument("--prefix", default="contact")
    args = parser.parse_args()

    pages = sorted(args.input_dir.glob(args.glob), key=natural_key)
    if not pages:
        raise SystemExit(f"No pages matched {args.glob!r} in {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("arial.ttf", 24)
    label_height = 38
    gutter = 18

    with Image.open(pages[0]) as sample:
        ratio = sample.height / sample.width
    thumb_height = round(args.thumb_width * ratio)
    rows = math.ceil(args.per_sheet / args.columns)
    sheet_width = gutter + args.columns * (args.thumb_width + gutter)
    sheet_height = gutter + rows * (thumb_height + label_height + gutter)

    for sheet_index in range(math.ceil(len(pages) / args.per_sheet)):
        subset = pages[sheet_index * args.per_sheet : (sheet_index + 1) * args.per_sheet]
        sheet = Image.new("RGB", (sheet_width, sheet_height), "#222831")
        draw = ImageDraw.Draw(sheet)
        for local_index, path in enumerate(subset):
            row, col = divmod(local_index, args.columns)
            x = gutter + col * (args.thumb_width + gutter)
            y = gutter + row * (thumb_height + label_height + gutter)
            with Image.open(path) as page:
                thumb = page.convert("RGB").resize((args.thumb_width, thumb_height), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y))
            physical_page = sheet_index * args.per_sheet + local_index + 1
            draw.text((x, y + thumb_height + 4), f"Physical page {physical_page}", fill="white", font=font)
        output = args.output_dir / f"{args.prefix}_{sheet_index + 1:02d}.jpg"
        sheet.save(output, quality=92, subsampling=0)
        print(output)


if __name__ == "__main__":
    main()
