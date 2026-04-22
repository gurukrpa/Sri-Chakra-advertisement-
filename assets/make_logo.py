from PIL import Image, ImageDraw
import math

size = 300
img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)
cx, cy = size // 2, size // 2

# Petals
for i in range(16):
    r = math.radians(i * (360 / 16))
    px = cx + int(90 * math.cos(r))
    py = cy + int(90 * math.sin(r))
    draw.ellipse([px - 16, py - 24, px + 16, py + 24], fill=(255, 182, 193, 200))

# Outer circles
draw.ellipse([40, 40, 260, 260], outline=(199, 21, 133), width=6)
draw.ellipse([55, 55, 245, 245], fill=(255, 255, 255, 255), outline=(139, 0, 0), width=3)

# Upward triangles (dark red)
for scale in [78, 56, 36]:
    pts = [(cx, cy - scale),
           (cx - int(scale * 0.866), cy + scale // 2),
           (cx + int(scale * 0.866), cy + scale // 2)]
    draw.polygon(pts, fill=(139, 0, 0, 210), outline=(80, 0, 0))

# Downward triangles (crimson)
for scale in [68, 46]:
    pts = [(cx, cy + scale),
           (cx - int(scale * 0.866), cy - scale // 2),
           (cx + int(scale * 0.866), cy - scale // 2)]
    draw.polygon(pts, fill=(180, 0, 40, 200), outline=(80, 0, 0))

# Center dot
draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(139, 0, 0))

img.save("/Users/apple/Desktop/srichakr add/ad-automation/assets/logo.png")
print("Logo saved.")
