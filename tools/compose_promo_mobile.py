from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PROMO = ROOT / "assets" / "promo"
SOURCE = ROOT / "Screenshot_20260711_130611_com.tencent.mm.jpg"
BG = PROMO / "mobile-poster-background.png"
QR = PROMO / "qr-user-provided.png"
CROP_OUT = PROMO / "mobile-page-crop.png"
OUT = PROMO / "typhoon-bavi-promo-mobile.png"

W, H = 1080, 1440
FONT_CN = r"C:\Windows\Fonts\msyh.ttc"
FONT_CN_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_LATIN = r"C:\Windows\Fonts\segoeuib.ttf"


def ft(path: str, size: int):
    return ImageFont.truetype(path, size=size)


def cover(im: Image.Image, target: tuple[int, int]) -> Image.Image:
    tw, th = target
    scale = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def rounded(im: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=radius, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask)
    return out


def shadow(base: Image.Image, box: tuple[int, int, int, int], radius=36, blur=30, alpha=180):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 10, y0 + 18, x1 + 10, y1 + 18), radius=radius, fill=(0, 0, 0, alpha))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


canvas = cover(Image.open(BG).convert("RGB"), (W, H)).convert("RGBA")

# Strengthen the clean left reading area while keeping the generated background visible.
left_shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(left_shade)
for x in range(650):
    a = int(155 * (1 - x / 650))
    sd.line((x, 0, x, H), fill=(2, 10, 27, a))
canvas.alpha_composite(left_shade)
draw = ImageDraw.Draw(canvas)

WHITE = (248, 251, 255, 255)
MUTED = (177, 204, 239, 255)
BLUE = (79, 170, 255, 255)
ORANGE = (255, 137, 45, 255)

# Header and hierarchy.
draw.rounded_rectangle((62, 58, 342, 108), radius=25, fill=(17, 64, 127, 220), outline=(88, 181, 255, 210), width=2)
draw.ellipse((82, 75, 98, 91), fill=ORANGE)
draw.text((112, 69), "浙江 · 台风实时信息", font=ft(FONT_CN_BOLD, 25), fill=WHITE)

draw.text((58, 154), "台风巴威", font=ft(FONT_CN_BOLD, 78), fill=WHITE)
draw.text((62, 257), "BAVI", font=ft(FONT_LATIN, 42), fill=BLUE)
draw.text((62, 320), "实时路径与浙江影响", font=ft(FONT_CN_BOLD, 34), fill=WHITE)
draw.text((63, 374), "路径、预警、影响，一屏掌握", font=ft(FONT_CN, 25), fill=MUTED)

# Feature list: compact, left aligned, no decorative clutter.
features = [
    ("01", "实时路径", "多机构预报路径与风圈"),
    ("02", "地市影响", "浙江 11 地市风险评估"),
    ("03", "官方预警", "预警信号与防御措施"),
    ("04", "定位查看", "附近风险与最近距离"),
]
y0 = 470
for i, (num, title, desc) in enumerate(features):
    y = y0 + i * 105
    draw.rounded_rectangle((61, y, 458, y + 82), radius=20, fill=(5, 28, 63, 190), outline=(77, 151, 222, 95), width=2)
    draw.rounded_rectangle((79, y + 16, 129, y + 66), radius=15, fill=(24, 87, 164, 220))
    draw.text((91, y + 27), num, font=ft(FONT_LATIN, 18), fill=WHITE)
    draw.text((150, y + 12), title, font=ft(FONT_CN_BOLD, 27), fill=WHITE)
    draw.text((150, y + 48), desc, font=ft(FONT_CN, 19), fill=MUTED)

# Crop exactly below the WeChat status/title bar. Preserve the real mobile page UI.
mobile = Image.open(SOURCE).convert("RGB").crop((0, 145, 630, 1422))
mobile = ImageEnhance.Contrast(mobile).enhance(1.03)
mobile = ImageEnhance.Sharpness(mobile).enhance(1.12)
mobile.save(CROP_OUT, quality=96)

screen_w = 500
screen_h = round(screen_w * mobile.height / mobile.width)
mobile = mobile.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
mobile = rounded(mobile, 32)

# Device-like frame, deliberately simple so the actual page remains the focus.
fx, fy = 518, 126
frame_w, frame_h = 530, screen_h + 30
frame_box = (fx, fy, fx + frame_w, fy + frame_h)
shadow(canvas, frame_box, radius=42, blur=35, alpha=205)
draw.rounded_rectangle(frame_box, radius=42, fill=(3, 12, 27, 255), outline=(126, 191, 246, 175), width=3)
canvas.alpha_composite(mobile, (fx + 15, fy + 15))

# Small live indicator bridges the poster and the real screenshot.
draw.rounded_rectangle((792, 77, 1018, 119), radius=21, fill=(3, 20, 46, 220), outline=(83, 164, 236, 120), width=2)
draw.ellipse((814, 91, 828, 105), fill=(255, 93, 73, 255))
draw.text((842, 85), "实时数据持续更新", font=ft(FONT_CN_BOLD, 21), fill=WHITE)

# QR and call to action.
draw.text((61, 928), "扫码立即查看", font=ft(FONT_CN_BOLD, 40), fill=WHITE)
draw.text((63, 984), "打开实时路径与影响评估", font=ft(FONT_CN, 22), fill=MUTED)

qr = Image.open(QR).convert("RGB")
qr_card = (61, 1038, 377, 1316)
shadow(canvas, qr_card, radius=28, blur=20, alpha=150)
draw.rounded_rectangle(qr_card, radius=28, fill=(255, 255, 255, 255))
canvas.paste(qr, (77, 1054))

draw.rounded_rectangle((61, 1340, 420, 1392), radius=26, fill=(21, 81, 157, 220), outline=(89, 180, 255, 150), width=2)
draw.text((93, 1352), "tzti.pages.dev", font=ft(FONT_LATIN, 25), fill=WHITE)

draw.text((521, 1348), "数据仅供参考，请以当地防汛部门最新发布为准", font=ft(FONT_CN, 17), fill=(150, 182, 220, 255))

OUT.parent.mkdir(parents=True, exist_ok=True)
canvas.convert("RGB").save(OUT, quality=96, optimize=True)
print(OUT)
