#!/usr/bin/env python3
"""PDF ingest wrapper for wiki-obsidian.

Calls opendataloader-pdf, post-processes markdown, places files into wiki structure:
  raw/assets/<file>.pdf  →  raw/sources/<YYYY-MM-DD>-<slug>.md
                            raw/assets/json/<slug>.json

Usage: uv run --directory tools/odl python ingest.py <pdf>...

---

Dependency: OpenDataLoader PDF (by Hancom — 한컴)
  Upstream: https://github.com/opendataloader-project/opendataloader-pdf
  License:  Apache License 2.0 (v2.0+)
  See ./NOTICE.md for full attribution and license compliance notes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parents[2]
RAW_SOURCES = WIKI_ROOT / "raw" / "sources"
RAW_ASSETS = WIKI_ROOT / "raw" / "assets"
RAW_JSON = RAW_ASSETS / "json"
JAVA_BIN = "/opt/homebrew/opt/openjdk@17/bin"


def is_inside_raw_assets(pdf: Path) -> bool:
    try:
        pdf.relative_to(RAW_ASSETS)
        return True
    except ValueError:
        return False


def slugify(text: str, maxlen: int = 80) -> str:
    text = text.strip().lower()
    text = re.sub(r"[\s/]+", "-", text)
    text = re.sub(r"[^\w가-힣\-.]", "", text)
    text = re.sub(r"-+", "-", text).strip("-.")
    return text[:maxlen] or "untitled"


def extract_title(data: dict, fallback: str) -> str:
    if data.get("title"):
        return str(data["title"]).strip()
    page1 = [
        k for k in data.get("kids", [])
        if k.get("type") == "heading" and k.get("page number") == 1
    ]
    if page1:
        best = max(page1, key=lambda h: h.get("font size", 0))
        content = (best.get("content") or "").strip()
        if content:
            return content
    return fallback


def clean_markdown(text: str) -> str:
    text = re.sub(r"·{5,}", "", text)
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def build_frontmatter(title: str, source: str, pages: int, slug: str, tags: list[str]) -> str:
    today = date.today().isoformat()
    safe_title = title.replace('"', '\\"')
    tag_lines = "\n".join(f'  - "{t}"' for t in tags)
    return (
        "---\n"
        f'title: "{safe_title}"\n'
        f"created: {today}\n"
        f"updated: {today}\n"
        f"tags:\n{tag_lines}\n"
        f'source: "{source}"\n'
        f"pdf_pages: {pages}\n"
        f"pdf_extracted_at: {today}\n"
        f'pdf_json_ref: "../assets/json/{slug}.json"\n'
        "---\n\n"
    )


def run_opendataloader(pdfs: list[Path], out_dir: Path, sanitize: bool) -> None:
    env = os.environ.copy()
    env["PATH"] = f"{JAVA_BIN}:{env.get('PATH', '')}"
    cmd = [
        "opendataloader-pdf",
        "-o", str(out_dir),
        "-f", "json,markdown",
        "--image-output", "off",
        "-q",
    ]
    if sanitize:
        cmd.append("--sanitize")
    cmd.extend(str(p) for p in pdfs)
    subprocess.run(cmd, env=env, check=True)


def ingest_one(pdf: Path, out_dir: Path, tags: list[str], force: bool, copy_pdf: bool) -> bool:
    base = pdf.stem
    json_path = out_dir / f"{base}.json"
    md_path = out_dir / f"{base}.md"
    if not (json_path.exists() and md_path.exists()):
        print(f"[skip] {pdf.name}: outputs missing in {out_dir}", file=sys.stderr)
        return False

    data = json.loads(json_path.read_text())
    title = extract_title(data, fallback=base)
    pages = int(data.get("number of pages", 0))
    slug = slugify(title)
    today = date.today().isoformat()
    target_md = RAW_SOURCES / f"{today}-{slug}.md"
    target_json = RAW_JSON / f"{slug}.json"

    if target_md.exists() and not force:
        print(f"[skip] {target_md.relative_to(WIKI_ROOT)} exists (use --force to overwrite)", file=sys.stderr)
        return False

    # Auto-copy PDF into raw/assets if outside, so source is permanent
    source_pdf = pdf
    if copy_pdf and not is_inside_raw_assets(pdf):
        RAW_ASSETS.mkdir(parents=True, exist_ok=True)
        target_pdf = RAW_ASSETS / f"{slug}.pdf"
        if not target_pdf.exists() or force:
            shutil.copy2(pdf, target_pdf)
            print(f"     copied pdf → {target_pdf.relative_to(WIKI_ROOT)}")
        source_pdf = target_pdf

    source_display = (
        str(source_pdf.relative_to(WIKI_ROOT))
        if source_pdf.is_relative_to(WIKI_ROOT)
        else str(source_pdf)
    )

    md_body = clean_markdown(md_path.read_text())
    fm = build_frontmatter(title, source_display, pages, slug, tags)
    target_md.write_text(fm + md_body)

    RAW_JSON.mkdir(parents=True, exist_ok=True)
    shutil.copy2(json_path, target_json)

    print(f"[ok] {target_md.relative_to(WIKI_ROOT)}  ({pages}p, {len(md_body):,} chars)")
    print(f"     {target_json.relative_to(WIKI_ROOT)}")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description="Ingest PDFs into wiki-ggq")
    p.add_argument("pdfs", nargs="+", help="PDF file paths")
    p.add_argument("--tag", action="append", default=[], help="Extra frontmatter tag (repeatable)")
    p.add_argument("--sanitize", action="store_true", help="Replace emails/URLs/IPs with placeholders")
    p.add_argument("--force", action="store_true", help="Overwrite existing target markdown")
    p.add_argument("--no-copy", action="store_true", help="Do NOT copy source PDF into raw/assets/")
    args = p.parse_args()

    pdf_paths: list[Path] = []
    for x in args.pdfs:
        path = Path(x).expanduser().resolve()
        if not path.exists() or path.suffix.lower() != ".pdf":
            print(f"[err] not a PDF: {path}", file=sys.stderr)
            return 1
        pdf_paths.append(path)

    tags = ["pdf", *args.tag]
    RAW_SOURCES.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="odl-") as tmp:
        out_dir = Path(tmp)
        run_opendataloader(pdf_paths, out_dir, sanitize=args.sanitize)
        ok_count = sum(
            ingest_one(p, out_dir, tags, args.force, copy_pdf=not args.no_copy)
            for p in pdf_paths
        )

    print(f"\n{ok_count}/{len(pdf_paths)} ingested.")
    return 0 if ok_count == len(pdf_paths) else 2


if __name__ == "__main__":
    sys.exit(main())
