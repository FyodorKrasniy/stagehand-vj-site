# Stagehand VJ — SEO checklist

Tier 1 (technical / on-page) is implemented. This file tracks what's *not* done in code — the off-page and content work that moves the needle long-term.

## What's already live in code

- [x] Single H1, semantic headings, mobile-responsive
- [x] `<title>` + meta description + canonical
- [x] Open Graph + Twitter Card tags with image dimensions
- [x] `theme-color`, `author`, `keywords` meta
- [x] JSON-LD: `SoftwareApplication` + `WebSite` + `FAQPage` schemas
- [x] `robots.txt` allowing all + pointing at sitemap
- [x] `sitemap.xml` with image sitemap extension
- [x] Hero image preloaded (`<link rel="preload" as="image">`)
- [x] All images carry explicit `width`/`height` + descriptive `alt`
- [x] WebP for hero + all feature animations (page weight: ~6.5 MB → ~1 MB)
- [x] HTTPS + custom domain (`stagehandvj.com`)

## Tier 1.5 — needs your hands (5-10 min each)

- [ ] **Enable Cloudflare Web Analytics**
  - Go to <https://dash.cloudflare.com/?to=/:account/web-analytics>
  - Add a site, copy the beacon token
  - In `index.html`, uncomment the `<script defer src=".../beacon.min.js"...>` line and paste the token
- [ ] **Submit sitemap to Google Search Console**
  - Verify domain at <https://search.google.com/search-console> (use DNS verification — Cloudflare makes this trivial)
  - Sitemaps → paste `https://stagehandvj.com/sitemap.xml`
  - Watch the Coverage report for crawl errors
- [ ] **Submit sitemap to Bing Webmaster Tools**
  - <https://www.bing.com/webmasters> (Bing → Yahoo → DuckDuckGo all feed from this)
  - Verify, then paste the sitemap URL
- [ ] **Test the structured data**
  - <https://search.google.com/test/rich-results> → paste the live URL
  - Should detect `SoftwareApplication` + `FAQPage`
  - FAQ rich result is the most valuable — earns expandable accordions in SERPs
- [ ] **Test PageSpeed**
  - <https://pagespeed.web.dev/> → paste the live URL
  - Aim for 90+ on mobile. Tailwind CDN is the biggest remaining cost; if PageSpeed flags it, see Tier 3 below.

## Tier 2 — on-page polish (when there's an hour)

- [ ] **Self-hosted minified Tailwind** instead of Play CDN (~200 KB → ~15 KB). Requires a build step (`npx tailwindcss -i src.css -o assets/site.css --minify`). Probably not worth it until you outgrow single-file.
- [ ] **Self-host the Inter + JetBrains Mono fonts** with `font-display: swap` to drop the Google Fonts roundtrip. Modest win.
- [ ] **Add a `/changelog`** anchor or page that lists each released version (auto-generated from GitHub releases). Search engines love change-cadence content.
- [ ] **Replace decorative SVG icons** with inline data-URI versions where small; cuts a few HTTP requests.

## Tier 3 — content + off-page (where the real ranking comes from)

Backlinks from authoritative niche sites move rankings *way* more than meta tags. None of this is technical.

### Listings (1-2 hours total, mostly forms)

- [ ] **AlternativeTo.net** — submit Stagehand VJ as alternative to "Resolume Alley". Free, drives qualified traffic.
- [ ] **Capterra / GetApp / Software Advice** — Gartner-owned listing network. Free tier is enough.
- [ ] **Slant.co** — comparison site with VJ software category.
- [ ] **G2.com** — when there are a few real users to review it.
- [ ] **Product Hunt launch** — *when 1.0 ships, not before*. Tuesday at midnight PT is the magic slot. Coordinate community in advance.
- [ ] **GitHub topics** on the app repo — make sure these are set: `vj`, `resolume`, `clip-library`, `video-tagging`, `metadata`, `multimedia`, `dxv`, `electron` (or whatever framework).

### Community presence

- [ ] **r/Resolume** — post when there's a feature drop or 1.0. Don't shill; lead with "here's what I built and why."
- [ ] **Resolume official forum** (`forum.resolume.com`) — same play, plus active in the "Tips & Tricks" subforum.
- [ ] **VJ Discord servers** — Resolume's official Discord, Visualist.io, /r/VJing Discord. Plus AV-themed Discord servers.
- [ ] **VJ Facebook groups** — there are large ones; one well-written post in each is worth months of meta-tag tuning.
- [ ] **Twitter/X + Bluesky** — `#vj` `#resolume` `#tdosc` tags. Engage with VJs who post about clip-management pain.

### Content marketing

- [ ] **Tutorial video** — already planned. Embed on a `/tutorial` page with a written transcript below the video. The transcript is what Google indexes.
- [ ] **One long-form post** like *"How I organize 2 TB of VJ clips"* on a blog or dev.to. Internal link back to stagehandvj.com. Long-tail SEO gold.
- [ ] **Screenshot/GIF shares** — every time a new feature lands, post a short clip with the feature name in the alt text. Twitter, Bluesky, IG, TikTok if you have the energy.

### Free resource / link bait

- [ ] **"VJ Clip Naming Convention" cheat sheet** — a 1-page PDF download in exchange for an email (or just free). Linked from the site and from your social posts. Becomes a citable thing that VJs link back to.
- [ ] **Open the underlying tag taxonomy** as a public reference (the example tags Stagehand suggests). Niche-SEO gold.

## Things *not* to do

- ❌ Don't add fake reviews / ratings — Google penalises `aggregateRating` on schemas without verifiable reviews.
- ❌ Don't keyword-stuff — the current copy is at the right density. Adding "VJ VJ VJ Resolume VJ clip" anywhere hurts ranking.
- ❌ Don't buy backlinks — Google's manual reviewers catch this and demote sites.
- ❌ Don't use AMP — it's deprecated and adds complexity for ~0 benefit on a marketing site.
- ❌ Don't add a cookie banner unless analytics actually use cookies. Cloudflare Web Analytics doesn't.

## Measuring success

In Search Console, after 2-4 weeks watch:

- Total impressions for `stagehand`, `resolume clip manager`, `vj clip library`, `vj tagging` etc.
- Click-through rate on those queries
- Indexed pages count (should be 1)
- Mobile usability score
- Core Web Vitals (LCP, FID/INP, CLS)

A new domain typically takes 2-3 months before Google starts ranking it for anything non-branded. Patience.
