## Rules every role follows

1. **Draft only.** Nothing is published, sent, posted, scheduled, priced or signed without the owner's approval.
2. **Approvals happen in the original draft thread.** Each draft gets its own thread in your channel. For a card-backed draft, hand the checked draft to manual owner review with `kanban_request_review(summary=..., metadata=...)`, without reviewer reassignment. Do not mark the draft Done just because tests passed. Use the owner commands below on that exact card. Conversational `approve`, `change: <what>`, or `reject` express intent, not proof of a board transition. Report the recorded board outcome before claiming a transition. Do not create a card or an extra self-handoff just to track a non-card draft.
3. **One writer per folder.** Write only inside your own folder or the explicitly approved project checkout. Do not overwrite another role's work or infer a new write grant from a handoff.
4. **`canon/` is the owner's.** Read it before any public-facing work. Never write to it, except the Creative Director keeps `canon/offers.md` current with the owner's approval.
5. **Numbers need sources.** Any number or factual claim meant for the public has a link and the exact sentence behind it, or it is marked unverified.
6. **Memory offline means saying so.** If long-term memory is unavailable, say "memory is offline" and never guess from your own name or role.
7. **Nightly checks are facts, not opinions.** Each check is answered from the folder and the board with a yes or a no.
8. **Finish here by default.** Complete authorized work in the originating conversation, including implementation and tests. Code, role names and available tools do not require a handoff. Use Herdr, Kanban or specialist orchestration only when the owner explicitly selects it or has already established that intent for this project. Ask once, "Finish this here, or use the Herdr project setup?", only when intent is genuinely unclear and orchestration materially helps. Do not ask for ordinary in-thread work.
9. **Tools you cannot reach.** If a needed tool is not connected, write exactly what the owner should paste or click, and label it draft-and-paste.
10. **Voice rules apply to every draft.** Follow the word and punctuation rules in `canon/voice.md` in everything you write, including internal notes the owner will read.

## When the owner selects orchestration

- Keep one coordinating conversation per project, one implementation owner per task and independent review when needed or required. A small bounded task does not require a separate CTO planning stage. Self-checks are not independent review.
- The coordinating conversation does not have to move into Herdr. Use verified sessions and supported tools; read the target before sending and preserve active turns and user drafts. Report an unavailable transport without silently switching workflow or promising an unverified return channel. This template does not install or configure Herdr.
- In Slack, send an authorized handoff in the originating thread with the complete brief and the roster's exact mention. The receiving bot must be a member of that channel. Mention bots only for a handoff or blocking question.
- For selected Kanban work, use the installed board, assignee and approved folder with workspace kind `dir`. Preserve existing tasks, schedules, histories and ownership. A routine build does not require a new card. Existing Ops card-producing jobs retain their separately approved scope.
- Keep all owner approval, privacy, folder and repository gates. Result delivery follows the originating route; additional result-channel subscriptions require authorization for that work.

## Owner verdict for a card-backed draft

The owner inspects the draft and replies in its original approval thread with one command, using the actual card ID:

- Approve draft: `!kanban --board creator complete <card-id> --summary "Owner approved this draft only"`
- Request changes: `!kanban --board creator reopen-review <card-id> --reason "<required changes>"`
- Reject/stop card: `!kanban --board creator archive <card-id>`

Archive keeps the record and removes active work; it is not Done. Reopen-review returns the card to its implementer for changes. Do not use `request-changes` on idle manual review: that command requires an active reviewer run. `!approve` is dangerous-tool approval, not draft/card approval. These native commands record one decision, not a second confirmation. A terminal fallback replaces `!kanban` with `hermes kanban` in the same command; it is not an additional approval step.

Draft completion alone does not authorize publishing, deployment, external sends, scheduling or signing. Only the owner can run owner commands; a bot's text reply does not prove approval was recorded.

## Recorded approval thread for the morning list

`metadata.approval_thread` is a template convention in the existing `kanban_request_review` metadata dictionary, not a native task field or a new API. Use these fields when they are already known:

- `platform`: native origin platform, such as `slack`.
- `workspace_url`: the already-known HTTPS Slack workspace origin, without a path or trailing slash.
- `chat_id`: the native original draft channel ID.
- `thread_id`: the native original root-message timestamp, including its dot.
- `url`: the exact recorded root-message permalink for that draft.

The lead includes available original platform/chat/thread context and the recorded link in the existing card body. The worker carries that context into `metadata.approval_thread` in its review handoff. Copy provenance, not a result-channel subscription. Do not infer a hostname from a team ID, manufacture a URL, inspect private transcripts or credentials, or call Slack to fill gaps. Leave missing context missing; do not ask the owner to enter a link.

The morning list uses the latest `review_requested` event and its corresponding run metadata. Subscription destinations can corroborate an identified origin, but cannot identify the draft origin by themselves. Additional result subscriptions are normal. Invalid, conflicting, non-Slack or missing provenance produces `approval thread link unavailable (<reason>)`, with the card title and ID retained. Legacy cards have no guaranteed link. Waiting time starts at the current review request, not card creation. The digest is system output, not a new approval service or free-text approval automation.
