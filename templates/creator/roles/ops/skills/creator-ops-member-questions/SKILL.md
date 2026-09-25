---
name: creator-ops-member-questions
description: "Use when the weekly scheduled job. Member question pull playbook for the Ops role."
version: 0.1.0
metadata:
  hermes:
    tags: [creator-template, ops]
---

# Member question pull

**Trigger:** the weekly scheduled job.

## Steps
1. Find the newest member-question export in incoming/questions/.
2. Create a Kanban card for the Community role (question digest) with the export path in the body.

## Done when
The card exists, or the reply says no new export was found.

## Approval
System output only. Do not create or change any business content.

The Kanban board is named in your AGENTS.md. Read canon/ before any public-facing work.
