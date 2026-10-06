// Збирання сайту (Vite). Результат — статичні файли в site/build, з відносними шляхами:
// сайт працює з будь-якої папки чи адреси (GitHub Pages, корпоративний сервер).
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './',
  plugins: [react()],
  build: { outDir: 'build' },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
  },
});
