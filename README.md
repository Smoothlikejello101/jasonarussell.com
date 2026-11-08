# jasonarussell.com

Personal site for Jason A. Russell: resume, photographs, FullGrown, and projects.

- **Site:** [Astro](https://astro.build), built to plain static files in `dist/`.
- **Hosting:** one Cloudflare Worker (`worker/index.js`) serves the static files and the photo routes.
- **Photos:** full-size originals live in a **private** R2 bucket. Visitors only ever get resized, watermarked WebP copies, made on demand by Cloudflare Images and cached. WebP output strips all EXIF, including GPS.

## What's where

| To change… | Edit |
| --- | --- |
| Home page text | `src/pages/index.astro` |
| Resume | `src/data/resume.json` and `public/resume.pdf` (see `docs/RESUME-UPDATES.md`) |
| Projects list | `src/data/projects.json` |
| Email, FullGrown link, location | `src/data/site.json` |
| Colors and fonts | `src/styles/global.css` |
| Watermark | replace `public/watermark.png` (transparent PNG, ~800px wide) |
| Photo sizes, watermark size/position | `VARIANTS` in `worker/index.js` |
| Visitor stats | Cloudflare dashboard → Web Analytics (Cloudflare injects the script automatically; nothing in the code) |

Adding a new page: create `src/pages/whatever.astro` (copy `projects.astro` as a starting point). It appears at `/whatever/`.

## Photos

See `docs/PHOTOS.md`. In short: export from darktable, upload the JPEG to the `jasonarussell-photos` R2 bucket, and it appears in the gallery within about 10 minutes.

## One-time setup

1. **R2 bucket.** Cloudflare dashboard → R2 → Create bucket → name it `jasonarussell-photos`. Leave public access **off**.
2. **Connect the repo.** Workers & Pages → Create → Import a repository → pick this repo.
   - Build command: `npm run build`
   - Deploy command: `npx wrangler deploy`

   Every push to `main` then rebuilds and deploys automatically.
3. **Domain.** Nothing to do by hand. The `routes` in `wrangler.jsonc` attach `jasonarussell.com` and `www.jasonarussell.com` on first deploy (www redirects to the bare domain).
4. **Visitor stats.** Enabled in the Cloudflare dashboard (Web Analytics); Cloudflare injects the script automatically.
5. **Email.** In Proton: Settings → Domain names → Add domain → `jasonarussell.com`, then add the records Proton shows (verification TXT, MX, SPF, DKIM, DMARC) in Cloudflare DNS. Create the address `jason@jasonarussell.com`.

## Working locally (optional)

```bash
npm install
npm run dev        # site only, at http://localhost:4321 (gallery won't load: no Worker)
npm run preview    # build + run the Worker locally with a local R2 bucket
```

Local preview resizes images but doesn't draw the watermark; that only happens on Cloudflare.

`npm run build:demo` builds a copy that uses placeholder photos, for previewing the design.
