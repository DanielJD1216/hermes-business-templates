# Short maintenance and recovery procedures

These are agent procedures, not a scheduled service. Use current native help and
the recorded installation method. Preserve existing main-agent access, ownership,
identity, history and customer edits. Never run the legacy Creator updater to
maintain this baseline. Record the affected component, evidence, backup and next
actor in the private progress record. Do not ask again for authority already granted.

## Before any consequential change

1. Read the private component map and actual current state. Identify the exact
   host, profile, service, version and owner. Work on one component at a time.
2. Confirm an independent recovery connection and a tested way to return to the
   current build. A second tab on the same failing service is not independent.
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

## Maintain lifecycle eligibility

Follow the [small-collection renewal and actual-route checks](knowledge-lifecycle.md#small-collection-first-then-reviewed-renewal).
Source or policy changes require source review, version-bound renewal and a
positive/withheld retrieval check. Do not automatically reseal changed hashes,
silently reactivate retired records or restore recall by disabling enforcement.
After a provider, adapter or search-package update, verify the approved bindings
and actual fresh-session route before retaining an enforcement claim. Record
errors separately from valid empty retrieval and preserve unexplained failures.

## Restore or recover an outage

- Identify whether the failure is transport, host/service, authentication, quota,
  dependency or data integrity. Read the exact bounded error; do not dump secrets.
- Use the independent recovery route. Preserve newer data before any restore.
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
