# Required finished state

This is an outcome contract. The agent chooses supported implementation steps
for the actual host; it is not required to reproduce the publisher's machine,
personal names, model, username, service paths or accounts. All components below
are required for baseline completion. Special-purpose tools and extra roles are
allocated according to need, not enabled everywhere.

Functional coverage and the named required products are required. Every
domain needs an actual implementation or a named incomplete requirement. Record
owner decisions separately from verification. LEANN, Obsidian and the four-pane
development team cannot be silently replaced or waived. A declined or deferred
requirement leaves the baseline incomplete. Names, access, devices and approved
schedule settings adapt to the owner. Sync is needed only when replicas are needed.
Kanban, formal delivery pipelines and old-conversation context reconstruction are
outside onboarding. Parsec is required for remote debugging and troubleshooting,
not as backup or data restoration. Preserve existing installations; exclusions do
not authorize removal. Data backup and restore verification remain separate requirements.

## Assistant behavior

Preserve the existing assistant's identity and working login. Use these generic
behaviors as a reviewed starting point, not an automatic replacement SOUL:

- Be practical, candid and accountable. Retrieve before asking; name assumptions.
- Execute authorized work and verify results. Distinguish planned, running,
  blocked, completed and verified states. State who must act next.
- Preserve privacy, owner choices and unrelated work. Do not impersonate the
  owner or treat historical permission as current consent.
- Keep ordinary non-development work in its originating conversation. Prepare the
  required per-project Herdr development team; keep one coordinator and one writer
  per scope. This does not require Kanban or a formal delivery pipeline.
- Keep durable facts, project rules, reusable procedures and mechanically enforced
  checks in the appropriate stores rather than duplicating everything everywhere.

A compatible existing instruction set can satisfy this with reviewed no-change.
Model names and personality are owner choices, not acceptance requirements.
For each affected approved profile, follow [identity and behavior guidance](context-and-files.md#identity-and-behavior-across-profiles)
and the [profile lifecycle](maintenance.md#profile-lifecycle). Verify the approved
instruction sources and active loading in the intended fresh session, not a preferred
personality or file presence alone. Reconcile affected roster, context, memory,
capability and maintenance proof after changes; retain the same required rows and
preserve valid unrelated evidence. A profile inventory is not automatic enforcement.

## Components and proof

| Component | Required outcome | Proof required |
|---|---|---|
| Hermes and model access | Working native Hermes on the intended host; owner-selected supported provider/model and owner-controlled authentication. New role profiles default to the EA's provider/account through supported native credential reuse, not separate providers/subscriptions. | Version/runtime and effective selection checked per profile; existing recent scoped proof or an authorized bounded interaction confirms access to the intended account. Preserve owner-selected exceptions. A config value or auth-file presence alone is insufficient; missing supported credential sharing remains a named gap, not permission to copy credentials or change billing. |
| Main assistant | Existing name, identity, login and history preserved; approved generic behavior merge or no-change. | Reviewed diff/no-change and read-back of the intended instruction locations. No secret contents in evidence. |
| Responsibilities and roster | Existing primary assistant as EA, permanent CTO and Engineer roles, and two ready Engineer sessions in the required development team; explicit curation/maintenance ownership. | Preserve the EA's individual name and login. Verify role profiles, approved instructions, authentication, tool/data/channel scope and all four session bindings. Default to three profiles: EA, CTO and one Engineer profile with two distinct conversation IDs. Verify shared memory/write safety before concurrent use; do not automatically create a second Engineer profile. Main-only operation or temporary workers do not satisfy this row. Extra non-development roles are not mandatory. |
| Canonical context and projects | Clear identity, operating rules, approved facts, operational file-placement/access rules and project catalog. | Existing roots preserved; personal, owner-business and shared-business audiences separated. An approved project or operating-system collection exercises intake, correct placement, local authority, output and archive rules. Naming/status and catalog-drift handling work. No invented business project is required. |
| OpenViking memory | Reliable persistent memory on a supported exact runtime combination, with correct owner/profile scope and private service access. | Follow [memory reliability](memory-reliability.md): version-bound native release evidence plus bounded target-host fresh save/index/recall, growth/tail, distinct-source and scope checks; intact canonical sources and truthful interruption/failure handling. Health, submission, `.done` and empty queues alone do not prove completion. Missing compatible artifacts or platform proof block this row. No historical replay merely for onboarding. |
| Memory watchdog | Script-only health/search, failed/stalled-save and installed-version/patch-drift checks, with approved alert/recovery delivery. | Follow [watchdog acceptance](memory-reliability.md#required-watchdog-behavior): exact job/environment read-back, bounded negative checks and authorized destination delivery tested. Unknown/inaccessible task states remain unverified; preserve historical failures. No chat model. Explain embedding use/cost. An existing main or selected profile can own it; do not require Ops. |
| Local file discovery | LEANN semantic search plus exact file lookup and authorized history lookup over approved local roots. | Verify installed LEANN and actual retrieval through each assigned agent surface. Retrieve the known source and read its bytes; verify exclusions. An approved addition/change and rename/removal followed by refresh must show fresh results and no stale hit. OpenViking resources do not replace required LEANN. |
| Scheduled index refresh | An enabled recurring LEANN refresh on the actual host, with explicit approved scope, cadence/timezone, embedding cost boundary and failure recipient. | Follow [refresh acceptance](maintenance.md#required-leann-refresh-schedule): shared exclusions, unknown-root quarantine, safe candidate publication and retained working index on failure. Verify changed-source retrieval and absent removed/excluded sources; unchanged refresh still needs bounded search and binding proof. Read back the actual schedule and authorized attention/recovery messages. Missing/stale proof is unverified, not healthy. No silent ingestion expansion or chat model for refresh. |
| Curated knowledge and scoped currentness | Source-backed wiki or equivalent with a useful bounded collection, current decisions and preserved history. | Cite approved originals, identify the curator and source-update procedure, and test the selected answer route with current, changed/corrected, conflicting and out-of-scope evidence. Stale/history material must not become current authority. Record ungoverned paths; do not imply universal memory enforcement. See [lifecycle acceptance](knowledge-lifecycle.md). |
| Knowledge viewing and device workflow | Explicit mapping of agent host, owner-selected viewing/editing devices and authoritative knowledge storage; Obsidian connected to the approved vault on each selected viewing device. | Follow [device-role selection](knowledge-lifecycle.md#select-device-roles-before-installation). Verify device identity, intended vault, current content and actual Obsidian navigation from index to explanation to original on every selected viewer. Host-only installation cannot satisfy a separate viewer; inaccessible devices remain incomplete. Reuse approved vaults; select sync only when replicas are needed and verify its intended direction, conflict/version handling and exclusions. Another viewer or an installed skill does not satisfy this row. |
| Slack | Owner/team interface with correct bot identities, minimum allowlists and owner-only administration. Channel messages and thread follow-ups require explicit mentions. | Authorized reply in the exact channel/thread, mention-only behavior and denial of unauthorized access/administration verified with scoped tests. Use the approved role/channel map; no duplicate bot tokens or unapproved extra roles. |
| Hermes Desktop | Working owner client connected privately to the intended host/profile. | Client installation, endpoint/profile selection and authenticated owner access observed. Server health alone does not prove client access. |
| Tailscale/private transport | Private host reachability and minimum access policy. | Reachability from an approved client plus effective ACL/grant policy and service binding/authentication checked. Tailnet membership alone is insufficient. No public Funnel or public listener by default. |
| Herdr and Herdr Web UI | Private per-project development orchestration, the `devswha/herdr-web-ui` browser client, and the required four-pane team. | Verify EA top left, CTO top right, Engineer #1 bottom left and Engineer #2 bottom right. Install/discover the reusable project-onboarding skill; prove project creation/reuse, actual profile/session mapping and authenticated readiness in all four slots under applicable launch/model-use authority. Preserve the EA's name and active sessions. Shell-only or alternative layouts are not completion. Verify private owner access and a bounded authorized handoff; phone extras are separate choices. |
| Parsec remote debugging | Working Parsec access to the intended host desktop for owner-approved visual debugging and hands-on troubleshooting. | Verify actual host/client platform support, applicable license, account/OS permissions and an authorized connection with the needed display/input access. A client install alone is not hosting proof. Preserve sessions and limit support access to approved people/scope. Missing support, consent or entitlement is a blocker, not a silent substitute or forced purchase. This does not prove backup restoration or cold-boot disaster recovery. |
| Capability allocation | Full-catalog review and an installed, authenticated where needed, tested role-specific set of skills, plugins, MCP integrations and toolsets. | Record each catalog disposition and the required set per role, source/version, platform, account/cost, license and access. Verify use through the assigned agent surface. An unresolved required capability blocks completion; an inventory alone is insufficient. Excluded/unknown entries are not activated. Do not enable everything everywhere or bypass license, cost or account approval. |
| Maintenance and recovery data | Named maintenance owner, trigger, failure recipient and protected recovery set, including updates and rollback. | Verify selected routine outcomes, not just exit status. Record backup scope, consistency, retention and independent destination; restore to a separate private location and verify useful access/recall. Graphical reconnect and file existence do not prove data recovery. Follow [maintenance](maintenance.md). |
| Complete operating cycle | The components support useful work together. | An authorized request finds its original source, uses the correct project and responsible agent, produces a grounded output, retains a useful decision and retrieves it in a fresh session. Use approved existing or non-sensitive material; sends and model usage retain their approval gates. |

The memory watchdog and scheduled LEANN index refresh are baseline recurring jobs.
Both require approved scope, cadence, destination and cost; missing authority is
a blocker, not permission to omit them. Reuse existing jobs rather than duplicate
them. All other schedules require specific opt-in. Existing jobs and boards stay intact.
The removed business/content playbooks and recurring business digests are not
requirements of this agent-led guide, even though the legacy backend still ships them.

## Memory, knowledge and file discovery

- **Memory:** interaction-derived preferences, facts and experience. OpenViking
  handles this, with actual write/recall and scope checks.
- **Knowledge base:** approved reference documents, manuals, policies and project
  sources, with provenance, ownership and a known current version. It is not just
  extracted chat facts or a folder labelled knowledge.
- **Retrieval:** how the agent finds those sources. Required LEANN indexing plus
  direct source reads provides file-backed discovery. OpenViking
  also supports explicitly added resources; check the installed version's supported
  resource namespaces and access controls rather than assuming current upstream
  features are installed.

Reuse existing LEANN and canonical sources rather than duplicate installations.
Keep source files authoritative. If selected resources
are added to OpenViking, obtain scope/processing/cost approval, exclude credentials
and unrelated private data, preserve source/version provenance, verify processing
completion and a source-grounded answer, and check updates/removals stop stale
retrieval. Folder names and URI prefixes alone do not enforce access control.

The baseline requires canonical sources and verified LEANN discovery; a new
OpenViking resource corpus is an owner-approved implementation choice, not an
automatic import of the whole workspace. An empty resources collection does not
mean there are no knowledge files elsewhere, and memory recall does not prove
document ingestion. Do not reactivate archived knowledge projects implicitly.

Knowledge storage and viewing are separate: ordinary Markdown can hold the wiki;
required Obsidian displays/edits it. LLM curation maintains explanations and citations.
Neither a synced vault nor a successful memory write proves lifecycle-safe answers.
Follow [knowledge and lifecycle acceptance](knowledge-lifecycle.md), preserving
incomplete enforcement/runtime/model-evaluation gates rather than calling them done.

## Evidence and completion

The baseline does not require universal filtering across all memory-engine APIs,
capture, deletion and historical chat context. Such engineering is an explicitly
scoped extension with its own supported implementation, review and activation
gates. It cannot substitute for the required knowledge workflow. If the owner
requires broader protection, track it as an additional completion requirement;
do not label it complete from a bounded pilot or lower the requirement silently.

Use the private progress record described in [context and files](context-and-files.md).
For each component record: state (`verified`, `failed`, `not-tested`), actual host,
method, redacted observation, time if known, evidence location and remaining limit.
Record the relevant owner authority for model usage, sends and new schedules.
Reuse current applicable evidence; do not manufacture repeat usage charges.

State whether evidence is fresh, historical or owner-relayed. Configuration,
running processes, exercised behavior and restored operation are different proof
levels. A profile name is not isolation; a local terminal or shared OS identity
must not be described as sandboxed without verifying the actual tool boundary.
Match per-interface tool access to the approved audience, including search indexes.

Every required component must be verified before saying the baseline is complete.
On revision changes, reconcile existing evidence against the new requirements.
Preserve old graphical-recovery evidence and reuse it only where it proves the
Parsec debugging requirement. Add the distinct Parsec and index-refresh rows,
and reopen prior generic-viewer/search/main-only passes that do not meet this scope.
Calculate checklist coverage with a tool: verified rows divided by all required
rows times 100. Show the numerator and denominator; give no partial credit and do
not remove deferred rows. This is checklist coverage, not an effort/time estimate.
Track additional owner-required outcomes separately; they also gate completion.
Use the [mandatory progress checkpoint](../SKILL.md#mandatory-progress-checkpoint)
on every setup reply. The read-only checker derives the denominator from this
selected baseline and identifies owner-relayed rows within the total. Its passing
result establishes record consistency only, not independent verification of those
rows. A full percentage is not completion while decisions or owner outcomes remain.
A deferred client device, unsupported recovery method or missing memory test keeps
its row incomplete, but does not block independent host work. Report partial
completion honestly. A text instruction, model assertion, installed package,
fixture result or structured ledger cannot substitute for target-host evidence.

Model, memory and embedding providers are separate choices. The setup agent may
use any suitable model, but each installed service still needs an actually
supported provider/authentication route. Do not assume one subscription works
through every third-party application, force a new subscription, or silently
fall back to a paid API. Changing embedding models requires a separately rebuilt
and verified index; matching vector dimensions do not make existing vectors compatible.

### Native OAuth versus convenience setup

OpenViking has a native `openai-codex` backend for ChatGPT/Codex OAuth in supported
versions. A Quick Local adapter or setup wizard that accepts only a different
route does not prove the underlying backend lacks OAuth. Inspect installed native
help and provider code before declaring incompatibility or changing billing.
Preserve the owner's main Hermes model/login. Native OpenViking sign-in may be a
separate owner-attended authorization; never copy another service's credentials.
Backend availability is not a successful login or a passed memory write/recall test.
Local embeddings also do not make LLM extraction or document summarization local:
explain which selected provider receives text and obtain the applicable consent.
See [Hermes memory providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers)
and [OpenViking upstream](https://github.com/volcengine/OpenViking).
