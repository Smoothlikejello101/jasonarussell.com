// Shared photo helpers for the home page and the gallery.
// In production, photos come from the Worker (/api/photos) and images from /img/...
// The demo build (PUBLIC_DEMO=1) uses placeholder images so the layout can be previewed.

const DEMO = import.meta.env.PUBLIC_DEMO === "1";

const demoPhotos = [
  ["violet-iris.jpg", "Violet iris", "Morning light through the falls of a bearded iris.", 1067, 1600],
  ["coneflower.jpg", "Coneflower", "", 1600, 1067],
  ["passionflower.jpg", "Passionflower", "Passiflora incarnata, the native maypop.", 1200, 1600],
  ["dew-on-clover.jpg", "Dew on clover", "", 1600, 1600],
  ["salvia.jpg", "Salvia", "", 1067, 1600],
  ["magnolia.jpg", "Magnolia", "Southern magnolia, two days open.", 1600, 1067],
  ["aster.jpg", "Aster", "", 1200, 1600],
  ["lichen.jpg", "Lichen", "Not every subject is a flower.", 1600, 1200],
  ["camellia.jpg", "Camellia", "", 1067, 1600],
].map(([file, title, caption, width, height], i) => ({
  file, title, caption, width, height, featured: i === 0,
}));

export async function getPhotos() {
  if (DEMO) return demoPhotos;
  const res = await fetch("/api/photos");
  if (!res.ok) throw new Error(`Photo list returned ${res.status}`);
  const data = await res.json();
  return data.photos || [];
}

export function imgUrl(photo, variant) {
  if (DEMO) {
    const demoBase = ["..", "demo", ""].join("/"); // relative to the bundled script, for static previews
    return new URL(demoBase, import.meta.url).href + `${variant}/${photo.file.replace(/\.jpe?g$/i, ".webp")}`;
  }
  return `/img/${variant}/${encodeURIComponent(photo.file)}`;
}

export function inquiryLink(email, photo) {
  const subject = `Print inquiry: ${photo.title}`;
  const body = `Hi Jason,\n\nI'm interested in a print of "${photo.title}" (${photo.file}). Could you send sizes and prices?\n\nThanks,\n`;
  return `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}
