---
name: creator-ops-nightly-review
description: "Use when the 21:00 scheduled job. Nightly review playbook for the Ops role."
version: 0.1.0
metadata:
  hermes:
    tags: [creator-template, ops]
---

# Nightly review

**Trigger:** the 21:00 scheduled job.

## Steps
1. Read the Nightly checks section of each role's AGENTS.md (paths are in the roster in your AGENTS.md).
2. Answer each check with yes or no from the folders and from `hermes kanban --board creator list --json`.
3. Report only the failed checks, grouped by role, each with the file or card that failed.

## Format
Reply with only the result, no greeting and no sign-off. One line per failed check, grouped under the role's profile name:

`- <check>: <file or card that failed>`

Use commas, colons and parentheses only. Never use em dashes or en dashes.

## Done when
One post; if every check passed, reply with exactly: All nightly checks passed.

## Approval
System output only. Do not create or change any business content.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.
