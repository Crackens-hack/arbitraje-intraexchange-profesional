#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if ! command -v tree >/dev/null 2>&1; then
  echo "pre-commit: 'tree' not installed; skipping repo_tree.txt update" >&2
  exit 0
fi

tree -a -I '.git|.githooks|__pycache__|venv|.vscode|.idea|node_modules|.cache|.mypy_cache|.ruff_cache|.pytest_cache' > repo_tree.txt
git add repo_tree.txt
