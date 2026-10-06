# Hermes Business Templates

Free, MIT-licensed starting setups for running a small business on [Hermes Agent](https://hermes-agent.nousresearch.com/docs). Each template installs a small team of AI bots, each a separate Hermes profile with its own Slack app, on a server the business owns, using the owner's own AI subscription or API keys.

We provide the foundation only: bots, playbooks, folders, scheduled checks and an installer. Your business details, tools and accounts stay yours.

| Template | Status |
|---|---|
| Creator + Education | v0.5.0 unreleased candidate: opt-in local memory-draft review, global uninstall refusal and private recovery archives. Independent review pending. |
| Project Services | planned |
| Industrial Supplier | planned |

## What the Creator template installs

It copies a working creator business: one lead per department, the way a normal org chart grows. Rename anything to fit yours.

| Bot | Slack channels | Does |
|---|---|---|
| Creative Director | `#media-video`, `#media-edit`, `#media-newsletter`, `#marketing-distribution`, `#offers-optimization` | Leads Media and Marketing: topics, scripts, edits, newsletter, clips, community and sponsor drafts. 24 playbooks. |
| CTO | `#build-architect` | Leads Build: plans, system maps and PRDs. Never builds; hands each build to Engineer on a Kanban card. |
| Engineer | `#build-engineering` | Builds from the CTO's cards in `<projects>/<project>`, reports progress on the card, and asks the CTO when a plan is vague. |
| Ops | `#agents-report` (posts only) | No Slack app and no memory. Runs the scheduled jobs: morning approvals list, nightly review, memory and update watchdogs. |
| Editor desk | `#ext-editor-<name>`, one per editor | Optional. Answers one outside editor from a brief you write, inside a locked-down container. |

Your own main agent (your assistant) is not replaced. The installer records its limited Kanban and Ops-routing settings changes for uninstall; it does not share the main agent's skills with the bots. Every bot drafts; nothing is published, sent, priced or signed without your `approve`.

Also installed: a shared business folder with `canon/` (your business, offers, voice, brand and standing rules) plus one folder per bot, and a Kanban board named `creator`. Only you edit `canon/`, except `offers.md`: the Creative Director keeps it current and saves a change only after your `approve`.

## How the bots work together

- Each bot answers in its own channels without an @mention, and stays quiet when you @mention a different bot there.
- Bots hand work to each other by @mentioning the other bot in the thread they are working in, with the whole brief in that message. A bot can only reply in its own thread, so setup invites each bot into the channels of the bots that hand it work: CTO into the Creative Director's channels and `#build-engineering`, the Creative Director and Engineer into `#build-architect`.
- A bot hears another bot only when @mentioned, and a thread follow-up wakes only the bot you mentioned, so they never loop.
- Only you can run commands such as `!approve` or `!restart`. A bot that mentions another bot with a command gets a refusal.
- Say "Create a new project called hello world, plan it and build it" in `#build-architect`. The CTO writes the plan, creates a card for Engineer, and the result posts in `#build-engineering`. Ask the Creative Director for a landing page and it hands the build to the CTO the same way.

## Setup

```bash
git clone <this repo> ~/hermes-business-templates
cd ~/hermes-business-templates
./hbt setup creator
```

Setup walks you through one action at a time and checks each one before the next. You can stop anywhere; run it again and it picks up where you left off.

1. Asks for your timezone, your projects folder and your Slack member ID, then installs the bots, folders, board and jobs.
2. For each bot: prints its Slack app file. You create the app, then paste its two tokens into a hidden prompt. Setup checks them with Slack and refuses a token another bot already uses.
3. Finds each bot's channels by name and tells you which ones still need `/invite`.
4. Points Ops at `#agents-report` through your main agent's bot.
5. Asks you to run `hermes gateway restart` once.
6. Asks you to post "what's your job here?" in each bot's channel and waits for the right bot to answer.
7. Your first build: the hello-world card from CTO to Engineer. Engineer hands the checked draft to manual owner review, without reviewer reassignment. Inspect the draft and record your verdict on that exact card in its original approval thread, as below. Setup waits for a unique Done Engineer card in the recorded `<projects>/hello-world` folder, not any unrelated completed build.

Then ask your main agent to run the canon interview in `canon/INTERVIEW.md`. `./hbt status creator` shows what is installed and the next setup step.

### Approving a checked draft

Customer installs keep `review_dispatch: false`: you review the draft manually, and the card stays assigned to its implementer. CTO must not complete a draft just because implementation tests passed. In the original draft approval thread, use the actual card ID in one of these replies:

```text
!kanban --board creator complete <card-id> --summary "Owner approved this draft only"
!kanban --board creator reopen-review <card-id> --reason "<required changes>"
!kanban --board creator archive <card-id>
```

The commands mean approve this draft, request changes, or reject/stop the card, respectively. Archive keeps the record and removes active work; it is not Done. Reopen-review returns the card to its implementer. Do not use `request-changes` for idle manual review; it requires an active reviewer run. `!approve` is for dangerous-tool approval, not a draft/card verdict. Conversational `approve`, `change: <what>`, or `reject` remains owner intent until a recorded board outcome is reported; this template adds no free-text automation.

If Slack commands are unavailable, run the equivalent `hermes kanban --board creator complete <card-id> --summary "Owner approved this draft only"`, `hermes kanban --board creator reopen-review <card-id> --reason "<required changes>"`, or `hermes kanban --board creator archive <card-id>` in a terminal. This is a fallback, not another approval requirement. One native command records one decision.

Review, requested changes, archive/rejection, blocked work, text-only approval and a setup timeout leave first-build onboarding incomplete. Setup prints pending guidance; no automatic approval is recorded. Draft completion alone does not authorize publishing, deployment, external sends, scheduling or signing.

The morning approvals list groups cards by role, oldest current review first, and links to the original draft approval thread when its provenance is available. Leads carry already-known origin context in the card body; workers record it in the existing review metadata using the template's `approval_thread` convention in `workspace/RULES.md`. This is not a native task field. The helper uses the latest review request and corresponding run, not an earlier draft or task creation time. It validates the recorded Slack root-message URL without inventing one. Result-channel subscriptions cannot identify an origin. Legacy, missing, invalid, conflicting or non-Slack provenance produces an explicit `approval thread link unavailable (<reason>)` with the title and card ID. Missing review time is also explicit. No link-entry chore is required. A failed local read reports a failed digest, never "Nothing waiting for approval."

### Keeping the bots in step

Each bot has separate settings and permissions; selected playbooks now use one shared library. `./hbt check creator` compares installed provenance and prints one line per gap with its fix:

- missing or modified shared package files, unresolved migration conflicts, duplicate skill names, missing selected roots or missing bundled opt-out/manual;
- a tool that is turned on but not signed in, or lost its sign-in;
- a bot that does not hear another bot that hands it work, or is not in that bot's channel;
- a scheduled job whose last run failed;
- a date under "Dates coming up" in `canon/offers.md` that has passed.

Ops runs it every morning and posts only when the gaps change, and once a week while they stay open.

### Shared skills and native compatibility

The durable library lives at `<install-root>/business-templates/creator/skills/`, where install-root is the Hermes home used for the installation. It does not depend on this checkout staying in place:

- `template/<role>/<skill>/` holds the unchanged 24 Creative Director and four Ops playbooks.
- `bundled/<category>/<skill>/` holds stock packages from the installed Hermes source, preserving their support files and upstream attribution. The installer never uses the owner's writable skills folder, another profile or a personal tap as stock.
- Each bot gets an actual YAML `skills.external_dirs` list of exact selected package directories, not access to the whole library. Existing custom entries keep their order. Disabled, platform-disabled, auto-load and skill-creation settings remain yours.
- `hermes-agent` stays native-managed in each profile's local skills folder. The native `.no-bundled-skills` marker prevents nonessential packages from being seeded back into migrated profiles. Explicit `hbt update` refreshes shared stock; there is no background skill sync service.
- Sharing content grants no tools, MCP access or credentials. Trusted same-user bots are not filesystem-isolated. Desks receive no shared roots or mounts and keep their existing rootless-container policy.

Fresh stock selections are declared in `templates/creator/template.yaml`: ten for the Creative Director, seven for CTO, eleven for Engineer and none for Ops or desks. Migration preserves each existing role's proven, still-present native-bundled selection instead of shrinking it to those defaults. User-deleted packages are not reintroduced, and unknown/local/hub packages stay local. For example, an older Ops profile may retain its pre-existing stock selection, while a fresh Ops profile gets only its authored playbooks plus the native manual.

Compatibility is capability-checked, not inferred from a minimum patch number. Required stock packages, native external roots, disabled handling, essential-only seeding and profile distributions must be available before writes begin. Use Hermes's own dependency-complete Python (`HBT_PYTHON` can select it). Missing features/packages produce an upgrade message. A bundled-source override outside the installed source tree is refused because its provenance is unverified; package-manager layouts using such overrides need separate compatibility review. See the [native skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) and [profile distributions](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions).

Native listing precedence is not a safe collision policy: native `skill_view` refuses ambiguous local/external names. Migration therefore keeps a customized local or custom-external package active and omits that package's managed shared entry for the affected bot. Other bots can still use the pristine shared package.

### Desks for outside editors

```bash
./hbt desk creator desk-editor --name sam --guest U0123ABCD --channel ext-editor-sam=C0123ABCD
./hbt desk creator desk-editor --name sam --tokens      # hidden prompt for the desk's Slack tokens
```

Each editor gets their own Slack app, channel and folder (`desks/editor-sam`). A desk answers only its guests, only in its channel, with file tools only, inside rootless Docker with no network, and it sees nothing but its own folder. Desks install only where rootless Docker runs.

### Scheduled jobs

All times follow your timezone.

| Job | When | Posts |
|---|---|---|
| Morning approvals list | 07:30 daily | Every card waiting for your approval, or "Nothing waiting for approval." |
| Nightly review | 21:00 daily | Each bot's failed checks with the file or card behind them, or "All nightly checks passed." |
| Memory-draft review | 21:30 daily, initially paused | Local count summary only. Never posts drafts, memory or a model summary to Slack. Requires explicit opt-in. |
| Memory watchdog | every 5 minutes | Only when memory goes down, every 6 hours while it stays down, and when it recovers. |
| Update check | Mondays 09:00 | Only when a newer template version exists. |
| Drift check | 08:00 daily | Only when `./hbt check` finds new gaps, and weekly while they stay open. |
| Comment pull, member questions | paused | Resume once you drop exports into `ops/incoming/`. |

## What has been tested

The v0.5.0 memory-review checks use synthetic drafts and deterministic reviewer fixtures. Native memory storage, pending proposals, cron job creation and script execution, profile installation/update and whole-profile uninstall were exercised in disposable homes on Hermes source `7565f6477c211c315110fc12173e500f013366fc`, using Python 3.11.15. Both `HOME` and `HERMES_HOME` were set before native imports. Network and mount namespaces hid live profile/credential trees and exposed only read-only native code at the installed package's source path; filesystem audit guards restricted reads/writes and refused external-memory initialization. The script resolves native source from the installed `hermes_cli` package and fails closed if that runtime is unavailable. These checks are not a claim of containment against hostile native subprocesses or a test of a live client's runtime layout.

The tested scenarios include add and pinned replacement, discard archives, invalid-response refusal before mutation, native batch limits/security scanning, stale pins, replay protection, unknown-outcome retention, cleanup-only retry, bounded attempts, concurrent process exclusion and a real reviewer-child wall timeout. Fixtures replace the auxiliary transport before provider resolution. Installer checks include a real v0.4.0 upgrade, explicit enable/disable, owner-paused job retention, deleted-job retention, exact-nonce creation recovery, same-name ownership refusal, local-only wiring, zero-write dry-run, whole-uninstall refusal and exact-byte archival before native deletion.

No live provider call, model judgment-quality evaluation, provider sign-in, live scheduler/gateway operation, Slack delivery, live OpenViking, production installation or release was tested or authorized. The following table records earlier shared-skills evidence, not new memory-review results:

| Area | Result |
|---|---|
| Unit tests | 63 pass: existing installer tests plus package ownership, config/marker preservation, unknown provenance, collisions, dry-run, repeat update, interrupted activation, missing-file repair and protected uninstall. These tests use synthetic fixtures. |
| Native sandbox execution | 63 CLI/discovery/seeding checks passed using native Hermes `0.21.5+6662.g343500b`, source `343500b3547e12530457c2fda60ec687e25118b4`, with its existing Python 3.11.15 environment. Fresh install, status/offline check, exact shared skill view, disabled refusal, local manual and role/private-owner exclusions passed. |
| Real v0.3.2 migration | Baseline installer ran in separate homes, followed by pristine and customized updates. Added support bytes, custom external roots, disabled settings and deleted packages survived repeated update. Native reseeding did not recreate nonessential local copies. |
| Recovery and removal | Injected failure on the second profile's activation restored old packages/settings; retry passed. Missing shared assets were repaired without losing a local shadow. Subset install, existing desk settings and native manual seeding passed without starting Docker. Uninstall preserved custom local/shared bytes, recovery archives and unrelated owner settings/skills. |
| Isolation | Both HOME and HERMES_HOME were sandboxed before startup, inherited overrides were removed, lazy installs were disabled, jobs used local delivery and checks were offline. Final native/unit runs were additionally kernel write-confined to their evidence directory with Linux Landlock ABI 3. |

**Not proven by this candidate:** real Slack onboarding or messages, live gateway handoffs/cards, live OpenViking, actual Docker desk operation, provider sign-in, scheduled job delivery or an actual Hermes self-update. Older live/simulated v0.3 evidence is not a new v0.4 integration result. The managed Python launcher lacked dependencies in a new isolated home with lazy installs disabled; native acceptance used the existing dependency-complete Hermes venv instead, not fabricated CLI results. Complete Hermes's own dependency setup before installing a template. No template release or client rollout has occurred. v0.1 installs still require uninstall before moving to the newer profile names.

## Requirements

- A Linux server (or WSL2) with Hermes installed and its Python dependencies ready. The shared-skills capability checks above must pass; Hermes 0.21 alone is not a compatibility guarantee. Your main agent must be connected to Slack for live onboarding.
- Your main Hermes profile logged in to a model provider (`hermes model`). The bots use the same login and model settings.
- Optional: [OpenViking](https://github.com/volcengine/OpenViking) for long-term memory. Without it, bots use Hermes's built-in memory.
- Optional: rootless Docker, needed only for desks.

## Update

```bash
cd ~/hermes-business-templates && git pull && ./hbt update creator
```

Updates replace template-owned `SOUL.md`, scripts and generated `AGENTS.md` files through native profile distributions. Staged distributions no longer carry skill roots, so native update cannot overwrite customized local playbooks. Template-managed Slack/Kanban wiring is reapplied; unrelated settings, canon, workspace content, credentials, memories and sessions are retained. Shared packages are repaired/refreshed only when missing or still installer-owned, never force-overwritten over edits.

### Migration conflicts and recovery

Run `./hbt update creator --dry-run` first. Preflight reads old staged distributions before restaging, compares complete packages (including support files and additions), and previews removals, selected roots, marker changes and conflicts without writing. Missing/untrustworthy baselines count as unknown, not permission to overwrite.

Before activation, the installer creates a unique durable archive under `<install-root>/business-templates/creator/backups/skills-<id>/`. It contains local skills, relevant config/markers, previous staged distributions, shared assets and the previous install record. The existing `record.json` stores library ownership, package-relative SHA-256 hashes, source/version, role selections, exact managed entries, original settings and archive/conflict references. `status` shows these pointers; `check --offline` checks installed hashes rather than assuming a newer checkout was installed.

An update with retained conflicts exits **2**, and reports them explicitly. A clean update exits **0**. There is no force-overwrite switch or automatic merge:

1. Read `status` and `check --offline`, and copy any newer edits to a separate recovery location before changing them.
2. To keep a customized local/external package, leave it there. Its shared entry stays omitted and the intentional conflict remains visible. Resolve any pre-existing ambiguity between two user sources yourself; the installer does not delete either.
3. To return to the managed version, move the entire customized package out of every active discovery root into an archive (do not merely move it to another category in the same skills tree). For a custom external source, remove only that entry from the affected profile's native configuration after preserving it. Run `update` again, then `check --offline`. A modified shared package follows the same rule: preserve/move it first, then let `update` rebuild the missing managed package.
4. An interrupted migration retains a checkpoint. Retry `update`; it restores missing bytes in absent or partially deleted local packages and the previous managed settings from the recorded archive before replanning. Surviving bytes must match the archive. If new owner edits conflict with recovery, it refuses rather than overwriting them and retains the journal. A failed fresh install stays `pending`; run `uninstall` to retain its recovery archives, then retry `install`.

For a manual rollback, pause work in the affected bots and preserve all post-migration edits first. Use the archive's `record.json` and `profiles/<name>/` snapshots together: remove the new managed external entries before restoring old local skill packages, restore the previous marker state, and restore the matching staged `dist/` and native distribution manifest so its stable source remains valid. Move the current library into a separate recovery archive before restoring an older record that does not own it. Merge unrelated later settings rather than blindly replacing an entire config. Verify native skill list/view and `check --offline` before resuming work. Do not erase recovery archives.

## Uninstall

```bash
./hbt uninstall creator             # removes profiles, jobs and our settings; archives the board
./hbt uninstall creator --delete-workspace   # also deletes the business folder
hermes gateway restart
```

Uninstall now starts with one read-only preflight of **every recorded profile**, including Ops and desks. An unrelated job, ambiguous identity, unsafe path, unreadable store or uncovered owner file refuses the entire uninstall before backups, job changes, profile deletion, configuration writes or board archival. Paused and disabled owner jobs also block removal. `--yes` and `--delete-workspace` do not bypass this gate. Dry-run performs the same checks without writing.

Resolve the reported conflict before retrying. Move uncovered files outside all deletion roots yourself, preserving their bytes. For an unrelated job, explicitly relocate the workload and verify its operation under the new identity before removing the old job yourself. **Backing up jobs.json does not preserve a running job.** The installer does not relocate workloads, infer ownership from a job name or report partial profile retention as successful uninstall. An interrupted shared-skills checkpoint requires explicit `update` recovery before uninstall.

After all profiles pass, uninstall takes the memory-review run lock and preserves the current covered bytes outside the profiles. It stops only confirmed installer-owned jobs, verifies their removal, preserves logs changed by teardown, and checks the inventory again before native whole-profile deletion. A later race or preservation failure stops unsafe deletion but can leave archives, stopped jobs or earlier removed profiles. This is an all-or-nothing precheck, not a transaction or automatic rollback over native deletion.

Preservation coverage is deliberately bounded:

- Existing local `skills/`, `config.yaml`, `.no-bundled-skills` and `distribution.yaml`, plus complete discovered skill packages under endangered `external_dirs`/`create_dir` roots. Non-skill siblings are not covered.
- All remaining `memories/` and `pending/memory/` files, regardless of enrollment, origin or eligibility. Review receipts/state and review archives remain outside deletion roots.
- Regular `backups/config/config.yaml.good.*`, `logs/agent.log`, `logs/errors.log`, and their native positive-integer rotated log variants. These are preserved data, not disposable files. Changed/customized bytes in this narrow coverage receive new archives; a stale archive never justifies deletion of newer bytes.

New memory/uninstall archives use directories with mode `0700`, files with mode `0600`, verified SHA-256 hashes and an inventory of original size, mode and modification time. Existing shared-skills recovery copies retain source file metadata inside a private archive root. Archives are never pruned here. Already-preserved data qualifies only when its exact current bytes match a known recorded archive. Disposable exceptions are limited to verified shipped SOUL/scripts, the validated owned cron store, its empty native lock, reconstructible unmodified Ops settings and the exact one-newline `.env` produced for an unconfigured role. Any nonempty credential/settings content in `.env`, unknown script, session, non-memory pending file, extra log or other uncovered file refuses removal.

Archived custom skills survive but are no longer active in removed profiles. Only recorded managed external entries and pristine owned shared packages are removed; original marker/settings values are restored where still installer-owned. Modified/unrecognized shared content and all recovery archives remain. Default-profile skills, custom external directories outside removed profiles, external memories and Slack apps are not deleted. The business folder stays unless explicitly requested for removal, and the board is archived.

Custom path strings and their order remain unchanged. Planning, checks and archival resolve `${HERMES_HOME}` and relative skill paths against the consuming profile, not the installer home. Archival includes endangered packages even when a configured root is an ancestor of a removed profile; it excludes packages in unrelated profiles. Regression checks exercised a partial package deletion, native collision refusal followed by successful custom loading, and exact archived bytes after native whole-profile deletion. A focused five-gate native regression verified ancestor-root preservation and outside-package exclusion. Its two update attempts correctly refused duplicate native manuals exposed by the broad root; uninstall still preserved the custom package.

## Memory

With OpenViking running, each bot gets its **own memory account**, so bots cannot see each other's memories. Facts every bot needs belong in `canon/`, not in shared memory. Ops keeps no memory. Bots that run Kanban cards save memories without an approval prompt, because a card runs in the background where nobody can click one.

### Optional native memory-draft review

Fresh installation and legacy upgrade default to `off`. To authorize review, use one explicit owner command:

```bash
./hbt update creator --memory-review add-only
./hbt update creator --memory-review add-replace
./hbt update creator --memory-review off
```

The same option is available on `install`. An ordinary `update` preserves the recorded mode and owner-paused state; a deliberately deleted recorded job stays deleted. The installer stores the policy, enrolled installed non-Ops roles, timestamp, stable installation root, recovery paths and exact owned job identity in its existing `record.json`. Ops settings receive only an installation-root reference; unrelated keys remain unchanged. A create-before-checkpoint interruption is reconciled by the persisted ownership nonce, never by adopting a matching name.

- `add-only` authorizes applying original add proposals and rejecting eligible proposals. `add-replace` additionally authorizes original, pinned **whole-entry replacements**. Replacement can remove facts from the active entry; the full preimage is retained.
- Automatic `remove` is always forbidden. A batch with remove or an unauthorized replace remains pending as a whole, even when the reviewer requests discard. Discard rejects a proposal; it does not delete an existing memory entry.
- Only native pending records with `subsystem=memory` and `origin=background_review` from enrolled roles qualify. Default, Ops, desks and unrelated profiles are not enrolled. Foreground and unknown origins stay pending.
- Each draft uses its original profile and `memory` or `user` target. There is no shared USER.md and no default-profile fan-out. Profile-local USER.md differences or absence alone are not drift; no cross-profile copying is required.
- The reviewer can return only apply/discard/retain decisions and reasons. It cannot supply edited operations, new content, paths or policy. Missing decisions retain. Invalid or duplicate decisions reject the entire response before memory or queue mutation.
- Original pins, native enabled flags, configured limits, threat scanning and per-batch atomicity remain authoritative. Opt-in does not enable a disabled target, change native approval flags or change background proposal generation.

Ops calls its existing selected model/provider through the native text-only auxiliary interface in a child process. There are no tools, normal chat sessions, agent construction, OpenViking calls, reviewer memory writes or transcript learning. The implementation supplies no API key, hardcoded model or new fallback provider. Unsupported native interfaces or unresolved Ops configuration retain drafts with a local error. Existing provider authentication is still required for a real nonempty review and has not been tested by fixtures.

Each run admits at most 20 eligible drafts and 128 KiB of serialized input. Oversized drafts are retained, not truncated. There is one reviewer invocation and no script-level model retry, with a maximum 120-second child wall deadline or a lower native cron script timeout. Both native delta streams and completed-message responses use the same text-only validation. After three unsuccessful attempts for an unchanged input/policy fingerprint, that draft remains for owner review. The original draft hash is saved before the first review, including reviews that retain or fail. Policy or current-memory changes can reset the retry count but cannot authorize changed bytes under the same ID. An older attempt record without an identity hash requires owner reconciliation, not automatic repinning. Off and empty eligible queues do not call a reviewer or create recovery archives. A nonblocking kernel lock excludes overlapping scheduled/manual runs.

Before apply or discard, the script saves exact pending bytes, memory bytes or an absence marker, checksums and policy/source fingerprints in a unique private directory under `<install-root>/business-templates/creator/backups/memory-review/`. The memory preimage is captured inside the native mutation lock. Compact receipts at `memory-review/state.json` record preparation before mutation and completion around queue cleanup. If apply succeeds but cleanup fails, later runs only retry cleanup. A prepared/unknown outcome, changed/reused ID, changed draft or conflicting target requires recovery; matching current text alone never authorizes replay. Separate drafts can finish independently; there is no multi-profile transaction.

### Owner recovery and restoration

1. Read `./hbt status creator` for the exact job and recovery paths. Pause the owned job with `hermes -p ops cron pause <job-id>` and stop manual runs. Preserve later owner edits before any restoration.
2. Inspect the exact profile/ID receipt locally. Verify its `archive_sha256` against `preimage.json`, then verify the pending and memory SHA-256 values after Base64 decoding. Confirm the profile, target and original pending ID. Do not put archive content in a chat or report.
3. First restore into a separate disposable home. Restore decoded pending bytes to that profile's `pending/memory/<id>.json`. Restore decoded memory bytes to `memories/MEMORY.md` or `memories/USER.md`, or preserve the recorded absence. Verify byte equality and native loading there. Do not overwrite newer production memory automatically.
4. Reconcile any later edits and unknown mutation outcome yourself. Prefer retaining completed receipts for replay protection. Clear only the exact recovery/attempt record after reconciliation and resolution of its pending file; never delete the whole state file or archive tree to force a retry.
5. Use the existing native pending-review interface for any proposal that still needs individual owner judgment. Resume only the confirmed owned job after the policy, memory and queue agree.

`status` and `check --offline` expose policy, job state, counts and recovery pointers, never memory prose or raw reviewer output. The memory-draft job's delivery remains local through install, update and Slack connection. It does not replace the separate 21:00 operational/Kanban review or the memory watchdog.

## Known limits

- OpenViking has no login in its default local setup. Any program on the server can read any memory account by name, so keep the server to trusted software.
- Slack is the only chat platform tested.
- Messages you post in `#agents-report` go to Ops, because that route is how Ops posts through your main agent's bot. Keep the channel for system output.
- Turning on Kanban for the CTO's Slack tools saves Hermes's full default tool list for that bot, so it will not pick up tools Hermes adds to its defaults later. Re-run `hermes -p cto tools enable kanban --platform slack` after a Hermes update if you want them.
- A full install takes a few minutes. Native Hermes handles profiles, board/jobs and regular settings; the installer publishes verified shared packages and atomically updates exact native external-root lists.

## Tests

```bash
~/.hermes/hermes-agent/venv/bin/python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.
