import { defineConfig } from "vite";
import path from "path";
import { viteStaticCopy } from "vite-plugin-static-copy";

export default defineConfig({
  root: "./apps/web/static/vendor/frontend",

  base: "/static/vendor/frontend/output/",

  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: "../../../../../node_modules/@fortawesome/fontawesome-free/webfonts/*",
          dest: "webfonts",
        },
      ],
    }),
  ],

  build: {
    outDir: "output",
    emptyOutDir: true,

    rollupOptions: {
      input: {
        main: path.resolve(
          __dirname,
          "apps/web/static/vendor/frontend/js/frontend.js"
        ),
      },

      output: {
        entryFileNames: "bundle.js",

        assetFileNames: (assetInfo) => {
          return "assets/[name][extname]";
        },
      },
    },
  },
});
