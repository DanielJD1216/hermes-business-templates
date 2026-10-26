# T3 Code setup prompt

Use this prompt after the [role preparation procedure](role-setup.md) has produced
the approved EA, CTO and Engineer profiles. The owner installs T3 Code on the agent
host from its [install guide](https://github.com/pingdotgg/t3code/blob/main/docs/user/install.md),
signs in one built-in T3 agent and pastes the prompt below into a new T3 thread.
That built-in agent performs the setup, because Hermes is not connected to T3 yet.

Before the owner pastes it, give them the private folder you use for setup records.
The prompt asks the T3 agent to save its setup record there, so you can read it
directly. When the T3 agent finishes, read that record and its verified, pending
and UNKNOWN matrix, then update the `T3 Code development team` baseline row from
that evidence. The T3 agent's summary or a provider entry alone is not verification.

The prompt carries its own working rules and approval gates. Pasting it does not
grant authority beyond what the owner approves in that thread. Keep pairing codes,
tokens and other credentials out of the setup record.

```text
Help me connect my existing Hermes agents to T3 Code using a persistent server and Tailscale.

My goal:
Use T3 as the interface for my existing Hermes profiles, retaining their identities, tools, skills, memory, credentials, and model providers. Tasks should keep running when I quit the client app or lose its connection, provided the server machine stays running and online. If I want phone access, connect the mobile app and/or mobile browser to that same environment using the procedure in section 15.

Inspect my environment first. Do not assume my usernames, paths, versions, profile names, ports, or operating system.
This is a reusable setup procedure. Discover my installation and preferences; do not copy another user's model choices, machine-specific fixes, or diagnostic results as my configuration. Later troubleshooting and custom enforcement steps are conditional, not prerequisites for every setup.

1. Discover and verify
- Identify the client machine, server machine, installed T3 version, and Hermes version.
- For phone access, identify the phone OS and native T3 app version separately from the mobile browser and server versions. Verify compatibility and the actual pairing form; do not assume every client uses the same fields.
- For a custom installation, record the running executable, source/build revision and relevant hashes as well as displayed/API versions. A release directory name or version label alone does not prove which build is running.
- List my Hermes profiles and map their display names to actual profile names. Check whether my primary agent uses the default profile.
- Determine whether T3 is currently SSH launcher-managed or independently managed.
- Check the installed T3 version's documented support for persistent services and Local ACP command providers.
- Check Hermes ACP support and run the profile-specific ACP dependency/import check.
- Identify which ACP agent `hermes acp` runs in the installed Hermes version. From Hermes v0.22.5 it is the gateway-backed agent (`acp_adapter/gateway_server.py`): it attaches each T3 conversation to the profile's Hermes gateway runtime and starts that runtime if none is running. Changes made to the older in-process adapter (`acp_adapter/server.py`) do nothing there, even when their own tests pass.
- Inspect existing Tailscale configuration without disrupting other services.

2. Establish persistent hosting
- If needed, migrate T3 to its supported independently managed service.
- Choose hosting for the actual server OS and installed build. Inspect supported service methods on Linux, macOS, native Windows, or WSL as applicable; do not prescribe systemd, Windows configuration files, or WSL commands universally. Verify support before offering platform-specific commands; report unsupported methods and mark unverified support UNKNOWN.
- Preserve the existing T3 data directory, threads, projects, credentials, and settings.
- Never allow two T3 servers to use the same data directory simultaneously.
- Connect the client over Tailscale using a supported connection method that does not own or stop the server.
- Keep access private to my tailnet. Preserve existing Tailscale Serve routes; choose an unused port if needed.
- Explain that server-host shutdown, sleep, or loss of connectivity can interrupt server-side work. Include WSL lifecycle and Windows resource limits only when WSL is actually the host. Client disconnection and server shutdown are separate failure cases.

3. Connect my existing Hermes profiles
- Add one Local ACP command provider per profile on the SERVER environment.
- Use the verified absolute path to the Hermes executable.
- Supply arguments as separate literal rows:
  -p
  <verified-profile-name>
  acp
- Verify the syntax against my installed Hermes version.
- Use existing profile configuration and credentials; do not copy secrets into chat.
- Do not silently substitute native Codex or Claude for Hermes, even when they use the same underlying model.
- Keep active Hermes sessions, and any previous orchestration tool's sessions, running. Adding providers starts new sessions; it does not migrate running conversations.
- On gateway-backed Hermes, a gateway restart interrupts running T3 Hermes turns. Restart it only when T3 work is idle.

4. Verify reasoning controls
- Check whether my installed Hermes ACP agent advertises a per-conversation reasoning option (a `reasoning_effort` session config option). The gateway-backed agent in stock Hermes v0.22.5 advertises none, so T3 shows no Reasoning selector for Hermes. Check the installed version, because upstream may add it.
- Without the option, a conversation's effort can still be changed by typing `/reasoning <level>` in that Hermes thread. The gateway applies it to that conversation only, and `/reasoning reset` returns it to the profile default. `--global` changes the profile default and needs my approval. New conversations and delegated tasks use the profile default.
- Distinguish model selection, reasoning effort, edit-approval mode, and profile defaults.
- If the option is absent, inspect the actual adapter and T3 capability handling before proposing a fix.
- Never switch the thread to native Codex just to obtain its reasoning selector.
- If a patch is necessary, prepare and test it in an isolated checkout, on the ACP agent the installed version actually runs. Preserve unrelated local changes.
- The patch must keep overrides conversation-local, preserve profile defaults, survive session reloads and model changes, reject invalid or unsafe mid-turn changes, and avoid changing providers.
- Clearly distinguish requested reasoning effort from what the model/provider actually supports or sends.
- Record the requested T3 option, advertised ACP capability, runtime override, safe native launch/request metadata, and persisted session settings separately. A model's self-description or a composer label is not runtime proof.
- If session records show a different effort during a turn, inspect when those records were written. A constructor/default snapshot can precede a conversation override. Compare the installed resolver and adapter behavior with safe launch evidence and post-turn session metadata before diagnosing a mismatch. Do not expose private reasoning or secrets while tracing it.
- Save a reviewable patch, original-file backups, and rollback instructions. Explain how Hermes updates may affect it.
- Do not assume a config-validator warning proves a setting is ignored: verify the runtime code and behavior.

5. Handle discovery and UI caching
- Confirm Settings is scoped to the server environment, not the client machine.
- Inspect T3's live provider catalog to confirm which options it received.
- T3 also keeps each provider's last discovery on disk. One inspected v0.1.2 build writes `caches/<provider-instance>.json` in its data directory (`~/.t3` by default). Each model's `capabilities.optionDescriptors` there lists the options T3 accepts when it launches a task.
- Distinguish "Refresh provider status" from "Update all."
- Check the installed version's caching behavior. One inspected T3 v0.1.1 build cached successful ACP discovery for 15 minutes, and older live-session options could override refreshed discovery; treat this as a diagnostic lead to verify locally, not a universal timeout.
- A blank new-thread screen may not launch a new ACP process. If necessary, use a disposable new Hermes conversation with:
  "Reply ready. Do not run tools or change settings."
- Verify the selector appears in the conversation's model-options menu. Do not claim success from an ACP import check alone.

6. Test persistence and isolation
- Use a disposable task with timestamped progress.
- Record the T3 server PID, start time, task identity, and relevant worker identity.
- Quit and reopen the client, then verify the same server and task continued.
- Obtain user confirmation or independently observable evidence of the actual client quit/reopen interval. A heartbeat log alone proves worker continuity, not that the client was closed. Automatic reconnection after a server restart is a separate test with a new server PID; do not present it as quit/reopen persistence.
- Test client network loss separately if authorized; do not infer it from the quit/reopen test.
- Test that one conversation's reasoning changes do not alter other agents.
- If I want orchestration, separately verify Hermes-to-Hermes delegation through T3. Do not assume multiple provider entries reproduce every feature of a previous orchestration tool.

7. Register all agents and establish orchestration

Discover my actual Hermes profiles before configuring providers. Map each bot's display name to its profile directory; the primary bot may use the "default" profile. Do not assume other people's profile names match mine.

Guide me through adding every missing profile:
- Open T3 Settings → Providers.
- Select the SERVER environment in the environment dropdown at the top. Do not configure these entries on the client machine.
- Add provider → Local ACP command.
- Choose a recognizable display name, such as "Hermes CTO."
- Set Executable to the verified absolute Hermes executable path on the server.
- Add three separate argument rows:
  -p
  <actual-profile-name>
  acp
- Preserve existing entries and avoid duplicates.

If you can perform this through supported authenticated tools, do so within my authorization. Otherwise provide exact UI steps. Explain any access limitation; do not modify T3's database directly to bypass it.

Validate each provider:
- Confirm it appears in T3's live provider catalog.
- Run the profile-specific ACP check.
- Verify a disposable conversation starts with the correct Hermes profile and model.
- If new options are missing, inspect both discovery caching and older live-session configuration.
- Explain exactly where "Refresh provider status" is: the circular arrows beside "Checked…" at the top-right of the Providers page.
- A fresh conversation may need its first message before the ACP process starts and publishes its options.
- Do not confuse "Default" approval mode with default reasoning effort.

Explain the orchestration structure:
- A provider entry selects a Hermes profile; it is not itself a running worker.
- Separate conversations or delegated tasks can use the same profile. "Engineer #1" and "Engineer #2" do not require separate profiles unless they need different persistent configuration.
- Sessions using the same profile can share profile-level memory, skills, credentials, and other state. Separate conversations do not guarantee full isolation.
- Adding providers does not automatically reproduce a previous orchestration tool's coordination behavior or terminal layout.

Ask which profile should coordinate the work; do not assume a permanent hierarchy. Allow different profiles to coordinate different projects.

Establish model choices before testing delegation:
- Ask for or reuse my explicit choices of profile, model provider, exact model variant/context window and reasoning effort. Do not copy someone else's models or profile mappings.
- Distinguish the Hermes profile from its underlying model provider. A different profile or provider does not necessarily mean a different model.
- Verify each exact selection in the live catalog. Distinguish catalog availability, successful inference and actual large-context qualification; a [1m] label or a short reply does not prove a 1M-token request works.
- Save the approved defaults and verify fresh sessions. Explain that explicit delegation arguments can override profile defaults on stock T3.
- Track each configuration layer separately: saved Hermes defaults, ACP session overrides, T3 thread choices, typed-alias targets (if an alias patch is installed), optional guard rules, and temporary exceptions. Updating a profile default does not automatically update an alias, guard rule, or existing conversation override.
- Before changing defaults, identify which layers should follow the new choice. Update only the authorized layers and preserve unrelated profiles. Verify saved values with the installed config loader/resolver, aliases with the installed expander, and guard behavior with its policy resolver before spending inference on a fresh-session check. Report configuration-only verification separately from an actual model response.
- For independent adversarial review, use a fresh child with the brief and artifact to review. Give it criteria and evidence, not instructions to agree with the implementer. Different models help diversify review but do not guarantee independence; shared memory and supplied context can still bias it.
- Create a new delegated task for each review round, with a distinct stable request ID and the brief, artifact, prior findings/responses and unresolved objections. Continuing the old review child's conversation does not provide a fresh review. Verify the review model differs from the actual implementation task's model, not just the coordinator's current selection.

Then run a small, explicitly authorized orchestration test:
- Start with a coordinator using Hermes.
- Delegate harmless tasks through T3's app-owned delegation tools to two configured Hermes profiles.
- Discover the exact provider-instance IDs, model IDs, and reasoning options from T3's live catalog. If a Hermes provider lists no reasoning option, omit `reasoning_effort` from its delegation options. T3 refuses an option the agent does not advertise ("Unknown option reasoning_effort; supported options: ..."), and the destination profile's default effort applies.
- Explicitly select the intended Hermes provider for each worker. Never silently substitute native Codex or Claude.
- Verify each worker receives the intended profile, model, and supported options.
- Verify the coordinator receives the results and can track task status.
- Keep test work isolated from active projects. Use separate worktrees when workers will edit overlapping code.
- Verify persistence during client quit/reopen separately from delegation.
- Leave any previous orchestration tool's sessions alone until their active work finishes.

Report separately:
1. Profiles registered.
2. Individual Hermes conversations verified.
3. Reasoning controls verified (selector, typed /reasoning or profile defaults).
4. Hermes-to-Hermes delegation verified.
5. Client-disconnection persistence verified.
6. Remaining differences from the previous orchestration tool.

Do not declare the migration complete merely because all provider entries appear.

8. Expose Hermes / commands and skills in T3

Inspect the installed versions before changing anything. A working command menu in the Hermes terminal or desktop UI does not prove those commands are exposed through ACP.

Distinguish:
- T3's own composer commands.
- Built-in commands implemented by the Hermes ACP adapter.
- Hermes skills exposed as provider slash commands.
- Any separate $ skill menu supported by this T3 version.

Discover and validate:
- On gateway-backed Hermes (v0.22.5 and later), T3's / menu lists only the adapter's built-in commands: /help, /model, /tools, /context, /reset, /compress, /steer, /queue, /usage, /status, /version, /title, /undo and /retry. Hermes skills are not listed. A typed `/<skill-name> <task>` still goes to the gateway, which runs the installed skill. Other Hermes commands, such as `/reasoning`, also run there or are refused with a reason. Unrecognized commands reach the model as ordinary text.
- Check `skills.external_dirs` in each profile. In Hermes v0.22.5, when two or more entries each point directly at one skill's own folder, those skills all get the name `.`, none of their typed commands load, and the log shows `Skill name collision for '.'` ([issue #88064](https://github.com/NousResearch/hermes-agent/issues/88064)). A single such entry still loads; the failure starts with the second. Unless the installed version fixes this, point one entry at a folder that holds the skill folders, or give each profile its own folder of symbolic links to its selected skill folders. Both layouts load on stock v0.22.5 (tested on Linux).
- Inspect ACP available-command notifications and T3's handling of them.
- Discover skills using Hermes' existing profile/project/platform-aware scanner, respecting disabled skills and built-in command collisions.
- Do not copy one profile's skill list to every profile or execute skill bodies just to populate the menu.
- Check actual invocation as well as autocomplete. Selecting a skill must load its real instructions through the existing Hermes loader. Each load records a skill use, and the skill curator marks skills stale or archived by their last use. A script that loads every skill makes all of them look recently used, so verify through real invocations.
- Do not claim every Hermes terminal command works through ACP. Identify supported commands and remaining gaps.

If a compatibility patch is needed:
- Put it on the ACP agent the installed version runs. A skill-menu patch for the older in-process adapter does nothing on gateway-backed Hermes.
- Prepare it in an isolated checkout, preserve unrelated changes, follow repository instructions and test it before installation.
- Keep skill discovery profile-scoped. Preserve past conversation history and the original user invocation.
- Queue skill requests correctly when a turn is running; do not redirect an unexpanded invocation into active work.
- Return a useful error for an explicitly requested unavailable skill. Preserve existing behavior for unrelated commands.
- Check version-specific autocomplete limits and provide a verified fallback, such as /skill <name>, only if that fallback is implemented.
- Save the patch, backups, hashes, test evidence and rollback instructions.

Guide me through verification:
- Select the intended Hermes provider on the SERVER environment and start a fresh conversation.
- Send the supported Provider /help command or another harmless initialization message so the ACP session publishes its commands.
- Without a skill-menu patch, expect no skill suggestions: type the full `/<skill-name> <harmless task>` for a skill actually installed and enabled in that profile, and verify that its instructions ran. With a menu patch, a prefix of that skill's name should suggest it, and only if the skill exists and is enabled. Repeat the check for one skill from each skill folder the profile uses, including every `skills.external_dirs` entry.
- Verify it appears in the correct menu and execute a harmless skill task.
- If T3 says "No matching command," trace discovery, cached session state and UI handling before asking me to refresh repeatedly.
- Document text-only or attachment limitations. Do not claim success based only on an import check or protocol advertisement.

9. Route work to a role and verify real delegation

Stock Hermes has no typed-alias parser. A typed @BotName reaches the coordinator model as ordinary text, and the model may then call T3's delegate_task tool, so routing is model-mediated. Default to plain-language requests, such as "Ask CTO to <task>", and verify the task receipt. An alias patch written for the older in-process adapter does nothing on gateway-backed Hermes (v0.22.5 and later). Implement exact alias parsing only if I want it, on the ACP agent the installed version runs, as a maintained local patch. Neither way adds a native bot autocomplete menu. Native autocomplete is a separate T3 client feature and may require a custom build; do not silently replace my client.

Keep these behaviors distinct:
- A T3 @thread reference attaches context; it does not automatically message that thread.
- A typed @BotName alias requests a NEW delegated task using a configured Hermes profile.
- Messaging an existing conversation is a separate, explicit action.

Inspect existing support first. If I choose an alias patch:
- Discover exact provider-instance IDs from the live T3 catalog and create aliases only for registered profiles. Do not copy another person's provider IDs or invent missing entries.
- Install alias configuration for each intended Hermes coordinator profile, including the default profile when applicable.
- Use one leading standalone alias followed by a task, such as @CTO <task>. Match case-insensitively, reject unknown aliases and empty tasks, and document supported aliases.
- Preserve ordinary mid-sentence mentions, email addresses, paths, quoted examples and T3 context references. Document any text-only limitation.
- Keep processing inside the correct profile/session scope and queue requests safely during active turns. Do not mutate prior conversation context.
- Explain that prompt-based routing is model-mediated: exact alias parsing does not guarantee the model will make the correct tool calls. Validate receipts and behavior.

Require the coordinator to:
- Verify the exact target provider supports child tasks before dispatch.
- Resolve the intended model and reasoning options from the live catalog. Use my approved destination-profile defaults unless I explicitly request an override. Do not silently inherit the coordinator's model. Put the actual options in the tool arguments, not just the task prompt; report unsupported choices instead of substituting them.
- Use T3's app-owned delegate_task tool with the exact Hermes provider instance. Retain taskId and use a stable idempotency key for retries of the same dispatch where supported.
- Use injected T3 MCP tools, or the documented ACP MCP transport fallback when available. Do not substitute a shell-launched Hermes process.
- Create a child task, not an ordinary top-level conversation, unless I explicitly request a new top-level conversation.
- Pass the concrete task brief and relevant references. Do not assume a child inherits the full parent conversation. Do not send unrelated conversation history.
- Show the actual provider, model/options and task receipt. Return the real child result when it completes. Never claim delivery from prose alone or create duplicate work while waiting.
- Avoid recursive delegation unless requested. Use T3-supported worktree isolation for workers editing overlapping code.

Run a small, explicitly authorized end-to-end test:
- Start a NEW conversation explicitly using a Hermes coordinator, such as my verified primary profile.
- Send a self-contained request, replacing CTO with a registered role:
  Ask CTO to reply "hello from CTO." Coordinator: show the delegated task receipt and return the child's response.
- With an alias patch, also test the alias form: @CTO Reply "hello from CTO."
- Verify a new child-task card, real tool receipt, target provider-instance ID, model/options, completed child response and result delivery to the coordinator.
- A response saying "I am CTO" does not prove routing happened. Verify durable task records when accessible.
- Native Codex can also delegate to a Hermes child. Report that as cross-provider delegation, not proof that the Hermes alias parser ran.
- Do not rely only on the model name or icon to establish the runtime. Inspect the thread/provider configuration where possible.
- Avoid "review this design" as a test unless an actual design is supplied. An empty workspace or missing artifact is not an alias-routing failure.
- Do not ask me to repeat a test already supported by adequate evidence.

Report / command discovery, / skill execution, @ handling (plain text or alias patch), actual delegation and client UI verification separately. List unsupported profiles, command types or attachment workflows explicitly.

10. Choose delegation enforcement explicitly

A standard Hermes ACP setup does not require a custom T3 build. Explain these two choices before changing the server:
- Stock T3: coordinator instructions, approved destination defaults and verification of every task receipt. This avoids a custom server but remains model-mediated; it cannot guarantee every delegation follows the instructions.
- Optional custom T3 server guard: validation at the delegate_task boundary with an explicit choice of model defaults or model locks, while rejecting same-model reviews before a child starts. This changes the SERVER runtime, not merely Hermes configuration. A server-only patch may leave the client app unchanged, but client/server compatibility must be tested. It introduces build, update and rollback maintenance.

Do not describe a custom guard as a built-in T3 feature. Inspect the installed version for supported upstream equivalents first. If a custom build is necessary, explain its exact scope and obtain my choice before implementing it; keep standard setup available without it. A prompt alone does not distribute a patch: request or locate the actual reviewed patch and compatible source revision, or explicitly scope a new implementation. Do not assume another user's local artifact paths are available.

If I choose enforced delegation:
- Keep the policy operator-owned. Discover actual provider-instance IDs and model IDs; configure my approved selections rather than hardcoding another user's defaults.
- A guard that adds a reasoning option to every launch needs each target Hermes provider to advertise that option. Otherwise T3 refuses every guarded launch before it starts ("Unknown option reasoning_effort; supported options: ..."). Check each target's discovered options after every Hermes update, and omit reasoning from targets whose installed version does not advertise it.
- Choose the model-selection rule separately from the independent-review rule. If I want "use this setup when I request it," configure destination models/efforts as defaults: fill omitted fields, honor explicit per-task model and effort choices individually, and leave saved profile defaults unchanged. Keep provider-instance selection explicit and validate the selected model/options against the live catalog; never silently fall back. Use hard locks only when I explicitly want conflicting choices refused.
- Where the compatible custom patch supports it, `targetSelection: "defaults"` enables per-task selections; `"locked"` or an omitted field retains strict behavior. Verify this in the actual installed resolver. A structured target is not proof of a fresh human approval: defaults mode authorizes coordinators to select per task, and their instructions must follow my request. Do not claim the guard understands natural-language approval. Do not relax independent-review checks or other task permissions when enabling overrides.
- Require a declared review to identify the actual implementation task. Verify ownership, its recorded model, completed result and absence of pending child work. Do not compare only against the coordinator's current model.
- Compare underlying model identities across providers and context-window aliases using a verified mapping. Unknown identity must be reported and refused rather than guessed.
- Reject missing source results and known provider-error results. A task marked completed can still contain an error; distinguish transport completion from successful work. Document any heuristic error detection instead of claiming it catches every failure.
- Preserve idempotency for accepted dispatch retries. Verify the returned provider, model and reasoning match the intended selection; retain the receipt.
- State bypasses honestly: a guard on delegate_task does not automatically govern provider-native subagents, ordinary top-level threads, or reviews mislabeled as general work. It does not infer artifact authorship or remove shared-profile memory.
- Inspect how the adapter handles stalls. A wait timeout usually limits the parent's wait and does not cancel the worker. Never silently replace a failed reviewer with the implementer's model or launch duplicates while an earlier attempt is active.

Prepare and validate separately from activation:
- Work in an isolated checkout of the compatible server revision. Preserve unrelated edits and the live installation.
- Test the selected rule: omitted settings use destination defaults; explicit allowed model/effort choices reach the dispatch and receipt unchanged in defaults mode; strict mode still refuses conflicts. Verify unsupported and duplicate options, unavailable models, same-model aliases across providers, unknown review identities, invalid/unowned source tasks, incomplete/error results, valid diverse pairs and retry behavior. Test the service boundary, not only a standalone helper. Where catalog descriptors are missing, report validation limits instead of claiming support was proven.
- Build the server and start it with a temporary data directory and unused loopback port. Never run a test server against live userdata. Stop only the process captured at test launch.
- Run a disposable implementation/review pair using the approved distinct models, explicit reasoning and a self-contained task. Verify actual task records and both results. A test on stock T3 proves the chosen pair works; it does not prove the custom guard is active.
- Save the patch, policy, source revision, build artifacts, checks and rollback instructions. Report PREPARED and ACTIVE separately.
- Before activation, explain the concrete service changes and interruption risk. Use the authorized maintenance window after active work settles. Preserve the existing data directory, credentials, listener and Tailscale routes; ensure only one server owns that data directory.
- Record the approved restart count, exact candidate, baseline hashes and activation status. Check all T3 work for idleness immediately before the switch. If this thread itself prevents idleness, use a bounded activation helper outside the service being restarted, with a durable one-attempt marker and a supported way to resume verification afterward.
- A wait that expires while work is active is DEFERRED, not an activation or a failed model test. Do not stop work to force idleness. Preserve the unused approval and restart allowance; revalidate scope, expiry and the live baseline before requeueing a bounded wait. Do not ask for the same unchanged approval again merely because it was deferred. A consumed restart allowance or expanded scope requires any additional authorization that is actually needed.
- After activation, verify the running custom revision and loaded policy, refusal cases, a valid pair, client reconnection and persistence. Do not declare enforcement active just because a patched build passed tests.
- Verify runtime identity and the policy actually loaded by the process, not only the edited file on disk. Inspect whether policy reload is supported or startup-only; do not promise that editing a file or refreshing provider status reloads the guard.
- Roll back by stopping the custom service in an idle window and restoring the saved original runtime/service configuration against the same current data directory. Do not overwrite newer conversations with an old database backup.

11. Preserve the setup through updates and document rollback

- Save one setup record with installed versions, verified paths, service ownership, connection method, profile/provider mappings, alias syntax (if any), patch application order and verification evidence. Keep secrets out of it.
- Save that record as a file on the server, in the folder my main Hermes assistant uses for setup records. Ask me for that folder if you do not know it, and report the file's absolute path so my assistant can verify the result without me copying the report.
- Distinguish user configuration, Hermes ACP patches and any custom T3 server patch. Explain what is expected to survive updates and what must be rechecked. Stock T3 updates may replace the custom runtime; verify policy enforcement after every update rather than assuming it survived.
- Do not blindly reapply old patches to an updated Hermes or T3 build. Check compatibility, upstream support and test the current installation.
- After every Hermes update, check which ACP agent the new version runs. Then re-verify the options T3 discovers for each Hermes provider, the / command list, typed skill execution and one real delegated task. A patch on an adapter path the new version no longer runs fails silently, and its own tests still pass.
- Preserve original-file backups and hashes. When patches modify the same files, document the reverse order for rollback.
- Explain how to disable optional typed routing without restarting services if the implementation supports it.
- Do not restart existing agents merely to load a patch; verify using fresh disposable sessions and let active work finish.
- Finish with a verified/pending/UNKNOWN matrix covering all original checks plus / skills, @ routing, approved model defaults, cross-model review and optional guard preparation/activation. If phone access was requested, report network reachability, browser pairing, native-app pairing and mobile reconnect separately. Distinguish automated tests, live protocol checks, actual delegated-task records and user-confirmed UI behavior.
- Keep preparation records immutable where they serve as approval evidence, and maintain a separate current status/result record. Preserve earlier attempts and receipts when a check is deferred, fails, or is retried; do not let a preparation-time flag or an old success report masquerade as current state.

12. Diagnose provider stalls without masking them

- Separate resource pressure, authentication/quota errors, model latency, transport buffering, and task-runner failures. A successful greeting does not prove a tool-using preflight works.
- Check current memory pressure and provider errors before blaming the host. Stop live retries on an explicit account limit; record the provider-reported reset without inventing an automatic retry.
- If resource pressure is present, identify the actual host limits and current workers. Do not kill sessions merely because they are old or assume a host restart will restore every service. Prepare resource changes separately from the approved idle maintenance window.
- Use bounded disposable checks: a greeting, one harmless tool call, explicit repository checks, then the full preflight. Keep the model, effort, prompt, and injected tool catalog recorded for each comparison.
- When permitted, trace metadata along provider subprocess → Hermes → ACP → T3. Record timestamps, request identity, actual model/effort arguments, stream mode, statuses, and cancellation; never log credentials or private reasoning text.
- Verify the operative watchdog in code and logs. A first-event timeout, a non-streaming completion deadline, and a streaming inactivity timeout are different. Incoming thinking events establish transport activity, not a completed answer.
- Inspect whether Hermes disables streaming for external-process providers even when the installed plugin supports it. Do not remove that safety default globally. If necessary, implement an explicit provider capability, preserve other providers and user streaming-disable settings, and test tools, usage, cancellation, and signed replay in isolation.
- A process-local streaming override is diagnostic evidence, not an installed fix. Verify the installed change in a fresh process without the override; let existing agents finish normally.
- Keep requested reasoning intact. A High comparison that succeeds does not qualify a requested Max configuration. If Max still exceeds the test bound after the transport fix, report it as unresolved; do not silently downgrade or declare readiness.
- Treat High, XHigh, Max and other efforts as separate comparisons. An explicitly chosen alternative can be used for a new diagnostic; that does not change saved defaults or a benchmark's required settings. One completed XHigh trial does not establish that Max never works, that XHigh always works, or that the full context capacity is qualified.
- A successful check on one profile or in a setup thread does not establish another profile or project's readiness. Preserve the exact provider route and execution context when reporting what was verified.
- Direct ACP checks are not T3 delegation receipts. After they pass, verify the intended profile through actual T3 delegation. Filesystem access with an explicit path is not proof of the correct T3 workspace binding.
- Give each authorized disposable test a bounded deadline, for example ten minutes if agreed, measured from task acceptance. A tool wait timeout does not necessarily cancel work. Retain the actual task receipt, wait asynchronously, and at the deadline check status and cancel only that owned diagnostic if still incomplete. Close its deadline on completion; do not automatically retry or cancel unrelated work. Keep a diagnostic deadline separate from a benchmark timer.

13. Handle deliberate model locks and temporary exceptions

A policy rejection before launch is not an inference stall. First determine whether the user wants defaults with explicit overrides or intentionally locked routes. Do not create repeated one-shot exceptions just to emulate defaults. If defaults mode is approved and active, send the supported explicit target on each new task; changing a task target then needs no new policy edit or restart. Startup-only policy mode changes still require activation. The following exception procedure applies when the user chooses to retain hard locks.

- Read the rejected request and the policy actually loaded by the running server. Identify the exact parent thread, request ID, role, prompt, provider instance, model and reasoning. Check whether an earlier exception belongs to another thread, a completed attempt, different settings, or an expired window.
- Preserve the profile's normal defaults and unrelated guard rules. Under intentionally locked routing, prepare an exact, expiring exception for a one-off preflight tied to its parent and request. Do not widen a deliberate lock without authorization. An operator-approved switch to defaults mode is a separate durable policy choice, not a temporary exception. Keep the existing model-identity and independent-review checks intact.
- An earlier setup-thread exception does not automatically authorize the benchmark or project thread. Do not bypass the restriction by changing MCP sessions, using another task tool, relabeling a review as general work, or claiming approval in the task text. Record genuine user authorization and the concrete approved scope.
- If the user changes effort for this diagnostic, make the request options and brief agree. Preserve the original brief as evidence and explicitly state any diagnostic-only override. Do not silently alter the benchmark protocol or reuse the diagnostic as a benchmark session.
- Preserve the rejected attempt, and distinguish retrying an accepted dispatch from starting a new attempt. Use the same stable clientRequestId for recovery of the same dispatch; use a fresh ID only for an authorized new attempt after checking prior work is terminal.
- Before any dispatch, check saved receipts and durable child-thread/run records across MCP sessions. A generic command-receipts table may be incomplete. An older interrupted child may already use a seemingly rejected ID. If a matching child exists, recover its state and receipt rather than launching a duplicate. If duplication cannot be ruled out, report the gap before dispatch.
- Test the exact exception offline, including refusal for a different parent, request ID, prompt, role, effort or expired time. Confirm ordinary routing and independent-review restrictions still hold. Keep preparation, activation and successful inference as separate results.
- Apply only the approved candidate through the supported reload or authorized idle restart. Recheck expiry and the live baseline; do not silently widen the exception or overwrite newer changes. An expired exception must not be treated as current authorization.
- Dispatch from the intended parent. Sending instructions to another thread is an explicit action requiring authorization; an attached thread reference alone grants no permission to message it. If authorized, send the prepared instruction once with a stable message ID, retain that receipt, and have that coordinator deduplicate and submit the exact approved task.
- Save the actual delegation receipt immediately. Verify provider, model and options, then promptly capture allowlisted runtime metadata while the relevant worker exists. A completed task containing a quota or provider-error response is not a passed preflight.
- On expiry or rollback, preserve later legitimate policy edits. Remove only the owned exception when possible; restore a full snapshot only if it is still the correct baseline. Reloading or restarting for rollback remains subject to the applicable authorization and idle requirement.

14. Verify file location and workspace binding before real project work

- Explain which environment owns the project. With a remote server, its agents normally work on the server filesystem; a client app's presence does not imply local project files or automatic file synchronization. Verify the actual path and mounts instead of inferring from the machine name.
- Folder pickers may hide dot-directories. Check version-specific hidden-folder controls or direct-path entry before concluding that a directory is missing. Verify the path on the selected server environment; do not move a user's agent data just to make it visible in a picker.
- Record the T3 project/workspace binding, Hermes process cwd, native provider subprocess cwd and explicitly accessed repository path separately. A successful `cd` or `git -C <repo>` only proves that command used the path; it does not change T3's workspace binding. A provider may use a separate internal scratch directory.
- Select a supported workspace/isolation strategy before starting work. For delegated tasks, inspect the parent's binding and use the supported delegation isolation options. A nested standalone repository is not automatically a registered project or a worktree of its parent directory. If the intended repository needs a separate project, reuse or register that exact path through supported tools/UI. Create an ordinary top-level execution thread only when explicitly requested, bind it before starting it, and retain any coordinating thread separately. Do not substitute a top-level thread for a requested subagent or use it to evade a delegation guard. A model-policy change alone does not fix workspace binding.
- Verify repository HEAD and working-tree state with non-mutating commands; use `git --no-optional-locks -C <repo> status --short` where appropriate. Do not assume uncommitted changes were copied to a child worktree.
- A read-only preflight, correct repository checks and successful inference do not authorize benchmark prompt reading/submission, tests, builds, edits, or starting the benchmark clock. Report remaining workspace and execution-lifecycle gaps before actual project work, and retain any explicit start boundary.

15. Connect mobile clients over Tailscale, if requested

Connect the phone to the existing server environment. Do not create a second server, duplicate Hermes providers on the phone, or copy provider credentials to it. Project files and execution remain on the verified server filesystem.

Discover the route before pairing:
- Confirm the phone is connected to the intended tailnet and permitted to reach the server. Inspect the current server listener and Tailscale Serve/reverse-proxy mapping without changing them.
- Record the exact client-facing scheme, DNS name and port. A backend listening on loopback may be reached through a different HTTPS port; do not substitute the Tailscale IP plus the backend port or send the phone a localhost address.
- Preserve existing Serve routes. Do not reset routes, enable public Funnel, broaden the listener, or run a routing helper that rewrites configuration just to add a phone.
- Distinguish direct tailnet pairing from T3 Connect account/relay access. Follow the selected connection method; a working private route does not require switching to a different service. Check mobile notification support separately rather than promising background push from pairing alone.

Create a fresh pairing credential when the user is ready:
- Use the installed build's supported Connections UI, authenticated API, or pairing CLI. Inspect help/source first; commands such as `t3 pair` or `t3 auth pairing create` are version-dependent examples. Use the verified server executable, live environment/data directory and reachable base URL. Give an exact command labeled "run on server" when appropriate.
- Generate the credential without restarting T3 or interrupting agents. Do not reuse an old boot-log token, edit auth database rows, launch another server, or issue a permanent bearer credential as a workaround.
- Record the actual expiry and timezone from issuance; do not assume a universal 15-minute lifetime. Treat the code and complete pairing URL as credentials, even when the token is in a URL fragment. Keep them out of this reusable prompt, shared setup notes and diagnostic logs.
- Pair the mobile browser and native app separately. Each consumes its own one-time credential, even on the same phone. Do not test or open the user's pairing link yourself, and do not reuse a code already consumed by the browser in the app. Established clients should reconnect with their saved session, not the original one-time code.

Give exact instructions for the verified client:
- On the phone, enable Tailscale before opening the private address. For browser pairing, open the fresh complete pairing URL in the intended browser. Loading a login page proves reachability, not successful authorization or a live app connection.
- In the native app, locate its environment settings and Add environment screen; one inspected build uses Settings → Environments. If it has separate Address and Code fields, use the full reachable server origin in Address and the raw fresh token in Code.
- If the installed app supports a pairing URL or QR scan, preserve the complete URL, including its token. In builds verified to accept a full pairing URL in Address, leave Code empty. Do not guess that the Code field accepts a URL or ask the user to try conflicting field combinations without checking the parser.
- Use a placeholder such as `https://<server-dns-name>:<https-port>/pair#token=<fresh-token>` only to explain the verified format. Do not copy another user's hostname, port or credential, and do not imply every build uses this exact URL shape.

Diagnose errors at the correct layer:
- A timeout, DNS failure or TLS error requires checking the phone's tailnet connection, access rules and exact route. Avoid consuming a pairing token while testing basic reachability.
- "Invalid credential" requires checking expiry, prior consumption, revocation and the intended server. Inspect non-secret pairing/session metadata before issuing another code. A session labeled with the phone's name may belong to its browser; that alone does not prove native-app pairing.
- "Pairing URL is missing its token" indicates that the parser did not receive a usable token; it does not by itself prove expiry or a bad server credential. Check the actual app build, Address/Code values, QR parsing and whether copying or redirecting removed the fragment. A browser may remove the token after pairing, so its current address bar is not necessarily a reusable pairing link.
- Preserve the exact error text and separate confirmed causes from hypotheses. Do not restart the server or regenerate tokens repeatedly to mask an input-format problem.

Verify and document:
- Confirm the intended server environment, existing threads/projects and configured Hermes providers appear in each requested client. Verify a live connection; cached content alone is insufficient. Use a harmless disposable message only within the authorized test scope, and verify the response uses the intended Hermes provider.
- Report browser and native-app success separately. If the last native-app attempt still errors or lacks confirmation, mark it UNKNOWN rather than treating browser success as proof.
- Check reopening the paired mobile client without a new code. Test switching between Wi-Fi and cellular only if requested/authorized, with Tailscale connected, and report it separately from server-task persistence and desktop quit/reopen tests.
- Document how to remove the new mobile connection and revoke only its session or unused pairing link while preserving other clients and the running server.

Working rules:
- Do not stop active work, restart services, update software, or migrate data without explaining the concrete impact and obtaining any needed authorization.
- Reuse authorization already given for the same concrete action and scope. Prepare a reviewable change before asking for a new approval, explain why it is needed, and distinguish unused approval from an already-consumed one-shot action.
- Proceed autonomously with read-only inspection, isolated implementation, and tests.
- Follow repository instructions and supported installation methods.
- Never merely remove a managed marker or background an existing server process.
- Mark unverified claims UNKNOWN.
- Give exact commands with "run on client" or "run on server," and exact UI instructions.
- Finish with verified results, remaining limitations, update maintenance, and rollback steps.
```
