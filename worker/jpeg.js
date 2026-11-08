/**
 * Reads the first part of a JPEG and pulls out:
 *   width / height  (from the SOF frame header)
 *   title / description / rating  (from the XMP packet darktable writes)
 * No dependencies; works in Workers and Node.
 */
export function parseJpegHead(bytes) {
  const out = {};
  if (bytes[0] !== 0xff || bytes[1] !== 0xd8) return out;

  let i = 2;
  while (i + 4 <= bytes.length) {
    if (bytes[i] !== 0xff) { i++; continue; }
    const marker = bytes[i + 1];
    if (marker === 0xd8 || (marker >= 0xd0 && marker <= 0xd7) || marker === 0x01) { i += 2; continue; }
    if (marker === 0xda || marker === 0xd9) break; // start of image data
    const len = (bytes[i + 2] << 8) | bytes[i + 3];
    const start = i + 4;
    const end = Math.min(i + 2 + len, bytes.length);

    // SOF0..SOF15 except DHT(C4), JPG(C8), DAC(CC)
    if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
      if (start + 5 <= bytes.length) {
        out.height = (bytes[start + 1] << 8) | bytes[start + 2];
        out.width = (bytes[start + 3] << 8) | bytes[start + 4];
      }
    }

    if (marker === 0xe1) {
      const seg = new TextDecoder("utf-8", { fatal: false }).decode(bytes.subarray(start, end));
      if (seg.startsWith("http://ns.adobe.com/xap/1.0/")) Object.assign(out, parseXmp(seg));
    }
    i += 2 + len;
  }
  return out;
}

export function parseXmp(xmp) {
  const res = {};
  const alt = (tag) => {
    const m = xmp.match(new RegExp(`<dc:${tag}>\\s*<rdf:Alt>\\s*<rdf:li[^>]*>([\\s\\S]*?)</rdf:li>`, "i"));
    return m ? decodeEntities(m[1].trim()) : "";
  };
  const title = alt("title");
  const description = alt("description");
  if (title) res.title = title;
  if (description) res.description = description;

  const rating = xmp.match(/xmp:Rating(?:="|>)\s*(-?\d+)/);
  if (rating) res.rating = parseInt(rating[1], 10);
  return res;
}

function decodeEntities(s) {
  return s
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'").replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
    .replace(/&amp;/g, "&");
}
