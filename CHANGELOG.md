# Changelog

## 0.1.0 (2026-09-26)

First release: the Creator + Education template and the `hbt` installer.

- Six roles (Video, Editing, Newsletter, Distribution, Community, Partnerships) and Ops, each a separate Hermes profile with its own playbooks and folder.
- Installer: install, update, uninstall and status, with a dry run and a sandbox end-to-end test.
- Editor and client desks are defined in the template but not installed. They come in v0.2 and will require rootless Docker.

Fixed during live testing on a real server:

- The main config keeps its formatting byte for byte; a plain round trip rewrote 332 lines.
- A pre-existing workspace is never deleted on uninstall.
- Kanban auto-review is off, so a role cannot approve its own card.
- Update keeps the owner's original values for settings the installer changed.
- Each role gets a Slack home channel, so its first reply has no setup notice.
- Card notices reach the role's channel.
- The Video role keeps a `status.md` per episode and a runtime line in each script, so the nightly checks can pass.
- Ops jobs run in the Ops folder (so they read their rules) and on the owner's timezone.
- Ops keeps no memory and posts without the Hermes cron wrapper, in a fixed plain format.
- A profile name Hermes marked as deleted can be installed again.
- Voice rules include punctuation, and every role follows them.
