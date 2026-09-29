# Hermes Business Templates

Free, MIT-licensed starting setups for running a small business on [Hermes Agent](https://hermes-agent.nousresearch.com/docs). Each template installs a small team of AI bots, each a separate Hermes profile with its own Slack app, on a server the business owns, using the owner's own AI subscription or API keys.

We provide the foundation only: bots, playbooks, folders, scheduled checks and an installer. Your business details, tools and accounts stay yours.

| Template | Status |
|---|---|
| Creator + Education | v0.2.0: a department lead per area, one Slack app per bot, guided setup, one desk per outside editor. |
| Project Services | planned |
| Industrial Supplier | planned |

## What the Creator template installs

It copies a working creator business: one lead per department, the way a normal org chart grows. Rename anything to fit yours.

| Bot | Slack channels | Does |
|---|---|---|
| Creative Director | `#media-video`, `#media-edit`, `#media-newsletter`, `#marketing-distribution` | Leads Media and Marketing: topics, scripts, edits, newsletter, clips, community and sponsor drafts. 24 playbooks. |
| CTO | `#build-architect` | Leads Build: plans, system maps and PRDs. Never builds; hands each build to Engineer on a Kanban card. |
| Engineer | `#build-engineering` | Builds from the CTO's cards in `<projects>/<project>`, reports progress on the card, and asks the CTO when a plan is vague. |
| Ops | `#agents-report` (posts only) | No Slack app and no memory. Runs the scheduled jobs: morning approvals list, nightly review, memory and update watchdogs. |
| Editor desk | `#ext-editor-<name>`, one per editor | Optional. Answers one outside editor from a brief you write, inside a locked-down container. |

Your own main agent (your assistant) is not installed or changed. Every bot drafts; nothing is published, sent, priced or signed without your `approve`.

Also installed: a shared business folder with `canon/` (your business, voice, brand and standing rules, which only you edit) plus one folder per bot, and a Kanban board named `creator`.

## How the bots work together

- Each bot answers in its own channels without an @mention, and stays quiet when you @mention a different bot there.
- CTO and Engineer are invited to both build channels. They hear each other only when one @mentions the other, and a thread follow-up wakes only the bot you mentioned, so they never loop.
- Say "Create a new project called hello world, plan it and build it" in `#build-architect`. The CTO writes the plan, creates a card for Engineer, and the result posts in `#build-engineering`.

## Setup

```bash
git clone <this repo> ~/hermes-business-templates
cd ~/hermes-business-templates
./hbt setup creator
```

Setup walks you through one action at a time and checks each one before the next. You can stop anywhere; run it again and it picks up where you left off.

1. Asks for your timezone, your projects folder and your Slack member ID, then installs the bots, folders, board and jobs.
2. For each bot: prints its Slack app file. You create the app, then paste its two tokens into a hidden prompt. Setup checks them with Slack and refuses a token another bot already uses.
3. Finds each bot's channels by name and tells you which ones still need `/invite`.
4. Points Ops at `#agents-report` through your main agent's bot.
5. Asks you to run `hermes gateway restart` once.
6. Asks you to post "what's your job here?" in each bot's channel and waits for the right bot to answer.
7. Your first build: the hello-world card from CTO to Engineer.

Then ask your main agent to run the canon interview in `canon/INTERVIEW.md`. `./hbt status creator` shows what is installed and the next setup step.

### Desks for outside editors

```bash
./hbt desk creator desk-editor --name sam --guest U0123ABCD --channel ext-editor-sam=C0123ABCD
./hbt desk creator desk-editor --name sam --tokens      # hidden prompt for the desk's Slack tokens
```

Each editor gets their own Slack app, channel and folder (`desks/editor-sam`). A desk answers only its guests, only in its channel, with file tools only, inside rootless Docker with no network, and it sees nothing but its own folder. Desks install only where rootless Docker runs.

### Scheduled jobs

All times follow your timezone.

| Job | When | Posts |
|---|---|---|
| Morning approvals list | 07:30 daily | Every card waiting for your approval, or "Nothing waiting for approval." |
| Nightly review | 21:00 daily | Each bot's failed checks with the file or card behind them, or "All nightly checks passed." |
| Memory watchdog | every 5 minutes | Only when memory goes down, every 6 hours while it stays down, and when it recovers. |
| Update check | Mondays 09:00 | Only when a newer template version exists. |
| Comment pull, member questions | paused | Resume once you drop exports into `ops/incoming/`. |

## What has been tested

| Area | Result |
|---|---|
| Unit tests | 29 pass: template shape, config edits and exact restore, Slack settings, setup order, desk names. |
| Install in a clean sandbox | Passed on Hermes 0.21.5: 4 bots, workspace, board, 5 jobs, 3 Slack app files, the owner's config otherwise unchanged. |
| Connect and guided setup | Passed in the sandbox against a simulated Slack: refused the main agent's token, a bad token and a reused token; caught a missing invite; resumed mid-way and ran to the end. |
| Slack and card checks against a live workspace | Passed read-only: token check, channel lookup, spotting a bot's reply, and finding a finished card. |
| The same bots, settings and CTO to Engineer card flow | Running daily on the setup this template was taken from. |

**Not yet tested:** a full `./hbt setup` with real Slack apps from start to finish, cards on a separate `creator` board through a live gateway, a desk with long-term memory on, the two paused Ops jobs, a real memory outage, and any chat platform other than Slack. v0.1 installs cannot be updated to v0.2 in place: the bot names changed, so uninstall v0.1 first.

## Requirements

- A Linux server (or WSL2) running Hermes 0.21 or newer, with your main agent connected to Slack.
- Your main Hermes profile logged in to a model provider (`hermes model`). The bots use the same login and model settings.
- Optional: [OpenViking](https://github.com/volcengine/OpenViking) for long-term memory. Without it, bots use Hermes's built-in memory.
- Optional: rootless Docker, needed only for desks.

## Update

```bash
cd ~/hermes-business-templates && git pull && ./hbt update creator
```

Updates replace template-owned files only: each bot's `SOUL.md`, playbooks and scripts, and the generated `AGENTS.md` files. Your `canon/`, your folders' contents, your `.env` files, memories, sessions and any settings you changed are kept.

## Uninstall

```bash
./hbt uninstall creator             # removes profiles, jobs and our settings; archives the board
./hbt uninstall creator --delete-workspace   # also deletes the business folder
hermes gateway restart
```

Uninstall removes only what the installer recorded in `$HERMES_HOME/business-templates/creator/record.json`, and changed settings go back to your original values. The business folder, long-term memories and your Slack apps are kept unless you remove them.

## Memory

With OpenViking running, each bot gets its **own memory account**, so bots cannot see each other's memories. Facts every bot needs belong in `canon/`, not in shared memory. Ops keeps no memory. Bots that run Kanban cards save memories without an approval prompt, because a card runs in the background where nobody can click one.

## Known limits

- OpenViking has no login in its default local setup. Any program on the server can read any memory account by name, so keep the server to trusted software.
- Slack is the only chat platform tested.
- Messages you post in `#agents-report` go to Ops, because that route is how Ops posts through your main agent's bot. Keep the channel for system output.
- Turning on Kanban for the CTO's Slack tools saves Hermes's full default tool list for that bot, so it will not pick up tools Hermes adds to its defaults later. Re-run `hermes -p cto tools enable kanban --platform slack` after a Hermes update if you want them.
- A full install takes a few minutes: every change is made through the `hermes` command so Hermes checks it.

## Tests

```bash
~/.hermes/hermes-agent/venv/bin/python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.
