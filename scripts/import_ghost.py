#!/usr/bin/env python3
"""Import the old Ghost export into this Astro site.

Expected local inputs (ignored by git):
  _ghost/ghost-export.json
  _ghost/raw-assets/persist/mafalda/ghost/{images,media,...}

The script deliberately publishes only Ghost entries with status=published and
never commits the raw Ghost export, which can contain user/settings metadata.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "_ghost" / "ghost-export.json"
RAW_GHOST = ROOT / "_ghost" / "raw-assets" / "persist" / "mafalda" / "ghost"
CONTENT_DIR = ROOT / "src" / "content" / "pages"
PUBLIC_CONTENT = ROOT / "public" / "content"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
COPY_IMAGE_EXTS = {".svg", ".gif", ".ico", ".avif"}
MEDIA_EXTS = {".mp4", ".webm", ".mov", ".m4v", ".mp3", ".wav"}
SITE = "https://mafaldaribeiro.com"


@dataclass(frozen=True)
class AssetResult:
    url: str
    source: Path | None
    output: Path | None
    optimized: bool = False


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def q(value: str | None) -> str:
    return json.dumps(value or "", ensure_ascii=False)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "page"


def local_content_path(url: str) -> str | None:
    """Return path below Ghost content/ for a URL, or None for external URLs."""
    url = unquote(url.replace("&amp;", "&"))
    url = url.split("?", 1)[0].split("#", 1)[0]

    if url.startswith("__GHOST_URL__/content/"):
        return url.removeprefix("__GHOST_URL__/content/")
    if url.startswith("/content/"):
        return url.removeprefix("/content/")

    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and parsed.path.startswith("/content/"):
        # Treat old absolute Ghost asset URLs as local assets, regardless of host.
        return parsed.path.removeprefix("/content/")

    return None


def internal_page_url(url: str) -> str | None:
    url = url.replace("&amp;", "&")
    if url.startswith("__GHOST_URL__"):
        path = url.removeprefix("__GHOST_URL__") or "/"
    else:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return None
        if parsed.netloc not in {"mafaldaribeiro.com", "www.mafaldaribeiro.com"}:
            return None
        path = parsed.path or "/"
    if path.startswith("/content/"):
        return None
    if not path.endswith("/") and "." not in Path(path).name:
        path += "/"
    return path


def magick_available() -> bool:
    return shutil.which("magick") is not None


def optimize_image(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "magick",
        str(src),
        "-auto-orient",
        "-strip",
        "-resize",
        "2000x2000>",
        "-quality",
        "84",
        str(dest),
    ]
    subprocess.run(cmd, check=True)


def copy_asset(local_path: str, cache: dict[str, AssetResult]) -> AssetResult:
    if local_path in cache:
        return cache[local_path]

    rel = Path(local_path)
    src = RAW_GHOST / rel
    if not src.exists():
        result = AssetResult(url=f"/content/{local_path}", source=None, output=None)
        cache[local_path] = result
        return result

    suffix = src.suffix.lower()
    if rel.parts and rel.parts[0] == "images" and suffix in IMAGE_EXTS and magick_available():
        out_rel = Path("images") / Path(*rel.parts[1:]).with_suffix(".webp")
        dest = PUBLIC_CONTENT / out_rel
        optimize_image(src, dest)
        result = AssetResult(url="/content/" + out_rel.as_posix(), source=src, output=dest, optimized=True)
    elif rel.parts and rel.parts[0] == "images" and suffix in (IMAGE_EXTS | COPY_IMAGE_EXTS):
        out_rel = Path("images") / Path(*rel.parts[1:])
        dest = PUBLIC_CONTENT / out_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        result = AssetResult(url="/content/" + out_rel.as_posix(), source=src, output=dest)
    elif rel.parts and rel.parts[0] == "media" and suffix in MEDIA_EXTS:
        out_rel = Path("media") / Path(*rel.parts[1:])
        dest = PUBLIC_CONTENT / out_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        result = AssetResult(url="/content/" + out_rel.as_posix(), source=src, output=dest)
    else:
        out_rel = rel
        dest = PUBLIC_CONTENT / out_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        result = AssetResult(url="/content/" + out_rel.as_posix(), source=src, output=dest)

    cache[local_path] = result
    return result


def rewrite_url(value: str, cache: dict[str, AssetResult], warnings: list[str]) -> str:
    local = local_content_path(value)
    if local:
        result = copy_asset(local, cache)
        if result.source is None:
            warnings.append(f"Missing asset: {value} -> {local}")
            return value.replace("__GHOST_URL__", "")
        return result.url

    page = internal_page_url(value)
    if page is not None:
        return page

    return value


def simplify_video_cards(html: str) -> str:
    """Replace Ghost's JS-driven custom video chrome with native controls."""

    def repl(match: re.Match[str]) -> str:
        figure = match.group(0)
        video = re.search(r"<video\b([^>]*)></video>", figure, re.S)
        if not video:
            return figure
        attrs = video.group(1)
        attrs = re.sub(r"\s+(style|poster|controls)=\"[^\"]*\"", "", attrs)
        attrs = re.sub(r"\s+", " ", attrs).strip()
        thumb = re.search(r"data-kg-thumbnail=\"([^\"]+)\"", figure)
        poster = f' poster="{thumb.group(1)}"' if thumb else ""
        caption = re.search(r"(<figcaption>.*?</figcaption>)", figure, re.S)
        caption_html = caption.group(1) if caption else ""
        return f'<figure class="kg-card kg-video-card kg-card-hascaption"><video {attrs}{poster} controls></video>{caption_html}</figure>'

    return re.sub(r"<figure[^>]*\bkg-video-card\b[^>]*>.*?</figure>", repl, html, flags=re.S)


def rewrite_html(html: str, cache: dict[str, AssetResult], warnings: list[str]) -> str:
    # Use one optimized src per image; carrying Ghost srcsets would require many
    # derivative files and makes the repo unnecessarily heavy.
    html = simplify_video_cards(html)
    html = re.sub(r"\s+srcset=\"[^\"]*\"", "", html)
    html = re.sub(r"\s+sizes=\"[^\"]*\"", "", html)

    def attr_repl(match: re.Match[str]) -> str:
        name = match.group(1)
        value = match.group(2)
        return f'{name}="{rewrite_url(value, cache, warnings)}"'

    html = re.sub(r"\b(src|href|poster)=\"([^\"]+)\"", attr_repl, html)
    html = html.replace("__GHOST_URL__", SITE)
    return html.strip()


def nav_order(slug: str, post_type: str) -> int:
    order = {"portfolio": 10, "photography": 20, "about": 30, "coming-soon": 90}
    return order.get(slug, 50 if post_type == "page" else 80)


def write_page(post: dict, html: str) -> None:
    slug = slugify(post.get("slug") or post.get("title") or "page")
    title = post.get("title") or slug.replace("-", " ").title()
    excerpt = re.sub(r"\s+", " ", post.get("custom_excerpt") or post.get("excerpt") or "").strip()
    published = post.get("published_at") or post.get("created_at") or ""
    updated = post.get("updated_at") or ""
    post_type = post.get("type") or "page"

    frontmatter = "\n".join(
        [
            "---",
            f"title: {q(title)}",
            f"slug: {q(slug)}",
            f"kind: {q(post_type)}",
            f"publishedAt: {q(published)}",
            f"updatedAt: {q(updated)}",
            f"excerpt: {q(excerpt)}",
            f"navOrder: {nav_order(slug, post_type)}",
            "draft: false",
            "---",
            "",
        ]
    )
    (CONTENT_DIR / f"{slug}.md").write_text(frontmatter + html + "\n", encoding="utf-8")


def main() -> int:
    if not EXPORT.exists():
        print(f"Missing {EXPORT}", file=sys.stderr)
        return 1
    if not RAW_GHOST.exists():
        print(f"Missing {RAW_GHOST}; copy assets with rsync first", file=sys.stderr)
        return 1

    clean_dir(CONTENT_DIR)
    clean_dir(PUBLIC_CONTENT / "images")
    clean_dir(PUBLIC_CONTENT / "media")

    data = json.loads(EXPORT.read_text(encoding="utf-8"))
    posts = data.get("data", {}).get("posts", [])
    cache: dict[str, AssetResult] = {}
    warnings: list[str] = []
    published_count = 0

    for post in posts:
        if post.get("status") != "published":
            continue
        html = rewrite_html(post.get("html") or "", cache, warnings)
        write_page(post, html)
        published_count += 1

    outputs = [r for r in cache.values() if r.output]
    total_size = sum(r.output.stat().st_size for r in outputs if r.output and r.output.exists())
    optimized = sum(1 for r in outputs if r.optimized)
    print(f"Imported {published_count} published Ghost entries")
    print(f"Published assets: {len(outputs)} files, {total_size / 1024 / 1024:.1f} MiB ({optimized} optimized images)")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0 if not warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
