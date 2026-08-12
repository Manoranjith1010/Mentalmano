import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: fileURLToPath(new URL('../static/react', import.meta.url)),
    emptyOutDir: true,
    manifest: true,
  },
})
