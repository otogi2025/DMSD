#!/usr/bin/env zsh
set -euo pipefail

# Create a short local path for opening the Xcode project.
# Usage:
#   zsh 00_admin/create_local_dev_symlink.sh

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="$HOME/dev"
LINK_PATH="$TARGET_DIR/DMSD"

mkdir -p "$TARGET_DIR"
ln -sfn "$SRC_DIR" "$LINK_PATH"

echo "Created/updated symlink:"
echo "$LINK_PATH -> $SRC_DIR"
echo "Open Xcode project from: $LINK_PATH"
