import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "src-tauri/installer-assets"

# Color palette
TERRACOTTA = (204, 120, 92)
CREAM = (245, 239, 229)
CREAM2 = (247, 242, 234)
DARK_BROWN = (45, 36, 29)
WHITE = (255, 247, 242)
LIGHT_WHITE = (249, 233, 226)
MEDIUM_WHITE = (236, 199, 186)

APP_NAME_CN = "片刻"
APP_NAME_EN = "Pianke"
AUTHOR = "Alleyf & zhaoyue4810"
TAGLINE_1 = "AI 协助初筛与分组"
TAGLINE_2 = "把最终决定权"
TAGLINE_3 = "留给摄影师自己"
LOCAL_NOTE = "本地运行 · 不上传"
SHORT_DESC = "本地照片擂台式选片工具"

# Fonts
font_yahei_12 = ImageFont.truetype("msyh.ttc", 12)
font_yahei_14 = ImageFont.truetype("msyh.ttc", 14)
font_yahei_16 = ImageFont.truetype("msyh.ttc", 16)
font_yahei_18 = ImageFont.truetype("msyh.ttc", 18)
font_yahei_22 = ImageFont.truetype("msyh.ttc", 22)
font_yahei_26 = ImageFont.truetype("msyh.ttc", 26)
font_yahei_30 = ImageFont.truetype("msyh.ttc", 30)
font_segoe_10 = ImageFont.truetype("segoeui.ttf", 10)
font_segoe_12 = ImageFont.truetype("segoeui.ttf", 12)
font_segoe_14 = ImageFont.truetype("segoeui.ttf", 14)


def tb(text, font):
    """Return (w, h) of text."""
    tmp = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


# ── Icon drawing functions (all use top-left origin) ────────────────

def draw_camera_icon(draw, x, y, size, color):
    """Draw camera icon. Returns (w, h)."""
    s = size
    body_w, body_h = int(s * 1.4), int(s * 1.0)
    bump_w, bump_h = int(s * 0.5), int(s * 0.25)
    total_w = body_w
    total_h = body_h + bump_h
    cx = x + total_w // 2
    cy = y + bump_h + body_h // 2
    draw.rectangle([cx - body_w // 2, cy - body_h // 2,
                     cx + body_w // 2 - 1, cy + body_h // 2 - 1], fill=color)
    draw.rectangle([cx - bump_w // 2, cy - body_h // 2 - bump_h,
                     cx + bump_w // 2 - 1, cy - body_h // 2 - 1], fill=color)
    lens_r = int(s * 0.4)
    inner = DARK_BROWN if color == TERRACOTTA else WHITE
    draw.ellipse([cx - lens_r, cy - lens_r, cx + lens_r - 1, cy + lens_r - 1],
                  outline=color, fill=inner)
    lens_r2 = int(s * 0.2)
    draw.ellipse([cx - lens_r2, cy - lens_r2, cx + lens_r2 - 1, cy + lens_r2 - 1],
                  fill=color)
    return total_w, total_h


def draw_ai_icon(draw, x, y, size, color):
    """Draw AI neural network icon. Returns (size, size)."""
    s = size
    r = int(s * 0.5)
    cx, cy = x + r, y + r
    draw.ellipse([cx - r, cy - r, cx + r - 1, cy + r - 1], outline=color, width=2)
    nr = max(2, int(s * 0.12))
    draw.ellipse([cx - nr, cy - nr, cx + nr, cy + nr], fill=color)
    for angle in [0, 120, 240]:
        rad = math.radians(angle)
        nx = cx + int(r * 0.6 * math.cos(rad))
        ny = cy + int(r * 0.6 * math.sin(rad))
        nr2 = max(1, int(s * 0.07))
        draw.line([(cx, cy), (nx, ny)], fill=color, width=1)
        draw.ellipse([nx - nr2, ny - nr2, nx + nr2, ny + nr2], fill=color)
    return s, s


def draw_lock_icon(draw, x, y, size, color):
    """Draw lock icon. Returns (w, h)."""
    s = size
    body_w, body_h = int(s * 0.8), int(s * 0.6)
    arch_r = int(s * 0.3)
    total_h = body_h + arch_r + int(s * 0.05)
    total_w = body_w
    cx, cy = x + total_w // 2, y + total_h // 2
    draw.rectangle([cx - body_w // 2, cy - body_h // 2 + int(s * 0.15),
                     cx + body_w // 2 - 1, cy + body_h // 2 - 1], fill=color)
    draw.arc([cx - arch_r, cy - body_h // 2 - int(s * 0.05),
              cx + arch_r, cy - body_h // 2 + int(s * 0.35)],
             180, 0, fill=color, width=2)
    return total_w, total_h


def draw_photo_grid_icon(draw, x, y, size, color):
    """Draw 2x2 photo grid icon. Returns (w, h)."""
    s = size
    cell = int(s * 0.35)
    gap = int(s * 0.1)
    for row in range(2):
        for col in range(2):
            cx = x + col * (cell + gap)
            cy = y + row * (cell + gap)
            draw.rectangle([cx, cy, cx + cell - 1, cy + cell - 1], outline=color, width=1)
    total = 2 * cell + gap
    return total, total


# ── Sidebar content (used by nsis-sidebar and wix-dialog left) ─────

def draw_sidebar_content(draw, W, H):
    """Draw full sidebar on terracotta bg. Content: camera, name, tagline, author, local."""
    px = 20  # text left padding
    cx = W // 2
    y = 16

    # Camera icon (centered)
    cam_w, cam_h = draw_camera_icon(draw, cx - 15, y, 22, WHITE)
    y += cam_h + 12

    # App name
    tw, th = tb(APP_NAME_CN, font_yahei_30)
    draw.text((px, y), APP_NAME_CN, fill=WHITE, font=font_yahei_30)
    y += th + 4

    # English name
    draw.text((px, y), APP_NAME_EN, fill=LIGHT_WHITE, font=font_segoe_12)
    y += tb(APP_NAME_EN, font_segoe_12)[1] + 14

    # AI icon (centered)
    ai_size = 18
    draw_ai_icon(draw, cx - ai_size // 2, y, ai_size, LIGHT_WHITE)
    y += ai_size + 8

    # Taglines
    for line in [TAGLINE_1, TAGLINE_2, TAGLINE_3]:
        draw.text((px, y), line, fill=WHITE, font=font_yahei_16)
        y += tb(line, font_yahei_16)[1] + 4

    y += 14

    # Separator
    draw.line([(px, y), (W - px, y)], fill=MEDIUM_WHITE, width=1)
    y += 10

    # Author
    draw.text((px, y), "作者", fill=LIGHT_WHITE, font=font_yahei_12)
    y += tb("作者", font_yahei_12)[1] + 2
    draw.text((px, y), AUTHOR, fill=WHITE, font=font_segoe_12)
    y += tb(AUTHOR, font_segoe_12)[1] + 14

    # Lock + local note
    lock_size = 14
    tw_n, th_n = tb(LOCAL_NOTE, font_yahei_14)
    lock_w = int(lock_size * 0.8)
    lock_top = y + max(0, (th_n - lock_size) // 2)
    draw_lock_icon(draw, px, lock_top, lock_size, LIGHT_WHITE)
    nx = px + lock_w + 6
    draw.text((nx, y), LOCAL_NOTE, fill=WHITE, font=font_yahei_14)
    draw.line([(nx, y + th_n + 1), (nx + tw_n, y + th_n + 1)], fill=WHITE, width=1)


# ── Image generators ────────────────────────────────────────────────

def generate_nsis_sidebar():
    """NSIS sidebar: 164x314, full terracotta with complete branding."""
    W, H = 164, 314
    img = Image.new("RGB", (W, H), TERRACOTTA)
    draw = ImageDraw.Draw(img)
    draw_sidebar_content(draw, W, H)
    img.save(f"{OUTPUT_DIR}/nsis-sidebar.bmp", "BMP")
    print(f"Generated nsis-sidebar.bmp ({W}x{H})")


def generate_nsis_header():
    """NSIS header: 150x57, terracotta bg, camera + app name (vertical)."""
    W, H = 150, 57
    img = Image.new("RGB", (W, H), TERRACOTTA)
    draw = ImageDraw.Draw(img)

    cam_size = 20
    cam_w, cam_h = draw_camera_icon(draw, 0, 0, cam_size, WHITE)
    tw, th = tb(APP_NAME_CN, font_yahei_22)

    total = cam_h + 4 + th
    y = (H - total) // 2

    draw_camera_icon(draw, (W - cam_w) // 2, y, cam_size, WHITE)
    draw.text(((W - tw) // 2, y + cam_h + 4), APP_NAME_CN, fill=WHITE, font=font_yahei_22)

    img.save(f"{OUTPUT_DIR}/nsis-header.bmp", "BMP")
    print(f"Generated nsis-header.bmp ({W}x{H})")


def generate_wix_banner():
    """WIX banner: 493x58, terracotta stripe + cream, app name + short desc."""
    W, H = 493, 58
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    stripe_w = 13
    draw.rectangle([0, 0, stripe_w - 1, H - 1], fill=TERRACOTTA)

    # App name (large, centered) + short desc below
    tw_app, th_app = tb(APP_NAME_CN, font_yahei_26)
    tw_desc, th_desc = tb(SHORT_DESC, font_yahei_14)

    total = th_app + 2 + th_desc
    y = (H - total) // 2

    draw.text(((W - tw_app) // 2, y), APP_NAME_CN, fill=DARK_BROWN, font=font_yahei_26)
    draw.text(((W - tw_desc) // 2, y + th_app + 2), SHORT_DESC, fill=DARK_BROWN, font=font_yahei_14)

    # Photo grid decorative icon on far right
    grid_size = 24
    grid_w = 2 * int(grid_size * 0.35) + int(grid_size * 0.1)
    draw_photo_grid_icon(draw, W - grid_w - 16, (H - grid_w) // 2, grid_size, TERRACOTTA)

    img.save(f"{OUTPUT_DIR}/wix-banner.bmp", "BMP")
    print(f"Generated wix-banner.bmp ({W}x{H})")


def generate_wix_dialog():
    """WIX dialog: 493x312, terracotta sidebar + cream right panel.
    Left: full branding (sidebar content).
    Right: product description (NO duplication of sidebar content)."""
    W, H = 493, 312
    img = Image.new("RGB", (W, H), CREAM2)
    draw = ImageDraw.Draw(img)

    stripe_w = 164
    draw.rectangle([0, 0, stripe_w - 1, H - 1], fill=TERRACOTTA)

    # === LEFT SIDEBAR: full branding ===
    draw_sidebar_content(draw, stripe_w, H)

    # === RIGHT PANEL: product description (unique content, no duplicates) ===
    rx = stripe_w + 28  # right content left margin
    rw = W - stripe_w - 56  # right content width

    y = 24

    # App name (large, centered in right panel)
    tw, th = tb(APP_NAME_CN, font_yahei_30)
    draw.text((rx + (rw - tw) // 2, y), APP_NAME_CN, fill=DARK_BROWN, font=font_yahei_30)
    y += th + 4

    # English name
    tw, th = tb(APP_NAME_EN, font_segoe_14)
    draw.text((rx + (rw - tw) // 2, y), APP_NAME_EN, fill=TERRACOTTA, font=font_segoe_14)
    y += th + 16

    # Separator
    draw.line([(rx, y), (rx + rw, y)], fill=CREAM, width=1)
    y += 12

    # Product description paragraph (not repeated taglines)
    desc_lines = [
        "片刻是一款面向摄影师与摄影爱",
        "好者的本地照片选片工具。",
        "",
        "通过 AI 智能分析，自动完成",
        "失败片初筛与相似照片分组，",
        "将最终审美决定权留给你自己。",
        "",
        "所有处理均在本地完成，",
        "你的照片永远不会离开你的电脑。"
    ]
    for line in desc_lines:
        if line == "":
            y += 6
        else:
            draw.text((rx, y), line, fill=DARK_BROWN, font=font_yahei_16)
            y += tb(line, font_yahei_16)[1] + 2

    y += 14

    # Separator
    draw.line([(rx, y), (rx + rw, y)], fill=CREAM, width=1)
    y += 10

    # Feature list with small bullet icons
    features = [
        ("AI 智能初筛", "自动过滤模糊、闭眼等失败照片"),
        ("相似分组", "智能识别相似照片，减少选择困难"),
        ("擂台式选片", "两张对比快速决策，高效选片"),
        ("本地隐私", "所有数据本地处理，不上传云端"),
    ]

    for feat_title, feat_desc in features:
        # Small circle bullet
        bullet_r = 3
        bx = rx + 6
        by = y + 6
        draw.ellipse([bx - bullet_r, by - bullet_r, bx + bullet_r, by + bullet_r], fill=TERRACOTTA)

        # Title
        draw.text((rx + 14, y - 2), feat_title, fill=DARK_BROWN, font=font_yahei_14)
        y += tb(feat_title, font_yahei_14)[1] + 2

        # Description
        draw.text((rx + 14, y), feat_desc, fill=(100, 90, 80), font=font_yahei_12)
        y += tb(feat_desc, font_yahei_12)[1] + 8

    img.save(f"{OUTPUT_DIR}/wix-dialog.bmp", "BMP")
    print(f"Generated wix-dialog.bmp ({W}x{H})")


if __name__ == "__main__":
    generate_nsis_sidebar()
    generate_nsis_header()
    generate_wix_banner()
    generate_wix_dialog()
    print("Done!")
