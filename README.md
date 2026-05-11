# Stagehand VJ — Marketing Site

Single-file landing page for [Stagehand VJ Clip Manager](https://stagehandvj.example).

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

## Add your assets

See [assets/README.txt](assets/README.txt) for exact filenames. Missing images degrade gracefully — the site is safe to deploy with placeholders.

## Things to replace before going live

Search the file for these strings and swap them out:

| Find | Replace with |
|---|---|
| `YOUR_FORM_ID` | Your Formspree form ID (free at [formspree.io](https://formspree.io)) |
| `$XX` | Your beta access price (e.g. `$29`) — currently in `index.html` |
| `$XX` | Your beta access price (e.g. `$29`) |
| `https://stagehandvj.example` | Your real domain once you grab one |

The "Download Demo" button currently links to `#` — wire it to your actual demo download (Gumroad, direct link, etc.) when ready.

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
│   ├── README.txt              # which images go where
│   ├── logo-mark.png           # (you add)
│   ├── favicon.png             # (you add)
│   ├── og-image.png            # (you add)
│   └── screenshots/
│       ├── main.png            # (you add)
│       ├── search.png          # (you add)
│       └── tagging.png         # (you add)
└── README.md                   # this file
```
