from __future__ import annotations

import argparse
import json
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image
from pypdf import PdfReader


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
BASE_14_FONTS = {
    "/Courier", "/Courier-Bold", "/Courier-Oblique", "/Courier-BoldOblique",
    "/Helvetica", "/Helvetica-Bold", "/Helvetica-Oblique", "/Helvetica-BoldOblique",
    "/Times-Roman", "/Times-Bold", "/Times-Italic", "/Times-BoldItalic",
    "/Symbol", "/ZapfDingbats",
}


def pdf_report(path: Path) -> dict:
    reader = PdfReader(path)
    sizes = []
    image_sizes = []
    fonts: dict[str, dict] = {}
    for page in reader.pages:
        sizes.append([float(page.mediabox.width), float(page.mediabox.height)])
        resources = page.get("/Resources", {}).get_object()
        for name, ref in resources.get("/Font", {}).items():
            font = ref.get_object()
            descriptor = font.get("/FontDescriptor")
            if descriptor is None and "/DescendantFonts" in font:
                descendant = font["/DescendantFonts"][0].get_object()
                descriptor = descendant.get("/FontDescriptor")
            embedded = False
            if descriptor is not None:
                descriptor = descriptor.get_object()
                embedded = any(k in descriptor for k in ("/FontFile", "/FontFile2", "/FontFile3"))
            base_font = str(font.get("/BaseFont", ""))
            fonts[str(name)] = {
                "base_font": base_font,
                "embedded": embedded,
                "standard_base14": base_font in BASE_14_FONTS,
            }
        for ref in resources.get("/XObject", {}).values():
            obj = ref.get_object()
            if obj.get("/Subtype") == "/Image":
                image_sizes.append([int(obj.get("/Width", 0)), int(obj.get("/Height", 0))])
    return {
        "pages": len(reader.pages),
        "page_sizes_points": sorted({tuple(s) for s in sizes}),
        "fonts": fonts,
        "all_nonstandard_fonts_embedded": bool(fonts) and all(
            info["embedded"] or info["standard_base14"] for info in fonts.values()
        ),
        "image_objects": len(image_sizes),
        "image_sizes_pixels": sorted({tuple(s) for s in image_sizes}),
    }


def docx_report(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        media = sorted(name for name in archive.namelist() if name.startswith("word/media/"))
        image_sizes = []
        for name in media:
            with Image.open(BytesIO(archive.read(name))) as image:
                image_sizes.append(image.size)
        root = ET.fromstring(archive.read("word/document.xml"))
    doc_pr = root.findall(".//wp:docPr", NS)
    inline_images = root.findall(".//wp:inline", NS)
    missing_alt = [node.get("name", "") for node in doc_pr if not node.get("descr", "").strip()]
    page_breaks = [
        node
        for node in root.findall(".//w:br", NS)
        if node.get(f"{{{NS['w']}}}type") == "page"
    ]
    return {
        "inline_images": len(inline_images),
        "unique_media_images": len(media),
        "image_sizes_pixels": sorted(set(image_sizes)),
        "images_missing_alt_text": missing_alt,
        "page_breaks": len(page_breaks),
    }


def render_report(path: Path) -> dict:
    pngs = sorted(path.glob("page-*.png"))
    sizes = []
    for png in pngs:
        with Image.open(png) as image:
            sizes.append(image.size)
    return {"rendered_pages": len(pngs), "render_sizes_pixels": sorted(set(sizes))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("docx", type=Path)
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expected-pages", type=int)
    args = parser.parse_args()

    report = {
        "pdf": pdf_report(args.pdf.resolve()),
        "docx": docx_report(args.docx.resolve()),
        "render": render_report(args.render_dir.resolve()),
    }
    expected_pages = args.expected_pages or report["pdf"]["pages"]
    report["expected_pages"] = expected_pages
    report["pass"] = (
        report["pdf"]["pages"] == expected_pages
        and report["pdf"]["all_nonstandard_fonts_embedded"]
        and report["docx"]["inline_images"] == expected_pages
        and not report["docx"]["images_missing_alt_text"]
        and report["docx"]["page_breaks"] == expected_pages - 1
        and report["render"]["rendered_pages"] == expected_pages
    )
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
