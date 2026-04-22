"""
run_pipeline.py
---------------
Master pipeline script.
  1. Generate the ad video
  2. Upload to GCS + post to Facebook & Instagram
"""

from scripts.generate_video import build_video
from scripts.upload_social import main as post_social

if __name__ == "__main__":
    print("=" * 60)
    print("  STEP 1 — Generate Ad Video")
    print("=" * 60)
    build_video()

    print()
    print("=" * 60)
    print("  STEP 2 — Upload & Post to Social Media")
    print("=" * 60)
    post_social()
