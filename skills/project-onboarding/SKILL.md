---
name: project-onboarding
description: "Create or reuse an approved project and Herdr team."
version: 0.2.0
author: Hermes Business Templates contributors, Hermes Agent
license: MIT
platforms: [linux, macos]
---

# Adaptive project onboarding

Use when the owner explicitly asks to create/onboard a project and chooses a Herdr
workspace. Ordinary chat, research, fixes and implementation stay in the originating
conversation unless this workflow is selected. Setup is not permission to build,
publish, deploy, spend or send. No legacy Creator installation is required.

## Prerequisites and discovery

- Read the existing project/file map, approved roots, role decisions and current
  native Hermes/Herdr help. Retrieve known facts before asking. Do not scan the
  whole home or import private context merely to initialize a project.
- Identify the actual primary assistant's profile ID and display name. Reuse that
  assistant as Executive Assistant (EA). A role is a responsibility, not a mandate
  to rename the assistant or create a second main profile.
- Ask the project name first only if missing; then resolve the existing location
  and goal. Reuse existing repositories, branches, instructions and owner edits.
  For a new project, agree an exact folder within an approved root. No implicit
  Git initialization, clone, relocation, worktree or replacement AGENTS.md.
- Install this entire reviewed skill directory, including `scripts/onboard.py` and
  `references/role-setup.md`, in the selected coordinator's skill root through the
  supported native skill/write-approval route. A repository link or lone SKILL.md
  is not installation. Preserve any existing skill and review differences before
  updating. Verify native discovery and helper availability before claiming ready.

## Adapt the team once, not once per project

Use the [role preparation procedure](references/role-setup.md). Retrieve existing
choices, then recommend the minimum useful mapping and ask only missing decisions.
For a selected development team, offer EA, CTO and Engineer responsibilities. Names,
profile IDs and the number of independent worker profiles belong to the owner.
Do not assume the person typing owns every account or has authority to create roles.

Show this mapping before mutation:

| Position | Responsibility | Profile/session selection |
|---|---|---|
| Top left | Executive Assistant | Existing primary assistant, retaining its own name |
| Top right | CTO | Selected existing or approved new architecture/review profile |
| Bottom left | Engineer #1 | Selected implementation profile/session |
| Bottom right | Engineer #2 | Selected second session/profile; idle until safely assigned |

The owner may keep main-only operation or choose another layout. This helper is
for the selected four-pane layout only; do not force it on a different choice.
Reuse approved profiles across projects; do not recreate them for every project.

**Before launching concurrent sessions**, inspect the installed runtime's memory
and shared-profile behavior. Current upstream profile guidance warns that multiple
processes can write the same profile memory. Separate session IDs/worktrees do not
isolate that memory. Reusing one Engineer profile in both slots is not automatic
permission to run both simultaneously. Use separately approved worker profiles,
a verified supported write-isolation arrangement, or leave the second slot idle.
Apply the same check to the primary assistant and other already-running sessions.
Do not silently disable owner memory, clone profiles or copy credentials to solve it.

## Prepare the project and layout

The agent writes a private approved role-map JSON; the owner does not edit JSON.
The four slot keys are fixed; profile IDs and display labels are not. Example only,
not an instruction to create these names:

```json
{
  "executive-assistant": {"profile": "default", "label": "Primary assistant"},
  "cto": {"profile": "architect", "label": "Technical lead"},
  "engineer1": {"profile": "builder-a", "label": "Engineer #1"},
  "engineer2": {"profile": "builder-b", "label": "Engineer #2"}
}
```

Discover the actual default Hermes home containing named profiles; it may differ
from the current named profile's HERMES_HOME. The helper checks only profile-name,
tombstone and config-file metadata, not authentication or private config contents.
Missing/deleted profiles must be resolved through the approved role procedure first.

Use `terminal` to inspect `herdr --help`, `herdr --skill` and relevant native help.
The helper requires a genuine inherited `HERDR_ENV=1` and `HERDR_SOCKET_PATH` from
an authorized Herdr pane. It never falls back to the user's focused session.
If that transport is unavailable, report the specific limitation and one supported
owner action or authorized handoff. Do not spoof the environment, change session
ownership or move the originating business conversation merely to bypass a guard.

Read workspace/pane/agent metadata before acting. Reuse recorded layouts. An
unrecorded matching name/location needs reconciliation, not a duplicate workspace.
Run the helper with `terminal`, substituting discovered quoted absolute paths:

```bash
python3 /path/to/project-onboarding/scripts/onboard.py --workspace /approved/business-workspace --hermes-root /actual/default-hermes-home --roles /private/approved-roles.json --name 'Project name' --path /approved/project --goal 'Known goal'
```

Add `--create` only for the explicitly approved missing project folder; its parent
must exist. No repo, instructions, accounts or agents are created by this helper.
For repeat onboarding, omit path/goal only when the existing record remains valid.
Retain `--workspace`, `--hermes-root`, `--roles` and `--name`.

The helper creates labelled shells without changing focus, verifies geometry,
and saves `.hbt-projects.json` in the approved business workspace. It returns
`layout-ready` and proposed native launch argv, **not running agents**. Version-1
legacy receipts are refused rather than automatically migrated. Changed role maps,
paths, sockets, layouts or partial operations need inspection; do not delete a
receipt, retry an ambiguous mutation, or close possibly active panes as rollback.
The receipt is cooperative local bookkeeping, not an authorization or OS sandbox.

Update the existing project catalog with its canonical path, goal, authority,
audience, owner, status and receipt reference. Do not overwrite owner instructions
or create a second task/project database. Review any necessary project-local
instruction merge separately. The originating conversation keeps its return route.

## Start selected sessions and verify readiness

Before any launch, use native `pane get`, `pane process-info`, `pane read` and
`agent list` to verify the exact target. Preserve active turns, approvals, commands
and drafts. Reuse verified sessions rather than starting duplicates. Resolve
shared-profile concurrency and applicable model/tool-connection authority first.

For an approved idle shell, use the receipt's native `herdr agent start` argv
only after confirming it matches the approved profile and project. Each new session
uses explicit `-p` and `--in`, without `--continue` or a shared resume ID. Read native
agent state and visible output afterward. Verify the actual profile, working root,
conversation ID and readiness; Herdr recognizing the kind `hermes` is not enough.
A login prompt or unknown state is a named blocker, not a successful launch.
Owner-attended sign-in stays in its native secure interface, never in chat.

One coordinator owns the project. Assign one implementation owner for overlapping
files. Leave the second Engineer idle or read-only until independent work and any
required isolated writable checkout are approved. Four panes are not four jobs.
Do not start provider calls merely to prove labels. For authorized task handoffs,
read the destination, preserve drafts, submit the bounded brief through the native
agent surface, and read back the exact target before claiming delivery. A timeout
is an unknown outcome, not permission to send the prompt twice.

## Owner handoff and verification

Explain whether the owner is checking access, selecting a preset, or entering a
ready agent session. A shell prompt is not a chat prompt; do not ask the owner to
invent commands. The agent performs authorized setup where its tools permit.

Report project/root, approved role map, exact workspace/pane IDs, preserved files,
geometry/reuse result, and per-slot state: shell-only, awaiting authorization/login,
or verified agent session. Record launch and useful-task proof separately. Do not
claim native Mac acceptance from Linux tests, or model readiness from layout tests.

The helper uses Unix sockets and `fcntl`; native Windows is unsupported. A Windows
client can use a separately verified Linux/WSL host. Installed command contracts,
profile setup, model authentication and native client behavior require host-specific
checks. For isolated tests, set both HOME and HERMES_HOME to private test roots,
disable lazy installs/dotenv, and use only a named test Herdr session, never the
owner's default server.
