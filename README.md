# Taiwan Driving Practice (100% English Foreigner Edition)

A free, unofficial community study app and survival guide for foreigners in Taiwan (ARC, APRC, and Employment Gold Card holders from any country) preparing for the **2026 (ROC Year 115)** official English scooter and car driving exams.

## Two ways to run it

1. **Instant Local Offline App:** Double-click **`Taiwan Driving Practice.html`** in Edge, Chrome, Safari, or Firefox — zero internet or installation needed.
2. **Fast Live Website & Installable Phone PWA (`dist/`):** Ready to upload straight to **Cloudflare Pages** or **GitHub Pages** for $0/month (see [DEPLOY.md](DEPLOY.md)). Loads in <1 second on mobile and supports **"Add to Home Screen"** for offline MRT study.

## What’s included

- **All 2,032 Official 2026 English Questions:**
  - **Scooter:** 806 written questions (8 clear topics, including 148 illustrated signs/situations) + 126 linked hazard perception video questions
  - **Car:** 1,090 written questions (9 official topics, including 192 illustrated signs/diagrams) + 10 linked hazard perception video questions
- **Official 2026 Exam Simulator:**
  - **Official 2026 Mix:** 45 written + 5 official hazard videos = 50 questions, 30 minutes, 85% (43/50, max 7 mistakes) to pass
  - **Offline Written Exam:** 50 written questions completely offline
- **Official Gov Tests Hub:** Direct launch cards to Taiwan’s MVDIS online mock simulator, mandatory scooter hazard pre-test (`hpt.thb.gov.tw/videotest`), MVDIS online exam booking, and official Highway Bureau PDFs & full video packs — with clear English-switch guides.
- **Built-in Foreigner Survival Guide (Offline):**
  - **18 essential Traditional Chinese road-sign characters** (`停`, `慢`, `讓`, `機慢車兩段左轉`, `待轉區`, `禁行機車`, etc.) with Pinyin and English meanings
  - **Taiwan rules that surprise foreigners** (no right-on-red, two-stage left turns, red/yellow/white curb lines, green/white/yellow/red plate rules, 0.15 mg/L DUI limit, 3-meter crosswalk rule)
  - **Local ROC Birthday Converter** (`1990-05-09` → `0790509` with 1-click Copy — 100% in-browser, never uploaded)
  - **Show-Your-Phone DMV & Medical Clinic Phrase Card** (English + Traditional Chinese + Pinyin)
- **Universal Foreigner Licensing Checklist, Search Bank, Bookmarks & Contextual Tips:** All progress stays locally in your browser — zero accounts, zero tracking.

## Study on your phone (same Wi-Fi)

1. Connect your PC and phone to the same trusted Wi-Fi network.
2. Open PowerShell in this project folder and run:
   ```powershell
   python phone.py
   ```
3. Open the `http://...` address printed in the terminal on your phone. Press `Ctrl+C` when finished.

## Rebuild from source PDFs

Keep the four official Highway Bureau PDFs (`scooter.pdf`, `car.pdf`, `scooter-hazard.pdf`, `car-hazard.pdf`) beside **`build.py`** and **`app.html`**, install **`pymupdf`**, and run:

```powershell
python build.py
```

This generates both the standalone **`Taiwan Driving Practice.html`** and the production **`dist/`** web/PWA folder.

## Legal & Open Data Attribution

Unofficial free community study tool — not affiliated with Taiwan’s Ministry of Transportation and Communications (MOTC) or Highway Bureau. Question banks and illustrations are sourced from **Highway Bureau, MOTC (交通部公路局), 2026 (ROC Year 115)** under the [Taiwan Open Government Data License v1.0 (OGDL-Taiwan-1.0)](https://data.gov.tw/license) (CC BY 4.0 compatible) and [Highway Bureau Open Data Terms](https://www.thb.gov.tw/en/cp.aspx?n=860).
