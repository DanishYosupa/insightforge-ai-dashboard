import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  tanstackStart: {
    // Redirect TanStack Start's bundled server entry to src/server.ts (our SSR entry)
    // nitro/vite builds from this
    server: { entry: "src/server.ts" },
  },
  // We place our local API proxy bridge safely inside the custom 'vite' block here:
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  }
});
