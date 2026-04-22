# 🎬 Sri Chakra Ad Automation — Master Setup Guide

Automatically generate a promotional video and post it to **Facebook** and **Instagram** on a schedule using **GitHub Actions + Google Cloud**.

---

## 🔴 RESUME FROM HERE (Next Session / Tomorrow)

> **Last worked on: April 22, 2026**
> Everything below is already done except Step 3 & 4.

### ✅ Already Completed
| Item | Detail |
|---|---|
| GitHub repo | `gurukrpa/Sri-Chakra-advertisement-` |
| GCP Project | `srichakra-ads-2026` |
| GCS Bucket | `gs://srichakra-ads-videos-2026` (Mumbai) |
| Service Account | `ad-automation-sa@srichakra-ads-2026.iam.gserviceaccount.com` |
| GitHub Secret `GCS_BUCKET_NAME` | ✅ Set |
| GitHub Secret `GCLOUD_SERVICE_ACCOUNT_KEY` | ✅ Set |
| GitHub Secret `HEYGEN_API_KEY` | ✅ Set |
| Meta App | App ID: `2301766777017206` |
| FB Page ID | `102020288738081` (Srichakra page) |
| Instagram linked | Linked to Srichakra Page |
| Video generator | Working locally — 30-sec animated MP4 |
| GitHub Actions workflow | Ready — auto-posts Mon & Thu 7 AM IST |

---

### 🔜 NEXT — 3 Steps to Go Live

#### Step 1 — Get a fresh FB Access Token
Open this in browser on any laptop:
```
https://developers.facebook.com/tools/explorer/?app_id=2301766777017206
```
In Graph API Explorer:
1. Select App: **2301766777017206**
2. Click **"Generate Access Token"**
3. Tick these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
4. Select page: **Srichakra** (not personal profile)
5. Copy the `EAA...` token

> ⚠️ Token expires in ~1 hour — use it immediately in Step 2

---

#### Step 2 — Get Instagram Business Account ID
Once you have the token, run this in terminal:
```bash
curl -s "https://graph.facebook.com/v19.0/102020288738081?fields=instagram_business_account,name&access_token=YOUR_EAA_TOKEN"
```
Copy the `id` value from `instagram_business_account` (starts with `17841...`)

---

#### Step 3 — Add 4 secrets to GitHub
Go to: https://github.com/gurukrpa/Sri-Chakra-advertisement-/settings/secrets/actions

Add these 4 secrets:
| Secret Name | Value |
|---|---|
| `FB_PAGE_ID` | `102020288738081` |
| `FB_ACCESS_TOKEN` | The `EAA...` token from Step 1 |
| `IG_USER_ID` | The `17841...` ID from Step 2 |
| `IG_ACCESS_TOKEN` | Same as `FB_ACCESS_TOKEN` |

**OR** paste the `EAA...` token to GitHub Copilot — it will run Steps 2 & 3 automatically.

---

#### Step 4 — Trigger the workflow manually
Go to:
```
https://github.com/gurukrpa/Sri-Chakra-advertisement-/actions
```
Click **"🎬 Generate & Post Ad"** → **"Run workflow"** → **"Run workflow"**

✅ Video will be generated and posted to Facebook & Instagram automatically.

---

#### ⚠️ Security Note
After everything works, **regenerate the token** in Graph API Explorer and update `FB_ACCESS_TOKEN` + `IG_ACCESS_TOKEN` secrets. Old tokens become useless.

For a permanent token (60 days), exchange it:
```
GET https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id=2301766777017206
  &client_secret=YOUR_APP_SECRET
  &fb_exchange_token=SHORT_LIVED_EAA_TOKEN
```

---

---

## 👥 Multi-Admin / Multi-Laptop Workflow

This repo is designed so **any admin on any laptop** can clone it and pick up exactly where it left off.

### How it works across laptops:
```
Laptop A (this Mac)        →  Pushed all code, GCloud setup done, video tested ✅
Laptop B (admin's laptop)  →  Clone repo, add FB/IG secrets, done ✅
GitHub Actions             →  Runs automatically — no laptop needed after setup ✅
```

### For the admin who will connect Facebook & Instagram:
1. Clone the repo on your laptop:
   ```bash
   git clone --recurse-submodules git@github.com:gurukrpa/Sri-Chakra-advertisement-.git
   cd Sri-Chakra-advertisement-
   ```
2. Install deps:
   ```bash
   pip3 install -r requirements.txt
   brew install ffmpeg imagemagick
   ```
3. Follow **Step 3** below to get FB/IG tokens
4. Add the 4 remaining GitHub secrets (FB_PAGE_ID, FB_ACCESS_TOKEN, IG_USER_ID, IG_ACCESS_TOKEN)
5. Go to GitHub → **Actions** → **"🎬 Generate & Post Ad"** → **Run workflow** to trigger manually

> ⚠️ The `GCLOUD_SERVICE_ACCOUNT_KEY` and `GCS_BUCKET_NAME` secrets are **already set** — do not change them.

---

---

## Architecture

```
GitHub Actions (trigger: schedule / push)
        │
        ▼
1. generate_video.py  ──►  output/ad_video.mp4   (MoviePy + gTTS)
        │
        ▼
2. upload_social.py
   ├── upload_to_gcs()       ──►  gs://YOUR_BUCKET/ads/ad_video.mp4 (public URL)
   ├── upload_to_facebook()  ──►  Facebook Page Video Post
   └── upload_to_instagram() ──►  Instagram Reel
```

---

## Step 1 — Prerequisites

Install on your local machine:
- Python 3.11+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- Git
- ffmpeg  (`brew install ffmpeg` on Mac)

---

## Step 2 — Clone & Install Dependencies

```bash
git clone https://github.com/YOUR_USERNAME/ad-automation.git
cd ad-automation
pip install -r requirements.txt
```

---

## Step 3 — Facebook & Instagram API Setup

### 3a. Create a Facebook App
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new App → **Business** type
3. Add products: **Facebook Login** + **Instagram Graph API**

### 3b. Get a Page Access Token
1. Open **Graph API Explorer** → select your App
2. Select your **Facebook Page** (not personal profile)
3. Request permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
4. Generate a **Long-Lived Page Access Token**
   ```
   GET https://graph.facebook.com/v19.0/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id=APP_ID
     &client_secret=APP_SECRET
     &fb_exchange_token=SHORT_LIVED_TOKEN
   ```

### 3c. Get Instagram Business Account ID
```
GET https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_TOKEN
```
Then:
```
GET https://graph.facebook.com/v19.0/PAGE_ID?fields=instagram_business_account&access_token=YOUR_TOKEN
```
Copy the `id` from `instagram_business_account`.

---

## Step 4 — Google Cloud Setup

Run the setup script once:
```bash
bash cloud/setup_gcloud.sh YOUR_GCP_PROJECT_ID YOUR_BUCKET_NAME
```

This will:
- Enable required APIs (Storage, IAM, Cloud Run)
- Create a GCS bucket in `asia-south1`
- Create a service account with Storage Object Admin
- Download `service-account-key.json`

---

## Step 5 — GitHub Secrets Setup

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name                  | Value                                   |
|------------------------------|-----------------------------------------|
| `FB_PAGE_ID`                 | Your Facebook Page numeric ID           |
| `FB_ACCESS_TOKEN`            | Long-lived Page Access Token            |
| `IG_USER_ID`                 | Instagram Business Account ID           |
| `IG_ACCESS_TOKEN`            | Same as FB_ACCESS_TOKEN                 |
| `GCS_BUCKET_NAME`            | Your GCS bucket name                    |
| `GCLOUD_SERVICE_ACCOUNT_KEY` | Full contents of service-account-key.json |

> ⚠️ Delete `service-account-key.json` from your computer after adding it to GitHub Secrets.

---

## Step 6 — Push to GitHub

```bash
cd ad-automation
git init
git add .
git commit -m "feat: initial ad automation pipeline"
git remote add origin https://github.com/YOUR_USERNAME/ad-automation.git
git branch -M main
git push -u origin main
```

---

## Step 7 — Verify GitHub Actions

1. Go to your repo on GitHub
2. Click **Actions** tab
3. You'll see the workflow **"🎬 Generate & Post Ad"**
4. Click **Run workflow** → **Run workflow** to test it manually

The workflow will:
- Install ffmpeg + Python deps
- Generate the video (`output/ad_video.mp4`)
- Upload to GCS
- Post to Facebook Page
- Post to Instagram as a Reel

---

## Step 8 — Scheduling

The workflow runs automatically on a schedule (defined in `.github/workflows/post_ad.yml`):
```yaml
schedule:
  - cron: "30 1 * * 1,4"   # Every Monday & Thursday at 7 AM IST
```

To change the schedule, edit the cron expression:
- [crontab.guru](https://crontab.guru) — visual cron editor

---

## Step 9 — Local Test Run

```bash
cp .env.example .env
# Fill in your values in .env

export $(cat .env | xargs)
python run_pipeline.py
```

---

## Folder Structure

```
ad-automation/
├── .github/
│   └── workflows/
│       └── post_ad.yml          ← GitHub Actions workflow
├── cloud/
│   └── setup_gcloud.sh          ← One-time GCloud setup
├── scripts/
│   ├── generate_video.py        ← Creates the MP4 video
│   └── upload_social.py         ← Posts to FB & Instagram
├── assets/                      ← Drop brand images here
├── output/                      ← Generated videos (gitignored)
├── run_pipeline.py              ← Master pipeline entry point
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md                    ← This file
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ImageMagick policy error` | Run: `sudo sed -i 's/rights="none"/rights="read\|write"/' /etc/ImageMagick-6/policy.xml` |
| `Instagram FINISHED never reached` | Check video is H.264, max 60s, min 720p |
| `FB token expired` | Refresh with long-lived token exchange (valid 60 days) |
| `GCS 403 Forbidden` | Ensure service account has `roles/storage.objectAdmin` |

---

## Credits

- Video generation: [MoviePy](https://zulko.github.io/moviepy/) + [gTTS](https://gtts.readthedocs.io/)
- Hosting: Google Cloud Storage (`srichakra-ads-videos-2026`, region: asia-south1)
- Automation: GitHub Actions (auto-runs Mon & Thu 7 AM IST)
- Social APIs: Meta Graph API v19.0
- GCP Project: `srichakra-ads-2026`
- GitHub Repo: [gurukrpa/Sri-Chakra-advertisement-](https://github.com/gurukrpa/Sri-Chakra-advertisement-)

---

## 🧰 Included Tools (Git Submodules)

These two tools are bundled into this repo as **git submodules** — they will automatically download when anyone clones this repo with `--recurse-submodules`.

### 📊 graphify
- **Repo:** https://github.com/safishamsi/graphify
- **What it does:** AI coding assistant — reads your files, builds a knowledge graph, helps understand any codebase fast
- **Use it:** Type `/graphify` in Claude, Copilot, Cursor, Gemini CLI etc.
- **Local path:** `./graphify/`

### 🔗 GitNexus
- **Repo:** https://github.com/abhigyanpatwari/GitNexus
- **What it does:** Git intelligence tool — powerful repo analysis and navigation
- **Local path:** `./GitNexus/`

### Cloning with submodules (any laptop):
```bash
git clone --recurse-submodules git@github.com:gurukrpa/Sri-Chakra-advertisement-.git
```

### If you already cloned without `--recurse-submodules`:
```bash
git submodule update --init --recursive
```
