# Slack setup and channel layout

Slack is where the owner works with the agents every day. The development team
works in T3 Code. This page covers which roles get a Slack app, how to create
each app and how to lay out channels. The Slack row of the [baseline](baseline.md)
defines what must be verified.

## Which roles get a Slack app

- The EA gets a Slack app when the owner uses Slack.
- An optional department lead gets its own app for its channels.
- The CTO and the Engineer work in T3 Code. Give them a Slack app only when the
  owner wants to talk to them in Slack.
- One app per role. Never give two profiles the same bot token.

## Create each app

Use the manifest generator that Hermes includes. Check
`hermes slack manifest --help` on the installed version first. For each role:

1. Generate the manifest in that role's profile, with the role's display name:
   `hermes -p <profile> slack manifest --agent-view --name "<display name>" --write`.
   Bare `--write` saves `slack-manifest.json` in that profile's Hermes home.
2. The owner opens https://api.slack.com/apps?new_app=1, chooses **From an app
   manifest**, pastes the file and installs the app to the workspace.
3. Store the bot and app tokens with the native setup for that profile:
   `hermes -p <profile> gateway setup`, then choose Slack. Never ask for tokens
   in chat.
4. Set the allowed users and the home channel for that profile. Invite the bot
   only to the channels where it works.

## Lay out channels by business function

- Make one sidebar section per business function, for example Marketing,
  Finance, Operations and People.
- Inside a section, make one channel per recurring job. Put the function first
  in the channel name, so the grouping also shows in search and channel lists.
- Keep one topic per channel. When two channels keep overlapping, merge them.
- Add an HQ channel for general requests to the EA, and a system channel for
  scheduled reports and alerts. The system channel is a good failure recipient
  for the maintenance row.
- Start small: HQ, system and the channels for the owner's first workflow. Add
  a channel when a new recurring job appears.

Example:

```text
HQ          hq
MARKETING   marketing-ideas
            marketing-distribution
            marketing-community
FINANCE     finance-revenue
            finance-invoices
            finance-expenses
OPERATIONS  ops-scheduling
SYSTEM      system-alerts
```

## Bot membership and privacy

- The EA joins HQ and the channels the owner chooses. A department lead joins
  the channels of its function. Scheduled jobs post to the system channel.
- In shared channels, a bot answers only when mentioned, including follow-ups
  in threads. Stock Hermes does not do this by default: after one mention, a bot
  keeps following that thread, and it answers messages that open by addressing
  someone else. On each bot's profile, run
  `hermes -p <profile> config set slack.strict_mention true` and
  `hermes -p <profile> config set slack.ignore_other_user_mentions true`.
  A channel where the bot should answer without a mention, such as its home
  channel, goes in `slack.free_response_channels` as channel IDs. The settings
  apply after the gateway restarts while no T3 work runs. Test in a thread where
  the bot was mentioned once: a reply without a mention gets no answer from it.
- To test denial, a person who is not among a bot's allowed users mentions it
  once, and the bot must not act. A guest account can play that person. When
  nobody is available, record the test as skipped by the owner; the Slack row
  stays unproven until someone runs it.
- Shared channels are group spaces. Private owner facts stay in direct messages
  or private conversations.

Record the approved channel map in the owner's private progress record and in
the workspace AGENTS.md ([template](../templates/workspace-agents.md)).
