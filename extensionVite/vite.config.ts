import { defineConfig } from 'vite';
import { resolve } from "node:path";
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
   build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        background: resolve(__dirname, "src/background.ts"),
        content: resolve(__dirname, "src/content.ts"),
     //   popup: resolve(__dirname, "src/popup/index.html"),
      },
      output: {
        entryFileNames: (chunk) => {
          if (chunk.name === "background") return "background.js";
          if (chunk.name === "content") return "content.js";
          return "assets/[name].js";
        },
      },
    },
  },
  plugins: [react()],
})
