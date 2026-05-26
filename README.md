# Stagehand VJ — Marketing Site

Single-file landing page for [Stagehand VJ Clip Manager](https://stagehandvj.com).

## Stack

- **One HTML file** — no build step
- **Tailwind CSS** via Play CDN (compiled in-browser)
- **Vanilla JS** for any interactivity (currently none required)
- **Inter** + **JetBrains Mono** from Google Fonts

That's the whole stack. To work on it: open `index.html` in a browser. To deploy: upload the folder. There is no `npm install`.

## Run locally

Just open `index.html` in a browser. For a slightly better dev experience (live reload, proper paths), serve the folder with any static server, e.g.:

```powershell
# Python (comes with Windows Python install)
python -m http.server 8000

# Or, if you have Node installed later:
npx serve .
```

Then visit `http://localhost:8000`.

## Assets

All assets live in `/assets/`. The hero composite, feature GIFs, logo, OG image, favicon, and workflow icons are wired in. Missing images degrade gracefully via `onerror` fallbacks, so swapping in new images is safe.

### Regenerating WebP variants of images

The hero PNG and feature GIFs are converted to WebP for a ~6× page-weight reduction. After swapping a source asset, re-run:

```powershell
py tools/optimize_assets.py
```

This reads `assets/hero-platforms.png` + `assets/stagehand-*-large.gif` and writes matching `.webp` files. The site HTML references the `.webp` versions; originals stay on disk as source-archive copies.

### SEO checklist

[`SEO.md`](SEO.md) tracks what's done in code (JSON-LD schemas, sitemap, robots.txt, OG tags, image optimisation) and what's left for off-page work (listings, community posts, content marketing).

### Regenerating the hero composite

The hero image (`assets/hero-platforms.png`) is built from `tools/sources/stagehand-mac.png` + `tools/sources/stagehand-windows.png` + `assets/logo-mark.png` by a small Pillow script. To rebuild after swapping a source screenshot:

```powershell
py tools/compose_hero.py
```

Layout knobs (canvas size, screenshot widths, rotations, positions, shadows, logo placement) all live at the top of `tools/compose_hero.py`.

## Live wiring

- **Downloads** → GitHub release `v0.4.1-beta` on `FyodorKrasniy/stagehand-vj`. Three assets (`StagehandVJ-Beta-WinSetup_r35.exe`, `StagehandVJ-Beta-arm-x64_r35.zip`, `StagehandVJ-Beta-osx-x64_r35.zip`). Same binary runs as the free demo or licence-unlocked. Buttons use the GitHub `releases/latest/download/` alias — filenames carry the `_rNN` build suffix, so each release the three URLs in `index.html` need updating to match (search for `releases/latest/download/StagehandVJ`).
- **Beta licence checkout** → Lemon Squeezy product `452521b6-782a-4d64-b89a-cb43312098ce`. To change, search the file for `lemonsqueezy.com/checkout/buy/` and swap the URL.
- **Email signup** → Formspree form `mnjwldzb` (search for that string to replace).
- **Price** is set to `$25 AUD` in four places (nav, hero secondary button, pricing card, pricing card button). Search for `$25 AUD` and `$25</span>` to swap.

## Deploy to Cloudflare Pages (free)

1. Create a free account at [pages.cloudflare.com](https://pages.cloudflare.com).
2. Push this folder to a GitHub repo.
3. In Cloudflare Pages: "Create a project" → connect the GitHub repo.
4. Build settings: **Framework preset: None**, **Build command: (leave blank)**, **Build output directory: `/`**.
5. Deploy. You'll get a URL like `stagehandvj.pages.dev` immediately. Unlimited bandwidth, free forever.

Alternative free hosts: Netlify, GitHub Pages, Vercel — all work identically with a static folder.

## When to migrate to Astro

Stay on raw HTML until you need:

- A blog or changelog with many posts
- A multi-page tutorial with shared layout
- Localisation or content collections
- Anything that would mean duplicating chunks of HTML across pages

At that point, scaffold an Astro project and port the index in an afternoon — the markup and Tailwind classes drop in directly.

## File layout

```
.
├── index.html                  # the entire site
├── assets/
│   ├── logo-mark.png           # nav + footer logo, also overlaid on hero composite
│   ├── favicon.png             # browser tab icon
│   ├── og-image.png            # social share card (1200x630)
│   ├── hero-platforms.png      # composed Mac + Windows hero (output of tools/compose_hero.py)
│   ├── icons/                  # workflow-step icons
│   │   ├── icon-folder.png
│   │   ├── icon-tag.png
│   │   ├── icon-search.png
│   │   ├── icon-play.png
│   │   └── icon-collection.png
│   ├── stagehand-*-large.gif   # annotated feature gifs used on the page
│   ├── gifs/                   # source/variants of the feature gifs
│   │   ├── *.gif               # small unannotated
│   │   ├── annotated/*.gif     # small annotated
│   │   └── annotated-large/    # large annotated (canonical copies are also mirrored at /assets root)
│   └── screenshots/            # legacy static screenshots (no longer used on the page)
│       ├── main.jpg
│       ├── search.jpg
│       ├── preview.jpg
│       └── tagging.jpg
├── tools/
│   ├── compose_hero.py         # regenerate assets/hero-platforms.png from sources
│   ├── optimize_assets.py      # convert hero PNG + feature GIFs to WebP
│   ├── release-notes-v0.4.0-beta.md  # archive: notes for v0.4.0-beta (r34)
│   ├── release-notes-v0.4.1-beta.md  # archive: notes for v0.4.1-beta (r35)
│   └── sources/                # raw Mac/Windows screenshots used by the composer
│       ├── stagehand-mac.png
│       └── stagehand-windows.png
├── robots.txt                  # crawler directives + sitemap pointer
├── sitemap.xml                 # 1-URL sitemap with image extension
├── SEO.md                      # what's done in code + checklist of off-page TODOs
└── README.md                   # this file
```
