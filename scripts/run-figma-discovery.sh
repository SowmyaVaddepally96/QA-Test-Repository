#!/usr/bin/env bash
# Run Figma full extraction for Sophi - Developers Hand Off, node 8062-9900.
# Requires: FIGMA_TOKEN (and optionally FIGMA_PASSWORD if file is password-protected).
#
# Usage:
#   export FIGMA_TOKEN="figd_..."
#   # optional: export FIGMA_PASSWORD="your-password"
#   ./scripts/run-figma-discovery.sh
#
# Or with .env in the figma skill directory:
#   export $(cat .cursor/skills/figma/.env | xargs) && ./scripts/run-figma-discovery.sh

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ -f ".cursor/skills/figma/.env" ]; then
  set -a
  source .cursor/skills/figma/.env
  set +a
fi

if [ -z "${FIGMA_TOKEN:-}" ]; then
  echo "Error: FIGMA_TOKEN is not set."
  echo "Get a token from Figma > Settings > Personal access tokens"
  echo "Then: export FIGMA_TOKEN=\"figd_...\""
  exit 1
fi

FIGMA_URL="https://www.figma.com/design/yFFgIDlTbDcQAbICJyFEuu/Sophi---Developers-Hand-Off?node-id=8062-9900&t=kqucwgizz0RE5adN-4"
NODE_IDS="8062:9900"
OUTPUT_DIR="figma-data"
OUTPUT_FILE="${OUTPUT_DIR}/node-8062-9900-full.json"

mkdir -p "$OUTPUT_DIR"

echo "Fetching Figma full data for node 8062:9900..."
if [ -n "${FIGMA_PASSWORD:-}" ]; then
  python3 .cursor/skills/figma/scripts/figma_fetch.py full --file-key "$FIGMA_URL" --node-ids "$NODE_IDS" --password "$FIGMA_PASSWORD" > "$OUTPUT_FILE"
else
  python3 .cursor/skills/figma/scripts/figma_fetch.py full --file-key "$FIGMA_URL" --node-ids "$NODE_IDS" > "$OUTPUT_FILE"
fi

echo "Figma data saved to $OUTPUT_FILE"
echo "Ask the agent: 'Generate test case discovery from $OUTPUT_FILE' to get the full discovery report."
