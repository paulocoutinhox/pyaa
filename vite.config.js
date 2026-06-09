import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
    root: "./apps/web/static/vendor/frontend",

    base: "/static/frontend/",

    build: {
        outDir: path.resolve(__dirname, "apps/web/static/frontend"),
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
