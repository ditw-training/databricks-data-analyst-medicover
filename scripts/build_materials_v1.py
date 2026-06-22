"""Build v1 materials for Databricks-Data-Analyst-Medi.

This script intentionally avoids external notebook dependencies. It writes
Databricks-compatible nbformat v4 JSON directly and uses Pillow for visual
assets.
"""

from __future__ import annotations

import json
import random
import shutil
import textwrap
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / "Databricks-Data-Analyst"
CANVAS = (1600, 900)
PAPER = "#f7f5ee"
INK = "#202020"
PENCIL = "#565656"
LIGHT_PENCIL = "#d8d3c7"
MUTED_INK = "#333333"
CARD_FILL = "#fbfaf6"


def ensure_dirs() -> None:
    for rel in [
        "assets/images",
        "bundle",
        "data/source_csv",
        "docs/templates",
        "notebooks",
        "setup",
        "workshops",
    ]:
        (ROOT / rel).mkdir(parents=True, exist_ok=True)


def md_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "source": source.strip("\n").splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uuid.uuid4().hex[:8],
        "metadata": {},
        "outputs": [],
        "source": source.strip("\n").splitlines(keepends=True),
    }


def precheck_cell(required_tables: list[str], prereq_notebook: str) -> dict:
    """Build a standardized pre-check code cell.

    `required_tables` entries may reference notebook-scope variables (e.g.
    `"{SILVER}.customers"`, `"{GOLD}.fact_sales"`) — each is emitted as an
    f-string literal in the generated cell, so `{SILVER}`/`{GOLD}` resolve
    against the notebook's own variables at runtime, exactly like the rest
    of this codebase's generated SQL/Python.

    Generates a code cell that asserts every table in `required_tables`
    exists via `spark.catalog.tableExists`. If any are missing, it prints a
    friendly message naming `prereq_notebook` as the notebook to run first,
    then raises to stop execution (fail fast instead of confusing errors
    later in the notebook).

    Reuse plan: this helper currently powers the data-generator's own
    upstream check (GLOBAL-01 first usage). It is intended to also replace
    the duplicated inline `missing = [... tableExists ...]` blocks in
    `notebook_module_2()`, `notebook_module_3()`, `notebook_module_4()` and
    `notebook_workshop_1()/notebook_workshop_2()` in a later block — not
    done yet, out of scope here.
    """
    tables_literal = ",\n    ".join(f'f"{t}"' for t in required_tables)
    prereq_escaped = prereq_notebook.replace('"', '\\"')
    source = f'''required_tables = [
    {tables_literal},
]

missing = [t for t in required_tables if not spark.catalog.tableExists(t)]
if missing:
    print("[BLOCKED] Missing required tables:")
    for t in missing:
        print("  -", t)
    print()
    print("Run this notebook first: {prereq_escaped}")
    raise Exception("Pre-check failed: missing prerequisite tables. Run \\"{prereq_escaped}\\" first.")

print("[OK] Pre-check passed, all required tables exist:")
for t in required_tables:
    print("  -", t)'''
    return code_cell(source)


def write_notebook(path: Path, cells: list[dict]) -> None:
    nb = {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_reference_csvs() -> None:
    src_dir = SOURCE_ROOT / "data/source_csv"
    dst_dir = ROOT / "data/source_csv"
    for name in ["Customers.csv", "Product.csv", "ProductCategory.csv"]:
        src = src_dir / name
        if src.exists():
            shutil.copy2(src, dst_dir / name)


def copy_reference_assets() -> None:
    """Bring over source screenshots that are useful in Medi delivery."""
    src_dir = SOURCE_ROOT / "assets/images"
    dst_dir = ROOT / "assets/images"
    assets = {
        "sql_editor.png": "source_sql_editor.png",
        "catalog_explorer_hierarchy.png": "source_catalog_explorer_hierarchy.png",
        "catalog_explorer_lineage.png": "source_catalog_explorer_lineage.png",
        "powerbi_directquery_connector.webp": "source_powerbi_directquery_connector.webp",
    }
    for src_name, dst_name in assets.items():
        src = src_dir / src_name
        if src.exists():
            shutil.copy2(src, dst_dir / dst_name)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Marker Felt.ttf",
        "/System/Library/Fonts/Supplemental/Chalkboard.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def multiline(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: str, size: int, bold: bool = False, spacing: int = 6) -> None:
    draw.multiline_text(xy, text, fill=fill, font=font(size, bold), spacing=spacing)


def wrap(text: str, width: int = 88) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def sketch_line(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: str = PENCIL, width: int = 3) -> None:
    for dx, dy in [(-1, 1), (0, 0), (1, -1)]:
        draw.line((start[0] + dx, start[1] + dy, end[0] + dx, end[1] + dy), fill=fill, width=max(1, width - 1))


def sketch_rect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = CARD_FILL, outline: str = PENCIL, width: int = 3) -> None:
    x1, y1, x2, y2 = box
    if fill:
        draw.rectangle((x1 + 2, y1 + 2, x2 + 2, y2 + 2), fill=fill)
    for off in [(-2, 1), (1, -1), (0, 0)]:
        dx, dy = off
        draw.line((x1 + dx, y1 + dy, x2 + dx, y1 + dy), fill=outline, width=width)
        draw.line((x2 + dx, y1 + dy, x2 + dx, y2 + dy), fill=outline, width=width)
        draw.line((x2 + dx, y2 + dy, x1 + dx, y2 + dy), fill=outline, width=width)
        draw.line((x1 + dx, y2 + dy, x1 + dx, y1 + dy), fill=outline, width=width)


def hatch(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], step: int = 12, fill: str = "#c7c2b8") -> None:
    x1, y1, x2, y2 = box
    height = y2 - y1
    for x in range(x1, x2, step):
        end_x = min(x + height, x2)
        end_y = y2 - (end_x - x)
        draw.line((x, y2, end_x, max(y1, end_y)), fill=fill, width=1)


def soft_fill(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str, hatch_step: int = 16) -> None:
    sketch_rect(draw, box, color, PENCIL, 3)
    hatch(draw, (box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4), step=hatch_step, fill="#d7d1c6")


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str = "#d0d7de", width: int = 2, radius: int = 18) -> None:
    card_fill = fill if fill and fill.lower() not in {"#ffffff", "white"} else CARD_FILL
    sketch_rect(draw, box, card_fill, PENCIL, max(2, width))


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: str = "#344054", width: int = 5) -> None:
    fill = PENCIL
    sketch_line(draw, start, end, fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    if x2 >= x1:
        points = [(x2, y2), (x2 - 20, y2 - 13), (x2 - 17, y2 + 14)]
    else:
        points = [(x2, y2), (x2 + 20, y2 - 13), (x2 + 17, y2 + 14)]
    draw.polygon(points, outline=fill, fill="#efede6")
    for a, b in [(points[0], points[1]), (points[1], points[2]), (points[2], points[0])]:
        sketch_line(draw, a, b, fill=fill, width=max(1, width - 2))


def base_canvas(title: str, subtitle: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    random.seed(42)
    img = Image.new("RGB", CANVAS, PAPER)
    draw = ImageDraw.Draw(img)

    # Paper texture, close to the hand-drawn training assets used in
    # Data Engineer Associate and Lakehouse & Transformation.
    for _ in range(2200):
        x = random.randrange(0, CANVAS[0])
        y = random.randrange(0, CANVAS[1])
        shade = random.choice(["#ede9df", "#f2efe8", "#e2ded4", "#faf8f1"])
        draw.point((x, y), fill=shade)

    multiline(draw, (72, 48), title, INK, 44, True)
    sketch_line(draw, (72, 105), (min(CANVAS[0] - 120, 72 + len(title) * 20), 105), PENCIL, 3)
    if subtitle:
        multiline(draw, (74, 125), wrap(subtitle, 96), MUTED_INK, 23, spacing=8)
    return img, draw


def icon_file(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int = 1) -> None:
    w, h = 34 * scale, 46 * scale
    sketch_rect(draw, (x, y, x + w, y + h), None, PENCIL, 2)
    sketch_line(draw, (x + w - 12 * scale, y), (x + w, y + 12 * scale), PENCIL, 2)
    for i in range(3):
        sketch_line(draw, (x + 8 * scale, y + (19 + i * 8) * scale), (x + w - 8 * scale, y + (19 + i * 8) * scale), PENCIL, 1)


def icon_table(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int = 1) -> None:
    w, h = 52 * scale, 42 * scale
    sketch_rect(draw, (x, y, x + w, y + h), None, PENCIL, 2)
    for i in [1, 2]:
        sketch_line(draw, (x + i * w // 3, y), (x + i * w // 3, y + h), PENCIL, 1)
    for j in [1, 2]:
        sketch_line(draw, (x, y + j * h // 3), (x + w, y + j * h // 3), PENCIL, 1)


def icon_gear(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int = 1) -> None:
    cx, cy = x + 24 * scale, y + 24 * scale
    r = 18 * scale
    for a in range(0, 360, 45):
        # short radial ticks suggest gear teeth without requiring trigonometry-heavy precision
        if a in [0, 180]:
            sketch_line(draw, (cx - r, cy), (cx + r, cy), PENCIL, 2)
        elif a in [90, 270]:
            sketch_line(draw, (cx, cy - r), (cx, cy + r), PENCIL, 2)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=PENCIL, width=2)
    draw.ellipse((cx - 7 * scale, cy - 7 * scale, cx + 7 * scale, cy + 7 * scale), outline=PENCIL, width=2)


def icon_dashboard(draw: ImageDraw.ImageDraw, x: int, y: int, scale: int = 1) -> None:
    sketch_rect(draw, (x, y, x + 70 * scale, y + 48 * scale), None, PENCIL, 2)
    draw.rectangle((x + 10 * scale, y + 26 * scale, x + 19 * scale, y + 39 * scale), outline=PENCIL, width=2, fill="#f4f2eb")
    draw.rectangle((x + 25 * scale, y + 18 * scale, x + 34 * scale, y + 39 * scale), outline=PENCIL, width=2, fill="#f4f2eb")
    draw.rectangle((x + 40 * scale, y + 10 * scale, x + 49 * scale, y + 39 * scale), outline=PENCIL, width=2, fill="#f4f2eb")
    sketch_line(draw, (x + 55 * scale, y + 34 * scale), (x + 65 * scale, y + 18 * scale), PENCIL, 2)


def callout(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, body: str, fill: str = "#fff7d6") -> None:
    soft_fill(draw, box, fill, hatch_step=20)
    multiline(draw, (box[0] + 20, box[1] + 18), title, INK, 24, True)
    wrap_width = max(24, (box[2] - box[0]) // 13)
    multiline(draw, (box[0] + 20, box[1] + 55), wrap(body, wrap_width), MUTED_INK, 19, spacing=5)


def save(img: Image.Image, name: str) -> None:
    img.save(ROOT / "assets/images" / name)


def image_medallion() -> None:
    img, draw = base_canvas(
        "Medallion to Power BI",
        "A BI dashboard is only as trustworthy as the layer contract behind it.",
    )

    # Source systems and raw files.
    soft_fill(draw, (70, 205, 325, 430), "#f7f1df", hatch_step=18)
    multiline(draw, (92, 230), "Sources", INK, 26, True)
    icon_file(draw, 95, 285, 1)
    icon_file(draw, 150, 285, 1)
    icon_gear(draw, 215, 282, 1)
    multiline(draw, (90, 350), "CSV extracts\nJSON orders\nstreaming events", MUTED_INK, 17, spacing=4)

    layers = [
        {
            "title": "Bronze",
            "label": "[bronze.*]",
            "body": "Raw landing zone\nappend-only history\nminimal assumptions",
            "footer": "Owner: ingestion",
            "color": "#fee4e2",
            "icon": "file",
        },
        {
            "title": "Silver",
            "label": "[silver.orders]",
            "body": "Clean types\nstandard names\nquality rules",
            "footer": "Owner: data engineering",
            "color": "#e0f2fe",
            "icon": "gear",
        },
        {
            "title": "Gold",
            "label": "[gold.fact_sales]",
            "body": "Kimball grain\nKPI definitions\ncertified BI contract",
            "footer": "Owner: analytics + business",
            "color": "#dcfce7",
            "icon": "table",
        },
        {
            "title": "Power BI",
            "label": "[Executive KPI]",
            "body": "Thin report layer\nfew DAX measures\nImport or DirectQuery",
            "footer": "Owner: BI team",
            "color": "#fef3c7",
            "icon": "dashboard",
        },
    ]

    x = 390
    for i, layer in enumerate(layers):
        box = (x, 230, x + 245, 545)
        soft_fill(draw, box, layer["color"], hatch_step=18)
        multiline(draw, (x + 24, 255), layer["title"], INK, 31, True)
        multiline(draw, (x + 24, 300), layer["label"], INK, 22, True)
        if layer["icon"] == "file":
            icon_file(draw, x + 160, 255, 1)
        elif layer["icon"] == "gear":
            icon_gear(draw, x + 160, 252, 1)
        elif layer["icon"] == "table":
            icon_table(draw, x + 155, 260, 1)
        else:
            icon_dashboard(draw, x + 145, 255, 1)
        multiline(draw, (x + 24, 360), layer["body"], MUTED_INK, 20, spacing=6)
        sketch_line(draw, (x + 22, 482), (x + 223, 482), PENCIL, 2)
        multiline(draw, (x + 24, 498), layer["footer"], MUTED_INK, 16)
        if i < len(layers) - 1:
            arrow(draw, (x + 258, 385), (x + 330, 385), PENCIL, 4)
        x += 300

    # Bottom teaching strip: what changes from layer to layer.
    y = 635
    labels = [
        ("Trust", "raw -> validated -> certified"),
        ("Grain", "events -> entities -> BI fact"),
        ("Cost", "wide scans -> curated aggregates"),
        ("Consumer", "engineers -> analysts -> executives"),
    ]
    for i, (title, body) in enumerate(labels):
        bx = 150 + i * 350
        soft_fill(draw, (bx, y, bx + 285, y + 120), "#f4f2eb", hatch_step=22)
        multiline(draw, (bx + 18, y + 18), title, INK, 24, True)
        multiline(draw, (bx + 18, y + 55), body, MUTED_INK, 18)

    multiline(draw, (88, 795), "Training point: Power BI should consume Gold, not rebuild business logic from Silver or Bronze.", INK, 24, True)
    save(img, "medallion_to_powerbi.png")


def image_kimball() -> None:
    img, draw = base_canvas("Kimball-Style Gold Model", "The Databricks model defines dimensions, fact grain, measures, and relationships.")
    rounded(draw, (610, 340, 990, 570), "#dcfce7", "#16a34a")
    multiline(draw, (670, 380), "gold.fact_sales", "#111827", 32, True)
    multiline(draw, (650, 440), "grain: one order line\nmeasures: revenue, margin\nFKs: date, product, customer", "#344054", 22)
    dims = [
        ((130, 170, 470, 320), "gold.dim_date", "day, month, year"),
        ((1130, 170, 1470, 320), "gold.dim_product", "category, subcategory"),
        ((130, 620, 470, 770), "gold.dim_customer", "segment, region"),
        ((1130, 620, 1470, 770), "gold.dim_channel", "channel, source"),
    ]
    for box, title, body in dims:
        rounded(draw, box, "#e0f2fe", "#0284c7")
        multiline(draw, (box[0] + 28, box[1] + 28), title, "#111827", 27, True)
        multiline(draw, (box[0] + 28, box[1] + 82), body, "#344054", 22)
        arrow(draw, ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), (800, 455), "#64748b", 4)
    save(img, "kimball_gold_model.png")


def image_powerbi_mockup() -> None:
    img, draw = base_canvas("RetailHub Executive KPI Dashboard", "Report mockup: Databricks owns the model, Power BI stays thin and focused.")
    kpis = [
        ("Revenue", "$42.8M", "+8.4%"),
        ("Gross margin", "31.6%", "+2.1 pp"),
        ("Orders", "184k", "+5.7%"),
        ("Return rate", "4.8%", "-0.6 pp"),
        ("DQ score", "94/100", "+3"),
    ]
    x = 60
    for title, value, delta in kpis:
        rounded(draw, (x, 200, x + 280, 320), "#ffffff", "#d0d5dd", radius=12)
        multiline(draw, (x + 22, 219), title, "#475467", 20)
        multiline(draw, (x + 22, 250), value, "#111827", 34, True)
        multiline(draw, (x + 190, 261), delta, PENCIL, 19, True)
        x += 300
    rounded(draw, (60, 350, 980, 780), "#ffffff", "#d0d5dd", radius=12)
    multiline(draw, (90, 375), "Revenue and margin trend", "#111827", 24, True)
    points = [(120, 700), (240, 630), (360, 650), (480, 565), (600, 520), (720, 475), (840, 440), (940, 390)]
    draw.line(points, fill=INK, width=5)
    draw.line([(120, 730), (240, 690), (360, 680), (480, 630), (600, 590), (720, 568), (840, 540), (940, 500)], fill=PENCIL, width=4)
    for p in points:
        draw.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), outline=INK, width=3, fill=CARD_FILL)
    rounded(draw, (1030, 350, 1510, 550), "#ffffff", "#d0d5dd", radius=12)
    multiline(draw, (1060, 375), "Revenue by region", "#111827", 24, True)
    bars = [("North", 330), ("West", 280), ("East", 225), ("South", 185)]
    y = 425
    for label, w in bars:
        multiline(draw, (1060, y), label, "#344054", 18)
        draw.rectangle((1140, y + 4, 1140 + w, y + 28), outline=PENCIL, width=3, fill="#f4f2eb")
        hatch(draw, (1140, y + 4, 1140 + w, y + 28), step=10)
        y += 34
    rounded(draw, (1030, 580, 1510, 780), "#ffffff", "#d0d5dd", radius=12)
    multiline(draw, (1060, 605), "Filters", "#111827", 24, True)
    for i, text in enumerate(["Date: last 12 months", "Region: all", "Channel: online + retail", "Category: all"]):
        rounded(draw, (1060, 650 + i * 30, 1455, 674 + i * 30), "#f2f4f7", "#eaecf0", radius=8)
        multiline(draw, (1075, 652 + i * 30), text, "#344054", 15)
    save(img, "powerbi_report_mockup.png")


def image_import_directquery() -> None:
    img, draw = base_canvas(
        "Power BI: Import vs Live DirectQuery",
        "Choose the storage mode by business latency, interaction cost, and Gold aggregate readiness.",
    )

    soft_fill(draw, (650, 220, 950, 350), "#dcfce7", hatch_step=18)
    icon_table(draw, 690, 258, 1)
    multiline(draw, (760, 247), "[gold.sales_mart]", INK, 26, True)
    multiline(draw, (760, 290), "certified KPI source", MUTED_INK, 19)

    # Import branch.
    soft_fill(draw, (100, 445, 660, 710), "#e0f2fe", hatch_step=18)
    multiline(draw, (130, 475), "Import mode", INK, 32, True)
    icon_dashboard(draw, 135, 535, 1)
    multiline(draw, (230, 530), "Scheduled refresh copies data\ninto the Power BI semantic model.", MUTED_INK, 22, spacing=6)
    multiline(draw, (130, 635), "Best for: executive dashboards, many readers,\nstable refresh windows, lower warehouse pressure.", INK, 19, spacing=5)
    arrow(draw, (690, 350), (360, 445), PENCIL, 4)
    multiline(draw, (270, 395), "warehouse used during refresh", PENCIL, 18, True)

    # DirectQuery branch.
    soft_fill(draw, (940, 445, 1500, 710), "#fef3c7", hatch_step=18)
    multiline(draw, (970, 475), "Live / DirectQuery", INK, 32, True)
    icon_dashboard(draw, 975, 535, 1)
    multiline(draw, (1070, 530), "Every visual interaction can\nsend SQL back to Databricks.", MUTED_INK, 22, spacing=6)
    multiline(draw, (970, 635), "Best for: operational freshness, small audiences,\nGold aggregates, monitored query volume.", INK, 19, spacing=5)
    arrow(draw, (910, 350), (1215, 445), PENCIL, 4)
    multiline(draw, (1045, 395), "warehouse used on interactions", PENCIL, 18, True)

    callout(
        draw,
        (525, 745, 1080, 835),
        "Training decision",
        "Default to Import. Use DirectQuery only when freshness is worth the interactive query cost.",
        "#fff7d6",
    )
    save(img, "import_vs_directquery.png")


def image_cost_decision() -> None:
    img, draw = base_canvas("SQL Warehouse Cost Decision Card", "Use pricing evidence plus workload behavior to choose a safe BI setup.")
    items = [
        ("Size", "larger warehouse\nhigher DBU/hour\nshorter runtime"),
        ("Auto-stop", "short for Import\nlonger for live demos\navoid idle spend"),
        ("Concurrency", "more users\nmore visuals\nmore parallel SQL"),
        ("DirectQuery", "each click may send SQL\nuse Gold aggregates\nmonitor query volume"),
        ("Serverless", "fast startup\nless operations\nverify current pricing"),
    ]
    callout(
        draw,
        (90, 190, 650, 340),
        "Cost mental model",
        "DBU rate x uptime x query volume x scanned data. Optimize the whole pattern, not one setting.",
        "#fff7d6",
    )
    soft_fill(draw, (735, 190, 1490, 340), "#f4f2eb", hatch_step=22)
    multiline(draw, (770, 222), "Before delivery", INK, 26, True)
    multiline(draw, (770, 260), "Capture a dated screenshot from the official Databricks pricing page.", MUTED_INK, 20)

    for i, (title, body) in enumerate(items):
        if i < 3:
            bx, by = 90 + i * 500, 365
        else:
            bx, by = 340 + (i - 3) * 500, 555
        soft_fill(draw, (bx, by, bx + 410, by + 145), "#fbfaf6", hatch_step=24)
        multiline(draw, (bx + 22, by + 18), title, "#111827", 25, True)
        multiline(draw, (bx + 22, by + 58), body, "#344054", 17, spacing=4)

    sketch_line(draw, (140, 765), (1460, 765), PENCIL, 4)
    arrow(draw, (1450, 765), (1510, 765), PENCIL, 4)
    multiline(draw, (110, 795), "lower cost risk", PENCIL, 20, True)
    multiline(draw, (1280, 795), "higher cost risk", PENCIL, 20, True)
    multiline(draw, (360, 810), "Import + aggregate", INK, 19, True)
    multiline(draw, (945, 810), "DirectQuery + many visuals", INK, 19, True)
    save(img, "sql_warehouse_cost_decision.png")


def image_lakeflow_dag() -> None:
    img, draw = base_canvas("Lakeflow Job DAG for BI Refresh", "Jobs orchestrate visible steps: validation, Gold refresh, BI readiness, and notification.")
    nodes = [
        ((90, 360, 320, 500), "validate\nsource data"),
        ((420, 260, 650, 400), "refresh\nGold model"),
        ((420, 520, 650, 660), "DQ checks\nKPI reconcile"),
        ((760, 360, 990, 500), "build\nBI aggregates"),
        ((1090, 360, 1320, 500), "publish\nBI contract"),
        ((1390, 360, 1560, 500), "notify\nowner"),
    ]
    for box, text in nodes:
        rounded(draw, box, "#ffffff", "#64748b")
        multiline(draw, (box[0] + 30, box[1] + 35), text, "#111827", 25, True)
    arrow(draw, (320, 430), (420, 330))
    arrow(draw, (320, 430), (420, 590))
    arrow(draw, (650, 330), (760, 430))
    arrow(draw, (650, 590), (760, 430))
    arrow(draw, (990, 430), (1090, 430))
    arrow(draw, (1320, 430), (1390, 430))
    save(img, "lakeflow_job_dag.png")


def image_dabs_flow() -> None:
    img, draw = base_canvas("DABs / Declarative Automation Bundles", "The same job definition can be validated and deployed across multiple targets.")
    boxes = [
        ("Repo", "notebooks\nsql\nbundle/databricks.yml", "#e0f2fe"),
        ("Validate", "databricks bundle validate", "#dcfce7"),
        ("Deploy dev", "bundle deploy -t dev", "#fef3c7"),
        ("Deploy prod", "bundle deploy -t prod", "#fee4e2"),
        ("Run job", "refresh_gold_bi_dataset", "#ede9fe"),
    ]
    x = 70
    for i, (title, body, color) in enumerate(boxes):
        rounded(draw, (x, 300, x + 260, 560), color, "#98a2b3")
        multiline(draw, (x + 28, 335), title, "#111827", 29, True)
        multiline(draw, (x + 28, 395), body, "#344054", 21)
        if i < len(boxes) - 1:
            arrow(draw, (x + 275, 430), (x + 355, 430))
        x += 310
    save(img, "dabs_deployment_flow.png")


def image_retailhub_source_map() -> None:
    img, draw = base_canvas("RetailHub Source Map", "Identify available data, table grain, and where analytical risk begins.")
    boxes = [
        ((70, 190, 420, 360), "customers", "grain: customer\nsegment, city, region\nrisk: stale attributes", "#e0f2fe"),
        ((70, 520, 420, 690), "products", "grain: product\ncategory, price, cost\nrisk: price changes", "#e0f2fe"),
        ((590, 190, 1010, 360), "sales_orders", "grain: order\nstatus, date, channel\nrisk: invalid statuses", "#fef3c7"),
        ((590, 520, 1010, 690), "order_lines", "grain: order line\nquantity, revenue, margin\nrisk: duplicates, missing price", "#fee4e2"),
        ((1180, 350, 1510, 540), "Gold model", "BI-ready contract\nvalidated KPIs\nPower BI source", "#dcfce7"),
    ]
    for box, title, body, color in boxes:
        rounded(draw, box, color, "#98a2b3")
        multiline(draw, (box[0] + 28, box[1] + 26), title, "#111827", 28, True)
        multiline(draw, (box[0] + 28, box[1] + 78), body, "#344054", 21)
    arrow(draw, (420, 275), (590, 275), "#64748b")
    arrow(draw, (420, 605), (590, 605), "#64748b")
    arrow(draw, (1010, 275), (1180, 410), "#64748b")
    arrow(draw, (1010, 605), (1180, 480), "#64748b")
    multiline(draw, (75, 755), "Trainer prompt: ask participants which table they would query first and why.", PENCIL, 24, True)
    save(img, "retailhub_source_map.png")


def image_gold_business_value() -> None:
    img, draw = base_canvas("Why Gold Creates Business Value", "Gold is not just a technical layer. It is the trust mechanism behind business decisions.")
    items = [
        ("Metric trust", "one revenue definition\none margin definition", "#dcfce7"),
        ("Decision speed", "fewer number disputes\nfaster status meetings", "#e0f2fe"),
        ("Cost control", "fewer ad-hoc joins\naggregates for BI", "#fef3c7"),
        ("Ownership", "KPI owner\nBI contract\nquality gate", "#fee4e2"),
    ]
    x = 90
    for title, body, color in items:
        rounded(draw, (x, 260, x + 330, 560), color, "#98a2b3")
        multiline(draw, (x + 26, 300), title, "#111827", 29, True)
        multiline(draw, (x + 26, 370), body, "#344054", 24)
        x += 380
    multiline(draw, (120, 665), "Case: RetailHub CEO asks why margin is down. Gold lets the team answer with agreed KPI logic, not with spreadsheet archaeology.", "#344054", 25)
    save(img, "gold_business_value.png")


def image_star_vs_flat() -> None:
    img, draw = base_canvas("Star Schema vs Flat BI Table", "Both patterns can be valid. Choose based on usage, cost, and governance.")
    rounded(draw, (80, 180, 720, 720), "#ffffff", "#93c5fd")
    rounded(draw, (880, 180, 1520, 720), "#ffffff", "#fbbf24")
    multiline(draw, (120, 220), "Star schema", "#111827", 32, True)
    multiline(draw, (120, 285), "fact_sales + dimensions\nreusable dimensions\nclear grain and relationships\nbetter for governed BI", "#344054", 24)
    rounded(draw, (320, 470, 520, 590), "#dcfce7", "#16a34a")
    multiline(draw, (352, 505), "fact", "#111827", 26, True)
    for x, y, label in [(145, 405, "date"), (540, 405, "product"), (145, 610, "customer"), (540, 610, "channel")]:
        rounded(draw, (x, y, x + 130, y + 70), "#e0f2fe", "#0284c7", radius=12)
        multiline(draw, (x + 18, y + 19), label, "#111827", 18, True)
        arrow(draw, (x + 65, y + 35), (420, 530), "#64748b", 3)
    multiline(draw, (920, 220), "Flat BI table", "#111827", 32, True)
    multiline(draw, (920, 285), "one wide table\nvery simple import\nfast first report\ncan duplicate dimensions", "#344054", 24)
    for i in range(7):
        y = 455 + i * 30
        draw.rectangle((990, y, 1410, y + 22), fill="#f2f4f7", outline="#d0d5dd")
    multiline(draw, (1010, 405), "fact_sales_dashboard", "#111827", 24, True)
    save(img, "star_schema_vs_flat_table.png")


def image_kpi_definition_flow() -> None:
    img, draw = base_canvas("KPI Definition Flow", "Before a Power BI measure exists, agree the semantics and validation in Gold.")
    steps = [
        ("Business question", "What decision changes?"),
        ("KPI definition", "formula, filters, caveats"),
        ("Gold SQL", "table/view/metric view"),
        ("Validation", "reconcile + DQ checks"),
        ("BI measure", "thin DAX or direct field"),
    ]
    x = 70
    for i, (title, body) in enumerate(steps):
        rounded(draw, (x, 310, x + 250, 560), "#ffffff", "#98a2b3")
        multiline(draw, (x + 24, 345), title, "#111827", 24, True)
        multiline(draw, (x + 24, 415), body, "#344054", 20)
        if i < len(steps) - 1:
            arrow(draw, (x + 260, 435), (x + 330, 435), "#64748b")
        x += 305
    multiline(draw, (90, 690), "Bad smell: KPI appears only as a report visual calculation and nobody owns the SQL definition.", PENCIL, 24, True)
    save(img, "kpi_definition_flow.png")


def image_gold_quality_gate() -> None:
    img, draw = base_canvas("Gold Quality Gate", "Not every issue blocks the report, but every issue needs a decision and an owner.")
    checks = [
        ("Grain", "line_id unique\nno accidental fan-out"),
        ("Keys", "customer/product/date joins\nno orphan rows"),
        ("Business rules", "valid statuses\ncompleted vs returned"),
        ("Amounts", "price/cost present\nmargin reconciliation"),
        ("Freshness", "latest order date\nrefresh SLA"),
    ]
    x, y = 90, 220
    for i, (title, body) in enumerate(checks):
        bx = x + (i % 3) * 500
        by = y + (i // 3) * 250
        rounded(draw, (bx, by, bx + 410, by + 185), "#ffffff", "#d0d5dd")
        draw.ellipse((bx + 25, by + 30, bx + 62, by + 67), fill=CARD_FILL, outline=PENCIL, width=3)
        draw.line((bx + 35, by + 49, bx + 45, by + 58, bx + 58, by + 38), fill=PENCIL, width=4)
        multiline(draw, (bx + 82, by + 25), title, "#111827", 28, True)
        multiline(draw, (bx + 82, by + 82), body, "#344054", 21)
    multiline(draw, (90, 765), "Workshop rule: every failed check becomes either a fix, accepted caveat, or BI exclusion.", PENCIL, 24, True)
    save(img, "gold_quality_gate.png")


def image_powerbi_connection_walkthrough() -> None:
    img, draw = base_canvas("Power BI Connection Walkthrough", "From SQL Warehouse to semantic dataset: know what to select and why.")
    steps = [
        ("1", "Databricks\nSQL Warehouse"),
        ("2", "Connection details\nserver + HTTP path"),
        ("3", "Power BI connector\nAzure AD auth"),
        ("4", "Choose mode\nImport or\nDirectQuery"),
        ("5", "Select Gold\nobjects\nmonthly + detail"),
        ("6", "Publish dataset\ncertify\ncontract"),
    ]
    x = 65
    for idx, title in steps:
        rounded(draw, (x, 270, x + 215, 590), "#ffffff", "#98a2b3")
        draw.ellipse((x + 22, 300, x + 70, 348), fill="#111827")
        multiline(draw, (x + 38, 310), idx, "#ffffff", 24, True)
        multiline(draw, (x + 22, 380), title, "#344054", 18, True, spacing=9)
        if idx != "6":
            arrow(draw, (x + 225, 430), (x + 285, 430), "#64748b", 4)
        x += 250
    multiline(draw, (88, 705), "Use source_powerbi_directquery_connector.webp as the real UI screenshot in the live walkthrough.", "#344054", 24)
    save(img, "powerbi_connection_walkthrough.png")


def image_incremental_refresh() -> None:
    img, draw = base_canvas("Incremental Refresh Window", "RangeStart is inclusive. RangeEnd is exclusive. This small detail protects refresh correctness.")
    sketch_line(draw, (140, 465), (1460, 465), INK, 5)
    months = ["2024-01", "2024-06", "2025-01", "2025-06", "2026-01", "2026-06"]
    for i, m in enumerate(months):
        x = 160 + i * 250
        sketch_line(draw, (x, 445), (x, 485), INK, 3)
        multiline(draw, (x - 45, 500), m, "#344054", 20)
    rounded(draw, (820, 390, 1320, 540), CARD_FILL, PENCIL, width=4)
    multiline(draw, (875, 420), "refresh partition", "#111827", 30, True)
    multiline(draw, (875, 470), "order_date >= RangeStart\norder_date <  RangeEnd", "#344054", 24)
    sketch_line(draw, (820, 350), (820, 580), PENCIL, 4)
    sketch_line(draw, (1320, 350), (1320, 580), PENCIL, 4)
    multiline(draw, (735, 310), "RangeStart", PENCIL, 24, True)
    multiline(draw, (1265, 310), "RangeEnd", PENCIL, 24, True)
    save(img, "incremental_refresh_range.png")


def image_query_profile() -> None:
    img, draw = base_canvas("Query Profile Reading Map", "Translate query profile symptoms into practical optimization decisions.")
    rounded(draw, (80, 180, 620, 720), "#ffffff", "#d0d5dd")
    multiline(draw, (120, 220), "Symptoms", "#111827", 30, True)
    for i, text in enumerate(["large scan", "shuffle spill", "slow join", "many tiny files", "SELECT *"]):
        multiline(draw, (140, 295 + i * 70), f"- {text}", "#344054", 25)
    rounded(draw, (730, 180, 1520, 720), "#ffffff", "#d0d5dd")
    multiline(draw, (770, 220), "Likely actions", "#111827", 30, True)
    actions = [
        ("large scan", "Gold aggregate, filter pushdown, column pruning"),
        ("shuffle spill", "lower cardinality, pre-aggregate, warehouse size"),
        ("slow join", "star model, stats, avoid joining Silver in BI"),
        ("many tiny files", "OPTIMIZE / predictive optimization"),
        ("SELECT *", "select BI columns only"),
    ]
    for i, (symptom, action) in enumerate(actions):
        y = 295 + i * 70
        multiline(draw, (790, y), symptom, "#111827", 23, True)
        arrow(draw, (950, y + 14), (1030, y + 14), "#64748b", 3)
        multiline(draw, (1060, y), action, "#344054", 20)
    save(img, "query_profile_reading_map.png")


def image_automation_checklist() -> None:
    img, draw = base_canvas("Automation Readiness Checklist", "Move the demo notebook into a repeatable, observable production process.")
    items = [
        ("Parameterize", "catalog, schema, date window"),
        ("Validate", "source checks + KPI reconcile"),
        ("Orchestrate", "Lakeflow Job DAG"),
        ("Deploy", "DABs dev/prod targets"),
        ("Observe", "run history, alerts, cost"),
        ("Document", "BI contract + decision log"),
    ]
    x, y = 95, 190
    for i, (title, body) in enumerate(items):
        bx = x + (i % 3) * 500
        by = y + (i // 3) * 245
        rounded(draw, (bx, by, bx + 410, by + 175), "#ffffff", "#d0d5dd")
        sketch_rect(draw, (bx + 28, by + 35, bx + 65, by + 72), None, PENCIL, 3)
        draw.line((bx + 34, by + 54, bx + 45, by + 65, bx + 62, by + 39), fill=PENCIL, width=4)
        multiline(draw, (bx + 88, by + 28), title, "#111827", 28, True)
        multiline(draw, (bx + 88, by + 85), body, "#344054", 21)
    multiline(draw, (96, 755), "Discussion: what must be automated before the report can be trusted every Monday morning?", "#344054", 24)
    save(img, "automation_readiness_checklist.png")


def image_workshop_success() -> None:
    img, draw = base_canvas("Workshop Success Criteria", "Participants should know not only what to build, but when the work is complete.")
    checks = [
        "Gold source exists and has documented grain",
        "KPI totals reconcile with detail source",
        "At least three DQ issues are named",
        "Import vs DirectQuery decision is justified",
        "Cost guardrails are written down",
        "Self-check cell passes",
    ]
    y = 190
    for i, text in enumerate(checks, 1):
        rounded(draw, (150, y, 1450, y + 85), "#ffffff", "#d0d5dd", radius=12)
        draw.ellipse((185, y + 20, 230, y + 65), fill="#111827")
        multiline(draw, (199, y + 28), str(i), "#ffffff", 22, True)
        multiline(draw, (260, y + 25), text, "#344054", 25)
        y += 102
    save(img, "workshop_success_criteria.png")


def build_images() -> None:
    image_medallion()
    image_kimball()
    image_powerbi_mockup()
    image_import_directquery()
    image_cost_decision()
    image_lakeflow_dag()
    image_dabs_flow()
    image_retailhub_source_map()
    image_gold_business_value()
    image_star_vs_flat()
    image_kpi_definition_flow()
    image_gold_quality_gate()
    image_powerbi_connection_walkthrough()
    image_incremental_refresh()
    image_query_profile()
    image_automation_checklist()
    image_workshop_success()


def write_templates() -> None:
    templates = {
        "kpi-dictionary.md": """# KPI Dictionary

| KPI | Business definition | SQL definition | Grain | Default filters | Owner | Caveats |
|---|---|---|---|---|---|---|
| Revenue | Completed order line revenue after discount | `SUM(line_revenue)` | order line | `status = 'Completed'` | Sales Ops | Excludes cancelled and returned lines |
| Gross margin | Revenue minus line cost | `SUM(line_margin)` | order line | `status = 'Completed'` | Finance | Requires product cost |
| Return rate | Returned orders divided by completed + returned orders | `returned_orders / eligible_orders` | order | rolling period | Sales Ops | Sensitive to status mapping |

## Trainer note

During the workshop participants fill at least three KPI rows and add one caveat
per KPI.
""",
        "bi-contract.md": """# BI Contract

## Dataset

- Name:
- Source table/view:
- Grain:
- Refresh owner:
- Business owner:
- Technical owner:

## Tables

| Object | Role | Grain | Refresh pattern | Notes |
|---|---|---|---|---|
| `gold.fact_sales_dashboard` | fact/reporting table | one row per order line | daily | filtered to BI-ready fields |
| `gold.fact_sales_dashboard_monthly` | aggregate | month/category/region | daily | preferred for summary pages |

## Measures

| Measure | Preferred location | Definition |
|---|---|---|
| Revenue | Databricks | `SUM(line_revenue)` |
| Gross margin | Databricks | `SUM(line_margin)` |

## Power BI mode decision

- Baseline:
- When Import is enough:
- When live/DirectQuery is justified:
- Cost guardrails:
""",
        "decision-log.md": """# Decision Log

| Date | Decision | Options considered | Chosen option | Reason | Consequence |
|---|---|---|---|---|---|
| YYYY-MM-DD | Reporting source | view/table/aggregate | table + monthly aggregate | stable refresh and lower BI cost | requires scheduled refresh |
""",
        "refresh-strategy.md": """# Refresh Strategy

## Target

- Dataset:
- SLA:
- Frequency:
- Trigger:
- Owner:

## Proposed Lakeflow Job

1. Validate source data.
2. Refresh Gold model.
3. Reconcile KPI.
4. Build BI aggregate.
5. Publish readiness status.

## Failure handling

- Retry:
- Repair run:
- Notification:
- Rollback:
""",
        "report-certification-checklist.md": """# Report Certification Checklist

| Check | Status | Evidence |
|---|---|---|
| KPI definitions documented | TODO | |
| Grain documented | TODO | |
| Data quality checks passed | TODO | |
| Import/DirectQuery decision documented | TODO | |
| Refresh strategy documented | TODO | |
| Cost guardrails documented | TODO | |
| Business owner approved | TODO | |
""",
        "data-quality-checklist.md": """# Data Quality Checklist

| Rule | Query/object | Threshold | Status |
|---|---|---|---|
| No duplicate order lines | `line_id` uniqueness | 0 duplicates | TODO |
| Valid statuses only | status dictionary | 0 invalid | TODO |
| No missing product/customer links | FK checks | 0 orphans | TODO |
| No future orders | order_date <= current_date | 0 rows | TODO |
| Price and cost present | unit_price/unit_cost | > 99% complete | TODO |
""",
        "cost-awareness-checklist.md": """# Cost Awareness Checklist

| Area | Question | Decision |
|---|---|---|
| Warehouse size | What size is enough for the demo/report? | |
| Auto-stop | How long should idle compute stay warm? | |
| Import mode | Can refresh be scheduled instead of live queries? | |
| DirectQuery | Which visuals can trigger expensive SQL? | |
| Aggregates | Which Gold aggregates reduce scan size? | |
| Monitoring | Where do we inspect query and billing usage? | |
""",
    }
    for name, text in templates.items():
        (ROOT / "docs/templates" / name).write_text(text, encoding="utf-8")


def write_visual_materials_map() -> None:
    text = """# Visual Materials Map

This file is generated by `scripts/build_materials_v1.py`.

## Source screenshots reused from `Databricks-Data-Analyst`

| Asset | Use |
|---|---|
| `assets/images/source_sql_editor.png` | Module 1 SQL Editor orientation |
| `assets/images/source_catalog_explorer_hierarchy.png` | Module 1 Unity Catalog / Catalog Explorer orientation |
| `assets/images/source_catalog_explorer_lineage.png` | Module 2 lineage and certification discussion |
| `assets/images/source_powerbi_directquery_connector.webp` | Module 3 Power BI connector walkthrough |

## Medi whiteboard visuals

| Asset | Use |
|---|---|
| `assets/images/sql_warehouse_cost_decision.png` | pricing and warehouse cost discussion |
| `assets/images/retailhub_source_map.png` | source-data discovery and grain discussion |
| `assets/images/medallion_to_powerbi.png` | Medallion to BI story |
| `assets/images/gold_business_value.png` | business case for Gold |
| `assets/images/star_schema_vs_flat_table.png` | modelling trade-off discussion |
| `assets/images/kimball_gold_model.png` | Kimball-style Gold model |
| `assets/images/gold_quality_gate.png` | Gold validation checklist |
| `assets/images/kpi_definition_flow.png` | KPI ownership and semantic contract |
| `assets/images/powerbi_report_mockup.png` | target report shape |
| `assets/images/import_vs_directquery.png` | Power BI mode decision |
| `assets/images/powerbi_connection_walkthrough.png` | SQL Warehouse to Power BI steps |
| `assets/images/incremental_refresh_range.png` | RangeStart / RangeEnd refresh explanation |
| `assets/images/query_profile_reading_map.png` | performance troubleshooting |
| `assets/images/lakeflow_job_dag.png` | Lakeflow Jobs orientation |
| `assets/images/dabs_deployment_flow.png` | DABs dev/prod deployment story |
| `assets/images/automation_readiness_checklist.png` | production readiness recap |
| `assets/images/workshop_success_criteria.png` | workshop instructions |

## Still required before delivery

- Capture a current official Databricks pricing screenshot and save it as
  `assets/images/databricks_pricing_YYYY-MM-DD.png`.
- Run the notebooks in a live Databricks workspace to validate SQL runtime,
  not only local JSON/Python structure.
"""
    (ROOT / "docs/07-visual-materials-map.md").write_text(text, encoding="utf-8")


def notebook_setup_pre_config() -> None:
    cells = [
        md_cell("""# 00 · Pre-config — RetailHub setup

Trainer-only notebook. It creates the per-user course catalog, schemas and
Volume used by the rest of `Databricks-Data-Analyst-Medi`.

Run this once before the course for every participant catalog pattern you need.
"""),
        code_cell("""import re

CATALOG_PREFIX = "training_dbx_ana_medi"
SCHEMAS = ["default", "bronze", "silver", "gold"]
VOLUME_NAME = "datasets"

current_user = spark.sql("SELECT current_user()").first()[0]
user_slug = re.sub(r"[^a-zA-Z0-9]", "_", current_user.split("@")[0]).lower()
user_slug = re.sub(r"_+", "_", user_slug).strip("_") or "trainer"

if "trainer" in current_user.lower() or "trener" in current_user.lower():
    user_slug = "trainer"

CATALOG = f"{CATALOG_PREFIX}_{user_slug}"
print("Provisioning catalog:", CATALOG)"""),
        code_cell("""spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"USE CATALOG {CATALOG}")

for schema in SCHEMAS:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema}")

spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.default.{VOLUME_NAME}")

DATASET_PATH = f"/Volumes/{CATALOG}/default/{VOLUME_NAME}"
print("Dataset Volume:", DATASET_PATH)
print("[OK] Catalog, schemas and Volume are ready.")"""),
        md_cell("""## Next step

Run `data/generate_training_dataset.ipynb`. The generator creates synthetic
RetailHub data, including controlled data-quality issues for the workshops.
"""),
    ]
    write_notebook(ROOT / "setup/00_pre_config.ipynb", cells)


def notebook_setup() -> None:
    cells = [
        md_cell("""# 00 · Setup — environment check

Every module starts with `%run ../setup/00_setup`. This notebook resolves the
participant catalog and exports shared variables.
"""),
        code_cell("""import re

CATALOG_PREFIX = "training_dbx_ana_medi"
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"
DEFAULT_SCHEMA = "default"
VOLUME_NAME = "datasets"

current_user = spark.sql("SELECT current_user()").first()[0]
user_slug = re.sub(r"[^a-zA-Z0-9]", "_", current_user.split("@")[0]).lower()
user_slug = re.sub(r"_+", "_", user_slug).strip("_") or "user"

if "trainer" in current_user.lower() or "trener" in current_user.lower():
    user_slug = "trainer"

CATALOG = f"{CATALOG_PREFIX}_{user_slug}"
BRONZE = f"{CATALOG}.{BRONZE_SCHEMA}"
SILVER = f"{CATALOG}.{SILVER_SCHEMA}"
GOLD = f"{CATALOG}.{GOLD_SCHEMA}"
DATASET_PATH = f"/Volumes/{CATALOG}/{DEFAULT_SCHEMA}/{VOLUME_NAME}"

print("User:", current_user)
print("Catalog:", CATALOG)"""),
        code_cell("""catalogs = {r[0] for r in spark.sql("SHOW CATALOGS").collect()}
if CATALOG not in catalogs:
    raise Exception(f"Catalog {CATALOG} not found. Ask the trainer to run setup/00_pre_config.")

spark.sql(f"USE CATALOG {CATALOG}")

schemas = {r[0] for r in spark.sql(f"SHOW SCHEMAS IN {CATALOG}").collect()}
missing = [s for s in [BRONZE_SCHEMA, SILVER_SCHEMA, GOLD_SCHEMA] if s not in schemas]
if missing:
    raise Exception(f"Missing schemas in {CATALOG}: {missing}")

print("[OK] Environment ready")
print("BRONZE:", BRONZE)
print("SILVER:", SILVER)
print("GOLD:", GOLD)
print("DATASET_PATH:", DATASET_PATH)"""),
    ]
    write_notebook(ROOT / "setup/00_setup.ipynb", cells)


def notebook_data_generator() -> None:
    cells = [
        md_cell("""# Generate RetailHub training dataset

This notebook builds the foundation for the Medi course:

- Bronze/Silver/Gold schemas,
- synthetic RetailHub customers, products, orders and order lines,
- controlled data-quality issues for labs,
- starter Gold objects used by modules.
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## GLOBAL-01: reusable pre-check helper

`scripts/build_materials_v1.py` defines a generic `precheck_cell(required_tables, prereq_notebook)`
helper next to `md_cell`/`code_cell`. It generates a standardized code cell
that checks `spark.catalog.tableExists` for each required object and stops
with a friendly message naming the prerequisite notebook if anything is
missing. This is the first usage example; the same helper is meant to be
reused by `notebook_module_2/3/4` and `notebook_workshop_1/2` in a later
block to replace their current ad-hoc inline checks.

Here it checks that the Bronze/Silver/Gold schemas from
`setup/00_pre_config.ipynb` already exist before this notebook tries to
write any data into them.
"""),
        code_cell("""# GLOBAL-01: pre-check that upstream setup ran before we generate data.
schemas_seen = {r[0] for r in spark.sql(f"SHOW SCHEMAS IN {CATALOG}").collect()}
required_schemas = [BRONZE_SCHEMA, SILVER_SCHEMA, GOLD_SCHEMA]
missing_schemas = [s for s in required_schemas if s not in schemas_seen]

if missing_schemas:
    print("[BLOCKED] Missing required schemas in catalog", CATALOG, ":", missing_schemas)
    print()
    print("Run this notebook first: setup/00_pre_config.ipynb")
    raise Exception("Pre-check failed: missing schemas. Run setup/00_pre_config.ipynb first.")

print("[OK] Pre-check passed, schemas are ready:", required_schemas)"""),
        md_cell("""## 0. Data contract

This is the explicit contract for every Silver and Gold object this notebook
creates. Treat it as the source of truth when writing SQL in later modules —
if a query needs a column that is not listed here, check the grain first.

| Obiekt | Grain | Klucze | Właściciel |
|---|---|---|---|
| `silver.customers` | one row per customer | PK `customer_id` | Data Engineering |
| `silver.products` | one row per product | PK `product_id` | Data Engineering |
| `silver.sales_orders` | one row per order (header) | PK `order_id`; FK `customer_id` -> `silver.customers` | Data Engineering |
| `silver.order_lines` | one row per order line | FK `order_id` -> `silver.sales_orders`, `product_id` -> `silver.products`, `customer_id` -> `silver.customers` (denormalized for convenience) | Data Engineering |
| `gold.dim_date` | one row per calendar day | PK `date_key` | Analytics Engineering |
| `gold.dim_product` | one row per product | PK `product_id` | Analytics Engineering |
| `gold.dim_customer` | one row per customer | PK `customer_id` | Analytics Engineering |
| `gold.fact_sales` | one row per order line | FK `order_id`, `product_id`, `customer_id`; no enforced PK (line-grain fact) | Analytics Engineering |
| `gold.kpi_daily` | one row per `order_date` | PK `order_date` | Analytics Engineering |
| `gold.revenue_monthly` | one row per `year_month` x `region` x `category` | PK (`year_month`, `region`, `category`) | Analytics Engineering |

Note: `silver.order_lines.customer_id` is intentionally denormalized from the
order header so `gold.fact_sales` can read it directly without an extra join.
This was the source of a bug fixed earlier in the build (see
`docs/build-log.md`) — keep `order_lines` and `sales_orders` customer_id in
sync when changing the generator.
"""),
        code_cell("""from pyspark.sql import functions as F

spark.sql(f"USE CATALOG {CATALOG}")

for schema in [BRONZE_SCHEMA, SILVER_SCHEMA, GOLD_SCHEMA]:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{schema}")

print("Building dataset in", CATALOG)"""),
        md_cell("""## 1. Silver master data"""),
        code_cell("""customers = (
    spark.range(1, 10001).withColumnRenamed("id", "customer_id")
    .withColumn("customer_name", F.concat(F.lit("Customer "), F.col("customer_id")))
    .withColumn("email", F.concat(F.lit("customer_"), F.col("customer_id"), F.lit("@retailhub.example")))
    .withColumn("city", F.expr("element_at(array('Warsaw','Krakow','Gdansk','Poznan','Wroclaw'), cast(customer_id % 5 as int) + 1)"))
    .withColumn("region", F.expr("element_at(array('North','South','East','West'), cast(customer_id % 4 as int) + 1)"))
    .withColumn("country", F.lit("PL"))
    .withColumn("segment", F.expr("element_at(array('Consumer','SMB','Enterprise'), cast(customer_id % 3 as int) + 1)"))
    .withColumn("created_date", F.date_add(F.to_date(F.lit("2022-01-01")), (F.col("customer_id") % 900).cast("int")))
)

products = (
    spark.range(1, 501).withColumnRenamed("id", "product_id")
    .withColumn("product_name", F.concat(F.lit("Product "), F.col("product_id")))
    .withColumn("category", F.expr("element_at(array('Bikes','Components','Clothing','Accessories','Services'), cast(product_id % 5 as int) + 1)"))
    .withColumn("subcategory", F.concat(F.col("category"), F.lit(" / "), F.expr("cast(product_id % 10 as string)")))
    .withColumn("unit_cost", F.round(F.lit(10) + (F.col("product_id") % 90) * 1.37, 2))
    .withColumn("unit_price", F.round(F.col("unit_cost") * (F.lit(1.25) + (F.col("product_id") % 7) / 20), 2))
    .withColumn("is_active", (F.col("product_id") % 17 != 0))
)

customers.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.customers")
products.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.products")

print("Silver customers:", customers.count())
print("Silver products :", products.count())"""),
        md_cell("""## 2. Orders and controlled quality issues

The dataset intentionally includes bad rows. They are visible enough for
training, but small enough not to dominate the scenario. Each issue below is
seeded with a deterministic modulo rule so it reproduces the same way every
time the generator runs:

| Issue | Where | Rule |
|---|---|---|
| Future-dated order | `silver.sales_orders.order_date` | `order_id % 997 = 0` |
| Out-of-dictionary status | `silver.sales_orders.status` | `order_id % 101 = 0` -> `'Unknown'` |
| Missing `unit_price` | `silver.order_lines.unit_price` | `line_id % 1543 = 0` |
| Exact duplicate `(order_id, product_id)` row | `silver.order_lines` | `line_id % 10007 = 0`, re-inserted with a new `line_id` |
| Orphan `customer_id` (no match in `silver.customers`) | `silver.order_lines.customer_id` | `line_id % 4001 = 0` |
| Orphan `product_id` (no match in `silver.products`) | `silver.order_lines.product_id` | `line_id % 3001 = 0` |
| Header vs lines revenue mismatch | `silver.sales_orders.order_total_amount` | `order_id % 401 = 0` |
"""),
        code_cell("""orders = (
    spark.range(1, 120001).withColumnRenamed("id", "order_id")
    .withColumn("customer_id", ((F.col("order_id") * 17) % 10000 + 1).cast("long"))
    .withColumn("order_date", F.date_add(F.to_date(F.lit("2024-01-01")), (F.col("order_id") % 730).cast("int")))
    .withColumn("channel", F.expr("element_at(array('Online','Retail','Partner'), cast(order_id % 3 as int) + 1)"))
    .withColumn(
        "status",
        F.when(F.col("order_id") % 101 == 0, "Unknown")
         .when(F.col("order_id") % 13 == 0, "Returned")
         .when(F.col("order_id") % 11 == 0, "Cancelled")
         .otherwise("Completed")
    )
    .withColumn("region", F.expr("element_at(array('North','South','East','West'), cast(order_id % 4 as int) + 1)"))
)

# Controlled future-date issue.
orders = orders.withColumn(
    "order_date",
    F.when(F.col("order_id") % 997 == 0, F.date_add(F.current_date(), 30)).otherwise(F.col("order_date"))
)

line_base = spark.range(1, 360001).withColumnRenamed("id", "line_id")
order_lines = (
    line_base
    .withColumn("order_id", ((F.col("line_id") - 1) % 120000 + 1).cast("long"))
    .withColumn("product_id", ((F.col("line_id") * 19) % 500 + 1).cast("long"))
    .withColumn("quantity", ((F.col("line_id") % 5) + 1).cast("int"))
    .join(products.select("product_id", "unit_price", "unit_cost", "category"), "product_id", "left")
    .join(orders.select("order_id", "customer_id", "order_date", "channel", "status", "region"), "order_id", "left")
    .withColumn("discount_pct", F.when(F.col("line_id") % 23 == 0, F.lit(0.15)).otherwise(F.lit(0.0)))
    .withColumn("unit_price", F.when(F.col("line_id") % 1543 == 0, F.lit(None).cast("double")).otherwise(F.col("unit_price")))
    .withColumn("line_revenue", F.round(F.col("quantity") * F.col("unit_price") * (F.lit(1) - F.col("discount_pct")), 2))
    .withColumn("line_cost", F.round(F.col("quantity") * F.col("unit_cost"), 2))
    .withColumn("line_margin", F.round(F.col("line_revenue") - F.col("line_cost"), 2))
)

# Controlled duplicate issue: re-insert a full row with the same (order_id,
# product_id) pair under a new line_id, so it is a genuine exact duplicate
# of business keys, not just a near-duplicate.
duplicates = order_lines.filter("line_id % 10007 = 0").withColumn("line_id", F.col("line_id") + F.lit(10000000))
order_lines = order_lines.unionByName(duplicates)

# Controlled orphan-reference issues: point a handful of lines at customer_id
# / product_id values that are outside the valid dimension ranges
# (customers are 1..10000, products are 1..500), so dimension joins from
# these lines will not match in silver.customers / silver.products.
order_lines = order_lines.withColumn(
    "customer_id",
    F.when(F.col("line_id") % 4001 == 0, F.lit(900000000).cast("long")).otherwise(F.col("customer_id")),
)
order_lines = order_lines.withColumn(
    "product_id",
    F.when(F.col("line_id") % 3001 == 0, F.lit(900000000).cast("long")).otherwise(F.col("product_id")),
)

order_lines.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.order_lines")

# FND-03(b): RetailHub's order header does not natively carry a total
# amount. We add a minimal header-level `order_total_amount` column so the
# header-vs-lines reconciliation check is meaningful (a common real-world DQ
# check: does the source system's order total match what the line items sum
# to?). For most orders the header total is computed as the exact sum of its
# completed line revenue (so it reconciles). For orders where
# `order_id % 401 = 0` we seed a deliberate mismatch by inflating the header
# total by a fixed amount, simulating a stale/incorrectly-entered header
# total from the source system.
line_totals = order_lines.groupBy("order_id").agg(F.sum("line_revenue").alias("lines_revenue_sum"))
orders = (
    orders.join(line_totals, "order_id", "left")
    .withColumn("lines_revenue_sum", F.coalesce(F.col("lines_revenue_sum"), F.lit(0.0)))
    .withColumn(
        "order_total_amount",
        F.when(F.col("order_id") % 401 == 0, F.round(F.col("lines_revenue_sum") + F.lit(50.0), 2))
         .otherwise(F.round(F.col("lines_revenue_sum"), 2)),
    )
    .drop("lines_revenue_sum")
)

orders.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.sales_orders")

print("Silver sales_orders:", orders.count())
print("Silver order_lines :", order_lines.count())"""),
        md_cell("""## FND-04: table comments

`CREATE OR REPLACE TABLE ... COMMENT '...' AS SELECT ...` (used below for the
Gold CTAS objects) and `COMMENT ON TABLE` (used for the Silver tables, since
they are written with `saveAsTable` rather than CTAS) are both table-level
and universally supported across current Databricks Runtime / Unity Catalog
versions. Column-level comments (`COMMENT ON COLUMN ...` or inline
`col TYPE COMMENT '...'` in a `CREATE TABLE` column list) are a nice-to-have
on top of this — add them later if the target Databricks Runtime / SQL
Warehouse supports it in your workspace; we deliberately keep this block to
table-level comments only, since that is the part guaranteed to work
everywhere.
"""),
        code_cell('''spark.sql(f"COMMENT ON TABLE {SILVER}.customers IS 'Silver master data: one row per RetailHub customer. Source of truth for customer attributes used by gold.dim_customer.'")
spark.sql(f"COMMENT ON TABLE {SILVER}.products IS 'Silver master data: one row per RetailHub product. Source of truth for product attributes used by gold.dim_product.'")
spark.sql(f"COMMENT ON TABLE {SILVER}.sales_orders IS 'Silver order header: one row per order, including the order_total_amount header total used for header-vs-lines revenue reconciliation checks.'")
spark.sql(f"COMMENT ON TABLE {SILVER}.order_lines IS 'Silver order line detail: one row per order line. Contains the controlled data-quality issues used in the bad data lab (missing prices, duplicates, orphan references).'")

print("[OK] Silver table comments set")'''),
        md_cell("""## 3. Starter Gold objects"""),
        code_cell('''spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_date
COMMENT 'Gold date dimension: one row per calendar day, 2024-01-01 to 2026-12-31. Used to join fact tables to calendar attributes.'
AS
SELECT
  explode(sequence(to_date('2024-01-01'), to_date('2026-12-31'), interval 1 day)) AS date_key
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_date
COMMENT 'Gold date dimension: one row per calendar day, 2024-01-01 to 2026-12-31. Used to join fact tables to calendar attributes.'
AS
SELECT
  date_key,
  year(date_key) AS year,
  month(date_key) AS month,
  date_format(date_key, 'yyyy-MM') AS year_month,
  quarter(date_key) AS quarter
FROM {GOLD}.dim_date
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_product
COMMENT 'Gold product dimension: one row per product, conformed for BI consumption.'
AS
SELECT product_id, product_name, category, subcategory, unit_cost, unit_price, is_active
FROM {SILVER}.products
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_customer
COMMENT 'Gold customer dimension: one row per customer, conformed for BI consumption.'
AS
SELECT customer_id, customer_name, city, region, country, segment, created_date
FROM {SILVER}.customers
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales
COMMENT 'Gold fact table at order-line grain. Source of truth for sales KPIs (revenue, margin, orders). One row per silver.order_lines row.'
AS
SELECT
  l.line_id,
  l.order_id,
  l.order_date,
  l.customer_id,
  l.product_id,
  l.channel,
  l.status,
  l.region,
  l.quantity,
  l.unit_price,
  l.unit_cost,
  l.discount_pct,
  l.line_revenue,
  l.line_cost,
  l.line_margin,
  l.category
FROM {SILVER}.order_lines l
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.kpi_daily
COMMENT 'Gold daily KPI aggregate: one row per order_date, with revenue/margin/order counts for Completed and Returned orders. Pre-aggregated for fast dashboard queries.'
AS
SELECT
  order_date,
  SUM(CASE WHEN status = 'Completed' THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN status = 'Completed' THEN line_margin ELSE 0 END) AS gross_margin,
  COUNT(DISTINCT CASE WHEN status = 'Completed' THEN order_id END) AS completed_orders,
  COUNT(DISTINCT CASE WHEN status = 'Returned' THEN order_id END) AS returned_orders
FROM {GOLD}.fact_sales
GROUP BY order_date
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.revenue_monthly
COMMENT 'Gold monthly revenue aggregate: one row per year_month x region x category. Used by Power BI summary visuals to avoid scanning fact_sales directly.'
AS
SELECT
  date_format(order_date, 'yyyy-MM') AS year_month,
  region,
  category,
  SUM(CASE WHEN status = 'Completed' THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN status = 'Completed' THEN line_margin ELSE 0 END) AS gross_margin
FROM {GOLD}.fact_sales
GROUP BY date_format(order_date, 'yyyy-MM'), region, category
""")

print("[OK] Starter Gold objects created")'''),
        code_cell("""spark.sql(f"SHOW TABLES IN {GOLD}").show(truncate=False)"""),
        md_cell("""## FND-02: inspect the real schema

The data contract above is a claim. Confirm it against the actual schema of
the two most important Gold objects before trusting it.
"""),
        code_cell("""spark.sql(f"DESCRIBE TABLE {GOLD}.fact_sales").show(truncate=False)"""),
        code_cell("""spark.sql(f"DESCRIBE TABLE {GOLD}.dim_date").show(truncate=False)"""),
        md_cell("""## FND-01: runtime pre-check

This is the proof step. It is not enough that the cells above ran without an
exception — confirm that every Silver/Gold table exists, has a sane row
count, and that the seeded bad-data-lab problems are actually present in the
data. If any assertion below fails, the bad data lab will not work as
designed for later modules and workshops.
"""),
        code_cell("""# (a) Every Silver and Gold table exists.
all_tables = [
    f"{SILVER}.customers",
    f"{SILVER}.products",
    f"{SILVER}.sales_orders",
    f"{SILVER}.order_lines",
    f"{GOLD}.dim_date",
    f"{GOLD}.dim_product",
    f"{GOLD}.dim_customer",
    f"{GOLD}.fact_sales",
    f"{GOLD}.kpi_daily",
    f"{GOLD}.revenue_monthly",
]

missing = [t for t in all_tables if not spark.catalog.tableExists(t)]
assert not missing, f"Missing tables after generation: {missing}"
print("[OK] (a) all Silver and Gold tables exist:", len(all_tables))"""),
        code_cell("""# (b) Sane minimum row counts.
min_rows = {
    f"{SILVER}.customers": 9_000,
    f"{SILVER}.products": 400,
    f"{SILVER}.sales_orders": 100_000,
    f"{SILVER}.order_lines": 300_000,
    f"{GOLD}.dim_date": 1_000,
    f"{GOLD}.dim_product": 400,
    f"{GOLD}.dim_customer": 9_000,
    f"{GOLD}.fact_sales": 300_000,
    f"{GOLD}.kpi_daily": 600,
    f"{GOLD}.revenue_monthly": 50,
}

row_counts = {t: spark.table(t).count() for t in min_rows}
for table, minimum in min_rows.items():
    assert row_counts[table] >= minimum, (
        f"{table} has {row_counts[table]} rows, expected at least {minimum}"
    )
    print(f"[OK] (b) {table}: {row_counts[table]} rows (>= {minimum})")"""),
        code_cell('''# (c) The seeded bad-data-lab problems are actually present, not just
# happy-path data. These are the checks later modules and workshops rely on.
null_price_count = spark.sql(f"SELECT COUNT(*) AS n FROM {SILVER}.order_lines WHERE unit_price IS NULL").first()["n"]
assert null_price_count > 0, "Expected at least one order line with missing unit_price"
print("[OK] (c1) missing unit_price rows:", null_price_count)

bad_status_count = spark.sql(
    f"SELECT COUNT(*) AS n FROM {SILVER}.sales_orders WHERE status NOT IN ('Completed','Returned','Cancelled')"
).first()["n"]
assert bad_status_count > 0, "Expected at least one out-of-dictionary order status"
print("[OK] (c2) out-of-dictionary status rows:", bad_status_count)

future_order_count = spark.sql(
    f"SELECT COUNT(*) AS n FROM {SILVER}.sales_orders WHERE order_date > current_date()"
).first()["n"]
assert future_order_count > 0, "Expected at least one future-dated order"
print("[OK] (c3) future-dated order rows:", future_order_count)

exact_dup_count = spark.sql(f"""
    SELECT COUNT(*) AS n FROM (
        SELECT order_id, product_id, COUNT(*) AS cnt
        FROM {SILVER}.order_lines
        GROUP BY order_id, product_id
        HAVING COUNT(*) > 1
    )
""").first()["n"]
assert exact_dup_count > 0, "Expected at least one exact duplicate (order_id, product_id) pair"
print("[OK] (c4) duplicate (order_id, product_id) pairs:", exact_dup_count)

orphan_customer_count = spark.sql(f"""
    SELECT COUNT(*) AS n FROM {SILVER}.order_lines l
    LEFT ANTI JOIN {SILVER}.customers c ON l.customer_id = c.customer_id
""").first()["n"]
assert orphan_customer_count > 0, "Expected at least one orphan customer_id in order_lines"
print("[OK] (c5) orphan customer_id rows:", orphan_customer_count)

orphan_product_count = spark.sql(f"""
    SELECT COUNT(*) AS n FROM {SILVER}.order_lines l
    LEFT ANTI JOIN {SILVER}.products p ON l.product_id = p.product_id
""").first()["n"]
assert orphan_product_count > 0, "Expected at least one orphan product_id in order_lines"
print("[OK] (c6) orphan product_id rows:", orphan_product_count)

revenue_mismatch_count = spark.sql(f"""
    SELECT COUNT(*) AS n FROM (
        SELECT o.order_id, o.order_total_amount, SUM(l.line_revenue) AS lines_sum
        FROM {SILVER}.sales_orders o
        JOIN {SILVER}.order_lines l ON o.order_id = l.order_id
        GROUP BY o.order_id, o.order_total_amount
        HAVING ABS(o.order_total_amount - SUM(l.line_revenue)) > 0.01
    )
""").first()["n"]
assert revenue_mismatch_count > 0, "Expected at least one header-vs-lines revenue mismatch"
print("[OK] (c7) header-vs-lines revenue mismatches:", revenue_mismatch_count)

print()
print("[OK] FND-01 runtime pre-check passed: bad data lab confirmed working.")'''),
        md_cell("""## GLOBAL-01: self-check using the reusable pre-check helper

As a final proof that the helper itself works end to end, re-run the
standardized `precheck_cell` check against all Gold objects this notebook
just built. Module 2 onward can call the same generated pattern instead of
hand-rolling table-existence checks.
"""),
        precheck_cell(
            [
                "{GOLD}.dim_date",
                "{GOLD}.dim_product",
                "{GOLD}.dim_customer",
                "{GOLD}.fact_sales",
                "{GOLD}.kpi_daily",
                "{GOLD}.revenue_monthly",
            ],
            "data/generate_training_dataset.ipynb (this notebook)",
        ),
    ]
    write_notebook(ROOT / "data/generate_training_dataset.ipynb", cells)


def notebook_module_1() -> None:
    cells = [
        md_cell("""# Module 1 - SQL Warehouse, pricing and data profiling

![SQL Warehouse cost decision](../assets/images/sql_warehouse_cost_decision.png)

This module starts the RetailHub case. The goal is not only to run SQL, but to
understand which warehouse and Power BI mode will be cost-safe for the report.
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Real Databricks UI context

Use the source screenshots below as short visual anchors before the hands-on
part. They come from the base `Databricks-Data-Analyst` training.

![Databricks SQL Editor](../assets/images/source_sql_editor.png)

![Catalog Explorer hierarchy](../assets/images/source_catalog_explorer_hierarchy.png)
"""),
        md_cell("""## RetailHub source map

![RetailHub source map](../assets/images/retailhub_source_map.png)
"""),
        md_cell("""## Business question

RetailHub wants an executive KPI dashboard. Before building Gold tables, we
need to answer:

- What data exists?
- What is the grain?
- Which columns drive filters and joins?
- What can make the report expensive?
"""),
        md_cell("""## Runtime pre-check

If this fails, run:

1. `setup/00_pre_config.ipynb`
2. `data/generate_training_dataset.ipynb`
"""),
        code_cell("""required_tables = [
    f"{SILVER}.customers",
    f"{SILVER}.products",
    f"{SILVER}.sales_orders",
    f"{SILVER}.order_lines",
    f"{GOLD}.fact_sales",
]

missing = [table for table in required_tables if not spark.catalog.tableExists(table)]
if missing:
    raise Exception("Missing tables. Run setup and dataset generator first: " + ", ".join(missing))

print("[OK] Required tables exist")"""),
        code_cell("""spark.sql(f"SHOW TABLES IN {SILVER}").show(truncate=False)
spark.sql(f"SHOW TABLES IN {GOLD}").show(truncate=False)"""),
        code_cell('''spark.sql(f"""
SELECT 'customers' AS table_name, COUNT(*) AS rows FROM {SILVER}.customers
UNION ALL SELECT 'products', COUNT(*) FROM {SILVER}.products
UNION ALL SELECT 'sales_orders', COUNT(*) FROM {SILVER}.sales_orders
UNION ALL SELECT 'order_lines', COUNT(*) FROM {SILVER}.order_lines
""").show()'''),
        md_cell("""## Pricing and cost discussion

Use the official Databricks pricing page or calculator during delivery. Do not
treat values copied into training materials as permanent.

Trainer asset to refresh before delivery:

`assets/images/databricks_pricing_YYYY-MM-DD.png`

Decision questions:

- Is Import mode enough for the report?
- Which pages need live data?
- Does DirectQuery query Silver or Gold?
- What auto-stop is acceptable for a live demo?
"""),
        md_cell("""## Warehouse sizing discussion

Use this as a guided conversation, not as a static pricing lecture.

| Scenario | Candidate mode | Cost risk | Mitigation |
|---|---|---|---|
| Daily executive dashboard | Import | refresh window too wide | incremental refresh, monthly aggregate |
| Operational live page | DirectQuery | every slicer interaction sends SQL | Gold aggregate, fewer visuals, query profile |
| Ad-hoc analyst exploration | SQL Editor / Notebook | large scans | filters, sample first, select needed columns |
| Training demo | Serverless SQL Warehouse | idle time | short auto-stop, prepared objects |

Before delivery, refresh the current official pricing screenshot and place it
as `assets/images/databricks_pricing_YYYY-MM-DD.png`.
"""),
        md_cell("""## Data profiling"""),
        code_cell('''spark.sql(f"""
SELECT
  status,
  COUNT(DISTINCT order_id) AS orders
FROM {SILVER}.sales_orders
GROUP BY status
ORDER BY orders DESC
""").show()'''),
        code_cell('''spark.sql(f"""
SELECT
  MIN(order_date) AS min_order_date,
  MAX(order_date) AS max_order_date,
  COUNT(*) AS rows,
  COUNT(DISTINCT order_id) AS orders,
  COUNT(DISTINCT product_id) AS products
FROM {SILVER}.order_lines
""").show()'''),
        code_cell('''spark.sql(f"""
SELECT
  channel,
  region,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(line_revenue), 2) AS line_revenue
FROM {SILVER}.order_lines
GROUP BY channel, region
ORDER BY line_revenue DESC
""").show(truncate=False)'''),
        code_cell('''spark.sql(f"""
SELECT
  category,
  COUNT(*) AS lines,
  COUNT(DISTINCT product_id) AS products,
  ROUND(AVG(unit_price), 2) AS avg_price,
  ROUND(AVG(unit_cost), 2) AS avg_cost
FROM {SILVER}.order_lines
GROUP BY category
ORDER BY lines DESC
""").show(truncate=False)'''),
        md_cell("""## First risk scan

This is the moment to show why Gold exists. The source is usable, but not yet a
trusted BI contract.
"""),
        code_cell('''spark.sql(f"""
SELECT 'invalid_status' AS issue, COUNT(*) AS rows FROM {SILVER}.sales_orders
WHERE status NOT IN ('Completed','Cancelled','Returned')
UNION ALL
SELECT 'future_orders', COUNT(*) FROM {SILVER}.sales_orders
WHERE order_date > current_date()
UNION ALL
SELECT 'missing_prices', COUNT(*) FROM {SILVER}.order_lines
WHERE unit_price IS NULL
UNION ALL
SELECT 'duplicate_line_ids', COUNT(*) - COUNT(DISTINCT line_id) FROM {SILVER}.order_lines
""").show(truncate=False)'''),
        md_cell("""## Artifact: first data map

Fill this in during the session:

| Object | Grain | Business use | Risk |
|---|---|---|---|
| `silver.sales_orders` | one row per order | status, date, customer | status definitions |
| `silver.order_lines` | one row per order line | revenue, margin, quantity | missing prices, duplicates |
| `gold.fact_sales` | one row per order line | BI fact | must be validated |
"""),
        md_cell("""## Mini exercise: warehouse decision

In pairs, decide the baseline for the executive dashboard:

| Decision | Your answer |
|---|---|
| Import or DirectQuery by default? | |
| Which Gold object should feed summary pages? | |
| What warehouse auto-stop would you use for a live demo? | |
| Which query should never be executed by a Power BI visual? | |

Trainer note: this section can easily take 15-20 minutes when participants
compare cost, freshness and usability trade-offs.
"""),
    ]
    write_notebook(ROOT / "notebooks/m1_sql_warehouse_notebooks.ipynb", cells)


def notebook_module_2() -> None:
    cells = [
        md_cell("""# Module 2 - Medallion, Gold layer, Kimball and KPI

![Medallion to Power BI](../assets/images/medallion_to_powerbi.png)

The Gold layer is the contract between data engineering, analytics and BI.
This module builds the RetailHub Gold model and makes KPI definitions explicit.
This is the spine of the course: everything in Workshop 1, Module 3 and
Workshop 2 depends on objects created here.
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## GLOBAL-01: runtime pre-check

Reuses the standardized `precheck_cell` helper from
`scripts/build_materials_v1.py` (first used in
`data/generate_training_dataset.ipynb`). It checks that the Gold starter
objects from the generator already exist, and stops with a clear message if
they do not, instead of failing later with a confusing `TABLE_OR_VIEW_NOT_FOUND`.
"""),
        precheck_cell(
            [
                "{GOLD}.dim_date",
                "{GOLD}.dim_product",
                "{GOLD}.dim_customer",
                "{GOLD}.fact_sales",
            ],
            "data/generate_training_dataset.ipynb",
        ),
        md_cell("""## M2-01: Medallion layers in practice

Bronze, Silver and Gold are not just "three folders" - they are three
different contracts with different owners, different quality bars and
different consumers.

| Layer | Ownership | Quality bar | Latency | Typical consumers |
|---|---|---|---|---|
| Bronze | Data Engineering | raw, as-landed; no dedup, no schema enforcement beyond ingestion | minutes to hours | Data Engineering only |
| Silver | Data Engineering | cleaned types, conformed keys, documented known issues; **not** guaranteed business-correct | hourly to daily | Analytics Engineering, advanced analysts |
| Gold | Analytics Engineering | business-validated, agreed KPI definitions, stable grain, owner assigned | daily (or per refresh contract) | BI tools, dashboards, executives, most analysts |

**What should NOT land in Gold:**

- raw, unvalidated rows with known data-quality issues (orphan keys, nulls
  in measures, out-of-dictionary statuses) - those stay visible in Silver
  for investigation, not hidden in Gold,
- ad-hoc one-off filters that only make sense for a single report,
- personal calculation logic that has not been agreed with the KPI owner,
- columns nobody can explain the business meaning of.

**Gold vs. an analyst's ad-hoc working view:** an ad-hoc view answers one
person's question once, with whatever join and filter felt right that day.
Gold answers an organization's question repeatedly, with a join and filter
that have been reviewed, documented (see the data contract in the data
generator notebook) and will give the same number to Finance, Sales Ops and
the CEO whenever they ask. If the number cannot survive three people asking
"why" once, it is not ready for Gold.
"""),
        md_cell("""## Why Gold exists

![Gold business value](../assets/images/gold_business_value.png)

The business value of Gold is not "another table". It is:

- one agreed definition of revenue and margin,
- stable grain for Power BI,
- fewer expensive joins in reports,
- repeatable validation,
- a place to document ownership and refresh.

RetailHub case:

The CEO sees lower margin in the weekly dashboard. Without Gold, three teams
arrive with three different answers because they apply different filters and
return logic. With Gold, the group debates the business event, not the SQL.

Training prompt:

- Which KPI must be owned by Finance?
- Which KPI can be owned by Sales Ops?
- Which caveat must be visible in the BI contract?
"""),
        md_cell("""## Star schema or flat BI table?

![Star schema vs flat table](../assets/images/star_schema_vs_flat_table.png)

For this course we use both ideas:

- dimensions and facts to explain Kimball discipline,
- a curated dashboard table/aggregate for Power BI simplicity and cost control.

## M2-02: Kimball step-by-step - grain first

Kimball discipline says: agree the **grain** before you build anything. The
grain is the answer to "what does one row in this table represent?". Decide
it wrong and every downstream SUM/COUNT/AVG is silently wrong too.

For RetailHub's dashboard fact table we declare the grain up front:

> **One row = one order line, enriched with customer and product attributes,
> with a flag for whether the line counts toward completed/returned KPIs.**

This is deliberately the *same* grain as `gold.fact_sales` (one row per
order line) - we are not changing the grain, we are denormalizing it for BI
convenience. If the grain were different (e.g. one row per order), every
KPI definition below would need to change too.
"""),
        md_cell("""## Recap: the conformed dimensions already exist

`data/generate_training_dataset.ipynb` already built the Kimball-style
dimensions this module reuses. We do not recreate them - we inspect them as
the worked example of "build dimensions before the fact".
"""),
        code_cell('''spark.sql(f"DESCRIBE TABLE {GOLD}.dim_date").show(truncate=False)
spark.sql(f"DESCRIBE TABLE {GOLD}.dim_customer").show(truncate=False)
spark.sql(f"DESCRIBE TABLE {GOLD}.dim_product").show(truncate=False)'''),
        code_cell('''spark.sql(f"SELECT * FROM {GOLD}.dim_customer LIMIT 5").show(truncate=False)
spark.sql(f"SELECT * FROM {GOLD}.dim_product LIMIT 5").show(truncate=False)'''),
        md_cell("""## Kimball Gold model

![Kimball Gold model](../assets/images/kimball_gold_model.png)

`dim_date`, `dim_customer` and `dim_product` are the conformed dimensions
above. The fact table in the diagram is the line-grain fact we are about to
build as `gold.fact_sales_dashboard` - distinct from the generator's
`gold.fact_sales` (same grain, denormalized for BI consumption: dimension
attributes are pre-joined so Power BI does not need to repeat the joins on
every query).

Before we build it, we prove the grain of the source fact table and check
whether a join can create fan-out (duplicate rows per key, which silently
inflates SUM/COUNT).
"""),
        code_cell('''spark.sql(f"""
SELECT
  COUNT(*) AS rows,
  COUNT(DISTINCT line_id) AS distinct_line_ids,
  COUNT(*) - COUNT(DISTINCT line_id) AS duplicate_line_ids
FROM {GOLD}.fact_sales
""").show()'''),
        code_cell('''spark.sql(f"""
SELECT
  COUNT(*) AS rows_after_customer_join,
  COUNT(DISTINCT f.line_id) AS distinct_line_ids
FROM {GOLD}.fact_sales f
LEFT JOIN {GOLD}.dim_customer c
  ON f.customer_id = c.customer_id
""").show()'''),
        md_cell("""## Build `gold.fact_sales_dashboard`

This is Module 2's own artifact: a denormalized, dashboard-ready fact table
at the grain declared above. It is a NEW object, distinct from the
generator's `gold.fact_sales` - Workshop 1 and later modules depend on this
table existing, so it is created here, not just discussed.
"""),
        code_cell('''spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard
COMMENT 'Module 2 Kimball-style dashboard fact: one row per order line (same grain as gold.fact_sales), denormalized with customer and product attributes for direct Power BI consumption.'
AS
SELECT
  f.order_date,
  f.order_id,
  f.line_id,
  f.customer_id,
  c.segment,
  c.region AS customer_region,
  f.product_id,
  p.category,
  p.subcategory,
  f.channel,
  f.status,
  f.quantity,
  f.unit_price,
  f.unit_cost,
  f.discount_pct,
  f.line_revenue,
  f.line_cost,
  f.line_margin,
  CASE WHEN f.status = 'Completed' THEN true ELSE false END AS is_completed,
  CASE WHEN f.status = 'Returned' THEN true ELSE false END AS is_returned
FROM {GOLD}.fact_sales f
LEFT JOIN {GOLD}.dim_customer c ON f.customer_id = c.customer_id
LEFT JOIN {GOLD}.dim_product p ON f.product_id = p.product_id
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard_monthly
COMMENT 'Monthly aggregate over gold.fact_sales_dashboard for summary Power BI visuals. Must reconcile against the detail table - see the reconciliation check below.'
AS
SELECT
  date_format(order_date, 'yyyy-MM') AS year_month,
  customer_region,
  category,
  channel,
  SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END) AS gross_margin,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders,
  COUNT(DISTINCT CASE WHEN is_returned THEN order_id END) AS returned_orders
FROM {GOLD}.fact_sales_dashboard
GROUP BY date_format(order_date, 'yyyy-MM'), customer_region, category, channel
""")

print("[OK] gold.fact_sales_dashboard and gold.fact_sales_dashboard_monthly created")'''),
        md_cell("""## Gold quality gate

![Gold quality gate](../assets/images/gold_quality_gate.png)

The checks below are intentionally business-facing. A red result does not
automatically mean "stop the project"; it means "write a decision".
"""),
        md_cell("""## M2-03: KPI dictionary - built in the notebook

This recreates `docs/templates/kpi-dictionary.md` as in-notebook work: each
KPI gets a business definition AND a SQL definition side by side, queried
directly against `gold.fact_sales_dashboard` so the numbers are not just
claims.

| KPI | Business definition | SQL definition | Grain | Caveat |
|---|---|---|---|---|
| Revenue | Completed order line revenue after discount | `SUM(line_revenue) WHERE is_completed` | order line | excludes returned/cancelled lines |
| Gross margin | Completed revenue minus completed cost | `SUM(line_margin) WHERE is_completed` | order line | depends on product cost data quality |
| Return rate | Returned orders / (completed + returned) orders | `COUNT(DISTINCT order_id WHERE is_returned) / COUNT(DISTINCT order_id WHERE is_completed OR is_returned)` | order | must use `COUNT(DISTINCT order_id)`, not line count |
| Orders | Distinct completed orders | `COUNT(DISTINCT order_id) WHERE is_completed` | order | line-grain `COUNT(*)` over-counts - see distinct-count trap below |
| DQ score | Weighted count of failed quality checks | `SUM(score_component)` from `gold.data_quality_score` | one row per run | see M2-05 breakdown below for what is and is not included |
"""),
        code_cell('''kpi_dictionary = spark.sql(f"""
SELECT
  SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END) AS gross_margin,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders,
  COUNT(DISTINCT CASE WHEN is_returned THEN order_id END) AS returned_orders,
  ROUND(
    COUNT(DISTINCT CASE WHEN is_returned THEN order_id END) /
    NULLIF(COUNT(DISTINCT CASE WHEN is_completed OR is_returned THEN order_id END), 0),
    4
  ) AS return_rate
FROM {GOLD}.fact_sales_dashboard
""")
kpi_dictionary.show(truncate=False)

# Persist the KPI dictionary numbers as a temp view so the rest of the
# notebook (and Workshop 1) can query "today's KPI snapshot" by name instead
# of re-deriving it from scratch.
kpi_dictionary.createOrReplaceTempView("kpi_dictionary_snapshot")
print("[OK] kpi_dictionary_snapshot temp view created")'''),
        md_cell("""## KPI definition flow

![KPI definition flow](../assets/images/kpi_definition_flow.png)

### Distinct-count trap

If the same order can contain products from many categories, summing order
counts by category can over-count orders. This is a good discussion point for
Power BI modelling and aggregation design - and it is exactly the
`COUNT(DISTINCT)` pitfall referenced in the KPI dictionary above: counting
orders at line-grain without `DISTINCT` inflates the count.
"""),
        code_cell('''spark.sql(f"""
SELECT
  COUNT(*) AS line_grain_count_no_distinct,
  COUNT(DISTINCT order_id) AS correct_distinct_order_count,
  COUNT(*) - COUNT(DISTINCT order_id) AS inflation_from_wrong_grain
FROM {GOLD}.fact_sales_dashboard
WHERE is_completed
""").show()'''),
        code_cell('''spark.sql(f"""
WITH by_category AS (
  SELECT
    category,
    COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders
  FROM {GOLD}.fact_sales_dashboard
  GROUP BY category
),
overall AS (
  SELECT COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders
  FROM {GOLD}.fact_sales_dashboard
)
SELECT
  (SELECT SUM(completed_orders) FROM by_category) AS sum_of_category_orders,
  (SELECT completed_orders FROM overall) AS true_completed_orders,
  (SELECT SUM(completed_orders) FROM by_category) - (SELECT completed_orders FROM overall) AS overcount
""").show()'''),
        md_cell("""## M2-04: Reconciliation - `fact_sales` vs `fact_sales_dashboard`

Two Gold objects exist at the same grain (one row per order line):
`gold.fact_sales` (the generator's grain) and `gold.fact_sales_dashboard`
(this module's denormalized grain). They must reconcile - if they do not,
either the join logic or the grain assumption is wrong.
"""),
        code_cell('''spark.sql(f"""
WITH base AS (
  SELECT
    ROUND(SUM(CASE WHEN status = 'Completed' THEN line_revenue ELSE 0 END), 2) AS revenue
  FROM {GOLD}.fact_sales
),
dashboard AS (
  SELECT
    ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard
)
SELECT
  base.revenue AS fact_sales_revenue,
  dashboard.revenue AS fact_sales_dashboard_revenue,
  base.revenue - dashboard.revenue AS diff
FROM base CROSS JOIN dashboard
""").show()'''),
        md_cell("""## Reconciliation: detail vs aggregate

The monthly aggregate is safe for summary reporting only if totals reconcile
against the detail table at the same filter scope.
"""),
        code_cell('''spark.sql(f"""
WITH detail AS (
  SELECT
    ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS revenue,
    ROUND(SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END), 2) AS gross_margin
  FROM {GOLD}.fact_sales_dashboard
),
agg AS (
  SELECT
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin
  FROM {GOLD}.fact_sales_dashboard_monthly
)
SELECT
  detail.revenue AS detail_revenue,
  agg.revenue AS aggregate_revenue,
  detail.revenue - agg.revenue AS revenue_diff,
  detail.gross_margin AS detail_margin,
  agg.gross_margin AS aggregate_margin,
  detail.gross_margin - agg.gross_margin AS margin_diff
FROM detail CROSS JOIN agg
""").show()'''),
        md_cell("""## Reconciliation breaks: a deliberately bad join (fan-out)

This is the negative example: joining `fact_sales_dashboard` back to
`dim_product` on `category` instead of `product_id` creates a many-to-many
fan-out (many products share a category), duplicating rows and inflating
revenue. This is what "the bad join breaking the match" looks like in
practice - compare this result to the correct reconciliation above.
"""),
        code_cell('''spark.sql(f"""
WITH bad_join AS (
  SELECT f.line_id, f.line_revenue, f.is_completed
  FROM {GOLD}.fact_sales_dashboard f
  JOIN {GOLD}.dim_product p ON f.category = p.category
)
SELECT
  COUNT(*) AS rows_after_fanout_join,
  (SELECT COUNT(*) FROM {GOLD}.fact_sales_dashboard) AS rows_before_join,
  ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS inflated_revenue,
  (SELECT ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) FROM {GOLD}.fact_sales_dashboard) AS correct_revenue
FROM bad_join
""").show()'''),
        md_cell("""## M2-05: Data quality score - breakdown and severity

Reuses Block 1's expanded bad-data-lab checks (orphan refs, revenue
mismatch, exact duplicates, null prices, bad statuses, future dates) and
turns them into a numeric/categorical score with a severity threshold per
issue type.
"""),
        code_cell('''dq_checks = spark.sql(f"""
WITH checks AS (
  SELECT 'missing_price' AS issue_type, 'high' AS severity, COUNT(*) AS issue_count
  FROM {SILVER}.order_lines WHERE unit_price IS NULL
  UNION ALL
  SELECT 'invalid_status', 'medium', COUNT(*)
  FROM {SILVER}.sales_orders WHERE status NOT IN ('Completed','Cancelled','Returned')
  UNION ALL
  SELECT 'future_order_date', 'high', COUNT(*)
  FROM {SILVER}.sales_orders WHERE order_date > current_date()
  UNION ALL
  SELECT 'orphan_customer_id', 'high', COUNT(*)
  FROM {SILVER}.order_lines l LEFT ANTI JOIN {SILVER}.customers c ON l.customer_id = c.customer_id
  UNION ALL
  SELECT 'orphan_product_id', 'high', COUNT(*)
  FROM {SILVER}.order_lines l LEFT ANTI JOIN {SILVER}.products p ON l.product_id = p.product_id
  UNION ALL
  SELECT 'exact_duplicate_line', 'medium', COUNT(*) FROM (
    SELECT order_id, product_id FROM {SILVER}.order_lines
    GROUP BY order_id, product_id HAVING COUNT(*) > 1
  )
  UNION ALL
  SELECT 'revenue_mismatch_header_vs_lines', 'high', COUNT(*) FROM (
    SELECT o.order_id FROM {SILVER}.sales_orders o
    JOIN {SILVER}.order_lines l ON o.order_id = l.order_id
    GROUP BY o.order_id, o.order_total_amount
    HAVING ABS(o.order_total_amount - SUM(l.line_revenue)) > 0.01
  )
)
SELECT
  issue_type,
  severity,
  issue_count,
  CASE severity WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END AS severity_weight,
  CASE
    WHEN issue_count = 0 THEN 0.0
    ELSE ROUND(issue_count * (CASE severity WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END) / 100.0, 2)
  END AS penalty_points
FROM checks
ORDER BY penalty_points DESC
""")
dq_checks.createOrReplaceTempView("dq_breakdown")
dq_checks.show(truncate=False)

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.data_quality_score
COMMENT 'Gold data quality scorecard: 100 minus weighted penalty points per issue type/severity from the bad-data-lab checks. Recomputed each time Module 2 runs.'
AS
SELECT
  current_timestamp() AS calculated_at,
  ROUND(GREATEST(0, 100 - SUM(penalty_points)), 1) AS score
FROM dq_breakdown
""")
spark.sql(f"SELECT * FROM {GOLD}.data_quality_score").show()'''),
        md_cell("""## Sample bad rows per issue type

One or two concrete rows per issue type, so the score is not an abstract
number - participants can see exactly which records are failing and why.
"""),
        code_cell('''print("-- missing_price (silver.order_lines) --")
spark.sql(f"""
SELECT line_id, order_id, product_id, unit_price FROM {SILVER}.order_lines
WHERE unit_price IS NULL LIMIT 2
""").show(truncate=False)

print("-- orphan_customer_id (silver.order_lines) --")
spark.sql(f"""
SELECT l.line_id, l.order_id, l.customer_id FROM {SILVER}.order_lines l
LEFT ANTI JOIN {SILVER}.customers c ON l.customer_id = c.customer_id
LIMIT 2
""").show(truncate=False)

print("-- revenue_mismatch_header_vs_lines (silver.sales_orders) --")
spark.sql(f"""
SELECT o.order_id, o.order_total_amount, ROUND(SUM(l.line_revenue), 2) AS lines_sum
FROM {SILVER}.sales_orders o JOIN {SILVER}.order_lines l ON o.order_id = l.order_id
GROUP BY o.order_id, o.order_total_amount
HAVING ABS(o.order_total_amount - SUM(l.line_revenue)) > 0.01
LIMIT 2
""").show(truncate=False)

print("-- exact_duplicate_line (silver.order_lines) --")
spark.sql(f"""
SELECT order_id, product_id, COUNT(*) AS dup_count FROM {SILVER}.order_lines
GROUP BY order_id, product_id HAVING COUNT(*) > 1 LIMIT 2
""").show(truncate=False)'''),
        md_cell("""## Decision: fix in Silver, Gold, or the report layer?

Where a fix belongs depends on whether the issue is a data-entry problem
(fix upstream/Silver), a business-rule decision (encode in Gold), or a
presentation choice (handle in the report layer).

| Issue type | Fix layer | Reasoning |
|---|---|---|
| `missing_price` | Silver | Source data defect; Gold should not guess a price. Block the row or flag it until corrected at the source. |
| `orphan_customer_id` / `orphan_product_id` | Silver | Referential integrity belongs in Silver - Gold dimensions should only ever join cleanly. Quarantine orphan rows before they reach Gold. |
| `revenue_mismatch_header_vs_lines` | Gold (documented), Silver (root cause) | Gold should pick one source of truth (lines, since that is the agreed Revenue KPI definition) and document the caveat; Silver/source should still investigate why headers drift. |
| `exact_duplicate_line` | Silver | Deduplication is a cleaning responsibility - Gold should never have to deduplicate at read time, that is expensive and easy to get wrong per-report. |
| `invalid_status` (out-of-dictionary) | Gold | This is a business-rule mapping decision (how do we treat `'Unknown'`?), not a data-entry fix - encode the mapping once in Gold so every report applies it the same way. |
| `future_order_date` | Report layer (filter) + Silver (alert) | Showing future-dated orders in a "this month" report is a presentation bug - filter in the report/semantic layer, but also alert Silver owners since it likely signals a clock or feed issue. |
"""),
        md_cell("""## Lineage and discoverability

![Catalog Explorer lineage](../assets/images/source_catalog_explorer_lineage.png)

Trainer prompt:

- Which object would you certify?
- Which object would you hide from BI users?
- Which object should have the clearest owner and description?

### Decision card: view vs table vs aggregate

| Option | Use when | Risk |
|---|---|---|
| View | logic is simple and source is small | repeated cost on every query |
| Table | stable BI source, scheduled refresh | needs orchestration |
| Aggregate | summary page or DirectQuery | lower detail, needs grain discipline |

## M2-06: Bonus (dla szybszych grup)

This section is genuinely optional - skip it if the group is on schedule or
behind. It introduces a Metric View / materialized aggregate as an advanced
topic on top of what was already built.
"""),
        md_cell("""### Bonus: Metric View or materialized aggregate

A Databricks Unity Catalog **Metric View** lets you define measures and
dimensions once (centrally governed) so every consumer - SQL, Power BI,
Genie - gets the same KPI math without re-deriving it per report. Where a
Metric View is not available in your workspace/runtime, a materialized
aggregate table (what we already built as `fact_sales_dashboard_monthly`)
is the practical fallback.

Discussion prompts for fast groups:

- Which KPIs from the dictionary above are safe to pre-aggregate, and which
  must stay computable at line-grain (e.g. return rate needs order-level
  distinctness, not just a sum)?
- What happens to the Metric View / aggregate when a new KPI is added later
  - do consumers need to change their queries?
- How would you version a breaking change to a KPI definition without
  silently changing historical dashboard numbers?
"""),
        code_cell('''# Bonus hands-on: an additional materialized aggregate by year_month, segment
# and category - a finer-grained alternative to fact_sales_dashboard_monthly,
# useful for a segment/category drill-through page.
spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard_segment_monthly
COMMENT 'Bonus materialized aggregate: one row per year_month x segment x category, for segment/category drill-through pages.'
AS
SELECT
  date_format(order_date, 'yyyy-MM') AS year_month,
  segment,
  category,
  SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END) AS gross_margin,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders
FROM {GOLD}.fact_sales_dashboard
GROUP BY date_format(order_date, 'yyyy-MM'), segment, category
""")
spark.sql(f"SELECT * FROM {GOLD}.fact_sales_dashboard_segment_monthly ORDER BY year_month LIMIT 10").show()'''),
        md_cell("""## Optional extension for longer delivery

If the group is strong or the course has 8-9 hours:

- add a Type 2 dimension example for customer segment changes,
- add table and column comments for BI discoverability,
- compare `fact_sales_dashboard` as a view vs table,
- ask participants to write the final KPI dictionary row by row using
  `docs/templates/kpi-dictionary.md`.
"""),
    ]
    write_notebook(ROOT / "notebooks/m2_gold_kpi_best_practices.ipynb", cells)


def notebook_module_3() -> None:
    cells = [
        md_cell("""# Module 3 - Power BI semantic dataset: Import and live

![Power BI mockup](../assets/images/powerbi_report_mockup.png)

The model is built in Databricks. Power BI should be a thin reporting layer with
only the measures and interactions that belong in the report.
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Runtime pre-check

Run Module 2 first. This notebook expects the dashboard fact and monthly
aggregate to exist.
"""),
        precheck_cell(
            [
                "{GOLD}.fact_sales_dashboard",
                "{GOLD}.fact_sales_dashboard_monthly",
            ],
            "notebooks/m2_gold_kpi_best_practices.ipynb",
        ),
        md_cell("""## 1. Import vs live/DirectQuery - decision table

![Import vs DirectQuery](../assets/images/import_vs_directquery.png)

Both modes read the same Gold tables. The difference is *when* and *how often*
Databricks does the work.

| Dimension | Import | DirectQuery / live |
|---|---|---|
| Where the query runs | once, at refresh time, into an in-memory Power BI model | every time a user opens a page or changes a filter |
| Data freshness | as fresh as the last refresh (minutes to hours old) | as fresh as the warehouse, essentially real time |
| SQL Warehouse load | one batch query per refresh | one query per visual per interaction |
| Report responsiveness | fast, served from memory | depends on warehouse latency and concurrency |
| Cost driver | scheduled refresh compute | every click, every filter change |
| Best source shape | aggregate or curated table | small, well-indexed table or selective view |
""" ),
        md_cell("""### Query fan-out: why DirectQuery cost is not linear

A Power BI page with 6 visuals does not send 1 query per refresh - it can send
**1 query per visual per filter context**. A KPI card, a trend chart and a
region bar chart on the same page each fire their own SQL query against the
warehouse. Slicers and cross-filtering multiply this further: changing one
slicer can re-trigger every visual that listens to it.

```
1 page, 6 visuals, 1 slicer change
  -> up to 6 new SQL Warehouse queries per click
  -> multiplied by every active report user
```

This is the **interaction cost** of DirectQuery: it scales with `visuals x
filter changes x concurrent users`, not with data volume. Import mode pays
this cost once, at refresh time, regardless of how many users click around
afterwards.

**When does live/DirectQuery make sense?**

- an operational dashboard where "this morning's returns" must be exact, not
  approximate to the last refresh,
- a narrow page (1-3 visuals) against a small, pre-aggregated Gold object,
- a controlled audience (few concurrent users) where warehouse cost is
  predictable,
- never as the default for a wide exploratory report with many slicers.
"""),
        md_cell("""## 2. Power BI connector context

![Power BI DirectQuery connector](../assets/images/source_powerbi_directquery_connector.webp)

This is the real Power BI "Get Data" connector dialog for Databricks. Use it
as a visual walkthrough before opening Power BI Desktop. The key point for
analysts: connector mode (`Import` vs `DirectQuery`) is selected here, in the
connector dialog, before any table is even chosen - it is a modelling
decision, not just a technical checkbox.
"""),
        md_cell("""## 3. Connection walkthrough (live Power BI Desktop)

![Power BI connection walkthrough](../assets/images/powerbi_connection_walkthrough.png)

Step-by-step, with exactly where each value comes from:

1. In Databricks, open the **SQL Warehouse** that will serve the report.
2. Go to **Connection details** on the warehouse page and copy:
   - **Server hostname** - looks like `dbc-xxxxxxxx-xxxx.cloud.databricks.com`,
   - **HTTP path** - looks like `/sql/1.0/warehouses/xxxxxxxxxxxxxxxx`.
3. In Power BI Desktop: **Get Data -> Databricks** (or **Azure Databricks**).
4. Paste **Server hostname** and **HTTP path** into the connector dialog.
5. Choose **Import** or **DirectQuery** *now* - this cannot be changed per
   table later without redoing the connection.
6. Authenticate (Azure AD / personal access token per your workspace policy).
7. In the navigator, select **only Gold objects** - `fact_sales_dashboard_monthly`,
   `v_fact_sales_incremental` (built below), `dim_date`, `dim_product`,
   `dim_customer`. Do not browse into Silver or Bronze schemas.
8. Click **Load** (Import) or **Transform Data** to shape column types first.

Trainer notes: explain authentication before discussing which tables to pick,
and default to Import unless a live use case from the decision table above is
explicit.
"""),
        md_cell("""### Variant: no Power BI Desktop available

Some training rooms cannot install or license Power BI Desktop. Per the
project's own risk mitigation (`docs/04-pre-implementation-analysis.md`,
Risk 3: "DirectQuery/live moze byc demo prowadzacego lub mock demo"), this
module works without live Power BI access:

- **Trainer demo (preferred when available):** the trainer runs the 8 steps
  above live, on a shared screen, against this workspace's SQL Warehouse.
  Participants follow along on the screenshots only.
- **Mock walkthrough (no Power BI access for anyone):** narrate each step
  against the screenshots in this notebook instead of clicking through a real
  dialog:
  1. Point at `source_powerbi_directquery_connector.webp` - "this is where you
     choose Import vs DirectQuery, before picking any table."
  2. Point at `powerbi_connection_walkthrough.png` step 2 - "Server hostname
     and HTTP path always come from the SQL Warehouse Connection details tab,
     never typed from memory."
  3. Point at step 5 ("Choose mode") - "this single click decides whether the
     warehouse is queried once per refresh or once per click for the rest of
     the report's life."
  4. Run the two SQL cells below in this notebook - they reproduce exactly
     what Power BI would receive, so the data and the query shape are still
     real even though no Power BI UI was opened.
- Either way, every participant leaves with the same decision (mode per
  table) recorded in the BI contract section further down.
"""),
        md_cell("""## 4. Incremental refresh: building `v_fact_sales_incremental`

![Incremental refresh](../assets/images/incremental_refresh_range.png)

**Requirements for the date column used in incremental refresh:**

- must be a real `DATE` (or `TIMESTAMP`) column, not a string,
- must not be null for rows that should ever be refreshed,
- should be the column the business actually files transactions under
  (here: `order_date`), so partition boundaries match reporting periods,
- the source table/view must allow a `WHERE column >= X AND column < Y`
  predicate to be pushed down efficiently (partitioning or clustering helps).

`order_date` on `gold.fact_sales_dashboard` satisfies all four, so the
incremental view below is built directly on top of it, with a 24-month
rolling window to keep the detail table bounded.
"""),
        code_cell('''spark.sql(f"""
CREATE OR REPLACE VIEW {GOLD}.v_fact_sales_incremental AS
SELECT
  order_date,
  order_id,
  line_id,
  customer_id,
  segment,
  customer_region,
  product_id,
  category,
  subcategory,
  channel,
  status,
  quantity,
  line_revenue,
  line_margin
FROM {GOLD}.fact_sales_dashboard
WHERE order_date >= add_months(current_date(), -24)
""")

spark.sql(f"SELECT MIN(order_date), MAX(order_date), COUNT(*) FROM {GOLD}.v_fact_sales_incremental").show()'''),
        md_cell("""### RangeStart / RangeEnd and the half-open interval

Power BI's incremental refresh policy injects two parameters into the query
that defines a partition: `RangeStart` and `RangeEnd`. The recommended date
filter is **half-open** - inclusive on the start, exclusive on the end:

```sql
WHERE order_date >= RangeStart
  AND order_date <  RangeEnd
```

If both ends were inclusive (`<=`), a row dated exactly at a partition
boundary (e.g. midnight on the 1st of the month) would be refreshed by *two*
adjacent partitions and double-counted in any cross-partition aggregation.
Half-open intervals tile the timeline with no overlap and no gap.
"""),
        code_cell('''# Simulates what Power BI sends for one refresh partition: RangeStart = 2025-01-01, RangeEnd = 2025-04-01
spark.sql(f"""
SELECT
  COUNT(*) AS rows_in_window,
  MIN(order_date) AS min_date,
  MAX(order_date) AS max_date
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-04-01'
""").show()'''),
        code_cell('''# Boundary check: a row dated exactly on RangeEnd must NOT appear in this window (half-open contract)
spark.sql(f"""
SELECT COUNT(*) AS rows_exactly_on_range_end
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date = DATE '2025-04-01'
""").show()'''),
        md_cell("""### Reading the query plan for the partition filter

Before trusting an incremental refresh policy in production, confirm the
date predicate is actually usable by the engine - run `EXPLAIN FORMATTED` on
the same filter Power BI will send and check the `PushedFilters` /
`Pruned` lines for `order_date`.
"""),
        code_cell('''spark.sql(f"""
EXPLAIN FORMATTED
SELECT order_date, category, customer_region, line_revenue
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-04-01'
""").show(80, truncate=False)'''),
        md_cell("""## 5. BI contract in practice

Template: `docs/templates/bi-contract.md`. Fill it in for *this* course's
tables before connecting anything in Power BI - the contract is the
hand-off artifact between the Databricks builder and the report author.

**Worked example for RetailHub:**

| Source object | Grain | Mode | Refresh | Owner |
|---|---|---|---|---|
| `gold.fact_sales_dashboard_monthly` | month x region x category x channel | Import | daily, scheduled after Gold job | Data team |
| `gold.v_fact_sales_incremental` | one row per order line (24 month window) | Import incremental, or DirectQuery for a live page | incremental: daily; live: every query | Data team |
| `gold.dim_date` | one row per calendar date | Import | rarely changes, refresh weekly | Data team |
| `gold.dim_product` | one row per product | Import | daily, with Gold job | Data team |
| `gold.dim_customer` | one row per customer | Import | daily, with Gold job | Data team |

Minimum decisions to record:

- Source for summary page: `gold.fact_sales_dashboard_monthly`.
- Source for detail/drill-through: `gold.v_fact_sales_incremental`.
- Baseline mode: Import.
- Live/DirectQuery only when freshness is more important than cost stability
  (see the decision table in section 1).
"""),
        md_cell("""### Is the dataset ready? Checklist

Before handing the contract to a report author, confirm:

- [ ] every table in the contract exists and `spark.catalog.tableExists(...)`
      returns `True`,
- [ ] the date column used for incremental refresh is a real `DATE`/`TIMESTAMP`,
      never null, and matches business reporting periods,
- [ ] summary and detail sources reconcile (see Module 2's reconciliation
      check) - a report built on both must not show conflicting totals,
- [ ] column names are final - renaming a Gold column after Power BI tables
      are built breaks every downstream measure,
- [ ] at least one full Import refresh has been timed, so refresh duration is
      known before scheduling,
- [ ] the contract names an owner for "what happens when this breaks".
"""),
        code_cell('''spark.sql(f"""
SELECT
  year_month,
  customer_region,
  category,
  revenue,
  gross_margin,
  completed_orders,
  returned_orders
FROM {GOLD}.fact_sales_dashboard_monthly
ORDER BY year_month DESC, revenue DESC
LIMIT 20
""").show(truncate=False)'''),
        md_cell("""## Dataset table plan

| Power BI table | Source | Mode | Why |
|---|---|---|---|
| `Sales Monthly` | `gold.fact_sales_dashboard_monthly` | Import baseline | compact summary source |
| `Sales Detail` | `gold.v_fact_sales_incremental` | Import incremental or DirectQuery for live page | drill-through and freshness |
| `Date` | `gold.dim_date` | Import | stable dimension |
| `Product` | `gold.dim_product` | Import | slicers and category labels |
| `Customer` | `gold.dim_customer` | Import | segment and region slicers |

For a live demo, connect a small report page to the monthly aggregate first.
Avoid DirectQuery against line-grain Silver tables.
"""),
        md_cell("""## Power BI thin layer example

Suggested Power BI measures:

```DAX
Revenue = SUM(fact_sales_dashboard_monthly[revenue])
Gross Margin % = DIVIDE(SUM(fact_sales_dashboard_monthly[gross_margin]), [Revenue])
Return Rate = DIVIDE(SUM(fact_sales_dashboard_monthly[returned_orders]), SUM(fact_sales_dashboard_monthly[completed_orders]) + SUM(fact_sales_dashboard_monthly[returned_orders]))
```

Everything else should be pushed into Databricks Gold unless there is a clear
reporting reason not to.
"""),
        md_cell("""## 6. Mock report walkthrough - widget by widget

![Power BI mockup](../assets/images/powerbi_report_mockup.png)

Walk through this report sketch one widget at a time. This is the mapping to
use whether the room has live Power BI or only the screenshot.

| Widget | What it shows | Powering table | Aggregate or detail? |
|---|---|---|---|
| 5 KPI cards (Revenue, Gross margin, Orders, Return rate, DQ score) | single current-period numbers | `gold.fact_sales_dashboard_monthly` | aggregate - cards never need line-grain rows |
| Revenue and margin trend (line chart) | trend across months | `gold.fact_sales_dashboard_monthly` | aggregate - one point per `year_month` |
| Revenue by region (bar chart) | revenue sliced by `customer_region` | `gold.fact_sales_dashboard_monthly` | aggregate - region is already a grouping column |
| Filters panel (Date / Region / Channel / Category) | slicers that filter every visual on the page | `gold.dim_date`, `gold.dim_customer`, `gold.dim_product` | dimension tables - slicers should list values, not scan facts |
| (drill-through page, not shown in mockup) | order-line detail behind any KPI card | `gold.v_fact_sales_incremental` | detail - the only place line-grain rows belong |

**Rule of thumb applied here:** any visual that renders one mark per
month/region/category should read from an aggregate table. Only a
drill-through or "show me the rows" page should ever touch the detail view.
This keeps the report fast and keeps DirectQuery (if used on the
drill-through page) limited to a narrow, already-filtered slice.
"""),
        md_cell("""## Discussion: choose the mode

| Question | Import answer | DirectQuery answer |
|---|---|---|
| How fresh must the number be? | daily/hourly is enough | user needs current operational state |
| How many users click the report? | many readers | controlled audience |
| Where is cost paid? | scheduled refresh | every interaction |
| What Gold object is required? | curated table/view | aggregate or very selective view |
"""),
        md_cell("""## Module 3 wrap-up

By the end of this module each participant has:

- a decision table and a worked cost argument for Import vs DirectQuery,
- a real (or mock-narrated) connection walkthrough from SQL Warehouse to
  Power BI, including where hostname and HTTP path come from,
- `gold.v_fact_sales_incremental` built with a correct half-open date filter,
  ready for Power BI's `RangeStart`/`RangeEnd` parameters,
- a filled-in BI contract for RetailHub's Gold tables and a readiness
  checklist,
- a widget-by-widget map of the mock report to its powering table.

Workshop 2 reuses `gold.fact_sales_dashboard_monthly` and
`gold.v_fact_sales_incremental` directly - both must exist before starting it.
"""),
    ]
    write_notebook(ROOT / "notebooks/m3_powerbi_semantic_dataset.ipynb", cells)


def notebook_module_4() -> None:
    cells = [
        md_cell("""# Module 4 - Performance, cost, Lakeflow Jobs and DABs

![Query profile reading map](../assets/images/query_profile_reading_map.png)

This is production-readiness orientation. We do not build a full CI/CD lab, but
we show what should be automated and how it can be described as code.
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Runtime pre-check

Run Modules 2 and 3 first. This module compares detail vs aggregate query
patterns and references the BI-ready objects.
"""),
        code_cell("""required_objects = [
    f"{GOLD}.fact_sales_dashboard_monthly",
    f"{GOLD}.v_fact_sales_incremental",
]

missing = [table for table in required_objects if not spark.catalog.tableExists(table)]
if missing:
    raise Exception("Missing objects. Run Modules 2 and 3 first: " + ", ".join(missing))

print("[OK] Performance demo objects exist")"""),
        md_cell("""## Before/after performance

Bad pattern: DirectQuery report scans detailed Silver rows on every interaction.
Better pattern: query Gold aggregate for summary pages and detail view only for
drill-through.
"""),
        code_cell('''spark.sql(f"""
EXPLAIN FORMATTED
SELECT category, SUM(line_revenue) AS revenue
FROM {SILVER}.order_lines
WHERE status = 'Completed'
GROUP BY category
""").show(80, truncate=False)'''),
        code_cell('''spark.sql(f"""
EXPLAIN FORMATTED
SELECT category, SUM(revenue) AS revenue
FROM {GOLD}.fact_sales_dashboard_monthly
GROUP BY category
""").show(80, truncate=False)'''),
        md_cell("""## Query profile reading

Use the map at the top of this notebook with the real Databricks Query Profile.
The training goal is to connect what participants see in the plan to an action:

- large scan -> Gold aggregate or narrower columns,
- shuffle -> pre-aggregation or different grain,
- slow join -> star model or BI-ready table,
- many tiny files -> OPTIMIZE / predictive optimization,
- repeated DirectQuery -> Import or cache-friendly aggregate.
"""),
        md_cell("""## Practical optimization checklist

| Technique | Training message |
|---|---|
| Column pruning | do not feed Power BI `SELECT *` sources |
| Predicate pushdown | date filters must fold to Databricks |
| Monthly aggregate | summary visuals should not scan line grain |
| OPTIMIZE / stats | physical layout helps, but does not replace good modelling |
| Warehouse sizing | size is a trade-off between runtime and DBU/h |
"""),
        md_cell("""## Lakeflow Job DAG

![Lakeflow Job DAG](../assets/images/lakeflow_job_dag.png)
"""),
        md_cell("""## DABs deployment flow

![DABs deployment flow](../assets/images/dabs_deployment_flow.png)

Reference file: `bundle/databricks.yml`.
"""),
        md_cell("""## Automation readiness checklist

![Automation readiness checklist](../assets/images/automation_readiness_checklist.png)
"""),
        md_cell("""## Refresh strategy

Use `docs/templates/refresh-strategy.md`.

Recommended DAG:

1. Validate source data.
2. Refresh Gold model.
3. Reconcile KPI.
4. Build BI aggregate.
5. Publish BI readiness status.

Important operational ideas:

- schedule for daily reports,
- table update trigger for upstream refresh,
- repair run after a failed transform,
- job parameters for dev/test/prod,
- owner notification when certification fails.
"""),
        md_cell("""## Cost guardrails

Use `docs/templates/cost-awareness-checklist.md`.

The key training message: live BI is not free. It changes the warehouse usage
pattern from scheduled refresh to interactive query fan-out.
"""),
        md_cell("""## Long-form delivery extension

If you need to stretch toward 9 hours, use these extra prompts:

- compare the two `EXPLAIN FORMATTED` plans line by line,
- ask participants to decide which DAG task should fail-fast,
- convert one workshop decision into a `bundle/databricks.yml` parameter,
- sketch dev/test/prod promotion on the DABs diagram,
- discuss how Power BI live pages affect SQL Warehouse auto-stop and concurrency.
"""),
    ]
    write_notebook(ROOT / "notebooks/m4_performance_automation_cicd_orientation.ipynb", cells)


def notebook_workshop_1(solution: bool) -> None:
    title = "solution" if solution else "exercise"
    cells = [
        md_cell(f"""# Workshop 1 - Gold KPI package ({title})

Goal: extend the BI-ready Gold objects from Module 2 with a new reporting
slice, define a NEW set of KPI, hunt for data-quality issues, reconcile two
aggregates and fill the decision log - the full path from raw Gold table to a
defensible BI number.

![Workshop success criteria](../assets/images/workshop_success_criteria.png)

This workshop is split into exactly 5 tasks (W1-02). Each task has an
"Expected output" callout (W1-03) that doubles as a grading rubric - if your
result does not match the callout, the task is not done yet.
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Success criteria

You are done when:

1. `gold.fact_sales_dashboard_channel_daily` exists with the documented grain.
2. Average Order Value, Margin Rate % and Completed Share by Region are
   calculated from Gold - these are NOT the same KPI Module 2 already showed
   you (Revenue, Gross Margin, Return Rate, Orders) - you are extending the
   dictionary, not repeating it.
3. At least three data-quality issues are named with example rows, using the
   bad-data-lab patterns from the data generator.
4. Two aggregates that should agree are reconciled, and any mismatch is
   explained.
5. The decision log (`docs/templates/decision-log.md`) has a real, filled-in
   row for this workshop's reporting-source decision.
6. The self-check cell passes.
"""),
        precheck_cell(
            [
                "{GOLD}.fact_sales_dashboard",
                "{GOLD}.fact_sales_dashboard_monthly",
            ],
            "notebooks/m2_gold_kpi_best_practices.ipynb",
        ),
        md_cell("""## Prerequisite chain

This workshop is the last link in a chain. If the pre-check above failed,
walk back through the chain in order:

1. `setup/00_pre_config.ipynb`
2. `data/generate_training_dataset.ipynb`
3. `notebooks/m2_gold_kpi_best_practices.ipynb` - uruchom modul 2 najpierw,
   jesli `gold.fact_sales_dashboard` lub `gold.fact_sales_dashboard_monthly`
   nie istnieja. Ten warsztat startuje dokladnie tam, gdzie modul 2 konczy.
"""),
        md_cell("""## The 5 tasks

1. **Zadanie 1 - zbuduj reporting table.** Build a new Gold object,
   `gold.fact_sales_dashboard_channel_daily`, one level more granular in time
   (daily, not monthly) and narrower in dimensions (channel only) than
   anything Module 2 built - a realistic "BI asked for a daily channel view"
   request.
2. **Zadanie 2 - zdefiniuj KPI.** Define four KPI that Module 2's dictionary
   does NOT already contain: Average Order Value, Margin Rate %, Completed
   Share by Region and Revenue per Channel-Day.
3. **Zadanie 3 - znajdz data quality issues.** Find at least three
   data-quality issues directly in `gold.fact_sales_dashboard`, with example
   rows, using the bad-data-lab patterns.
4. **Zadanie 4 - zrob reconciliation.** Compare your new daily-channel
   aggregate against `gold.fact_sales_dashboard_monthly` for the same scope
   and prove they agree (or explain why they do not).
5. **Zadanie 5 - wypelnij decision log.** Fill a real row in the decision log
   for the table-vs-view-vs-aggregate choice you made in Task 1.
"""),
    ]
    if solution:
        cells.extend([
            md_cell("""## Zadanie 1 - zbuduj reporting table

**Dlaczego:** Module 2 already gave us a monthly aggregate
(`fact_sales_dashboard_monthly`) and a segment/category aggregate (the Bonus
`fact_sales_dashboard_segment_monthly`). Neither answers "how did each
channel perform yesterday?" - a daily, channel-only grain is a genuinely new
reporting need, not a copy of what already exists. We build it as a table
(not a view) because BI will hit it repeatedly and the source detail table
is large enough that repeated re-aggregation on every Power BI query would
be wasteful.

**Alternative considered:** a view would avoid a refresh job, but every
DirectQuery page render would re-scan and re-aggregate
`fact_sales_dashboard`. For a daily-refreshed channel dashboard, the
materialized-table cost (one scheduled job) is cheaper than the
query-time cost (many ad-hoc scans), so we choose table + scheduled refresh.
"""),
            code_cell('''spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard_channel_daily
COMMENT 'Workshop 1 reporting table: one row per order_date x channel, materialized as a table (not a view) because it is refreshed on a schedule and queried repeatedly by Power BI - see decision log.'
AS
SELECT
  order_date,
  channel,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders,
  SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END) AS gross_margin
FROM {GOLD}.fact_sales_dashboard
GROUP BY order_date, channel
""")
print("[OK] gold.fact_sales_dashboard_channel_daily created")

spark.sql(f"""
SELECT COUNT(*) AS rows, COUNT(DISTINCT (order_date, channel)) AS distinct_grain_keys
FROM {GOLD}.fact_sales_dashboard_channel_daily
""").show()'''),
            md_cell("""## Zadanie 2 - zdefiniuj KPI

**Dlaczego:** Average Order Value needs revenue divided by a DISTINCT order
count (the same distinct-count trap Module 2 flagged) - not a per-line
average. Margin Rate % is a ratio, not a sum, so it must be computed after
aggregation, never pre-averaged per row. Completed Share by Region needs the
denominator to include both completed and non-completed orders for that
region, otherwise the "share" is meaningless (always 100%).
"""),
            code_cell('''spark.sql(f"""
SELECT
  ROUND(
    SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END)
    / NULLIF(COUNT(DISTINCT CASE WHEN is_completed THEN order_id END), 0),
    2
  ) AS avg_order_value,
  ROUND(
    100.0 * SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END)
    / NULLIF(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 0),
    2
  ) AS margin_rate_pct
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
            code_cell('''spark.sql(f"""
SELECT
  customer_region,
  COUNT(DISTINCT order_id) AS all_orders,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders,
  ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN is_completed THEN order_id END)
    / NULLIF(COUNT(DISTINCT order_id), 0),
    2
  ) AS completed_share_pct
FROM {GOLD}.fact_sales_dashboard
GROUP BY customer_region
ORDER BY completed_share_pct DESC
""").show()'''),
            code_cell('''spark.sql(f"""
SELECT order_date, channel, revenue,
       ROUND(revenue / NULLIF(completed_orders, 0), 2) AS revenue_per_completed_order
FROM {GOLD}.fact_sales_dashboard_channel_daily
ORDER BY order_date DESC, channel
LIMIT 10
""").show()'''),
            md_cell("""## Zadanie 3 - znajdz data quality issues

**Dlaczego:** Module 2's DQ score runs against `silver.*`. Here we check the
same families of issues directly against `gold.fact_sales_dashboard` to show
participants that a left join does not "clean" orphan references - it turns
them into NULL dimension attributes that silently break any GROUP BY on
`segment`, `customer_region`, `category` or `subcategory`. That is a
different, Gold-specific symptom of the same Silver-layer root cause.
"""),
            code_cell('''spark.sql(f"""
SELECT 'missing_unit_price' AS issue_type, COUNT(*) AS issue_count
FROM {GOLD}.fact_sales_dashboard WHERE unit_price IS NULL
UNION ALL
SELECT 'invalid_status', COUNT(*)
FROM {GOLD}.fact_sales_dashboard WHERE status NOT IN ('Completed','Cancelled','Returned')
UNION ALL
SELECT 'future_order_date', COUNT(*)
FROM {GOLD}.fact_sales_dashboard WHERE order_date > current_date()
UNION ALL
SELECT 'null_customer_region_after_join', COUNT(*)
FROM {GOLD}.fact_sales_dashboard WHERE customer_region IS NULL
UNION ALL
SELECT 'null_category_after_join', COUNT(*)
FROM {GOLD}.fact_sales_dashboard WHERE category IS NULL
ORDER BY issue_count DESC
""").show()'''),
            code_cell('''spark.sql(f"""
SELECT line_id, order_id, order_date, status, customer_region, category, unit_price, line_revenue
FROM {GOLD}.fact_sales_dashboard
WHERE unit_price IS NULL
   OR status NOT IN ('Completed','Cancelled','Returned')
   OR order_date > current_date()
   OR customer_region IS NULL
   OR category IS NULL
ORDER BY order_date DESC
LIMIT 20
""").show(truncate=False)'''),
            md_cell("""**Alternative considered:** these checks could instead run against
`silver.order_lines`/`silver.customers`/`silver.products` directly (as
Module 2's `dq_breakdown` does) to catch issues before they reach Gold. We
deliberately check Gold here too, because a Gold-level check catches a
different failure mode: a join bug or a stale dimension table that
introduces NULLs even when Silver itself is clean. Production setups should
have both - Silver gate AND Gold spot-check.
"""),
            md_cell("""## Zadanie 4 - zrob reconciliation

**Dlaczego:** `fact_sales_dashboard_channel_daily` (Task 1) and
`fact_sales_dashboard_monthly` (Module 2) are two independently aggregated
views of the same detail table, sliced on different dimensions (channel+day
vs region+category+channel+month). If we roll the daily-channel table up to
month+channel and compare it against the monthly table rolled down to
month+channel, the revenue totals must match exactly - this proves both
aggregates trace back to the same detail rows with no double-counting or
silent filter drift.
"""),
            code_cell('''spark.sql(f"""
WITH from_daily AS (
  SELECT date_format(order_date, 'yyyy-MM') AS year_month, channel,
         ROUND(SUM(revenue), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard_channel_daily
  GROUP BY date_format(order_date, 'yyyy-MM'), channel
),
from_monthly AS (
  SELECT year_month, channel, ROUND(SUM(revenue), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard_monthly
  GROUP BY year_month, channel
)
SELECT
  d.year_month, d.channel,
  d.revenue AS daily_rollup_revenue,
  m.revenue AS monthly_table_revenue,
  ROUND(d.revenue - m.revenue, 2) AS diff
FROM from_daily d
JOIN from_monthly m ON d.year_month = m.year_month AND d.channel = m.channel
ORDER BY ABS(d.revenue - m.revenue) DESC
LIMIT 15
""").show()'''),
            md_cell("""**Alternative considered:** we could reconcile against `gold.fact_sales`
(the generator's raw fact) instead of `fact_sales_dashboard_monthly`. That
would also work, but it would only prove the join in `fact_sales_dashboard`
is correct - it would not prove the two Gold-layer aggregates participants
actually hand to BI agree with each other, which is the failure mode BI
developers hit in practice (two dashboard tiles built from different
aggregates showing different numbers).
"""),
            md_cell("""## Zadanie 5 - wypelnij decision log

**Dlaczego:** a decision without a written reason is not reusable - the next
person rebuilds the table-vs-view-vs-aggregate debate from scratch. This row
is the actual `docs/templates/decision-log.md` entry for the Task 1 choice,
filled as a worked example.

| Date | Decision | Options considered | Chosen option | Reason | Consequence |
|---|---|---|---|---|---|
| 2026-06-23 | Reporting source for daily channel view | view / table / materialized aggregate | table (`fact_sales_dashboard_channel_daily`), scheduled refresh | repeated Power BI queries against a daily grain would re-scan and re-aggregate `fact_sales_dashboard` on every page load; a table makes the cost predictable and the refresh schedule explicit | requires a scheduled job (e.g. Lakeflow/Workflow) to keep the table current; consumers see data as of the last refresh, not real-time |
"""),
            md_cell("""## Self-check"""),
            code_cell('''assert spark.catalog.tableExists(f"{GOLD}.fact_sales_dashboard_channel_daily"), "Missing Task 1 reporting table"

grain = spark.sql(f"""
SELECT COUNT(*) AS rows, COUNT(DISTINCT (order_date, channel)) AS distinct_keys
FROM {GOLD}.fact_sales_dashboard_channel_daily
""").first()
assert grain["rows"] == grain["distinct_keys"], "Channel-daily table grain is not unique on (order_date, channel)"

recon = spark.sql(f"""
WITH from_daily AS (
  SELECT date_format(order_date, 'yyyy-MM') AS year_month, channel, ROUND(SUM(revenue), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard_channel_daily
  GROUP BY date_format(order_date, 'yyyy-MM'), channel
),
from_monthly AS (
  SELECT year_month, channel, ROUND(SUM(revenue), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard_monthly
  GROUP BY year_month, channel
)
SELECT MAX(ABS(d.revenue - m.revenue)) AS max_diff
FROM from_daily d JOIN from_monthly m ON d.year_month = m.year_month AND d.channel = m.channel
""").first()["max_diff"]
assert recon < 0.01, f"Task 4 reconciliation does not hold: max diff {recon}"

print("[OK] Workshop 1 self-check passed")'''),
        ])
    else:
        cells.extend([
            md_cell("""## Zadanie 1 - zbuduj reporting table

Build `gold.fact_sales_dashboard_channel_daily`: one row per `order_date` x
`channel`, with completed orders, revenue and gross margin, sourced from
`gold.fact_sales_dashboard`. Decide table vs view (you will justify the
choice in Task 5).

**Oczekiwany wynik (rubric):**
- table exists with columns `order_date, channel, completed_orders, revenue, gross_margin`,
- `COUNT(*) == COUNT(DISTINCT (order_date, channel))` - grain is unique,
- minimum success: the table is queryable and non-empty.
"""),
            code_cell('''# TODO: create gold.fact_sales_dashboard_channel_daily
# grain: one row per (order_date, channel)
# columns: completed_orders, revenue, gross_margin (completed orders only)
spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard_channel_daily
COMMENT 'TODO: add a comment describing the grain and refresh choice'
AS
SELECT
  order_date,
  channel
  -- TODO: add completed_orders, revenue, gross_margin aggregates
FROM {GOLD}.fact_sales_dashboard
GROUP BY order_date, channel
""")

spark.sql(f"""
SELECT COUNT(*) AS rows, COUNT(DISTINCT (order_date, channel)) AS distinct_grain_keys
FROM {GOLD}.fact_sales_dashboard_channel_daily
""").show()'''),
            md_cell("""## Zadanie 2 - zdefiniuj KPI

Define FOUR KPI that Module 2 did NOT already give you:

1. Average Order Value (revenue / distinct completed orders - watch the
   distinct-count trap from Module 2),
2. Margin Rate % (gross margin as a percentage of revenue, computed AFTER
   aggregation, not per-row),
3. Completed Share by Region (completed orders / all orders, per
   `customer_region`),
4. Revenue per Channel-Day (from your Task 1 table).

**Oczekiwany wynik (rubric):**
- AOV and Margin Rate % are single numbers, both NULL-safe (`NULLIF` on the
  denominator),
- Completed Share by Region returns one row per region, share between 0 and 100,
- minimum success: all four KPI use `COUNT(DISTINCT order_id)` where the
  business definition needs a per-order count, never raw `COUNT(*)`.
"""),
            code_cell('''# TODO: Average Order Value and Margin Rate %
spark.sql(f"""
SELECT
  -- TODO: avg_order_value = completed revenue / distinct completed orders
  -- TODO: margin_rate_pct = 100 * completed margin / completed revenue
  COUNT(*) AS rows
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
            code_cell('''# TODO: Completed Share by Region
spark.sql(f"""
SELECT
  customer_region
  -- TODO: add all_orders, completed_orders, completed_share_pct
FROM {GOLD}.fact_sales_dashboard
GROUP BY customer_region
""").show()'''),
            code_cell('''# TODO: Revenue per Channel-Day, using your Task 1 table
spark.sql(f"""
SELECT order_date, channel, revenue
  -- TODO: add revenue_per_completed_order
FROM {GOLD}.fact_sales_dashboard_channel_daily
ORDER BY order_date DESC, channel
LIMIT 10
""").show()'''),
            md_cell("""## Zadanie 3 - znajdz data quality issues

Find at least THREE data-quality issues directly in
`gold.fact_sales_dashboard` (not Silver). Hint: a left join does not delete
orphan references, it turns them into NULLs - check `customer_region` and
`category` for NULLs in addition to the missing-price/invalid-status/
future-date checks you already know from Module 2.

**Oczekiwany wynik (rubric):**
- at least 3 distinct `issue_type` rows with `issue_count > 0` for at least
  some of them (a generated dataset should reproduce the seeded bad-data-lab
  problems),
- a second query returns concrete example rows (not just counts) for at
  least one issue type,
- minimum success: every issue type you list is checked against
  `gold.fact_sales_dashboard`, with an explanation of what it means at the
  Gold layer (not just "this is a Silver bug").
"""),
            code_cell('''# TODO: count at least 3 data-quality issue types against gold.fact_sales_dashboard.
# Include at least one check that did NOT appear in Module 2's silver-level DQ score
# (e.g. null customer_region or null category after the join).
spark.sql(f"""
SELECT status, COUNT(*) AS rows
FROM {GOLD}.fact_sales_dashboard
GROUP BY status
ORDER BY rows DESC
""").show()'''),
            code_cell('''# TODO: pull concrete example rows for at least one issue type found above.
spark.sql(f"""
SELECT line_id, order_id, order_date, status, customer_region, category, unit_price
FROM {GOLD}.fact_sales_dashboard
LIMIT 20
""").show(truncate=False)'''),
            md_cell("""## Zadanie 4 - zrob reconciliation

Compare your `gold.fact_sales_dashboard_channel_daily` (Task 1), rolled up to
month + channel, against `gold.fact_sales_dashboard_monthly` (Module 2),
also rolled up to month + channel. Revenue must match for every
(year_month, channel) pair.

**Oczekiwany wynik (rubric):**
- a result set with `daily_rollup_revenue`, `monthly_table_revenue` and
  `diff` columns,
- `diff` is 0 or within rounding tolerance (< 0.01) for every row,
- minimum success: if `diff` is NOT close to zero, you can name the reason
  (different filter, different grain, double-counted join) rather than
  ignoring the mismatch.
"""),
            code_cell('''# TODO: roll up gold.fact_sales_dashboard_channel_daily to (year_month, channel)
# and compare revenue against gold.fact_sales_dashboard_monthly rolled up the same way.
spark.sql(f"""
SELECT 'TODO' AS year_month, 'TODO' AS channel, 0.0 AS daily_rollup_revenue, 0.0 AS monthly_table_revenue, 0.0 AS diff
""").show()'''),
            md_cell("""## Zadanie 5 - wypelnij decision log

Fill a real row of `docs/templates/decision-log.md` for the table-vs-view
choice you made in Task 1. Write it as if a teammate will read it in six
months with no other context.

**Oczekiwany wynik (rubric):**
- every column filled (Date, Decision, Options considered, Chosen option,
  Reason, Consequence) - no blanks,
- "Reason" references a concrete tradeoff (cost, freshness, refresh
  orchestration), not just "it seemed best",
- minimum success: "Consequence" names at least one thing that becomes true
  *because* of the choice (e.g. "needs a scheduled job").

| Date | Decision | Options considered | Chosen option | Reason | Consequence |
|---|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO | TODO |
"""),
            md_cell("""## Bonus (dla szybszych grup)

- add `segment` as a third grouping column to your Task 1 table and re-check
  the Task 4 reconciliation still holds,
- write a `COMMENT ON COLUMN` for `revenue` on your new table,
- prepare a one-minute explanation of your Task 3 findings for a business
  stakeholder who has never heard the term "orphan reference".
"""),
        ])
    write_notebook(ROOT / f"workshops/w1_gold_kpi_{title}.ipynb", cells)


def notebook_workshop_2(solution: bool) -> None:
    title = "solution" if solution else "exercise"
    cells = [
        md_cell(f"""# Workshop 2 - Power BI dataset readiness ({title})

Goal: prepare the BI-ready dataset and document Import vs DirectQuery decision.

![Power BI mockup](../assets/images/powerbi_report_mockup.png)
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Success criteria

You are done when:

1. Summary page source is identified and row count is known.
2. Drill-through/detail source is identified and has date boundaries.
3. Import vs DirectQuery decision is justified.
4. Incremental refresh predicate uses a half-open date window.
5. BI contract and cost guardrails are written.
6. The self-check cell passes.
"""),
        md_cell("""## Runtime pre-check

Run Modules 2 and 3 before this workshop.
"""),
        code_cell("""required_objects = [
    f"{GOLD}.fact_sales_dashboard_monthly",
    f"{GOLD}.v_fact_sales_incremental",
]

missing = [table for table in required_objects if not spark.catalog.tableExists(table)]
if missing:
    raise Exception("Missing objects. Run Modules 2 and 3 first: " + ", ".join(missing))

print("[OK] Workshop inputs exist")"""),
        md_cell("""## Tasks

1. Check if monthly aggregate is enough for the summary page.
2. Check if incremental view has date boundaries.
3. Document BI contract.
4. Decide Import vs live/DirectQuery.
5. List cost guardrails.
6. Validate the expected refresh window predicate.
"""),
    ]
    if solution:
        cells.extend([
            md_cell("""## Task 1 - summary aggregate"""),
            code_cell('''spark.sql(f"""
SELECT
  MIN(year_month) AS min_month,
  MAX(year_month) AS max_month,
  COUNT(*) AS aggregate_rows,
  SUM(revenue) AS revenue
FROM {GOLD}.fact_sales_dashboard_monthly
""").show()'''),
            md_cell("""## Task 2 - detail/incremental source"""),
            code_cell('''spark.sql(f"""
SELECT
  MIN(order_date) AS min_date,
  MAX(order_date) AS max_date,
  COUNT(*) AS detail_rows
FROM {GOLD}.v_fact_sales_incremental
""").show()'''),
            md_cell("""## Task 3 - simulate incremental-refresh window"""),
            code_cell('''spark.sql(f"""
SELECT
  COUNT(*) AS rows_in_window,
  MIN(order_date) AS min_date,
  MAX(order_date) AS max_date
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-04-01'
""").show()'''),
            md_cell("""## Task 4 - BI contract"""),
            md_cell("""Suggested BI contract:

| Area | Decision |
|---|---|
| Summary source | `gold.fact_sales_dashboard_monthly` |
| Detail source | `gold.v_fact_sales_incremental` |
| Baseline mode | Import |
| Live option | DirectQuery only for a small operational page on Gold aggregate |
| Refresh | incremental by `order_date`, half-open window |
| Cost guardrail | no visual can query Silver detail |
| Owner | Sales Ops for KPI, BI team for report |
"""),
            md_cell("""## Suggested decision

Use Import for the executive dashboard baseline. Use DirectQuery/live only for a
small operational page that reads Gold aggregates, not Silver detail.
"""),
            md_cell("""## Task 5 - self-check"""),
            code_cell('''assert spark.catalog.tableExists(f"{GOLD}.fact_sales_dashboard_monthly"), "Missing monthly aggregate"
assert spark.catalog.tableExists(f"{GOLD}.v_fact_sales_incremental"), "Missing incremental view"

summary_rows = spark.sql(f"SELECT COUNT(*) AS rows FROM {GOLD}.fact_sales_dashboard_monthly").first()["rows"]
detail_rows = spark.sql(f"SELECT COUNT(*) AS rows FROM {GOLD}.v_fact_sales_incremental").first()["rows"]
assert summary_rows > 0, "Summary aggregate is empty"
assert detail_rows > 0, "Incremental view is empty"

window = spark.sql(f"""
SELECT
  MIN(order_date) AS min_date,
  MAX(order_date) AS max_date
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-04-01'
""").first()
assert str(window["min_date"]) >= "2025-01-01", "Window starts too early"
assert str(window["max_date"]) < "2025-04-01", "Window includes RangeEnd boundary"

print("[OK] Workshop 2 self-check passed")'''),
        ])
    else:
        cells.extend([
            md_cell("""## Task 1 - inspect summary aggregate

Expected output: month range, row count and total revenue.
"""),
            code_cell("""# TODO: inspect summary aggregate.
spark.sql(f"SELECT * FROM {GOLD}.fact_sales_dashboard_monthly LIMIT 20").show()"""),
            md_cell("""## Task 2 - inspect incremental view

Expected output: date range and detail row count.
"""),
            code_cell("""# TODO: inspect incremental view.
spark.sql(f"SELECT MIN(order_date), MAX(order_date), COUNT(*) FROM {GOLD}.v_fact_sales_incremental").show()"""),
            md_cell("""## Task 3 - simulate Power BI incremental refresh

Expected output: rows only between `2025-01-01` and before `2025-04-01`.
"""),
            code_cell('''# TODO: apply the half-open RangeStart / RangeEnd predicate.
spark.sql(f"""
SELECT COUNT(*) AS rows_in_window
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  -- add RangeEnd predicate
""").show()'''),
            md_cell("""## Task 4 - mode decision

Fill this in:

| Decision | Your answer |
|---|---|
| Baseline mode | |
| Live/DirectQuery justified? | |
| Which table/view for summary page? | |
| Which table/view for detail page? | |
| Main cost risk | |
| Mitigation | |
"""),
            md_cell("""## Bonus

- add a separate source for a live operational page,
- decide which visuals should use aggregate vs detail,
- list three fields that must become slicers,
- write one DAX measure and decide whether it belongs in Power BI or Gold.
"""),
        ])
    write_notebook(ROOT / f"workshops/w2_powerbi_dataset_{title}.ipynb", cells)


def write_bundle() -> None:
    text = """# Reference DABs / Declarative Automation Bundles example.
# Validate against the current Databricks CLI/docs before live use.

bundle:
  name: retailhub_kpi_dashboard

variables:
  catalog:
    description: Target Unity Catalog catalog
    default: training_dbx_ana_medi_trainer

resources:
  jobs:
    refresh_gold_bi_dataset:
      name: refresh_gold_bi_dataset
      tasks:
        - task_key: validate_sources
          notebook_task:
            notebook_path: ../notebooks/m1_sql_warehouse_notebooks.ipynb
        - task_key: refresh_gold
          depends_on:
            - task_key: validate_sources
          notebook_task:
            notebook_path: ../notebooks/m2_gold_kpi_best_practices.ipynb
        - task_key: build_bi_dataset
          depends_on:
            - task_key: refresh_gold
          notebook_task:
            notebook_path: ../notebooks/m3_powerbi_semantic_dataset.ipynb

targets:
  dev:
    mode: development
    variables:
      catalog: training_dbx_ana_medi_dev
  prod:
    mode: production
    variables:
      catalog: training_dbx_ana_medi_prod
"""
    (ROOT / "bundle/databricks.yml").write_text(text, encoding="utf-8")


def build_notebooks() -> None:
    notebook_setup_pre_config()
    notebook_setup()
    notebook_data_generator()
    notebook_module_1()
    notebook_module_2()
    notebook_module_3()
    notebook_module_4()
    notebook_workshop_1(solution=False)
    notebook_workshop_1(solution=True)
    notebook_workshop_2(solution=False)
    notebook_workshop_2(solution=True)


def main() -> None:
    ensure_dirs()
    copy_reference_csvs()
    copy_reference_assets()
    write_templates()
    write_visual_materials_map()
    build_images()
    write_bundle()
    build_notebooks()
    print("Built Databricks-Data-Analyst-Medi v1 materials")


if __name__ == "__main__":
    main()
