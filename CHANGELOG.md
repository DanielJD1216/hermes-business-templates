# Changelog

## 0.4.0 (unreleased candidate)

Independent review pending. No tag, published release or client rollout.

- Install authored and explicitly selected native stock packages once in a durable template-owned library. Native `skills.external_dirs` selects exact package roots per role; no new loader, service or dependency.
- Preserve v0.3.2 role selections, deleted skills, disabled settings and customized whole packages. Capture old staged provenance and durable recovery archives before restaging; omit colliding managed entries rather than relying on native listing precedence.
- Keep `hermes-agent` native-managed locally, and opt template profiles out of nonessential bundled reseeding. Desks gain no shared roots or mounts.
- Record package hashes, native source/version, selections, managed settings, original values and recovery/conflict pointers in the existing install record. Status and offline checks diagnose missing assets, local shadows and unresolved conflicts. Explicit update is the repair/refresh path.
- Add recoverable migration activation and safe uninstall archives for custom local skills/settings. Preserve modified or unknown shared content and unrelated owner settings/assets. Conflicted updates return exit 2 instead of reporting a clean success.
- Archive custom external/create-dir skill packages inside removed profiles, recover partially deleted packages without overwriting owner edits, and resolve variable-based external roots in the consuming profile for collision checks.
- Preserve endangered packages discovered through ancestor roots, including cross-profile archive overlap, without archiving outside packages or arbitrary non-skill files.
- Verify 63 unit tests. Earlier revisions passed 63 real native sandbox CLI/discovery/seeding checks; the ancestor-root correction adds five focused native gates, including two expected ambiguity refusals and exact-byte preservation after uninstall. Runs use sandboxed homes and a kernel write boundary. Live Slack, gateway, provider, Docker, memory and release integration remain untested for this candidate.

## 0.3.2 (2026-09-29)

- Security fix: bots that hear each other could run each other's commands, because `@bot !approve` counts as a command and every allowed user could run commands. Commands are now limited to the owner (`slack.allow_admin_from` and `slack.group_allow_admin_from`), and `./hbt check` reports any bot without that limit. Existing installs: run `./hbt update creator`, then restart the gateway.

## 0.3.1 (2026-09-29)

- New channel `#offers-optimization` for the Creative Director: the offers themselves (promise, who each offer is for, price, features and benefits, proof), worked from `canon/offers.md`. Create it and invite the Creative Director and CTO; setup lists it with the other channels.
- `canon/offers.md` asks for features and benefits per offer: what it does, and what is in it for them.

## 0.3.0 (2026-09-29)

Fixes the gaps found by running the same setup for real: bots that could not hand each other work, copies that drifted apart, and nothing that noticed.

- The Creative Director and CTO are now peers: each hears the other by @mention, and setup invites each bot into the channels of the bots that hand it work. A handoff is an @mention in the sender's thread with the whole brief. Before, only CTO and Engineer could reach each other.
- New `./hbt check`: finds drift between the bots (owner profile, playbooks, tool sign-ins, handoff wiring, failing jobs, passed offer dates) and prints each gap with its fix. Ops runs it every morning and posts only when the gaps change.
- New `canon/offers.md`: what you sell, dates coming up, and replaced decisions. The Creative Director keeps it current with your approval; the canon interview fills it in.
- `./hbt update` now adds scheduled jobs the template gained since your install.

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
