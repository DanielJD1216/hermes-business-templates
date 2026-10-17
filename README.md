# Hermes Business Templates

**Start with your private agent, not an installation command.** This template is
an agent-led setup guide for a customer-owned [Hermes Agent](https://hermes-agent.nousresearch.com/docs)
system. The agent may use Claude, OpenAI or another suitable supported model. It
inspects the actual machine, adapts to existing state, executes approved work,
debugs failures and proves the finished setup. The development team is required;
the existing primary assistant keeps its own name and identity as EA.

Template guidance is MIT-licensed. Referenced software, skills and repair artifacts
have their own licenses, access requirements and costs. Your facts, accounts,
credentials and operating history are not part of this public repository.

## Start here: one message to your agent

Use your existing **private, tool-capable agent on the intended host**. Paste:

```text
Help me set up or resume Hermes Business Templates from https://github.com/DanielJD1216/hermes-business-templates.
Explicitly read README.md, AGENTS.md, skills/customer-onboarding/SKILL.md and its linked references from the same repository revision.
First verify that you can act on my intended host and inspect the existing setup. Preserve my current assistant, model/login, history, files and working access.
Follow the agent-led baseline, not the legacy Creator installer. Retrieve known facts before asking, propose the missing work and get the applicable approvals. Then execute and verify authorized work yourself; ask me only for missing decisions, account sign-in, OS permissions or actions your tools cannot perform.
Keep a private resumable progress record. Do not reset or reinstall working components, create unwanted roles, copy credentials or invent successful checks. Report exact blockers and whether the required baseline is actually complete.
Before each setup reply, reconcile that record against the selected guide and run its read-only progress checker. End the reply with its evidence-based fraction/percentage, current step, just-verified result, next action/actor and my exact action or none. Continue authorized work without asking me to say go on. Stop only for a real blocker, necessary owner action, a registered background continuation, my explicit pause or verified completion. Never promise an automatic return without a supported continuation route.
```

A URL does not automatically load instructions. The agent must actually read them.
A browser-only chat can guide you, but must disclose that it cannot execute host
setup. Model choice does not automatically provide host tools or make every
third-party service support the same authentication method.

## What the finished setup includes

The [required baseline](skills/customer-onboarding/references/baseline.md) covers
the whole operating workflow: preserved identity and model access; an explicit
EA/CTO/Engineer responsibility map; file placement and project onboarding;
persistent memory and a script-only watchdog; LEANN with scheduled index refresh,
exact and history discovery; a source-backed curated wiki viewed in Obsidian;
private Slack/Desktop/Tailscale access; four-pane Herdr development orchestration
and its Web UI; installed/tested role-specific capabilities; maintenance ownership;
Parsec for remote debugging/troubleshooting; and verified data backup/restoration.

The required project layout is EA top left, CTO top right, Engineer #1 bottom left
and Engineer #2 bottom right. Reuse the owner's main assistant as EA and approved
permanent specialist profiles. Names adapt; the required roles and positions do
not disappear. Default to separate Engineer profiles; sharing needs verified
memory/write safety. Extra non-development roles are not mandatory.

Review the full capability catalog, then install, authenticate where needed and
test a required role-specific set of skills, plugins, MCP integrations and toolsets.
Unresolved required items block completion. This does not mean enable every item
on every agent or waive account, license, cost or access approval.

The memory watchdog and LEANN index-refresh schedule are required. Choose their
scope, cadence, timezone, costs and failure recipient with the owner. Other schedules
remain opt-in. Kanban, formal delivery pipelines and old-conversation reconstruction
are outside onboarding. Parsec is mandatory for owner-approved remote debugging
and hands-on troubleshooting, not as a backup or data-restoration mechanism.
Existing tools and data are preserved; backups and restore verification remain mandatory.

Memory acceptance must also prove growth/tail recall, distinct-source retrieval,
owner scope, source preservation and truthful failure handling. Follow the required
[memory reliability checks](skills/customer-onboarding/references/memory-reliability.md):
reuse version-bound release evidence and run bounded checks on the actual host.
The watchdog must expose failed/stalled saves and version/patch drift, not just
healthy search. This guide ships no memory repair or acceptance runner and does
not certify a universally supported runtime combination. Missing compatible
artifacts or platform evidence block the memory requirement, not independent work;
Linux/WSL evidence does not establish native Mac support.

For repeatable per-project setup, use the bundled
[project-onboarding skill](skills/project-onboarding/SKILL.md). It retrieves the
project name/location/goal, preserves the existing primary assistant as EA,
prepares only approved missing role profiles through native operations, and creates
or reuses the required four-pane Herdr layout. Its stdlib helper creates shells,
not model sessions; the skill separately checks launch authority and readiness.
Install the complete skill in the selected coordinator's skill root and verify
discovery. It is not installed merely by reading this repository.

See [onboarding](skills/customer-onboarding/SKILL.md),
[context and file guidance](skills/customer-onboarding/references/context-and-files.md),
[sources and capability limits](skills/customer-onboarding/references/sources-and-capabilities.md),
and [Mac troubleshooting evidence](skills/customer-onboarding/references/mac-notes.md).
The [Herdr Web UI guide](skills/customer-onboarding/references/herdr-web-ui.md)
covers the existing-session browser client and its terminal-access security.

Memory and knowledge are distinct: OpenViking memories retain interaction-derived
facts; a knowledge base holds approved reference sources such as manuals, policies
and project documentation. Canonical files plus scoped retrieval can already serve
that purpose. OpenViking resources can index selected reference material when
needed, but do not replace required LEANN. No additional database or whole-workspace
duplicate ingestion is required.
See the [knowledge/retrieval boundary](skills/customer-onboarding/references/baseline.md#memory-knowledge-and-file-discovery).
Baseline acceptance demonstrates a small useful collection and a complete work
and retrieval cycle. Comprehensive memory-engine enforcement and customer-specific
business automation are separately scoped extensions, not hidden installation work.

## Current status and limits

This is a **published guide for an agent-led trial**, not a completed universal
installer or proof that every Mac/Linux configuration works. Actual host support,
provider access and each baseline outcome require evidence. Owner choices and
missing client access do not erase unfinished required checks.

The [capability reference sheet](capabilities/REFERENCE.md) and
[catalog](capabilities/catalog.json) contain 333 records: 198 included, 39 excluded
and 96 native candidates whose activation was not established. Included selections
cover 160 skills, 8 plugins, 13 MCP integrations and 17 native toolsets.

Delivery uses pinned upstream sources, vendor connection guidance and
[23 bundled generic procedures](reusable/procedures.md), not copies of a private
installation. Two third-party redistribution questions remain explicitly blocked
in the reference sheet. Included does not mean activated, authenticated or tested
on a customer's host. The main agent reviews the whole catalog and verifies the
required role-specific set, rather than stopping at inventory.

A bounded guide/resumption trial preserved synthetic identity, instructions,
project state and an unsent draft. It found and fixed a guide-version recording
gap. This was a Linux/WSL discovery exercise, not native Mac or service acceptance;
all full customer baseline checks remain untested by that exercise.

Use the [short maintenance/recovery procedures](skills/customer-onboarding/references/maintenance.md)
and optional [private progress template](skills/customer-onboarding/templates/progress.md).
The guide requires LEANN refresh and Obsidian acceptance, but does not itself install
services or schedules. Report verified rows / all required rows and the calculated
checklist percentage, not estimated effort. Reconcile older progress against this
revision without erasing historical evidence.

Every setup reply requires the onboarding skill's progress checkpoint. Its
[read-only checker](skills/customer-onboarding/scripts/check_progress.py) calculates
coverage and supplies the footer; owner-confirmed evidence remains labelled.
It checks record consistency, not whether receipts are genuine or host tests passed.
This guide installs no response hook, extra checker bot or notification service.
The agent must invoke the checker and use the result; text instructions alone do
not mechanically enforce every model reply or guarantee a later notification.

Repository checks use only Python's standard library and do not start Hermes:
`python3 scripts/check_customer_guide.py` and
`python3 scripts/check_capabilities.py --self-test`.

## Legacy backend is separate

The [historical Creator backend](legacy/README.md) is retained for separately
requested support of existing installations. It is not a fallback onboarding path.
Do not execute its installer or copy its role seeds to implement this guide.
The runtime paths remain stable; this separation does not delete customer state.

## License

MIT for this repository's authored guidance. See [LICENSE](LICENSE). Referenced
packages retain their own terms.
