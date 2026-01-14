import { defineConfig } from "vite";
import path from "path";
import { viteStaticCopy } from "vite-plugin-static-copy";

export default defineConfig({
    root: "./apps/web/static/vendor/frontend",

    base: "/static/frontend/",

    plugins: [
        viteStaticCopy({
            targets: [
                {
                    src: path.resolve(__dirname, "node_modules/@fortawesome/fontawesome-free/webfonts/*"),
                    dest: "webfonts",
                },
            ],
        }),
    ],

    build: {
        outDir: path.resolve(__dirname, "static/frontend"),
        emptyOutDir: true,
        manifest: true,

        rollupOptions: {
            input: {
                frontend: path.resolve(__dirname, "apps/web/static/vendor/frontend/js/frontend.js"),
            },
            output: {
                entryFileNames: "[name]-[hash].js",
                chunkFileNames: "[name]-[hash].js",
                assetFileNames: "assets/[name]-[hash][extname]",
            },
        },
    },
});
