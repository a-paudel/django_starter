import { defineConfig } from "vite";
import * as path from "path";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    base: "/__static__/",
    plugins: [
        //
        tailwindcss(),
    ],
    build: {
        manifest: "manifest.json",
        outDir: path.resolve("./__staticfiles__"),
        rollupOptions: {
            input: [
                //
                path.resolve("./__assets__/js/main.ts"),
            ],
        },
    },
});
