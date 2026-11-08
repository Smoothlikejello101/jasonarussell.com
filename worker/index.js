/**
 * jasonarussell.com — Cloudflare Worker
 *
 * Serves the static site and two dynamic routes:
 *   GET /api/photos          JSON list of photos (title, caption, size) read from R2
 *   GET /img/:variant/:file  watermarked, resized WebP made from the private original
 *
 * Originals live in a private R2 bucket and are never served directly.
 * WebP output discards all EXIF metadata, so GPS/location data never leaves.
 */

import { parseJpegHead } from "./jpeg.js";

// The only sizes anyone can request. Adding a size = one more cached
// transformation per photo (Cloudflare Images free tier: 5,000 unique/month).
export const VARIANTS = {
  thumb: { long: 720, quality: 80, mark: 96, inset: 12 },
  full: { long: 1600, quality: 84, mark: 220, inset: 24 },
};

const IMAGE_EXT = /\.(jpe?g)$/i;
const HEAD_BYTES = 256 * 1024; // enough to reach XMP + image dimensions
const LIST_TTL = 600; // seconds the photo list is cached
const IMG_TTL = 60 * 60 * 24 * 30; // 30 days

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.hostname === "www.jasonarussell.com") {
      url.hostname = "jasonarussell.com";
      return Response.redirect(url.toString(), 301);
    }

    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405 });
    }

    if (url.pathname === "/api/photos") {
      return cached(request, ctx, LIST_TTL, () => listPhotos(env));
    }

    const m = url.pathname.match(/^\/img\/(thumb|full)\/(.+)$/);
    if (m) {
      const variant = m[1];
      const key = decodeURIComponent(m[2]);
      if (!isSafeKey(key)) return notFound();
      return cached(request, ctx, IMG_TTL, () => renderImage(env, url, key, variant));
    }

    return env.ASSETS.fetch(request);
  },
};

export function isSafeKey(key) {
  return (
    IMAGE_EXT.test(key) &&
    !key.includes("..") &&
    !key.startsWith("/") &&
    !key.startsWith("_") && // files starting with _ stay hidden (drafts)
    !key.includes("/_") &&
    key.length < 300
  );
}

async function cached(request, ctx, ttl, make) {
  const cache = caches.default;
  const key = new Request(new URL(request.url).toString(), { method: "GET" });
  const hit = await cache.match(key);
  if (hit) return hit;

  const res = await make();
  if (res.ok) {
    const out = new Response(res.body, res);
    out.headers.set("Cache-Control", `public, max-age=${ttl}`);
    ctx.waitUntil(cache.put(key, out.clone()));
    return out;
  }
  return res;
}

async function listPhotos(env) {
  const objects = [];
  let cursor;
  do {
    const page = await env.PHOTOS.list({ cursor, limit: 1000 });
    objects.push(...page.objects);
    cursor = page.truncated ? page.cursor : undefined;
  } while (cursor);

  const visible = objects.filter((o) => isSafeKey(o.key));

  const photos = await Promise.all(
    visible.map(async (o) => {
      const head = await env.PHOTOS.get(o.key, { range: { offset: 0, length: HEAD_BYTES } });
      const info = head ? parseJpegHead(new Uint8Array(await head.arrayBuffer())) : {};
      return {
        file: o.key,
        title: info.title || titleFromFilename(o.key),
        caption: info.description || "",
        width: info.width || null,
        height: info.height || null,
        added: o.uploaded,
        // Set a rating of 5 stars in darktable to feature a photo on the home page.
        featured: (info.rating || 0) >= 5,
      };
    })
  );

  // Ordering: filenames starting with digits sort first in that order
  // (e.g. "010-iris.jpg"); everything else newest first.
  photos.sort((a, b) => {
    const na = /^\d/.test(a.file), nb = /^\d/.test(b.file);
    if (na && nb) return a.file.localeCompare(b.file, undefined, { numeric: true });
    if (na !== nb) return na ? -1 : 1;
    return new Date(b.added) - new Date(a.added);
  });

  return Response.json({ photos }, { headers: { "Access-Control-Allow-Origin": "*" } });
}

export function titleFromFilename(key) {
  const base = key.split("/").pop().replace(IMAGE_EXT, "");
  if (/^_?(img|dsc|dscn|dscf|pxl|p\d{6,})[-_ ]?\d*/i.test(base)) return "Untitled"; // camera default names
  const words = base
    .replace(/^\d+[-_ ]*/, "")
    .replace(/[-_]+/g, " ")
    .replace(/\s+\d+$/, "")
    .trim();
  return words ? words.charAt(0).toUpperCase() + words.slice(1) : "Untitled";
}

async function renderImage(env, url, key, variantName) {
  const v = VARIANTS[variantName];
  const original = await env.PHOTOS.get(key);
  if (!original) return notFound();

  const markRes = await env.ASSETS.fetch(new Request(new URL("/watermark.png", url.origin)));
  if (!markRes.ok) return new Response("Watermark missing", { status: 500 });

  const result = await env.IMAGES.input(original.body)
    .transform({ width: v.long, height: v.long, fit: "scale-down" })
    .draw(env.IMAGES.input(markRes.body).transform({ width: v.mark }), {
      bottom: v.inset,
      right: v.inset,
      opacity: 0.85,
    })
    .output({ format: "image/webp", quality: v.quality });

  const res = result.response();
  const out = new Response(res.body, res);
  out.headers.set("Content-Disposition", "inline");
  return out;
}

function notFound() {
  return new Response("Not found", { status: 404 });
}
