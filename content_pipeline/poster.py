from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


_font_path: str | None = None


def _resolve_font_path() -> str | None:
    global _font_path

    if _font_path is not None:
        return _font_path

    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    ]

    for path in candidates:

        if Path(path).exists():
            _font_path = path
            return _font_path

    _font_path = ""
    return None


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = _resolve_font_path()
    return ImageFont.truetype(path, size=size) if path else ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for char in text:
        trial = current + char
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def create_poster(
    base_image_path: Path | None,
    output_path: Path,
    title: str,
    subtitle: str,
    price_text: str,
    brand: str = "BWS 印尼旅行",
) -> Path:
    width, height = 1024, 1536
    if base_image_path and base_image_path.exists():
        img = Image.open(base_image_path).convert("RGB")
        img.thumbnail((width, height))
        canvas = Image.new("RGB", (width, height), "#f6f1e8")
        x = (width - img.width) // 2
        y = (height - img.height) // 2
        canvas.paste(img, (x, y))
    else:
        canvas = Image.new("RGB", (width, height), "#f7efe3")
        bg = ImageDraw.Draw(canvas)
        for y in range(height):
            if y < height * 0.48:
                ratio = y / (height * 0.48)
                r = int(126 + ratio * 88)
                g = int(194 + ratio * 36)
                b = int(214 + ratio * 20)
            elif y < height * 0.62:
                ratio = (y - height * 0.48) / (height * 0.14)
                r = int(35 + ratio * 14)
                g = int(139 + ratio * 52)
                b = int(162 + ratio * 38)
            else:
                ratio = (y - height * 0.62) / (height * 0.38)
                r = int(226 + ratio * 18)
                g = int(199 + ratio * 22)
                b = int(145 + ratio * 40)
            bg.line((0, y, width, y), fill=(r, g, b))
        bg.rectangle((0, int(height * 0.56), width, int(height * 0.59)), fill="#f8f2df")
        bg.polygon(
            [(0, int(height * 0.43)), (260, int(height * 0.36)), (520, int(height * 0.44)), (780, int(height * 0.34)), (width, int(height * 0.42)), (width, int(height * 0.51)), (0, int(height * 0.51))],
            fill="#4f7d73",
        )
        bg.polygon(
            [(80, int(height * 0.64)), (290, int(height * 0.58)), (540, int(height * 0.63)), (790, int(height * 0.57)), (width, int(height * 0.62)), (width, int(height * 0.68)), (0, int(height * 0.68)), (0, int(height * 0.62))],
            fill="#e8d198",
        )

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, height * 0.58, width, height), fill=(0, 0, 0, 150))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(76)
    subtitle_font = _load_font(38)
    price_font = _load_font(48)
    brand_font = _load_font(30)

    margin = 72
    y = int(height * 0.63)
    for line in _wrap_text(draw, title, title_font, width - margin * 2)[:3]:
        draw.text((margin, y), line, fill="white", font=title_font)
        y += 92

    y += 20
    for line in _wrap_text(draw, subtitle, subtitle_font, width - margin * 2)[:2]:
        draw.text((margin, y), line, fill="#f6e7c8", font=subtitle_font)
        y += 52

    if price_text:
        draw.text((margin, height - 190), price_text, fill="#ffd166", font=price_font)
    draw.text((margin, height - 96), brand, fill="white", font=brand_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, quality=95)
    return output_path
