#!/usr/bin/env bash
# Update day: apply a tested port diff onto a clean checkout at TARGET, then prove the working tree
# equals the tested tree. Dry run by default; --apply writes the working tree only (never commits,
# stashes, or restarts anything).
# usage: DIFF=<file> DIFF_SHA=<sha256> TARGET=<commit> TESTED_TREE=<tree> apply_port.sh [--apply]
#   TESTED_TREE = `git rev-parse port^{tree}` in the port clone where the tests passed.
set -euo pipefail
LIVE=${LIVE:-$HOME/.hermes/hermes-agent}
: "${DIFF:?}" "${DIFF_SHA:?}" "${TARGET:?}" "${TESTED_TREE:?}"

[ "$(sha256sum < "$DIFF" | cut -d' ' -f1)" = "$DIFF_SHA" ] || { echo 'STOP: diff changed since testing'; exit 1; }
[ "$(git -C "$LIVE" rev-parse HEAD)" = "$(git -C "$LIVE" rev-parse "$TARGET^{commit}")" ] \
  || { echo "STOP: $LIVE is not at $TARGET"; exit 1; }
[ -z "$(git -C "$LIVE" status --porcelain --untracked-files=all)" ] \
  || { echo 'STOP: working tree not clean (run the update with --keep-stash first)'; exit 1; }
git -C "$LIVE" apply --check "$DIFF"
echo 'check passed: the tested changes apply cleanly'
[ "${1:-}" = --apply ] || { echo 'dry run only; rerun with --apply'; exit 0; }

git -C "$LIVE" apply "$DIFF"
idx="$(mktemp -d)/index"; trap 'rm -rf "$(dirname "$idx")"' EXIT
GIT_INDEX_FILE=$idx git -C "$LIVE" read-tree HEAD      # temporary index: the real index stays untouched
GIT_INDEX_FILE=$idx git -C "$LIVE" add -A
tree=$(GIT_INDEX_FILE=$idx git -C "$LIVE" write-tree)
[ "$tree" = "$TESTED_TREE" ] || { echo "MISMATCH: tree $tree != tested $TESTED_TREE"; exit 1; }
echo "applied: working tree == tested tree ($tree)"
