# visualization/airbus_panel.py
"""
Airbus overhead ENG panel for the Streamlit app — a clickable PIL image.

panel_image(mode, master_on, bleed_on) renders the ENG panel (dark slate body,
corner screws, ENG 1/ENG 2 toggle switches with white caps, a rotary MODE knob
whose pointer rotates to the selection, an APU BLEED switch, and FIRE buttons) as
a PIL image reflecting the current state. It is shown via streamlit-image-
coordinates so the switches are clicked directly; hit_test(x, y) maps a click to
the control ('master' | 'mode' | 'bleed' | None) using PANEL_REGIONS.

PANEL_CSS styles the surrounding column as the panel bay and the legend text.
"""
import math
from PIL import Image, ImageDraw, ImageFont

IMG_W, IMG_H = 360, 300

# Click regions in image pixel space -> control name
PANEL_REGIONS = {
    'master': (52, 40, 128, 184),     # ENG 1 toggle switch
    'mode':   (146, 110, 214, 182),   # rotary MODE knob
    'bleed':  (104, 238, 256, 276),   # APU BLEED switch
}

PANEL_CSS = """<style>
.panel-marker { display: none; }
[data-testid="column"]:has(.panel-marker) {
    background: linear-gradient(160deg, #2c3036 0%, #1c1f23 100%);
    border: 2px solid #0c0d0f; border-radius: 10px; padding: 14px 16px 18px;
    box-shadow: inset 0 1px 0 #44474c, 0 8px 22px rgba(0,0,0,0.6);
}
.ap-label {
    color: #9aa0a6; font-family: 'Courier New', monospace; font-size: 11px;
    font-weight: bold; letter-spacing: 2px; margin: 10px 0 4px; text-transform: uppercase;
}
/* image-coordinates panel: pointer cursor + tidy framing */
div[data-testid="stImageCoordinates"] img,
div:has(> img[alt]) img { cursor: pointer; border-radius: 6px; }
</style>"""


def hit_test(x, y):
    """Return the control name whose region contains (x, y), or None."""
    for name, (x0, y0, x1, y1) in PANEL_REGIONS.items():
        if x0 <= x <= x1 and y0 <= y <= y1:
            return name
    return None


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                       # very old Pillow
        return ImageFont.load_default()


def _toggle(d, cx, label, on):
    """Draw one ENG MASTER toggle switch (lever up=ON / down=OFF) with white cap."""
    word, num = label.split()
    d.ellipse((cx - 14, 114, cx + 14, 128), fill=(38, 41, 46), outline=(12, 13, 15))
    d.ellipse((cx - 9, 116, cx + 9, 124), fill=(58, 63, 69))
    if on:
        d.line((cx, 121, cx, 90), fill=(212, 215, 219), width=8)
        cap_y = 62
    else:
        d.line((cx, 121, cx, 152), fill=(150, 156, 162), width=8)
        cap_y = 150
    d.rounded_rectangle((cx - 20, cap_y, cx + 20, cap_y + 30), radius=4,
                        fill=(237, 239, 233), outline=(119, 124, 131), width=2)
    d.text((cx, cap_y + 9), word, font=_font(9), fill=(21, 23, 26), anchor='mm')
    d.text((cx, cap_y + 21), num, font=_font(13), fill=(21, 23, 26), anchor='mm')
    on_c = (230, 233, 237) if on else (98, 102, 109)
    off_c = (98, 102, 109) if on else (230, 233, 237)
    d.text((cx - 30, 96), 'ON', font=_font(9), fill=on_c, anchor='lm')
    d.text((cx - 32, 158), 'OFF', font=_font(9), fill=off_c, anchor='lm')


def panel_image(mode, master_on, bleed_on):
    """Render the ENG panel as a PIL image reflecting mode / master / bleed state."""
    img = Image.new('RGB', (IMG_W, IMG_H), (28, 31, 35))
    d = ImageDraw.Draw(img)

    # Panel body + bevel
    d.rounded_rectangle((6, 6, 354, 294), radius=12, fill=(68, 74, 82),
                        outline=(35, 38, 42), width=3)
    d.rounded_rectangle((10, 10, 350, 290), radius=10, outline=(96, 102, 110), width=1)
    for sx, sy in ((24, 24), (336, 24), (24, 276), (336, 276)):
        d.ellipse((sx - 5, sy - 5, sx + 5, sy + 5), fill=(90, 95, 102), outline=(28, 31, 35))
        d.line((sx - 3, sy, sx + 3, sy), fill=(28, 31, 35), width=1)

    d.text((180, 26), 'ENG', font=_font(13), fill=(231, 233, 236), anchor='mm')

    _toggle(d, 90, 'ENG 1', master_on)
    _toggle(d, 270, 'ENG 2', False)

    # Rotary MODE knob
    grn = (124, 252, 0)
    grey = (207, 210, 214)
    d.text((180, 92), 'MODE', font=_font(9), fill=grey, anchor='mm')
    d.text((180, 106), 'NORM', font=_font(9),
           fill=grn if mode == 'NORM' else grey, anchor='mm')
    d.ellipse((150, 115, 210, 175), fill=(196, 198, 192), outline=(58, 61, 66), width=2)
    d.ellipse((158, 123, 202, 167), outline=(140, 143, 136), width=1)
    ang = {'CRANK': -50, 'NORM': 0, 'IGN/START': 50}.get(mode, 0)
    rad = math.radians(ang)
    cx, cy = 180, 145
    ex, ey = cx + 24 * math.sin(rad), cy - 24 * math.cos(rad)
    d.line((cx, cy, ex, ey), fill=(21, 23, 26), width=4)
    d.text((132, 192), 'CRANK', font=_font(9),
           fill=grn if mode == 'CRANK' else grey, anchor='mm')
    d.text((226, 188), 'IGN/', font=_font(9),
           fill=grn if mode == 'IGN/START' else grey, anchor='mm')
    d.text((230, 200), 'START', font=_font(9),
           fill=grn if mode == 'IGN/START' else grey, anchor='mm')

    # APU BLEED switch
    bcol = (44, 120, 60) if bleed_on else (24, 27, 31)
    btxt = (220, 255, 220) if bleed_on else (150, 156, 162)
    d.rounded_rectangle((104, 240, 256, 274), radius=4, fill=bcol, outline=(90, 95, 102))
    d.text((180, 252), 'APU BLEED', font=_font(9), fill=btxt, anchor='mm')
    d.text((180, 265), 'ON' if bleed_on else 'OFF', font=_font(10), fill=btxt, anchor='mm')

    # FIRE buttons (decorative)
    for fx, lbl in ((52, '1'), (308, '2')):
        d.rounded_rectangle((fx - 22, 238, fx + 22, 278), radius=4,
                            fill=(13, 13, 15), outline=(90, 29, 29))
        d.text((fx, 252), 'FIRE', font=_font(7), fill=(194, 59, 59), anchor='mm')
        d.text((fx, 270), lbl, font=_font(10), fill=(207, 210, 214), anchor='mm')

    return img
