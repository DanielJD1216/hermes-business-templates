# Creator scope decisions

Status: local unreleased candidate. Reduced lifecycle tested on a disposable Ubuntu x86_64 server. No production installation or public release.

## Approved product

- Ordinary work stays in the requesting conversation. Herdr is for explicitly selected project-session orchestration, not a required destination for every task. One coordinator per project, one implementation owner per task and independent review when needed.
- No Creator-specific content playbooks. The 24 original procedures are removed, as are the Ops business-review playbooks. A generic project-onboarding skill is supplied separately with the canonical workspace documents.
- Only the optional OpenViking memory watchdog remains scheduled. It uses Python, not a chat model, and reports outage/recovery. Its search probe can use the memory service's embedding model. Verify the delivery route separately.
- Morning approvals, Nightly review, Memory-draft review, Comment pull, Member-question pull, Template update check and Drift check are retired. The manual `hbt check` command remains.
- A separate publisher-supplied tools/MCP reference sheet gives names, purpose, official setup links and account requirements. Customers choose and install only what they need. The finalized sheet/PDF is not yet supplied.
- Selected native Hermes skills are distinct from those external tools and the removed Creator playbooks. No private skills or credentials are copied.

## Implemented lifecycle

Customer setup now starts from the root README's private-agent message and the
repo-scoped `skills/customer-onboarding/SKILL.md`, not a terminal checklist. It
preserves the existing main identity/login, reconstructs only accessible context
with separate extraction/consolidation prompts, records private review/approval
receipts, and gates the existing hbt backend behind exact-output approval. Personal
and business can coexist in owner-private review, but adopted stores/audiences must
be separated. No runtime skill is auto-installed. The reusable development
`project-onboarding` skill remains separate. Checkpoint tests exercise structural
receipt/review gates, not model truthfulness or a complete customer conversation.
Even an empty existing install record blocks fresh installation; missing profiles
or tombstones are recovery signals, not authority to recreate deleted roles.

Fresh installation creates no Kanban board or dispatcher settings. Setup no longer offers a card demonstration or claims Herdr handoff acceptance. The shipped role instructions contain no card-based workflow. Only the watchdog script remains in the Ops distribution.

Legacy update preflights ownership and active claims before changes. It archives and pauses exact recorded retired jobs, reads their paused state back and retains history. Deleted jobs stay deleted. Retired managed skill roots are detached; pristine legacy local copies can be archived and removed, while modified or unknown sources are preserved and reported. Changes to shipped scripts or SOUL files stop replacement until reconciled.

Historical boards and dispatcher settings are preserved, including during uninstall. Retiring this template does not grant authority to disable other workflows or erase historical tasks. Minimal old memory-policy validation and lock/archive handling remain only for safe legacy preservation, not to run a reviewer.

The existing Ops profile remains the script host. It is included in the default team and legacy subset shortcut; a new explicit team JSON can omit it. Removing or relocating an installed host is not supported by the customization command. Without Ops or OpenViking, no watchdog job is created.

Fresh setup offers default versus customized teams before profile/manifest creation. Explicit team JSON supports subsets, display aliases separate from stable IDs, and new purpose-defined draft roles with zero tools or public web tools only. It never clones credentials. Existing-install correction is deliberately narrower: projects default and pre-Slack built-in display aliases, with provenance checks/backups and no moves/deletions. See README for limits and exact commands.

## Verification and remaining limits

The candidate now integrates the generic SOUL/AGENTS/USER/canon documents, blank project index and file-placement guidance. The existing main assistant is not replaced; its Executive Assistant identity template is optional. Explicit onboarding prepares a checked four-pane Herdr layout, while ordinary work stays in-thread. The helper never starts a model or sends a prompt. See [canonical integration](canonical-integration.md) for exact package paths, adoption rules, native layout evidence and remaining session-startup limits.

The full local suite passed after replacing tests for removed features with boardless lifecycle/migration checks. Disposable-server acceptance exercised legacy dry-run, upgrade/repeat-upgrade, status, uninstall, fresh install, update and uninstall. It checked owner-file preservation, custom-skill archival and unchanged historical board bytes. No provider login or Slack send was used.

This does not establish real provider authentication, Slack delivery, wall-clock alert delivery, a customer's OpenViking service, Herdr agent handoffs or editor-desk isolation. Separate native Herdr geometry/reuse checks and Hermes instruction-loading checks used isolated state without model calls. No live profiles, jobs or gateway settings were changed.

The previous diagram is obsolete. Replace it with the reduced product after this code checkpoint; do not present the old visual as the customer package.
