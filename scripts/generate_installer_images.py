import os
import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "src-tauri/installer-assets"

# ---------------------------------------------------------------------
# Visual direction
# ---------------------------------------------------------------------
# 1. Keep the original font files and font family choices unchanged.
# 2. Replace repeated camera / AI / grid icons with one calmer brand mark.
# 3. Use stronger whitespace, warm cards, and installer-friendly hierarchy.
# 4. Draw at 3x resolution and downsample to BMP for smoother edges.

SCALE = 3
RESAMPLE = getattr(Image, "Resampling", Image).LANCZOS

# Color palette
TERRACOTTA = (204, 120, 92)
TERRACOTTA_DARK = (172, 84, 64)
TERRACOTTA_LIGHT = (224, 148, 116)
CREAM = (245, 239, 229)
CREAM2 = (247, 242, 234)
CARD = (255, 250, 244)
CARD_WARM = (250, 242, 235)
DARK_BROWN = (45, 36, 29)
MUTED_BROWN = (112, 94, 82)
SOFT_BROWN = (150, 124, 108)
WHITE = (255, 247, 242)
LIGHT_WHITE = (249, 233, 226)
MEDIUM_WHITE = (236, 199, 186)
LINE = (226, 216, 203)
SHADOW = (230, 218, 205)

APP_NAME_CN = "片刻"
APP_NAME_EN = "Pianke"
AUTHOR = "Alleyf & zhaoyue4810"

# Copywriting can be optimized, but the original meaning is kept.
TAGLINE_HERO = "AI 先筛，摄影师终选"
TAGLINE_SUB = "本地照片筛选与相似分组"
TAGLINE_NOTE = "更快找到值得保留的瞬间"
LOCAL_NOTE = "本地运行 · 不上传"
SHORT_DESC = "本地 AI 照片筛选与相似分组工具"

# Fonts: keep the same font files as the previous version.
# On Windows, these are usually available from the system font directory.
font_yahei_12 = ImageFont.truetype("msyh.ttc", 12 * SCALE)
font_yahei_13 = ImageFont.truetype("msyh.ttc", 13 * SCALE)
font_yahei_14 = ImageFont.truetype("msyh.ttc", 14 * SCALE)
font_yahei_15 = ImageFont.truetype("msyh.ttc", 15 * SCALE)
font_yahei_16 = ImageFont.truetype("msyh.ttc", 16 * SCALE)
font_yahei_18 = ImageFont.truetype("msyh.ttc", 18 * SCALE)
font_yahei_20 = ImageFont.truetype("msyh.ttc", 20 * SCALE)
font_yahei_22 = ImageFont.truetype("msyh.ttc", 22 * SCALE)
font_yahei_26 = ImageFont.truetype("msyh.ttc", 26 * SCALE)
font_yahei_30 = ImageFont.truetype("msyh.ttc", 30 * SCALE)
font_segoe_10 = ImageFont.truetype("segoeui.ttf", 10 * SCALE)
font_segoe_11 = ImageFont.truetype("segoeui.ttf", 11 * SCALE)
font_segoe_12 = ImageFont.truetype("segoeui.ttf", 12 * SCALE)
font_segoe_14 = ImageFont.truetype("segoeui.ttf", 14 * SCALE)


def px(value):
    return int(round(value * SCALE))


def box(values):
    return [px(v) for v in values]


def tb(text, font):
    """Return logical-pixel (w, h) of text."""
    tmp = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=font)
    return (b[2] - b[0]) / SCALE, (b[3] - b[1]) / SCALE


def new_canvas(W, H, fill):
    return Image.new("RGB", (px(W), px(H)), fill)


def save_bmp(img, W, H, name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = img.resize((W, H), RESAMPLE)
    out.save(f"{OUTPUT_DIR}/{name}", "BMP")
    print(f"Generated {name} ({W}x{H})")


def draw_text(draw, xy, text, fill, font):
    draw.text((px(xy[0]), px(xy[1])), text, fill=fill, font=font)


def draw_centered_text(draw, x, y, width, text, fill, font):
    tw, _ = tb(text, font)
    draw_text(draw, (x + (width - tw) / 2, y), text, fill, font)


def draw_line(draw, points, fill, width=1):
    draw.line([(px(x), px(y)) for x, y in points], fill=fill, width=px(width))


def draw_rect(draw, bbox, fill, outline=None, width=1):
    draw.rectangle(box(bbox), fill=fill, outline=outline, width=px(width))


def draw_round(draw, bbox, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box(bbox), radius=px(radius), fill=fill, outline=outline, width=px(width))


def draw_ellipse(draw, bbox, fill=None, outline=None, width=1):
    draw.ellipse(box(bbox), fill=fill, outline=outline, width=px(width))


def draw_vertical_gradient(img, W, H, top, bottom):
    draw = ImageDraw.Draw(img)
    total_h = px(H)
    for y in range(total_h):
        t = y / max(1, total_h - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line([(0, y), (px(W), y)], fill=color)


def draw_soft_orbits(draw, cx, cy, radius, color):
    """Subtle decorative rings; not an icon, just quiet brand texture."""
    for i, alpha_like in enumerate([0, 1, 2]):
        r = radius + i * 13
        c = tuple(min(255, int(color[j] + i * 14)) for j in range(3))
        draw_ellipse(draw, (cx - r, cy - r, cx + r, cy + r), outline=c, width=1)


def draw_brand_mark(draw, x, y, size, color, fill=None, accent=None):
    """Single abstract photo-selection mark used as the app's visual symbol."""
    fill = fill if fill is not None else CARD
    accent = accent if accent is not None else TERRACOTTA_LIGHT

    # Back photo sheet
    draw_round(
        draw,
        (x + size * 0.08, y + size * 0.18, x + size * 0.78, y + size * 0.82),
        size * 0.12,
        fill=None,
        outline=accent,
        width=1,
    )

    # Front selected sheet
    draw_round(
        draw,
        (x + size * 0.23, y + size * 0.06, x + size * 0.94, y + size * 0.72),
        size * 0.12,
        fill=fill,
        outline=color,
        width=2,
    )

    # Minimal image horizon inside the selected sheet
    ix1 = x + size * 0.33
    iy1 = y + size * 0.34
    ix2 = x + size * 0.83
    iy2 = y + size * 0.61
    draw_line(draw, [(ix1, iy2), (ix1 + size * 0.16, iy1 + size * 0.07),
                     (ix1 + size * 0.29, iy1 + size * 0.18),
                     (ix2, iy1)], fill=color, width=1)
    draw_ellipse(
        draw,
        (x + size * 0.66, y + size * 0.18, x + size * 0.76, y + size * 0.28),
        fill=accent,
    )

    # A small selection dot: suggests "chosen" without repeating a checkmark icon.
    draw_ellipse(
        draw,
        (x + size * 0.75, y + size * 0.58, x + size * 0.86, y + size * 0.69),
        fill=color,
    )


def draw_pill(draw, x, y, text, font, fill, fg, pad_x=9, pad_y=4, outline=None):
    tw, th = tb(text, font)
    w = tw + pad_x * 2
    h = th + pad_y * 2
    draw_round(draw, (x, y, x + w, y + h), h / 2, fill=fill, outline=outline, width=1)
    draw_text(draw, (x + pad_x, y + pad_y - 1), text, fg, font)
    return w, h


def draw_feature_card(draw, x, y, w, number, title, desc):
    draw_round(draw, (x + 1, y + 2, x + w + 1, y + 50), 12, fill=SHADOW)
    draw_round(draw, (x, y, x + w, y + 48), 12, fill=CARD, outline=LINE, width=1)

    draw_text(draw, (x + 13, y + 10), number, TERRACOTTA, font_segoe_12)
    draw_text(draw, (x + 44, y + 8), title, DARK_BROWN, font_yahei_14)
    draw_text(draw, (x + 44, y + 28), desc, MUTED_BROWN, font_yahei_12)


def draw_footer_local(draw, x, y, width):
    """Privacy footer with no lock icon; avoids visual repetition."""
    text = LOCAL_NOTE
    tw, th = tb(text, font_yahei_13)
    pill_w = tw + 26
    draw_round(
        draw,
        (x + (width - pill_w) / 2, y, x + (width + pill_w) / 2, y + th + 13),
        13,
        fill=(188, 96, 73),
        outline=TERRACOTTA_LIGHT,
        width=1,
    )
    draw_text(draw, (x + (width - tw) / 2, y + 5), text, WHITE, font_yahei_13)


# ---------------------------------------------------------------------
# Shared sidebar / hero composition
# ---------------------------------------------------------------------

def draw_sidebar_content(draw, W, H, compact=False):
    """Terracotta brand block with one brand mark, clear type, and calm footer."""
    draw_soft_orbits(draw, W - 18, 28, 30, (211, 130, 101))

    y = 24 if not compact else 18
    mark_size = 52 if not compact else 42
    draw_brand_mark(
        draw,
        (W - mark_size) / 2 - 2,
        y,
        mark_size,
        WHITE,
        fill=(211, 126, 96),
        accent=MEDIUM_WHITE,
    )
    y += mark_size + (15 if not compact else 10)

    draw_centered_text(draw, 0, y, W, APP_NAME_CN, WHITE, font_yahei_30)
    y += tb(APP_NAME_CN, font_yahei_30)[1] + 3
    draw_centered_text(draw, 0, y, W, APP_NAME_EN, LIGHT_WHITE, font_segoe_12)
    y += tb(APP_NAME_EN, font_segoe_12)[1] + 22

    # Hero copy: one strong line + two supporting lines.
    draw_centered_text(draw, 0, y, W, TAGLINE_HERO, WHITE, font_yahei_16)
    y += 25
    draw_centered_text(draw, 0, y, W, TAGLINE_SUB, LIGHT_WHITE, font_yahei_13)
    y += 19
    draw_centered_text(draw, 0, y, W, TAGLINE_NOTE, LIGHT_WHITE, font_yahei_13)

    # Bottom author and local note. Kept light so the installer UI has breathing room.
    footer_y = H - (74 if not compact else 66)
    draw_line(draw, [(22, footer_y), (W - 22, footer_y)], MEDIUM_WHITE, width=1)
    footer_y += 12
    draw_centered_text(draw, 0, footer_y, W, "作者", LIGHT_WHITE, font_yahei_12)
    footer_y += 16
    draw_centered_text(draw, 0, footer_y, W, AUTHOR, WHITE, font_segoe_11)
    draw_footer_local(draw, 12, H - 29, W - 24)


# ---------------------------------------------------------------------
# Image generators
# ---------------------------------------------------------------------

def generate_nsis_sidebar():
    """NSIS sidebar: 164x314."""
    W, H = 164, 314
    img = new_canvas(W, H, TERRACOTTA)
    draw_vertical_gradient(img, W, H, TERRACOTTA_DARK, TERRACOTTA)
    draw = ImageDraw.Draw(img)

    # Tiny warm highlight at bottom left for depth.
    draw_ellipse(draw, (-58, H - 40, 74, H + 92), fill=(197, 105, 81))
    draw_sidebar_content(draw, W, H)

    save_bmp(img, W, H, "nsis-sidebar.bmp")


def generate_nsis_header():
    """NSIS header: 150x57. Typography-first, no repeated camera/grid icon."""
    W, H = 150, 57
    img = new_canvas(W, H, CREAM)
    draw = ImageDraw.Draw(img)

    draw_rect(draw, (0, 0, 6, H), fill=TERRACOTTA)
    draw_round(draw, (16, 11, 134, 46), 10, fill=CARD, outline=LINE, width=1)

    draw_centered_text(draw, 16, 8, 118, APP_NAME_CN, DARK_BROWN, font_yahei_22)
    draw_centered_text(draw, 16, 33, 118, "Pianke Setup", TERRACOTTA, font_segoe_10)

    save_bmp(img, W, H, "nsis-header.bmp")


def generate_wix_banner():
    """WIX banner: 493x58. Clean brand banner with one small mark and aligned text."""
    W, H = 493, 58
    img = new_canvas(W, H, CREAM2)
    draw = ImageDraw.Draw(img)

    draw_rect(draw, (0, 0, W, H), fill=CREAM2)
    draw_rect(draw, (0, 0, 11, H), fill=TERRACOTTA)
    draw_ellipse(draw, (W - 82, -54, W + 32, 60), fill=(242, 230, 219))

    mark_size = 34
    draw_brand_mark(draw, 26, 12, mark_size, TERRACOTTA, fill=CARD, accent=SOFT_BROWN)

    draw_text(draw, (75, 9), APP_NAME_CN, DARK_BROWN, font_yahei_22)
    draw_text(draw, (127, 16), APP_NAME_EN, TERRACOTTA, font_segoe_12)
    draw_text(draw, (75, 35), SHORT_DESC, MUTED_BROWN, font_yahei_13)

    draw_pill(draw, W - 133, 18, LOCAL_NOTE, font_yahei_12, CARD, TERRACOTTA, outline=LINE)

    save_bmp(img, W, H, "wix-banner.bmp")


def generate_wix_dialog():
    """WIX dialog: 493x312.
    Left: brand impression.
    Right: installer welcome + feature cards, no duplicated sidebar content.
    """
    W, H = 493, 312
    sidebar_w = 176

    img = new_canvas(W, H, CREAM2)
    draw = ImageDraw.Draw(img)

    # Background
    draw_rect(draw, (0, 0, W, H), fill=CREAM2)
    draw_rect(draw, (sidebar_w, 0, W, H), fill=CREAM2)
    draw_round(draw, (sidebar_w + 16, 17, W - 14, H - 17), 18, fill=CARD_WARM)
    draw_round(draw, (sidebar_w + 16, 17, W - 14, H - 17), 18, fill=None, outline=LINE, width=1)

    # Left brand block
    left_img = img.crop((0, 0, px(sidebar_w), px(H)))
    draw_vertical_gradient(left_img, sidebar_w, H, TERRACOTTA_DARK, TERRACOTTA)
    img.paste(left_img, (0, 0))
    draw = ImageDraw.Draw(img)

    draw_ellipse(draw, (-48, -42, 102, 108), fill=(185, 90, 68))
    draw_ellipse(draw, (100, H - 104, 240, H + 42), fill=(212, 130, 100))
    draw_sidebar_content(draw, sidebar_w, H, compact=True)

    # Right panel
    rx = sidebar_w + 34
    rw = W - sidebar_w - 58
    y = 30

    draw_text(draw, (rx, y), "欢迎使用片刻安装向导", DARK_BROWN, font_yahei_20)
    y += 30
    draw_text(draw, (rx, y), "在安装前，先认识一下这款为摄影师准备的", MUTED_BROWN, font_yahei_13)
    y += 18
    draw_text(draw, (rx, y), "本地照片筛选工具。", MUTED_BROWN, font_yahei_13)
    y += 24

    draw_line(draw, [(rx, y), (rx + rw, y)], LINE, width=1)
    y += 15

    draw_feature_card(draw, rx, y, rw, "01", "先把失败片筛掉", "模糊、闭眼、明显失焦优先处理")
    y += 58
    draw_feature_card(draw, rx, y, rw, "02", "再把相似片分组", "相近构图自动归类，减少重复浏览")
    y += 58
    draw_feature_card(draw, rx, y, rw, "03", "最后由你决定", "AI 只做辅助，保留你的审美判断")
    y += 62

    # Privacy banner
    draw_round(draw, (rx, y, rx + rw, y + 38), 13, fill=(247, 235, 226), outline=LINE, width=1)
    # draw_text(draw, (rx + 15, y + 9), "照片处理均在本地完成，不会上传云端。", DARK_BROWN, font_yahei_13)

    save_bmp(img, W, H, "wix-dialog.bmp")


if __name__ == "__main__":
    generate_nsis_sidebar()
    generate_nsis_header()
    generate_wix_banner()
    generate_wix_dialog()
    print("Done!")
