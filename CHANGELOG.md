# Changelog

## 0.2.0 (2026-09-29)

The Creator template is now a working setup copied as is: a lead per department, one Slack app per bot, and a guided setup.

- Bots: Creative Director (Media and Marketing), CTO and Engineer (Build), and Ops (scheduled jobs, no Slack app). The six v0.1 specialist roles are gone; their 24 playbooks moved to the Creative Director.
- Plain profile names (`creative-director`, `cto`, `engineer`, `ops`). The installer refuses to overwrite a profile that already exists.
- Each bot gets its own Slack app file and settings: it answers its own channels without an @mention, ignores @mentions of other bots, and only the owner can talk to it. CTO and Engineer hear each other only by @mention, with thread follow-ups waking only the bot mentioned.
- CTO hands every build to Engineer on a Kanban card in `<projects>/<project>`; the result posts in Engineer's channel. Card-running bots save memories without an approval prompt, and are added to the Kanban runner list when the owner keeps one.
- New `./hbt setup`: one action at a time, each checked, resumable. New `./hbt connect`: hidden token prompt, checked with Slack, refuses a token another bot uses, finds channels by name.
- Desks: one per outside editor (`./hbt desk ... --name <editor>`), each with its own Slack app, channel and folder.
- No channel routes for the bots any more; only Ops keeps one, so it can post in `#agents-report` through the main agent's bot.

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
