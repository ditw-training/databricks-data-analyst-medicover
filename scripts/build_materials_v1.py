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
training, but small enough not to dominate the scenario.
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

orders.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.sales_orders")

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

# Controlled duplicate issue.
duplicates = order_lines.filter("line_id % 10007 = 0").withColumn("line_id", F.col("line_id") + F.lit(10000000))
order_lines = order_lines.unionByName(duplicates)

order_lines.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.order_lines")

print("Silver sales_orders:", orders.count())
print("Silver order_lines :", order_lines.count())"""),
        md_cell("""## 3. Starter Gold objects"""),
        code_cell('''spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_date AS
SELECT
  explode(sequence(to_date('2024-01-01'), to_date('2026-12-31'), interval 1 day)) AS date_key
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_date AS
SELECT
  date_key,
  year(date_key) AS year,
  month(date_key) AS month,
  date_format(date_key, 'yyyy-MM') AS year_month,
  quarter(date_key) AS quarter
FROM {GOLD}.dim_date
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_product AS
SELECT product_id, product_name, category, subcategory, unit_cost, unit_price, is_active
FROM {SILVER}.products
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.dim_customer AS
SELECT customer_id, customer_name, city, region, country, segment, created_date
FROM {SILVER}.customers
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales AS
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
CREATE OR REPLACE TABLE {GOLD}.kpi_daily AS
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
CREATE OR REPLACE TABLE {GOLD}.revenue_monthly AS
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
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Runtime pre-check

Run `data/generate_training_dataset.ipynb` before this notebook.
"""),
        code_cell("""required_tables = [
    f"{GOLD}.fact_sales",
    f"{GOLD}.dim_customer",
    f"{GOLD}.dim_product",
    f"{GOLD}.dim_date",
]

missing = [table for table in required_tables if not spark.catalog.tableExists(table)]
if missing:
    raise Exception("Missing Gold starter tables. Run data/generate_training_dataset first: " + ", ".join(missing))

print("[OK] Gold starter model exists")"""),
        md_cell("""## Why Gold exists

The business value of Gold is not "another table". It is:

- one agreed definition of revenue and margin,
- stable grain for Power BI,
- fewer expensive joins in reports,
- repeatable validation,
- a place to document ownership and refresh.
"""),
        md_cell("""## Business value case

![Gold business value](../assets/images/gold_business_value.png)

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
"""),
        md_cell("""## Kimball Gold model

![Kimball Gold model](../assets/images/kimball_gold_model.png)
"""),
        md_cell("""## Inspect the current Gold grain

The fact table should be one row per order line. Before we create BI objects,
we prove that grain and check whether joins can create fan-out.
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
        code_cell('''spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard AS
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
CREATE OR REPLACE TABLE {GOLD}.fact_sales_dashboard_monthly AS
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

print("[OK] Dashboard fact and aggregate created")'''),
        md_cell("""## Gold quality gate

![Gold quality gate](../assets/images/gold_quality_gate.png)

The checks below are intentionally business-facing. A red result does not
automatically mean "stop the project"; it means "write a decision".
"""),
        md_cell("""## KPI dictionary starter

The template lives in `docs/templates/kpi-dictionary.md`.
"""),
        md_cell("""## KPI definition flow

![KPI definition flow](../assets/images/kpi_definition_flow.png)

Suggested KPI dictionary rows:

| KPI | Business definition | SQL definition | Caveat |
|---|---|---|---|
| Revenue | completed line revenue after discount | `SUM(line_revenue) WHERE is_completed` | excludes returned/cancelled |
| Gross margin | completed revenue minus cost | `SUM(line_margin) WHERE is_completed` | depends on product cost quality |
| Return rate | returned orders / eligible orders | returned / (completed + returned) | distinct count grain matters |
"""),
        code_cell('''spark.sql(f"""
SELECT
  SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END) AS gross_margin,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders,
  COUNT(DISTINCT CASE WHEN is_returned THEN order_id END) AS returned_orders
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
        md_cell("""## Distinct-count trap

If the same order can contain products from many categories, summing order
counts by category can over-count orders. This is a good discussion point for
Power BI modelling and aggregation design.
"""),
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
        md_cell("""## Data quality score"""),
        code_cell('''quality = spark.sql(f"""
WITH checks AS (
  SELECT 'missing_price' AS check_name, COUNT(*) AS issue_count FROM {GOLD}.fact_sales_dashboard WHERE unit_price IS NULL
  UNION ALL
  SELECT 'invalid_status', COUNT(*) FROM {GOLD}.fact_sales_dashboard WHERE status NOT IN ('Completed','Cancelled','Returned')
  UNION ALL
  SELECT 'future_order_date', COUNT(*) FROM {GOLD}.fact_sales_dashboard WHERE order_date > current_date()
  UNION ALL
  SELECT 'missing_customer', COUNT(*) FROM {GOLD}.fact_sales_dashboard WHERE segment IS NULL
  UNION ALL
  SELECT 'missing_product', COUNT(*) FROM {GOLD}.fact_sales_dashboard WHERE category IS NULL
)
SELECT
  check_name,
  issue_count,
  CASE WHEN issue_count = 0 THEN 20 ELSE greatest(0, 20 - issue_count / 20) END AS score_component
FROM checks
""")

quality.createOrReplaceTempView("dq_components")
quality.show()
spark.sql(f"""
CREATE OR REPLACE TABLE {GOLD}.data_quality_score AS
SELECT
  current_timestamp() AS calculated_at,
  ROUND(SUM(score_component), 1) AS score
FROM dq_components
""")
spark.sql(f"SELECT * FROM {GOLD}.data_quality_score").show()'''),
        code_cell('''spark.sql(f"""
SELECT
  status,
  category,
  order_date,
  unit_price,
  line_revenue,
  line_margin
FROM {GOLD}.fact_sales_dashboard
WHERE unit_price IS NULL
   OR status NOT IN ('Completed','Cancelled','Returned')
   OR order_date > current_date()
ORDER BY order_date DESC
LIMIT 25
""").show(truncate=False)'''),
        md_cell("""## Lineage and discoverability

![Catalog Explorer lineage](../assets/images/source_catalog_explorer_lineage.png)

Trainer prompt:

- Which object would you certify?
- Which object would you hide from BI users?
- Which object should have the clearest owner and description?
"""),
        md_cell("""## Decision card: view vs table vs aggregate

| Option | Use when | Risk |
|---|---|---|
| View | logic is simple and source is small | repeated cost on every query |
| Table | stable BI source, scheduled refresh | needs orchestration |
| Aggregate | summary page or DirectQuery | lower detail, needs grain discipline |
"""),
        md_cell("""## Optional extension for longer delivery

If the group is strong or the course has 8-9 hours:

- add a Type 2 dimension example for customer segment changes,
- add table and column comments for BI discoverability,
- compare `fact_sales_dashboard` as a view vs table,
- create an additional aggregate by `year_month`, `segment` and `category`,
- ask participants to write the final KPI dictionary row by row.
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
        code_cell("""required_tables = [
    f"{GOLD}.fact_sales_dashboard",
    f"{GOLD}.fact_sales_dashboard_monthly",
]

missing = [table for table in required_tables if not spark.catalog.tableExists(table)]
if missing:
    raise Exception("Missing BI-ready Gold tables. Run Module 2 first: " + ", ".join(missing))

print("[OK] BI-ready Gold tables exist")"""),
        md_cell("""## Import vs live/DirectQuery

![Import vs DirectQuery](../assets/images/import_vs_directquery.png)
"""),
        md_cell("""## Power BI connector context

![Power BI DirectQuery connector](../assets/images/source_powerbi_directquery_connector.webp)

Use this as a visual walkthrough before opening Power BI Desktop. The key point
for analysts: connector mode is a modelling decision, not just a technical
checkbox.
"""),
        md_cell("""## Connection walkthrough

![Power BI connection walkthrough](../assets/images/powerbi_connection_walkthrough.png)

Trainer notes:

- show where SQL Warehouse Server hostname and HTTP path live,
- explain authentication before discussing tables,
- select only Gold objects,
- pick Import first unless a live use case is explicit.
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
        md_cell("""## Incremental refresh design

![Incremental refresh](../assets/images/incremental_refresh_range.png)

Power BI uses `RangeStart` and `RangeEnd` parameters. The recommended date
filter is half-open:

```sql
WHERE order_date >= RangeStart
  AND order_date <  RangeEnd
```

This avoids double-counting rows that fall exactly on a boundary.
"""),
        code_cell('''spark.sql(f"""
SELECT
  COUNT(*) AS rows_in_window,
  MIN(order_date) AS min_date,
  MAX(order_date) AS max_date
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-04-01'
""").show()'''),
        code_cell('''spark.sql(f"""
EXPLAIN FORMATTED
SELECT order_date, category, customer_region, line_revenue
FROM {GOLD}.v_fact_sales_incremental
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-04-01'
""").show(80, truncate=False)'''),
        md_cell("""## BI contract

Use `docs/templates/bi-contract.md`.

Minimum decisions:

- Source for summary page: `gold.fact_sales_dashboard_monthly`.
- Source for detail/drill-through: `gold.v_fact_sales_incremental`.
- Baseline mode: Import.
- Live/DirectQuery only when freshness is more important than cost stability.
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
        md_cell("""## Report layout walkthrough

Use `assets/images/powerbi_report_mockup.png` as the target report sketch:

- KPI cards at the top,
- revenue/margin trend as primary visual,
- region/category slices,
- filters that map to Gold columns,
- no hidden complex transformations in Power Query.
"""),
        md_cell("""## Discussion: choose the mode

| Question | Import answer | DirectQuery answer |
|---|---|---|
| How fresh must the number be? | daily/hourly is enough | user needs current operational state |
| How many users click the report? | many readers | controlled audience |
| Where is cost paid? | scheduled refresh | every interaction |
| What Gold object is required? | curated table/view | aggregate or very selective view |
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

Goal: build a BI-ready Gold object, define KPI, validate data quality and write
the decision log.

![Workshop success criteria](../assets/images/workshop_success_criteria.png)
"""),
        code_cell("""%run ../setup/00_setup"""),
        md_cell("""## Success criteria

You are done when:

1. `gold.fact_sales_dashboard` exists and has documented grain.
2. Revenue, Gross Margin and Return Rate are calculated from Gold.
3. Detail totals reconcile with the monthly aggregate.
4. At least three data-quality issues are named with example rows.
5. A view/table/aggregate decision is justified.
6. The self-check cell passes.
"""),
        md_cell("""## Runtime pre-check

Run Module 2 before this workshop. The workshop starts from the BI-ready Gold
objects created there.
"""),
        code_cell("""required_tables = [
    f"{GOLD}.fact_sales_dashboard",
    f"{GOLD}.fact_sales_dashboard_monthly",
]

missing = [table for table in required_tables if not spark.catalog.tableExists(table)]
if missing:
    raise Exception("Missing tables. Run Module 2 first: " + ", ".join(missing))

print("[OK] Workshop inputs exist")"""),
        md_cell("""## Tasks

1. Build or inspect `gold.fact_sales_dashboard`.
2. Define Revenue, Gross Margin and Return Rate.
3. Find at least three data-quality issues.
4. Decide whether the reporting source should be a view, table or aggregate.
5. Fill the KPI dictionary and decision log templates.
6. Prepare a short BI contract paragraph for Power BI.
"""),
    ]
    if solution:
        cells.extend([
            md_cell("""## Task 1 - inspect grain"""),
            code_cell('''spark.sql(f"""
SELECT
  COUNT(*) AS rows,
  COUNT(DISTINCT line_id) AS distinct_line_ids,
  COUNT(*) - COUNT(DISTINCT line_id) AS duplicate_line_ids
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
            md_cell("""## Task 2 - KPI definitions"""),
            code_cell('''spark.sql(f"""
SELECT
  SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END) AS revenue,
  SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END) AS gross_margin,
  COUNT(DISTINCT CASE WHEN is_returned THEN order_id END) AS returned_orders,
  COUNT(DISTINCT CASE WHEN is_completed THEN order_id END) AS completed_orders,
  ROUND(
    COUNT(DISTINCT CASE WHEN is_returned THEN order_id END)
    / NULLIF(
        COUNT(DISTINCT CASE WHEN is_completed THEN order_id END)
        + COUNT(DISTINCT CASE WHEN is_returned THEN order_id END),
        0
      ),
    4
  ) AS return_rate
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
            md_cell("""## Task 3 - quality issues with evidence"""),
            code_cell('''spark.sql(f"""
SELECT 'missing_price' AS issue, COUNT(*) AS rows FROM {GOLD}.fact_sales_dashboard WHERE unit_price IS NULL
UNION ALL SELECT 'invalid_status', COUNT(*) FROM {GOLD}.fact_sales_dashboard WHERE status NOT IN ('Completed','Cancelled','Returned')
UNION ALL SELECT 'future_order_date', COUNT(*) FROM {GOLD}.fact_sales_dashboard WHERE order_date > current_date()
""").show()'''),
            code_cell('''spark.sql(f"""
SELECT line_id, order_id, order_date, status, category, unit_price, line_revenue
FROM {GOLD}.fact_sales_dashboard
WHERE unit_price IS NULL
   OR status NOT IN ('Completed','Cancelled','Returned')
   OR order_date > current_date()
ORDER BY order_date DESC
LIMIT 20
""").show(truncate=False)'''),
            md_cell("""## Task 4 - reconciliation"""),
            code_cell('''spark.sql(f"""
WITH detail AS (
  SELECT ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard
),
agg AS (
  SELECT ROUND(SUM(revenue), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard_monthly
)
SELECT detail.revenue AS detail_revenue, agg.revenue AS agg_revenue, detail.revenue - agg.revenue AS diff
FROM detail CROSS JOIN agg
""").show()'''),
            md_cell("""## Suggested decision

Use a table for `gold.fact_sales_dashboard` and an aggregate for summary report
pages. Avoid DirectQuery on Silver detail tables.
"""),
            md_cell("""## Suggested BI contract paragraph

The executive dashboard uses `gold.fact_sales_dashboard_monthly` for summary
pages and `gold.fact_sales_dashboard` for detail validation. Grain is one row
per month, customer region, category and channel in the aggregate. Revenue and
gross margin include completed orders only. DirectQuery must not read Silver
detail tables.
"""),
            md_cell("""## Self-check"""),
            code_cell('''assert spark.catalog.tableExists(f"{GOLD}.fact_sales_dashboard"), "Missing dashboard fact"
assert spark.catalog.tableExists(f"{GOLD}.fact_sales_dashboard_monthly"), "Missing monthly aggregate"

grain = spark.sql(f"""
SELECT COUNT(*) AS rows, COUNT(DISTINCT line_id) AS distinct_line_ids
FROM {GOLD}.fact_sales_dashboard
""").first()
assert grain["rows"] >= grain["distinct_line_ids"], "Unexpected grain result"

recon = spark.sql(f"""
WITH detail AS (
  SELECT ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard
),
agg AS (
  SELECT ROUND(SUM(revenue), 2) AS revenue
  FROM {GOLD}.fact_sales_dashboard_monthly
)
SELECT ABS(detail.revenue - agg.revenue) AS diff
FROM detail CROSS JOIN agg
""").first()["diff"]
assert recon < 0.01, f"Aggregate does not reconcile: {recon}"

print("[OK] Workshop 1 self-check passed")'''),
        ])
    else:
        cells.extend([
            md_cell("""## Task 1 - inspect grain

Expected output: row count, distinct `line_id`, and duplicate count.
"""),
            code_cell('''# TODO: inspect the grain of gold.fact_sales_dashboard.
spark.sql(f"""
SELECT
  COUNT(*) AS rows
  -- add COUNT(DISTINCT line_id) and duplicate calculation
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
            md_cell("""## Task 2 - calculate KPI

Expected output: Revenue, Gross Margin, Completed Orders, Returned Orders and
Return Rate.
"""),
            code_cell('''# TODO: calculate Revenue, Gross Margin and Return Rate from Gold.
spark.sql(f"""
SELECT
  -- add measures here
  COUNT(*) AS rows
FROM {GOLD}.fact_sales_dashboard
""").show()'''),
            md_cell("""## Task 3 - find data-quality issues

Expected output: at least three issue names and counts.
"""),
            code_cell('''# TODO: find data-quality issues.
spark.sql(f"""
SELECT status, COUNT(*) AS rows
FROM {GOLD}.fact_sales_dashboard
GROUP BY status
ORDER BY rows DESC
""").show()'''),
            md_cell("""## Task 4 - reconcile detail with aggregate

Expected output: revenue difference should be zero or close to zero.
"""),
            code_cell('''# TODO: compare detail revenue with monthly aggregate revenue.
spark.sql(f"""
SELECT 'TODO' AS check_name, 0 AS diff
""").show()'''),
            md_cell("""## Task 5 - decision log

Fill this in:

| Decision | Your answer |
|---|---|
| Reporting source | |
| Why not Silver? | |
| Import vs DirectQuery default | |
| Accepted caveats | |
| Owner | |
"""),
            md_cell("""## Bonus

- add one more quality rule,
- add `segment` to the monthly aggregate,
- write a comment for the certified Gold object,
- prepare a one-minute explanation for a business stakeholder.
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
