---
name: project-onboarding
description: "Use when the owner explicitly onboards a project."
version: 0.1.0
author: Hermes Business Templates contributors, Hermes Agent
license: MIT
platforms: [linux, macos]
---

# Project onboarding

Ordinary chat, research, drafting, fixes and implementation stay in the originating
conversation. A role label, code request or available Herdr tool is not onboarding
consent. Use this procedure when the owner asks to onboard/set up a project or
explicitly chooses the Herdr project workflow. Do not make the owner relay reports.

## Discover before asking

1. Ask the **project name first**, only if it is missing. Reuse a supplied name exactly.
2. Read the business workspace's `PROJECTS.md`, `.hbt-projects.json` if present,
   applicable install record's projects root, conversation context and exact known
   project location. Do not search private catalogs or scan the whole home directory.
3. Ask for the **existing repo/location**, only if still missing or ambiguous. If it
   is a new project, agree its exact new folder under the approved projects root.
   Reuse existing repos, instructions, branches and changes. No automatic cloning,
   moving, Git initialization, checkout resets, worktrees or replacement AGENTS.md.
4. Ask for the **goal**, only if missing. A known goal does not need reconfirmation.
   Separate project setup from permission to implement, publish, deploy or spend.

Read `FILES.md` for file placement/access. Semantic search is optional, manually
installed and indexed by the owner. It is not required, bundled or scheduled.
When loaded through native discovery outside the business workspace, resolve that
workspace from the approved install record or supplied path first. Do not treat
this skill's installation directory or the current repo as the business workspace.

## Prepare Herdr safely

- Herdr is owner-installed. Run `herdr --help` and `herdr --skill`, then relevant
  command groups and `herdr api schema --json` if shapes differ. The installed
  binary is authoritative. Do not silently upgrade/restart a server.
- Require `HERDR_ENV=1` and an inherited `HERDR_SOCKET_PATH`. Outside a Herdr pane,
  report that transport limit and ask the owner to open the intended session.
  Never spoof these variables to control the user's focused session.
- Read the intended session's `workspace list`, `pane list` and `agent list` before
  acting. Reuse a recorded layout. An unrecorded matching name/location requires
  inspecting its actual panes and agreeing how to reuse it, not duplicating it.
- Verify the selected native `default`, `cto` and `engineer` profiles exist. Never
  create or clone a missing profile automatically. The main assistant is the
  **existing default profile**, not a new executive-assistant runtime profile.
- Keep one coordinator. Four visible slots are not four authorized assignments.

From the authorized pane, invoke the bundled stdlib helper (substitute discovered
absolute paths and quote shell values):

```bash
python3 /path/to/project-onboarding/scripts/onboard.py \
  --workspace /path/to/business-workspace \
  --name 'Project name' --path /path/to/existing-project --goal 'Known goal'
```

Add `--create` only for the agreed missing folder. It creates that directory only;
it does not overwrite files, clone a repo, write project instructions or start work.
For a recorded project, `--workspace` and `--name` suffice. A changed goal/path,
server restart, partial receipt or modified layout stops rather than recreating it.
Inspect and reconcile interrupted receipts with native state; do not delete the
receipt to bypass a refusal. No automatic rollback closes possibly active panes.

Default arrangement, verified through native pane geometry:

| Position | Slot | Runtime profile |
|---|---|---|
| Top left | Executive Assistant | default |
| Top right | CTO | cto |
| Bottom left | engineer1 | engineer |
| Bottom right | engineer2 | engineer |

The helper creates **labelled shell panes**, reads their native layout back, and
prints a receipt with explicit `launch` argument arrays. It does not send input,
start Hermes, authenticate a provider or run a prompt. Preserve this distinction
in progress reports: layout ready is not four live agent sessions.

## Start the selected sessions, then verify

Starting the four interactive sessions is the next step of owner-selected project
onboarding, not a background installer action. Read each target using `pane get`,
`pane process-info` and `pane read` before any launch. On repeat onboarding inspect
`agent get`/`agent read`; reuse verified existing sessions rather than relaunching.
Do not interrupt a foreground command, active turn, approval dialog or owner draft.
If a shell's readiness or draft state is uncertain, ask instead of sending keys.

Use the receipt's exact `launch` argv with native `herdr agent start`. These are
fresh interactive Hermes starts with explicit `-p` values, no prompt, no `--continue`
or shared `--resume` ID. engineer1 and engineer2 are **separate sessions using the
same engineer profile**, not cloned profiles or a shared conversation. Native
startup may expose login/tool-connection needs; report them, never copy credentials.
Inspect `agent get` and `agent read` after startup, confirm profile/working directory
and distinct session IDs when available. If native detection cannot prove a session,
report unverified rather than claiming startup success. Do not auto-answer logins.

The main profile's SOUL stays unchanged. Optional Executive Assistant identity
adoption is a separate owner-reviewed merge from the package's SOUL document.

## Assign work only with scope

All four shells initially use the approved repo/location. **Do not automatically
send implementation prompts to both engineers on the same checkout.** Appoint one
implementation owner. Leave engineer2 idle unless independent read-only work or an
explicitly approved separate checkout/worktree and write boundary is assigned.
Never create worktrees or enable nested delegation merely because two panes exist.

For an authorized handoff: read the exact destination, confirm identity/readiness,
preserve drafts, send the scoped brief through native `agent prompt`, then verify
receipt/observed activity and the result at that destination. A timeout does not
prove non-delivery, so read before retrying. Keep the agreed return route, repository
checks and independent review gates. The originating business chat need not move
into Herdr, and a missing transport is not permission to change its audience.

## Pitfalls

The helper requires Unix sockets and `fcntl`; native Windows is unsupported. Use
the Linux/WSL host for a Windows client. macOS behavior still needs acceptance.
Native registration follows `FILES.md` and is optional; it grants no Herdr access.
Changed receipt launch commands or profiles are refused, not silently repaired.

## Done when

Report project name, reused/created directory, goal, verified layout and exact pane
IDs. Separately report which agent sessions are verified, awaiting owner startup,
or blocked. State the one writer, coordinator, checks and return destination when
work is assigned. No setup test may use real prompts/provider calls without separate
authorization. Do not claim a handoff, model login or completed work from pane labels.
