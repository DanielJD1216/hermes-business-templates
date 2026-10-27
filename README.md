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
Help me set up or resume Hermes Business Templates. Install its guide as a skill with: hermes skills install skills-sh/DanielJD1216/hermes-business-templates/skills/dooing-onboarding
If you cannot run that command here, read README.md, AGENTS.md, skills/dooing-onboarding/SKILL.md and its linked references from https://github.com/DanielJD1216/hermes-business-templates at one repository revision.
First verify that you can act on my intended host and inspect the existing setup. Preserve my current assistant, model/login, history, files and working access.
Follow the agent-led baseline. Retrieve known facts before asking, propose the missing work and get the applicable approvals. Then execute and verify authorized work yourself; ask me only for missing decisions, account sign-in, OS permissions or actions your tools cannot perform.
Keep a private resumable progress record. Do not reset or reinstall working components, create unwanted roles, copy credentials or invent successful checks. Report exact blockers and whether the required baseline is actually complete.
Before each setup reply, reconcile that record against the selected guide and run its read-only progress checker. End the reply with its evidence-based fraction/percentage, current step, just-verified result, next action/actor and my exact action or none. Continue authorized work without asking me to say go on. Stop only for a real blocker, necessary owner action, a registered background continuation, my explicit pause or verified completion. Never promise an automatic return without a supported continuation route.
```

A URL does not automatically load instructions. The agent must actually read them.
A browser-only chat can guide you, but must disclose that it cannot execute host
setup. Model choice does not automatically provide host tools or make every
third-party service support the same authentication method.

## What the finished setup includes

The [required baseline](skills/dooing-onboarding/references/baseline.md) covers
the whole operating workflow: preserved identity and model access; an explicit
EA/CTO/Engineer responsibility map; file placement and project onboarding;
persistent memory and a script-only watchdog; LEANN with scheduled index refresh,
exact and history discovery; a source-backed curated wiki viewed in Obsidian;
private Slack/Desktop/Tailscale access; a T3 Code development team on a persistent
server; installed/tested role-specific capabilities; maintenance ownership;
Parsec for remote debugging/troubleshooting; and verified data backup/restoration.

New to these parts? [How your setup works](skills/dooing-onboarding/references/how-it-works.md)
explains each one in plain words, how work flows after setup and the setup milestones.

The required development team is EA, CTO, Engineer #1 and Engineer #2, used through
[T3 Code](https://github.com/pingdotgg/t3code) with each Hermes profile connected as
its own Local ACP provider. Reuse the owner's main assistant as EA and approved
permanent specialist profiles. The default is three profiles: EA, CTO and one
Engineer profile used by two distinct Engineer threads. Engineer #1 and #2 are
thread labels, not profile names. Verify shared-profile memory/write safety
before concurrent use; do not create another profile as an automatic workaround.
Names adapt; the required roles do not disappear. Extra non-development roles
are not mandatory.

Each role's SOUL starts from a role template that the owner adapts. A main
assistant whose SOUL is still Hermes's stock text gets an identity interview
first. USER.md stays personal to each owner.

All new role profiles reuse the owner's existing model-provider accounts through a
supported native sharing mechanism, with no new subscriptions or repeated sign-ins.
When the owner has more than one model subscription, each role gets an approved
model suited to its work: the strongest reasoning model for the CTO, a strong
general model for the EA and a faster, lower-cost coding model for the Engineer.
Verify effective access per profile; a matching model name is not authentication.
Preserve existing owner-selected exceptions. This default does not share Slack/bot
tokens, copy credential files or grant specialists the EA's private context.

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

LEANN refresh must share its exclusion rules with its precheck: excluded caches
must not stop approved sources from updating. Unknown roots stay excluded pending
approval, while genuine safety/build failures preserve the last working index and
raise attention. Require bounded search, helper-binding and failure/recovery checks
through the [existing maintenance path](skills/dooing-onboarding/references/maintenance.md#required-leann-refresh-schedule),
including when no rebuild is needed. These requirements do not install a runtime repair.

Memory acceptance must also prove growth/tail recall, distinct-source retrieval,
owner scope, source preservation and truthful failure handling. Follow the required
[memory reliability checks](skills/dooing-onboarding/references/memory-reliability.md):
reuse version-bound release evidence and run bounded checks on the actual host.
The watchdog must expose failed/stalled saves and version/patch drift, not just
healthy search. This guide ships no memory repair or acceptance runner and does
not certify a universally supported runtime combination. Missing compatible
artifacts or platform evidence block the memory requirement, not independent work;
Linux/WSL evidence does not establish native Mac support.

After the agent prepares the approved role profiles, you install T3 Code on the
agent host, sign in one of its built-in agents and paste the
[T3 setup prompt](skills/dooing-onboarding/references/t3-setup-prompt.md) into a
new T3 thread. That agent sets up the persistent server and private Tailscale access,
connects each Hermes profile, tests it and saves a setup record your main agent can
read. Your main agent then verifies the result from that record. A provider entry
in T3 is not proof that the team works. Phone access is a separate choice covered
by the same prompt. Herdr is no longer part of the baseline; an existing Herdr setup
keeps running until its active work moves to T3.

See [onboarding](skills/dooing-onboarding/SKILL.md),
[context and file guidance](skills/dooing-onboarding/references/context-and-files.md),
[sources and capability limits](skills/dooing-onboarding/references/sources-and-capabilities.md),
and [Mac troubleshooting evidence](skills/dooing-onboarding/references/mac-notes.md).
Before any Hermes update, use the [Hermes update safety skill](skills/hermes-update-safety/SKILL.md):
updates silently remove local source changes, and it ports them first.

Memory and knowledge are distinct: OpenViking memories retain interaction-derived
facts; a knowledge base holds approved reference sources such as manuals, policies
and project documentation. Canonical files plus scoped retrieval can already serve
that purpose. OpenViking resources can index selected reference material when
needed, but do not replace required LEANN. No additional database or whole-workspace
duplicate ingestion is required.
See the [knowledge/retrieval boundary](skills/dooing-onboarding/references/baseline.md#memory-knowledge-and-file-discovery).
Baseline acceptance demonstrates a small useful collection and a complete work
and retrieval cycle. Comprehensive memory-engine enforcement and customer-specific
business automation are separately scoped extensions, not hidden installation work.

## Profiles and behavior after initial setup

Follow the [profile lifecycle](skills/dooing-onboarding/references/maintenance.md#profile-lifecycle)
when approved profiles are added, changed or retired, and after relevant updates.
Discover the actual roster; preserve owner-specific roles and existing exceptions.
Reconcile each affected profile's instructions, capabilities, memory binding,
monitoring and recovery coverage without copying secrets or histories.

The [identity guidance](skills/dooing-onboarding/references/context-and-files.md#identity-and-behavior-across-profiles)
separates shared operating rules, role-specific SOUL and audience-scoped USER/context.
Preserve personality and owner choices; verify active loading in the intended
fresh session, not only files on disk. Missing required evidence stays incomplete.
This is an agent-led procedure, not an automatic new-profile detector or installer.
[Historical memory repair](skills/dooing-onboarding/references/maintenance.md#keep-historical-memory-repair-separate)
remains separate from independent template/onboarding work; required memory checks
and unresolved failure alerts are not waived.

## Current status and limits

This is a **published guide for an agent-led trial**, not a completed universal
installer or proof that every Mac/Linux configuration works. Actual host support,
provider access and each baseline outcome require evidence. Owner choices and
missing client access do not erase unfinished required checks.

The [capability reference sheet](capabilities/REFERENCE.md) and
[catalog](capabilities/catalog.json) contain 333 records: 197 included, 40 excluded
and 96 native candidates whose activation was not established. Included selections
cover 160 skills, 7 plugins, 13 MCP integrations and 17 native toolsets.

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

Use the [short maintenance/recovery procedures](skills/dooing-onboarding/references/maintenance.md)
and optional [private progress template](skills/dooing-onboarding/templates/progress.md).
The guide requires LEANN refresh and Obsidian acceptance, but does not itself install
services or schedules. Report verified rows / all required rows and the calculated
checklist percentage, not estimated effort. Reconcile older progress against this
revision without erasing historical evidence.

Every setup reply requires the onboarding skill's progress checkpoint. Its
[read-only checker](skills/dooing-onboarding/scripts/check_progress.py) calculates
coverage and supplies the footer; owner-confirmed evidence remains labelled.
It checks record consistency, not whether receipts are genuine or host tests passed.
This guide installs no response hook, extra checker bot or notification service.
The agent must invoke the checker and use the result; text instructions alone do
not mechanically enforce every model reply or guarantee a later notification.

Repository checks use only Python's standard library and do not start Hermes:
`python3 scripts/check_customer_guide.py` and
`python3 scripts/check_capabilities.py --self-test`.

## Updates

Ask your agent to run `hermes skills update dooing-onboarding`. The guide's
[upgrade notes](skills/dooing-onboarding/references/upgrade-notes.md) tell it
what changed and what to apply to your setup, so you do not need a separate note.

Before version 0.27.0 the guide was installed as `customer-onboarding`. On such a
setup, run `hermes skills update customer-onboarding` once: it installs a short
pointer that tells your agent how to switch to `dooing-onboarding`.

## Retired legacy installer

The old Creator installer was removed in version 0.24.0 of the onboarding guide. It is archived
at tag [legacy-creator-installer](https://github.com/DanielJD1216/hermes-business-templates/tree/legacy-creator-installer)
and is not an onboarding path. Removing it from the repository does not change an
existing installation.

## License

MIT for this repository's authored guidance. See [LICENSE](LICENSE). Referenced
packages retain their own terms.
