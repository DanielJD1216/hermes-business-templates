---
name: hermes-update-safety
description: "Use when updating Hermes Agent or checking update safety."
version: 1.1.0
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [hermes, update, local-patches, port, git, rollback, maintenance]
    related_skills: [hermes-agent]
---

# Hermes Update Safety

A git-installed Hermes can carry uncommitted local source changes in its checkout (`~/.hermes/hermes-agent` by default; the bundled scripts read `LIVE` or `HERMES_REPO` for another path). Every update path removes those changes from the running code without an error, so check first and port the changes before updating. The check is read-only, the port runs in a separate clone, and the update is a production change that needs the owner's approval. The owner, or an operator the owner names, restarts services.

## Why updates drop local changes

- `hermes update` stashes with `--include-untracked`, updates, then re-applies. Any conflict resets the tree and parks the whole stash, not only the conflicting files. Hermes keeps running; the features disappear.
- The Desktop Update button runs `--keep-stash`: it parks local changes by design.
- `hermes-update-autostash-*` entries in `git stash list` are changes that earlier updates parked. Review them before any drop.

## 1. Safety check (read-only)

1. `hermes update --check` gives the target release; `hermes update --plan` lists the services it restarts. Both are read-only.
2. Inventory: `git status --porcelain --untracked-files=all`, file dates, `git stash list`. Name each feature from its docs and test files.
3. Merge test without touching the tree:
   ```bash
   S=$(git stash create)   # commit object of tracked changes; no ref, no tree change
   git merge-tree --write-tree --name-only --merge-base=HEAD "$S" <target>   # exit 1 = conflicts
   ```
   Check each untracked path against the target with `git cat-file -e <target>:<path>`.
4. Plugins: `python3 scripts/plugin_compat.py <target>` reports removed internal imports, removed hook names and memory-provider abstract method changes. It is static; behavior needs tests.
5. Backups: read `updates.pre_update_backup` with `hermes config get` (a system Python may lack the YAML module). Legacy `false` means off, including the quick snapshot. `quick` skips files over 1 GiB, such as a large `state.db`. Use `--backup` (quick snapshot plus a HERMES_HOME zip that excludes `backups/` and `state-snapshots/`) for a large jump. The zip is all or nothing: if any SQLite file under HERMES_HOME fails its snapshot (a stray test database is enough), the zip is abandoned and the update continues without it. Measure its input first; `workspace/` alone can be tens of GB.
6. Restart coverage: `--plan` lists gateways only. The Desktop backend and T3 ACP sessions keep old code until they restart.
7. Activity: no running T3 turn (open `~/.t3/userdata/statev2.sqlite` read-only; `orchestration_v2_projection_provider_turns` with status `running` and a recent `started_at`), no cron run and no chat turn in flight. A `running` record that started before T3 Code's last restart is stale; for a live one, the thread's `updated_at` in `orchestration_v2_projection_threads` is recent.
8. Size: `git rev-list --count HEAD..<target>`. A patch version can still span thousands of commits.
9. ACP path: check which agent class `hermes acp` builds on the target (`acp_adapter/entry.py`; `HermesACPAgent.__new__` in `acp_adapter/server.py`). From v0.22.5 (not v0.22.2), `HermesACPAgent()` without a `session_manager` returns `GatewayACPAgent`, so T3 sessions run `acp_adapter/gateway_server.py`. Local changes to the in-process `server.py`, `commands.py` or `session.py` then do nothing in real T3 sessions, while tests that pass a `session_manager` still pass.
   - A T3 launch guard or policy that adds `reasoning_effort` to every delegated launch needs each target agent to advertise that option in its session `configOptions`. Otherwise T3 rejects the launch ("Unknown option reasoning_effort; supported options: _t3/session-mode"). Confirm that the target's ACP path advertises `reasoning_effort`. v0.22.5's `GatewayACPAgent` advertises no options without a local patch.

Report unsafe while any local change would be parked, a run is active, or no backup is configured.

## 2. Port local changes (no live change)

1. Write a feature list (`keep|drop <TAB> commit message <TAB> path`, every changed path once), then run `bash templates/port_feature_commits.sh` with `OUT=<private output dir> TARGET=<commit> FEATURES=<list>`. It saves the original patch and untracked tarball, rebuilds one commit per feature on the live HEAD, byte-checks every file against live, then cherry-picks the kept features onto the target. Exit 3 means a conflict.
2. Mark a feature `drop` only after proving the target ships the same behavior (same field or function, same semantics).
3. When upstream deleted the conflicting code, find where it moved with `git grep` on the target tree and re-apply the change there; keep upstream's version of the old file. Commit, then cherry-pick the remaining `local/base` commits.
4. Test with the canonical runner, baseline first:
   - Run `scripts/run_tests.sh <files>` in a subshell with `HOME` and `HERMES_HOME` pointing at a sandbox, plus `PYTHON_DOTENV_DISABLED=1 HERMES_DISABLE_LAZY_INSTALLS=1`. Activation then builds the project's own test environment inside the sandbox; pointing `UV_CACHE_DIR` at the real uv cache avoids downloading every package again. Never run it against the real home: setup can migrate production data.
   - Run the same files on the clean target, then on the port. A failure in both is not a port regression. Run each new test once without its fix as well: it must fail.
   - Do not set `HERMES_PYTHON` to a hand-built `pm.build_env` venv; it diverges from the canonical environment and times out on clean code.
   - Platform SDKs (slack, telegram, discord) are opt-in extras outside the default `[all]` test environment, while a live host may have them. Run those files once more against the real SDK: the canonical interpreter from `pm.testenv.testenv_python`, `env -i`, `PYTHONPATH=<repo>:<dir holding only the SDK packages>`, one subprocess per file.
   - Agent terminal tools time out on long suites. Split them or run them in the background.
5. Package in the private output dir: `git diff --binary <target> port` for update day, a `git format-patch` series for upstream PRs, and the original patch plus tarball for rollback, each with sha256. Prove the diff recreates the tested tree (`git rev-parse port^{tree}`) on a clean target worktree, then rehearse `templates/apply_port.sh` there.

## 3. Update day (owner's approval)

1. Quiet window. Take a fresh configuration backup.
2. `hermes update --backup --keep-stash --no-gateway-restart --yes`.
3. `bash templates/apply_port.sh` as a dry run, then with `--apply`. It refuses unless the checkout is clean at the target, and verifies the result equals the tested tree.
4. Before the restart, copy every profile's `state.db` with `sqlite3.backup()` into a private backup folder and compare session and message counts with live. The first start of the new version can migrate the schema, the quick snapshot skips files over 1 GiB, and the full zip may have been abandoned.
5. The owner or named operator restarts every affected service: the gateway (`hermes-gateway` when it runs as a systemd user unit), the Desktop backend and T3 Code.
6. Verify: fleet version in `hermes update --plan`; gateway log; Desktop reconnect; every profile's `state.db` `schema_version` and counts against the step 4 copies (the Desktop backend can log "behind SCHEMA_SQL" for a few seconds until the gateway migrates each store; that is expected); every enabled MCP server connects (`hermes mcp list` and the gateway log); a new T3 session; T3's view of each Hermes agent (after T3's next probe, minutes after the restart, it rewrites `~/.t3/caches/acpRegistry_<provider>.json`; every model's `capabilities.optionDescriptors` there must list `reasoning_effort`); one T3 delegated launch (a new session alone does not exercise launch-option validation); normal chat use. Record the evidence in the owner's private setup record.
   - T3 starts each agent on its profile default model unless T3's picker overrides it per thread; the T3 run payload records the pick as `modelSelection`.
   - Reasoning effort is not logged. It resolves session `/reasoning`, then `agent.reasoning_overrides`, then `agent.reasoning_effort`.
   - Scheduled jobs: an update can refuse a job's saved command line, for example a toolset name the new version no longer accepts, and the job then fails only at its next run. For each profile with jobs (`hermes -p <profile> cron list`), after each enabled job's first run on the new version, `hermes -p <profile> cron doctor` must report no issue and `hermes -p <profile> cron incidents` must show no new incident. Do not trigger extra runs only to check: a manual run repeats the job's side effects, cost and messages.
7. Keep the update's autostash until verification passes. Rollback: stash the applied port, check out the old commit, apply the autostash, `hermes pm repair`, restore config from the quick snapshot if the old code refuses the new config version, restore the step 4 `state.db` copies (old code against a migrated schema is untested), then restart.

## Pitfalls

- `git apply --index` stages every file, so the first per-feature commit swallows all features. Apply to the working tree only.
- Bash reserves `GROUPS` (your group ids); assigning it has no effect. Use another variable name.
- A kill loop or count over `pgrep -f <pattern>` also matches the shell running it. Filter on the real command and skip `$$`.
- Python 3.13+ `Path.resolve()` no longer raises on a symlink loop. Code or tests that rely on the error pass on 3.11 only. The repo's `.venv` can be a stale 3.11 while the runtime is 3.14, so test on the runtime's Python.
- Adapter test stubs given to `set_authorization_check` must accept keyword arguments (`thread_id`, `is_bot`); otherwise the base class treats the sender as unknown and guard tests fail.
- The live repo can be a blobless partial clone. A local clone cannot read some old history, and long-range `git diff` in the live repo fetches blobs over the network. Only the base and target trees are needed.
- An update can tighten a dependency's limits. v0.22.5 moved the MCP SDK from 2.0.0 to 2.3.0, whose Streamable HTTP client caps each server-sent event at 1 MiB, so a server with a large tool list never connects (`Server-sent event exceeded the 1048576 byte limit`). Upstream PR NousResearch/hermes-agent#143803 passes Hermes' own 10 MiB cap instead; until a release includes it, port that change as a local patch or wait for the release.
- Upstreaming the local changes is the durable fix; until then each update repeats this port.
- Upstream PR prep: one logical change per PR, and search open and closed PRs first (`gh search prs`, short terms; the search API allows 30 calls per minute), because many fixes already have competing PRs. Author commits with the GitHub `<id>+<login>@users.noreply.github.com` email; `.github/workflows/contributor-check.yml` fails unmapped emails. Set the clone's push URL to an invalid value so nothing is pushed by accident.
- Never switch branches in a checkout while a background test run uses it; run branch tests one after another from one driver script.
- Never load-check a plugin by starting Hermes with a temporary `HERMES_HOME`. The bootstrap builds a dependency environment for that data root (a dependency that needs a compiler, such as `python-olm`, can fail there) and can race a sync of the real install's environment (`installs/<id>/facts.json` can move to a new environment with the same lock). Run the plugin's own tests with the `.venv` interpreter; on the live interpreter, only execute the module file with the real `HERMES_HOME` and `python -I -B`, without constructing or initializing a provider. `-I` ignores every `PYTHON*` variable, so `PYTHONDONTWRITEBYTECODE=1` alone does not stop bytecode writes.
- A skill-resolution check against real profiles is not read-only. `build_skill_invocation_message` records a use for every skill it loads (`tools.skill_usage.bump_use`; the `skill_view` tool also records a view), which moves the curator's stale clock and creates usage records. Stub `tools.skill_usage._mutate = lambda *a, **k: None` before the check, and compare each profile's `skills/.usage.json` hash before and after.
