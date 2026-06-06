# Agent notes for Mafalda Ribeiro website

- This is an Astro static site, intended to be easy to edit with Codex.
- Do not commit `_ghost/`; it may contain raw Ghost export metadata and large original assets.
- Content pages are in `src/content/pages/*.md`.
- Public assets are in `public/content/`.
- Before claiming success, run `npm run build`.
- Keep deployment on GitHub Pages via `.github/workflows/deploy.yml` unless Mafalda explicitly chooses another host.
