# Required finished state

This is an outcome contract. The agent chooses supported implementation steps
for the actual host; it is not required to reproduce the publisher's machine,
profile roster, model, username, service paths or accounts. All components below
are required for baseline completion. Special-purpose tools and extra roles are
allocated according to need, not enabled everywhere.

Functional coverage is required; implementation choices are adaptable. Every
domain needs an actual implementation or a named incomplete requirement. Record
owner decisions separately from verification. Declining a particular product can
select an equivalent; declining a required outcome leaves the baseline incomplete.
An unasked roster, viewer, sync or capability choice remains `not-offered` or
`not-decided`, never implicitly declined. Optional implementations must still be
considered for the owner's workflow, without installing unnecessary services.

## Assistant behavior

Preserve the existing assistant's identity and working login. Use these generic
behaviors as a reviewed starting point, not an automatic replacement SOUL:

- Be practical, candid and accountable. Retrieve before asking; name assumptions.
- Execute authorized work and verify results. Distinguish planned, running,
  blocked, completed and verified states. State who must act next.
- Preserve privacy, owner choices and unrelated work. Do not impersonate the
  owner or treat historical permission as current consent.
- Keep ordinary work in its originating conversation. Use development-session
  orchestration only when selected; keep one coordinator and one writer per scope.
- Keep durable facts, project rules, reusable procedures and mechanically enforced
  checks in the appropriate stores rather than duplicating everything everywhere.

A compatible existing instruction set can satisfy this with reviewed no-change.
Model names and personality are owner choices, not acceptance requirements.

## Components and proof

| Component | Required outcome | Proof required |
|---|---|---|
| Hermes and model access | Working native Hermes on the intended host; owner-selected supported provider/model and owner-controlled authentication. | Version/runtime and effective selection checked; existing recent scoped proof or an authorized bounded interaction confirms access. A config value or auth-file presence alone is insufficient. |
| Main assistant | Existing name, identity, login and history preserved; approved generic behavior merge or no-change. | Reviewed diff/no-change and read-back of the intended instruction locations. No secret contents in evidence. |
| Responsibilities and roster | Explicit needs-based ownership for ordinary work, implementation/review when needed, knowledge curation and maintenance. | Reviewed main-only or selected specialist map, including tool/data/channel access and orchestration choice. A terminal pane or temporary worker is not a persistent agent. |
| Canonical context and projects | Clear identity, operating rules, approved facts, operational file-placement/access rules and project catalog. | Existing roots preserved; personal, owner-business and shared-business audiences separated. An approved project or operating-system collection exercises intake, correct placement, local authority, output and archive rules. Naming/status and catalog-drift handling work. No invented business project is required. |
| OpenViking memory | Working persistent memory with correct owner/profile scope and private service access. | Native service health; one authorized non-sensitive write reaches completed status and is recalled in the intended scope; authentication/exposure/routing verified. No historical replay merely for onboarding. |
| Memory watchdog | Script-only memory health/search checks and approved outage/recovery delivery. | Exact job read-back, health/search behavior and authorized destination delivery tested. No chat model. Explain any embedding use/cost. An existing main or selected profile can own it; do not require Ops. |
| Local file discovery | Semantic search plus exact file lookup and authorized history lookup over approved local roots. | Known source retrieved with its actual path; source bytes read; exclusions verified; an approved addition/change and rename/removal followed by refresh shows fresh results and no stale hit. |
| Curated knowledge and scoped currentness | Source-backed wiki or equivalent with a useful bounded collection, current decisions and preserved history. | Cite approved originals, identify the curator and source-update procedure, and test the selected answer route with current, changed/corrected, conflicting and out-of-scope evidence. Stale/history material must not become current authority. Record ungoverned paths; do not imply universal memory enforcement. See [lifecycle acceptance](knowledge-lifecycle.md). |
| Knowledge viewing and device workflow | Owner can inspect the curated index, explanation and original; explicit viewer and synchronization decisions. | Choose Obsidian or an existing suitable viewer and demonstrate navigation. Select sync only when needed for approved devices, or record why no replica is needed. A selected sync route requires client, conflict/version and exclusion checks; app/skill presence is insufficient. |
| Slack | Owner/team interface with correct bot identities, minimum allowlists and owner-only administration. Channel messages and thread follow-ups require explicit mentions. | Authorized reply in the exact channel/thread, mention-only behavior and denial of unauthorized access/administration verified with scoped tests. No forced specialists or duplicate bot tokens. |
| Hermes Desktop | Working owner client connected privately to the intended host/profile. | Client installation, endpoint/profile selection and authenticated owner access observed. Server health alone does not prove client access. |
| Tailscale/private transport | Private host reachability and minimum access policy. | Reachability from an approved client plus effective ACL/grant policy and service binding/authentication checked. Tailnet membership alone is insufficient. No public Funnel or public listener by default. |
| Herdr and Herdr Web UI | Available private development-session workspace, the `devswha/herdr-web-ui` browser client, and a verified preset mapped to the chosen roster. | Offer the [standard four-pane development preset](herdr-web-ui.md#standard-four-pane-development-preset) or record an approved alternative. Verify native installation, web-client health, owner access, private authorization and actual pane/profile/session mapping. Preserve existing sessions; main-only use may keep main sessions or idle slots without creating specialists. Follow the [Web UI checks](herdr-web-ui.md); a loaded shell is not a ready agent workspace. Phone features and model-session launches need their applicable authority and evidence. |
| Remote recovery | Supported, licensed graphical recovery independent of the normal agent connection. | Verify Parsec host/platform/license suitability, or an explicitly approved equivalent, and actual owner reconnect/recovery. No forced purchase or assumption of universal free hosting. |
| Capability allocation | A reviewable inventory of skills, plugins, MCP integrations and toolsets, with selected assignments and unresolved acquisition gaps visible. | Record purpose, source/version, platform support, account/cost, license, permissions, install/auth state and responsible profile. Check real availability. Disabled, unavailable and unverified are distinct. Metadata inclusion is not permission to activate or redistribute. |
| Maintenance and recovery data | Named maintenance owner, trigger, failure recipient and protected recovery set, including updates and rollback. | Verify selected routine outcomes, not just exit status. Record backup scope, consistency, retention and independent destination; restore to a separate private location and verify useful access/recall. Graphical reconnect and file existence do not prove data recovery. Follow [maintenance](maintenance.md). |
| Complete operating cycle | The components support useful work together. | An authorized request finds its original source, uses the correct project and responsible agent, produces a grounded output, retains a useful decision and retrieves it in a fresh session. Use approved existing or non-sensitive material; sends and model usage retain their approval gates. |

Only the memory watchdog is a baseline recurring job. Additional schedules,
including semantic-index refresh, require the owner's specific choice of scope,
cadence, destination and cost. Existing unrelated jobs and boards remain intact.
The removed business/content playbooks and recurring business digests are not
requirements of this agent-led guide, even though the legacy backend still ships them.

## Memory, knowledge and file discovery

- **Memory:** interaction-derived preferences, facts and experience. OpenViking
  handles this, with actual write/recall and scope checks.
- **Knowledge base:** approved reference documents, manuals, policies and project
  sources, with provenance, ownership and a known current version. It is not just
  extracted chat facts or a folder labelled knowledge.
- **Retrieval:** how the agent finds those sources. A bounded local index such as
  LEANN plus direct source reads can provide a file-backed knowledge base. OpenViking
  also supports explicitly added resources; check the installed version's supported
  resource namespaces and access controls rather than assuming current upstream
  features are installed.

Prefer existing canonical sources and working retrieval over another database or
duplicate ingestion pipeline. Keep source files authoritative. If selected resources
are added to OpenViking, obtain scope/processing/cost approval, exclude credentials
and unrelated private data, preserve source/version provenance, verify processing
completion and a source-grounded answer, and check updates/removals stop stale
retrieval. Folder names and URI prefixes alone do not enforce access control.

The baseline requires canonical sources and verified local discovery; a new
OpenViking resource corpus is an owner-approved implementation choice, not an
automatic import of the whole workspace. An empty resources collection does not
mean there are no knowledge files elsewhere, and memory recall does not prove
document ingestion. Do not reactivate archived knowledge projects implicitly.

Knowledge storage and viewing are separate: ordinary Markdown can hold the wiki;
Obsidian can display/edit it. LLM curation maintains its explanations and citations.
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
