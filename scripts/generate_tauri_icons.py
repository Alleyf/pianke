from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "src-tauri" / "icons"


def build_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = int(size * 0.08)
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=int(size * 0.22),
        fill=(197, 113, 79, 255),
    )
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (int(size * 0.24), int(size * 0.18), int(size * 0.72), int(size * 0.66)),
        fill=(255, 255, 255, 72),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(max(2, size // 28)))
    img.alpha_composite(glow)

    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (int(size * 0.26), int(size * 0.30), int(size * 0.74), int(size * 0.67)),
        radius=int(size * 0.08),
        outline=(255, 255, 255, 255),
        width=max(2, size // 20),
    )
    draw.ellipse(
        (int(size * 0.40), int(size * 0.38), int(size * 0.60), int(size * 0.58)),
        outline=(255, 255, 255, 255),
        width=max(2, size // 26),
    )
    draw.rectangle(
        (int(size * 0.60), int(size * 0.24), int(size * 0.70), int(size * 0.30)),
        fill=(255, 255, 255, 255),
    )
    return img


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)

    sizes = {
        "32x32.png": 32,
        "128x128.png": 128,
        "128x128@2x.png": 256,
    }
    rendered = {}
    for name, size in sizes.items():
        img = build_icon(size)
        img.save(ICON_DIR / name)
        rendered[size] = img

    rendered[256].save(ICON_DIR / "icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    rendered[256].save(ICON_DIR / "icon.icns")
    print(f"Generated icons in {ICON_DIR}")


if __name__ == "__main__":
    main()
