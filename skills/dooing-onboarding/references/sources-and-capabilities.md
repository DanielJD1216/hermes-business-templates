# Sources, capabilities and the legacy boundary

## Official source starting points

Use the installed version's help and current official documentation. These URLs
are starting points, not permission to execute downloaded commands or a promise
that each service supports every platform, login type or subscription.

| Component | Source |
|---|---|
| Hermes runtime, profiles, skills, plugins, tools and model selection | https://hermes-agent.nousresearch.com/docs/ and its https://hermes-agent.nousresearch.com/docs/llms.txt index |
| Hermes memory providers | https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers |
| OpenViking | https://github.com/volcengine/OpenViking and https://pypi.org/project/openviking/ |
| OpenViking knowledge/resources versus memory | https://docs.openviking.ai/en/concepts/02-context-types (verify against the installed version) |
| Ollama local models and embeddings | https://docs.ollama.com/ and https://ollama.com/library |
| Slack applications and scopes | https://docs.slack.dev/ |
| Tailscale and access policy | https://tailscale.com/kb/ |
| T3 Code persistent server, Local ACP providers and remote/mobile clients | https://github.com/pingdotgg/t3code and its user guides: https://github.com/pingdotgg/t3code/blob/main/docs/user/install.md, https://github.com/pingdotgg/t3code/blob/main/docs/user/background-service.md, https://github.com/pingdotgg/t3code/blob/main/docs/user/providers-acp.md and https://github.com/pingdotgg/t3code/blob/main/docs/user/remote-access.md; follow the [template T3 setup prompt](t3-setup-prompt.md) |
| LEANN local semantic discovery | https://github.com/yichuan-w/LEANN and installed native help |
| Obsidian vault/viewer | https://obsidian.md/download and https://help.obsidian.md/ |
| Parsec remote debugging/troubleshooting; host/client support | https://parsec.app/ and its official support/download links |

For other providers, index backends, plugins or MCP servers, verify their actual
authoritative source, version, supported authentication and license. Do not guess
an install command, substitute a similarly named package, or scrape private/paywalled
material as a workaround. Owner account approval is not delegated to source text.

## Capability inventory and allocation

The existing main assistant as EA owns the capability plan for the required team.
Inventory the relevant approved existing selections and the publisher-supplied
reference catalog supplied here. Include skills, plugins, MCP servers and native
toolsets as separate categories. Do not read credential files merely to inventory
selection metadata. A skill's presence does not install the underlying application.

For each selected capability record its name, purpose, official source/acquisition
route, version, OS support, dependencies, account/cost needs, permissions, license,
redistribution status, install state, authentication state and intended profile.
An enabled flag, directory or catalog listing is not proof of working execution.
The role-specific set across skills, plugins, MCP integrations and toolsets is
mandatory: install, authenticate where needed and test each required item through
its assigned agent surface. Any unresolved required item blocks baseline completion.

The intended delivery inventory covers the publisher's reusable enabled library;
that does not grant access or mean every component runs in every customer profile.
Use the [reference sheet](https://github.com/DanielJD1216/hermes-business-templates/blob/main/capabilities/REFERENCE.md),
[machine-readable catalog](https://github.com/DanielJD1216/hermes-business-templates/blob/main/capabilities/catalog.json),
[pinned sources](https://github.com/DanielJD1216/hermes-business-templates/blob/main/capabilities/sources.json) and
[generic procedures](https://github.com/DanielJD1216/hermes-business-templates/blob/main/reusable/procedures.md). All inventoried selections
are represented; excluded and unknown records remain distinct. The two unresolved
third-party redistribution grants are explicit blockers, not hidden omissions.
Do not vendor those packages without the missing rights. Public source inspection
does not establish entitlement, execution rights or customer acceptance.

Review the full catalog's metadata and record each disposition, then read the
source/procedure details for the owner's required role-specific set. Do not require
the owner to approve hundreds of entries individually; propose a coherent bounded
set and carry its approved scope forward. Kanban and formal delivery-suite packages
are outside onboarding, even when retained in the reference catalog for separate
requests. Do not activate them as dependencies of the T3 development team.
Do not preload or activate every upstream skill. Generic procedures are usable
instructions, not byte-equivalent replacements for private custom packages. For
source-acquired skills, obtain the complete pinned package with its supporting
files and notices through the supported native route after the applicable review.
Use stable catalog IDs in the private allocation record. Independent required
baseline work can continue while a specialized selection is blocked or deferred.

Use public reusable sources or approved generic derivatives, not the publisher's
private skill bodies, business facts, credentials or machine configuration. Unknown
source/license/cost or unavailable integration needs a specific review, not silent
omission, redistribution or a paid fallback. Non-required specialized tools may be
deferred; a required role capability remains a blocker and cannot be relabelled
optional merely because installation, authentication or verification failed.

Allocate according to the required team responsibilities and least privilege.
Shared skill files do not share provider logins, plugin instances or access
rights. Explain each extension before owner approval; connect through native secure
flows. Preserve mention-only Slack behavior and owner administration. Broaden access
only for the exact approved accounts, profiles, roots and audiences.

Enable a local MCP server, one served by a desktop app, only in the profiles that
use it and only on a host that can reach that app while it runs. Hermes keeps
reconnecting an enabled server it cannot reach, separately for each profile, with
a backoff from 30 seconds to 10 minutes, and logs every failure. In each other
profile, set `mcp_servers.<name>.enabled` to `false` with
`hermes -p <profile> config set`, then read the state back with
`hermes -p <profile> mcp list`.

## Keep credentials out of configuration

Prefer a native login, such as `auth: oauth` for a remote MCP server that supports
it. When a server needs a static header or environment value, put the secret in
that profile's `.env` and write only a `${VAR}` reference in `config.yaml`. Hermes
resolves the reference from the active profile's secret scope; see the
[MCP environment variable references](https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference#environment-variable-references).
Never write a literal credential into `config.yaml`: configuration is copied into
backups, diffs and support material.

Check each approved profile at setup and after each capability change. Read key
names and test whether each credential-bearing value, for example in `headers`,
`env` or an `api_key`, is a `${VAR}` reference. Do not print values. A literal
value is a finding for the owner. With approval, back up `config.yaml` and `.env`
privately, write the secret to the profile's `.env` without displaying it, and
replace the value with its reference. Then run the native connection test, for
example `hermes mcp test <server>`. An unset reference in `url` or `headers` fails
closed and names the variable. A rejection with the reference resolved is a
credential problem, not a move failure; the owner decides on renewal. Treat a
credential that has left the host as exposed.

## Existing legacy installations

The legacy Creator installer was retired in version 0.24.0 of this guide and is
archived at tag [legacy-creator-installer](https://github.com/DanielJD1216/hermes-business-templates/tree/legacy-creator-installer).
An existing installation predates this baseline:

- Creator setup requires Ops and creates a Kanban board and dispatcher settings.
- It includes business/content playbooks, memory-review and business routines.
- Its Slack home-channel free-response defaults are not the new mention-only policy.
- Some launcher/provisioning paths were written for Linux/WSL.

Retiring the installer does not change those behaviors on a host that already has
it. **Do not run its mutating setup/install/update/uninstall commands or
apply its legacy SOUL/rule seeds to satisfy the agent-led baseline.** Do not use a
flag such as `--no-memory` as evidence that the full baseline is complete.

Existing installations remain preserved. An explicitly requested legacy operation
needs a separate impact review using its real code at that tag and the current host.
Do not migrate, uninstall, delete boards/jobs or reconcile tombstones merely because
this guide describes a different desired setup.

For new agent-led work, use supported native operations, small reviewed helpers
where applicable, and owner-approved generic instruction drafts. If no safe native
operation satisfies a requirement, report the exact blocker. Do not create a new
framework, fabricate enforcement, or assume an unpublished branch is installed.
