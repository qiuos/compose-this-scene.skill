#!/usr/bin/env python3
"""Render crop and annotation previews for composition plans."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


SUPPORTED_GUIDES = {
    "thirds",
    "center",
    "diagonal",
    "diagonals",
    "golden",
    "golden_spiral",
    "crosshair",
}


def slugify(value: str, fallback: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return value or fallback


def load_font(size: int) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "Helvetica.ttc", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


def normalize_box(raw_box: list[float], width: int, height: int) -> tuple[int, int, int, int]:
    if len(raw_box) != 4:
        raise ValueError("crop must contain four numbers: [left, top, right, bottom]")

    left, top, right, bottom = [float(v) for v in raw_box]
    if max(abs(left), abs(top), abs(right), abs(bottom)) <= 1.0:
        left, right = left * width, right * width
        top, bottom = top * height, bottom * height

    left = max(0, min(width - 1, round(left)))
    right = max(1, min(width, round(right)))
    top = max(0, min(height - 1, round(top)))
    bottom = max(1, min(height, round(bottom)))

    if right <= left or bottom <= top:
        raise ValueError(f"invalid crop box after clamping: {(left, top, right, bottom)}")

    return left, top, right, bottom


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont) -> None:
    if not text:
        return
    x, y = xy
    bbox = draw.textbbox((x, y), text, font=font)
    pad = 6
    rect = (bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
    draw.rounded_rectangle(rect, radius=5, fill=(20, 20, 20, 220))
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)


def draw_guides(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], guides: list[str], color: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = box
    width = right - left
    height = bottom - top

    normalized = {guide.lower() for guide in guides}
    if "diagonals" in normalized:
        normalized.add("diagonal")

    if "thirds" in normalized:
        for i in (1, 2):
            x = left + width * i / 3
            y = top + height * i / 3
            draw.line([(x, top), (x, bottom)], fill=color, width=2)
            draw.line([(left, y), (right, y)], fill=color, width=2)

    if "center" in normalized or "crosshair" in normalized:
        cx = left + width / 2
        cy = top + height / 2
        draw.line([(cx, top), (cx, bottom)], fill=color, width=2)
        draw.line([(left, cy), (right, cy)], fill=color, width=2)

    if "diagonal" in normalized:
        draw.line([(left, top), (right, bottom)], fill=color, width=2)
        draw.line([(left, bottom), (right, top)], fill=color, width=2)

    if "golden" in normalized or "golden_spiral" in normalized:
        phi = 0.618
        x1 = left + width * phi
        x2 = right - width * phi
        y1 = top + height * phi
        y2 = bottom - height * phi
        draw.line([(x1, top), (x1, bottom)], fill=color, width=2)
        draw.line([(x2, top), (x2, bottom)], fill=color, width=2)
        draw.line([(left, y1), (right, y1)], fill=color, width=2)
        draw.line([(left, y2), (right, y2)], fill=color, width=2)


def draw_focus_points(
    draw: ImageDraw.ImageDraw,
    points: list[dict[str, Any]],
    original_size: tuple[int, int],
    crop_box: tuple[int, int, int, int],
    offset: tuple[int, int] = (0, 0),
    crop_relative: bool = False,
) -> None:
    original_w, original_h = original_size
    left, top, right, bottom = crop_box
    crop_w, crop_h = right - left, bottom - top
    font = load_font(max(12, min(original_w, original_h) // 55))

    for point in points:
        x = float(point.get("x", 0))
        y = float(point.get("y", 0))
        label = str(point.get("label", ""))

        if max(abs(x), abs(y)) <= 1.0:
            if crop_relative:
                px = x * crop_w
                py = y * crop_h
            else:
                px = x * original_w - left
                py = y * original_h - top
        else:
            px = x - left
            py = y - top

        px += offset[0]
        py += offset[1]
        radius = max(6, min(crop_w, crop_h) // 80)
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(255, 214, 10, 235), outline=(0, 0, 0, 220), width=2)
        if label:
            draw_label(draw, (int(px + radius + 6), int(py - radius)), label, font)


def render_annotated(original: Image.Image, variant: dict[str, Any], crop_box: tuple[int, int, int, int]) -> Image.Image:
    annotated = original.convert("RGBA")
    overlay = Image.new("RGBA", annotated.size, (0, 0, 0, 95))
    crop = annotated.crop(crop_box)
    overlay.paste(crop, crop_box)
    annotated = Image.alpha_composite(annotated, overlay)
    draw = ImageDraw.Draw(annotated, "RGBA")

    left, top, right, bottom = crop_box
    accent = (255, 214, 10, 245)
    draw.rectangle(crop_box, outline=accent, width=max(4, min(original.size) // 180))
    draw_guides(draw, crop_box, variant.get("guides", []), (255, 255, 255, 170))
    draw_focus_points(draw, variant.get("focus_points", []), original.size, crop_box)

    title = str(variant.get("title") or variant.get("id") or "Composition")
    font = load_font(max(16, min(original.size) // 40))
    label_y = max(12, top - font.size - 18) if hasattr(font, "size") else max(12, top - 34)
    draw_label(draw, (max(12, left), label_y), title, font)
    return annotated.convert("RGB")


def render_crop(original: Image.Image, variant: dict[str, Any], crop_box: tuple[int, int, int, int]) -> Image.Image:
    crop = original.crop(crop_box).convert("RGBA")
    draw = ImageDraw.Draw(crop, "RGBA")
    crop_local_box = (0, 0, crop.width, crop.height)
    draw_guides(draw, crop_local_box, variant.get("guides", []), (255, 255, 255, 150))
    draw_focus_points(draw, variant.get("focus_points", []), original.size, crop_box)
    return crop.convert("RGB")


def make_contact_sheet(items: list[dict[str, Any]], out_path: Path) -> None:
    if not items:
        return

    thumb_w = 420
    label_h = 64
    gap = 18
    cols = 2 if len(items) > 1 else 1
    rows = math.ceil(len(items) / cols)
    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * (thumb_w + label_h) + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (248, 248, 246))
    draw = ImageDraw.Draw(sheet)
    title_font = load_font(20)
    caption_font = load_font(14)

    for index, item in enumerate(items):
        row, col = divmod(index, cols)
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_w + label_h + gap)
        image = Image.open(item["crop_path"]).convert("RGB")
        image.thumbnail((thumb_w, thumb_w), Image.LANCZOS)
        frame = Image.new("RGB", (thumb_w, thumb_w), (232, 232, 228))
        frame.paste(image, ((thumb_w - image.width) // 2, (thumb_w - image.height) // 2))
        sheet.paste(frame, (x, y))
        draw.text((x, y + thumb_w + 8), item["title"], fill=(24, 24, 24), font=title_font)
        caption = item.get("caption", "")
        if caption:
            draw.text((x, y + thumb_w + 34), caption[:72], fill=(82, 82, 82), font=caption_font)

    sheet.save(out_path, quality=94)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render composition crop and annotation previews.")
    parser.add_argument("--image", required=True, help="Input image path.")
    parser.add_argument("--plan", required=True, help="JSON file containing composition variants.")
    parser.add_argument("--out-dir", required=True, help="Directory for generated previews.")
    parser.add_argument("--prefix", default="composition", help="Filename prefix.")
    args = parser.parse_args()

    image_path = Path(args.image).expanduser().resolve()
    plan_path = Path(args.plan).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    original = Image.open(image_path).convert("RGB")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    variants = plan.get("variants", [])
    if not isinstance(variants, list) or not variants:
        raise ValueError("plan must contain a non-empty 'variants' list")

    outputs: list[dict[str, Any]] = []
    for index, variant in enumerate(variants, start=1):
        if "crop" not in variant:
            raise ValueError(f"variant {index} is missing a crop box")

        invalid_guides = sorted(set(variant.get("guides", [])) - SUPPORTED_GUIDES)
        if invalid_guides:
            raise ValueError(f"variant {index} has unsupported guides: {', '.join(invalid_guides)}")

        crop_box = normalize_box(variant["crop"], *original.size)
        variant_id = slugify(str(variant.get("id") or variant.get("title") or index), f"option-{index}")
        stem = f"{args.prefix}_{index:02d}_{variant_id}"
        annotated_path = out_dir / f"{stem}_annotated.jpg"
        crop_path = out_dir / f"{stem}_crop.jpg"

        render_annotated(original, variant, crop_box).save(annotated_path, quality=94)
        render_crop(original, variant, crop_box).save(crop_path, quality=94)

        outputs.append(
            {
                "id": variant_id,
                "title": str(variant.get("title") or variant_id),
                "caption": str(variant.get("caption") or ""),
                "crop_box_px": list(crop_box),
                "annotated_path": str(annotated_path),
                "crop_path": str(crop_path),
            }
        )

    contact_sheet_path = out_dir / f"{args.prefix}_contact_sheet.jpg"
    make_contact_sheet(outputs, contact_sheet_path)

    result = {
        "image": str(image_path),
        "plan": str(plan_path),
        "contact_sheet": str(contact_sheet_path),
        "variants": outputs,
    }
    result_path = out_dir / "composition_outputs.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
