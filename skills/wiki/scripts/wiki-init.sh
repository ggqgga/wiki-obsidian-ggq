#!/usr/bin/env bash
# wiki-init.sh — 위키 생성 + qmd 컬렉션 setup
# Usage: wiki-init.sh [dir] [--name <name>] [--domain <domain>]
set -euo pipefail

DIR="${1:-.}"
NAME=""
DOMAIN=""

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) NAME="$2"; shift 2 ;;
        --domain) DOMAIN="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [[ -z "$NAME" ]]; then
    echo "Error: --name is required"
    echo "Usage: wiki-init.sh [dir] --name <name> [--domain <domain>]"
    exit 1
fi

DOMAIN="${DOMAIN:-personal knowledge base}"

echo "=== 1/2 Wiki Init ==="
if wiki status &>/dev/null; then
    echo "Wiki already exists. Skipping init."
    WIKI_PATH=$(wiki status --json 2>/dev/null | grep -o '"path":"[^"]*"' | head -1 | cut -d'"' -f4 || pwd)
else
    wiki init "$DIR" --name "$NAME" --domain "$DOMAIN"
    WIKI_PATH="$DIR"
fi

echo ""
echo "=== 2/2 QMD Setup ==="
if ! command -v qmd &>/dev/null; then
    echo "qmd not found. Install with: npm install -g @tobilu/qmd"
    echo "QMD setup skipped."
    exit 0
fi

# Check if collection already exists
if qmd collection list 2>/dev/null | grep -q "$NAME"; then
    echo "QMD collection '$NAME' already exists. Skipping."
else
    WIKI_DIR="${WIKI_PATH}/wiki"
    if [[ "$WIKI_PATH" == "." ]]; then
        WIKI_DIR="./wiki"
    fi

    echo "Adding collection: $NAME -> $WIKI_DIR"
    qmd collection add "$WIKI_DIR" --name "$NAME"
    qmd context add "qmd://$NAME" "$DOMAIN"
    echo "Generating embeddings..."
    qmd embed
    echo "QMD setup complete."
fi

echo ""
echo "Done. Wiki '$NAME' is ready."
