from PIL import Image, ImageDraw, ImageFont

font_yahei_12 = ImageFont.truetype("msyh.ttc", 12)
font_yahei_14 = ImageFont.truetype("msyh.ttc", 14)
font_yahei_16 = ImageFont.truetype("msyh.ttc", 16)
font_yahei_22 = ImageFont.truetype("msyh.ttc", 22)
font_yahei_26 = ImageFont.truetype("msyh.ttc", 26)
font_yahei_30 = ImageFont.truetype("msyh.ttc", 30)
font_segoe_12 = ImageFont.truetype("segoeui.ttf", 12)
font_segoe_14 = ImageFont.truetype("segoeui.ttf", 14)

def tb(text, font):
    tmp = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(tmp)
    b = d.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]

def cam_h(size):
    return int(size * 1.0) + int(size * 0.25)

print("=" * 60)
print("SIDEBAR (164x314)")
print("=" * 60)
y = 16
hc = cam_h(22)
print(f"  y={y}-{y+hc}: Camera (h={hc})")
y += hc + 12
tw, th = tb("片刻", font_yahei_30)
print(f"  y={y}-{y+th}: '片刻' (h={th}, w={tw})")
y += th + 4
tw, th = tb("Pianke", font_segoe_12)
print(f"  y={y}-{y+th}: 'Pianke' (h={th})")
y += th + 14
print(f"  y={y}-{y+18}: AI icon (h=18)")
y += 18 + 8
for line in ["AI 协助初筛与分组", "把最终决定权", "留给摄影师自己"]:
    tw, th = tb(line, font_yahei_16)
    print(f"  y={y}-{y+th}: '{line}' (w={tw})")
    y += th + 4
y += 14
print(f"  y={y}: Separator")
y += 10
tw, th = tb("作者", font_yahei_12)
print(f"  y={y}-{y+th}: '作者'")
y += th + 2
tw, th = tb("Alleyf & zhaoyue4810", font_segoe_12)
print(f"  y={y}-{y+th}: Author (w={tw})")
y += th + 14
tw_n, th_n = tb("本地运行 · 不上传", font_yahei_14)
print(f"  y={y}-{y+max(th_n,14)}: Lock+note (w={tw_n})")
y += max(th_n, 14) + 4
print(f"  FINAL y={y}/314  {'OK' if y <= 304 else 'OVERFLOW!'}")

print()
print("=" * 60)
print("WIX DIALOG RIGHT PANEL (x=192, w=237, H=312)")
print("=" * 60)
y = 24
tw, th = tb("片刻", font_yahei_30)
print(f"  y={y}-{y+th}: '片刻' (h={th})")
y += th + 4
tw, th = tb("Pianke", font_segoe_14)
print(f"  y={y}-{y+th}: 'Pianke'")
y += th + 16
print(f"  y={y}: Separator")
y += 12
desc_lines = [
    "片刻是一款面向摄影师与摄影爱",
    "好者的本地照片选片工具。",
    "", "通过 AI 智能分析，自动完成",
    "失败片初筛与相似照片分组，",
    "将最终审美决定权留给你自己。",
    "", "所有处理均在本地完成，",
    "你的照片永远不会离开你的电脑。"
]
for line in desc_lines:
    if line == "":
        y += 6
    else:
        tw, th = tb(line, font_yahei_16)
        print(f"  y={y}-{y+th}: '{line}' (w={tw})")
        y += th + 2
y += 14
print(f"  y={y}: Separator")
y += 10
features = [
    ("AI 智能初筛", "自动过滤模糊、闭眼等失败照片"),
    ("相似分组", "智能识别相似照片，减少选择困难"),
    ("擂台式选片", "两张对比快速决策，高效选片"),
    ("本地隐私", "所有数据本地处理，不上传云端"),
]
for ft, fd in features:
    tw_t, th_t = tb(ft, font_yahei_14)
    tw_d, th_d = tb(fd, font_yahei_12)
    print(f"  y={y}-{y+th_t+th_d+2}: [{ft}] {fd}")
    y += th_t + 2 + th_d + 8
print(f"  FINAL y={y}/312  {'OK' if y <= 302 else 'OVERFLOW!'}")

print()
print("=" * 60)
print("NSIS HEADER (150x57)")
print("=" * 60)
cam_sz = 20
hc = cam_h(cam_sz)
tw, th = tb("片刻", font_yahei_22)
total = hc + 4 + th
y = (57 - total) // 2
print(f"  Camera: y={y}-{y+hc}, x={(150-int(cam_sz*1.4))//2}")
print(f"  App:    y={y+hc+4}-{y+hc+4+th}, x={(150-tw)//2}")
print(f"  Gap={4}, Fits: {'OK' if y+total <= 57 else 'OVERFLOW'}")

print()
print("=" * 60)
print("WIX BANNER (493x58)")
print("=" * 60)
tw_a, th_a = tb("片刻", font_yahei_26)
tw_d, th_d = tb("本地照片擂台式选片工具", font_yahei_14)
total = th_a + 2 + th_d
y = (58 - total) // 2
print(f"  App: y={y}-{y+th_a}, w={tw_a}")
print(f"  Desc: y={y+th_a+2}, w={tw_d}")
print(f"  Fits: {'OK' if total <= 58 else 'OVERFLOW'}")
