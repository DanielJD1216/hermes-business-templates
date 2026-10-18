# Herdr Web UI

Include [devswha/herdr-web-ui](https://github.com/devswha/herdr-web-ui) alongside
Herdr in the baseline. It is a browser/phone view of existing Herdr sessions,
not another agent coordinator, a replacement for Hermes Desktop, or a requirement
to move every task into Herdr. Preserve the same sessions and terminal identities.

## Inspect and choose the supported route

Read the current upstream [agent installation guide](https://github.com/devswha/herdr-web-ui/blob/main/INSTALL.md)
and [user guide](https://github.com/devswha/herdr-web-ui/blob/main/docs/guide.md).
Use installed help for the actual release. Confirm supported OS/architecture,
Herdr, Bun and any Node prerequisite; do not assume a PATH entry means the running
Herdr process sees that same environment. Reuse a working existing installation.

Upstream offers a Herdr plugin and a source/service installation. Prefer its
supported plugin route for a new ordinary setup; do not migrate a working
source/service installation just to match that preference. Preserve saved devices,
state, configuration and the exact running build. An update supervisor may run a
newer build than the original checkout. Verify runtime evidence, not folder names.

The one-line upstream installer can install prerequisites AND change Tailscale
Serve configuration. Inspect that scope and obtain any missing owner authority
before using it. Do not star a repository, create an account or accept a purchase
for the owner. Do not stop/restart the Herdr server or its agents merely to install,
update or debug the web client. Coordinate any genuinely necessary disruptive
prerequisite repair separately with a verified resume/recovery path.

## Terminal-access security comes first

- Preserve the default loopback binding, normally `127.0.0.1:7317`. A reachable
  unprotected web UI can type into agent terminals; it is not a harmless dashboard.
- Remote browser/phone access needs an explicitly approved private route and
  effective access control. Use the existing Tailscale design or a reviewed secure
  alternative. Never enable public Funnel, `0.0.0.0`, or a broadly accessible proxy
  as a convenience. Preserve other existing Serve handlers and the recovery route.
- Tailscale membership alone is not proof of app authorization. Verify the installed
  version's owner-identity, pairing/token and proxy behavior, plus actual access
  and denial from the relevant clients. Do not blindly enable a trust-proxy or
  Serve-only bypass. Same-owner exceptions depend on the real topology and owner
  confirmation; a shared tailnet or additional proxy changes the trust boundary.
- Store any required token using the native protected configuration path. Never
  print tokens, pairing codes, private keys or credential-file contents in chat,
  logs, this repository or onboarding evidence. Do not copy the publisher's token,
  tailnet name, host address, session IDs or installation path.
- Review telemetry, automatic updates, push notifications, microphone/transcription
  and usage-meter options with the owner. They may involve external services or
  credentials even though session files stay on the host. Do not enable them or
  add paid API requirements silently. Browser speech is not automatically offline.

## Standard four-pane development preset

This preset is required for per-project development orchestration. Names adapt to
the owner; the responsibilities and positions remain fixed. Ordinary non-development
conversations need not move into Herdr. Carry compatible existing approvals forward;
an older approval for main-only access does not authorize creation or model launches.

| Top left | Top right |
|---|---|
| Executive Assistant | CTO |
| Engineer #1 | Engineer #2 |

The existing primary assistant fills Executive Assistant; display names and role
assignments adapt to the owner. Default to one Engineer profile with two distinct
sessions. Verify supported shared-profile memory/write safety before concurrent
use; separate session IDs do not isolate profile memory. If that safety is unverified,
report the concurrency blocker rather than automatically creating a second profile.
Preserve separately approved exceptions through the
[role preparation procedure](../../project-onboarding/references/role-setup.md).
An unresolved concurrency issue leaves readiness incomplete; do
not substitute a shell-only slot for acceptance. They may work in parallel only
with non-overlapping ownership and isolated writable workspaces where needed.
Do not create unapproved worktrees or two writers for the same files. Keep one
coordinator; the preset does not make every pane a coordinator.

Present the required mapping and reuse approved permanent profiles. Obtain missing
authority to create CTO/Engineer roles rather than treating them as optional.
Do not reactivate deleted profiles or replace the main assistant. Main-only use,
an alternative layout or labelled shells leaves baseline acceptance incomplete.
An idle shell labelled CTO is not evidence that a CTO agent exists or is ready.
Distinguish persistent profile, terminal pane, running process and conversation.

For creating or reusing this layout per project, use the bundled
[project-onboarding skill](../../project-onboarding/SKILL.md), including its native
role-preparation step and stdlib layout helper. Reuse the owner's existing assistant
as EA; create missing specialists only after approval, once for reuse rather than
once per project. Never copy the publisher's profile names, identity or credentials.

Verify the complete installed skill and authorized control/return route before
layout creation. The originating Slack, Desktop or terminal conversation can use
the project helper's explicit `--session` route when its tools reach the approved
host. Running inside a Herdr pane is not required for that route. Keep exact server
and project binding; browser access alone does not supply host execution authority.
Follow the project skill's
[single-session acceptance gate](../../project-onboarding/SKILL.md#prove-one-fresh-session-before-expanding-the-team):
prove one fresh role's startup, recognition and authorized response round trip on
the actual host before launching the remaining slots. Preserve each command's
exit status and target binding. Existing working agents, echoed prompt text,
sidebar status and a later successful read are not substitutes for that proof.
After the gate passes, the authorized operator continues approved setup; do not make
the owner execute every routine step. A missing control route or a runtime defect
remains a named blocker, not a reason to spoof context or modify working agents.

After approval, the setup agent configures the selected preset with supported
native operations, using the installed version's help. Preserve existing sessions,
drafts, working directories and pane identities. Never rearrange a busy workspace
or auto-start model sessions to demonstrate a layout. If native support is missing,
report the exact limitation rather than inventing a command or silently updating.

Verify and record positions, labels, actual profile/session bindings, project
roots and idle/running state. Check the owner's chosen client: an active pane may
be zoomed, and client/version capabilities can differ. Do not infer the entire
workspace layout from one visible pane or claim a four-pane view from labels alone.

## Explain the owner-facing step

Before sending the owner to Herdr, state whether this is an access check, preset
selection or a ready development session. Name the expected workspace and exactly
what the owner should observe. A shell prompt is a terminal, not an assistant
waiting for a natural-language request. For an access-only check, explicitly say
not to type commands; a loaded idle shell proves only that limited check.

Do not leave the owner at a blank terminal to work out setup. Configure approved
work yourself where tools permit; otherwise give one precise owner action and
explain the access limitation. Confirm an actual intended agent is ready before
asking the owner to send it a task, with the applicable launch/model-use authority.
An update banner is not a prerequisite or permission to upgrade a working client.

## Acceptance evidence

The agent checks and records:

1. Actual web-client build, Herdr compatibility, selected install method and healthy
   connection to the intended Herdr server. A queued plugin action is not success.
2. Existing workspaces/panes and terminal identities are preserved. No duplicate
   sessions, replaced drafts, unrequested worktrees or accidental sends.
   The selected preset's positions, profile/session mapping and idle/running states
   are recorded. A browser-load check alone does not verify the development preset.
3. The owner's browser opens the intended session and can use the supported
   chat/terminal view. Any input test needs the right target and approved scope;
   do not type into a busy agent, a user draft or a dangerous terminal prompt.
4. Loopback binding, authenticated/private remote route, effective authorization
   and denial of unauthorized access. Local health alone does not prove these.
5. Chosen startup/update behavior and recovery are documented and checked. A
   transient process is not proof the UI returns after a reboot. Do not reboot a
   working host merely for acceptance without owner coordination.
6. Phone/PWA installation, push or microphone tests only when selected and the
   device is available. HTTPS/secure-context requirements and provider processing
   must be explained. Missing phone access does not block independent host work;
   report that selected client check as pending rather than claiming it passed.

Installation and the verified four-session development team are required for the
baseline. Obtain applicable authority before starting agents or sending handoffs;
missing authority leaves acceptance pending. Using Herdr for non-development work,
adding remote PCs and enabling phone extras remain separate owner choices.
