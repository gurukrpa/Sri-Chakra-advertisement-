"""
generate_video.py  v2 — Animated 25-sec Sri Chakra Ad
------------------------------------------------------
• White & deep-red brand colours matching logo
• 2 AI voices (A & B) speaking naturally short lines
• Fade-in text animations per slide
• Sri Chakra logo top-left on every frame
• Final CTA slide with website + offer details
• Max ~25 seconds total
"""

import textwrap
import numpy as np
from pathlib import Path

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/magick"})

from gtts import gTTS
from moviepy.editor import (
    AudioFileClip, ColorClip, CompositeVideoClip,
    ImageClip, TextClip, concatenate_videoclips,
)
from moviepy.video.fx.fadein import fadein

# ── Config ────────────────────────────────────────────────────────────────────
BASE       = Path(__file__).parent.parent
OUTPUT_DIR = BASE / "output";  OUTPUT_DIR.mkdir(exist_ok=True)
LOGO_PATH  = BASE / "assets" / "logo.png"

BG_COLOR   = (255, 255, 255)   # white
RED        = "#8B0000"         # deep red (logo)
PINK       = "#C2185B"         # brand pink
DARK       = "#1A1A1A"         # near-black text

FONT_BOLD  = "/Users/apple/Library/Fonts/DejaVuSans-Bold.ttf"
FONT_REG   = "/Users/apple/Library/Fonts/DejaVuSans.ttf"
W, H       = 1080, 1080
FPS        = 24

WEBSITE    = "srichakraacademy.com/career-assessment"
REGISTER   = "https://share.google/ZyfYraRyv6QaMRUto"

# ── Short snappy lines — total spoken time ~21 s ──────────────────────────────
LINES = [
    ("A", "Did you know — you can become a certified career counsellor in just 3 months?"),
    ("B", "3 months?! With live sessions, a career lab, and real mentoring?"),
    ("A", "Yes — and right now it is only 14,999 rupees. That is 30 percent off!"),
    ("B", "Starts first week of May. Limited seats — register now!"),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def tts(text: str, path: Path) -> Path:
    gTTS(text=text, lang="en", slow=False).save(str(path))
    return path


def logo_clip(duration: float):
    if not LOGO_PATH.exists():
        return None
    # Resize with Pillow first (avoids MoviePy ANTIALIAS deprecation error)
    from PIL import Image as PILImage
    pil_img = PILImage.open(str(LOGO_PATH)).convert("RGBA")
    ratio = 100 / pil_img.height
    new_w = int(pil_img.width * ratio)
    pil_img = pil_img.resize((new_w, 100), PILImage.LANCZOS)
    arr = np.array(pil_img)
    return (
        ImageClip(arr, ismask=False)
        .set_position((32, 32))
        .set_duration(duration)
    )


def make_slide(speaker: str, text: str, audio_path: Path) -> CompositeVideoClip:
    audio    = AudioFileClip(str(audio_path))
    duration = audio.duration + 0.2

    bg  = ColorClip(size=(W, H), color=BG_COLOR, duration=duration)

    # Top bar
    top_bar = ColorClip(size=(W, 12), color=(139, 0, 0), duration=duration)\
              .set_position((0, 0))
    bot_bar = ColorClip(size=(W, 8), color=(194, 24, 91), duration=duration)\
              .set_position((0, H - 8))

    # Speaker pill
    pill_color = (139, 0, 0) if speaker == "A" else (194, 24, 91)
    pill = ColorClip(size=(200, 40), color=pill_color, duration=duration)\
           .set_position(((W - 200) // 2, H - 185))\
           .fx(fadein, 0.2)
    pill_txt = TextClip(
        f"{'Priya' if speaker=='A' else 'Ananya'} says",
        fontsize=24, color="white", font=FONT_BOLD,
    ).set_position(("center", H - 182)).set_duration(duration).fx(fadein, 0.25)

    # Main body text — centred, animated
    wrapped = "\n".join(textwrap.wrap(text, width=26))
    body = (
        TextClip(wrapped, fontsize=56, color=DARK, font=FONT_BOLD,
                 method="caption", size=(960, None), align="center")
        .set_position("center")
        .set_duration(duration)
        .fx(fadein, 0.35)
    )

    # Offer ticker at bottom
    ticker = (
        TextClip("30% OFF  |  Starts May  |  Limited Seats",
                 fontsize=28, color=RED, font=FONT_BOLD)
        .set_position(("center", H - 130))
        .set_duration(duration)
        .fx(fadein, 0.5)
    )

    layers = [bg, top_bar, bot_bar, pill, pill_txt, body, ticker]
    logo = logo_clip(duration)
    if logo:
        layers.append(logo)

    return CompositeVideoClip(layers).set_audio(audio)


def make_cta_slide() -> CompositeVideoClip:
    duration = 4.0
    bg      = ColorClip(size=(W, H), color=(255, 255, 255), duration=duration)
    top_bar = ColorClip(size=(W, 12), color=(139, 0, 0), duration=duration).set_position((0, 0))
    bot_bar = ColorClip(size=(W, 10), color=(194, 24, 91), duration=duration).set_position((0, H - 10))

    brand = TextClip("Srichakra Academy", fontsize=70, color=RED, font=FONT_BOLD)\
            .set_position(("center", 260)).set_duration(duration).fx(fadein, 0.4)
    sub   = TextClip("Career Consultants", fontsize=38, color=PINK, font=FONT_BOLD)\
            .set_position(("center", 348)).set_duration(duration).fx(fadein, 0.5)
    tag   = TextClip("Self Discovery to Success", fontsize=28, color="#555555", font=FONT_REG)\
            .set_position(("center", 400)).set_duration(duration).fx(fadein, 0.55)

    # Register button
    btn_bg = ColorClip(size=(660, 68), color=(139, 0, 0), duration=duration)\
             .set_position(((W - 660) // 2, 500)).fx(fadein, 0.6)
    btn_txt = TextClip("REGISTER NOW", fontsize=38, color="white", font=FONT_BOLD)\
              .set_position(("center", 514)).set_duration(duration).fx(fadein, 0.65)

    site    = TextClip(WEBSITE, fontsize=28, color=PINK, font=FONT_REG)\
              .set_position(("center", 600)).set_duration(duration).fx(fadein, 0.7)
    offer   = TextClip("Rs.14,999  |  30% OFF  |  Starts May  |  Limited Seats",
                       fontsize=30, color=DARK, font=FONT_BOLD)\
              .set_position(("center", 650)).set_duration(duration).fx(fadein, 0.75)
    contact = TextClip("Call / WhatsApp: 85903 96662  /  98430 30697",
                       fontsize=26, color="#555555", font=FONT_REG)\
              .set_position(("center", 710)).set_duration(duration).fx(fadein, 0.8)

    layers = [bg, top_bar, bot_bar, brand, sub, tag, btn_bg, btn_txt, site, offer, contact]
    logo = logo_clip(duration)
    if logo:
        layers.append(logo)
    return CompositeVideoClip(layers)


def build_video() -> str:
    clips = []
    for i, (speaker, text) in enumerate(LINES):
        audio_path = OUTPUT_DIR / f"line_{i:02d}.mp3"
        tts(text, audio_path)
        clips.append(make_slide(speaker, text, audio_path))

    clips.append(make_cta_slide())

    final   = concatenate_videoclips(clips, method="compose")
    out     = str(OUTPUT_DIR / "ad_video.mp4")
    final.write_videofile(out, fps=FPS, codec="libx264", audio_codec="aac")
    print(f"\n[✓] Video saved → {out}")
    return out


if __name__ == "__main__":
    build_video()
