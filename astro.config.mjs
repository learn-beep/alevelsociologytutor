import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://www.alevelsociologytutor.com',
  trailingSlash: 'always',
  integrations: [sitemap({ filter: (page) => !page.includes('/print/') && !page.includes('/data/') && !page.includes('/thank-you/') })],
});
