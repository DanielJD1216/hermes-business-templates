# Hermes Business Templates

Free, MIT-licensed starting setups for running a small business on [Hermes Agent](https://hermes-agent.nousresearch.com/docs). Each template installs a team of AI roles as separate Hermes profiles, on a server the business owns, using the owner's own AI subscription or API keys.

We provide the foundation only: roles, playbooks, folders, scheduled checks and an installer. Your business details, tools and accounts stay yours.

| Template | Status |
|---|---|
| Creator + Education | v0.1.0: roles and Ops. Editor and client desks come in v0.2. |
| Project Services | planned |
| Industrial Supplier | planned |

## What the Creator template installs

- **Six roles:** Video, Editing, Newsletter, Distribution, Community and Partnerships. Each is its own Hermes profile with its own playbooks, its own folder and (optionally) its own long-term memory.
- **Ops:** one background profile that runs every scheduled job, so timers never fill the roles' memory with noise. It posts system output only (morning approvals list, nightly review, memory alerts, update notices) to one channel.
- **A shared business folder:** `canon/` (your business, voice, brand and standing rules, which only you edit) plus one folder per role.
- **A Kanban board** named `creator`. Roles hand work to each other as cards and wait for your approval in the thread.

Every role drafts; nothing is published, sent, priced or signed without your `approve`.

## What has been tested

v0.1.0 was installed on a real server (Ubuntu 24.04 on WSL2, Hermes 0.21.5, Slack, OpenViking, a ChatGPT subscription login) with the Video role and Ops, used, and uninstalled.

| Area | Result |
|---|---|
| Install, update and uninstall | Passed with all seven profiles in a sandbox, and with Video and Ops on the live server. Uninstall restored the main config byte for byte. |
| Main config edits | Only the added lines change. Your formatting, comments and settings are kept. |
| A role answering in its own Slack channel | Passed (Video). The role answers, not the main agent, and works in its own folder. |
| Kanban card from start to your approval | Passed. The card stops at review and waits for you; the role cannot approve its own work. |
| Card notices in the role's channel | Passed. |
| Separate long-term memory per role | Passed (Video). |
| Morning approvals list | Passed when run on demand: posted the waiting card to `#agents-report`. Its 07:30 run uses the same scheduler as the nightly review. |
| Nightly review | Passed. Ran on schedule at 21:00 owner time and named the file behind each failed check. |
| Memory watchdog | Passed while memory was healthy (silent, as designed). The outage alert path is covered by tests, not a live outage. |
| Update check | Passed. Silent when no newer version exists. |

**Not yet tested on a live server:** the Editing, Newsletter, Distribution, Community and Partnerships roles (their playbooks are written but have not run against real work), the two paused Ops jobs (comment pull and member questions), a real memory outage, and any chat platform other than Slack.

## Requirements

- A Linux server (or WSL2) running Hermes 0.21 or newer, with the gateway connected to Slack.
- Your main Hermes profile logged in to a model provider (`hermes model`). The roles use the same login and model settings.
- Optional: [OpenViking](https://github.com/volcengine/OpenViking) for long-term memory. Without it, roles use Hermes's built-in memory.
- Optional for v0.1: Docker. Without it, roles run commands directly on the server, limited by their folder and rules. The v0.2 editor and client desks serve people outside the business, so they will install only where rootless Docker is available.

## Install

```bash
git clone <this repo> ~/hermes-business-templates
cd ~/hermes-business-templates
./hbt install creator --dry-run          # shows every change, changes nothing
./hbt install creator \
  --timezone America/Vancouver \
  --channel agents-report=C0123ABCD \
  --channel creator-video=C0234BCDE      # repeat for each role channel you created
hermes gateway restart                    # once, see below
```

The restart is needed once: the gateway picks up new profiles, channel routing and the Kanban runner setting at startup. Until then the roles do not answer and nothing posts.

Then ask your main agent to run the canon interview in `canon/INTERVIEW.md` and fill in the four canon files.

Options: `--roles video,edit` installs a subset (Ops is always included). `--no-memory` skips OpenViking. `--workspace <path>` puts the business folder somewhere else. `-y` skips the confirmation.

### Slack channels

Create one channel per role (`#creator-video`, `#creator-edit`, `#creator-newsletter`, `#creator-distribution`, `#creator-community`, `#creator-partnerships`) plus `#agents-report`, invite your Hermes bot, and pass each channel ID with `--channel`. You can add channels later with `./hbt update creator --channel name=ID`.

Messages in a role's channel are answered by that role. `#agents-report` is routed to Ops, so keep it for system output and limited to the owner.

### Scheduled jobs

All times follow the `--timezone` you give (the server clock otherwise, which is often UTC).

| Job | When | Posts |
|---|---|---|
| Morning approvals list | 07:30 daily | Every card waiting for your approval, or "Nothing waiting for approval." |
| Nightly review | 21:00 daily | Each role's failed checks with the file or card behind them, or "All nightly checks passed." |
| Memory watchdog | every 5 minutes | Only when memory goes down, every 6 hours while it stays down, and when it recovers. |
| Update check | Mondays 09:00 | Only when a newer template version exists. |
| Comment pull, member questions | paused | Resume once you drop exports into `ops/incoming/`. |

## Update

```bash
cd ~/hermes-business-templates && git pull && ./hbt update creator
```

Updates replace template-owned files only: each role's `SOUL.md`, playbooks and scripts, and the generated `AGENTS.md` files. Your `canon/`, your role folders' contents, your `.env` files, memories, sessions and any settings you changed are kept.

## Uninstall

```bash
./hbt uninstall creator             # removes profiles, jobs, routes; archives the board
./hbt uninstall creator --delete-workspace   # also deletes the business folder
hermes gateway restart
```

Uninstall removes only what the installer recorded in `$HERMES_HOME/business-templates/creator/record.json`. Routes and settings you added yourself are never touched, and changed settings go back to your original values. The business folder and long-term memories are kept unless you ask otherwise. `--delete-workspace` refuses a folder that existed before the install.

## Memory

With OpenViking running, each role gets its **own memory account**, so roles cannot see each other's memories. Facts every role needs belong in `canon/`, not in shared memory. Ops keeps no memory; it watches OpenViking every 5 minutes instead.

Roles run unattended from Kanban, so their built-in memory writes are off (an approval prompt nobody can answer would stall them).

## Known limits

- OpenViking has no login in its default local setup. Any program on the server can read any memory account by name, so keep the server to trusted software.
- Slack is the only chat platform tested.
- One Slack bot serves every role. Roles are told apart by channel, not by bot name.

## Tests

```bash
~/.hermes/hermes-agent/venv/bin/python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.
