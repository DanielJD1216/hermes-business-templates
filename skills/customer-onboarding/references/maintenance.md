# Short maintenance and recovery procedures

These are agent procedures, not a scheduled service. Use current native help and
the recorded installation method. Preserve existing main-agent access, ownership,
identity, history and customer edits. Never run the legacy Creator updater to
maintain this baseline. Record the affected component, evidence, backup and next
actor in the private progress record. Do not ask again for authority already granted.

## Assign operational ownership

Record the responsible agent/operator, trigger, scope, expected useful result and
failure recipient for discovery refresh, wiki review, memory/skill draft review,
tool updates and backups. Reuse existing mechanisms; a responsibility does not
require an extra non-development agent. The memory watchdog and LEANN index refresh
are required recurring jobs. Approve their scope, cadence/timezone, delivery and
costs; other schedules remain opt-in. Verify outcomes, not merely scheduler success.
Track pending drafts and failed checks without applying or deleting data to make
the status green. Do not promise automatic memory pruning from skill-curator
settings; retention, archive and deletion have different scopes and authority.

For memory, apply the required [reliability and watchdog checks](memory-reliability.md).
Monitor failed/stalled saves, unknown submission outcomes and version/patch drift
as well as health/search. Preserve the distinction between an available service
and unresolved save failures. Verify the scheduled job's actual profile/environment
and authorized alert delivery; a manual shell check alone is not enough.

The recovery set must cover the selected profiles/configuration and approved
skills, session/history state, project/task records, canonical work/wiki files and
native memory stores. Record exclusions and a protected credential-recovery or
reauthentication plan without reading secrets. Choose a destination independent
of the failure being recovered from. A skills snapshot or synchronized replica
alone is not whole-system recovery. Test restoration without replacing live data.

Discover suitable storage the owner already has: an encrypted external drive,
another computer, a NAS or approved cloud storage. A NAS purchase is not required;
RAID or synchronization alone does not establish a recoverable backup. Protect
sensitive archives before off-host transfer and keep recovery-key custody separate
from the archive. Git repositories suit code and sanitized instructions, not the
default destination for large history databases or full recovery archives.

## Required LEANN refresh schedule

Use current LEANN/native scheduler documentation and the actual installed help.
Reuse a suitable existing index and recurring job. Otherwise propose a bounded
local refresh script and the host's native scheduler (for example launchd on Mac
or a user systemd timer on Linux). No chat model or new orchestration service is
needed. Record roots, exclusions, embedding model/runtime, resources/cost, cadence,
timezone, overlap prevention, startup behavior, last success and failure recipient.
Preserve the last usable index on a failed refresh; do not publish a partial build.

Read the job back, run an authorized bounded refresh and retrieve the changed source
through LEANN. Verify rename/removal and exclusion behavior with approved fixtures.
Check failure reporting safely without breaking the live index or sending an
unapproved message. A failing precheck must leave an explicit stale/failed state,
not a successful schedule result. An unrelated cache-folder warning must not be
silently mistaken for completed index maintenance. Missing support/authority is a
required-row blocker, not grounds to substitute manual-only refresh.

## Before any consequential change

1. Read the private component map and actual current state. Identify the exact
   host, profile, service, version and owner. Work on one component at a time.
2. Confirm a change-appropriate access and rollback path to the current build.
   If the change could sever the only connection, arrange an independent route or
   attended local recovery first. Required Parsec debugging access may help with
   diagnosis, but does not by itself prove independent recovery or data restoration.
3. Preserve affected configuration and content in durable owner-private storage.
   Record versions, permissions and hashes; prove the backup is readable. Use a
   supported consistent database backup, or coordinate quiescing all writers.
   Copying a running SQLite file without its transaction state is not a backup.
   OpenViking can span multiple stores; follow its actual installed backup method.
4. Keep secrets out of the evidence and repository. Use supported protected secret
   backup only with owner authority; do not inspect or print credential contents.
   Reauthentication may be safer than moving tokens between hosts or profiles.
5. Coordinate disruption with affected sessions and preserve unsent drafts. A live
   production change, destructive restore or change to the only access route needs
   the applicable owner approval. Unknown ownership or conflicting edits means stop
   that operation, not overwrite. Continue independent safe work.

## Safe update

- Inspect upstream release notes and the supported update route for the installed
  component. Pin the chosen release/revision; review dependency and data migrations.
  Do not install a random latest version merely because the updater offers it.
- Review local modifications and update-created stashes before applying anything.
  Preserve patches and rollback artifacts; never blindly apply a stash or discard
  customer edits. Check license, account and platform compatibility first.
- Stage and test the changed component where practical. Keep main Hermes, memory
  service, embeddings, skills and web UI as separate update decisions. Changing an
  embedding model requires a separately rebuilt and tested index, not same-dimension
  reuse. Do not mix an old index with a new embedding model.
- Use the native update mechanism. Update stored evidence only after read-back.
  Check startup/version, effective settings and affected baseline acceptance rows:
  provider access, memory write/recall, mention-only Slack, file lookup and remote
  access as relevant. Reuse valid recent proof; new sends/model calls need scope.
- A stale process may still run old code after files change. Use a coordinated fresh
  process/resume when required; do not rewrite working source to fix mixed imports.
  If checks fail, retain diagnostics and return to the known build only after checking
  data compatibility. A code downgrade cannot reverse an incompatible data migration.
- Revalidate affected [memory reliability evidence](memory-reliability.md#updates-and-resumed-onboarding)
  after service, adapter, model or patch changes. Preserve historical failures and
  never refresh expected hashes blindly. Fence writers and client auto-start paths;
  idle queues do not prevent new submissions. If maintenance stops the coordinating
  chat service, establish an independent attended route first. After incompatible
  writes, preserve new data and use the documented repair-forward path.

## Maintain lifecycle eligibility

Follow the [small-collection renewal and actual-route checks](knowledge-lifecycle.md#small-collection-first-then-reviewed-renewal).
For baseline curation, review changed originals and dependent pages, preserve
history, update citations/provenance and recheck the actual answer route. Index
refresh alone does not establish current authority.
For a selected mechanical enforcement extension, source or policy changes require
version-bound renewal and a positive/withheld retrieval check. Do not automatically
reseal changed hashes, silently reactivate retired records or restore recall by
disabling enforcement.
After a provider, adapter or search-package update, verify the approved bindings
and actual fresh-session route before retaining an enforcement claim. Record
errors separately from valid empty retrieval and preserve unexplained failures.

## Restore or recover an outage

- Identify whether the failure is transport, host/service, authentication, quota,
  dependency or data integrity. Read the exact bounded error; do not dump secrets.
- Use the approved change-specific recovery route. Preserve newer data before any restore.
  Restore the matching version/config/data set into a separate private location
  first. Verify hashes, ownership, supported loading and scoped recall/search there.
- Coordinate production cutover and writer quiescence. Preserve the failed state and
  rollback target. Do not clear queues, lock files, jobs, tombstones or install records
  to force startup. Reconcile unknown write outcomes before any replay; do not infer
  a never-submitted message from an empty-looking directory.
- If memory is unavailable, report degraded operation. Do not silently switch memory
  or model providers, forget pending writes, or claim saved context is extracted
  memory. Any temporary fallback needs explicit scope and a recovery plan.
- Verify the actual client reconnects and the affected baseline rows pass. Restarting
  a process or obtaining HTTP 200 alone is not recovery. Resume only owned work that
  was paused, and record anything still unavailable.

## Expired or revoked authentication

- Confirm the exact account/profile and distinguish expiry from quota, missing
  scope, revoked access or a network outage. Preserve the working identity elsewhere.
- Use the installed native secure reconnect/login flow. The owner completes consent
  and enters secrets locally. Never ask for a token in chat, copy a peer profile's
  login, or silently substitute an API key/provider/subscription.
- Read back account identity and granted scope without tokens. Perform an authorized
  minimal operation, then verify the exact affected agent surface. If the account
  remains blocked, record the provider error and owner action without a retry loop.

## Move to another host

- Inventory current ownership, pinned sources, paths, approved data and external
  device/app bindings. Check destination OS/architecture and service support.
- Build the approved target privately; restore approved data using supported native
  paths and permissions. Treat logical profile/account names as routing, not isolation.
  Keep credentials on authorized hosts and use owner-attended sign-in where needed.
- Test preservation, memory scope, search freshness and actual client/recovery access.
  Coordinate the single active owner for gateways, schedules and writers before
  switching routes. Do not run duplicate bots/jobs or two independent memory writers.
- Keep the old host and rollback evidence until target acceptance. Retiring the old
  host is a separate approval; do not delete it on the strength of a file copy.

## Retire a component or agent

- Identify exact owned files, services, schedules, accounts, webhooks, devices and
  dependants. Separate shared resources and customer data from disposable software.
- Present the concrete stop/revoke/archive/delete scope. Require explicit approval
  for deletion and access revocation; retain required records and recovery archives.
- Stop only the approved owned activity, then verify it is inactive. Revoke obsolete
  provider/app/device access through the native owner interface and verify status.
  Removing a local directory does not revoke a remote token or stop a remote job.
- Verify remaining assistants and access still work. Mark the component retired,
  identify retained data and its owner, and record any revocation not yet confirmed.
