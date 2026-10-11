# Hermes Business Templates

MIT-licensed starting setups for [Hermes Agent](https://hermes-agent.nousresearch.com/docs), on a server the customer controls.

**Creator + Education is an unreleased candidate.** The current reduction removes Kanban-based workflows and all Creator playbooks. Implementation and acceptance evidence must be checked together; historical tests are not proof of this revision. No public release or live rollout is implied.

## Start here: talk to your private agent

Open your **private, tool-capable agent on the computer where Hermes will run**.
Paste this repository URL and this message:

> Help me set up Hermes Business Templates from
> https://github.com/DanielJD1216/hermes-business-templates.
> Explicitly read the root README.md, root AGENTS.md and
> skills/customer-onboarding/SKILL.md. First check that you can act on my intended
> host and that this conversation is private. Preserve my existing main assistant
> and login. Retrieve what you already know, then guide me one missing question or
> one instruction at a time. Do not install specialist profiles, import memory or
> connect accounts before we review the context, team and access boundaries.

**A URL alone does not auto-load README or AGENTS.md.** The agent must fetch/read
those files. If it can only chat in a browser and cannot execute on the intended
host, it must say so and guide you to a capable private session, not pretend to
install anything. Hermes is the initial supported agent harness; models/providers
remain interchangeable through native model selection. You do not need a new model
subscription or any specialist agent to begin.

Your agent checks only missing prerequisites, including secure remote access when
needed, preserves your existing main identity, offers an optional reference/org
chart, and helps reconstruct context from the AI platforms you choose. It uses
[Prompt 1 for each export](skills/customer-onboarding/references/prompt-1-extraction.md)
and [Prompt 2 for reviewed consolidation](skills/customer-onboarding/references/prompt-2-consolidation.md).
Personal **and** business context can belong to your owner-private main assistant;
subsequent storage, audiences and role access must stay explicitly separated.
Private does not mean offline: selected providers and tools may process the data.
Never paste credentials into chat.

After you approve the reviewed context and role boundaries, your agent prepares
SOUL/AGENTS/USER/context/tools/team drafts and an exact write plan, obtains approval,
and operates the **existing installer below**. You make decisions and complete
native logins; the agent handles authorized tool work and JSON, rather than handing
you a terminal checklist. Slack access is verified per role, not granted to every
workspace member. Optional Herdr development sessions are a later choice, not the
initial onboarding interface.

Progress, approvals, immutable exports and evidence live in owner-private storage
outside this repository. A small [checkpoint helper](skills/customer-onboarding/references/checkpoints.md)
checks required artifacts, order and hashes across interruptions. It is not a
security boundary, human-consent authenticator or replacement installer. Deleted
specialist profiles do **not** prove an old install record, workspace or deletion
markers are gone. Stale/partial state stops for reviewed recovery, never automatic
record deletion or forced recreation. No customer Mac repair is implied by this
candidate's local tests.

## What the customer gets

- Default Creative Director, CTO and Engineer profiles, or a reviewed custom team selected before setup creates profiles and Slack manifests. Conversational roles have their own Slack apps and folders.
- An Ops profile hosting only the optional script-only memory watchdog. Ops has no conversational Slack bot or personal memory. It is included in the default team and legacy `--roles` shortcut; an explicit team JSON can omit it. Without Ops or OpenViking, no watchdog job is scheduled.
- Generic role SOUL documents, generated workspace rules, a blank private USER worksheet and editable `canon/` files for business, offers, voice, brand and standing rules, plus a guided interview.
- A blank project index, file-placement/access guide and reusable project-onboarding skill with a stdlib Herdr layout helper. These are not the removed content/business-review playbooks.
- Selected native Hermes skills in a shared, provenance-tracked library. These are not the removed 24 Creator playbooks and do not install external tools or grant credentials.
- Install, resumable setup, connection, status, manual check, update and preservation-aware uninstall commands.
- An optional editor desk with its own bot and rootless-container policy. Actual isolation still requires acceptance testing.

The customer's existing main assistant stays in place. An optional Executive Assistant SOUL is supplied for a reviewed merge, never automatically installed as another profile or written over the default identity. No new task board, dispatcher configuration, card-based onboarding demo, business digest or automatic memory reviewer is part of this setup.

See [canonical integration and package paths](docs/canonical-integration.md). Fresh workspace instructions explicitly point to the separate project-onboarding skill; it is a workspace file, not automatically registered in the default profile's skills list. The installed FILES.md supplies optional, explicit adoption through native `skills.external_dirs`, preserving existing roots/settings and the main SOUL, with exact-source discovery checks. No separate installer is added. USER/canon/index files are seeded only when absent. Generated instructions and helper files update only against recorded unchanged hashes; owner edits and untracked legacy files are preserved and reported for manual merge.

### Tools and MCP reference sheet

The publisher supplies a separate paper/PDF reference: tool name, purpose, when it is useful, official download/setup link and account requirements. Customers choose which tools to install and connect. They do not need every tool on the sheet. This repository does not contain a finalized reference sheet or automate those installations.

## How work happens

Finish authorized work in the requesting conversation, including simple implementation and testing. Code and role names do not automatically trigger delegation.

Use Herdr when the owner explicitly selects project-session orchestration. Keep one coordinating conversation, one implementation owner per task and independent review when needed. Verify the destination session before sending a handoff, verify receipt, and return evidence directly to the coordinator. Do not make the owner relay reports. Herdr is an owner-installed tool, not a bundled framework or automatically tested connection.

Explicit project onboarding asks for the project name, then only missing repo/location and goal, reusing known project facts. Its default 2x2 layout is Executive Assistant top-left, CTO top-right, engineer1 bottom-left and engineer2 bottom-right. The main slot uses the existing default profile; the engineers use separate sessions of the same engineer profile. The helper creates/verifies labelled shell panes only, then the skill guides read-before-start native session setup. It sends no prompts and never automatically assigns two writers to one checkout. Ordinary chats do not invoke it. Local semantic search is optional and manually owner-installed/indexed, with no new schedule.

For an authorized Slack handoff, mention the receiving bot in the originating thread. Bots must be in the relevant channels and allowlisted. The current Slack configuration answers human messages in the bot's home channels without a mention, ignores mentions of other bots, and requires mentions for bot-to-bot messages.

Approval stays in the working conversation. Nothing is published, sent, scheduled, priced or signed without approval for that action. Passing tests does not grant external-action authority. Native command approvals and repository gates remain in force.

## Backend operator reference: requirements and setup

The customer entrypoint is the private-agent conversation above. The commands and
JSON examples below are for that agent or an experienced operator **after** the
onboarding approval gates, not first instructions for a new customer.

- Linux or WSL2 with Hermes installed. Native macOS and ARM64 are not established by x86_64 Linux testing.
- Customer-controlled model login, selected with native `hermes model`. The installer copies model settings, not private agent histories or skills.
- Separate Slack apps and customer-entered credentials. Never paste tokens into chat.
- Optional existing OpenViking service for memory; optional rootless Docker for editor desks.

```bash
./hbt setup creator
```

Setup offers the default team or customization before any profiles or Slack manifests are created, asks for timezone/projects/Slack member ID, creates selected profiles, generates Slack manifests, verifies bot identity and membership, and asks the owner to restart the gateway. It then checks conversational replies. It does not run a card-based build demo or claim Herdr handoffs were tested.

Ops reports through the main assistant's configured system-channel route. If the main agent has no Slack login, setup reports delivery as unverified and leaves existing delivery settings alone. Configuration is not destination confirmation. Use `status` to see the next setup action, and complete `canon/INTERVIEW.md` with the assistant.

An interrupted installation or missing recorded profile requires recovery. Setup must not silently reduce the selected team or claim success. Ordinary resume does not reopen role selection or add profiles.

### Customize the team before installation

At the first setup prompt, press Enter for the default team, or type `customize` and supply a reviewed JSON file. The smaller built-in subset shortcut still accepts `cto,engineer` (and includes Ops). For a precise subset, display renames or custom purposes, save a file such as `~/creator-team.json`:

```json
{
  "schema": 1,
  "roles": [
    {"key": "creative-director", "title": "Studio Lead"},
    {"key": "engineer", "title": "Builder"},
    {
      "key": "researcher",
      "title": "Researcher",
      "purpose": "Draft summaries of public sources for the owner to review.",
      "permissions": "draft-only",
      "tools": ["web"]
    }
  ]
}
```

Or preview/install directly:

```bash
./hbt install creator --team "$HOME/creator-team.json" --no-memory --dry-run
./hbt install creator --team "$HOME/creator-team.json" --no-memory
./hbt setup creator
```

- The list is the exact team, including Ops only if explicitly listed. Built-in keys are `creative-director`, `cto`, `engineer`, `ops`. The main assistant remains untouched.
- `key` is the stable profile ID, not a display name. Built-in entries accept only `key` and `title`: their canonical SOUL, responsibilities, channels, folders and tool defaults stay unchanged. A display rename is **not** a new custom responsibility.
- A new key creates a genuine owner-purpose draft role with a generated SOUL, `team/<key>` workspace folder and `#team-<key>` Slack channel. Custom roles require explicit `permissions: "draft-only"` and `tools: []` (no tools) or `["web"]` (public web research). Manual approvals, explicit native platform tool selections, disabled automatic memory writes and `no_mcp` are configured. No terminal, file, browser, delegation, scheduling or MCP capability is selected; no extra stock skills are selected. They produce drafts in conversation, not project files.
- Custom roles are intentionally conservative. Purpose text cannot grant permissions. Broader custom permissions, automatic peer routing and clones of built-in roles are not supported. Hermes can warn that a `no_mcp`-only selection has no valid toolsets; native resolution is intentionally zero tools. Existing host plugins or owner overrides are outside this template's permission guarantee.
- Same-responsibility additional draft instances require deliberately adding separate entries with unique IDs and display names, each with explicit purpose/permissions/tools. Credentials, private skills, histories and memory are never cloned. Selecting a new role does not connect any account.
- The validated team is saved in the installation record. Resume/update/connect/check/uninstall use that record, not a later-edited or missing input file. Changing an installed roster or role purpose is **not** supported by editing the JSON or rerunning install. Stop for a separately reviewed migration; do not delete records or reinstall over profiles.
- The optional four-pane **development preset** remains EA top-left, CTO top-right, engineer1 bottom-left and engineer2 bottom-right. Generic teams need not use it. It neither installs additional roles nor changes the customized roster.

### Projects paths and existing-install correction

Projects input must be an absolute path or `~/folder`; Enter accepts `~/projects`. The folder need not exist. Paths with spaces work. Relative paths, placeholders such as `not setup yet`, shell expressions, parent traversal, symlinks and non-directory components are rejected before installer writes. Working folders and role rules are **not filesystem isolation**: local tools run with the operating-system account's permissions, including access to any credentials that account can read.

If setup already created profiles and is waiting at the first Slack-app step, stop it with Ctrl+C. Use the updated package's narrow correction command, not install/uninstall:

```bash
./hbt configure creator --projects "$HOME/projects" --dry-run
./hbt configure creator --projects "$HOME/projects"
./hbt status creator
./hbt setup creator
```

This changes the recorded default and unchanged generated CTO/Engineer instructions, creates the new folder if needed, and leaves every existing project folder/file in place. A mistakenly created `Downloads/.../not setup yet` directory is **not** moved or deleted. Profiles and `terminal.cwd` stay in their business-workspace folders; the projects path is the default for future projects, not a profile migration.

Optional, **before creating a built-in role's Slack app**, change its display name without changing its stable ID:

```bash
./hbt configure creator --rename 'creative-director=Studio Lead' --dry-run
./hbt configure creator --rename 'creative-director=Studio Lead'
```

The command updates only the team record, tracked generated roster/instructions and local Slack manifest display fields. It does not change canonical SOUL responsibilities, profile IDs, credentials, sessions, skills, schedules, channels or external Slack apps. Installed custom-role names/purposes are frozen in this minimal implementation. A saved Slack token or bot identity blocks a rename; if an app was created externally but no token was saved, stop and reconcile it yourself before using this command. No remote rename is performed.

Correction takes verified private backups under `business-templates/creator/backups/configure-*`, refuses owner-edited/untracked instructions or changed manifest names, checks for concurrent changes, reads back applied bytes and is a no-op on repeat. Run it with affected sessions stopped. Ordinary write failures restore still-owned changed bytes; a hard kill/power loss can leave a partial correction requiring reconciliation with the printed archive. Do not overwrite later owner edits, mark a record complete, or delete recovery records. Existing roster additions/removals require a separate migration, not this command.

### Runtime discovery

The launcher checks recognized managed Hermes installations through existing native package-manager state. It does not invoke bootstrap, install dependencies or repair an environment to discover Python. Explicit `--hermes`, `HBT_HERMES` and `HBT_PYTHON` values keep precedence; broken explicit or recognized managed environments fail with a diagnostic. Legacy layouts require a dependency-complete interpreter.

When prerequisites are missing, interactive setup can display the [official installation instructions](https://hermes-agent.nousresearch.com/docs/getting-started/installation/) after a default-No prompt. It does not execute the installer. Return to setup after installing or repairing Hermes yourself. `install --yes` is not bootstrap consent.

## Memory and the only scheduled job

Without OpenViking, conversational profiles use native built-in memory. With OpenViking, each profile receives a logical account for routing separation. Account names are **not an authorization or hostile-process boundary**. Same-user profiles can access the same filesystem. Ops keeps no memory; shared business facts belong in `canon/`.

The customer supplies OpenViking and its model/embedding/index configuration. The template does not provision the service or install its models. Follow native `hermes memory setup`, the [Hermes memory-provider documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers) and [OpenViking documentation](https://github.com/volcengine/OpenViking). Check English search suitability, costs and credentials. Check service authentication and network exposure; not every deployment is unauthenticated.

Configured OpenViking profiles have built-in memory flags disabled. This is **not automatic outage fallback**. The watchdog reports trouble, not a successful failover or repair.

| Job | Schedule | Behavior |
|---|---|---|
| Memory watchdog | Every five minutes, only when OpenViking is configured | Tests health and search. Silent when healthy; alerts on outage, repeats after six hours while down, and reports recovery. |

The watchdog uses Python with `no_agent: true`. It invokes no chat model. Its search request can use the configured memory service's embedding model. Alert timestamps use the chosen timezone. Verify an actual notification before claiming delivery works.

Morning approvals, Nightly review, Memory-draft review, Comment pull, Member-question pull, Template update check and Drift check have been retired. Normal memory storage remains; there is no automatic proposal reviewer.

## Manual maintenance

```bash
./hbt status creator
./hbt check creator --offline
./hbt update creator --dry-run
./hbt update creator
```

`check` is on demand, not a scheduled routine. It reports selected-skill integrity, configuration/connection gaps and recorded job failures without turning those findings into mandatory daily chores.

Shared stock comes from the installed Hermes source, not the owner's writable skill directories. Each profile loads exact selected directories through `skills.external_dirs`; custom roots, disabled lists and creation settings remain owner-controlled. The essential `hermes-agent` manual remains native-managed. The bundled opt-out marker prevents unselected packages from being automatically reseeded. Sharing skills grants no MCP access, credentials or filesystem isolation.

Capability checks, not a minimum version number alone, determine compatibility. Native external-root support, profile distributions and the selected skill sources must be available.

## Updating older installations

Stop work in the affected template profiles before migration. Start with `update --dry-run`. Migration must preserve owner data, unrelated jobs and settings, and historical boards. It must not call the board dispatcher or globally disable settings another workflow may use.

Retired automation requires exact recorded ownership, not a matching name alone. A running job, ambiguous identity or changed owned script must stop unsafe migration. Durable archives preserve prior records, settings and retired assets before changes. Owner-modified/custom skills remain intact and must be reported rather than silently deleted. Historical boards are not removed during update or uninstall.

This is not an atomic transaction across native commands. A failed run can leave an archive or already-paused job. Read the reported state and retry only after resolving its exact blocker. Do not manually mark a record complete or erase a recovery journal to bypass a refusal.

Shared-skill activation retains its existing archive and recovery mechanism. On interrupted activation, retry restores only bytes/settings that still match the preserved state before replanning. New owner edits stop recovery rather than being overwritten. An update with retained conflicts exits 2; a clean update exits 0. Never interpret a conflict exit as a clean migration.

## Uninstall and recovery

```bash
./hbt uninstall creator --dry-run
./hbt uninstall creator
# Optional, destructive and separately deliberate:
./hbt uninstall creator --delete-workspace
```

Uninstall preflights every recorded profile before deletion. Unrelated jobs, unsafe paths, ambiguous ownership, unreadable stores or uncovered files refuse removal. Paused owner jobs still count. `--yes` does not bypass preservation checks. Backing up a job file does not preserve a running workload.

Covered data includes profile-local skills/configuration, discovered skill packages under endangered roots, memories and pending memory proposals, exact native `auth.lock`, supported native config backups and named/rotated logs. Credentials, unknown scripts, sessions and other uncovered files are not silently deleted. The exact reason is reported so the owner can preserve or relocate them deliberately.

Private preservation archives use checked hashes and bounded paths. Teardown rechecks inventory, removes only owned jobs, preserves logs changed by native commands and confirms profile deletion. Concurrent changes or preservation failures can stop later steps after earlier steps completed. This is a fail-closed precheck, not automatic rollback.

The workspace stays unless explicitly deleted. External memories, Slack apps, outside custom roots and existing task boards remain. Review/history archives from retired features stay available; they are not reactivated. Native legacy policy validation and locking remain only where needed for safe preservation.

For rollback, preserve all later owner edits first. Use the matching archived install record, profile settings and staged distribution together in a disposable home. Verify byte equality and native loading there. Merge later changes; do not blindly replace a live configuration or clear all recovery records.

## Optional editor desk

```bash
./hbt desk creator desk-editor --name sam --guest U0123ABCD --channel ext-editor-sam=C0123ABCD
```

Each desk has its own Slack app, channel and folder. The policy is guest-restricted, file-tools-only, own-folder mounts and no network. Actual container and native-tool enforcement remains unverified until selected-path acceptance.

The customer supplies rootless Docker for the same operating-system user. Follow the [official instructions](https://docs.docker.com/engine/security/rootless/) for subordinate user/group IDs and user-daemon/context setup. The installer checks the daemon; it does not install Docker or disable host services. No shared skill roots are mounted into the desk.

## Verification limits

Run the current suite with the native dependency-complete Python and native source on `PYTHONPATH`:

```bash
python -m unittest discover -s tests -v
```

Unit/synthetic tests are not provider-login, Slack-delivery, wall-clock scheduling, Herdr-session or Docker-isolation acceptance. Removed-feature tests no longer count toward current coverage. Keep exact revision, commands, counts and native runtime identities with each acceptance record. Separate isolated Herdr 0.9.3 Linux/WSL checks verified the native four-pane geometry and repeat reuse with no agents running. Isolated native Hermes profile/context-loading checks preserved the main SOUL. These do not establish live model sessions, prompt delivery or macOS behavior.

Earlier template revisions and the previous notification-ownership patch have bounded historical evidence, not blanket compatibility guarantees. The boardless template no longer depends on a task-notification collector to finish setup. Real authentication, notification delivery, selected memory service operation, desktop/Herdr transport and desk isolation still need their own proof. The candidate is not release-ready solely because local tests pass.

## License

MIT. See `LICENSE`.
