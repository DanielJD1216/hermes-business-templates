# Canonical documents and project onboarding

Status: integrated into the local unreleased Creator candidate. Not a live rollout,
provider-login acceptance or public release.

## Package map

| Package path | Installed / intended destination | Behavior |
|---|---|---|
| `templates/creator/roles/{creative-director,cto,engineer,ops}/SOUL.md` | Selected native profile homes | Generic role identity through existing profile distributions |
| `templates/creator/roles/executive-assistant/SOUL.md` | Optional reviewed merge into the existing default profile | Document only; no new profile, automatic adoption or identity overwrite |
| `templates/creator/workspace/AGENTS.md` and `RULES.md` | Rendered root and role-folder AGENTS.md | Canonical policy, actual shared-root pointer and selected-profile roster |
| `templates/creator/workspace/USER.md` | Shared workspace `USER.md` | Blank private worksheet; explicitly read only when relevant and authorized |
| `templates/creator/workspace/canon/` | Shared workspace `canon/` | Blank owner-maintained business, offers, voice, brand and standing worksheets |
| `templates/creator/workspace/FILES.md` | Shared workspace `FILES.md` | Placement, access, discovery and optional search guidance |
| `templates/creator/workspace/PROJECTS.md` | Shared workspace `PROJECTS.md` | Blank human-maintained project index; no author's private catalog |
| `templates/creator/workspace/skills/project-onboarding/` | Same relative path in shared workspace | Reusable procedure and stdlib Herdr layout helper, explicitly read via AGENTS.md |

The workspace skill is not automatically registered in the default profile's skill
list. It is accessible by its documented path without changing that profile's config.
For explicit native adoption, follow the installed FILES.md procedure: append only
the exact reviewed `skills/project-onboarding` directory to the chosen profile's
existing `skills.external_dirs` with native `hermes config set`. Preserve all other
roots/settings and SOUL bytes, refuse unresolved collisions or disabled-skill intent,
and verify native list/view resolves that exact source and its helper. No new
installer, automatic config mutation or profile cloning is needed. This registers
a live reference, not a pinned copy; workspace updates and filesystem permissions
still govern its content. Withdrawal removes only that entry, never owner skills.
Selected native shared skills remain a different, provenance-tracked library.
No external tool is installed by registering either kind of skill. See the native
[skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills#external-skill-directories).

## Adoption and updates

Back up the destination before an optional identity merge. Review the Executive
Assistant document against the default profile's existing SOUL.md and merge only
approved sections. Retain recipient-specific personality, permissions and history.
Changing a display name does not rename a runtime profile or grant authority.
Never clone a live profile or import its memory, credentials or conversations.

The installer seeds USER, canon, indexes and guidance without overwriting existing
copies. Generated AGENTS.md and bundled workspace skill files are updated only
when their bytes match `.hbt-workspace.json` provenance. Changed or untracked files
are preserved and reported for manual merge. Older installations without hashes
need a reviewed instructions merge; the installer does not infer ownership from
an AGENTS.md heading. Ordinary unchanged updates remain repeatable. Do not edit
provenance to bypass a retained-file warning. This is preservation, not rollback
or a filesystem security boundary.

Native instruction discovery is version-dependent. Root and role working directories
have their own generated instructions; an existing project's instructions are never
replaced by onboarding. A higher-priority `.hermes.md` or override may take precedence.
When work moves into a repo, the scoped handoff must name the relevant shared policy
and business files explicitly. Do not assume the business workspace's USER or canon
is automatically injected into an unrelated repo, or expose private USER in a group.

## Explicit onboarding contract

Ask for project name first, then only missing repo/location and goal. Reuse supplied
facts and verified indexed projects before asking again. Ordinary requests remain
in-thread; explicit project onboarding selects this default Herdr arrangement:

| Top left | Top right |
|---|---|
| Executive Assistant, existing profile `default` | CTO, profile `cto` |
| engineer1, profile `engineer` | engineer2, profile `engineer` |

The two engineers use separate conversations with the same profile. They are not
separate security sandboxes. No concurrent writing on the same checkout is assigned
automatically. Keep one implementation owner; engineer2 waits for a separately
scoped read-only task or approved isolated checkout.

Run the helper from an authorized Herdr pane with inherited socket context. It
creates or verifies four labelled shell panes, preserves focus, records exact IDs
and checks their native geometry. It does not start a provider or send a prompt.
The skill's next step reads each destination, starts/reuses the selected interactive
Hermes sessions with explicit profile and `--in` project path, and verifies them.
An existing active turn or draft is never replaced. Session startup and handoff
receipt need their own evidence; pane labels do not prove either.

A missing directory is created only with explicit `--create` and an existing approved
parent. Existing repositories remain untouched. Repeat onboarding reuses recorded
IDs after read-back. Name/path conflicts, unrecorded matching native workspaces,
changed geometry, profile/launch commands, socket identity changes and partial receipts stop without blind
recreation. Partial failure can leave owned panes for inspection; the helper never
closes them automatically. Receipt locking serializes this helper, not other Herdr
clients or human edits. Local Unix sockets are supported; native Windows and remote
machine forwarding are not implemented in this helper. A Windows client attached
to Linux/WSL uses the helper on that host.

## Retained, adapted, excluded

Retained: practical communication, resourcefulness, verification, privacy, scoped
authority, one implementation owner and honest independent review.

Adapted: a personal main assistant becomes an optional Executive Assistant document;
roles use stable keys and recipient-configured routes; transport is not fixed by
identity; ordinary work is direct and team orchestration is intentional.

Excluded: author identity and personal facts, customer/project history, private
catalogs, device/network paths, account IDs, credentials, conversations, memory
stores, historical permissions, model choices and deployment grants. Client-specific
customizations belong in a separate private implementation, not the public baseline.

## Optional and unverified

- Herdr: owner-installed; no server config changes or integration installation.
- Local semantic search: optional, owner-installed, manually indexed approved roots.
- Tools/MCP reference sheet: separate publisher deliverable, not yet a finalized PDF.
- Main-assistant identity adoption: optional reviewed merge. Native skill registration:
  optional FILES.md procedure, tested only in an isolated native profile home.
- Only the existing optional memory watchdog can be scheduled. No new recurring job.
- Provider login, four live model sessions, prompt handoffs, Slack delivery, memory
  service, editor-desk enforcement and macOS hardware acceptance need separate proof.

Synthetic tests cover preservation and helper contracts. Native Linux/WSL acceptance
separately exercised layout geometry and repeat reuse without agents, and native
profile installation/context loading without provider calls. Neither is a model
behavior, authentication or policy-enforcement guarantee.
