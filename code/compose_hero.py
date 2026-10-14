from PIL import Image, ImageDraw, ImageFont

SRC = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/lead-lines-brief-2026-10-15/charts/media-generation-hero-lead-lines-base-0-c7890322-476a-4c1f-b910-154339b88843.webp"
OUT = "/home/hatch/workspace/goals/daily-civic-data-brief/hidden_files/lead-lines-brief-2026-10-15/charts/hero.png"

img = Image.open(SRC).convert("RGB")
W, H = img.size
print("base size:", W, H)

# gradient scrim across the top sky band for text legibility
scrim = Image.new("L", (1, H))
for y in range(H):
    t = y / (H * 0.42)
    a = max(0, int(165 * (1 - t))) if t < 1 else 0
    scrim.putpixel((0, y), a)
scrim = scrim.resize((W, H))
dark = Image.new("RGB", (W, H), (18, 17, 14))
img = Image.composite(dark, img, scrim.point(lambda v: v))

d = ImageDraw.Draw(img)
AMBER = (232, 163, 61)
PAPER = (241, 231, 218)
DIM = (196, 186, 168)
x = int(W * 0.045)
y = int(H * 0.055)

f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(H * 0.115))
f_cap = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(H * 0.037))
f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(H * 0.026))

d.text((x, y), "21,426", font=f_big, fill=AMBER)
y += int(H * 0.135)
d.text((x, y), "premises are still in Denver Water's lead-line program", font=f_cap, fill=PAPER)
y += int(H * 0.052)
d.text((x, y), "11,400 confirmed lead lines - Denver Water inventory, June 30, 2026", font=f_sub, fill=DIM)

img.save(OUT)
print("saved", OUT)
