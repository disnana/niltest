import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://niltest.disnana.com",
  output: "static",
  outDir: "./dist",
  trailingSlash: "always",
  build: {
    format: "directory",
    inlineStylesheets: "auto",
  },
  compressHTML: true,
});
