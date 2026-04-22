"""
upload_social.py
----------------
Uploads a video to:
  1. Facebook Page (via Graph API)
  2. Instagram Business Account (via Instagram Graph API)

Requires environment variables — set via GitHub Actions secrets or .env file.
"""

import os
import time
import requests
from pathlib import Path

# ── Env vars (set as GitHub Actions secrets / GCloud Secret Manager) ─────────
FB_PAGE_ID        = os.environ["FB_PAGE_ID"]           # Facebook Page numeric ID
FB_ACCESS_TOKEN   = os.environ["FB_ACCESS_TOKEN"]      # Page-level long-lived token
IG_USER_ID        = os.environ["IG_USER_ID"]           # Instagram Business Account ID
IG_ACCESS_TOKEN   = os.environ["IG_ACCESS_TOKEN"]      # Same FB token works for IG Graph API

VIDEO_PATH = Path(__file__).parent.parent / "output" / "ad_video.mp4"

POST_CAPTION = (
    "🎓 Become a Certified Career Counsellor in just 3 months!\n\n"
    "✅ Live Sessions  ✅ Career Assessment Lab  ✅ Ongoing Mentoring\n"
    "💰 ₹19,500 → ₹14,999 (30% OFF)\n"
    "📅 Starts 1st Week of May | Limited Seats!\n\n"
    "Register 👉 https://forms.gle/mnW1jDmoSFX8pRbq5\n\n"
    "#CareerCounsellor #CertifiedCounsellor #CareerGuidance #SriChakra"
)

GRAPH = "https://graph.facebook.com/v19.0"


# ── Facebook ──────────────────────────────────────────────────────────────────

def upload_to_facebook(video_path: str) -> dict:
    """Upload video to a Facebook Page and publish it."""
    print("[FB] Uploading video …")

    # Step 1 – initialise resumable upload
    init_url = f"{GRAPH}/{FB_PAGE_ID}/videos"
    with open(video_path, "rb") as f:
        resp = requests.post(
            init_url,
            data={
                "access_token": FB_ACCESS_TOKEN,
                "description": POST_CAPTION,
                "published": "true",
            },
            files={"source": f},
            timeout=300,
        )
    resp.raise_for_status()
    data = resp.json()
    print(f"[FB ✓] Posted! Video ID: {data.get('id')}")
    return data


# ── Instagram ─────────────────────────────────────────────────────────────────

def upload_to_instagram_via_url(public_video_url: str) -> dict:
    """
    Upload a video Reel to Instagram Business account.
    Instagram Graph API requires a PUBLIC URL (not a local file path).
    We use the GCS public URL produced by upload_to_gcs().
    """
    print("[IG] Creating media container …")

    # Step 1 – create container
    container_url = f"{GRAPH}/{IG_USER_ID}/media"
    resp = requests.post(
        container_url,
        data={
            "access_token": IG_ACCESS_TOKEN,
            "media_type": "REELS",
            "video_url": public_video_url,
            "caption": POST_CAPTION,
            "share_to_feed": "true",
        },
        timeout=60,
    )
    resp.raise_for_status()
    container_id = resp.json()["id"]
    print(f"[IG] Container ID: {container_id} — waiting for processing …")

    # Step 2 – poll until ready
    for attempt in range(20):
        time.sleep(10)
        status_resp = requests.get(
            f"{GRAPH}/{container_id}",
            params={"fields": "status_code", "access_token": IG_ACCESS_TOKEN},
            timeout=30,
        )
        status = status_resp.json().get("status_code")
        print(f"[IG] Status: {status}")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError("Instagram media processing failed.")

    # Step 3 – publish
    publish_resp = requests.post(
        f"{GRAPH}/{IG_USER_ID}/media_publish",
        data={
            "access_token": IG_ACCESS_TOKEN,
            "creation_id": container_id,
        },
        timeout=60,
    )
    publish_resp.raise_for_status()
    result = publish_resp.json()
    print(f"[IG ✓] Published! Media ID: {result.get('id')}")
    return result


# ── GCS helper (needed for IG) ────────────────────────────────────────────────

def upload_to_gcs(video_path: str) -> str:
    """Upload video to Google Cloud Storage and return a signed public URL."""
    from google.cloud import storage

    bucket_name = os.environ["GCS_BUCKET_NAME"]
    blob_name   = f"ads/{Path(video_path).name}"

    client  = storage.Client()
    bucket  = client.bucket(bucket_name)
    blob    = bucket.blob(blob_name)

    print(f"[GCS] Uploading {video_path} → gs://{bucket_name}/{blob_name} …")
    blob.upload_from_filename(video_path, content_type="video/mp4")

    # Make the file publicly readable (or use signed URL)
    blob.make_public()
    public_url = blob.public_url
    print(f"[GCS ✓] Public URL: {public_url}")
    return public_url


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    video_path = str(VIDEO_PATH)
    assert Path(video_path).exists(), f"Video not found: {video_path}"

    # 1. Upload to GCS (needed for Instagram public URL)
    public_url = upload_to_gcs(video_path)

    # 2. Post to Facebook
    upload_to_facebook(video_path)

    # 3. Post to Instagram
    upload_to_instagram_via_url(public_url)

    print("\n[✓] All done — video posted to Facebook & Instagram!")


if __name__ == "__main__":
    main()
