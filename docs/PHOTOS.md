# Adding photographs

## 1. Set titles in darktable (optional but recommended)

In the darkroom or lighttable, open the **metadata editor** module and fill in:

- **Title**: shown under the photo and used in print inquiries. If empty, the site makes one from the filename (`purple-coneflower.jpg` → "Purple coneflower").
- **Description**: optional caption shown in the photo viewer.

Give a photo **5 stars** to feature it on the home page. If several have 5 stars, the first in gallery order wins.

## 2. Export settings (set once, save as a style/preset)

In the **export** module:

- Format: **JPEG**, quality **92**
- Size: **4000 × 4000** max. That's plenty for the site (it shows at most 1600px) and keeps each file well under Cloudflare's 20 MB limit for image processing. Don't upload RAW files.
- Click the gear (preferences) next to the export button → **metadata**:
  - On: *exif data*, *metadata* (this carries title, description, rating)
  - Off: *geo tags*, *develop history*, *tags*

  The site strips all metadata from what visitors see anyway, but this keeps location data out of the bucket too and keeps files small.

## 3. Upload

Easiest: Cloudflare dashboard → R2 → `jasonarussell-photos` → **Upload** → drag the JPEGs in.

From Ubuntu, for many at once, `rclone` can sync a folder to R2 (`rclone sync ~/Pictures/site-exports r2:jasonarussell-photos`). Ask Claude to set it up when you want it.

New photos show up in the gallery within about 10 minutes.

## Order, hiding, and removing

- **Order:** photos whose filenames start with a number come first, in that order (`010-iris.jpg`, `020-aster.jpg`, …). Everything else follows, newest upload first.
- **Hide without deleting:** rename so the filename starts with `_` (for example `_iris.jpg`). It disappears from the gallery and its image URLs stop working.
- **Remove:** delete it from the bucket. It leaves the gallery within 10 minutes. Copies already cached at Cloudflare's edge can linger at their direct URL for up to 30 days unless you purge the cache (dashboard → Caching → Purge).

## What visitors can get

Only the watermarked 720px thumbnail and 1600px viewer version. The originals have no public address. Right-click saving is discouraged on the page, but anything shown on screen can be captured, so the watermark is the real protection.
