# Hermes Business Templates

Free, MIT-licensed starting setups for running a small business on [Hermes Agent](https://hermes-agent.nousresearch.com/docs). Each template installs a team of AI roles as separate Hermes profiles, on a server the business owns, using the owner's own AI subscription or API keys.

We provide the foundation only: roles, playbooks, folders, scheduled checks and an installer. Your business details, tools and accounts stay yours.

| Template | Status |
|---|---|
| Creator + Education | v0.1.0, first build |
| Project Services | planned |
| Industrial Supplier | planned |

## What the Creator template installs

- **Six roles:** Video, Editing, Newsletter, Distribution, Community and Partnerships. Each is its own Hermes profile with its own playbooks, its own folder and (optionally) its own long-term memory.
- **Ops:** one background profile that runs every scheduled job, so timers never fill the roles' memory with noise. It posts system output only (morning approvals list, nightly review, memory alerts, update notices) to one channel.
- **A shared business folder:** `canon/` (your business, voice, brand and standing rules, which only you edit) plus one folder per role.
- **A Kanban board** named `creator`. Roles hand work to each other as cards and wait for your approval in the thread.

Every role drafts; nothing is published, sent, priced or signed without your `approve`.

## Requirements

- A Linux server (or WSL) running Hermes 0.21 or newer, with the gateway connected to Slack.
- Your main Hermes profile logged in to a model provider (`hermes model`). The roles use the same model settings.
- Optional: [OpenViking](https://github.com/volcengine/OpenViking) for long-term memory. Without it, roles use Hermes's built-in memory.
- Optional: Docker. Without it, roles run commands directly on the server, limited by their folder and rules.

## Install

```bash
git clone <this repo> ~/hermes-business-templates
cd ~/hermes-business-templates
./hbt install creator --dry-run          # shows every change, changes nothing
./hbt install creator \
  --timezone America/Vancouver \
  --channel agents-report=C0123ABCD \
  --channel creator-video=C0234BCDE      # repeat for each role channel you created
hermes gateway restart                    # once, so the gateway serves the new roles
```

Then ask your main agent to run the canon interview in `canon/INTERVIEW.md` and fill in the four canon files.

Options: `--roles video,edit` installs a subset (Ops is always included). `--no-memory` skips OpenViking. `--workspace <path>` puts the business folder somewhere else. `-y` skips the confirmation.

### Slack channels

Create one channel per role (`#creator-video`, `#creator-edit`, `#creator-newsletter`, `#creator-distribution`, `#creator-community`, `#creator-partnerships`) plus `#agents-report`, invite your Hermes bot, and pass each channel ID with `--channel`. You can add channels later with `./hbt update creator --channel name=ID`.

Messages in a role's channel are answered by that role. `#agents-report` is routed to Ops, so keep it for system output and limited to the owner.

## Update

```bash
cd ~/hermes-business-templates && git pull && ./hbt update creator
```

Updates replace template-owned files only: each role's `SOUL.md`, playbooks and scripts, and the generated `AGENTS.md` files. Your `canon/`, your role folders' contents, your `.env` files, memories, sessions and any settings you changed are kept. Ops checks for a new version weekly and posts a notice.

## Uninstall

```bash
./hbt uninstall creator             # removes profiles, jobs, routes; archives the board
./hbt uninstall creator --delete-workspace   # also deletes the business folder
hermes gateway restart
```

Uninstall removes only what the installer recorded in `$HERMES_HOME/business-templates/creator/record.json`. Routes and settings you added yourself are never touched. The business folder and long-term memories are kept unless you ask otherwise.

## Memory

With OpenViking running, each role and desk gets its **own memory account**, so roles cannot see each other's memories. Facts every role needs belong in `canon/`, not in shared memory. Ops uses built-in memory only and watches OpenViking every 5 minutes, posting when it goes down, every 6 hours while it stays down, and when it recovers.

Roles run unattended from Kanban, so their built-in memory writes are off (an approval prompt nobody can answer would stall them).

## Tests

```bash
~/.hermes/hermes-agent/venv/bin/python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.
