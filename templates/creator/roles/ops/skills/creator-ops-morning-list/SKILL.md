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
1. Run `hermes kanban --board creator list --status review --json`.
2. For each card, list the role (assignee), the title and how long it has waited.
3. If nothing is waiting, reply with exactly: Nothing waiting for approval.

## Format
Reply with only the list, no greeting and no sign-off. One line per card, grouped under the role's profile name, oldest first:

`- <card title> (<card id>), waiting <how long>`

Use commas and parentheses only. Never use em dashes or en dashes.

## Done when
One short list, grouped by role, oldest first.

## Approval
System output only. Do not create or change any business content.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.
