# Required memory reliability

A healthy server and one successful search do not prove that later saves work.
The OpenViking memory and Memory watchdog baseline rows require the evidence below.
The agent runs these checks under existing authority; this is not an extra owner
checklist or permission to engineer a private memory fork during onboarding.

## Select a supported combination

Record the exact service and Hermes adapter/plugin revisions, OS/architecture,
service interpreter, extraction provider/authentication route, embedding model and
runtime, vector dimensions, effective input limit including prefixes, and any
compatibility patch identifier/hash. Preserve the owner's login and model choices.
Local embeddings do not make extraction local; retain processing and cost consent.

Prefer a supported upstream release with applicable reliability evidence. A version
number, import, matching dimensions or successful small write is not that evidence.
A compatibility patch also needs a distributable artifact, exact base-version and
platform bindings, integrity checks, license review, maintenance owner and tested
installation/recovery instructions. Do not copy a maintainer's installed package,
private installer, credentials or machine-specific paths into a customer setup.

**This guide ships requirements, not an OpenViking repair or acceptance runner.**
It certifies no runtime combination merely by listing a package or platform.
Linux/WSL evidence does not establish native macOS support. For each selected host,
locate the applicable supported artifact and release checks before making changes.
If they are unavailable or incompatible, mark the memory row blocked and name the
missing artifact, evidence or platform support. Continue independent onboarding;
do not invent commands, silently change providers or ask the customer to build a fork.
Missing proof is not proof of a broken installation or an unsupported platform.
Different OS or Python versions alone do not establish incompatibility; identify
the actual unverified boundary in the selected combination.

## Reuse native Mac evidence without overstating it

The official [Mac API/CLI job](https://github.com/volcengine/OpenViking/actions/runs/35500420728/job/106051099500)
ran on 2026-09-20 at commit `3fca2577520f00b7f580d85d4ac6ae42bb9ba6f1`.
Its structured reports identify macOS 14.8.9 arm64 and Python 3.10.11. The job log
confirms the full VLM/embedding-credential branch ran, not the credential-free fallback.

| Executed group | Passed | Skipped |
|---|---:|---:|
| Serial API filesystem/resource checks | 34 | 0 |
| Remaining non-slow API checks | 93 | 0 |
| Released CLI compatibility checks | 16 | 0 |
| Current-source CLI integration checks | 45 | 1 |

These are test executions across separate invocations, not distinct reliability
guarantees. The HTML reports omit the separate serial and compatibility runs;
read the job log as well. Slow suites were excluded by the
[pinned workflow](https://github.com/volcengine/OpenViking/blob/3fca2577520f00b7f580d85d4ac6ae42bb9ba6f1/.github/workflows/api_test.yml).
The skipped CLI wait-timeout test records a query/body parameter mismatch at that
revision. Check installed-version applicability before using it for a bounded wait;
do not assume either that the defect persists or that it is fixed.

The report artifact is `api-test-reports-macos-14-35500420728`, ID `10603295699`;
its downloaded ZIP matched GitHub's SHA-256
`1f1171ce83f113745d8256b4ef0d86018bd6fe6efdb14ead63fff8a2b3eafa1e`.
Artifacts can expire. This is a version-bound evidence reference, not a promise
of permanent download availability or a recommendation to install that revision.

This proves native Mac execution, not the customer's complete Hermes memory route.
For example, the pinned session-commit tests check response/session/task identifiers,
not completed extraction followed by fresh-session recall. The nominal account
isolation file mainly checks health/search counters; it is not denied cross-owner
access proof. Map assertions to requirements instead of accepting test names or
green job labels. Growth/tail retrieval, owner boundaries, durable recovery and
customer watchdog coverage still need applicable evidence below.

### When detailed reports require authorization

A 401 from an artifact endpoint is an access gap, not a failed test or absent Mac
support. Use an existing authorized read-only connection, or obtain an evidence
copy from an authorized reviewer/publisher. Do not repeatedly retry anonymous
downloads, share credentials, bypass access controls or require a new customer
GitHub account solely when an authorized evidence-copy route is available.

Retain the original repository, run/job, commit, artifact identifier and digest,
plus retrieval/review attribution. Verify copied bytes against the published digest
when available. Separate direct artifact inspection from an attributed summary;
a digest proves byte identity, not coverage. Keep credentials, owner data and
unreviewed raw logs out of shared summaries.

In the existing private progress record, map each required behavior to applicable
release and host evidence. Name partial coverage and exact missing proof. Prepare
only the uncovered host checks using an existing supported procedure, with expected
results, isolated data, provider/request/time limits and stop conditions. The
[bundled memory check](#bundled-memory-check) is that procedure for growth/tail,
distinct sources and restart. For anything else without one, name the specific gap;
do not invent a runner or claim the requirements below are themselves a complete
tested procedure. This research
does not authorize live/provider tests, upgrades, history replay or resumed paused work.

## Release evidence and bounded host acceptance

The release maintainer owns the complete implementation regression suite. Reuse
version-bound release evidence instead of rebuilding that suite for each customer.
The setup agent must still verify the actual installed combination and host route.
Record release proof and host proof separately; neither substitutes for the other.

Required release proof covers these behaviors through native write, index and
retrieval paths, not a helper-only simulation:

- **Growth and tail recall:** grow natural-text sources beyond the effective embedding
  input limit, then retrieve a distinctive late fact. Preserve full canonical bytes;
  do not silently truncate input or accept a successful embedding as retrieval proof.
  If the runtime uses sections, verify coverage, source mapping and invalidation of
  old sections after changes. Include growing directory summaries, not just files.
- **Distinct results and scope:** two matching canonical sources remain discoverable
  at a result limit of two. Hidden sections must not crowd out a source or leak as
  user-facing results. Verify intended-owner access and denied cross-owner access
  through the supported agent routes. Names and URI prefixes are not access controls.
  Check the service's authentication mode first. An OpenViking server without a root
  key runs in development mode: every caller that can reach it is an administrator
  and names its own account and user in request headers, so owner separation is only
  a naming convention and the denied cross-owner check fails. Include one request
  that names another owner's account. Real separation needs a root key and one user
  key per owner.
  To set up per-owner keys on OpenViking (tested with 0.4.21), with the owner's
  approval:
  1. Back up the server config and the data folder, and pause any memory watchdog.
  2. In the server config, set `server.root_api_key` to a long random value and
     `encryption.api_key_hashing.enabled` to `true`, so the server stores Argon2id
     hashes instead of user keys. Treat the config as a credential file:
     owner-only permissions, never shown, kept out of ordinary backups.
  3. The owner restarts the memory service while no assistant is working. A
     request without a key now returns 401.
  4. With the root key, register each profile's account:
     `POST /api/v1/admin/accounts` with
     `{"account_id": "<account>", "admin_user_id": "<admin>"}`. The reply's
     `result.user_key` is an admin key for that account: store it with the root
     key, not in a profile. Then add the assistant as a limited user:
     `POST /api/v1/admin/accounts/<account>/users` with
     `{"user_id": "<user>", "role": "user"}`, where `<user>` is the user name the
     profile's memories already use, often `default`. That reply's
     `result.user_key` is the assistant's key. Memories already in the account
     stay as they were. The `default` account exists as soon as keys are on, so
     its first call returns 409: only add its user.
  5. Write each assistant key to its profile's `.env` as `OPENVIKING_API_KEY`,
     changing only that line and never showing the value. The owner restarts the
     Hermes services.
  6. Run the separation check below.
  A server that already holds plain-text keys converts them to hashes at its next
  start once hashing is on, and the keys keep working. Each request then runs one
  Argon2id check: OpenViking 0.4.21 keeps no cache of checked keys, and one check
  took about 70 ms on a desktop processor. At normal assistant volume this is small.
  To check separation on the host, first ask the owner to approve this sentence:
  "Each assistant uses its own memory key, without showing it, to try to open
  another assistant's memories, and the memory service should refuse. Nothing is
  created, changed or deleted." Then:
  1. Check that every profile has its own `OPENVIKING_API_KEY` and that no two
     profiles share one. Compare SHA-256 hashes and never print a value. A
     missing key, a shared key or the server's root key fails the check for those
     profiles.
  2. When an account has more than one user, use one user's key to list another
     user's memories (`GET /api/v1/fs/ls?uri=viking://user/<other user>/memories`).
     Expect 403.
  3. With the same key, send another profile's account and user in the
     `X-OpenViking-Account` and `X-OpenViking-User` headers and list memories
     again. Expect the same result as without the headers: the server takes the
     identity from the key.
  Record status codes and entry counts, not memory text. Any other owner's entry
  in a result fails the check; stop and tell the owner in plain words.
- **Interruption and failure:** exercise native lock contention, interrupted indexing
  and process restart in isolation. Track the same durable work identifiers through
  recovery, preserve source bytes, and detect stale/orphaned work. Failed or unfinished
  indexing must not become a successful save. Record bounded retry and recovery
  limits; do not promise indefinite retries or automatic recovery not demonstrated.

On the actual host, start with the ordinary save-and-recall check in steps 1 and 2
on the existing installed route, under applicable owner/provider authority. Use
supported native operations and existing controls, not a new runner. Broader growth,
scope and recovery proof remains required for full acceptance, but is not a
prerequisite for this first check unless a concrete safety dependency requires it.
Name that dependency and its owner rather than blocking on general missing coverage.
Distinguish enforced limits from proposed or observed limits; do not claim a caller
deadline caps internal provider calls or cancels server work. Missing consent or a
necessary safety control still blocks the affected operation.

Run these checks independently; preserve each check's evidence and limits:

1. Verify installed versions/hashes, effective provider/model bindings, private
   service access and the intended owner/profile route. Record evidence that the
   active process loaded the selected revision; changed files alone do not prove
   this. If that evidence is unavailable, retain the version-attribution gap and
   identify whether it prevents safe execution or only limits attribution. Do not
   restart working sessions just to strengthen attribution for the first check.
2. Save an authorized new useful fact or decision through the real agent memory
   route once. Match the session/task/account evidence and observe within a recorded
   request budget and deadline. Recognized queued/running states permit continued
   observation, not resubmission. Stop on failure, unknown/malformed state, identity
   mismatch or exhausted limits. A timeout/disconnect can leave server work running;
   retain identifiers, report an uncertain write outcome and never blindly replay it.
   Verify completed indexing and the actual canonical memory contents. Then verify
   recall in a fresh Hermes conversation without supplying the answer in its prompt,
   and retain the retrieved source reference. That recall chat is an ordinary
   conversation: if the memory provider syncs primary chats, its transcript is stored
   in the owner's memory and may be extracted. Check the installed provider; in the
   reviewed Hermes OpenViking plugin, only cron, subagent and flush contexts skip
   writes, and a session-list tag does not change that. Include this in the same
   owner approval as the model use, ask a real useful question, and inspect what
   extraction wrote afterward. Remove the chat only with explicit owner approval,
   through the provider's native delete. Report the model and account from the
   session record: a fresh chat uses the profile's configured model, not the
   operator's current one. A fresh CLI search alone proves only
   service retrieval, not fresh-Hermes recall. Submission, `.done`, empty queues and
   HTTP 200 are not completion. A legitimate extraction skip is not a demonstrated
   new save; do not force duplicate memories to obtain a pass.
3. Run the [bundled memory check](#bundled-memory-check) for growth/tail,
   distinct sources and restart, and the scope check above, which only reads. Do
   not put synthetic fixtures into the owner's real memory. Reuse recent evidence
   from the same installed versions where still applicable.
4. Verify the installed watchdog and its authorized schedule/destination below.
   Keep historical failures visible and distinguish them from newly submitted work.

Do not kill a production service to repeat interruption tests. Reuse applicable
release proof and verify the host's documented recovery binding without disruption;
a missing binding remains unverified. Missing test support, provider consent or
budget is a blocker, not permission to skip a required check or broaden billing.

### Bundled memory check

[`scripts/memory_check.py`](../scripts/memory_check.py) runs three checks on a
throwaway OpenViking server started from the installed `openviking-server`, with
its own data folder and loopback port, both removed afterwards. It never opens the
owner's memory or the running service. Embeddings go to the embedding service in
the server config through a local proxy that stops at a hard request cap, 400 by
default. A local stub replaces the summary model, so no chat model is called. It
needs Python 3, and every embedding service in the config needs an `api_base`.
If the config leaves it to the provider's default, pass `--config` a private copy
(mode 600) that holds only the `embedding` section with the provider's documented
address added, and delete the copy after the run.

1. Run `python3 scripts/memory_check.py --plan`, adding `--config` and `--server`
   when the defaults do not fit. It starts nothing and shows the input limit, the
   test sizes, the request cap and `package`: whether the server's installed
   OpenViking matches its install record. Use the `--server` the live service
   runs, or the result describes a different install. If `package` lists changed,
   missing or extra files, the install is not stock: the fixes below assume stock
   files. Report the files, explain what each change does and let the owner decide
   before changing settings. To test a fix for a changed install, copy the whole
   install, change only the candidate files in the copy, confirm the copy differs
   from live only by those files, and run the check with
   `--server "<copy>/bin/python -m openviking_cli.server_bootstrap"`. Change the
   live install only after the copy passes with no rejected requests. Prefer
   reverting only the files behind the problem: other local changes can be
   safeguards the owner relies on.
2. Ask the owner to approve, in plain words: "I'll test your memory service on a
   separate, throwaway copy. It uses your embedding service for up to 400
   requests, calls no chat model and doesn't touch your memories." For a paid
   embedding service, add the cost: each request carries at most the input limit
   in tokens.
3. Run it without `--plan`. Exit 0 means every check passed, 1 means a check
   failed and 2 means it could not finish; the JSON names the reason. A request
   the embedding service rejects fails the check it ran in. On a desktop a run
   took 1 to 5 minutes and up to 300 requests. `--time-limit` stops new checks
   but lets a running one finish, so give your own command timeout at least 5
   minutes more. A stopped run still removes its throwaway server and folder.
   Record the JSON summary; it holds no memory text.

What each check proves:

- `long_memory`: a memory grows to three times the embedder's input limit. At
  each size both copies must be indexed, and the newest fact, written last, must
  raise the search score above a control copy that has a plain sentence in its
  place. A gain of exactly 0 means the fact was never indexed.
- `two_sources`: a long and a short memory on one topic both come back when two
  results are allowed.
- `restart`: the server is killed right after a write. After a restart the memory
  must be indexed and keep every written byte.

Lock contention is not covered: reuse release proof or record it as a gap.

#### Rejected embedding requests

The JSON then shows `embedding_errors` above 0, `first_rejection` and a hint. On a
stock package it usually means `embedding.max_input_tokens` lets OpenViking send
more text than the embedding service accepts. OpenViking estimates about 4
characters per token;
code, numbers and some languages use more tokens per character. The effect on the
owner's memory: a new memory the service rejects is never searchable, and a
rejected update keeps the previous version in the index, so search finds the
memory by outdated text. A service restart repairs neither.

Offer this fix before the choices below:

1. Find the embedding model's documented input limit and start about a quarter
   below it.
2. Run the check with `--max-input-tokens <value>`. It changes only the throwaway
   server. Lower the value until no request is rejected. If requests are still
   rejected at a low value, the limit is not the cause: stop and check `package`.
   In one changed install, the adapter sent full text with cutting turned off and
   used the limit as the model's context size, so a lower value rejected more.
3. With the owner's approval, set `embedding.max_input_tokens` to that value in
   the server config and restart the service.
4. Re-index every memory folder the assistant's key can reach, including peer
   memory folders, one at a time: stock `POST /api/v1/content/reindex` with body
   `{"uri": "<memory folder>", "mode": "vectors_only"}`. This sends every memory
   in each folder to the embedding service again, so state the counts and any
   cost first. Track each task to completion; a timed-out request is not a
   failure to resubmit. Then confirm the memories rejected before can be found,
   not only that the tasks finished.
5. Run the check again without `--max-input-tokens`.

Long memories are then searchable by their start. Facts past the limit are still
missed; see the known result below.

Measured in October 2026 on stock 0.4.21, with an embedding service that rejected
inputs over 6,000 characters and an input limit of 2048: guide 0.41.0 reported a
false `long_memory` pass from outdated index entries, and this version fails it.
With `--max-input-tokens 1400` nothing was rejected, and `two_sources` and
`restart` passed. A rejected memory stayed unsearchable after a restart with the
lower limit and became searchable after the reindex call.

Known result, checked in October 2026: stock OpenViking 0.4.21 and 0.5.2.1 pass
`two_sources` and `restart` but fail `long_memory` past the input limit. They
embed only the start of each memory file, so search cannot find a fact past that
point; within the limit the check passes. On a long-running setup, memory files
that collect facts over time can grow past the limit. Fix rejected requests first,
as above. Then tell the owner in plain words and offer the choices: accept it as a
recorded exception, to revisit when a release indexes whole memory files; use an
embedding model with a larger input limit, which moves the point where facts are
lost, then run the check again; or wait for an upstream fix. When the owner
accepts the exception, record the row as verified with that limit and the owner's
decision. Do not patch the installed package as part of onboarding.

## Required watchdog behavior

Use or adapt an existing script-only monitor and native scheduler. No chat model,
new agent or second monitoring service is required. Account for real search's
embedding use/cost. Read back the job's profile/environment, endpoint, identity,
schedule, timezone and approved failure destination; test the actual scheduled
execution context, not only an interactive shell with different settings.

The monitor must check health and actual search, plus failed/cancelled/stalled saves,
messages not uploaded within the bound, commit submissions without a confirmed task,
and installed-version/patch drift.
Require exact task-to-session and owner/account matching. An unknown state, missing
identity, inaccessible task, malformed receipt, clock anomaly or exhausted checking
budget is **unverified**, not healthy. Scope server task listings explicitly: a
process cache or requester-only view is not an all-owner inventory.

Separate message upload from extraction commit. A conversation that is open or
below its commit threshold is normal however long it stays quiet, so receipt age
alone is not a fault. Alert when any queued message has not reached the memory
server within one hour (or the approved bound), with one stable line per
conversation. A conversation that ended without a commit or a recorded skip is
also a fault; if the selected monitor cannot detect it, record that coverage gap.

Uploads are ordered per conversation: one upload with an unknown outcome, such as
a client timeout, holds every later message. The server may already have stored
it, so never resend it blindly. Compare its message or tool-call identifiers with
the server session, send only messages that are absent, keep the original payload
and record the result. This is a separately authorized repair, not a routine retry.

Bound discovery, file/body sizes and total request time. Retained legacy receipts
need an explicit classification, not blind replay or deletion. Preserve task IDs,
failure history and unknown submission outcomes. Report service availability and
save health separately so working search cannot hide failed saves.

Use the selected monitor's isolated negative checks for failure, stalled work, an
hour-old queued message, unknown state and drift, plus a quiet open conversation
that must not alert. Do not corrupt production receipts to test alerts. Verify
an authorized alert and recovery message at the exact destination. A script result
or scheduler exit alone does not prove delivery. Keep delivery unverified when
permission or destination access is missing; do not send an unapproved test message.

## Updates and resumed onboarding

Follow [maintenance](maintenance.md) before updates. Back up affected state durably,
coordinate every writer and client auto-start path, and retain independent access
before stopping the service that carries the coordinating chat. Idle counters alone
are not a maintenance fence. Confirm code/data compatibility before rollback; after
new-format writes, preserve new data and use the documented repair-forward path
rather than blindly restoring old code or an older data snapshot.

After service, adapter, embedding or compatibility-patch changes, detect drift and
revalidate affected acceptance evidence. An embedding change needs a separately
rebuilt and verified index. Do not silently rebaseline hashes to make checks pass.
A failed historical save needs separately scoped reconciliation: inspect its exact
account, task and indexed outcome before any replay. Reinstalling does not recover it.

When adopting this guide revision, reopen only the memory/watchdog proof that no
longer meets these requirements, plus any actually affected dependency. Preserve
valid login, identity, team, file and other baseline evidence. Reconcile the new
baseline fingerprint in the existing private progress record; do not reset setup
or lower the denominator. A working installation can have unresolved save alerts;
report that limit instead of claiming the full baseline is complete.
If an older audit finding has a later verified repair receipt, retain that repair
as completed. Do not reopen it merely because separate memory coverage is still missing.
Record a successful ordinary save/recall check separately from full memory acceptance.
Retain existing save and recall evidence in the private progress record; distinguish
owner-confirmed results from directly inspected evidence. Do not repeat a successful
check merely to populate paperwork. Keep broader unverified requirements visible and
do not mark the whole memory row complete from this first check alone.
