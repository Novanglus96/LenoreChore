#!/bin/bash
# Usage: ./scripts/update-version.sh <version>
# Stamps the release version across the project, from semantic-release prepare.
#
# ── Why this is strict ──────────────────────────────────────────────────────
# The previous version listed backend/Dockerfile and frontend/Dockerfile, both
# of which stopped existing when the single-container consolidation replaced
# them with the root Dockerfile. Every release since printed
#
#     sed: can't read backend/Dockerfile: No such file or directory
#     sed: can't read frontend/Dockerfile: No such file or directory
#
# to the log and then exited 0 with "Updated version to X". Two more targets --
# App.vue and AppNavigation.vue -- had become silent no-ops when those files
# switched to reading the version from package.json, and produced no output at
# all. So four of eight stamps were dead and the release still reported success.
#
# `set -euo pipefail` plus an explicit existence check means a target that goes
# missing now stops the release instead of quietly not being stamped.
set -euo pipefail

VERSION="${1:-}"
if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>" >&2
  exit 1
fi

VERSION_FILE="scripts/version.txt"
DOCKER_FILE="Dockerfile"
MODEL_VERSION_FILE="backend/api/fixtures/version.json"
API_PY_FILE="backend/backend/api.py"
PACKAGE_JSON_FILE="frontend/package.json"

for f in "$DOCKER_FILE" "$MODEL_VERSION_FILE" "$API_PY_FILE" "$PACKAGE_JSON_FILE"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: version target '$f' does not exist." >&2
    echo "A stamp target has moved or been deleted. Fix this script rather than" >&2
    echo "letting the release publish an unstamped artifact." >&2
    exit 1
  fi
done

# Asserts the substitution actually matched, so a target that still EXISTS but
# whose pattern has drifted fails too. That is the case the old script could not
# catch: App.vue and AppNavigation.vue were present and simply never matched.
stamp() {
  local file="$1" pattern="$2" probe="$3"
  sed -i -r "$pattern" "$file"
  if ! grep -qE "$probe" "$file"; then
    echo "ERROR: stamping '$file' did not produce version $VERSION." >&2
    echo "The file exists but its version pattern no longer matches." >&2
    exit 1
  fi
}

echo "$VERSION" > "$VERSION_FILE"

stamp "$DOCKER_FILE" \
  "s/^LABEL version=\"[^\"]*\"/LABEL version=\"$VERSION\"/" \
  "^LABEL version=\"$VERSION\""

stamp "$MODEL_VERSION_FILE" \
  "s/\"version_number\": \"[^\"]*\"/\"version_number\": \"$VERSION\"/" \
  "\"version_number\": \"$VERSION\""

stamp "$API_PY_FILE" \
  "s/^api.version = \"[^\"]*\"/api.version = \"$VERSION\"/" \
  "^api\.version = \"$VERSION\""

stamp "$PACKAGE_JSON_FILE" \
  "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" \
  "\"version\": \"$VERSION\""

echo "Updated version to $VERSION"
