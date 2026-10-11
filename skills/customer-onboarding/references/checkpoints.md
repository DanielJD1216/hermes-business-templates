# Checkpoint contract

Agent-operated, stdlib-only Python 3.9+ on Linux/WSL and macOS (uses `fcntl`).
Native Windows is not supported by this helper. macOS runtime acceptance remains
unverified. Do not confuse upstream platform support with this candidate's tests.

The owner chooses a private directory outside Git checkouts, shared workspaces and
runtime memory. The helper requires owner-only directory permissions (0700), rejects
symlinks/hardlinked evidence, writes checkpoints as 0600, locks one local writer and
atomically replaces/fsyncs the receipt. Evidence files are protected by the private
parent directory; do not move them to shared folders. Parent backup/sync policies
and same-user processes still need review. No code here supplies OS isolation.

## Evidence and advancement

Under `evidence/<stage>/`, create exactly the required files named in SKILL.md.
For `exports`, also include the source files enumerated below. Unknown extra files,
empty outputs and missing files block advancement. Use fixed artifact names, not
customer names. Source/provenance/approvals themselves are private. Never put tokens
in any artifact. The checkpoint stores only hashes, fixed filenames/stages and opaque
message references, not source contents or absolute paths.

1. Run `init` once. On repeat, use `status`, never overwrite the existing record.
2. Collect the next stage's real evidence using the skill. Run `status`; it returns
   a `proposal_digest` only if required artifacts are present and structurally valid.
3. For `identity`, `review`, `boundaries`, `files` and `closeout`, show the actual
   proposal in the private conversation, ask one approval question and wait. Map
   the owner's real message to an opaque ID such as `approval-001`; keep the actual
   conversation locator privately in that stage's evidence before computing the
   final digest. Do not put personal prose into `--receipt` or fabricate a reference.
4. Run `advance` with exact stage/digest and, for gated stages, `--receipt`. An
   out-of-order stage, changed digest, missing approval reference or active blocker
   refuses the write. A `files` approval is the pre-install/write authorization gate;
   **require status to report `install` before invoking hbt or writing runtime data**.
   The helper never invokes hbt, creates profiles, writes memories or connects tools.
5. Use `block --reason access|prerequisite|approval|source|privacy|recovery|drift|verification`
   for an unresolved step. `block --reason none` clears it only after actual
   resolution. `status` computes the next action. Failure to verify old evidence
   exits 2 without modifying it; if drift prevents recording a blocker, retain that
   error with the private run's recovery notes, not by editing the checkpoint.
6. Resume with `status` and live read-only checks, not just a saved stage label.
   Completed source/output hashes are rechecked every time. A hard interruption
   before receipt replacement leaves the previous stage current. Inspect already
   performed external actions before retrying; do not repeat sends/installs blindly.
7. Final closeout sets `archived: true`; the directory stays in place. It is a
   historical setup receipt, not an assertion that all optional integrations passed.

There is deliberately no force/reset/delete or automatic recovery command. If a
completed proposal needs legitimate revision, preserve the entire prior run and
its raw sources, agree the new scope, create a separately named revision run and
reference its predecessor in private evidence. Reuse verified files by ordinary
copies (not links); get new approvals for changed outputs/destinations. Do not
reinterpret an existing stale installer record as a fresh-install opportunity.

This checks structure/order/hashes, not whether the model told the truth. Markdown
receipts must contain actual tool output and scoped conclusions, not "done".
Approval IDs are audit pointers, **not authenticated consent tokens**. A capable
agent could bypass the helper and call hbt directly; the skill forbids that, but
text instructions are not mechanical security. A forged ledger, omitted conflict
or invented provenance cannot be detected semantically by this small helper.

## Private export manifest (`exports/sources.json`)

The agent writes this, not the customer. Preserve each returned credential-free
export as received; record its hash at collection and never revise its bytes.
The stage snapshot seals the manifest and every named raw export together.

```json
{
  "skipped": false,
  "sources": [
    {
      "id": "source-001",
      "file": "source-001.md",
      "origin": "origin-001",
      "platform": "owner-selected platform",
      "model": "unknown",
      "exported_at": "unknown",
      "coverage": "only genuinely accessible material",
      "lineage": "original export; cite available source pointers here"
    }
  ]
}
```

Use `source-001` through `source-999`; files must match IDs. Related copies use
one origin ID. Unknown origin is JSON `null`, not a newly invented independent
origin. Platform/model/date can be `unknown`; don't infer them from writing style.
An owner-declined export stage is `{"skipped": true, "sources": []}` with the
reason/consent noted in the preceding private reference evidence. Never invent an
export just to satisfy a stage. A source's self-reported lineage is not independent
proof; verify where possible and keep uncertainty.

## Private review ledger (`review/context-review.json`)

```json
{
  "claims": [
    {
      "id": "claim-001",
      "text": "Synthetic example of an uncertain preference, not customer data.",
      "sources": ["source-001"],
      "source_locations": "source-001, claim A; exact available pointer",
      "independent_origins": 1,
      "flags": ["stale", "inferred"],
      "decision": "REVIEW",
      "domain": "personal",
      "audience": "owner",
      "destination": "private-review",
      "reason": "Needs a specific clarification; keep the original."
    }
  ]
}
```

- `sources` lists manifest IDs, or `owner` for an actual interview answer referenced
  in `source_locations`. Unknown/missing sources cannot become evidence.
- `independent_origins` cannot exceed known distinct origins (plus an actual owner
  answer). Copied exports with one origin count once; unknown origins count zero.
  The helper verifies the declared structure, not whether an origin is genuine.
- Flags: `conflict`, `stale`, `inferred`, `duplicate`, `domain`. Flagged INCLUDE
  requires `resolution_ref`, an opaque reference to the actual clarification or
  source resolution documented in `reason`/`source_locations`.
- INCLUDE destinations: personal/owner/owner-personal; business/owner/owner-business;
  business/team/shared-business. Business sharing still needs the later exact
  boundary approval. Mixed/unknown cannot be INCLUDE.
- REVIEW always uses owner/private-review. EXCLUDE uses destination `none` and does
  not delete raw data. Empty claims are allowed only when there is genuinely no
  adoptable context; explain the missing context in consolidated.md.

Files-stage `team.json` uses the existing hbt schema in README. For an explicitly
main-only setup, save `{"schema": 1, "roles": []}` as the decision artifact and
state **do not pass this to hbt** in write-plan.md; the backend requires roles and
must be skipped. Do not create an empty/default team by accident. Other staged
Markdown outputs are drafts until approved; never deploy the combined private
review document to a shared business folder.

## Official sources

Recheck these at customer setup; vendor support, pricing and commands change.
Official pages consulted on 2026-10-11 UTC (2026-10-10 PDT):

- [Hermes documentation index](https://hermes-agent.nousresearch.com/docs/llms.txt),
  [installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation),
  [models](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models),
  [file purposes](https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what).
  Hermes is the initial supported harness, with interchangeable providers/models
  through native selection (`hermes model`; verify installed help first). Preserve
  a working login; do not replace it to match a template. No pinned model purchase.
- [Tailscale quickstart](https://tailscale.com/kb/1017/install): private host access
  and access-control policies. Verify only intended owners/devices can reach it.
  Do not expose services publicly, use Funnel or weaken ACLs to bypass a blocker.
- [Parsec compatibility](https://support.parsec.app/hc/en-us/articles/32381568346644-Hardware-and-Software-Compatibility),
  [Linux support](https://support.parsec.app/hc/en-us/articles/32381552552340-Install-Parsec-App-on-Linux),
  [pricing/licensing](https://parsec.app/pricing): graphical recovery option on
  compatible Windows/macOS hosts; Linux client does not provide Linux hosting.
  Current pricing labels Personal/Individuals for personal non-commercial use;
  commercial use requires Teams/Enterprise. Do not promise free business recovery
  or universal OS support. Verify exact host, permissions, licensing and fallback
  with the owner before installation. Unsupported Parsec hosting needs a separately
  agreed recovery method, not a claim of working access.
- [Herdr](https://herdr.dev): persistent development sessions. Use installed
  `herdr --help` / `herdr --skill` as the command authority. Optional project setup
  stays in `templates/creator/workspace/skills/project-onboarding/SKILL.md`.

Fetch source pages with `web_extract` or the owner's browser; use `terminal` for
installed help. A page describing a feature does not prove it works on this host.
