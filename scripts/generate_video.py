"""
generate_video.py
-----------------
Creates a 20-30 second promotional video from a script and branding image.
Uses gTTS (text-to-speech) + MoviePy to render the final MP4.
"""

import os
import textwrap
from pathlib import Path

# Tell MoviePy where ImageMagick is (required for TextClip on macOS)
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/opt/homebrew/bin/magick"})

from gtts import gTTS
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
)

# ── Config ──────────────────────────────────────────────────────────────────
ASSETS_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

BG_COLOR = (88, 24, 69)       # deep purple from brand image
ACCENT    = "#FFC107"     # gold/yellow
TEXT_COLOR = "white"
FONT       = "/Users/apple/Library/Fonts/DejaVuSans-Bold.ttf"
VIDEO_SIZE = (1080, 1080)     # square (FB + IG friendly)
FPS        = 24

# ── Script lines (Person A / Person B alternating) ──────────────────────────
LINES = [
    ("A", "Wait — have you heard about this?"),
    ("A", "You can become a Certified Career Counsellor in just 3 months!"),
    ("B", "3 months?! Are you serious?!"),
    ("A", "YES! Live sessions, mentoring, a career assessment lab — everything!"),
    ("A", "And right now it's only ₹14,999 — that's 30% OFF!"),
    ("B", "That's insane! The batch starts the first week of May!"),
    ("A", "Whether you're a teacher, a graduate, or someone who loves guiding people —"),
    ("A", "this is literally made for you!"),
    ("B", "Guys — LIMITED SEATS ONLY. The link is in the bio. Go. NOW!"),
]

SPEAKER_COLORS = {"A": "#FFD700", "B": "#FFFFFF"}

# ── Helpers ──────────────────────────────────────────────────────────────────

def make_audio(text: str, filename: str) -> str:
    """Generate TTS mp3 for a line of text."""
    path = OUTPUT_DIR / filename
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(str(path))
    return str(path)


def make_line_clip(speaker: str, text: str, audio_path: str) -> CompositeVideoClip:
    """Create a video clip for a single spoken line."""
    audio = AudioFileClip(audio_path)
    duration = audio.duration + 0.3  # tiny pause at end

    bg = ColorClip(size=VIDEO_SIZE, color=BG_COLOR, duration=duration)

    label = TextClip(
        f"Person {speaker}",
        fontsize=36,
        color=SPEAKER_COLORS[speaker],
        font=FONT,
    ).set_position(("center", 120)).set_duration(duration)

    wrapped = "\n".join(textwrap.wrap(text, width=32))
    body = TextClip(
        wrapped,
        fontsize=54,
        color=TEXT_COLOR,
        font=FONT,
        method="caption",
        size=(960, None),
    ).set_position("center").set_duration(duration)

    badge = TextClip(
        "₹19,500 → ₹14,999  |  30% OFF  |  Starts May",
        fontsize=32,
        color=ACCENT,
        font=FONT,
    ).set_position(("center", VIDEO_SIZE[1] - 120)).set_duration(duration)

    clip = CompositeVideoClip([bg, label, body, badge]).set_audio(audio)
    return clip


def build_video() -> str:
    """Assemble all line clips into one final MP4."""
    clips = []
    for i, (speaker, text) in enumerate(LINES):
        audio_file = f"line_{i:02d}.mp3"
        audio_path = make_audio(text, audio_file)
        clip = make_line_clip(speaker, text, audio_path)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    out_path = str(OUTPUT_DIR / "ad_video.mp4")
    final.write_videofile(out_path, fps=FPS, codec="libx264", audio_codec="aac")
    print(f"[✓] Video saved → {out_path}")
    return out_path


if __name__ == "__main__":
    build_video()
