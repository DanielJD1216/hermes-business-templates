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

## Done when
One short list, grouped by role, oldest first.

## Approval
System output only. Do not create or change any business content.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.
