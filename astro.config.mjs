import { defineConfig } from "astro/config";

// Fully static build. Dynamic bits (the photo gallery and the watermarked
// image versions) are handled by the Cloudflare Worker in worker/index.js.
export default defineConfig({
  site: "https://jasonarussell.com",
  output: "static",
  trailingSlash: "ignore",
  build: { format: "directory" },
});
