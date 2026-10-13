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

## Acceptance evidence

The agent checks and records:

1. Actual web-client build, Herdr compatibility, selected install method and healthy
   connection to the intended Herdr server. A queued plugin action is not success.
2. Existing workspaces/panes and terminal identities are preserved. No duplicate
   sessions, replaced drafts, unrequested worktrees or accidental sends.
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

Installation is required for the browser-based Herdr baseline. Using Herdr for
ordinary tasks, adding remote PCs, sending messages, starting agents and enabling
optional phone integrations remain separate owner choices.
