# Mafalda Ribeiro website

Static Astro version of the former Ghost site for `mafaldaribeiro.com`.

## Edit the site

Most text lives in:

```text
src/content/pages/
```

Each file is one page. Edit the frontmatter title/excerpt or the HTML/Markdown body, then run:

```bash
npm install --include=dev
npm run dev
```

Open the local URL printed by Astro. Before publishing, run:

```bash
npm run build
```

## Add a new page

1. Copy an existing file in `src/content/pages/`.
2. Change `title`, `slug`, `excerpt`, and body content.
3. Visit `/<slug>/` locally.
4. Add it to the navigation in `src/layouts/BaseLayout.astro` if it should be visible in the menu.

## Images

Published assets live in `public/content/`. Use root-relative URLs, for example:

```html
<img src="/content/images/example.webp" alt="Describe the image" />
```

The raw Ghost export and copied original assets live under `_ghost/` and are ignored by git. Do not commit `_ghost/`.

## Deployment

The site deploys to **Cloudflare Workers** via GitHub Actions.

### Setup (one-time)

1. Push `main` to GitHub.
2. In the [Cloudflare dashboard](https://dash.cloudflare.com), go to **Workers & Pages** and note your **Account ID**.
3. Go to **My Profile → API Tokens** and create a token with **Cloudflare Workers** edit permissions.
4. In the GitHub repo, go to **Settings → Secrets and variables → Actions** and add:
   - `CLOUDFLARE_API_TOKEN` — the API token from step 3.
5. Push to `main` or trigger the workflow manually. The site will deploy to `mafaldaribeiro-com.workers.dev`.

### Custom domain

In the Cloudflare dashboard, go to your Worker → **Settings → Domains & Routes** and add `mafaldaribeiro.com`. Cloudflare handles TLS automatically.

### Local deploy (optional)

```bash
npx wrangler login
npm run build
npx wrangler deploy
```

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).
