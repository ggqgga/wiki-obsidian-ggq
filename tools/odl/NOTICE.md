# Attribution & License

## OpenDataLoader PDF

This directory uses the [OpenDataLoader PDF](https://github.com/opendataloader-project/opendataloader-pdf) open-source project as a runtime dependency.

| Item | Value |
|------|-------|
| **Project** | OpenDataLoader PDF |
| **Developed by** | Hancom (한컴) — in collaboration with [Dual Lab](https://duallab.com/) (veraPDF developers) and the [PDF Association](https://pdfa.org/) |
| **License** | [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) (v2.0+) |
| **Upstream** | https://github.com/opendataloader-project/opendataloader-pdf |
| **PyPI** | https://pypi.org/project/opendataloader-pdf/ |
| **Note** | This project uses OpenDataLoader PDF as an **unmodified upstream dependency**, installed via `uv add opendataloader-pdf`. No source code from OpenDataLoader is redistributed here. |

### License Compliance

- Apache License 2.0 is a permissive license that allows commercial and personal use, modification, and redistribution
- When distributing this wiki template or any work that bundles OpenDataLoader PDF, retain this NOTICE file and the upstream license
- Pre-2.0 versions of OpenDataLoader are licensed under MPL 2.0; this project targets v2.0+ (Apache 2.0) only

### Why We Use It

OpenDataLoader PDF is used for the `/wiki add <path>.pdf` pipeline — converting PDF documents into structured markdown + JSON for the wiki's knowledge base. Its benchmark-leading extraction accuracy (#1 overall 0.907), local-only processing (no cloud), and Korean OCR support make it ideal for a personal second-brain wiki.

### Alternative Parsers

If you prefer a different PDF parser, you can modify `ingest.py` to call any CLI-based parser with markdown/JSON output. The wiki pipeline only requires:
- A tool that outputs markdown (for `raw/sources/`) and structured JSON (for citation/page references)
- Extracted images/figures can be omitted (see `--image-output off`)

---

## This Directory's Own Code

`ingest.py` and `pyproject.toml` in this directory are part of the wiki-obsidian template and shared under whatever license the parent repository uses.
