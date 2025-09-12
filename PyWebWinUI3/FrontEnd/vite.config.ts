import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte({
      // Warnings are normally passed straight to Rollup. You can
      // optionally handle them here, for example to squelch
      // warnings with a particular code
      onwarn: (warning, handler) => {
        // e.g. don't warn on a11y-autofocus
        if (warning.code.startsWith('a11y-')) return

        // let Rollup handle all other warnings normally
        handler(warning)
      }
    })],
    build: {
      minify: 'terser',
      terserOptions: {
        mangle: {
          keep_fnames: true
        },
        compress: {
          keep_fnames: true
        }
      }
    },
  })
