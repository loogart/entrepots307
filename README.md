# Entrepôts 307

Bilingual static website for Entrepôts 307 in Cantley, Québec. The approved redesign uses square corners, black/yellow branding, responsive storage cards, and original facility photography alongside approved generated illustrations.

## Build and verify

```sh
npm run build
npm test
python3 -m http.server 8310
```

No package installation is required. Python 3.9+ builds all 12 pages and the bilingual XML sitemap. Open `http://localhost:8310/` to review the production website.

- `_source/tools/build.py`: page templates and approved content refinements.
- `_source/tools/seo.py`: unique bilingual metadata, canonical and alternate URLs, business/service/FAQ structured data, and preserved tracking extraction.
- `_source/legacy/`: frozen source copy and original tracking snippets.
- `_source/brand/`: editable vector social-preview artwork.
- `_source/media/`: photo masters; optimized WebP files are in `assets/site/`.
- `assets/site/home-copy.json`: approved shortened homepage introduction.
- `assets/site/styles.css` and `site.js`: shared responsive styles and navigation.

## Publishing

GitHub Pages deploys the root of `main` to https://entrepots307.com/ using the existing `CNAME`. `_config.yml` excludes editing sources and the local draft from the published site. Push the verified production changes to `main` and check the Pages deployment.

The original 12 French/English routes remain in place. Legacy `wp-content` files are retained for existing document and media URLs. The new pages have no dependency on the old Oxygen, WordPress, staging-domain, or Typekit styles.

## Search and sharing

Every page includes a unique title and description, absolute canonical URL, reciprocal French/English alternates, Open Graph and Twitter preview metadata, and factual JSON-LD. `sitemap.xml` lists every translated route; `robots.txt` permits public indexing. FAQs use the same answers shown in the page. Prices and business details must stay synchronized with visible content; no reviews or opening hours are invented.

The favicon, Apple touch icon, install icons, and French/English social cards use the approved brand artwork. Social cards are 1200 × 630 PNGs. Keep assets at their current URLs when rebuilding.

## Tracking and reservations

Google Ads `AW-16731741234` and Meta Pixel `1455636772776328`, including PageView and the noscript fallback, are preserved from the original production pages. The release check compares the exact tracking snippets with the frozen originals.

Reservations continue to use the existing Anemone booking destination and partner ID, with the matching French/English language parameter. The site does not process bookings itself.

Search Console and Bing Webmaster Tools sitemap submissions and business-profile management happen in their respective owner accounts; deploying this repository does not submit them automatically.
