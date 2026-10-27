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

### Back up configuration and instructions

This method covers the configuration and instruction part of the recovery set.
Session history, project records and memory stores use the
[data method](#back-up-history-memory-and-work-data) below.

1. For each approved profile, select instruction and built-in memory files,
   configuration, profile metadata, schedule definitions, scripts, plugins and skills.
   Exclude `.env` and other credential files, databases with their sidecar files,
   sessions, logs, caches, virtual environments and files over a size limit.
   Record symlinks instead of following them.
2. Commit the selection on the approved cadence to a private repository or other
   approved destination that the owner controls. Read back private visibility
   before the first push. Scan every outgoing commit with a pinned secret scanner.
   Also refuse any configuration value under a secret-like key that is not a
   `${VAR}` reference: scanners miss some formats, such as a plain bearer token.
3. Hold every file that a scan or the size limit stops; do not drop it silently.
   Record held paths and reasons only. The owner chooses: move the secret out (see
   [credential references](sources-and-capabilities.md#keep-credentials-out-of-configuration)),
   keep the hold, or approve an exact exception.
4. After each push, confirm that the remote branch head equals the recorded
   commit. Script exit status and scheduler success are not proof.
5. Test restoration: clone into a separate private location and compare bytes with
   the live selection. Report matched, changed, missing and extra counts. Explain
   each difference, for example schedule state that changed after the snapshot.
6. Name a reinstall source for each excluded skill, plugin and held file: bundled
   with Hermes, an official optional skill or a pinned upstream source. Back up
   an item that has no reinstall source, or record it as a recovery gap.

### Back up history, memory and work data

This method covers session history, project and task records, memory stores, T3
Code state and canonical work/wiki files. It was tested with restic and rclone;
any tool that encrypts before upload, deduplicates and verifies restores can
replace them. Test the owner's own destination before relying on it.

1. Copy every SQLite store consistently before the file backup: each profile's
   session database, task boards, memory-service stores and T3 Code state. Use
   SQLite's online backup API into a private staging folder, one store at a time,
   while writers continue. Give each copy a deadline: Python's `sqlite3` backup
   retries a locked source without limit. Leave out lock-only files; an inspected
   T3 Code v0.1.2 install holds `server-owner.sqlite` locked while it runs.
2. Back up the staging folder and the plain-file stores (session folders, memory
   service data, T3 data, canonical work files) to an encrypted repository. Leave
   out the live database files and their sidecars. Exclude credential files by
   name across the whole selection, not only at profile roots: test folders and
   exports hold copies of `.env` files, OAuth client secrets, private keys and
   `rclone.conf`. Exclude `.git` folders by name: restic's
   `--exclude-if-present .git` keeps the `.git` folder itself. Record each
   exclusion, such as large media projects, with the owner's decision.
3. Rehearse against a local repository first. List the snapshot and search it
   for credential names, `.git` paths and excluded folders. Only then point the
   job at the approved destination.
4. Keep the repository password and the restore steps in the owner's password
   manager or another place off the host. Without the password the backup cannot
   be read. Never print it.
5. Schedule the job at low CPU and disk priority. Set retention, for example 7
   daily, 4 weekly and 12 monthly snapshots. Prune on a fixed day and read back a
   sample of the stored data, for example `restic check --read-data-subset 5%`.
6. Test restoration from the destination, not from the staging folder, into a
   separate private location. Run `PRAGMA quick_check` on each restored database
   and compare file hashes with the live files. Explain each difference, for
   example files that changed after the snapshot. To check a database copy on
   read-only media, such as a mounted snapshot or image, open it as
   `file:<copy>?immutable=1`. SQLite then skips locking and change detection, so
   never open a live database this way.
7. Alert the approved recipient when a run fails or when no run has succeeded
   within the expected interval, for example 30 hours for a nightly job.

Destination notes:

- **NAS on the owner's network**, for example a UGREEN DXP4800 Pro running UGOS
  Pro. Create a backup shared folder and a NAS user who is not an administrator
  and can reach only that folder. Connect through rclone's
  [SMB backend](https://rclone.org/smb/), so the agent host needs no mount or
  root access. UGREEN's guide describes SSH, and the SFTP option in its settings,
  for [administrator accounts](https://support.ugnas.com/detail/article/en-US/481);
  do not give the backup job an administrator login to use SFTP. On a Btrfs
  volume, add a [snapshot plan](https://support.ugnas.com/detail/article/en-US/654)
  with a retention policy for that folder, timed after the backup window. Only
  NAS administrators manage snapshots, so a host that holds only the backup
  user's login cannot delete them. Snapshots need a Btrfs volume, and changing a
  volume's file system means formatting it. A
  [restic REST server](https://github.com/restic/rest-server) container in
  `--append-only` mode is a stronger alternative, but pruning then needs
  separate access. A NAS at the same site does not survive fire, theft or flood
  with the host: also copy snapshots off site, for example with `restic copy` to
  a cloud repository, or record that gap with the owner's decision. The
  publisher has not yet tested this NAS route end to end.
- **Cloud drive through rclone**, for example Google Drive. Use the owner's own
  OAuth desktop client, because rclone's shared client
  [will stop working during 2026](https://rclone.org/drive/#making-your-own-client-id).
  Enable the Drive API in that client's project and publish the app: logins for
  an External app left in Testing expire after 7 days. The `drive.file` scope
  reaches only files that the same app created, so choose the client before the
  first upload.
- **Encrypted external drive**: it works only while connected, so the failure
  alert must cover a missing drive. It protects against site loss only when a
  second drive rotates off site.

## Required LEANN refresh schedule

Use current LEANN/native scheduler documentation and the actual installed help.
Reuse a suitable existing index and recurring job. Otherwise propose a bounded
local refresh script and the host's native scheduler (for example launchd on Mac
or a user systemd timer on Linux). No chat model or new orchestration service is
needed. Record roots, exclusions, embedding model/runtime, resources/cost, cadence,
timezone, overlap prevention, startup behavior, last success and failure recipient.
Preserve the last usable index on a failed refresh; do not publish a partial build.

Use one exclusion policy in precheck and discovery. Already-excluded caches must
not block updates to approved sources. Keep unfamiliar top-level directories and
loose files out of ingestion until explicitly approved; report a scoped warning
without stopping the approved refresh. Do not inspect their contents merely to
make the warning disappear. Historical folder inventories and a baseline snapshot
are not ingestion approval. For an existing index, reconcile its verified source
manifest with owner-approved scope; for a new index, obtain that scope first.
Never automatically accept the current filesystem as a new baseline.

New eligible documents within an approved directory may follow its existing
filters and bounded expansion policy; that does not authorize new top-level roots.
Apply the same boundary to manual builds, scheduled refreshes and validation.
Unsafe paths, invalid scope/configuration, unreadable eligible sources and genuine
integrity errors remain blocking. Do not turn every failed precheck into a warning.
Preserve the prior index and manifest on failed build or validation. Validate the
candidate before promotion, verify caught publication failures restore usable
state, and document any interruption window requiring manual recovery.

Read the job back, run an authorized bounded refresh and retrieve a known source
through the actual agent surface. Verify edits, rename/removal and exclusions with
approved isolated fixtures, never test data mixed into production. Also prove an
unchanged refresh performs a bounded search rather than returning success solely
because source hashes match. Verify the selected local model/runtime and effective
helper bindings before/after native work. Same-host helpers should use loopback;
no current listener proves inactivity, not safe configuration. Revalidate reviewed
compatibility changes after upgrades; do not copy private package patches or
silently accept changed hashes. Native Mac evidence is separate from Linux/WSL.

Record freshness time, search/binding results, warnings and failures separately.
An existing script-only watcher should check the actual service/timer outcome and
missing, stale or invalid evidence, including precheck failures that never reached
the builder. Reuse the existing approved delivery route. Confirm attention and
recovery messages at that destination, even when unrelated issues remain open.
Retain known delivery failures across silent checks; script success is not receipt
proof, and ambiguous sends do not authorize blind retries. Test failures safely
without breaking the live index or sending an unapproved message. Label fixture,
manual-service and observed automatic-run evidence distinctly. No new monitoring
platform or chat model is required. Missing support/authority remains a required-row
blocker, not grounds to substitute manual-only refresh or claim readiness from this guide.

On resume, reconcile only affected LEANN rows and dependent proof against these
requirements. Preserve valid identity, login, team and other baseline evidence;
do not reset onboarding or repeat unrelated tests.

## Profile lifecycle

At setup, resume, an approved profile addition/change/retirement, or a relevant
service/plugin/provider update, inspect current native profile metadata and reconcile
it with the existing private roster. Discover IDs and effective homes instead of
copying a publisher's fixed profile list. A discovered profile is not permission to
configure it, ingest its files, activate tools or add it to external reporting.
Preserve unknown profiles and deletion markers; name missing ownership or authority.

For each affected approved profile:

1. Map its ID, role, owner, effective home, active sessions and intended data/tool/
   channel access. Reuse profiles; a second session is not another profile. Keep
   the required EA/CTO/two-Engineer team and its shared-profile concurrency gate.
   Extra roles need owner selection, not automatic creation.
2. Apply the [identity and behavior procedure](context-and-files.md#identity-and-behavior-across-profiles):
   shared operating rules, role-specific SOUL and audience-scoped USER/context.
   Preserve approved overrides and use narrow reviewed changes, not blanket copying.
3. Use supported native configuration and role preparation. Default model access
   to the EA's approved account through supported native sharing, preserving owner
   exceptions. Verify effective authentication per profile without copying secrets.
   Review the full capability catalog and verify the required role-specific set;
   check local copies/overrides that may shadow a shared skill or plugin revision.
4. Verify the intended memory provider, endpoint and account/user/agent binding,
   effective precedence and fresh-session route without printing secrets. A linked
   plugin, healthy endpoint or different namespace does not prove correct loading,
   successful save/recall or authenticated isolation. Follow the existing memory
   acceptance procedure and its consent limits; do not inherit another profile's
   readiness or pending writes. Reuse applicable evidence without replaying history.
5. Reconcile applicable memory-watchdog coverage, backup/restore roots, maintenance
   writer inventory, and approved discovery/index scopes. Reuse existing monitors
   and jobs. Include cached clients, finalizers and startup paths, not just the new
   profile directory. An inventory entry does not enforce exclusion. Broader data
   access, alert destinations, schedules or costs require their applicable approval;
   leave coverage gaps visible rather than silently expanding a job or duplicating it.
6. Record creation, configuration, active loading and verification separately in the
   existing private record, with source revisions and exact profile/session evidence.
   Reopen affected baseline rows and dependencies only. Keep one baseline denominator;
   a per-profile evidence table supports those rows, not a second completion score.
   Required coverage is complete only when all applicable approved profiles have
   proof. Preserve earlier valid evidence and explain why any row became incomplete.

For rename, retirement or update, trace dependencies and cached bindings by native
ID, not display name. Follow the supported native route; do not rename directories,
merge histories or remove unknown state to match the roster. Use the retirement
procedure below for stop/revoke/archive/delete decisions. Revalidate only affected
instruction, identity, capability, memory and monitoring evidence; preserve unrelated
working sessions and approved exceptions.

This is a repeatable agent procedure, not an installed profile-creation hook or
background detector. Assign the reconciliation owner and trigger in the existing
maintenance record. Claim automatic discovery/configuration only if a supported
mechanism is actually installed and verified within approved scope. Do not add a
watcher, agent or service merely to make the template appear future-proof.

## Keep historical memory repair separate

A failed historical save is an incident with its own exact task/owner evidence and
recovery authority, not a prerequisite for every template edit or independent
onboarding step. Keep it open and visible while continuing unrelated authorized
work. Do not downgrade required memory/watchdog checks, suppress old alerts or
mark full acceptance complete because a fresh save succeeds.

Do not ship private recovery helpers, synthetic acceptance or offline authentication
designs as supported installed repairs. Live recovery requires the actual compatible
artifact, identity, writer controls and backup/restore evidence. Stopping named bots
or observing idle queues does not prove all writers excluded; native startup can
resume internal work before an HTTP check. Even a status GET needs a source-backed
no-mutation assessment rather than an assumption based on its HTTP method. Missing
controls remain explicit blockers for the affected operation, not permission to
build a private memory fork during onboarding. Use [memory reliability](memory-reliability.md)
for the distinction between release evidence, first save/recall and full acceptance.

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

- Before any update of a git-installed Hermes, follow the
  [Hermes update safety skill](../../hermes-update-safety/SKILL.md) from the same
  repository revision. Every update path silently removes uncommitted local source
  changes from the running code; the skill checks for them read-only, ports them in
  a separate clone and verifies the result before and after the restart.
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
- After a Hermes update on the host, restart the Hermes gateway, and the Desktop
  backend (`hermes serve`) when Desktop connects remotely, so neither keeps the old
  code. Restart only while no T3 turn is running: a gateway restart interrupts
  running T3 Hermes turns. Then update Hermes Desktop on each client when it offers
  the update. The Desktop message "This backend is running old code after an
  update" means a Hermes process on the host still runs the old code.
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
- Stop only the approved owned activity, then verify it is inactive and stays
  inactive: disable automatic start and check that it does not restart. Revoke obsolete
  provider/app/device access through the native owner interface and verify status.
  Removing a local directory does not revoke a remote token or stop a remote job.
- Verify remaining assistants and access still work. Mark the component retired,
  identify retained data and its owner, and record any revocation not yet confirmed.
