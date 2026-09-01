import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    license: { fileName: 'third-party-licenses.md' },
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'react-core', test: /\/node_modules\/(?:react|react-dom|scheduler)\// },
            { name: 'interface-kit', test: /\/node_modules\/(?:@radix-ui|lucide-react|motion)\// },
            { name: 'state-kit', test: /\/node_modules\/(?:@tanstack|zustand)\// },
          ],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:8765',
    },
  },
})
