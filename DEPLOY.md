# Go-Live Deployment Guide (100% Free on Cloudflare Pages)

This project builds a pure static website in `dist/` — no backend server, no database, no user accounts, and **$0/month hosting** with global HTTPS and offline PWA support ("Add to Home Screen" on iPhone & Android).

## 1. Legal & Open-Data Checklist (Already Built In)
- **100% Legal Reuse:** Uses Taiwan Highway Bureau (MOTC) 2026 English question banks published under the **Taiwan Open Government Data License v1.0 (OGDL-Taiwan-1.0)** (compatible with CC BY 4.0).
- **Proper Attribution:** Included in the footer (`Highway Bureau, MOTC / 交通部公路局`, 2026 Year 115, with direct links to `data.gov.tw/license` and `thb.gov.tw/en/cp.aspx?n=860`).
- **Clear Unofficial Notice:** Clearly labeled as a free, unofficial community study gift — uses custom non-government icons (`favicon.svg`, `icon-192.png`, `icon-512.png`), never official ROC government seals.
- **No Scraping / No Tracking:** Official video streams, MVDIS booking, and MVDIS simulator open directly on official `.gov.tw` portals. Zero personal data (ARC/birthday) ever leaves the user's browser.

## 2. Deploy Live in 5 Minutes (Cloudflare Pages)

### Option A — Drag-and-Drop Instant Preview (No GitHub Needed, 60 Seconds)
1. Log into [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Workers & Pages** → **Create** → **Pages** → **Direct Upload**.
2. Name the project (e.g. `taiwan-driving-practice`).
3. Drag and drop the **`dist/`** folder from `C:\Users\Shop\Documents\Taiwan-Driving-Practice\dist`.
4. Click **Deploy site** — your site is live immediately at `https://taiwan-driving-practice.pages.dev`!

### Option B — Automatic Deploys via GitHub (Recommended)
1. Create a new GitHub repository (e.g. `taiwan-driving-practice`).
2. Push this local Git repo:
   ```powershell
   cd "C:\Users\Shop\Documents\Taiwan-Driving-Practice"
   git remote add origin https://github.com/<your-username>/taiwan-driving-practice.git
   git push -u origin main
   ```
3. In Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**:
   - **Repository:** `taiwan-driving-practice`
   - **Production branch:** `main`
   - **Build command:** *(leave empty — `dist/` is prebuilt!)*
   - **Build output directory:** `dist`
4. Click **Save and Deploy**. Every future `git push` updates the live site in ~15 seconds.

## 3. Optional Custom Domain (~US$10/year)
In your Cloudflare Pages project → **Custom domains** → **Set up a custom domain** (e.g. `taiwandrivingtest.org`, `twdriving.org`, or `taiwanlicense.guide`). Cloudflare automatically provisions free SSL/HTTPS.

## 4. Annual Question Bank Update (5 Minutes)
Whenever Taiwan's Highway Bureau releases a new year's English PDFs:
1. Drop the updated `scooter.pdf`, `car.pdf`, `scooter-hazard.pdf`, and `car-hazard.pdf` into this folder.
2. Run `python build.py` to rebuild both `dist/` and `Taiwan Driving Practice.html`.
3. Commit and `git push` — Cloudflare Pages updates automatically.
