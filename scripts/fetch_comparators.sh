#!/usr/bin/env sh
# Fetches the three source skills' current SKILL.md into evals/comparators/
# (gitignored) so eval runs always compare against their live published
# version, never a copy vendored into this repo.

set -eu

script_dir=$(dirname -- "$0")
out_dir="$script_dir/../evals/comparators"
mkdir -p "$out_dir"

fetch() {
  repo="$1"
  path="$2"
  out="$3"
  gh api "repos/$repo/contents/$path" --jq '.content' | base64 -d > "$out_dir/$out"
  echo "wrote $out_dir/$out"
}

fetch "JuliusBrussee/caveman" "skills/caveman/SKILL.md" "caveman.md"
fetch "DietrichGebert/ponytail" "skills/ponytail/SKILL.md" "ponytail.md"
fetch "ayghri/i-have-adhd" "skills/i-have-adhd/SKILL.md" "i-have-adhd.md"
