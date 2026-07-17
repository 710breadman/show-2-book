from __future__ import annotations

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from PIL import Image, ImageFilter


# Base preset: narrative_proposal.
# Named override: storybook_landscape (Letter landscape, 0.35 in margins,
# Trebuchet MS 18.5 pt body, 32 pt title, inline 16:9 image, pastel text panels).
PAGE_W, PAGE_H = landscape(letter)
MARGIN = 0.35 * 72
IMAGE_W = PAGE_W - 2 * MARGIN
IMAGE_H = IMAGE_W * 9 / 16
IMAGE_Y = PAGE_H - MARGIN - IMAGE_H

THEMES = [
    {"bg": "F5FBFE", "border": "B8E4F3", "panel": "E8F6FC"},
    {"bg": "FFFAF0", "border": "F3D89A", "panel": "FFF3D8"},
    {"bg": "F5FCF6", "border": "C5E8C8", "panel": "E9F7EB"},
    {"bg": "FFF7F3", "border": "F5CEC2", "panel": "FDEAE4"},
    {"bg": "FAF8FF", "border": "DCCEF5", "panel": "F0EAFB"},
    {"bg": "F3FBFA", "border": "BCE5DF", "panel": "E5F6F3"},
]

ROLE_STYLES = {
    "narrator": {"font": "Story", "color": "17324D", "bold": False},
    "dad": {"font": "ComicBold", "color": "2F5DA8", "bold": True},
    "bluey": {"font": "ComicBold", "color": "0087C8", "bold": True},
    "bingo": {"font": "ComicBold", "color": "E36C25", "bold": True},
    "mum": {"font": "ComicBold", "color": "C34F7A", "bold": True},
    "both": {"font": "ComicBold", "color": "6A49B8", "bold": True},
    "sound": {"font": "ComicBold", "color": "EF5662", "bold": True},
}

DEFAULT_BOOK = {
    "title": "The Magic Xylophone",
    "season": 1,
    "episode": 1,
    "cover_band": "52BDE5",
    "cover_title_color": "FFFFFF",
    "final_message": [
        {"text": "The best games aren't about getting every turn.", "color": "17324D"},
        {"text": "They're about making sure everyone gets to be part of the fun.", "color": "E36C25"},
    ],
}


PAGES = [
    {
        "kind": "cover",
        "frame": "cover_2_0116.25.jpg",
        "alt": "Bluey and Bingo hold the magic xylophone while Dad stands frozen behind them.",
        "sfx": {"text": "DING!", "x": 0.08, "y": 0.78, "size": 31, "rotation": -9, "color": "EF5662"},
    },
    {
        "frame": "01_piano_4_0035.75.jpg",
        "alt": "Dad pretends to be a piano while Bluey plays and Bingo waits nearby.",
        "parts": [
            ("dad", "\"Ladies and gentlemen, I will now play for you the rondo 'Alla Turca,'\" "),
            ("narrator", "announced Dad. He cracked his knuckles. "),
            ("dad", "\"Hmm, hmm, hmm!\" "),
            ("narrator", "Dad began, while Bluey squirmed and giggled on his lap. "),
            ("dad", "\"Hey! Piano!\" "),
            ("narrator", "said Dad as the laughing piano wriggled away."),
        ],
        "sfx": {"text": "HMM-HMM-HMM!", "x": 0.05, "y": 0.78, "size": 24, "rotation": -7, "color": "6A49B8"},
    },
    {
        "frame": "02_turns_4_0063.75.jpg",
        "alt": "Bluey stays on Dad's lap while Bingo asks for a turn.",
        "parts": [
            ("bingo", "\"Dad! I want to be the piano,\" "),
            ("narrator", "said Bingo. "),
            ("bluey", "\"No! It's still my turn,\" "),
            ("narrator", "said Bluey, hugging Dad tighter. Dad looked between them. "),
            ("dad", "\"Taking turns can be difficult.\" "),
            ("narrator", "Bingo stretched her arms wide. "),
            ("bingo", "\"Dad! She's had this many turns!\""),
        ],
    },
    {
        "frame": "03_discovery_1_0101.50.jpg",
        "alt": "Bingo discovers the rainbow xylophone in the toy basket.",
        "parts": [
            ("dad", "\"You can be the bum-bongos!\" "),
            ("narrator", "said Dad, drumming a silly beat. But Bingo wanted real bongos. She dug through the toy basket, then gasped. "),
            ("bingo", "\"Bluey, look!\" "),
            ("narrator", "Inside was the Magic Xylophone."),
        ],
    },
    {
        "frame": "04_first_freeze_4_0113.75.jpg",
        "alt": "Dad freezes in place after Bingo taps the xylophone.",
        "parts": [
            ("bluey", "\"Quick, Bingo! Get the dinger thing!\" "),
            ("narrator", "called Bluey. "),
            ("dad", "\"Let me up! Let me out of here!\" "),
            ("narrator", "cried Dad. "),
            ("bingo", "\"Got it! Do a ding! Freeze!\" "),
            ("sound", "DING! "),
            ("narrator", "Dad stopped mid-step. "),
            ("both", "\"Yeah! The Magic Xylophone!\" "),
            ("narrator", "cheered the girls."),
        ],
        "sfx": {"text": "DING!", "x": 0.06, "y": 0.78, "size": 32, "rotation": -8, "color": "EF5662"},
    },
    {
        "frame": "05_mischief_2_0134.25.jpg",
        "alt": "Bluey and Bingo pose frozen Dad while Mum looks on.",
        "parts": [
            ("bluey", "\"Mum, come and look at this!\" "),
            ("narrator", "called Bluey. Mum smiled at Dad's ridiculous pose. "),
            ("mum", "\"Oh, look! It's just like when we first met.\" "),
            ("narrator", "Bingo tapped the xylophone. "),
            ("sound", "DING! "),
            ("narrator", "Dad unfroze. "),
            ("dad", "\"What?! How did I get fingers up my nose? Oh. The Magic Xylophone!\""),
        ],
    },
    {
        "frame": "06_moustache_2_0160.25.jpg",
        "alt": "Dad wears a curly felt-pen moustache while Bluey grins beside him.",
        "parts": [
            ("bluey", "\"Freeze!\" "),
            ("narrator", "called Bluey. "),
            ("sound", "DING! "),
            ("narrator", "Dad stopped again. "),
            ("bluey", "\"Bingo, let's get the pens!\" "),
            ("narrator", "Soon Dad had a magnificent purple moustache. Mum admired their work. "),
            ("mum", "\"Oh, what a splendid moustache you have. Ooh! Lovely.\" "),
            ("bingo", "\"It's my turn to unfreeze him.\""),
        ],
        "sfx": {"text": "HEE HEE!", "x": 0.05, "y": 0.78, "size": 25, "rotation": -6, "color": "E36C25"},
    },
    {
        "frame": "07_chase_4_0181.75.jpg",
        "alt": "Dad chases Bluey and Bingo through the garden in a silly costume.",
        "parts": [
            ("bingo", "\"Unfreeze!\" "),
            ("narrator", "said Bingo. "),
            ("sound", "DING! "),
            ("narrator", "Dad came roaring after them. "),
            ("dad", "\"You kids! Give me the magic xylophone!\" "),
            ("bluey", "\"Run!\" "),
            ("narrator", "cried Bluey. Just before Dad caught them - "),
            ("sound", "DING! "),
            ("bluey", "\"Yaha! Too slow, Mr Moustache!\" "),
            ("narrator", "Bluey laughed."),
        ],
        "sfx": {"text": "DING!", "x": 0.06, "y": 0.78, "size": 31, "rotation": -8, "color": "EF5662"},
    },
    {
        "frame": "08_bingo_left_out_3_0187.00.jpg",
        "alt": "Bingo looks disappointed as Bluey keeps the xylophone.",
        "parts": [
            ("bingo", "\"Bluey, you're taking all the turns freezing,\" "),
            ("narrator", "said Bingo, her ears drooping. "),
            ("narrator", "But Bluey hurried away with the xylophone. "),
            ("bluey", "\"Come on, Bingo. Let's get the teddies.\" "),
            ("bingo", "\"Okay,\" "),
            ("narrator", "said Bingo quietly, following behind."),
        ],
    },
    {
        "frame": "09_hair_pluck_0213.00.jpg",
        "alt": "Mum plucks a loose hair from Dad while he stands frozen in antlers and dress-up clothes.",
        "parts": [
            ("bluey", "\"Mum! Mum! Look at Dad now!\" "),
            ("narrator", "called Bluey. Dad stood under a mountain of teddies, antlers and dress-ups. Mum leaned closer. "),
            ("mum", "\"This loose hair's been bugging me all morning,\" "),
            ("narrator", "said Mum as she plucked it free. "),
            ("sound", "PLUCK!"),
        ],
        "sfx": {"text": "PLUCK!", "x": 0.42, "y": 0.20, "size": 24, "rotation": 7, "color": "C34F7A"},
    },
    {
        "frame": "10_mums_lesson_3_0224.00.jpg",
        "alt": "Mum speaks to Bluey and Bingo beside their frozen, dressed-up Dad.",
        "parts": [
            ("bluey", "\"Okay, I'll unfreeze him,\" "),
            ("narrator", "said Bluey. "),
            ("bingo", "\"I want to do it. Mum, Bluey's not letting me have any turns,\" "),
            ("narrator", "said Bingo. "),
            ("narrator", "Mum knelt beside them. "),
            ("mum", "\"Bluey, if you don't take turns with people, people won't take turns with you.\" "),
            ("narrator", "Bluey hugged the xylophone. "),
            ("bluey", "\"But Bingo's too slow. Dad will catch her!\""),
        ],
    },
    {
        "frame": "11_bingos_turn_3_0250.00.jpg",
        "alt": "Bluey hands the xylophone dinger to Bingo in the garden.",
        "parts": [
            ("bluey", "\"Here, Bingo,\" "),
            ("narrator", "said Bluey, offering the dinger at last. "),
            ("bluey", "\"But stand right back here. That way, you could get a head start. He runs really fast when he's mad.\" "),
            ("narrator", "Bingo gripped the dinger. "),
            ("bingo", "\"Okay. Unfreeze!\" "),
            ("narrator", "said Bingo bravely."),
        ],
    },
    {
        "frame": "12_dad_chases_4_0262.75.jpg",
        "alt": "Bluey and Bingo race away as Dad springs after them.",
        "parts": [
            ("sound", "DING! "),
            ("narrator", "Dad sprang to life. "),
            ("dad", "\"There you are!\" "),
            ("bluey", "\"Run, Bingo! Back inside!\" "),
            ("narrator", "called Bluey. "),
            ("dad", "\"Bingo! Bluey! Come back here!\" "),
            ("narrator", "shouted Dad, thundering after them. The girls squeezed into a cupboard and tried not to giggle."),
        ],
        "sfx": {"text": "STOMP! STOMP!", "x": 0.05, "y": 0.78, "size": 24, "rotation": -5, "color": "2F5DA8"},
    },
    {
        "frame": "13_squabble_3_0289.00.jpg",
        "alt": "Bluey and Bingo tug on the xylophone while hiding in a cupboard.",
        "parts": [
            ("dad", "\"Where are they? I can't find them anywhere!\" "),
            ("narrator", "called Dad. Inside the cupboard, Bluey whispered, "),
            ("bluey", "\"I think we should freeze him, just in case. Give me the xylophone.\" "),
            ("bingo", "\"No, I want to freeze him! You've had all the freezing turns,\" "),
            ("narrator", "said Bingo. The sisters tugged and squabbled, never noticing Dad hiding above them."),
        ],
    },
    {
        "frame": "14_dad_wins_4_0299.75.jpg",
        "alt": "Dad triumphantly holds the xylophone after catching Bluey and Bingo.",
        "parts": [
            ("dad", "\"Freedom!\" "),
            ("narrator", "cried Dad, dropping out of the cupboard. "),
            ("dad", "\"Got it!\" "),
            ("narrator", "He snatched the xylophone and laughed wickedly. "),
            ("dad", "\"You ding-dongs were too busy squabbling. Freeze! Freeze, freeze, freeze!\" "),
            ("sound", "DING-DING-DING! "),
            ("narrator", "Bluey and Bingo froze. Dad grinned. "),
            ("dad", "\"Mwa-ha-ha!\" "),
            ("narrator", "he boomed."),
        ],
        "sfx": {"text": "MWA-HA-HA!", "x": 0.06, "y": 0.78, "size": 27, "rotation": -7, "color": "6A49B8"},
    },
    {
        "frame": "15_garden_gnome_4_0318.75.jpg",
        "alt": "Dad places frozen Bluey in a red gnome hat on the garden fountain.",
        "parts": [
            ("dad", "\"Oh, never mind. She'll keep,\" "),
            ("narrator", "said Dad. He carried frozen Bluey outside. "),
            ("dad", "\"Now, look at this lovely new garden gnome. Ahh. This is the perfect spot.\" "),
            ("narrator", "Then he noticed the felt pen on her fingers. "),
            ("dad", "\"Probably from some mischief! I'd better get the hose.\" "),
            ("bluey", "\"Nnn! Nnnnn!\" "),
            ("narrator", "Bluey protested."),
        ],
    },
    {
        "frame": "16_bingo_turns_composite.jpg",
        "alt": "Two moments show Bingo hesitating beside frozen Bluey, then explaining how Bluey's turn-taking made her feel.",
        "text_size": 15.4,
        "parts": [
            ("bluey", "\"Unfreeze me!\" "),
            ("narrator", "called Bluey. Bingo hesitated, then tapped the xylophone. "),
            ("sound", "DING! "),
            ("bluey", "\"Thanks, Bingo. Dad's gone to get the hose. Let's go and hi-\" "),
            ("sound", "DING! "),
            ("narrator", "Bingo froze her again. "),
            ("bingo", "\"Bluey, you always never take turns with me. You just take all of the turns, and it makes me feel sad. I'll unfreeze you if you promise you'll let me have turns, too.\" "),
            ("narrator", "Bluey blinked twice: yes."),
        ],
    },
    {
        "frame": "17_the_trick_4_0382.75.jpg",
        "alt": "Bluey and Bingo work together to freeze Dad beside the garden fountain.",
        "parts": [
            ("narrator", "Dad marched back with the hose. "),
            ("dad", "\"Okay, time for a little bath, garden gnome!\" "),
            ("narrator", "Bluey waited until he leaned close. Then she grabbed the dinger. "),
            ("bluey", "\"Freeze!\" "),
            ("sound", "DING! "),
            ("narrator", "Dad stopped. "),
            ("bluey", "\"We tricked you! Bingo unfroze me. I was just pretending. Now, Bingo!\""),
        ],
        "sfx": {"text": "DING!", "x": 0.18, "y": 0.67, "size": 31, "rotation": -7, "color": "EF5662"},
    },
    {
        "frame": "18_water_fountain_3_0393.00.jpg",
        "alt": "Frozen Dad sprays water like a fountain while Bluey and Bingo laugh.",
        "parts": [
            ("dad", "\"Blub-blub-blub!\" "),
            ("narrator", "bubbled Dad as the water sprayed from his mouth. Bluey and Bingo collapsed into giggles. This time, the trick belonged to both of them."),
        ],
        "sfx": {"text": "BLUB! BLUB!", "x": 0.66, "y": 0.68, "size": 25, "rotation": 6, "color": "0087C8"},
    },
    {
        "frame": "19_sharing_smiles_0406.00.jpg",
        "alt": "Bluey and Bingo smile as Bluey hands Bingo the magic xylophone.",
        "parts": [
            ("narrator", "After a while, Bluey held out the xylophone. "),
            ("bluey", "\"Here, Bingo. You can unfreeze him.\" "),
            ("narrator", "Bingo beamed. "),
            ("bingo", "\"Thanks, Bluey.\" "),
            ("narrator", "Dad kept blubbing. Bingo looked over at the Daddy water fountain and grinned. "),
            ("bingo", "\"Not just yet. I like the Daddy water fountain.\" "),
            ("narrator", "The sisters sat shoulder to shoulder. Now the game belonged to them both."),
        ],
    },
    {
        "kind": "back",
        "frame": "back_2_0418.25.jpg",
        "alt": "Bluey and Bingo sit together on the front steps with the magic xylophone.",
    },
]


def font_run(
    run,
    size: float,
    *,
    bold: bool = False,
    color: str = "17324D",
    font_name: str = "Trebuchet MS",
) -> None:
    run.font.name = font_name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), font_name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), font_name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def shade_paragraph(paragraph, fill: str) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    shd = p_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        p_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_picture_border(shape, color: str, width_pt: float = 2.5) -> None:
    sp_pr = shape._inline.graphic.graphicData.pic.spPr
    existing = sp_pr.find(qn("a:ln"))
    if existing is not None:
        sp_pr.remove(existing)
    line = OxmlElement("a:ln")
    line.set("w", str(int(width_pt * 12700)))
    fill = OxmlElement("a:solidFill")
    rgb = OxmlElement("a:srgbClr")
    rgb.set("val", color)
    fill.append(rgb)
    line.append(fill)
    join = OxmlElement("a:round")
    line.append(join)
    sp_pr.append(line)


def set_page_border(section, color: str = "B8E4F3") -> None:
    sect_pr = section._sectPr
    old = sect_pr.find(qn("w:pgBorders"))
    if old is not None:
        sect_pr.remove(old)
    borders = OxmlElement("w:pgBorders")
    borders.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "24")
        border.set(qn("w:space"), "6")
        border.set(qn("w:color"), color)
        borders.append(border)
    sect_pr.append(borders)


def parts_plain(page: dict) -> str:
    return "".join(text for _, text in page.get("parts", []))


def parts_markup(page: dict) -> str:
    marked = []
    for role, text in page.get("parts", []):
        style = ROLE_STYLES[role]
        marked.append(
            f'<font name="{style["font"]}" color="#{style["color"]}">{escape(text)}</font>'
        )
    return "".join(marked)


def add_page_field(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr_text, fld_char2])
    font_run(run, 9, color="6A7C8F")


def set_alt_text(shape, title: str, description: str) -> None:
    doc_pr = shape._inline.docPr
    doc_pr.set("title", title)
    doc_pr.set("descr", description)


def build_docx(assets: list[Path], output: Path, book: dict | None = None) -> None:
    book = book or DEFAULT_BOOK
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(0.35)
    section.bottom_margin = Inches(0.35)
    section.left_margin = Inches(0.35)
    section.right_margin = Inches(0.35)
    section.header_distance = Inches(0.15)
    section.footer_distance = Inches(0.15)
    set_page_border(section)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Trebuchet MS"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Trebuchet MS")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Trebuchet MS")
    normal.font.size = Pt(16.5)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing = 1.12
    for style_name, size, color, before, after in [
        ("Title", 32, "FFFFFF", 0, 3),
        ("Subtitle", 15, "17324D", 0, 3),
        ("Heading 1", 16, "2E74B5", 18, 10),
        ("Heading 2", 13, "2E74B5", 12, 6),
        ("Heading 3", 12, "1F4D78", 8, 4),
    ]:
        style = styles[style_name]
        style.font.name = "Trebuchet MS"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Trebuchet MS")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Trebuchet MS")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
    styles["Title"].font.bold = True

    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.clear()
    add_page_field(footer_p)

    for page_index, (page, asset) in enumerate(zip(PAGES, assets)):
        image_p = doc.add_paragraph()
        image_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        image_p.paragraph_format.space_before = Pt(0)
        image_p.paragraph_format.space_after = Pt(0)
        picture = image_p.add_run().add_picture(str(asset), width=Inches(10.0))
        set_alt_text(picture, f"Story illustration {page_index + 1}", page["alt"])

        kind = page.get("kind", "story")
        theme = THEMES[(page_index - 1) % len(THEMES)] if kind == "story" else THEMES[0]
        set_picture_border(picture, theme["border"], width_pt=2.5)

        if page.get("sfx"):
            effect_p = doc.add_paragraph()
            effect_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            effect_p.paragraph_format.space_before = Pt(0)
            effect_p.paragraph_format.space_after = Pt(0)
            effect_p.paragraph_format.line_spacing = 0.9
            effect_p.paragraph_format.keep_with_next = True
            font_run(
                effect_p.add_run(page["sfx"]["text"]),
                13.5,
                bold=True,
                color=page["sfx"]["color"],
                font_name="Comic Sans MS",
            )

        if kind == "cover":
            title_p = doc.add_paragraph()
            title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_p.paragraph_format.space_before = Pt(0)
            title_p.paragraph_format.space_after = Pt(2)
            shade_paragraph(title_p, book.get("cover_band", "52BDE5"))
            font_run(
                title_p.add_run(book["title"].upper()),
                book.get("cover_title_size_docx", 28),
                bold=True,
                color=book.get("cover_title_color", "FFFFFF"),
                font_name="Segoe Print",
            )
            subtitle_p = doc.add_paragraph()
            subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            subtitle_p.paragraph_format.space_before = Pt(0)
            subtitle_p.paragraph_format.space_after = Pt(0)
            cover_line = book.get(
                "cover_line",
                f"A picture-book retelling | Bluey, Season {book['season']}, Episode {book['episode']}",
            )
            font_run(subtitle_p.add_run(cover_line), 13.5, color="17324D")
        elif kind == "back":
            moral_p = doc.add_paragraph()
            moral_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            moral_p.paragraph_format.space_before = Pt(7)
            moral_p.paragraph_format.space_after = Pt(0)
            moral_p.paragraph_format.line_spacing = 1.0
            shade_paragraph(moral_p, THEMES[0]["panel"])
            for line_index, line in enumerate(book["final_message"]):
                run = moral_p.add_run(line["text"])
                font_run(
                    run,
                    book.get("final_message_size", 23),
                    bold=True,
                    color=line.get("color", "17324D"),
                    font_name="Segoe Print",
                )
                if line_index != len(book["final_message"]) - 1:
                    run.add_break()
        else:
            story_p = doc.add_paragraph()
            story_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            story_p.paragraph_format.left_indent = Inches(0.15)
            story_p.paragraph_format.right_indent = Inches(0.15)
            story_p.paragraph_format.space_before = Pt(1)
            story_p.paragraph_format.space_after = Pt(2)
            story_p.paragraph_format.line_spacing = 1.05
            shade_paragraph(story_p, theme["panel"])
            text_size = page.get("text_size", 16.5)
            for role, text in page["parts"]:
                role_style = ROLE_STYLES[role]
                font_run(
                    story_p.add_run(text),
                    text_size,
                    bold=role_style["bold"],
                    color=role_style["color"],
                    font_name="Trebuchet MS" if role == "narrator" else "Comic Sans MS",
                )

        if page_index != len(PAGES) - 1:
            doc.add_page_break()

    props = doc.core_properties
    props.title = f"Bluey: {book['title']} - Picture Book"
    props.subject = f"A private-family picture-book retelling of Bluey Season {book['season']}, Episode {book['episode']}"
    props.author = "Picture-book adaptation"
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


def draw_page_border(c: canvas.Canvas, color: str) -> None:
    c.setStrokeColor(HexColor(f"#{color}"))
    c.setLineWidth(5)
    c.roundRect(9, 9, PAGE_W - 18, PAGE_H - 18, 18, fill=0, stroke=1)


def draw_image(c: canvas.Canvas, path: Path, border_color: str) -> None:
    c.setFillColor(HexColor(f"#{border_color}"))
    c.roundRect(MARGIN - 5, IMAGE_Y - 5, IMAGE_W + 10, IMAGE_H + 10, 12, fill=1, stroke=0)
    c.drawImage(ImageReader(str(path)), MARGIN, IMAGE_Y, IMAGE_W, IMAGE_H, preserveAspectRatio=True, mask="auto")


def draw_sfx(c: canvas.Canvas, effect: dict) -> None:
    x = MARGIN + IMAGE_W * effect["x"]
    y = IMAGE_Y + IMAGE_H * effect["y"]
    c.saveState()
    c.translate(x, y)
    c.rotate(effect["rotation"])
    c.setFont("ComicBold", effect["size"])
    c.setFillAlpha(0.20)
    c.setFillColor(HexColor("#17324D"))
    c.drawString(3, -3, effect["text"])
    c.setFillAlpha(1)
    c.setFillColor(white)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1.5, -1.5), (1.5, 1.5)]:
        c.drawString(dx, dy, effect["text"])
    c.setFillColor(HexColor(f"#{effect['color']}"))
    c.drawString(0, 0, effect["text"])
    c.setFillColor(HexColor("#F6D04D"))
    c.circle(-8, effect["size"] * 0.9, 3, fill=1, stroke=0)
    c.circle(c.stringWidth(effect["text"], "ComicBold", effect["size"]) + 9, 4, 2.5, fill=1, stroke=0)
    c.restoreState()


def draw_xylophone(c: canvas.Canvas, y: float) -> None:
    colors = ["EF6B72", "F49A4A", "F6D04D", "64C982", "5BB9E8", "8E78D7"]
    bar_w = 37
    gap = 7
    total = len(colors) * bar_w + (len(colors) - 1) * gap
    start_x = (PAGE_W - total) / 2
    for i, color in enumerate(colors):
        h = 11 + i * 1.5
        c.setFillColor(HexColor(f"#{color}"))
        c.roundRect(start_x + i * (bar_w + gap), y, bar_w, h, 4, fill=1, stroke=0)


def build_pdf(assets: list[Path], output: Path, book: dict | None = None) -> None:
    book = book or DEFAULT_BOOK
    pdfmetrics.registerFont(TTFont("Story", r"C:\Windows\Fonts\trebuc.ttf"))
    pdfmetrics.registerFont(TTFont("StoryBold", r"C:\Windows\Fonts\trebucbd.ttf"))
    pdfmetrics.registerFont(TTFont("Comic", r"C:\Windows\Fonts\comic.ttf"))
    pdfmetrics.registerFont(TTFont("ComicBold", r"C:\Windows\Fonts\comicbd.ttf"))
    pdfmetrics.registerFont(TTFont("Display", r"C:\Windows\Fonts\segoepr.ttf"))
    pdfmetrics.registerFont(TTFont("DisplayBold", r"C:\Windows\Fonts\segoeprb.ttf"))
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle(f"Bluey: {book['title']} - Picture Book")
    c.setSubject(f"A private-family picture-book retelling of Bluey Season {book['season']}, Episode {book['episode']}")
    c.setAuthor("Picture-book adaptation")

    story_style = ParagraphStyle(
        "Story",
        fontName="Story",
        fontSize=17.2,
        leading=21.5,
        textColor=HexColor("#17324D"),
        alignment=TA_LEFT,
        spaceAfter=0,
    )
    back_style = ParagraphStyle(
        "Back",
        fontName="DisplayBold",
        fontSize=23,
        leading=29,
        textColor=HexColor("#17324D"),
        alignment=TA_CENTER,
    )

    for page_index, (page, asset) in enumerate(zip(PAGES, assets)):
        kind = page.get("kind", "story")
        if kind == "cover":
            theme = THEMES[0]
            c.setFillColor(HexColor(f"#{book.get('cover_band', '52BDE5')}"))
        elif kind == "back":
            theme = THEMES[0]
            c.setFillColor(HexColor(f"#{theme['bg']}"))
        else:
            theme = THEMES[(page_index - 1) % len(THEMES)]
            c.setFillColor(HexColor(f"#{theme['bg']}"))
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        draw_page_border(c, theme["border"])
        draw_image(c, asset, theme["border"])
        if page.get("sfx"):
            draw_sfx(c, page["sfx"])

        if kind == "cover":
            c.setFillColor(HexColor(f"#{book.get('cover_title_color', 'FFFFFF')}"))
            c.setFont("DisplayBold", book.get("cover_title_size_pdf", 30))
            c.drawCentredString(PAGE_W / 2, 108, book["title"].upper())
            c.setFont("Comic", 13.5)
            c.drawCentredString(
                PAGE_W / 2,
                82,
                book.get(
                    "cover_line",
                    f"A picture-book retelling | Bluey, Season {book['season']}, Episode {book['episode']}",
                ),
            )
            draw_xylophone(c, 45)
        elif kind == "back":
            c.setFillColor(HexColor(f"#{THEMES[0]['panel']}"))
            c.setStrokeColor(HexColor(f"#{THEMES[0]['border']}"))
            c.setLineWidth(1.5)
            c.roundRect(MARGIN, 48, IMAGE_W, 105, 16, fill=1, stroke=1)
            message = "<br/>".join(
                f'<font color="#{line.get("color", "17324D")}">{escape(line["text"])}</font>'
                for line in book["final_message"]
            )
            paragraph = Paragraph(message, back_style)
            w, h = paragraph.wrap(PAGE_W - 2 * MARGIN - 34, 92)
            paragraph.drawOn(c, (PAGE_W - w) / 2, 101 - h / 2)
            draw_xylophone(c, 25)
        else:
            panel_x = MARGIN
            panel_y = MARGIN
            panel_w = IMAGE_W
            panel_h = IMAGE_Y - 1.45 * MARGIN
            c.setFillColor(HexColor(f"#{theme['panel']}"))
            c.setStrokeColor(HexColor(f"#{theme['border']}"))
            c.setLineWidth(1.5)
            c.roundRect(panel_x, panel_y, panel_w, panel_h, 13, fill=1, stroke=1)
            text_size = page.get("text_size", story_style.fontSize)
            page_style = ParagraphStyle(
                f"Story-{page_index}",
                parent=story_style,
                fontSize=text_size,
                leading=text_size * 1.25,
            )
            paragraph = Paragraph(parts_markup(page), page_style)
            text_w = panel_w - 34
            text_h_limit = panel_h - 24
            w, h = paragraph.wrap(text_w, text_h_limit)
            paragraph.drawOn(c, panel_x + 17, panel_y + (panel_h - h) / 2 + 2)
            c.setFillColor(HexColor(f"#{theme['border']}"))
            c.setFont("ComicBold", 9)
            c.drawRightString(PAGE_W - MARGIN - 10, MARGIN + 8, str(page_index))

        c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("storyboard_frames", type=Path)
    parser.add_argument("output_root", type=Path)
    args = parser.parse_args()

    source = args.storyboard_frames.resolve()
    output_root = args.output_root.resolve()
    assets_dir = output_root / "assets" / "bluey_s01e01"
    assets_dir.mkdir(parents=True, exist_ok=True)

    assets = []
    for i, page in enumerate(PAGES):
        source_frame = source / page["frame"]
        if not source_frame.exists():
            raise FileNotFoundError(source_frame)
        target = assets_dir / f"page_{i:02d}.jpg"
        with Image.open(source_frame) as source_image:
            prepared = source_image.convert("RGB").resize((2560, 1440), Image.Resampling.LANCZOS)
            prepared = prepared.filter(ImageFilter.UnsharpMask(radius=1.0, percent=55, threshold=3))
            prepared.save(target, quality=96, subsampling=0, optimize=True)
        assets.append(target)

    pdf_path = output_root / "pdf" / "Bluey_S01E01_The_Magic_Xylophone_Picture_Book_Polished.pdf"
    docx_path = output_root / "docx" / "Bluey_S01E01_The_Magic_Xylophone_Picture_Book_Polished.docx"
    build_pdf(assets, pdf_path)
    build_docx(assets, docx_path)
    print(f"pdf={pdf_path}")
    print(f"docx={docx_path}")
    print(f"pages={len(PAGES)}")


if __name__ == "__main__":
    main()
