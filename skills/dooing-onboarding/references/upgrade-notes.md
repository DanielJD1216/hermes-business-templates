# Upgrade notes

A skill update changes this guide, not the owner's setup. After
`hermes skills update dooing-onboarding`, use these notes to bring the setup up
to the new version:

1. Find the version the setup was last reconciled with. Read `Template revision`
   in the private progress record, then the `version:` line of
   `skills/dooing-onboarding/SKILL.md` at that commit, for example from
   `https://raw.githubusercontent.com/DanielJD1216/hermes-business-templates/<commit>/skills/dooing-onboarding/SKILL.md`.
   For a commit before 0.27.0, the path is `skills/customer-onboarding/SKILL.md`.
   If the record or that commit is unavailable, treat every entry as unchecked.
2. Work through each newer entry, oldest first. Check whether the setup already does
   what **Apply** says. Propose only the missing changes, get the applicable
   approvals, then apply and verify them.
3. Run the progress checker. If it reports a changed baseline fingerprint, reconcile
   the record with the new baseline before you update `Baseline SHA256`.
4. Record the new `Template revision` and each entry you applied or skipped, with
   the reason.

An entry with **Apply:** nothing and **Re-check:** none needs no owner action.

## 0.37.0

- **Changed:** the footer adds a `Why:` line under the next step: one plain sentence
  on what the step is for, so the owner can decide without asking. The private
  record has a new field, `Why the next step`, with the same plain-words rule. The
  checker rejects an unfinished record without it, and a complete record must set it
  to `none`.
- **Apply:** add `- Why the next step: <one plain sentence>` to the checkpoint
  section of the private record, after `Owner action needed`. Then run the checker.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.36.0

- **Changed:** the footer is written for the owner. The record fields it shows (the
  next action, the owner action when the owner acts next, and the blocker when setup
  is blocked) must be one short plain sentence of at most 25 words, with no
  commands, code or file paths. The checker rejects a record whose footer text
  breaks this. The footer names the agent as `me` and an outside party as
  `someone else`.
- **Apply:** rewrite those fields in the private record in plain words for the
  owner, even if the checker accepts them, and move technical detail to the
  affected baseline row's next action cell. Then run the checker.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.35.1

- **Changed:** the memory scope check in `memory-reliability.md` now starts with the
  service's authentication mode. An OpenViking server without a root key treats
  every caller as an administrator that names its own owner in request headers, so
  profile separation is only a naming convention. The check now includes one
  request that names another owner's account.
- **Apply:** check whether the OpenViking server has a root key. If it has none,
  record the OpenViking memory row's scope check as failed and propose per-owner
  keys (a root key and one user key per profile) for owner approval.
- **Re-check:** the OpenViking memory row's scope evidence. The baseline
  fingerprint stays `9fba33a8`.

## 0.35.0

- **Changed:** step 1 no longer calls `hermes auth list` read-only. On Hermes
  v0.22.5 it loads every provider's stored logins, which can merge a login shared
  across profiles and save the change. The guide now prefers the agent's own
  session as model-access evidence and runs `hermes auth list` at most once, when
  no other Hermes process is signing in.
- **Apply:** nothing.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.34.1

- **Changed:** the footer's `Blocked:` line now appears only when the checkpoint
  state is `blocked`, as the 0.34.0 note describes. In 0.34.0 it also appeared
  when the record's `Blocker` field named a remaining failure in another state.
- **Apply:** nothing.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.34.0

- **Changed:** the progress footer is shorter. It shows the progress percentage,
  rounded down, and the next action with who takes it: `you` for the owner, the
  agent, or a background job. A third line names the blocker only when setup is
  blocked. Row counts, owner-confirmed labels, the checkpoint state and the last
  verified result stay in the private record and in the checker's JSON output.
- **Apply:** nothing.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.33.0

- **Changed:** four clarifications from a second test on an empty host. Step 1
  says not to read or print credential files such as `auth.json` or `.env` during
  discovery; `hermes auth list` shows which logins exist. When the agent's own
  session is the model-access evidence, the record names the model and provider
  that session runs on, which can differ from the profile default. Step 1 links
  Tailscale's install instructions. The guide says that its version numbers the
  guide, not Hermes, and that its most recent checks used Hermes v0.22.5.
- **Apply:** if the "Hermes and model access" row names a model, confirm that it
  is the model the evidence session ran on, and correct the row if not.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.32.0

- **Changed:** five clarifications found in a test on an empty host. The guide now
  says when to use `owner-action` instead of `continue` or `blocked`, including on a
  host with no Hermes. Step 1 gives read-only commands to check Hermes and model
  access, and points to the official Hermes installer. The checkpoint section covers
  a skill with no recorded source commit and says to keep the private record
  owner-only.
- **Apply:** on an existing private progress record, set owner-only access
  (`chmod 600 "<private-progress.md>"` on Linux and macOS). Nothing else changes.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.31.0

- **Changed:** the capability catalog adds 7 cua entries: the Cua MCP server (`mcp-0334`), the `cua-spaces`
  plugin (`plugin-0335`) and the cua-driver, cua-sandboxes, cua-spaces, cua-volume and gui-automation skills
  (`skill-0336` to `skill-0340`). Cua gives agents isolated computers that the owner can watch.
- **Apply:** nothing. A role that needs isolated or watched computers can review those entries.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.30.0

- **Changed:** "Read first" in the guide now lists the files to read before the
  first reply separately from the files to read before the step that uses them.
  The source and capability notes add
  [a check that each chat can use its MCP servers](sources-and-capabilities.md#check-that-each-chat-can-use-its-mcp-servers).
  Step 1 adds signing in from the daily computer over SSH, and the Mac findings add
  Remote Login for a Mac host. The checkpoint section says where to find the full
  source commit for the progress record.
- **Apply:** in each profile, run that MCP check for every enabled server that its
  roles need. Nothing else changes.
- **Re-check:** none. The baseline fingerprint stays `9fba33a8`.

## 0.29.0

- **Changed:** the guide no longer checks a Parsec license or plan. The baseline
  Parsec row, step 3 of the guide, the source list and the progress template's
  Parsec decision drop the license wording.
- **Apply:** in the private progress record, rename one owner decision
  from `Parsec debugging host/client, support permissions and applicable license`
  to `Parsec debugging host/client and support permissions`. The progress checker
  reads the decision names from the template, so until then it reports that
  required owner decisions are missing.
- **Re-check:** the "Parsec remote debugging" row. It only lost a requirement, so
  its passing evidence stays valid. The baseline fingerprint changes from
  `d523e008` to `9fba33a8`.

## 0.28.0

- **Changed:** connecting Hermes Desktop on the owner's daily computer is now the
  first setup priority. It ends step 1, before the identity interview, so the owner
  follows every later step on their own computer. Parsec stays required, but only
  as the last resort: when Desktop or its backend is down, when an OS permission
  prompt or a browser sign-in appears only on the host, or when the host waits at
  its login screen after a restart. The Mac notes add what Parsec needs for that
  last case. The setup milestones are reordered: "Your daily computer connects" is
  milestone 1 and Parsec moves to milestone 7. The README's first message has one
  new line about Desktop.
- **Apply:** if the owner still follows setup steps on the host's own screen,
  connect Hermes Desktop on their daily computer now and continue from there.
  Otherwise nothing.
- **Re-check:** none. The baseline fingerprint stays `d523e008`.

## 0.27.1

- **Changed:** one sentence about conversation history in delegation briefs
  (section 9 of the T3 setup prompt) is reworded. Hermes's skill scanner read it
  as an exfiltration instruction, which blocked a fresh install from a community
  source. The rule itself is unchanged.
- **Apply:** nothing.
- **Re-check:** none. The baseline fingerprint stays `d523e008`.

## 0.27.0

- **Changed:** the guide is renamed from `customer-onboarding` to
  `dooing-onboarding`, so its skill command is `/dooing-onboarding`. Content,
  baseline and progress checker are unchanged. The old path now holds a short
  pointer skill for setups installed under the old name.
- **Apply:** install `skills-sh/DanielJD1216/hermes-business-templates/skills/dooing-onboarding`,
  check that `hermes skills list` shows it, then run
  `hermes skills uninstall customer-onboarding`. Run the progress checker from
  `skills/dooing-onboarding/scripts/check_progress.py` from now on.
- **Re-check:** none. The baseline fingerprint stays `d523e008`.

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
