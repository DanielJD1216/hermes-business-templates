---
name: project-onboarding
description: "Create or reuse an approved project and Herdr team."
version: 0.10.0
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
- Check the permitted host and Herdr control route before layout or launch work.
  Slack, Hermes Desktop and terminal conversations may coordinate setup without
  running inside a Herdr pane. Require actual tools on the approved host, not a
  particular chat interface. Use inherited context or the explicit-session route
  below; preserve the original coordinator and verify the result-return route.
  If neither route is available, name the missing access and one necessary owner
  action. Never fabricate pane context or select the user's focused session.
- Ask the project name first only if missing; then resolve the existing location
  and goal. Reuse existing repositories, branches, instructions and owner edits.
  For a new project, agree an exact folder within an approved root. No implicit
  Git initialization, clone, relocation, worktree or replacement AGENTS.md.
  If the owner has not chosen a goal or audience, record them as undecided. This
  does not block authorized setup or authorize research or development assignments.
- Install this entire reviewed skill directory, including `scripts/onboard.py` and
  `references/role-setup.md`, in the selected coordinator's skill root through the
  supported native skill/write-approval route. A repository link or lone SKILL.md
  is not installation. Preserve any existing skill and review differences before
  updating. Verify native discovery and helper availability before claiming ready.
  Load the installed skill, verify its complete file set against the selected
  source revision, and run the installed helper's `--help`. Reading the repository
  alone is not this check. If a native scanner blocks installation, review its
  exact findings and obtain any required package-specific override; never bypass
  the scanner by copying files or granting blanket trust.

Resolve the execution route before creating a layout. Record the originating
coordinator, authorized execution host, selected Herdr session/endpoint, project
scope and exact result-return route in the existing private project record.
Retrieve approved target choices before asking; ordinary setup authority covers
routine target-bound operations, not unrelated servers or projects. Prefer direct
execution from this conversation when its tools reach that host. An authorized
in-Herdr operator is an alternative, not a prerequisite or a new coordinator.
Preserve busy agents and drafts. Do not move or restart a working conversation,
create a bridge/service, or promise continuation without a verified route. If
access is genuinely unavailable, give one necessary owner action, explain whether
it targets a shell or assistant, and keep acceptance pending. The operator does
routine authorized work; the owner is not a command-by-command relay.

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
The helper supports two authorized host-local routes:

- **Inherited:** genuine `HERDR_ENV=1` and `HERDR_SOCKET_PATH` from an authorized
  Herdr pane. Existing invocations remain supported.
- **Explicit session:** add `--session <approved-session>` from a tool-capable
  conversation on the intended host. Use `--session default` only when that server
  is the approved target, never as a guessed fallback. The helper uses native
  `herdr --session <name> status --json`, requires a matching running compatible
  server and a same-user, owner-only Unix socket, then checks the receipt's endpoint
  identity and project metadata. Every native call carries the selected session;
  inherited Herdr caller variables are removed from those child processes, not
  invented or changed in the originating conversation. Endpoint replacement stops
  the operation. No automatic server start, restart, migration or fallback occurs.

Herdr's bundled agent guidance may describe only in-pane operation. That is not
proof that its documented external-client CLI is unavailable. Use this explicit
route within owner-approved host/project scope; do not pretend to satisfy the
inherited-context check. The socket checks and receipt are not an OS sandbox or
protection against a hostile same-user process. Preserve native OS permissions.
This helper does not forward to arbitrary remote hosts. If chat tools run elsewhere,
use an existing approved execution route to run the helper on the intended host;
otherwise report missing access. No token copying or new network listener is needed.

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
For explicit-session execution, retain `--session` on every helper invocation.
The output's `control` field identifies the route. Returned launch argv includes
the explicit native session prefix; stored legacy launch argv stays unchanged.
For later native reads, launches, prompts and waits, retain that same prefix and
an exact verified pane ID or unique agent name. Never execute old unqualified
receipt commands from an external caller or use `--current` there.

The helper creates labelled shells without changing focus, verifies geometry,
and saves `.hbt-projects.json` in the approved business workspace. It returns
`layout-ready` and proposed native launch argv, **not running agents**. Version-1
legacy receipts are refused rather than automatically migrated. Changed role maps,
paths, sockets, layouts or partial operations need inspection or the explicit
same-path endpoint recovery below; do not delete a
receipt, retry an ambiguous mutation, or close possibly active panes as rollback.
The receipt is cooperative local bookkeeping, not an authorization or OS sandbox.

`layout-ready` is an intermediate result. Continue the authorized session launches
and readiness checks below without another routine approval. If a real blocker
stops startup, report each slot's actual state and name the blocker and next actor;
do not present empty panes as a completed team.

### Inspect and reconcile an interrupted layout

Using the same verified route and target, run the existing helper with `--inspect`
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
uncertain or the server endpoint changed, stop automatic recovery. A same-path
socket replacement has the explicit recovery below; other gaps need scoped native
inspection and owner-approved reconciliation. Do not hand-edit IDs, delete the
receipt, recreate the layout or use a focused-session fallback to make a check
pass. Recovery modes are mutually exclusive. Inspection success means an observation was obtained, not that
the layout or sessions passed; parse the report instead of using exit zero alone.

### Rebind a receipt after an approved server restart

A restarted Herdr server can recreate its Unix socket at the same path with a
different inode/device. Ordinary onboarding, `--inspect` and `--finalize` still
reject this mismatch. Do not loop those commands or remove the identity guard.
Use `--rebind` only after the owner authorizes recovery of this exact host, server
path and recorded project. Existing setup authority alone does not authorize
rebinding an unexpected server. Retrieve the approved scope before asking again.
The same operation can reconcile terminal cell dimensions changed by a resize,
with or without a socket replacement. Require owner-approved receipt recovery,
unchanged pane identities and role positions, not an unchanged window size.

1. Read the original receipt and establish the intended host and native session.
   Require a version-2 `layout-ready` record with all four pane IDs, its original
   role map, launch arguments and layout. A partially created or unknown layout
   is not eligible. Do not adopt IDs from names, sidebar order or a different server.
2. Select an existing private durable backup directory under an approved root,
   outside scratch/cache. The agent can create an owner-only subdirectory for this
   authorized recovery. Preserve all earlier backups; the owner need not edit JSON.
3. Run the helper on that host with the original workspace/name/roles/Hermes root
   and verified route, adding `--rebind --backup-dir '/absolute/private/backups'`.
   Do not add `--create`, `--inspect` or `--finalize`. For external callers, include
   the explicit native session as in this single-line example, substituting known
   owner values, not the publisher's paths:

   ```bash
   python3 /path/to/project-onboarding/scripts/onboard.py --workspace '/approved/business-workspace' --hermes-root '/actual/hermes-home' --roles '/private/roles.json' --name 'Existing project' --session 'approved-session' --rebind --backup-dir '/approved/private/backups'
   ```

   The helper requires the same canonical socket path, same-user ownership and
   owner-only socket permissions. Under the existing receipt lock it checks exact
   recorded workspace/pane IDs, labels, project paths and tab. Both the saved and
   current rectangles must independently prove the same role-labelled, unzoomed
   2x2 layout. Different cell dimensions are accepted; changed roles, pane IDs,
   tab, project paths, malformed rectangles or moved/uneven panes are not. Keep
   the window size and layout stable during the operation. The helper never
   resizes panes, launches agents or changes Herdr state.
4. Before changing the binding, the helper saves and fsyncs the original receipt
   bytes to a unique owner-only backup. It rechecks native metadata, the socket and
   the receipt, then atomically saves the endpoint and any verified geometry update
   with an `endpoint_rebindings` audit entry: timestamp, old/new identities, backup
   path and original SHA-256. A resize also records `previous_layout` and
   `current_layout`. A second geometry change after the initial observation stops
   recovery and retains the backup. Other projects and historical fields stay intact. Native
   inspection is not an atomic transaction with Herdr; these are drift checks for
   cooperative owner-controlled state, not protection against a hostile same-user
   process. Keep the layout quiescent during recovery.
5. Read the result. `binding_status: rebound` is receipt recovery, with
   `readiness: not-verified`. `geometry_status: updated` means the verified resize
   was recorded, not that panes were moved. A matching socket reports
   `binding_status: unchanged` even if geometry was updated; only when both are
   unchanged is there no backup or receipt write. On failure, preserve any
   backup and inspect the receipt before retrying; a final durability error can
   occur after atomic replacement. Never assume a failed command means no write.
   Then run `--inspect` normally and separately verify each agent before startup
   or handoff. Restored shells are not restored authenticated agent sessions.

This does not repair Hermes recognition or make an unavailable upstream fix exist.
Linux tests do not establish native macOS acceptance. On a Mac, first run the
selected revision's stdlib recovery tests in isolated HOME/HERMES_HOME with dotenv
and lazy installs disabled: `python3 -B -m unittest discover -s tests -p test_project_rebind.py`.
They use synthetic native responses and local test sockets, not real Herdr or model
calls. Preserve their exact result, then perform the separately authorized native
receipt operation and read it back. Native macOS recovery remains unverified until
those host checks pass. Missing guidance should be routed to its owner once;
public issue posting is optional coordination, not a required recovery gate.

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
by the selected workflow; do not infer it from another profile. Use the
[per-profile integration checks](references/role-setup.md#verify-the-session-integration-per-profile)
before starting new sessions. The integration's
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

Verify each session's actual terminal working root through the
[terminal-root check](references/role-setup.md#verify-and-correct-the-session-terminal-root).
Pane cwd, launch `--in`, banners and session metadata do not replace tool output.
Use an authorized useful task for this check; a no-tools acknowledgement cannot
prove the terminal root. Keep any necessary correction local to the new session.

### Prove one fresh session before expanding the team

For first-host acceptance, or after a relevant runtime/launcher change, start one
selected role in the approved new test/project layout before launching the other
slots. Do not interrupt or use the owner's working team as test targets. A
successful existing session does not prove fresh startup; matching version numbers
or similar launcher source does not prove either failure or compatibility.
Reuse valid evidence for an unchanged combination rather than repeat model tests
for every project. Record the host, client/server versions, Hermes runtime,
profile, pane and conversation binding with that evidence.

1. Verify the target is the recorded available shell. Start that role once using
   the recorded native launch arguments. Retain the numeric exit status and native
   response. After a timeout or nonzero result, inspect the same pane read-only;
   a process may already exist. Do not retry startup or launch the remaining slots
   while the outcome is unresolved.
2. Verify recognition, interactive readiness, actual profile and working root.
   Record conversation identity separately; an absent identity is not a missing
   process. Do not install a session plugin as an assumed recognition repair.
3. With existing model-use/handoff authority, exercise one bounded response through
   `herdr agent prompt <target> <text> --wait --timeout <milliseconds>`. First read
   the exact destination and require an idle/done agent with an empty composer,
   no active turn, approval or draft. Use a unique non-sensitive acknowledgement
   marker, ask for no tools or durable memory writes, and read the response back
   from that same target. Prefer an isolated approved test conversation/memory
   scope. An instruction not to save is not isolation from automatic memory hooks;
   if isolation is unavailable, defer the synthetic probe or use the owner's
   approved first useful task. Do not silently disable shared memory settings.
4. Keep startup, submission evidence, completion wait and output retrieval results
   separate. A prompt-and-wait command may combine submission and waiting; its
   failure can leave submission unknown. A later successful read must not replace
   that command's exit status. A marker in echoed input is not an assistant reply.
   A sidebar completion icon or readable answer does not establish wait success.
5. Pass the round trip only when the native wait succeeds with the intended agent
   settled in idle/done and the expected assistant response is read back from the
   same bound conversation. Blocked, timeout, stalled, wrong target, missing
   response or missing result remains failed or unverified, not passed. Do not
   resend an ambiguous prompt. Inspect the existing attempt instead.

The agent can use this shell evidence-capture pattern after establishing the
target, prompt, timeout and a private evidence directory. Variables are discovered
values, not defaults to copy. Preserve separate command outcomes even in a shell
with `set -e`; do not rerun this block to recover a lost result.

```bash
prompt_wait_rc=0
herdr agent prompt "$target" "$probe" --wait --timeout "$timeout_ms" >"$evidence/prompt-wait.json" 2>"$evidence/prompt-wait.stderr" || prompt_wait_rc=$?
read_rc=0
herdr agent read "$target" --source recent-unwrapped --lines 80 >"$evidence/read.json" 2>"$evidence/read.stderr" || read_rc=$?
printf 'prompt_wait_exit=%s\nread_exit=%s\n' "$prompt_wait_rc" "$read_rc" >"$evidence/exits.txt"
```

Use a new private evidence directory per authorized attempt so prior results are
not overwritten. Keep raw terminal evidence private and bounded; redact secrets
and unrelated context before sharing. Record timestamps, exact target/session,
startup exit, submission evidence or uncertainty, wait exit/final state, read exit
and reply verification in the existing project/progress record. This example
captures evidence; it neither validates the results nor supplies authorization.

After this gate passes, the authorized operator continues the remaining
approved slot launches and per-slot readiness checks without another routine
"go on". Preserve concurrency/resource limits and stop only the affected work on
a real blocker. One successful role is not full-team acceptance or proof that
another host works. A runtime recognition defect remains a separate repair;
this procedure does not patch Herdr, extend timeouts or replace a working launcher.

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
