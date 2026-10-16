# Hermes Business Templates

**Start with your private agent, not an installation command.** This template is
an agent-led setup guide for a customer-owned [Hermes Agent](https://hermes-agent.nousresearch.com/docs)
system. The agent may use Claude, OpenAI or another suitable supported model. It
inspects the actual machine, adapts to existing state, executes approved work,
debugs failures and proves the finished setup. No fixed specialist roster or
replacement main assistant is required.

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
```

A URL does not automatically load instructions. The agent must actually read them.
A browser-only chat can guide you, but must disclose that it cannot execute host
setup. Model choice does not automatically provide host tools or make every
third-party service support the same authentication method.

## What the finished setup includes

The [required baseline](skills/customer-onboarding/references/baseline.md) covers
the whole operating workflow: preserved identity and model access; an explicit
responsibility map; file placement and project onboarding; persistent memory and
a script-only watchdog; semantic, exact and history discovery; a source-backed
curated wiki; viewer/device decisions; private Slack/Desktop/Tailscale access;
Herdr and its Web UI for selected development work; capability allocation;
maintenance ownership; and verified data restoration and graphical recovery.

The main agent may handle everything or propose specialists that fit the owner.
There is no compulsory CTO, Engineer, Ops or four-agent customer organization.
The roster must still be discussed: preserving the main assistant is not a decision
to decline every specialist. Every functional area needs an implementation and
evidence; products, role names, devices and schedules adapt to the owner. A missing
decision stays undecided, not silently optional or complete.
Ordinary work stays in its requesting conversation. Skills, plugins, MCP servers
and extra tools are assigned according to need and owner-approved access, not
enabled everywhere. Only the memory watchdog is a baseline recurring job.

For repeatable per-project setup, use the bundled
[project-onboarding skill](skills/project-onboarding/SKILL.md). It retrieves the
project name/location/goal, preserves the existing primary assistant as EA,
prepares only approved missing role profiles through native operations, and creates
or reuses the selected four-pane Herdr layout. Its stdlib helper creates shells,
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
needed; there is no requirement to add another database or duplicate every file.
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
on a customer's host. The main agent selects and allocates capabilities by need.

A bounded guide/resumption trial preserved synthetic identity, instructions,
project state and an unsent draft. It found and fixed a guide-version recording
gap. This was a Linux/WSL discovery exercise, not native Mac or service acceptance;
all full customer baseline checks remain untested by that exercise.

Use the [short maintenance/recovery procedures](skills/customer-onboarding/references/maintenance.md)
and optional [private progress template](skills/customer-onboarding/templates/progress.md).
No second-brain migration, new knowledge service or extra scheduled routine is
introduced by this package.

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
