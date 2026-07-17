from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(args.pdf.resolve()))
    scale = args.dpi / 72
    for index in range(len(document)):
        page = document[index]
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil()
        image.save(output / f"page-{index + 1:02d}.png")
        page.close()
    document.close()
    print(f"pages={index + 1 if 'index' in locals() else 0}")


if __name__ == "__main__":
    main()
