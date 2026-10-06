---
name: creator-ops-morning-list
description: "Use when the 07:30 scheduled job. Morning approvals list playbook for the Ops role."
version: 0.1.0
metadata:
  hermes:
    tags: [creator-template, ops]
---

# Morning approvals list

**Trigger:** the 07:30 scheduled job.

## Steps
1. Locate this installed skill directory from the loaded skill path. Run `python3 "<installed skill directory>/scripts/format_approvals.py"`. Do not resolve the script relative to the Ops working folder or an installer checkout.
2. Return the helper's output unchanged, including an explicit failed digest on a nonzero exit. Do not turn a read failure into an empty-success message.
3. The helper reads board `creator` with native `list --status review --json`, `show <card-id> --json` and `notify-list <card-id> --json`. It does not mutate cards, call a provider or send messages. Native list can recompute ready dependencies, so this is not a globally zero-write native command.

## Format
Reply with only the list, no greeting and no sign-off. One line per card, grouped under the role's profile name, oldest first:

`- <card title> (<card id>), waiting <how long>, approval thread <recorded URL>`

Missing or invalid provenance becomes `approval thread link unavailable (<reason>)`. Missing or invalid review time becomes `waiting time unavailable`. Successful empty output is exactly `Nothing waiting for approval.`

Links come only from the current review handoff's `metadata.approval_thread`, as defined in the shared rules. The helper validates Slack workspace, channel and root timestamp, then returns the recorded URL unchanged. Do not synthesize links, use arbitrary comment URLs or substitute a result/system channel, channel root or dashboard link. Subscriptions alone do not identify the draft origin. Legacy and non-Slack cards may have no available link.

Use commas and parentheses for prose; literal URL punctuation is allowed. Never use em dashes or en dashes. Waiting time starts at the latest review request, not task creation.

## Done when
One short list, grouped by role, oldest review first, with recorded links or explicit unavailable notices. Unknown waiting times sort last within each role. A failed local read is reported as a failed digest.

## Approval
System output only. Do not create or change any business content.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.
