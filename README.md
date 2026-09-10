# entrepots307 — static export

Static mirror of entrepots307.com. Real compiled CSS, real JS, real images —
styling is identical to the live site, not an approximation.

## Structure

```
index.html                      Accueil (FR)
conseils/  contact/  faq/  nos-entrepots/  reservation-en-ligne/
en/index.html                   Home (EN)
en/contact/  en/faq/  en/online-booking/  en/our-warehouses/  en/tips/
wp-content/                     images, Oxygen CSS, plugin JS  — required
wp-includes/                    jQuery — required
.nojekyll                       stops GitHub Pages mangling the folders
```

12 pages, 69 files, 2.6 MB.

## What was removed

- `wp-json/` REST API dumps and oembed endpoints (~380 KB, no purpose in a static site)
- Duplicate `?p=ID` copies of every page — the menus that pointed at them now
  point at the real pages instead
- Dead `<link>` tags: shortlink, pingback, EditURI, wlwmanifest, oembed (82 tags)

`hreflang` tags were kept, so FR↔EN stays intact.

**Nothing else was deleted.** The multiple image sizes that look like duplicates
(`photo-300x200.jpg`, `photo-768x512.jpg`…) are all referenced in `srcset` —
I checked every one. Pruning them would break responsive images.

Verified: **0 broken internal references** across all 69 files.

## Before you push

**One stylesheet loads from an old staging domain.** `index.html`,
`contact/` and `reservation-en-ligne/` pull `oxygen/css/12.css` from
`thomtech.wttb2jowsb-ewl6n1vzj352.p.temp-site.link`. That file is not in this
export, and the *live site has the same dependency* — if that temp host expires,
styling breaks there too. Grab it and localise:

```bash
curl -o wp-content/uploads/oxygen/css/12.css \
  "https://thomtech.wttb2jowsb-ewl6n1vzj352.p.temp-site.link/wp-content/uploads/oxygen/css/12.css"
grep -rl 'temp-site.link' --include="*.html" . | \
  xargs sed -i '' 's|https://thomtech[^/]*temp-site\.link/|/|g'
```

**Adobe Fonts is domain-locked.** The site loads `use.typekit.net/ppw6qyv.css`.
Typekit kits only serve to whitelisted domains — add your `github.io` domain to
the kit settings or the type falls back to system fonts.

**The contact form won't work.** Static hosting can't process a POST.
Formspree, Netlify Forms, or a mailto link.

**Other external dependencies** (all fine, just noting they're live calls):
Google Tag Manager, Google Fonts, cdnjs (fancybox), Facebook, and the Anemone
booking portal.

## Deploy

```bash
git init && git add -A && git commit -m "static export"
git remote add origin <your-repo>
git push -u origin main
```

Settings → Pages → deploy from branch, root folder. Add a `CNAME` file
containing the domain if you point DNS at it.
