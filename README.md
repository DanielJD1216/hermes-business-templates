# Hermes Business Templates

Free, MIT-licensed starting setups for running a small business on [Hermes Agent](https://hermes-agent.nousresearch.com/docs). Each template installs a small team of AI bots, each a separate Hermes profile with its own Slack app, on a server the business owns, using the owner's own AI subscription or API keys.

We provide the foundation only: bots, playbooks, folders, scheduled checks and an installer. Your business details, tools and accounts stay yours.

| Template | Status |
|---|---|
| Creator + Education | v0.4.0 unreleased candidate: shared skills, protected v0.3.2 migration, guided per-bot setup. Independent review pending. |
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
7. Your first build: the hello-world card from CTO to Engineer.

Then ask your main agent to run the canon interview in `canon/INTERVIEW.md`. `./hbt status creator` shows what is installed and the next setup step.

### Keeping the bots in step

Each bot has separate settings and permissions; selected playbooks now use one shared library. `./hbt check creator` compares installed provenance and prints one line per gap with its fix:

- a bot with a different `USER.md`, missing or modified shared package files, unresolved migration conflicts, duplicate skill names, missing selected roots or missing bundled opt-out/manual;
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
| Memory watchdog | every 5 minutes | Only when memory goes down, every 6 hours while it stays down, and when it recovers. |
| Update check | Mondays 09:00 | Only when a newer template version exists. |
| Drift check | 08:00 daily | Only when `./hbt check` finds new gaps, and weekly while they stay open. |
| Comment pull, member questions | paused | Resume once you drop exports into `ops/incoming/`. |

## What has been tested

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

Uninstall first archives local skills, settings and conflict data outside each profile, then invokes native profile deletion. It also archives whole skill packages discovered through custom `external_dirs` and `create_dir` locations inside profiles being removed, retaining their profile-relative paths. It does not archive arbitrary non-skill files from these custom roots. Archived custom skills survive but are no longer active in the removed profiles. Only recorded managed external entries and pristine owned shared packages are removed; original marker/settings values are restored where still installer-owned, while later unrelated owner changes remain. Modified or unrecognized shared content and all recovery archives stay in place, with paths printed. Unowned or symlinked library roots are refused. Your default-profile skills and custom external directories outside removed profiles are not deleted. The business folder, long-term memories and Slack apps are kept unless you remove them, and the board is archived as before.

Custom path strings and their order remain unchanged. Planning, checks and archival resolve `${HERMES_HOME}` and relative skill paths against the consuming profile, not the installer home. Archival includes endangered packages even when a configured root is an ancestor of a removed profile; it excludes packages in unrelated profiles. Regression checks exercised a partial package deletion, native collision refusal followed by successful custom loading, and exact archived bytes after native whole-profile deletion. A focused five-gate native regression verified ancestor-root preservation and outside-package exclusion. Its two update attempts correctly refused duplicate native manuals exposed by the broad root; uninstall still preserved the custom package.

## Memory

With OpenViking running, each bot gets its **own memory account**, so bots cannot see each other's memories. Facts every bot needs belong in `canon/`, not in shared memory. Ops keeps no memory. Bots that run Kanban cards save memories without an approval prompt, because a card runs in the background where nobody can click one.

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
