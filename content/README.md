# Content folder — How to add posters and videos

The GitHub Action posts **1 poster + 1 video** every day at:
- **8:00 AM IST** (morning)
- **8:00 PM IST** (evening)

Each run picks the **next** poster and the **next** video in numeric order, then loops back to `01` after the last one.

---

## Folder layout

```
content/
├── posters/
│   ├── 01.jpg          ← poster image #1 (also accepts .png, .jpeg)
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
```

## Rules
1. **File names must be 2-digit numbers**: `01`, `02`, `03`, ..., `99`.
2. Every poster must have a matching `.txt` caption with the same number.
3. Every video must have a matching `.txt` caption with the same number.
4. Numbering must be continuous (no gaps): `01, 02, 03` ✅  not `01, 03, 05` ❌.
5. Posters and videos are rotated **independently** — you can have 10 posters and 7 videos; each cycles separately.

## Caption file (`.txt`) tips
- Plain text. Emojis are fine. 
- Keep under 2,200 characters (Instagram limit).
- Add hashtags at the end: `#SriChakra #YourTag`
- A blank line in the file becomes a paragraph break.

## How to add new content
1. Drop the files into the right folder using GitHub's web UI:
   - Open the repo → `content/posters/` (or `videos/`) → **Add file → Upload files**
2. Commit straight to `main`.
3. The next scheduled run will pick them up automatically.

## How to test immediately (without waiting for 8 AM/PM)
- Go to **Actions** tab → **🎬 Generate & Post Ad** → **Run workflow** → green button.
