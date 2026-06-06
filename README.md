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

The repository includes a GitHub Actions workflow for GitHub Pages. Once the repo is created on the GitHub account that will own the site:

1. Push `main`.
2. In GitHub repo settings, enable Pages with **GitHub Actions** as the source.
3. Set the custom domain to `mafaldaribeiro.com`.
4. Point DNS at GitHub Pages.

`public/CNAME` is already set to `mafaldaribeiro.com`.
