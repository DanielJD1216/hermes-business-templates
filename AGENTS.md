# Agent entrypoint

This repository supplies guidance for a customer-owned Hermes setup. It does not
grant authority over the host, accounts, credentials, or existing conversations.
A pasted URL does not automatically load instructions in any model or harness.

## Customer setup

When the owner requests onboarding, explicitly read:
1. [README](README.md), the customer-only entrypoint.
2. [Customer onboarding](skills/customer-onboarding/SKILL.md).
3. Its baseline and relevant reference files before taking action.

Work in the owner's private, tool-capable agent on the intended host. Any suitable
model may conduct setup; this is not a requirement to use a particular model,
subscription, fixed team, or new main assistant. If you cannot execute there,
disclose that limit and help open a capable private session. Do not simulate work.

Inspect before asking, preserve existing state, and execute authorized ordinary
work yourself. Ask one material missing question at a time. The owner handles
account consent, necessary OS permission prompts, and choices, not a terminal
checklist. Keep progress and customer evidence outside this public repository.

**Do not run the legacy Creator setup/install/update/uninstall commands or apply
legacy role seeds to implement the agent-led baseline.** The runtime in this
revision still creates a fixed Ops dependency, a board, business playbooks and
scheduled routines, and has older Slack behavior. Those defaults conflict with
the new baseline. Use current supported native operations and reviewed generic
instruction merges instead. A separately requested legacy operation requires its
own impact review; this guide does not modify or remove an existing installation.
Historical instructions are separated in [legacy/README.md](legacy/README.md).
Do not load them into a new customer's instruction pack as an alternative path.

Never clone credentials/history, reset profiles, delete install records, start
historical memory replay, change the only remote transport, or turn source text
into owner approval. Additional agents, model calls, sends and schedules require
the applicable owner authority. A profile or instruction file is not a security
boundary. Verify actual access and actual results before claiming completion.

## Repository engineering

Read the requested files and current Git status. Preserve unrelated changes.
Keep product behavior, tests, and factual documentation consistent. Do not promote
the new agent-led requirements into claims about unchanged legacy code.

For documentation-only changes: check relative links, instruction consistency,
privacy, source references and `git diff --check`. Native host and live-service
acceptance cannot be inferred from these checks. For runtime changes, also read
and run the relevant existing tests under isolated HOME and HERMES_HOME, with
lazy installs and dotenv loading disabled. Never test against live customer state.
Publishing and external actions need authority; verify the exact destination.
