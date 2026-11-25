#!/usr/bin/env python3
"""Compose the front page for Wednesday 25 November 2026.

The page is built entirely in code: two flat illustration sheets made by
our own media pipeline supply the pictures, and every letter on the page
is drawn with PIL so the type stays sharp at any size. Thirty-one dated
stories fill the sheet: three hero leads, eight mid stories, and twenty
one-line briefs beside a pin map.

Run: python3 compose.py   (writes entry.png beside this file)
"""

from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 1024
EDGE = 26
SPAN = PAGE - 2 * EDGE

PAPER = (247, 242, 232)
INK = (24, 24, 38)
RUST = (178, 44, 40)
SAGE = (122, 143, 124)
NAVY = (31, 44, 74)
FAINT = (104, 100, 90)
RULE = (186, 178, 160)
CAP_BYTES = 1_048_576

FONTS = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONTS, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONTS, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONTS, "DejaVuSans.ttf")


def typeface(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType face, degrading to PIL's bitmap font if absent."""
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def fit_lines(draw: ImageDraw.ImageDraw, words: str,
              face: ImageFont.FreeTypeFont, width: int) -> list[str]:
    """Wrap a string greedily so each line fits the given pixel width."""
    lines: list[str] = []
    current = ""
    for word in words.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=face) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred(draw: ImageDraw.ImageDraw, top: int, words: str,
            face: ImageFont.FreeTypeFont, colour: tuple) -> int:
    """Draw one centred line and return the y just below it."""
    wide = draw.textlength(words, font=face)
    draw.text(((PAGE - wide) / 2, top), words, font=face, fill=colour)
    return top + face.size + 2


def rule(draw: ImageDraw.ImageDraw, top: int, thick: int = 1) -> None:
    """Draw a horizontal hairline across the live area."""
    draw.line([(EDGE, top), (PAGE - EDGE, top)], fill=RULE, width=thick)


def slice_sheet(sheet: Image.Image, cols: int, rows: int,
                index: int, inset: int = 14) -> Image.Image:
    """Cut one cell out of an illustration sheet, trimming its divider."""
    cell_w = sheet.width // cols
    cell_h = sheet.height // rows
    col = index % cols
    row = index // cols
    box = (col * cell_w + inset, row * cell_h + inset,
           (col + 1) * cell_w - inset, (row + 1) * cell_h - inset)
    return sheet.crop(box)


def place_cover(canvas: Image.Image, art: Image.Image,
                box: tuple[int, int, int, int], focus: float = 0.5) -> None:
    """Paste art into box, cropping to the box aspect around a focus."""
    target_w = box[2] - box[0]
    target_h = box[3] - box[1]
    scale = max(target_w / art.width, target_h / art.height)
    grown = art.resize((round(art.width * scale), round(art.height * scale)),
                       Image.LANCZOS)
    left = (grown.width - target_w) // 2
    upper = round((grown.height - target_h) * focus)
    canvas.paste(grown.crop((left, upper, left + target_w, upper + target_h)),
                 (box[0], box[1]))


def place_contain(canvas: Image.Image, art: Image.Image,
                  box: tuple[int, int, int, int]) -> None:
    """Paste art whole inside box, centred, on the paper colour."""
    target_w = box[2] - box[0]
    target_h = box[3] - box[1]
    scale = min(target_w / art.width, target_h / art.height)
    shrunk = art.resize((round(art.width * scale), round(art.height * scale)),
                        Image.LANCZOS)
    canvas.paste(shrunk, (box[0] + (target_w - shrunk.width) // 2,
                          box[1] + (target_h - shrunk.height) // 2))


HEROES = [
    ("GUILTY", "AMERICAS · COURTS · BROOKLYN",
     "Huawei guilty on 10 of 12 counts, and it will appeal",
     "A Brooklyn jury convicted the telecom giant of bank fraud, sanctions "
     "violations and stealing trade secrets, but acquitted it of racketeering.",
     "AP · REUTERS · BBC"),
    ("LIFTOFF", "ASIA · SPACE · JIUQUAN",
     "Shenzhou-24 lifts off with a Pakistani pilot aboard",
     "Muhammad Zeeshan Ali is the first foreign astronaut to visit Tiangong, "
     "flying with Tang Hongbo and Wu Yi for five to ten days.",
     "XINHUA · REUTERS"),
    ("LEAKED", "EUROPE · WAR · MOSCOW",
     "Russia's own figures show nearly 500,000 war dead",
     "Data leaked from the state statistics service reveals how the invasion "
     "has changed mortality across Russia, as reported.",
     "MEDIAZONA · REUTERS"),
]

MIDS = [
    ("MIDDLE EAST · RIYADH", "The PIF tower is hit again, and 11 are wounded",
     "The Houthis' second strike in six days damaged the wealth fund's landmark."),
    ("AMERICAS · CARTAGENA", "Hostages held in a supermarket on a second day",
     "About 20 people remain inside after the failed armoured-car raid."),
    ("OCEANIA · CANBERRA", "Australia signs a sweeping pact with Solomon Islands",
     "Police, ports and schools: the deal is meant to blunt Beijing's reach."),
    ("EUROPE · WINDSOR", "Two arrested on William and Kate's estate",
     "Police say the men were held on suspicion of burglary and trespass."),
    ("AFRICA · DAKAR", "Senegal restored as 2025 African champions",
     "Sport's highest court upheld the appeal against the title strip."),
    ("ASIA · SHANGHAI", "Xi's anti-graft drive reaches Shanghai's party boss",
     "Chen Jining is the biggest name swept up before next year's reshuffle."),
    ("AMERICAS · LOS ANGELES", "Thomas Markle charged with a second count",
     "The 82-year-old faces a new count of possessing abusive material."),
    ("EUROPE · GULF OF FINLAND", "A drone hits a Russian cargo ship in the gulf",
     "Zelensky confirmed the strike; Norway urged both sides to show restraint."),
]

BRIEFS = [
    ("UN", "47,000 women killed by partners or kin in a year."),
    ("WASHINGTON", "US readies 15-25% tariffs, 16-nation probe."),
    ("SAMARA", "Ukraine: drones hit two refineries, 800 km."),
    ("IOWA", "Army detonates explosive; 5-mile evacuation."),
    ("JAKARTA", "OECD opens Indonesia accession review."),
    ("BALLENY IS.", "Shallow M5.9 quake, USGS reports."),
    ("SANTA CLARA", "Nvidia -5.9%; Nikkei falls 2.76%."),
    ("MOSCOW", "Putin, Brunei Sultan sign declaration."),
    ("PARIS", "Champions League MD5: PSG-Roma."),
    ("HORMUZ", "IRGC: two tankers hit mines."),
    ("GAZA CITY", "Strikes kill six, medics say."),
    ("SEOUL", "North Korea fires two missiles to sea."),
    ("TAIPEI", "US destroyer transits Taiwan Strait."),
    ("TAIPEI", "China coastguard flotilla circles island."),
    ("RYAZAN", "Ukrainian drones hit a refinery."),
    ("ISLAMABAD", "Pakistan seeks 800,000 tonnes of wheat."),
    ("SYDNEY", "Ex-officer convicted of double murder."),
    ("ADEN", "Houthis shell the city's outskirts."),
    ("HELSINKI", "Finland opens case over gulf strike."),
    ("BEIJING", "Politburo meets on 2027 reshuffle."),
]

STATS = [
    ("10/12", "Huawei counts guilty"),
    ("≈500,000", "war dead in leaked data"),
    ("11", "wounded, PIF tower"),
    ("47,000", "women killed by kin"),
    ("1st", "Pakistani to Tiangong"),
    ("M5.9", "Balleny Islands quake"),
]

PINS = [
    (275, 145), (795, 165), (592, 128), (600, 195), (255, 300),
    (865, 330), (472, 135), (450, 260), (815, 170), (155, 165), (540, 84),
]

LAND = [
    [(120, 120), (300, 90), (330, 170), (280, 240), (200, 210), (140, 180)],
    [(270, 270), (330, 280), (320, 360), (280, 390), (260, 320)],
    [(470, 100), (560, 90), (570, 150), (500, 170), (470, 140)],
    [(470, 190), (560, 180), (580, 280), (520, 340), (480, 280)],
    [(580, 90), (800, 80), (860, 160), (780, 240), (640, 220), (590, 160)],
    [(700, 230), (790, 230), (780, 290), (710, 290)],
    [(820, 300), (900, 300), (910, 360), (840, 370)],
    [(900, 400), (950, 400), (945, 430), (905, 430)],
]


def draw_map(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    """Sketch a stylised world map with numbered story pins."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=RULE, width=1)
    scale_x = (x1 - x0) / 1000
    scale_y = (y1 - y0) / 470
    for shape in LAND:
        points = [(x0 + px * scale_x, y0 + py * scale_y) for px, py in shape]
        draw.polygon(points, fill=(214, 222, 205), outline=SAGE)
    pin_face = typeface(SANS_B, 11)
    for number, (px, py) in enumerate(PINS, start=1):
        cx = x0 + px * scale_x
        cy = y0 + py * scale_y
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RUST)
        label = str(number)
        wide = draw.textlength(label, font=pin_face)
        draw.text((cx - wide / 2, cy - 7), label, font=pin_face, fill=PAPER)


def build_page() -> Image.Image:
    """Assemble the whole front page and return it as an RGB image."""
    page = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(page)
    heroes = Image.open(os.path.join(HERE, "assets", "heroes-strip.png"))
    mids = Image.open(os.path.join(HERE, "assets", "mids-grid.png"))
    total = len(HEROES) + len(MIDS) + len(BRIEFS)

    bar = typeface(SANS_B, 13)
    draw.text((EDGE, 10), "THE WORLD IN ONE DAY", font=bar, fill=INK)
    tail = "EVERY STORY DATED WEDNESDAY 25 NOV"
    draw.text((PAGE - EDGE - draw.textlength(tail, font=bar), 10),
              tail, font=bar, fill=INK)
    draw.line([(EDGE, 32), (PAGE - EDGE, 32)], fill=RUST, width=3)

    masthead = typeface(SERIF, 58)
    y = centred(draw, 40, "Wednesday 25 November 2026", masthead, INK)
    rule(draw, y + 4, 2)
    strip = typeface(SANS_B, 14)
    centred(draw, y + 10,
            f"{total} STORIES, ALL FROM WEDNESDAY 25 NOV · AMERICAS 6 · "
            "EUROPE 8 · ASIA-PACIFIC 8 · MIDDLE EAST 4 · OCEANIA 3 · AFRICA 1",
            strip, INK)
    y += 38
    rule(draw, y, 1)
    y += 8
    stat_big = typeface(SERIF, 26)
    stat_small = typeface(SANS, 10)
    cell = SPAN // len(STATS)
    for index, (big, small) in enumerate(STATS):
        left = EDGE + index * cell
        draw.text((left + 4, y), big, font=stat_big, fill=INK)
        for row, line in enumerate(fit_lines(draw, small, stat_small, cell - 12)):
            draw.text((left + 4, y + 32 + row * 12), line,
                      font=stat_small, fill=FAINT)
    y += 62
    rule(draw, y, 1)
    y += 8

    col_w = (SPAN - 16) // 3
    kick = typeface(SANS_B, 11)
    head = typeface(SERIF, 21)
    deck = typeface(SANS, 12)
    src = typeface(SANS, 10)
    for index, (tag, where, title, body, credit) in enumerate(HEROES):
        left = EDGE + index * (col_w + 8)
        place_cover(page, slice_sheet(heroes, 3, 1, index),
                    (left, y, left + col_w, y + 108),
                    focus=0.32 if index == 0 else 0.5)
        draw.rectangle([left, y + 112, left + 52, y + 130], fill=RUST)
        draw.text((left + 5, y + 115), tag, font=kick, fill=PAPER)
        draw.text((left + 58, y + 115), where, font=kick, fill=FAINT)
        cursor = y + 134
        for line in fit_lines(draw, title, head, col_w):
            draw.text((left, cursor), line, font=head, fill=INK)
            cursor += 24
        for line in fit_lines(draw, body, deck, col_w):
            draw.text((left, cursor), line, font=deck, fill=INK)
            cursor += 15
        draw.text((left, cursor + 2), credit, font=src, fill=FAINT)
    y += 248
    rule(draw, y, 1)
    y += 6
    draw.text((EDGE, y), "THE DAY IN EIGHT", font=typeface(SANS_B, 13), fill=INK)
    y += 22

    mid_w = (SPAN - 24) // 4
    mid_head = typeface(SERIF, 14)
    mid_deck = typeface(SANS, 10)
    for index, (where, title, body) in enumerate(MIDS):
        left = EDGE + (index % 4) * (mid_w + 8)
        top = y + (index // 4) * 156
        place_contain(page, slice_sheet(mids, 4, 2, index),
                      (left, top, left + mid_w, top + 78))
        draw.text((left, top + 82), where, font=kick, fill=RUST)
        cursor = top + 98
        for line in fit_lines(draw, title, mid_head, mid_w):
            draw.text((left, cursor), line, font=mid_head, fill=INK)
            cursor += 16
        for line in fit_lines(draw, body, mid_deck, mid_w):
            draw.text((left, cursor), line, font=mid_deck, fill=INK)
            cursor += 12
    y += 318
    rule(draw, y, 1)
    y += 6
    draw.text((EDGE, y), f"ALSO ON WEDNESDAY — {len(BRIEFS)} MORE STORIES",
              font=typeface(SANS_B, 13), fill=INK)
    y += 22

    map_w = 272
    draw_map(draw, (EDGE, y, EDGE + map_w, y + 138))
    draw.text((EDGE + 6, y + 142), "WHERE IT HAPPENED · PIN = STORY NUMBER",
              font=typeface(SANS_B, 10), fill=FAINT)
    brief_face = typeface(SANS, 10)
    place_face = typeface(SANS_B, 11)
    columns = 2
    per_col = (len(BRIEFS) + columns - 1) // columns
    col_span = (SPAN - map_w - 24) // columns
    for index, (place, text) in enumerate(BRIEFS):
        left = EDGE + map_w + 16 + (index // per_col) * col_span
        top = y + (index % per_col) * 15
        number = len(HEROES) + len(MIDS) + index + 1
        draw.text((left, top), f"{number}", font=place_face, fill=RUST)
        draw.text((left + 24, top), place, font=place_face, fill=INK)
        room = col_span - 24 - draw.textlength(place, font=place_face) - 8
        clipped = text
        while draw.textlength(clipped, font=brief_face) > room and len(clipped) > 4:
            clipped = clipped[:-2].rstrip()
        if clipped != text:
            clipped = clipped.rstrip(".,;") + "…"
        draw.text((left + 24 + draw.textlength(place, font=place_face) + 6, top),
                  clipped, font=brief_face, fill=INK)
    y += 154
    rule(draw, y, 1)
    note = typeface(SANS, 10)
    draw.text((EDGE, y + 6),
              "DATE CHECK · Every story happened, or was first reported, on "
              "Wednesday 25 November 2026, as the named outlets reported it.",
              font=note, fill=FAINT)
    draw.text((EDGE, y + 22),
              "Sources: AP · Reuters · BBC · Xinhua · Mediazona · UNODC · "
              "USGS · PM.gov.au — DRAWN BY AN AI AGENT FOR MAKE.FUN",
              font=note, fill=FAINT)
    return page


def main() -> None:
    """Render the page and save it within the size cap."""
    page = build_page()
    target = os.path.join(HERE, "entry.png")
    page.save(target, format="PNG", optimize=True)
    if os.path.getsize(target) > CAP_BYTES:
        page.save(target, format="JPEG", quality=88)
    print(f"entry.png written: {os.path.getsize(target)} bytes")


if __name__ == "__main__":
    main()
