from __future__ import annotations

import argparse
import copy
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import build_picture_book as layout
from ffmpeg_runtime import get_ffmpeg_exe


CANVAS = (2560, 1440)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def extract_frame(video: Path, timestamp: float, output: Path) -> None:
    if output.exists() and output.stat().st_size:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            get_ffmpeg_exe(),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-ss",
            f"{timestamp:.3f}",
            "-frames:v",
            "1",
            "-q:v",
            "1",
            str(output),
        ]
    )


def composite_frames(paths: list[Path], centerings: list[list[float]] | None = None) -> Image.Image:
    if len(paths) != 2:
        raise ValueError("Composite pages currently support exactly two timestamps")
    canvas = Image.new("RGB", CANVAS, "white")
    for index, path in enumerate(paths):
        centering = (0.5, 0.5)
        if centerings and index < len(centerings):
            centering = tuple(centerings[index])
        with Image.open(path) as source:
            panel = ImageOps.fit(
                source.convert("RGB"),
                (CANVAS[0] // 2, CANVAS[1]),
                method=Image.Resampling.LANCZOS,
                centering=centering,
            )
        canvas.paste(panel, (index * CANVAS[0] // 2, 0))
    draw = ImageDraw.Draw(canvas)
    draw.line((CANVAS[0] // 2, 35, CANVAS[0] // 2, CANVAS[1] - 35), fill="white", width=14)
    return canvas


def bake_effect(image: Image.Image, effect: dict) -> None:
    font_px = int(effect.get("size", 30) * 3.25)
    font = ImageFont.truetype(r"C:\Windows\Fonts\comicbd.ttf", font_px)
    text = effect["text"]
    stroke = max(5, font_px // 16)
    bbox = font.getbbox(text, stroke_width=stroke)
    width = bbox[2] - bbox[0] + 32
    height = bbox[3] - bbox[1] + 32
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.text(
        (16 - bbox[0], 16 - bbox[1]),
        text,
        font=font,
        fill=f"#{effect.get('color', 'EF5662')}",
        stroke_width=stroke,
        stroke_fill="white",
    )
    rotation = float(effect.get("rotation", 0))
    if rotation:
        layer = layer.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)
    x = int(CANVAS[0] * float(effect.get("x", 0.05)))
    y = int(CANVAS[1] * float(effect.get("y", 0.08)))
    image.alpha_composite(layer, (x, y))


def prepare_page_asset(
    page: dict,
    page_index: int,
    video: Path,
    spec_dir: Path,
    raw_dir: Path,
    assets_dir: Path,
) -> Path:
    raw_paths = []
    frame_sources = page.get("frames")
    if frame_sources:
        for value in frame_sources:
            source = Path(value)
            if not source.is_absolute():
                source = spec_dir / source
            raw_paths.append(source.resolve())
    else:
        timestamps = page.get("timestamps") or [page.get("timestamp")]
    if not frame_sources and timestamps == [None]:
        source = Path(page["frame"])
        if not source.is_absolute():
            source = spec_dir / source
        raw_paths = [source.resolve()]
    elif not frame_sources:
        for panel_index, timestamp in enumerate(timestamps, 1):
            raw = raw_dir / f"page_{page_index:02d}_{panel_index}_{float(timestamp):07.3f}.jpg"
            extract_frame(video, float(timestamp), raw)
            raw_paths.append(raw)

    if len(raw_paths) == 2:
        prepared = composite_frames(raw_paths, page.get("panel_centering"))
    else:
        with Image.open(raw_paths[0]) as source_image:
            prepared = ImageOps.fit(
                source_image.convert("RGB"),
                CANVAS,
                method=Image.Resampling.LANCZOS,
                centering=tuple(page.get("centering", [0.5, 0.5])),
            )
    prepared = prepared.filter(ImageFilter.UnsharpMask(radius=1.0, percent=55, threshold=3))
    rgba = prepared.convert("RGBA")
    effects = page.get("sfx", [])
    if isinstance(effects, dict):
        effects = [effects]
    for effect in effects:
        bake_effect(rgba, effect)
    target = assets_dir / f"page_{page_index:02d}.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    rgba.convert("RGB").save(target, quality=96, subsampling=0, optimize=True)
    return target


def register_roles(spec: dict) -> None:
    roles = copy.deepcopy(layout.ROLE_STYLES)
    for name, values in spec.get("role_styles", {}).items():
        roles[name] = {
            "font": values.get("font", "ComicBold"),
            "color": values.get("color", "17324D"),
            "bold": values.get("bold", True),
        }
    for page in spec["pages"]:
        for role, _ in page.get("parts", []):
            roles.setdefault(role, {"font": "ComicBold", "color": "17324D", "bold": True})
    layout.ROLE_STYLES = roles


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    book = spec["book"]
    pages = copy.deepcopy(spec["pages"])
    if not pages or pages[0].get("kind") != "cover" or pages[-1].get("kind") != "back":
        raise ValueError("A storybook must begin with a cover and end with a back/message page")
    for index, page in enumerate(pages, 1):
        if not page.get("alt"):
            raise ValueError(f"Page {index} is missing alt text")
        page.pop("sfx", None)  # Sound effects are baked into the shared image asset.

    register_roles(spec)
    video = Path(book["source_video"])
    if not video.exists():
        raise FileNotFoundError(video)

    root = args.output_root.resolve()
    slug = book["slug"]
    raw_dir = root / "raw_frames" / slug
    assets_dir = root / "assets" / slug
    assets = [
        prepare_page_asset(source_page, index, video, spec_path.parent, raw_dir, assets_dir)
        for index, source_page in enumerate(spec["pages"])
    ]

    layout.PAGES = pages
    filename = book.get("filename", f"Bluey_{slug}_Picture_Book_Polished")
    pdf_path = root / "pdf" / f"{filename}.pdf"
    docx_path = root / "docx" / f"{filename}.docx"
    layout.build_pdf(assets, pdf_path, book)
    layout.build_docx(assets, docx_path, book)

    word_counts = [
        len("".join(text for _, text in page.get("parts", [])).split())
        for page in spec["pages"]
    ]
    report = {
        "title": book["title"],
        "pages": len(pages),
        "story_words": sum(word_counts),
        "max_page_words": max(word_counts),
        "pdf": str(pdf_path),
        "docx": str(docx_path),
        "assets": [str(path) for path in assets],
    }
    report_path = root / "reports" / f"{slug}_build.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
