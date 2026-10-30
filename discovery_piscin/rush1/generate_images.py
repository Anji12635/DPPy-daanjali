"""Creates images/background1.jpg, background2.jpg and icon.png (needs Pillow)."""
import os
import random
from PIL import Image, ImageDraw

os.makedirs("images", exist_ok=True)
random.seed(7)


def gradient(w, h, stops):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        pos = y / (h - 1) * (len(stops) - 1)
        i = min(int(pos), len(stops) - 2)
        f = pos - i
        color = tuple(int(stops[i][k] * (1 - f) + stops[i + 1][k] * f) for k in range(3))
        d.line([(0, y), (w, y)], fill=color)
    return img


def stars(img, n):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(n):
        x, y = random.randint(0, w), random.randint(0, h // 2)
        r = random.choice([0, 0, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))


def city(img):
    d = ImageDraw.Draw(img)
    w, h = img.size
    x = 0
    while x < w:
        bw, bh = random.randint(40, 110), random.randint(60, 260)
        d.rectangle([x, h - bh, x + bw, h], fill=(24, 16, 44))
        for wy in range(h - bh + 12, h - 10, 22):
            for wx in range(x + 8, x + bw - 8, 18):
                if random.random() < 0.25:
                    d.rectangle([wx, wy, wx + 6, wy + 9], fill=(255, 200, 120))
        x += bw + random.randint(0, 12)


bg1 = gradient(1600, 700, [(20, 18, 60), (90, 40, 130), (220, 90, 150), (255, 150, 120)])
stars(bg1, 220)
city(bg1)
bg1.save("images/background1.jpg", quality=92)

bg2 = gradient(1600, 900, [(10, 12, 36), (30, 22, 70), (60, 30, 100)])
stars(bg2, 300)
bg2.save("images/background2.jpg", quality=92)

icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(icon)
ring = (240, 138, 208, 255)
d.arc([20, 100, 236, 160], start=180, end=360, fill=ring, width=10)   # back of ring
d.ellipse([60, 60, 196, 196], fill=(176, 110, 243, 255))              # planet
d.ellipse([78, 78, 140, 140], fill=(205, 150, 255, 255))
d.arc([20, 100, 236, 160], start=0, end=180, fill=ring, width=10)     # front of ring
icon.save("images/icon.png")
print("Images created in images/")
