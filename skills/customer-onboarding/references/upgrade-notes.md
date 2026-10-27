# Upgrade notes

A skill update changes this guide, not the owner's setup. After
`hermes skills update customer-onboarding`, use these notes to bring the setup up
to the new version:

1. Find the version the setup was last reconciled with. Read `Template revision`
   in the private progress record, then the `version:` line of
   `skills/customer-onboarding/SKILL.md` at that commit, for example from
   `https://raw.githubusercontent.com/DanielJD1216/hermes-business-templates/<commit>/skills/customer-onboarding/SKILL.md`.
   If the record or that commit is unavailable, treat every entry as unchecked.
2. Work through each newer entry, oldest first. Check whether the setup already does
   what **Apply** says. Propose only the missing changes, get the applicable
   approvals, then apply and verify them.
3. Run the progress checker. If it reports a changed baseline fingerprint, reconcile
   the record with the new baseline before you update `Baseline SHA256`.
4. Record the new `Template revision` and each entry you applied or skipped, with
   the reason.

An entry with **Apply:** nothing and **Re-check:** none needs no owner action.

## 0.26.0

- **Changed:** a plain-language [setup map](how-it-works.md) with the parts, the
  work flow after setup and setup milestones; owner steps name the device, the app
  and what the owner should see next; T3 steps for an owner who works from another
  computer (pairing links work once and expire after 5 minutes by default; connect
  the built-in agent for the host's environment); Hermes Desktop connects early on
  the daily computer; an approved clone for a project that exists only in a remote
  repository; retiring an orchestration tool that T3 replaces; restarting the
  Desktop backend after a Hermes update; an export the owner offers can be a draft
  source for USER.md.
- **Apply:** nothing required. If an orchestration tool that T3 replaced still runs
  and its work has finished, propose retiring it. If Hermes Desktop shows "This
  backend is running old code after an update", restart the host's Hermes services
  while no T3 turn is running.
- **Re-check:** none. The baseline fingerprint stays `d523e008`.

## 0.25.0

- **Changed:** role templates for each SOUL (EA, CTO, Engineer and an optional
  department lead) and a workspace AGENTS.md template; a stock or empty SOUL now
  counts as no identity; a [Slack setup and channel layout](slack-setup.md) guide;
  with more than one model subscription, each role gets an owner-approved model.
- **Apply:** if the EA's SOUL is Hermes's stock text or empty, run the identity
  interview and draft it from the EA template, with approval and a backup.
  Compare existing role SOULs with the templates and propose only missing parts.
  If Slack has no channel layout yet, propose one. If the owner has more than one
  model subscription, propose one model per role.
- **Re-check:** yes. The baseline fingerprint changes from `b40cb8a8` to
  `d523e008`: reconcile the "Main assistant" and "Hermes and model access" rows.

## 0.24.0

- **Changed:** the legacy Creator installer is removed from this repository and
  archived at tag `legacy-creator-installer`. These upgrade notes are new, and the
  README installs this guide as a skill.
- **Apply:** nothing. Leave an existing legacy installation as it is; do not
  reinstall it.
- **Re-check:** none. The baseline is unchanged.

## 0.23.3

- **Changed:** section 9 of the [T3 setup prompt](t3-setup-prompt.md) has follow-up
  routing rules for the coordinator: PARALLEL, QUEUE, STEER and TRACK.
- **Apply:** if the setup has a T3 coordinator, add the rules to its instructions.
- **Re-check:** none.

## 0.23.2

- **Changed:** the [Hermes update safety skill](../../hermes-update-safety/SKILL.md)
  ships in this repository.
- **Apply:** for a git-installed Hermes, install it with
  `hermes skills install skills-sh/DanielJD1216/hermes-business-templates/skills/hermes-update-safety`
  and run its check before every Hermes update.
- **Re-check:** none.

## 0.23.1

- **Changed:** a [backup method](maintenance.md#back-up-history-memory-and-work-data)
  for chat history, memory and work data, encrypted and off the machine, and a
  documented Hermes v0.22.5 skill-loading defect.
- **Apply:** if the baseline's tested restore is not met yet, propose the backup
  method. If 2 or more `skills.external_dirs` entries each point at one skill's own
  folder and the log shows "Skill name collision for '.'", move to a layout from
  the [T3 setup prompt](t3-setup-prompt.md).
- **Re-check:** none.

## 0.23.0

- **Changed:** the [T3 setup prompt](t3-setup-prompt.md) matches gateway-backed
  Hermes ACP from Hermes v0.22.5: type `/<skill-name>` in full, set reasoning per
  conversation with `/reasoning <level>`, `@Name` is plain text, and a gateway
  restart interrupts running T3 turns.
- **Apply:** if T3 is set up, compare its per-role reasoning setup with the prompt.
  Restart the gateway only when T3 work is idle.
- **Re-check:** none.

## 0.22.0

- **Changed:** T3 Code replaces Herdr for the development team. project-onboarding
  is retired; its role setup moved to [role setup](role-setup.md).
- **Apply:** plan T3 with the [T3 setup prompt](t3-setup-prompt.md); Herdr keeps
  working until T3 passes its check. If project-onboarding is installed, remove it
  with `hermes skills uninstall project-onboarding --yes`.
- **Re-check:** yes. The baseline fingerprint changes from `763f9fb9` to
  `b40cb8a8`: reconcile the T3 row and the renamed decision row.

## Before 0.22.0

Reconcile the whole record against the current baseline with the progress checker.
