#!/usr/bin/env bash
# wiki-reindex.sh — qmd 검색 인덱스 갱신
# Usage: wiki-reindex.sh
set -euo pipefail

if ! command -v qmd &>/dev/null; then
    echo "qmd not installed. Skipping reindex."
    exit 0
fi

echo "Updating index..."
qmd update

echo "Refreshing embeddings..."
qmd embed

echo "Reindex complete."
