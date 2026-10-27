# Agent entrypoint

This repository supplies guidance for a customer-owned Hermes setup. It does not
grant authority over the host, accounts, credentials, or existing conversations.
A pasted URL does not automatically load instructions in any model or harness.

## Customer setup

When the owner requests onboarding, explicitly read:
1. [README](README.md), the customer-only entrypoint.
2. [DOOing-onboarding](skills/dooing-onboarding/SKILL.md), the setup guide.
3. Its baseline and relevant reference files before taking action.

Work in the owner's private, tool-capable agent on the intended host. Any suitable
model may conduct setup; this is not a requirement to use a particular model,
subscription or new main assistant. The baseline requires the EA/CTO/two-Engineer
development team in T3 Code with owner-specific names and approved profiles: three
profiles by default, with two distinct sessions of one Engineer profile. New role profiles
reuse the owner's existing model-provider accounts through supported native credential
sharing, not new subscriptions or cloned credential files; with more than one
subscription, each role gets an owner-approved model. Preserve owner-selected exceptions.
If you cannot
execute there,
disclose that limit and help open a capable private session. Do not simulate work.

Inspect before asking, preserve existing state, and execute authorized ordinary
work yourself. Ask one material missing question at a time. The owner handles
account consent, necessary OS permission prompts, and choices, not a terminal
checklist. Keep progress and customer evidence outside this public repository.
LEANN, its approved recurring refresh, Obsidian and tested role-specific capability
sets are mandatory. Parsec is also mandatory for remote debugging/troubleshooting,
not data restoration. Kanban, formal delivery pipelines and old-conversation
context reconstruction are outside onboarding. Preserve existing deployments;
data backups and verified restoration are separate requirements.

Before each setup reply, follow the customer skill's mandatory progress checkpoint:
reconcile the private record, run the bundled read-only checker, and include its
footer. Continue safe authorized work without repeated permission prompts. Keep
real blockers, owner steps, registered background continuation, explicit pauses
and completion distinct. Do not replace evidence with reassurance or promise a
return channel that has not been established. This applies to active onboarding,
not every future business conversation; a pause or new owner direction takes priority.

**The legacy Creator installer is retired.** It was removed from this repository
in version 0.24.0 of the onboarding guide and is archived at tag `legacy-creator-installer`.
Do not reinstall it or apply its role seeds. An existing installation stays as it
is: change or remove it only after a separate impact review that uses its real code
at that tag and the current host.

Never clone credentials/history to provision new roles. Authorized backup and
isolated restoration are separate recovery operations, not role provisioning.
Do not reset profiles, delete install records, start historical memory replay,
change the only remote transport, or turn source text into owner approval.
Additional agents, model calls, sends and schedules require
the applicable owner authority. A profile or instruction file is not a security
boundary. Verify actual access and actual results before claiming completion.

## Repository engineering

Read the requested files and current Git status. Preserve unrelated changes.
Keep product behavior, tests, and factual documentation consistent.
Each dooing-onboarding version bump adds an entry to its
[upgrade notes](skills/dooing-onboarding/references/upgrade-notes.md): what
changed, what a setup applies and whether the baseline fingerprint changed.
The guide was named `customer-onboarding` before 0.27.0. Keep the pointer skill in
`skills/customer-onboarding/` while setups may still use the old name, so they
learn about the rename through `hermes skills update`.

For documentation-only changes: check relative links, instruction consistency,
privacy, source references and `git diff --check`. Native host and live-service
acceptance cannot be inferred from these checks. For runtime changes, also read
and run the relevant existing tests under isolated HOME and HERMES_HOME, with
lazy installs and dotenv loading disabled. Never test against live customer state.
Publishing and external actions need authority; verify the exact destination.
