# Required finished state

This is an outcome contract. The agent chooses supported implementation steps
for the actual host; it is not required to reproduce the publisher's machine,
profile roster, model, username, service paths or accounts. All components below
are required for baseline completion. Special-purpose tools and extra roles are
allocated according to need, not enabled everywhere.

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
| Canonical context and projects | Clear identity, operating rules, approved user/context/tool facts, file-placement/access map and project catalog. | Actual approved locations and source links; personal/owner-business/shared-business scopes separated. Existing equivalent documents may be mapped instead of renamed or duplicated. |
| OpenViking memory | Working persistent memory with correct owner/profile scope and private service access. | Native service health; one authorized non-sensitive write reaches completed status and is recalled in the intended scope; authentication/exposure/routing verified. No historical replay merely for onboarding. |
| Memory watchdog | Script-only memory health/search checks and approved outage/recovery delivery. | Exact job read-back, health/search behavior and authorized destination delivery tested. No chat model. Explain any embedding use/cost. An existing main or selected profile can own it; do not require Ops. |
| Local file discovery | Semantic search plus exact file lookup and authorized history lookup over approved local roots. | Known source retrieved with its actual path; source bytes read; exclusions verified; an approved addition/change and rename/removal followed by refresh shows fresh results and no stale hit. |
| Slack | Owner/team interface with correct bot identities, minimum allowlists and owner-only administration. Channel messages and thread follow-ups require explicit mentions. | Authorized reply in the exact channel/thread, mention-only behavior and denial of unauthorized access/administration verified with scoped tests. No forced specialists or duplicate bot tokens. |
| Hermes Desktop | Working owner client connected privately to the intended host/profile. | Client installation, endpoint/profile selection and authenticated owner access observed. Server health alone does not prove client access. |
| Tailscale/private transport | Private host reachability and minimum access policy. | Reachability from an approved client plus effective ACL/grant policy and service binding/authentication checked. Tailnet membership alone is insufficient. No public Funnel or public listener by default. |
| Herdr | Available private development-session workspace and a verified preset mapped to the chosen roster. | Supported native installation, private session access and preset/pane mapping observed. A main-only roster may use separate main sessions or idle slots; never create unwanted roles. Do not start paid/model sessions just to prove pane labels. |
| Remote recovery | Supported, licensed graphical recovery independent of the normal agent connection. | Verify Parsec host/platform/license suitability, or an explicitly approved equivalent, and actual owner reconnect/recovery. No forced purchase or assumption of universal free hosting. |
| Capability allocation | A reviewable inventory of skills, plugins, MCP integrations and toolsets, with selected assignments and unresolved acquisition gaps visible. | Record purpose, source/version, platform support, account/cost, license, permissions, install/auth state and responsible profile. Check real availability. Disabled, unavailable and unverified are distinct. Metadata inclusion is not permission to activate or redistribute. |

Only the memory watchdog is a baseline recurring job. Additional schedules,
including semantic-index refresh, require the owner's specific choice of scope,
cadence, destination and cost. Existing unrelated jobs and boards remain intact.
The removed business/content playbooks and recurring business digests are not
requirements of this agent-led guide, even though the legacy backend still ships them.

## Evidence and completion

Use the private progress record described in [context and files](context-and-files.md).
For each component record: state (`verified`, `failed`, `not-tested`), actual host,
method, redacted observation, time if known, evidence location and remaining limit.
Record the relevant owner authority for model usage, sends and new schedules.
Reuse current applicable evidence; do not manufacture repeat usage charges.

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
