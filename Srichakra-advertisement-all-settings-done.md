# Srichakra Advertisement — All Settings Done

**Date:** 29 April 2026
**Repo:** https://github.com/gurukrpa/Sri-Chakra-advertisement-
**Owner:** Eswari K
**Goal:** Auto-post posters + videos to Srichakra Facebook Page and Instagram (`@eswari_srichakra`) twice a day, every day.

---

## 1. What We Accomplished Today

### 1.1 Facebook & Instagram setup
- ✅ Generated a **Facebook Graph API token** for app `Srichakra Ads` (App ID `2301766777017206`).
- ✅ Granted all 4 required permissions on the token:
  - `pages_manage_posts`
  - `pages_read_engagement`
  - `instagram_basic`
  - `instagram_content_publish`
- ✅ Confirmed Eswari K is admin of the **Srichakra** Facebook Page (via Professional Dashboard).
- ✅ Linked the **Srichakra** Facebook Page to the **@eswari_srichakra** Instagram account (chose "Switch Page" — moved the link from Srichakra Overseas to Srichakra).
- ✅ Exchanged the short-lived user token for a **never-expiring Page access token** using the App Secret.
- ✅ Verified token via `debug_token` API: `expires_at: 0` (never expires), all 4 scopes attached.

### 1.2 GitHub repository secrets
Added 4 secrets at https://github.com/gurukrpa/Sri-Chakra-advertisement-/settings/secrets/actions:

| Secret name | Purpose |
|---|---|
| `FB_PAGE_ID` | Srichakra Facebook Page numeric ID (`102020288738081`) |
| `FB_ACCESS_TOKEN` | Never-expiring Page access token |
| `IG_USER_ID` | Instagram Business Account ID (`17841447570801015`) |
| `IG_ACCESS_TOKEN` | Same as `FB_ACCESS_TOKEN` |

> Pre-existing secrets (`GCLOUD_SERVICE_ACCOUNT_KEY`, `GCS_BUCKET_NAME`, `HEYGEN_API_KEY`) were left untouched.

### 1.3 Code changes (committed to `main`)
- ✅ **Deleted** `scripts/generate_video.py` (auto-generated test video — no longer needed).
- ✅ **Deleted** `scripts/upload_social.py` (replaced by new script).
- ✅ **Created** `scripts/post_content.py` — posts next poster + next video from `content/` folder, rotates state.
- ✅ **Replaced** `run_pipeline.py` with a thin entry point that calls `post_content.main()`.
- ✅ **Updated** `requirements.txt` — removed `moviepy`, `gTTS`, `Pillow`, `numpy` (no longer needed). Kept only `requests` + `google-cloud-storage`.
- ✅ **Updated** `.github/workflows/post_ad.yml`:
  - New schedule: `0230 UTC` and `1430 UTC` daily (= **8 AM IST** and **8 PM IST**)
  - Removed ImageMagick, ffmpeg, MoviePy setup (no longer needed)
  - Added auto-commit step that pushes the updated `state/last_index.json` after each run
  - Added `concurrency: post-ad` to prevent two runs clashing
- ✅ **Created** `content/posters/`, `content/videos/`, `state/last_index.json`, `content/README.md`.

---

## 2. How the System Works Now

### 2.1 Folder structure
```
content/
├── posters/
│   ├── 01.jpg          ← poster #1 (also accepts .png, .jpeg)
│   ├── 01.txt          ← caption for poster #1
│   ├── 02.jpg
│   ├── 02.txt
│   └── ...
└── videos/
    ├── 01.mp4          ← video #1 (must be .mp4)
    ├── 01.txt          ← caption for video #1
    ├── 02.mp4
    ├── 02.txt
    └── ...

state/
└── last_index.json     ← auto-tracked rotation pointer (don't edit manually)
```

### 2.2 What happens at 8 AM IST and 8 PM IST
1. Workflow wakes up on GitHub Actions runner.
2. Reads `state/last_index.json` to find the next poster + video.
3. **Posts the poster** to Facebook Page (as photo) AND Instagram (as image post) using `01.txt` caption.
4. **Posts the video** to Facebook Page (as video) AND Instagram (as Reel, also shared to feed) using `01.txt` caption.
5. Updates `state/last_index.json` → poster_index = 1, video_index = 1.
6. Commits the state file back to the repo so next run picks slot `02`.
7. After the last slot, loops back to slot `01`.

### 2.3 Posters and videos rotate independently
You can have **10 posters but only 7 videos** — each cycles on its own. Example:
- Day 1 morning: poster 01 + video 01
- Day 1 evening: poster 02 + video 02
- Day 4 morning: poster 07 + video 07
- Day 4 evening: poster 08 + **video 01** ← video looped back, posters keep going

---

## 3. Rules You Asked About / We Established

### 3.1 File-naming rules
- File names **must** be 2-digit numbers: `01`, `02`, `03`, …, `99`. ✅
- Every media file **must** have a matching `.txt` caption with the same number, in the same folder. ✅
- Numbering must be **continuous** — no gaps. `01, 02, 03` ✅. `01, 03, 05` ❌.
- Posters: `.jpg`, `.jpeg`, or `.png`.
- Videos: `.mp4` only.

### 3.2 Caption rules
- Each poster has its **own caption** in its `.txt` file.
- Each video has its **own caption** in its `.txt` file.
- Plain text. Emojis allowed. Hashtags at the end.
- Keep under **2,200 characters** (Instagram limit).

### 3.3 Recommended media specs
- **Poster:** square 1080×1080 or 4:5 portrait 1080×1350 (best for IG feed).
- **Video:** vertical 9:16 1080×1920 (best for IG Reels). MP4, H.264 codec, ≤90 seconds for Reels, ≤100 MB.

### 3.4 Schedule
- **8:00 AM IST** every day (cron `30 2 * * *` UTC)
- **8:00 PM IST** every day (cron `30 14 * * *` UTC)
- ⚠️ GitHub Actions cron can be delayed by 5–15 minutes during peak hours. Posts may go out at 8:00–8:15.

### 3.5 Cost
- **₹0/month.** Everything runs on free tiers:
  - GitHub Actions (free for public repos / 2,000 min/month for private; we use ~60 min/month)
  - Facebook Graph API (free, unlimited)
  - Instagram Graph API (free, ~50 posts/day cap)
  - GCS bucket (existing free-tier usage, well below limits)

---

## 4. Q&A from Today's Session

### Q: Will it post test/AI-generated content?
**A:** No. The old test-video generator script was deleted. Only files YOU upload to `content/` are posted.

### Q: Can I have different videos for morning and evening?
**A:** Yes — each scheduled run picks the **next** video in the folder. Morning posts `01`, evening posts `02`, next morning `03`, and so on.

### Q: What if I want to add more videos later?
**A:** Just upload `08.mp4` + `08.txt` (or whatever the next number is) to `content/videos/` via the GitHub web UI. The next run picks them up automatically.

### Q: What happens when the rotation reaches the last item?
**A:** It loops back to slot `01` automatically. So a folder with 7 videos = 7 evenings of unique content, then it repeats.

### Q: Can I pause posting (e.g. for a holiday)?
**A:** Yes — go to **Actions** tab → **🎬 Post Ad (Poster + Video)** → click **"…" → Disable workflow**. Re-enable when you want it back.

### Q: How do I trigger a post manually (without waiting for 8 AM/PM)?
**A:** Go to **Actions** tab → **🎬 Post Ad (Poster + Video)** → click **Run workflow** (green button) → confirm.

### Q: What if a post fails (Facebook is down, etc.)?
**A:** The script logs the failure, but **does not advance the rotation** for that side (poster or video) — so the next run will retry the same slot. This prevents skipping content due to transient errors.

### Q: Do I need to install anything on my laptop?
**A:** No. Everything runs on GitHub's servers. You only need the browser to:
1. Upload files to the repo.
2. Watch the Actions tab if you want to see logs.

---

## 5. Important Credentials (Keep Safe)

> ⚠️ The values below are stored as GitHub Actions secrets and **never logged**. Listed here only for your records. If anyone else gains access, rotate them immediately at https://developers.facebook.com/apps/2301766777017206

| Item | Value |
|---|---|
| Facebook App Name | Srichakra Ads |
| App ID | `2301766777017206` |
| App Secret | (stored only on your laptop locally — not in repo) |
| Facebook Page ID | `102020288738081` |
| Facebook Page Name | Srichakra |
| Instagram Username | `@eswari_srichakra` |
| Instagram Business ID | `17841447570801015` |
| Page Access Token | Stored in GitHub Secret `FB_ACCESS_TOKEN` (never expires) |

### How to rotate the token (if ever leaked)
1. Go to https://developers.facebook.com/apps/2301766777017206/settings/basic/
2. Click **"Reset App Secret"** → confirm.
3. Re-do the token-exchange process with the new secret.
4. Update GitHub Secret `FB_ACCESS_TOKEN` (and `IG_ACCESS_TOKEN`).

---

## 6. Quick Reference — Common Tasks

### Upload a new poster
1. Go to https://github.com/gurukrpa/Sri-Chakra-advertisement-/tree/main/content/posters
2. Click **Add file → Upload files**.
3. Drag in `09.jpg` and `09.txt` (rename before uploading).
4. Click **Commit changes**.

### Upload a new video
1. Go to https://github.com/gurukrpa/Sri-Chakra-advertisement-/tree/main/content/videos
2. Click **Add file → Upload files**.
3. Drag in `09.mp4` and `09.txt`.
4. Click **Commit changes**.

### Check today's posting status
- https://github.com/gurukrpa/Sri-Chakra-advertisement-/actions
- Green ✅ = success. Red ❌ = click the run to see the error.

### Reset rotation back to slot 01
1. Open https://github.com/gurukrpa/Sri-Chakra-advertisement-/blob/main/state/last_index.json
2. Click pencil ✏️ icon.
3. Change values to `0` and `0`.
4. Commit changes.

---

## 7. Status Today

| Item | Status |
|---|---|
| Facebook Page admin verified | ✅ Done |
| Instagram linked to Page | ✅ Done |
| Permanent FB+IG token generated | ✅ Done |
| 4 GitHub secrets added | ✅ Done |
| Rotation script deployed | ✅ Done |
| Schedule active (8 AM + 8 PM IST) | ✅ Done |
| Test content uploaded | ❌ **Pending — your turn** |
| First real post sent | ❌ **Pending — your turn** |

---

## 8. Your Next Step

1. Prepare your first batch of posters and videos on your laptop.
2. Rename them: `01.jpg`, `01.txt`, `02.jpg`, `02.txt`, `01.mp4`, `01.txt`, etc.
3. Upload them via GitHub's **Add file → Upload files** button.
4. Either wait for the next 8 AM / 8 PM IST run, or trigger it manually from the Actions tab.
5. Check Srichakra Facebook Page and `@eswari_srichakra` Instagram for the live posts.

🎉 **You're all set!**
