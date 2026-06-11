# Agent notes for Mafalda Ribeiro website

This is a static Astro site for `mafaldaribeiro.com`, deployed to Cloudflare Workers.

## Quick start

```bash
npm install          # install dependencies
npm run dev          # local dev server (open the URL it prints)
npm run build        # verify the build before pushing
```

## Content editing

- Pages live in `src/content/pages/*.md` — one file per page.
- Each file has frontmatter (title, slug, kind, navOrder, draft) and an HTML body.
- To add a new page: copy an existing file, change frontmatter and content.
- To change navigation order: edit `navOrder` in frontmatter (lower = first).
- To hide a page without deleting: set `draft: true` in frontmatter.

## Images

- All published images live in `public/content/images/`.
- Use `.webp` format (smaller, faster). Convert `.jpg`/`.png` before adding.
- Reference as `/content/images/YYYY/MM/filename.webp` in the page body.
- Do not commit the `_ghost/` folder (raw Ghost export, gitignored).

## Deployment

Pushing to `main` triggers a GitHub Actions workflow that builds and deploys to Cloudflare Workers.
The workflow needs `CLOUDFLARE_API_TOKEN` set as a GitHub Actions secret (one-time setup).

## Project structure

```text
src/content/pages/    ← editable content (Markdown + HTML)
src/layouts/         ← page layout (BaseLayout.astro)
src/pages/           ← Astro routes (index, 404, dynamic slug)
src/styles/          ← CSS
public/content/      ← images and static assets
wrangler.toml        ← Cloudflare Workers config
.github/workflows/   ← CI/CD deployment
```

## What NOT to touch

- `src/content.config.ts` — content schema (only change if adding new frontmatter fields)
- `wrangler.toml` — deployment config (only change if Cloudflare setup changes)
- `.github/workflows/deploy.yml` — CI/CD pipeline
- `_ghost/` — raw Ghost export, gitignored, do not commit
