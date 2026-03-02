#!/usr/bin/env bash
# populate-governance.sh — Fill governance template placeholders
#
# Usage:
#   ./populate-governance.sh <template-file> [--owner <name>]
#
# This script replaces TODO placeholders in governance templates
# with actual project values. Agents can use this to automate
# template population after installation.

set -euo pipefail

FILE="${1:?Usage: $0 <template-file> [--owner <name>]}"
OWNER="${3:-$(git config user.name 2>/dev/null || echo 'Maintainer')}"
DATE="$(date +%Y-%m-%d)"

if [ ! -f "$FILE" ]; then
    echo "✗ File not found: $FILE" >&2
    exit 1
fi

# Replace placeholders
sed -i "s/<!-- TODO: fill date -->/$DATE/g" "$FILE"
sed -i "s/<!-- TODO: fill owner -->/$OWNER/g" "$FILE"

echo "✓ Populated $FILE (owner=$OWNER, date=$DATE)"
