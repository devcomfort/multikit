#!/usr/bin/env bash
# ====================================================================
# Run Docker-based integration tests for the multikit CLI.
#
# Usage:
#   ./scripts/integration-test.sh          # build & run
#   ./scripts/integration-test.sh --build  # force rebuild
#   ./scripts/integration-test.sh --down   # tear down containers
# ====================================================================
set -euo pipefail

COMPOSE_FILE="tests/integration/docker-compose.yml"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

case "${1:-}" in
  --down)
    echo "🧹 Tearing down integration-test containers …"
    docker compose -f "$COMPOSE_FILE" down --rmi local --volumes --remove-orphans
    exit 0
    ;;
  --build)
    echo "🔨 Rebuilding images …"
    docker compose -f "$COMPOSE_FILE" build --no-cache
    ;;
esac

echo "🚀 Starting integration tests …"
docker compose -f "$COMPOSE_FILE" up \
  --build \
  --abort-on-container-exit \
  --exit-code-from test-runner

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Integration tests passed!"
else
  echo "❌ Integration tests failed (exit $EXIT_CODE)"
fi

# Clean up containers (images are cached for speed)
docker compose -f "$COMPOSE_FILE" down --volumes --remove-orphans

exit $EXIT_CODE
