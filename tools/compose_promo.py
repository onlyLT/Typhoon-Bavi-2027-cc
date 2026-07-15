from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "promo"
BG_PATH = ASSET_DIR / "typhoon-poster-background.png"
SCREEN_PATH = ASSET_DIR / "site-preview.png"
QR_PAGE_PATH = ASSET_DIR / "qr-page.png"
QR_PATH = ASSET_DIR / "qr-tzti.png"
OUT_PATH = ASSET_DIR / "typhoon-bavi-promo.png"

W, H = 1080, 1440
FONT_CN = r"C:\Windows\Fonts\msyh.ttc"
FONT_CN_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_LATIN = r"C:\Windows\Fonts\segoeuib.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    sw, sh = image.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    image = image.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return image.crop((left, top, left + tw, top + th))


def rounded_image(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
    out = image.convert("RGBA")
    out.putalpha(mask)
    return out


def add_shadow(base: Image.Image, box: tuple[int, int, int, int], radius: int, blur: int, alpha: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0 + 12, x1, y1 + 12), radius=radius, fill=(0, 0, 0, alpha))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


bg = cover(Image.open(BG_PATH).convert("RGB"), (W, H)).convert("RGBA")

# Readability gradients while retaining the generated meteorological artwork.
shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
spx = shade.load()
for y in range(H):
    top_a = max(0, int(178 * (1 - y / 550))) if y < 550 else 0
    bottom_a = max(0, int(160 * ((y - 970) / 470))) if y > 970 else 0
    a = max(top_a, bottom_a)
    for x in range(W):
        spx[x, y] = (2, 10, 27, a)
bg.alpha_composite(shade)
draw = ImageDraw.Draw(bg)

white = (248, 251, 255, 255)
muted = (190, 211, 239, 255)
blue = (84, 174, 255, 255)
orange = (255, 145, 48, 255)

# Header and exact marketing copy.
draw.rounded_rectangle((62, 54, 347, 108), radius=27, fill=(18, 67, 128, 215), outline=(92, 187, 255, 210), width=2)
draw.ellipse((82, 73, 98, 89), fill=orange)
draw.text((112, 67), "浙江 · 台风实时信息", font=font(FONT_CN_BOLD, 27), fill=white)

draw.text((60, 137), "台风巴威", font=font(FONT_CN_BOLD, 94), fill=white, stroke_width=1, stroke_fill=(4, 21, 47, 180))
draw.text((64, 251), "BAVI", font=font(FONT_LATIN, 50), fill=blue)
draw.text((225, 263), "/  实时路径与浙江影响", font=font(FONT_CN_BOLD, 34), fill=white)

draw.rounded_rectangle((62, 334, 1004, 438), radius=24, fill=(3, 22, 53, 172), outline=(112, 180, 240, 90), width=2)
draw.text((91, 352), "实时路径追踪", font=font(FONT_CN_BOLD, 28), fill=white)
draw.text((314, 352), "浙江 11 地市影响评估", font=font(FONT_CN_BOLD, 28), fill=white)
draw.text((91, 397), "官方预警汇总", font=font(FONT_CN, 25), fill=muted)
draw.text((314, 397), "定位附近风险与防御措施", font=font(FONT_CN, 25), fill=muted)

# Real project screenshot, with location-specific content replaced by generic feature copy.
screen = Image.open(SCREEN_PATH).convert("RGBA")
sd = ImageDraw.Draw(screen)
sd.rounded_rectangle((925, 310, 1252, 568), radius=16, fill=(247, 250, 255, 255), outline=(181, 204, 239, 255), width=2)
sd.text((946, 334), "定位我的位置", font=font(FONT_CN_BOLD, 26), fill=(29, 78, 216, 255))
sd.text((946, 382), "查看附近风险与防御措施", font=font(FONT_CN, 18), fill=(72, 86, 107, 255))
sd.text((946, 420), "授权定位后显示", font=font(FONT_CN, 17), fill=(132, 148, 169, 255))
sd.rounded_rectangle((946, 472, 1072, 518), radius=23, fill=(29, 78, 216, 255))
sd.text((973, 482), "一键定位", font=font(FONT_CN_BOLD, 19), fill=(255, 255, 255, 255))
# Persist only the privacy-safe preview in the project.
screen.save(SCREEN_PATH)

screen_w = 952
screen_h = round(screen_w * screen.height / screen.width)
screen = screen.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
screen = rounded_image(screen, 24)
sx, sy = 64, 482
add_shadow(bg, (sx, sy, sx + screen_w, sy + screen_h), radius=24, blur=24, alpha=170)
bg.alpha_composite(screen, (sx, sy))
draw = ImageDraw.Draw(bg)
draw.rounded_rectangle((sx, sy, sx + screen_w, sy + screen_h), radius=24, outline=(190, 221, 255, 160), width=2)

# QR/CTA panel.
panel = (48, 1061, 1032, 1382)
add_shadow(bg, panel, radius=32, blur=24, alpha=190)
draw.rounded_rectangle(panel, radius=32, fill=(4, 20, 48, 232), outline=(100, 177, 247, 120), width=2)
draw.text((82, 1102), "扫码查看实时动态", font=font(FONT_CN_BOLD, 47), fill=white)
draw.text((84, 1171), "实时路径 · 预警汇总 · 地市影响", font=font(FONT_CN, 25), fill=muted)
draw.rounded_rectangle((82, 1226, 475, 1280), radius=27, fill=(19, 76, 150, 220), outline=(93, 186, 255, 150), width=2)
draw.text((110, 1238), "tzti.pages.dev", font=font(FONT_LATIN, 26), fill=white)
draw.text((84, 1315), "数据持续更新，请以当地防汛部门最新发布为准", font=font(FONT_CN, 18), fill=(155, 181, 215, 255))

# Browser element clipping can vary with display scale, so crop from the
# calibrated full screenshot instead of relying on a device-pixel clip.
qr = Image.open(QR_PAGE_PATH).convert("RGB").crop((340, 60, 940, 660))
qr.save(QR_PATH)
qr = qr.resize((244, 244), Image.Resampling.NEAREST)
qx, qy = 753, 1099
draw.rounded_rectangle((735, 1081, 1015, 1361), radius=28, fill=(255, 255, 255, 255))
bg.paste(qr, (qx, qy))

# Small production mark, not a brand logo.
draw.text((62, 1404), "TYPHOON BAVI · REAL-TIME TRACKER", font=font(FONT_LATIN, 16), fill=(124, 160, 207, 220))

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
bg.convert("RGB").save(OUT_PATH, quality=96, optimize=True)
print(OUT_PATH)
