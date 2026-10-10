# Where information belongs

| Information | Location | Access and maintenance |
|---|---|---|
| Stable identity | Intended profile's `SOUL.md` | Profile owner; existing main assistant is not replaced |
| Local rules and commands | Workspace or repo `AGENTS.md` | Read the file in the actual working directory; check native precedence |
| Private owner preferences | `USER.md` | Explicitly read only when relevant in an authorized private session |
| Business / offers / voice / brand | `canon/` | Owner-maintained; share only necessary facts |
| Verified project locations | `PROJECTS.md` and `.hbt-projects.json` | Local private indexes; not authority to start work |
| Repo source, tests, decisions | Existing approved project location | Preserve its instructions and Git state; one writer per checkout |
| Reusable procedure | `skills/project-onboarding/SKILL.md` | Read explicitly from this workspace; optional native skill registration |
| Deliverables and evidence | Relevant project folder | Link exact paths in the originating conversation |
| Credentials and runtime controls | Native profile config / secret store | Never canon, USER, indexes, or public templates |

Start project discovery with the known project name, this index, the selected
install record's projects location, and the conversation's already-supplied path.
Inspect exact candidate paths and instructions before asking for information again.
Do not crawl unrelated private directories or automatically clone a remote repo.

Filesystem search is sufficient. Local semantic search is optional, owner-installed
and manually indexed for approved roots only. It adds no scheduler, credentials,
private catalog or search service to this package. An index is not the source of truth.

## Optional native onboarding-skill adoption

Skills here are workspace files, not automatically added to a profile's skills list.
The minimal adoption uses native `skills.external_dirs`, not a new installer or a
copy of a live skills directory. It registers only the reviewed package directory.
Do this only after approval for the exact destination profile; default is the
existing main assistant, not permission to change every profile.

1. Resolve the intended profile home and this workspace's absolute path. Back up
   that profile's `config.yaml` and `SOUL.md` privately. Read the package's SKILL.md
   and helper first. Do not register the workspace root or its entire skills tree.
2. Through `terminal`, inspect `hermes -p default config get skills.external_dirs --json`
   and `hermes -p default skills list`. Review disabled/platform-disabled settings
   and existing same-name skills, including trusted project skills. A collision or
   disabled skill needs a decision, not deletion, enabling or force-overwrite.
3. Form the complete JSON list: preserve every existing entry in order and append
   the exact `skills/project-onboarding` directory once. If already present, skip
   the write. If the key is absent, use an empty starting list only after checking
   the profile config; a failed/unreadable config is not an empty list. Keep other
   profile-config writers paused during adoption: native `config set` replaces the
   list, it is not an atomic append. Re-read just before writing and stop on changes.
   With substituted real paths:

   ```bash
   # Example only: retain YOUR existing entries, not this placeholder.
   hermes -p default config set skills.external_dirs '["/existing/approved/root", "/absolute/business/skills/project-onboarding"]'
   ```

   Use the native command through `terminal`, never replace the whole config. Do
   not change `skills.create_dir`, disabled lists, other settings or SOUL.md.
4. Read back `skills.external_dirs` and compare the saved config: only that list
   should differ semantically, and SOUL.md must be byte-identical. Native YAML
   writing may change formatting; keep the private backup. In the intended profile,
   verify `skills_list` contains `project-onboarding`, then `skill_view` resolves
   to this exact package and can read `scripts/onboard.py`. Listing a same-name
   owner skill is not proof. Use a fresh session/catalog refresh if needed; do not
   start a model solely to test discovery. Registration does not start Herdr.

This is a live reference to the workspace package, not a pinned copy. Reviewed
template updates can change unchanged managed skill files; owner edits remain
preserved by workspace provenance. External roots are mutable when filesystem
permissions allow it, not a sandbox. To withdraw adoption, remove only this exact
entry from the current list with native `config set`, retaining later owner edits;
verify it is no longer the resolved source. Do not restore an old whole config or
delete the workspace. A moved/deleted workspace needs a reviewed path update.
