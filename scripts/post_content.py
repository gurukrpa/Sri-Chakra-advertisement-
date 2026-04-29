"""
post_content.py
---------------
Posts ONE poster (image) and ONE video to Facebook Page + Instagram Business
account, rotating through the files in `content/posters/` and `content/videos/`.

State is tracked in `state/last_index.json` so each run picks the next item
and loops back to the first after the last one.

Required env vars (set as GitHub Actions secrets):
    FB_PAGE_ID, FB_ACCESS_TOKEN, IG_USER_ID, IG_ACCESS_TOKEN, GCS_BUCKET_NAME
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests

ROOT = Path(__file__).resolve().parent.parent
POSTERS_DIR = ROOT / "content" / "posters"
VIDEOS_DIR = ROOT / "content" / "videos"
STATE_FILE = ROOT / "state" / "last_index.json"

GRAPH = "https://graph.facebook.com/v19.0"

POSTER_EXTS = (".jpg", ".jpeg", ".png")
VIDEO_EXTS = (".mp4",)


# ── Env ──────────────────────────────────────────────────────────────────────

def env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        sys.exit(f"[ERROR] Missing env var: {name}")
    return v


FB_PAGE_ID = env("FB_PAGE_ID")
FB_ACCESS_TOKEN = env("FB_ACCESS_TOKEN")
IG_USER_ID = env("IG_USER_ID")
IG_ACCESS_TOKEN = env("IG_ACCESS_TOKEN")
GCS_BUCKET_NAME = env("GCS_BUCKET_NAME")


# ── Content discovery ────────────────────────────────────────────────────────

def list_numbered_files(folder: Path, exts: tuple[str, ...]) -> list[Path]:
    """Return numbered media files (01.mp4, 02.jpg, ...) sorted ascending."""
    if not folder.exists():
        return []
    items = []
    for p in folder.iterdir():
        if p.suffix.lower() not in exts:
            continue
        stem = p.stem
        if not stem.isdigit():
            continue
        items.append((int(stem), p))
    items.sort(key=lambda t: t[0])
    return [p for _, p in items]


def caption_for(media_path: Path) -> str:
    """Read the matching .txt caption next to the media file."""
    txt = media_path.with_suffix(".txt")
    if not txt.exists():
        print(f"[WARN] No caption file for {media_path.name}; posting without caption.")
        return ""
    return txt.read_text(encoding="utf-8").strip()


# ── State ────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"poster_index": 0, "video_index": 0}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def pick_next(items: list[Path], current_index: int) -> tuple[Optional[Path], int]:
    if not items:
        return None, current_index
    idx = current_index % len(items)
    next_idx = (current_index + 1) % len(items)
    return items[idx], next_idx


# ── GCS (needed for Instagram public URL) ────────────────────────────────────

def upload_to_gcs(local_path: Path, content_type: str) -> str:
    """Upload to GCS and return public URL."""
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob_name = f"ads/{int(time.time())}_{local_path.name}"
    blob = bucket.blob(blob_name)
    print(f"[GCS] Uploading {local_path.name} -> gs://{GCS_BUCKET_NAME}/{blob_name}")
    blob.upload_from_filename(str(local_path), content_type=content_type)
    blob.make_public()
    print(f"[GCS] Public URL: {blob.public_url}")
    return blob.public_url


# ── Facebook ─────────────────────────────────────────────────────────────────

def fb_post_photo(image_path: Path, caption: str) -> dict:
    print(f"[FB] Posting photo: {image_path.name}")
    with open(image_path, "rb") as f:
        r = requests.post(
            f"{GRAPH}/{FB_PAGE_ID}/photos",
            data={
                "access_token": FB_ACCESS_TOKEN,
                "caption": caption,
                "published": "true",
            },
            files={"source": f},
            timeout=300,
        )
    r.raise_for_status()
    print(f"[FB OK] photo id={r.json().get('id')}")
    return r.json()


def fb_post_video(video_path: Path, caption: str) -> dict:
    print(f"[FB] Posting video: {video_path.name}")
    with open(video_path, "rb") as f:
        r = requests.post(
            f"{GRAPH}/{FB_PAGE_ID}/videos",
            data={
                "access_token": FB_ACCESS_TOKEN,
                "description": caption,
                "published": "true",
            },
            files={"source": f},
            timeout=600,
        )
    r.raise_for_status()
    print(f"[FB OK] video id={r.json().get('id')}")
    return r.json()


# ── Instagram ────────────────────────────────────────────────────────────────

def _ig_wait(container_id: str) -> None:
    for _ in range(30):
        time.sleep(8)
        s = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": IG_ACCESS_TOKEN},
            timeout=30,
        ).json().get("status_code")
        print(f"[IG] container {container_id} status={s}")
        if s == "FINISHED":
            return
        if s == "ERROR":
            raise RuntimeError(f"IG container {container_id} ERROR")
    raise RuntimeError(f"IG container {container_id} timed out")


def ig_post_image(image_url: str, caption: str) -> dict:
    print("[IG] Creating image container ...")
    r = requests.post(
        f"{GRAPH}/{IG_USER_ID}/media",
        data={
            "access_token": IG_ACCESS_TOKEN,
            "image_url": image_url,
            "caption": caption,
        },
        timeout=60,
    )
    r.raise_for_status()
    cid = r.json()["id"]
    _ig_wait(cid)
    pub = requests.post(
        f"{GRAPH}/{IG_USER_ID}/media_publish",
        data={"access_token": IG_ACCESS_TOKEN, "creation_id": cid},
        timeout=60,
    )
    pub.raise_for_status()
    print(f"[IG OK] image media id={pub.json().get('id')}")
    return pub.json()


def ig_post_reel(video_url: str, caption: str) -> dict:
    print("[IG] Creating reel container ...")
    r = requests.post(
        f"{GRAPH}/{IG_USER_ID}/media",
        data={
            "access_token": IG_ACCESS_TOKEN,
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
        },
        timeout=60,
    )
    r.raise_for_status()
    cid = r.json()["id"]
    _ig_wait(cid)
    pub = requests.post(
        f"{GRAPH}/{IG_USER_ID}/media_publish",
        data={"access_token": IG_ACCESS_TOKEN, "creation_id": cid},
        timeout=60,
    )
    pub.raise_for_status()
    print(f"[IG OK] reel media id={pub.json().get('id')}")
    return pub.json()


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    posters = list_numbered_files(POSTERS_DIR, POSTER_EXTS)
    videos = list_numbered_files(VIDEOS_DIR, VIDEO_EXTS)

    if not posters and not videos:
        print("[ERROR] No posters or videos found in content/ folder. Nothing to do.")
        return 1

    state = load_state()
    print(f"[STATE] loaded: {state}")

    # Pick next items
    poster, next_p = pick_next(posters, state.get("poster_index", 0))
    video, next_v = pick_next(videos, state.get("video_index", 0))

    if poster:
        print(f"[PICK] poster: {poster.name}")
    else:
        print("[PICK] no posters available; skipping poster post.")
    if video:
        print(f"[PICK] video : {video.name}")
    else:
        print("[PICK] no videos available; skipping video post.")

    failures: list[str] = []

    # ---- POST POSTER ----
    if poster:
        cap = caption_for(poster)
        try:
            poster_url = upload_to_gcs(poster, "image/jpeg" if poster.suffix.lower() in (".jpg", ".jpeg") else "image/png")
        except Exception as e:
            failures.append(f"GCS upload poster: {e}")
            poster_url = None

        try:
            fb_post_photo(poster, cap)
        except Exception as e:
            failures.append(f"FB poster: {e}")

        if poster_url:
            try:
                ig_post_image(poster_url, cap)
            except Exception as e:
                failures.append(f"IG poster: {e}")

    # ---- POST VIDEO ----
    if video:
        cap = caption_for(video)
        try:
            video_url = upload_to_gcs(video, "video/mp4")
        except Exception as e:
            failures.append(f"GCS upload video: {e}")
            video_url = None

        try:
            fb_post_video(video, cap)
        except Exception as e:
            failures.append(f"FB video: {e}")

        if video_url:
            try:
                ig_post_reel(video_url, cap)
            except Exception as e:
                failures.append(f"IG video: {e}")

    # ---- Advance state only on success ----
    new_state = dict(state)
    if poster and not any(f.startswith(("FB poster", "IG poster")) for f in failures):
        new_state["poster_index"] = next_p
    if video and not any(f.startswith(("FB video", "IG video")) for f in failures):
        new_state["video_index"] = next_v

    save_state(new_state)
    print(f"[STATE] saved: {new_state}")

    if failures:
        print("\n[FAILURES]")
        for f in failures:
            print(f"  - {f}")
        return 2

    print("\n[DONE] All posts published successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
