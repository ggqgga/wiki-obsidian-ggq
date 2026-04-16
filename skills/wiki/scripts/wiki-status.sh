#!/usr/bin/env bash
# wiki-status.sh — wiki status + qmd status 통합 출력
set -euo pipefail

echo "=== Wiki Status ==="
wiki status "$@"

echo ""

if command -v qmd &>/dev/null; then
    echo "=== QMD Search Engine ==="
    qmd status
else
    echo "=== QMD Search Engine ==="
    echo "(qmd not installed)"
fi
