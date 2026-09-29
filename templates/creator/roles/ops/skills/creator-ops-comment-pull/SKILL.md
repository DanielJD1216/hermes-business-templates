---
name: creator-ops-comment-pull
description: "Use when the monthly scheduled job. Comment pull playbook for the Ops role."
version: 0.1.0
metadata:
  hermes:
    tags: [creator-template, ops]
---

# Comment pull

**Trigger:** the monthly scheduled job.

## Steps
1. Find the newest comment export in incoming/comments/.
2. Create a Kanban card for the Creative Director (Video workstream topic queue), assigned to `creative-director` with the export path in the body.

## Done when
The card exists, or the reply says no new export was found.

## Approval
System output only. Do not create or change any business content.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.
