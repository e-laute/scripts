#!/usr/bin/env bash
set -euo pipefail

ORG="${ORG:-e-laute}"
REPO="$ORG/GA-test"

declare -A SECRETS
SECRET_FILE=""

usage() {
  echo "Usage:"
  echo "  $0 --from-file ./secrets.env"
  echo "  $0 NAME1=VALUE1 NAME2=VALUE2 ..."
}

abort() { echo "Error: $*" >&2; exit 1; }

require_gh() {
  command -v gh >/dev/null 2>&1 || abort "gh CLI is not installed."
  gh auth status >/dev/null 2>&1 || abort "gh CLI not authenticated. Run: gh auth login"
}

parse_kv() {
  local kv="$1"
  [[ "$kv" == *"="* ]] || abort "Invalid secret spec '$kv' (expected NAME=VALUE)"
  local name="${kv%%=*}"
  local value="${kv#*=}"
  SECRETS["$name"]="$value"
}

load_env_file() {
  local file="$1"
  [[ -f "$file" ]] || abort "Secret file not found: $file"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" || "${line:0:1}" == "#" ]] && continue
    parse_kv "$line"
  done < "$file"
}

if [[ $# -eq 0 ]]; then usage; exit 1; fi
while (( "$#" )); do
  case "$1" in
    --from-file) shift; SECRET_FILE="$1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) parse_kv "$1"; shift ;;
  esac
done
[[ -n "$SECRET_FILE" ]] && load_env_file "$SECRET_FILE"

require_gh

echo "Testing with repository: $REPO"

existing=$(gh secret list -R "$REPO" --json name -q '.[].name')

for name in "${!SECRETS[@]}"; do
  if echo "$existing" | grep -q "^$name$"; then
    read -p "Secret '$name' already exists in $REPO. Overwrite? (y/N) " ans
    case "$ans" in
      [yY]*) ;;
      *) echo "  Skipping $name"; continue ;;
    esac
  fi
  if gh secret set "$name" -R "$REPO" --body "${SECRETS[$name]}" >/dev/null; then
    echo "  ✓ $name"
  else
    echo "  ✗ $name (failed)" >&2
  fi
done
