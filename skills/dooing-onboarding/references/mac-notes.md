# Mac implementation notes

These are troubleshooting evidence and limits, not a mandatory installation
script. The agent must inspect the actual host and current official support.
Neither the user's device name nor another customer's success proves compatibility.

## Discover rather than hardcode

- Distinguish Mac host from Mac client; inspect actual macOS version, architecture,
  interpreter and Rosetta state. Keep host work moving if a client is unavailable.
- A missing PATH command is not absence. Look for supported GUI app locations and
  the existing Hermes managed runtime before proposing duplicate installations.
- Do not invoke an Apple developer-tools shim just to get a Python version. Use an
  already verified interpreter for read-only discovery. Actual dependency setup is
  a separately reviewed write, not permission silently acquired during discovery.
- Choose a supported isolated service interpreter if needed. Do not change the
  main assistant's Python, model or login to fit the memory service.
- Use native macOS service management and preserve the current recovery route.
  Do not paste Linux systemd, `/proc` or firewall commands into a Mac setup.
- Keep owner-run commands to one physical line when remote clipboard transport
  corrupts line breaks. U+2028 is not a shell newline. Prefer direct execution of
  a verified script to nested `runpy` launchers that can lose `__main__` underscores.

## Narrow evidence from a native ARM64 trial

The following observations are useful, not certification of the entire setup:

- Ollama 0.40.3 loaded `embeddinggemma:300m` and returned one finite 768-dimensional
  vector for synthetic text with `truncate:false` and a 2048-token setting.
- An isolated macOS 27.0.1 / CPython 3.14.7 environment loaded OpenViking 0.4.21,
  its native vector engine and Rust binding, and the repaired service modules.
  The import check verified 1,414 service hashes. No server or provider instance
  was started by that check, and no end-to-end memory write/recall was established.
- LiteLLM 1.91.1 metadata excludes Python 3.14. A resolver nevertheless initially
  selected it. Independent checking selected 1.83.7 within the existing dependency
  constraint. Verify wheel tags AND Requires-Python; resolver exit 0 is not proof.
- The installed optional SDK emitted a Pydantic V1/Python 3.14 warning. Imports
  passed, but that does not establish API compatibility of every backend. Test
  the selected actual provider route before accepting a production runtime.
- urllib3 2.8.0 creates an IPv6 socket on import only to probe loopback binding.
  A blanket socket audit can record this as a failed import although the library
  handles the denial. Trace the caller first. In the offline test only, reporting
  IPv6 unavailable skips that optional probe; socket denial and OS network denial
  remain active. This does not test IPv6 or authorize relaxing live network policy.

The [validation prerelease](https://github.com/DanielJD1216/hermes-business-templates/releases/tag/mac-runtime-validation-20261013)
contains the exact diagnostic kit, source/repair provenance and limitations. It is
not the customer entrypoint, not an installer for a live service, and not a required
runtime lock for every Mac. Never copy its example paths, owner approvals or assumed
host state. Check whether a current upstream release already resolves a known issue
before selecting a historical repair. Preserve third-party license/source duties.

## Limits that still require a real decision or test

- The pinned OpenViking 0.4.21 distribution has separate ARM64 macOS 14+ and Intel
  macOS 15+ wheel tags. A tag is not full dependency/native/runtime acceptance.
  This trial does not establish Intel support or every OS/interpreter combination.
- Its reviewed existing-data migration guard uses Linux-specific primitives.
  Do not remove that guard, reset a store or invent Mac migration safety. Preserve
  existing data and report a migration blocker until a supported path is verified.
  This restriction does not by itself prevent a genuinely new empty Mac store.
- A default data folder being absent does not rule out a custom/remote store.
  Inspect relevant non-secret configuration and ownership before initialization.
- Model tags and documentation can disagree about context size. Verify actual
  bounded requests with truncation disabled; do not infer tokenizer limits from
  character counts or automatically increase a working budget.
- Alternative embedding models need compatibility and retrieval tests plus a
  separate rebuilt index. A larger multimodal model does not add image/audio
  support to an adapter that extracts and sends only text.
- After a restart, a Mac host without automatic login waits at its login window.
  The standard Parsec app cannot show that screen. Parsec's separate login-screen
  installer can, but it needs a wired network connection and FileVault turned off
  ([Parsec support](https://support.parsec.app/hc/en-us/articles/32381618319124-Access-Login-Screen-on-macOS)).
  Turning off FileVault removes disk encryption, so that is the owner's security
  decision. Otherwise, plan for someone to sign in at the host after a restart.
- Imports, authentication, service startup, memory write/recall, Slack delivery,
  private client access and recovery are separate checks. Complete only the gates
  observed on the intended host and approved scope; never claim all-Mac readiness.
