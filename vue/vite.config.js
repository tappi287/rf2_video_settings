import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue2'

import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
    // Run dev on :8080
    server: {
        port: 8080
    },
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    base: './',
    build: {
        outDir: '../web',
        emptyOutDir: true
    }
})