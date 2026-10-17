---
name: project-onboarding
description: "Create or reuse an approved project and Herdr team."
version: 0.6.0
author: Hermes Business Templates contributors, Hermes Agent
license: MIT
platforms: [linux, macos]
---

# Adaptive project onboarding

Use for required per-project Herdr development setup during authorized onboarding,
and when the owner later requests a new project. Ordinary non-development chat
stays in its originating conversation. Use the required team without Kanban or
formal delivery pipelines. Setup is not permission to build, publish, deploy,
spend or send. No legacy Creator installation is required.

## Prerequisites and discovery

- Read the existing project/file map, approved roots, role decisions and current
  native Hermes/Herdr help. Retrieve known facts before asking. Do not scan the
  whole home or import private context merely to initialize a project.
- Identify the actual primary assistant's profile ID and display name. Reuse that
  assistant as Executive Assistant (EA). A role is a responsibility, not a mandate
  to rename the assistant or create a second main profile.
- Check the permitted Herdr control context before preparing layout or launch work.
  A host-capable Desktop conversation may still lack the inherited pane context
  required below. Reuse an authorized in-Herdr operator if available; preserve the
  original coordinator and verify the result route. If no supported route exists,
  name the boundary and one necessary owner action, not a chain of improvised
  scripts. Do not claim native transport is impossible merely because a policy or
  helper rejects this caller. Never spoof context or select the focused session.
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
choices, then map the required EA, CTO and two Engineer slots and ask only missing
decisions. Preserve the existing EA and reuse permanent CTO/Engineer profiles or
prepare approved missing ones. Names and native profile IDs belong to the owner.
Do not assume the person typing owns every account or has authority to create roles.

Show this mapping before mutation:

| Position | Responsibility | Profile/session selection |
|---|---|---|
| Top left | Executive Assistant | Existing primary assistant, retaining its own name |
| Top right | CTO | Selected existing or approved new architecture/review profile |
| Bottom left | Engineer #1 | First distinct session of the selected Engineer profile |
| Bottom right | Engineer #2 | Second distinct session of that same Engineer profile; idle until safely assigned |

Main-only operation or another layout does not satisfy this baseline. A declined
team requirement remains incomplete; it is not permission to force creation.
Reuse approved profiles across projects; do not recreate them for every project.
EA and CTO must be distinct profiles, and neither may stand in for the Engineer
role. The default is three profiles, not four: one EA, one CTO and one Engineer.
Engineer #1 and Engineer #2 label separate sessions, not separate profiles. New
role profiles reuse the EA's model-provider account through the supported native
credential-sharing route in the role preparation procedure. Preserve existing
owner-selected exceptions; do not create new provider accounts by default.

**Before launching concurrent sessions**, inspect the installed runtime's memory
and shared-profile behavior. Current upstream profile guidance warns that multiple
processes can write the same profile memory. Separate session IDs/worktrees do not
isolate that memory. Reusing one Engineer profile in both slots is not automatic
permission to run both simultaneously. Verify a supported shared-profile memory/write
safety arrangement on the actual host. Otherwise keep the unsafe slot stopped and
report the specific concurrency blocker. Do not automatically create a second Engineer
profile; a different mapping requires a separate owner decision.
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
  "engineer1": {"profile": "engineer", "label": "Engineer #1"},
  "engineer2": {"profile": "engineer", "label": "Engineer #2"}
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

### Inspect and reconcile an interrupted layout

From the same authorized Herdr context, run the existing helper with `--inspect`
and the same `--workspace`, `--hermes-root`, `--roles` and `--name` arguments.
Do not add `--create`. This mode reads the existing receipt and scoped native
metadata without creating a lock or writing files. It does not adopt unrecorded
IDs, inspect terminal text or authenticate agents. A foreground process can be a
shell; `process_exists` is not proof of a Hermes process or ready session.
Missing recognition metadata remains unknown. Read `layout_status` separately
from `readiness`, which remains `not-verified` even for a verified layout.

If the native layout is already complete and the receipt contains all four exact
pane IDs, use `--finalize` instead of `--inspect` only within approved reconciliation
scope. It rereads under the existing lock and checks the endpoint, role mapping,
project path, labels, pane membership and geometry before changing the receipt to
`layout-ready`. Existing recorded geometry must match. This never creates, splits,
renames, starts or deletes anything in Herdr; it does not complete agent readiness.
Back up the private receipt before this write and preserve the original evidence.

If a response was lost before an ID was recorded, a pane is missing, ownership is
uncertain or the server endpoint changed, stop automatic recovery. Report the exact
gap for scoped agent-led native inspection and owner-approved reconciliation where
needed. Do not hand-edit IDs, delete the receipt, recreate the layout or use a
focused-session fallback to make the check pass. The two recovery modes are
mutually exclusive. Inspection success means an observation was obtained, not that
the layout or sessions passed; parse the report instead of using exit zero alone.

Update the existing project catalog with its canonical path, goal, authority,
audience, owner, status and receipt reference. Do not overwrite owner instructions
or create a second task/project database. Review any necessary project-local
instruction merge separately. The originating conversation keeps its return route.

## Start selected sessions and verify readiness

Before any launch, use native `pane get`, `pane process-info`, `pane read` and
`agent list` to verify the exact target. Preserve active turns, approvals, commands
and drafts. Reuse verified sessions rather than starting duplicates. Resolve
shared-profile concurrency and applicable model/tool-connection authority first.

Check the installed client/server compatibility and the applicable
[Hermes session integration](../../capabilities/REFERENCE.md#plugin-0196) for each
selected profile. Record native installation and loading evidence where required
by the selected workflow; do not infer it from another profile. The integration's
session identity reporting is distinct from process recognition and lifecycle
detection. An absent plugin is not by itself proof of a readiness-timeout cause.
Use the supported approved installation route if needed, preserving active sessions;
do not blindly reinstall or restart to diagnose an existing recognition failure.

For an approved idle shell, use the receipt's native `herdr agent start` argv
only after confirming it matches the approved profile and project. Each new session
uses explicit `-p` and `--in`, without `--continue` or a shared resume ID. Read native
agent state and visible output afterward. Verify the actual profile, working root,
conversation ID and readiness; Herdr recognizing the kind `hermes` is not enough.
A login prompt or unknown state is a named blocker, not a successful launch.
Owner-attended sign-in stays in its native secure interface, never in chat.

For any authorized launch sequence, retain the exact target, start/end timestamps,
numeric exit status and bounded sanitized native error details. Inspect after-state
even when the command returns nonzero: a process may have started before a readiness
timeout. Preserve that process and inspect recognition/detection before deciding
whether another action is safe. Prefer direct native operations; do not hide these
observations behind a success-only wrapper or retry the original batch blindly.

One coordinator owns the project. Assign one implementation owner for overlapping
files. Leave the second Engineer idle or read-only until independent work and any
required isolated writable checkout are approved. Four panes are not four jobs.
Apply the [owner-adapted coordination rules](references/role-setup.md#adapt-coordination-to-the-owners-setup)
when assigning work; the layout helper does not schedule workers or enforce capacity.
Do not start provider calls merely to prove labels. For authorized task handoffs,
read the destination, preserve drafts, submit the bounded brief through the native
agent surface, and read back the exact target before claiming delivery. A timeout
is an unknown outcome, not permission to send the prompt twice.

## Owner handoff and verification

Explain whether the owner is checking access, selecting a preset, or entering a
ready agent session. A shell prompt is not a chat prompt; do not ask the owner to
invent commands. The agent performs authorized setup where its tools permit.

Report project/root, approved role map, exact workspace/pane IDs, preserved files,
geometry/reuse result, and per-slot observations: shell-only, process-running,
recognized, ready, or verified, with authorization/login blockers kept explicit.
Each observation needs its own evidence; none implies the next. Baseline acceptance
requires authenticated readiness
in all four slots, not four shell labels. Ready agents may wait idle until safely
assigned. Record launch and useful-task proof separately. Do not
claim native Mac acceptance from Linux tests, or model readiness from layout tests.

The helper uses Unix sockets and `fcntl`; native Windows is unsupported. A Windows
client can use a separately verified Linux/WSL host. Installed command contracts,
profile setup, model authentication and native client behavior require host-specific
checks. For isolated tests, set both HOME and HERMES_HOME to private test roots,
disable lazy installs/dotenv, and use only a named test Herdr session, never the
owner's default server.
