#!/usr/bin/env bash
# Three UI screenshots with six planted defects.
set -euo pipefail
mkdir -p shots
python3 - <<'PY'
from PIL import Image, ImageDraw, ImageFont
def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)
    except OSError:
        return ImageFont.load_default()
W, H = 1200, 800
# pricing: clipped heading (1), lorem ipsum in FAQ (2)
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
d.text((560, 40), "Simple, transparent pricing for every team", font=font(48, True), fill="black")
for i, (name, price) in enumerate([("Starter", "$9/mo"), ("Team", "$29/mo"), ("Business", "$79/mo")]):
    x = 80 + i * 360
    d.rectangle((x, 160, x + 300, 520), outline="#333", width=2)
    d.text((x + 30, 190), name, font=font(32, True), fill="black")
    d.text((x + 30, 250), price, font=font(40, True), fill="#1a56db")
    d.rectangle((x + 30, 440, x + 270, 490), fill="#1a56db"); d.text((x + 95, 452), "Choose plan", font=font(22), fill="white")
d.text((80, 580), "FAQ", font=font(30, True), fill="black")
d.text((80, 630), "Can I cancel anytime? Yes, from your account settings.", font=font(22), fill="black")
d.text((80, 670), "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", font=font(22), fill="black")
im.save("shots/pricing.png")
# signup: TODO button label (3), near-invisible password hint (4)
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
d.text((420, 60), "Create your account", font=font(42, True), fill="black")
for i, label in enumerate(["Email", "Password"]):
    y = 180 + i * 140
    d.text((400, y), label, font=font(22), fill="black"); d.rectangle((400, y + 35, 800, y + 85), outline="#666", width=2)
d.text((400, 410), "Use 12+ characters with a number and a symbol", font=font(18), fill=(242, 242, 242))
d.rectangle((400, 480, 800, 540), fill="#1a56db"); d.text((540, 495), "TODO: label", font=font(24, True), fill="white")
im.save("shots/signup.png")
# dashboard: empty chart placeholder (5), overlapping card text (6)
im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
d.text((60, 40), "Dashboard", font=font(40, True), fill="black")
d.rectangle((60, 120, 560, 260), outline="#333", width=2); d.text((80, 140), "Active users", font=font(28, True), fill="black"); d.text((80, 190), "12,408", font=font(40, True), fill="black")
d.rectangle((600, 120, 1140, 260), outline="#333", width=2); d.text((470, 150), "Revenue this month", font=font(28, True), fill="black"); d.text((620, 190), "$84,210", font=font(40, True), fill="black")
d.rectangle((60, 300, 1140, 740), outline="#333", width=2); d.text((520, 500), "Chart goes here", font=font(26), fill="#999")
im.save("shots/dashboard.png")
PY
