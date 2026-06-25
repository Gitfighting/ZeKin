import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

const uniElements = new Set([
  'button',
  'form',
  'image',
  'input',
  'label',
  'navigator',
  'picker',
  'scroll-view',
  'swiper',
  'swiper-item',
  'switch',
  'text',
  'textarea',
  'view',
])

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => uniElements.has(tag),
        },
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'jsdom',
  },
})
