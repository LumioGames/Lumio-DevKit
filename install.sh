#!/usr/bin/env bash
set -euo pipefail

# Local checkout: use its exact source. Piped download: fetch the public main branch.
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  devkit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -f "$devkit_root/tools/install.py" && -f "$devkit_root/plugin/plugin.json" ]]; then
    exec python3 "$devkit_root/tools/install.py" "$@"
  fi
fi
command -v git >/dev/null || { echo 'Install git before running this installer.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'Install Python 3 before running this installer.' >&2; exit 1; }
devkit_temp="$(mktemp -d)"
trap 'rm -rf "$devkit_temp"' EXIT
git clone --quiet --depth 1 --branch main https://github.com/LumioGames/Lumio-DevKit.git "$devkit_temp/repo"
python3 "$devkit_temp/repo/tools/install.py" "$@"
