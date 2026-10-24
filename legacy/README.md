# Historical Creator backend

**Not the customer onboarding path.** These are preserved historical instructions,
not current baseline requirements or proof of current runtime acceptance. Return
to the [customer entrypoint](../README.md) for new setups. Do not follow the commands
below without a separately requested legacy operation and an impact review.

The original runtime remains at [installer/](../installer/), [hbt](../hbt),
[templates/creator/](../templates/creator/) and [tests/](../tests/). Commands below
assume the repository root, not this directory. Those paths stay stable to avoid
breaking existing installations and maintenance automation. Nothing here authorizes
removing an installed profile, job, board, account, workspace or memory.

Historical instructions below are preserved from the previous root README. They
include superseded role, schedule, Slack and optional-memory assumptions.

| Template | Status |
|---|---|
| Creator + Education | v0.5.0 unreleased candidate. Shared skills, memory review, recovery refusal and the G1/G3/G4 corrections have completed bounded independent review. G5 documentation/output cleanup awaits independent review. No release or live acceptance. |
| Project Services | planned |
| Industrial Supplier | planned |

## What the Creator template installs

It copies a working creator business: one lead per department, the way a normal org chart grows. Rename anything to fit yours.

| Bot | Slack channels | Does |
|---|---|---|
| Creative Director | `#media-video`, `#media-edit`, `#media-newsletter`, `#marketing-distribution`, `#offers-optimization` | Leads Media and Marketing: topics, scripts, edits, newsletter, clips, community and sponsor drafts. 24 playbooks. |
| CTO | `#build-architect` | Architecture, system maps, PRDs and bounded in-thread builds. Plans or independently reviews when development orchestration is selected. |
| Engineer | `#build-engineering` | Implements and tests approved scope in `<projects>/<project>`, directly in-thread or as the selected implementation owner. No mandatory CTO planning stage. |
| Ops | `#agents-report` (posts only) | No Slack app and no memory. Runs the scheduled jobs: morning approvals list, nightly review, memory and update watchdogs. |
| Editor desk | `#ext-editor-<name>`, one per editor | Optional. Intended to answer one outside editor from your brief under the rootless-container policy below; actual enforcement needs final selected-path acceptance. |

Your own main agent (your assistant) is not replaced. The installer records its limited Kanban and Ops-routing settings changes for uninstall; it does not share the main agent's skills with the bots. Every bot drafts; nothing is published, sent, priced or signed without your `approve`.

Also installed: a shared business folder with `canon/` (your business, offers, voice, brand and standing rules) plus one folder per bot, and a Kanban board named `creator`. Only you edit `canon/`, except `offers.md`: the Creative Director keeps it current and saves a change only after your `approve`.

## How the bots work together

- Each bot answers in its own channels without an @mention, and stays quiet when you @mention a different bot there.
- Work stays in its originating conversation by default, including implementation and testing. A Creative Director request for a simple page does not automatically go to CTO or Engineer. Ask "Finish this here, or use the Herdr project setup?" only when intent is genuinely unclear and orchestration materially helps.
- When the owner explicitly selects orchestration or has established it for the project, use one coordinating conversation, one implementation owner per task and independent review when needed or required. The coordinating conversation need not move into Herdr. This template does not install Herdr or provide a new handoff bridge; agents must verify the available sessions, transport and return route before using them.
- For a selected Slack handoff, @mention the receiving bot in the original thread with the whole brief. Setup supplies peer channel membership instructions. Existing Kanban tasks and separately approved Ops jobs retain their scope; code alone does not require a card. Do not delete boards, move active work or add reporting destinations implicitly.
- A bot hears another bot only when @mentioned, and a thread follow-up wakes only the bot you mentioned, so they never loop.
- Only you can run commands such as `!approve` or `!restart`. A bot that mentions another bot with a command gets a refusal.
- Say "Build a tiny hello-world script here" to work in-thread. Explicitly request CTO/Engineer Kanban orchestration to exercise the optional card workflow instead. Required owner approval and repository gates apply in either workflow.

This is an intent-based routing change, not a boardless installer: installation still provisions the `creator` board, dispatcher settings and Ops board-based checks described below. Existing data and schedules are preserved. The morning list covers card-backed drafts, not all in-thread or Herdr work.

## Setup

```bash
git clone <this repo> ~/hermes-business-templates
cd ~/hermes-business-templates
./hbt setup creator
```

Setup walks you through one action at a time and checks each one before the next. You can stop anywhere; run it again and it picks up where you left off.

1. Shows a role checklist, all selected by default. Press Enter for all, type `ops` for Ops only, or enter comma-separated role keys such as `creative-director,cto`. Ops is required and is always included. Setup rejects unknown keys and separator-only input before installation. It then asks for your timezone, a projects folder if Engineer is selected, and your Slack member ID (optional for Ops only), and installs only the selected profiles and their assets.
2. For each bot: prints its Slack app file. You create the app, then paste its two tokens into a hidden prompt. Setup checks them with Slack and refuses a token another bot already uses.
3. Finds each bot's channels by name and tells you which ones still need `/invite`.
4. Points Ops at `#agents-report` through your main agent's bot. When that bot is absent, setup skips the main-agent routing check, leaves existing job delivery settings unchanged, and reports Ops delivery as unverified. Configuration is not proof of job delivery.
5. Asks you to run `hermes gateway restart` once.
6. Asks you to post "what's your job here?" in each bot's channel and waits for the right bot to answer.
7. When both CTO and Engineer are installed, setup offers an optional hello-world Kanban demonstration, default No. Only `y` or `yes` opts in. Declining is remembered without a completed-card record; setup reports build handoff and review as unverified. EOF or interruption stops setup. If selected, Engineer hands the checked draft to manual owner review without reviewer reassignment. Setup waits for a unique Done Engineer card in the recorded `<projects>/hello-world` folder, not an unrelated build. A selected but unfinished demonstration remains pending on resume. Existing completed demonstrations are retained. Without both roles, setup reports that the demonstration was not run. Ops-only installs have no conversational bot reply tests.

Then ask your main agent to run the canon interview in `canon/INTERVIEW.md`. `./hbt status creator` shows what is installed and the next setup step.

Rerunning setup keeps recorded roles, demonstration choice and prior checks; it does not reopen selection, add missing peers or remove roles. After declining the demonstration, you can separately request a bounded orchestration exercise; setup will not retroactively claim it passed. An incomplete installation or a deleted recorded profile requires recovery, not a smaller replacement selection. Only installed peers appear in invitations, allowlists and the generated roster. Report missing-role dependencies for selected handoffs or required independent review; role specialties do not forbid authorized in-thread work.

### Missing prerequisites

The launcher checks for Hermes and a Python that imports both PyYAML and ruamel.yaml without starting the native launcher. Explicit `--hermes`, `HBT_HERMES` and `HBT_PYTHON` overrides must be usable; invalid overrides produce a diagnostic rather than selecting another installation. Global options precede the subcommand.

On interactive `./hbt setup creator`, missing prerequisites offer a default-No prompt to display the [official Linux/WSL installation instructions](https://hermes-agent.nousresearch.com/docs/getting-started/installation/) only. Explicit `y` or `yes` prints the owner-run command; hbt never downloads, installs, runs a package manager or continues setup. The official installer can install dependencies and change your environment. Provider login belongs in native secure setup, never chat. With an existing Hermes installation, this is a repair/reference handoff, not a claim that Hermes is absent.

Decline, empty/invalid input, EOF and redirected stdin exit nonzero. Piped `yes` and `install --yes` are not bootstrap consent. Even accepting instructions exits with prerequisites unresolved. After separately reviewing and completing native setup or repair, reload the shell if needed and run `./hbt setup creator` again. It rediscovers prerequisites, then uses the normal capability checks and incomplete-install recovery gate. There is no stored consent or installation-success flag. This template still targets Linux/WSL; native macOS and clean-VM acceptance remain unverified.

### Approving a checked draft

Customer installs keep `review_dispatch: false`: you review the draft manually, and the card stays assigned to its implementer. CTO must not complete a draft just because implementation tests passed. In the original draft approval thread, use the actual card ID in one of these replies:

```text
!kanban --board creator complete <card-id> --summary "Owner approved this draft only"
!kanban --board creator reopen-review <card-id> --reason "<required changes>"
!kanban --board creator archive <card-id>
```

The commands mean approve this draft, request changes, or reject/stop the card, respectively. Archive keeps the record and removes active work; it is not Done. Reopen-review returns the card to its implementer. Do not use `request-changes` for idle manual review; it requires an active reviewer run. `!approve` is for dangerous-tool approval, not a draft/card verdict. Conversational `approve`, `change: <what>`, or `reject` remains owner intent until a recorded board outcome is reported; this template adds no free-text automation.

If Slack commands are unavailable, run the equivalent `hermes kanban --board creator complete <card-id> --summary "Owner approved this draft only"`, `hermes kanban --board creator reopen-review <card-id> --reason "<required changes>"`, or `hermes kanban --board creator archive <card-id>` in a terminal. This is a fallback, not another approval requirement. One native command records one decision.

For an opted-in demonstration, review, requested changes, archive/rejection, blocked work, text-only approval and a setup timeout leave first-build onboarding incomplete. Setup prints pending guidance; no automatic approval is recorded. Draft completion alone does not authorize publishing, deployment, external sends, scheduling or signing.

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

- `template/<role>/<skill>/` holds 24 Creative Director and four Ops playbooks, including the approval and workstream-ownership corrections described below.
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

Each editor gets their own Slack app, channel and folder (`desks/editor-sam`). The configured policy is guest/channel-restricted access, file tools only, an own-folder rootless container and no network. Actual container and native-tool enforcement remains unverified until final selected-path acceptance; configuration alone is not isolation proof.

The owner must separately supply working rootless Docker for the same operating-system user that runs Hermes. Follow the [official rootless Docker instructions](https://docs.docker.com/engine/security/rootless/) for prerequisites, subordinate user/group IDs and user-daemon/context setup. hbt checks that the selected daemon answers as rootless. It does not install Docker, disable a rootful daemon or configure host services.

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

The following is historical evidence from completed bounded independent reviews, not checks rerun for the G5 documentation/output cleanup. Each template revision is the reviewed source head, not its merge commit. The native revisions and runtime identify only the paths exercised; they are not a minimum-version guarantee.

| Reviewed scope and template revision | Recorded checks and limits |
|---|---|
| Shared skills, v0.4.0 candidate: `8da75ed05040520655ca995c31fe71b1dcfa625f` | Final review passed 63 unit tests and five focused native gates. Earlier 63 broader native CLI/discovery/seeding checks used Hermes `343500b3547e12530457c2fda60ec687e25118b4` (`0.21.5+6662.g343500b`), Python 3.11.15; those broader checks were not all rerun at the final head. |
| Memory review, v0.5.0 candidate: `759b18efe6d484e8d7720d08c5b5d7bab17af432` | 131 isolated tests and five native scenario runners. Hermes `7565f6477c211c315110fc12173e500f013366fc`, preinstalled Python 3.11.15. Synthetic drafts and deterministic reviewer fixtures, not model-quality proof. |
| B1 incomplete-install recovery refusal: `703c1598f94ffb1da0982c5b1707b80611b143d7` | 133 tests, no skips, and six safe checkpoints including that suite. Preinstalled Python 3.11.15 with the local unreleased B2 native candidate identified below. Not clean managed bootstrap. |
| G1 profile-local memory drift correction: `2e03fe30ef64e33143f316fd508a3af7fdf24551` | 19 focused tests: equality/copy advice removed and memory bytes preserved. No native/B2 mount. |
| G3 manual approval and truthful thread links: `7678a5e47c51c52dbbdad809b34b3e8b66e0e400` | 38 focused tests plus seven native tests. Python 3.11.15, Hermes `7565f6477c211c315110fc12173e500f013366fc`. Manual owner flow and provenance formatting, not live Slack proof. |
| G4 role selection and prerequisite handoff: `f198181e0061fff91a730a7cb3e67c30f4db4f6a` | Final review passed 132 local tests; 52 native opt-in tests were skipped, not passed. Python 3.11.15 with three read-only utilities from Hermes `7565f6477c211c315110fc12173e500f013366fc`, not full native compatibility. Skipped Ops routing preserves existing job delivery settings and leaves delivery unverified. |

Shared-skills evidence includes real v0.3.2 sandbox migration, pristine and customized repeat updates, preserved support bytes/custom roots/disabled settings/deleted packages, native reseeding exclusion, injected activation recovery, and exact-byte archival before native whole-profile deletion. Broad-root ambiguity correctly refused updates rather than deleting a custom package. Existing desk settings were checked without starting Docker.

Memory-review evidence exercises native memory storage, pending proposals, cron creation and script execution, profile installation/update and whole-profile uninstall in disposable homes. It covers pinned add/replacement, discard archives, invalid-response refusal, batch limits/security scanning, stale pins, replay/unknown-outcome handling, cleanup-only retry, bounded attempts, process exclusion and the reviewer-child wall timeout. Deterministic fixtures replace auxiliary transport before provider resolution. Owner pauses/deletions, exact-nonce recovery, same-name refusal, local-only delivery configuration, zero-write dry-run and preservation/refusal checks were exercised; these are not real scheduling or external delivery tests.

Historical isolation set `HOME` and `HERMES_HOME` before startup, removed inherited overrides and disabled lazy installs. Shared-skills final checks used kernel write confinement; later native scenarios used network/mount namespaces to hide live credentials/profiles and read-only native code plus scoped filesystem guards. A fresh HOME with preinstalled dependencies is not clean bootstrap. The managed launcher lacked dependencies in an isolated home with lazy installs disabled, so native acceptance used the existing dependency-complete Python environment. No hostile-process containment or client-runtime compatibility is implied.

G5 fresh verification is narrower: offline update-advice tests execute the actual checker with a stubbed remote version, parse the selected template argument without applying an update, and verify silence, deduplication and preservation of synthetic settings/memory/job sentinels. Documentation assertions and existing TemplateShape checks cover ownership, approvals, optional-service limits, privacy and role/skill shape. These checks use preinstalled Python 3.11.15 with task-local homes and network/filesystem restrictions; they do not run a native lifecycle or B2 candidate. Exact-head commands, counts and logs belong to the G5 review evidence, separate from the historical table.

### G2: installed native notification ownership remains open

B1 notification checks depended on **LOCAL unreleased** native candidate `8776cac768ca810c1a6ce60acf2a95ffe617d5cf`, based on `7565f6477c211c315110fc12173e500f013366fc`. Approved source tests do not establish released or installed availability. Before final acceptance, select an independently approved installed native revision and repeat notification-ownership checks there. NULL/empty notifier owners retain legacy exact-session-key behavior, not owner isolation. Notification collection is not external delivery. Do not infer this fix from a minimum Hermes version or install the local patch on the strength of this documentation.

**Still unproven:** clean managed bootstrap, secure provider/Slack authentication, model judgment quality, real routing/manual approval/delivery and wall-clock scheduling, selected OpenViking services/models/indexes and outage recovery, actual Docker/native-tool desk isolation, preservation/recovery on the selected runtime, and actual Hermes self-update. Older v0.3 live/simulated evidence does not prove current-candidate live acceptance. Final Mac VM/live end-to-end acceptance and independent acceptance are deferred until feature-complete, not waived. A Linux guest on a Mac does not prove native macOS support. No tag, template release, live installation or client rollout is authorized by these results; the candidate is not release-ready. v0.1 installs still require uninstall before moving to the newer profile names.

## Requirements

- A Linux server (or WSL2) with Hermes installed and its Python dependencies ready. The shared-skills capability checks above must pass; Hermes 0.21 alone is not a compatibility guarantee. Your main agent must be connected to Slack for live onboarding.
- Your main Hermes profile logged in to a model provider (`hermes model`). The bots use the same login and model settings.
- Optional: an existing [OpenViking](https://github.com/volcengine/OpenViking) service for long-term memory. hbt connects it and assigns logical accounts; it does not provision the service or choose/install memory models, embeddings or indexes. If selected, follow current native `hermes memory setup`, the [Hermes memory-provider documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers) and the [official OpenViking documentation](https://github.com/volcengine/OpenViking/blob/main/docs/en/getting-started/02-quickstart.md) on the chosen runtime. Check English search suitability, costs and credentials separately. No particular model is required by this template.
- Installation without OpenViking uses built-in memory for non-Ops bots. This is not automatic outage fallback for profiles already configured for OpenViking: this installer disables their built-in memory and user-profile flags. Verify the chosen runtime's outage/recovery behavior separately.
- Optional: owner-provisioned rootless Docker for desks only, as described above. Linux/WSL remains the template target; a Linux VM on a Mac does not establish native macOS support.

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

With OpenViking configured, each non-Ops bot gets a logical memory account for routing separation. Account names are not an authorization or hostile-process boundary. Trusted same-user bots also share filesystem access. Facts every bot needs belong in `canon/`, not in shared memory. Ops keeps no memory. Bots that run Kanban cards save memories without an approval prompt, because a card runs in the background where nobody can click one.

The owner supplies the optional service and its model/embedding/index configuration through the native setup and official documentation linked in Requirements. Installation without OpenViking uses built-in memory; an outage of configured OpenViking does not re-enable the built-in memory flags that hbt disabled. The watchdog is not a fallback guarantee.

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

- The default local unauthenticated OpenViking setup permits programs that can reach it to address other accounts by name. Logical account routing does not prevent this. Check authentication and exposure on the selected deployment; not every deployment is unauthenticated.
- Slack is the only chat platform in the historical template tests. Current-candidate live routing, approval and delivery still need final acceptance.
- Messages you post in `#agents-report` go to Ops, because that route is how Ops posts through your main agent's bot. Keep the channel for system output.
- Turning on Kanban for the CTO's Slack tools saves Hermes's full default tool list for that bot, so it will not pick up tools Hermes adds to its defaults later. Re-run `hermes -p cto tools enable kanban --platform slack` after a Hermes update if you want them.
- A full install takes a few minutes. Native Hermes handles profiles, board/jobs and regular settings; the installer publishes verified shared packages and atomically updates exact native external-root lists.

## Tests

```bash
~/.hermes/hermes-agent/venv/bin/python -m unittest discover -s tests -v
```

## Retired Herdr development team

T3 Code replaced Herdr as the required development team interface in
customer-onboarding 0.22.0. The Herdr project-onboarding skill and Herdr Web UI
guide were removed from the current guide. Read them at the last revision that
included them:
[project-onboarding](https://github.com/DanielJD1216/hermes-business-templates/tree/a7e24eb025794e41b6013bfbf0091eccd99e178b/skills/project-onboarding)
and the
[Herdr Web UI guide](https://github.com/DanielJD1216/hermes-business-templates/blob/a7e24eb025794e41b6013bfbf0091eccd99e178b/skills/customer-onboarding/references/herdr-web-ui.md).
Updating customer-onboarding does not remove an installed copy of either. Keep an
existing Herdr setup running until its active work moves to T3; retire it only
after an owner-approved impact review.

## License

MIT. See `LICENSE`.
