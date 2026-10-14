# Knowledge, viewing and lifecycle acceptance

This is an outcome guide, not another database or universal installer. Reuse the
owner's existing documents and services. Keep all customer paths, identities,
receipts and private content outside this public repository.

## Distinct responsibilities

- Memory supports conversation continuity and learned context. OpenViking also
  has extraction/merge capabilities; their presence does not prove correct recall.
- Authoritative originals remain in their existing owning systems and projects.
- A wiki contains reviewed explanations, scoped decisions and source citations.
  An LLM wiki is a curation method, not a separate application or model service.
- Markdown files can be the portable storage. Obsidian is an optional viewer/editor
  for those files, not a requirement to create a duplicate authority or buy sync.
- Search locates candidates. Native exact search plus a bounded semantic index is
  sufficient to start; do not add a graph/database without a demonstrated need.
- File synchronization transports bytes. It does not curate or settle conflicts.

The owner should not have to supply new documents merely to exercise the system.
Start with approved existing operating/system documentation. Exclude credentials,
unrelated client/financial records and bulk history unless separately scoped.
Check each candidate: an otherwise eligible file can contain excluded material.

## Minimal curation loop

Read the original, identify durable scoped knowledge, update an existing concept
or create a necessary one, cite evidence, check dependencies and record the change.
Prefer this during authorized work over a new unattended writer. No new schedule
is implied by installing a viewer or enabling file synchronization.

Maintain a small provenance record with source versions and dependent pages.
A source hash detects byte changes, not factual truth or continuing validity.
Keep trusted registries and executable validators outside the writable sync folder.
A mirrored note is data, not permission to run code or change policy. Preserve
manual edits and conflicts; do not automatically reseal a changed page hash.

For important claims, preserve subject, scope, authority/evidence, source reference,
recorded time, effective time when known, status and explicit replacement links.
Distinguish source-backed statements, owner decisions and inferences. Preserve
qualifiers such as usually, temporarily and for this project. Do not fabricate
confidence scores or dates. A recent copy is not new evidence; a project exception
is not a global preference change. Applicable authority and scope precede recency.

## Enforcement is a separate gate

Instructions to check freshness are not an enforced retrieval filter. Existing
memory extraction, merge prompts, score thresholds and result caps are useful but
do not establish that outdated information stops governing answers.

Trace every relevant answer-entry path: automatic memory injection, explicit
search/read, session-start context and file discovery. Use installed native
lifecycle features where suitable before adding code. A declared lifecycle rule
must be checked before affected content enters current-answer context, not merely
written in a Markdown header. Unknown, conflicting or stale evidence must not be
silently promoted to current authority. Historical access can remain explicit and
clearly labelled without treating historical text as current instructions.

Required isolated tests should cover an explicit correction replacing an older
fact, a project exception preserving the global rule, a revoked/expired record,
an unresolved conflict, changed source content and malformed/missing lifecycle
metadata. Exercise actual retrieval adapters and context assembly, not only a
standalone predicate. Check identifier/source integrity and bypass paths. Retain
history; deletion requires separate authority. Synthetic cases stay outside live
memory. Model-answer quality requires its own authorized evaluation; filtering
fixtures alone do not prove a model will never invent or misuse a fact.

Record these independently: policy documented, filter implemented, adapter tests
passed, runtime activated, and target-specific answer tests passed. This guide does
not claim that every installed provider already enforces these requirements.

## Optional Obsidian and private device synchronization

Discover the actual host and viewer device. An unavailable client does not prevent
host preparation, but leaves client acceptance incomplete. Use an existing vault
or one approved dedicated folder outside another sync provider's managed location.
Do not sync the whole agent home. No community plugin is needed for basic links.

If the owner selects Syncthing over Tailscale:

- Verify official archive provenance and actual native help. In tested v2.1.6,
  generation creates no default folder; `--no-default-folder` is not a valid flag.
- Generate distinct device identities. Configure offline before the first listener.
  The native `cli config` command uses live REST, not a stopped config file.
- Use approved static Tailscale TCP addresses and device/network restrictions.
  Keep GUI/API on authenticated loopback. Disable public/local discovery, NAT,
  relays, telemetry and auto-upgrades for this static private design. Verify actual
  sockets and effective config, not merely the authored file. Check tailnet policy
  separately; do not infer it from membership or silently change it.
- Share only the intended folder. Exclude per-device `.obsidian`, credentials,
  caches and version stores. `.stignore` itself does not replicate: configure both.
  Keep conflict copies and native versioning plus independent private backups.
- Preserve existing apps/services. Use native per-user service management for each
  platform. Do not invent SSH access or bypass host-key, Gatekeeper or OS approval.
- Read mutations back by identity. Syncthing can reorder device arrays; inspect
  after an assertion failure before retrying a write that may already have worked.

Acceptance requires received-file hashes, a return edit, retained prior versions
on both receivers, per-device ignore isolation, zero pending items/errors and
actual viewer navigation from a concept to its source. A remote completion counter
is protocol evidence, not proof that Obsidian displayed the right vault. Label
relayed client evidence separately from direct host observations. Preserve test
artifacts until approved cleanup. This proves the tested device pair, not universal
OS compatibility, a cold-boot recovery path or memory lifecycle enforcement.

References: [Syncthing configuration](https://docs.syncthing.net/users/config.html),
[REST configuration](https://docs.syncthing.net/rest/config.html),
[versioning](https://docs.syncthing.net/users/versioning.html),
[Obsidian vaults](https://help.obsidian.md/manage-vaults).
