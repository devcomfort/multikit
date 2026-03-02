#!/bin/bash
# cikit: Setup script for Copilot CLI and Ralph Wiggum
#
# This script installs the tools required for cikit CI checks.
# Run in GitHub Actions or locally.
#
# Usage:
#   chmod +x .github/scripts/setup-copilot-ralph.sh
#   .github/scripts/setup-copilot-ralph.sh [--ralph]
#
# Options:
#   --ralph    Also install Ralph Wiggum (for loop mode)

set -e

INSTALL_RALPH=false
for arg in "$@"; do
  case "$arg" in
    --ralph) INSTALL_RALPH=true ;;
  esac
done

echo "🔧 cikit CI tools setup"
echo "========================"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found."
    echo "   Install via nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash"
    echo "   Then: nvm install 22 --lts && nvm use 22"
    exit 1
fi

NODE_VERSION=$(node --version | sed 's/v//' | cut -d. -f1)
if [ "$NODE_VERSION" -lt 22 ]; then
    echo "⚠️ Node.js $NODE_VERSION detected. Version 22+ recommended."
    echo "   Run: nvm install 22 --lts && nvm use 22"
fi
echo "✅ Node.js $(node --version)"

# Install GitHub Copilot CLI
if npm list -g @github/copilot &> /dev/null 2>&1; then
    echo "✅ @github/copilot already installed"
else
    echo "📦 Installing @github/copilot..."
    npm install -g @github/copilot
    echo "✅ @github/copilot installed"
fi

# Install Ralph Wiggum (optional)
if [ "$INSTALL_RALPH" = true ]; then
    if npm list -g @th0rgal/ralph-wiggum &> /dev/null 2>&1; then
        echo "✅ @th0rgal/ralph-wiggum already installed"
    else
        echo "📦 Installing @th0rgal/ralph-wiggum..."
        npm install -g @th0rgal/ralph-wiggum
        echo "✅ @th0rgal/ralph-wiggum installed"
    fi
fi

echo ""
echo "========================"
echo "✅ CI tools setup complete"

# Check authentication
if [ -n "$COPILOT_GITHUB_TOKEN" ] || [ -n "$GH_TOKEN" ] || [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ Authentication token detected"
else
    echo "⚠️ No authentication token found."
    echo "   Set COPILOT_GITHUB_TOKEN, GH_TOKEN, or run: copilot /login"
fi

# Check model configuration
if [ -n "$COPILOT_MODEL" ]; then
    echo "✅ Model: $COPILOT_MODEL"
else
    echo "ℹ️ COPILOT_MODEL not set — using Copilot default model"
fi
