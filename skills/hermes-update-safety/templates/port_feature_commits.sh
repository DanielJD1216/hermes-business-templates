#!/usr/bin/env bash
# Rebuild the live uncommitted Hermes changes as one commit per feature, byte-check them against
# live, then cherry-pick the kept features onto TARGET. Writes only under OUT. Exit 3 = conflict.
# usage: OUT=<durable dir> TARGET=<commit> FEATURES=<feature-groups.tsv> port_feature_commits.sh
#   feature-groups.tsv lines: keep|drop <TAB> commit message <TAB> path   (each changed path once;
#   first appearance of a message sets commit order; "drop" = upstream ships it, verified first)
set -euo pipefail
LIVE=${LIVE:-$HOME/.hermes/hermes-agent}
: "${OUT:?}" "${TARGET:?}" "${FEATURES:?}"  # not GROUPS: bash reserves it (your group ids)
R=$OUT/repo
BASE=$(git -C "$LIVE" rev-parse HEAD)
rows() { grep -v -e '^#' -e '^$' "$FEATURES"; }
changed=$(git -C "$LIVE" status --porcelain --untracked-files=all | cut -c4- | sort)
diff <(rows | cut -f3 | sort) <(echo "$changed") || { echo 'STOP: groups do not match the live changes exactly'; exit 1; }

mkdir -p "$OUT"; test ! -e "$R"
git -C "$LIVE" diff --binary HEAD > "$OUT/original-tracked.patch"
untracked=$(git -C "$LIVE" status --porcelain --untracked-files=all | awk '$1=="??"{print $2}')
[ -z "$untracked" ] || tar -C "$LIVE" -czf "$OUT/original-untracked.tgz" $untracked
git clone -q --local --no-checkout "$LIVE" "$R"
cd "$R"
git cat-file -e "$TARGET^{commit}"
git config user.name 'local port'; git config user.email 'port@local.invalid'
git checkout -q --detach "$BASE"
git apply "$OUT/original-tracked.patch"   # working tree only: --index would put every group in the first commit
[ ! -f "$OUT/original-untracked.tgz" ] || tar -xzf "$OUT/original-untracked.tgz"
git switch -q -c local/base
rows | cut -f2 | awk '!seen[$0]++' | while IFS= read -r msg; do
  rows | awk -F'\t' -v m="$msg" '$2==m{print $3}' | xargs git add -A --
  git commit -q -m "$msg"
done
test -z "$(git status --porcelain)"
for f in $changed; do cmp -s "$f" "$LIVE/$f" || { echo "MISMATCH $f"; exit 1; }; done
echo "local/base: $(git rev-list --count "$BASE"..local/base) feature commits, every file byte-identical to live"

git switch -q -c port "$TARGET"
for c in $(git rev-list --reverse "$BASE"..local/base); do
  msg=$(git log -1 --format=%s "$c")
  if rows | awk -F'\t' -v m="$msg" '$2==m && $1=="drop"{f=1} END{exit !f}'; then
    echo "  dropped (upstream ships it): $msg"; continue
  fi
  if git cherry-pick -x "$c" >/dev/null 2>&1; then echo "  picked clean: $msg"
  else echo "  CONFLICT: $msg (resolve, commit, then pick the remaining local/base commits)"
       git status --porcelain | grep -E '^(UU|AA|DU|UD) '; exit 3; fi
done
echo 'all kept features replayed onto TARGET'
