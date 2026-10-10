"""Unit tests for the installer and the Ops scripts. Standard library only.

Run from the repo root:  python3 -m unittest discover -s tests -v
(Uses Hermes's Python if PyYAML is missing: ~/.hermes/hermes-agent/venv/bin/python -m unittest ...)
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates" / "creator"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


hbt = load("hbt", ROOT / "installer" / "hbt.py")
watch = load("hbt_memory_watch", TPL / "roles" / "ops" / "scripts" / "hbt_memory_watch.py")


class TemplateShape(unittest.TestCase):
    def setUp(self):
        self.tpl = hbt.load_template("creator")

    def test_every_role_has_a_distribution_and_soul(self):
        for r in self.tpl.roles + self.tpl.desks:
            d = TPL / "roles" / r.key
            self.assertTrue((d / "distribution.yaml").is_file(), r.key)
            self.assertTrue((d / "SOUL.md").is_file(), r.key)

    def test_manifest_names_match_profile_names(self):
        import yaml
        for r in self.tpl.roles + self.tpl.desks:
            m = yaml.safe_load((TPL / "roles" / r.key / "distribution.yaml").read_text())
            self.assertEqual(m["name"], self.tpl.profile(r.key))

    def test_skills_are_namespaced_and_have_frontmatter(self):
        for skill in TPL.glob("roles/*/skills/*/SKILL.md"):
            role = skill.parts[-4]
            text = skill.read_text()
            self.assertTrue(text.startswith("---\n"), skill)
            m = re.search(r"^name: (\S+)$", text, re.M)
            self.assertIsNotNone(m, skill)
            self.assertEqual(m.group(1), skill.parent.name)
            # Ops playbooks are creator-ops-*; the lead's are named by workstream (creator-video-*, ...).
            self.assertTrue(m.group(1).startswith("creator-ops-" if role == "ops" else "creator-"), skill)
            if role != "ops":
                self.assertFalse(m.group(1).startswith("creator-ops-"), skill)
            self.assertIn("## Done when", text, skill)

    def test_job_skills_exist_in_ops(self):
        ops = self.tpl.ops
        for job in self.tpl.jobs:
            if job.get("skill"):
                self.assertTrue((TPL / "roles" / ops.key / "skills" / job["skill"] / "SKILL.md").is_file(), job["skill"])
            if job.get("script"):
                self.assertTrue((TPL / "roles" / ops.key / "scripts" / job["script"]).is_file(), job["script"])

    def test_no_em_or_en_dashes_or_private_names(self):
        # Owner-specific names live in a local, git-ignored .private-terms file (one per line).
        banned = ["\u2014", "\u2013", "DOO_MADE_CONTEXT"]
        extra = ROOT / ".private-terms"
        if extra.is_file():
            banned += [t.strip() for t in extra.read_text().splitlines() if t.strip() and not t.startswith("#")]
        public = [ROOT / "installer" / "hbt.py", ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "hbt"]
        for f in list(TPL.rglob("*")) + public:
            if f.is_file() and (f.suffix in {".md", ".yaml", ".py"} or f in public):
                text = f.read_text()
                for b in banned:
                    self.assertNotIn(b, text, f"{b!r} in {f}")

    def test_ops_is_always_selected(self):
        roles = hbt.select_roles(self.tpl, "cto")
        self.assertEqual({r.key for r in roles}, {"cto", "ops"})
        with self.assertRaises(SystemExit):
            hbt.select_roles(self.tpl, "cto,nope")

    def test_the_template_is_the_org_chart(self):
        """Q28: Creative Director, CTO and Engineer each get a Slack app; Ops has none; plain profile names."""
        keys = [r.key for r in self.tpl.roles]
        self.assertEqual(keys, ["creative-director", "cto", "engineer", "ops"])
        self.assertEqual([self.tpl.profile(k) for k in keys], keys)
        by = {r.key: r for r in self.tpl.roles}
        self.assertEqual(by["cto"].peers, ["engineer", "creative-director"])
        self.assertEqual(by["engineer"].peers, ["cto"])
        self.assertEqual(by["creative-director"].peers, ["cto"])  # v0.3: content hands build work to CTO
        self.assertFalse(by["engineer"].takes_cards)
        self.assertEqual([r.key for r in self.tpl.roles if r.builds], ["engineer"])
        self.assertNotIn("kanban", by["cto"].slack_toolsets)
        self.assertEqual(list(TPL.glob("roles/creative-director/skills/*/SKILL.md")), [])
        channels = [c for r in self.tpl.roles for c in r.channels]
        self.assertEqual(len(channels), len(set(channels)), "two bots answering in one channel would double-reply")


class DriftCheck(unittest.TestCase):
    """v0.3: hbt check finds the gaps that broke Daniel's own setup (2026-09-29)."""

    def setUp(self):
        self.tpl = hbt.load_template("creator")
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self._old = hbt.os.environ.get("HERMES_HOME")
        hbt.os.environ["HERMES_HOME"] = str(self.home)
        ids = {"creative-director": "U0CD00001", "cto": "U0CTO0001", "engineer": "U0ENG0001"}
        chans = {"media-video": "C1", "media-edit": "C2", "media-newsletter": "C3", "marketing-distribution": "C4",
                 "build-architect": "C5", "build-engineering": "C6"}
        self.rec = {"profiles": [self.tpl.profile(r.key) for r in self.tpl.roles], "bots": ids, "channels": chans,
                    "owner": "U0OWNER01", "workspace": str(self.home / "ws"), "jobs": []}
        for r in self.tpl.roles:
            prof = self.home / "profiles" / self.tpl.profile(r.key)
            (prof / "memories").mkdir(parents=True)
            (prof / "memories" / "USER.md").write_bytes(f"Synthetic {r.key} context\r\n".encode())
            (prof / "memories" / "MEMORY.md").write_bytes(b"Synthetic role memory\r\n\x00")
            src = TPL / "roles" / r.key / "skills"
            for f in src.rglob("*"):
                if f.is_file():
                    dst = prof / "skills" / f.relative_to(src)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(f.read_bytes())
            if r.kind == "ops":
                continue
            cfg, env = hbt.slack_settings(r, chans, "U0OWNER01", ids)
            (prof / ".env").write_text("".join(f"{k}={v}\n" for k, v in env.items()))
            slack = {k.split(".", 1)[1]: v for k, v in cfg.items()}
            (prof / "config.yaml").write_text(hbt.yaml.safe_dump({"slack": slack}))

        for parent in (self.home, self.home / "profiles" / "desk-sentinel"):
            (parent / "memories").mkdir(parents=True)
            (parent / "memories" / "USER.md").write_bytes(b"Synthetic excluded context\r\n")
        # A missing memory directory must stay absent too.
        (self.home / "profiles" / "desk-empty").mkdir()

    def tearDown(self):
        if self._old is None:
            hbt.os.environ.pop("HERMES_HOME", None)
        else:
            hbt.os.environ["HERMES_HOME"] = self._old
        self.tmp.cleanup()

    def memory_snapshot(self):
        roots = [self.home, *(self.home / "profiles").iterdir()]
        state = {}
        for root in roots:
            memory = root / "memories"
            for path in [memory, memory / "USER.md", memory / "MEMORY.md", *memory.rglob("*")]:
                state[str(path.relative_to(self.home))] = (
                    path.read_bytes() if path.is_file() else "directory" if path.is_dir() else None)
        return state

    def command(self, quiet=False):
        hbt.record_dir("creator").mkdir(parents=True, exist_ok=True)
        (hbt.record_dir("creator") / "record.json").write_text(hbt.json.dumps(self.rec))
        args = hbt.build_parser().parse_args(["check", "creator", "--offline"] + (["--quiet"] if quiet else []))
        before = self.memory_snapshot()
        out = []
        try:
            with patch.object(hbt, "say", out.append):
                self.assertEqual(args.func(args), 0)
        finally:
            self.assertEqual(self.memory_snapshot(), before)
        return out

    def gaps(self):
        before = self.memory_snapshot()
        try:
            gaps = hbt.check_gaps(self.tpl, self.rec, live=False)
        finally:
            self.assertEqual(self.memory_snapshot(), before)
        ordinary = self.command()
        expected = (f"{self.tpl.title} check: {len(gaps)} gap(s).\n" + "\n".join(f"- {g}" for g in gaps)
                    if gaps else f"{self.tpl.title} check: no gaps.")
        self.assertEqual(ordinary, [expected])
        quiet = self.command(quiet=True)
        self.assertIn(quiet, [ordinary, []] if gaps else [[]])
        self.assertEqual(self.command(quiet=True), [])
        self.assertEqual(self.memory_snapshot(), before)
        return gaps

    def test_a_fresh_install_has_no_gaps(self):
        self.assertEqual(self.gaps(), [])

    def test_every_peer_is_heard(self):
        """The live gap: CTO heard only Engineer, so a handoff from the Creative Director was ignored."""
        cfg, env = hbt.slack_settings(self.tpl.roles[1], {}, "U0OWNER01", self.rec["bots"])
        self.assertEqual(env["SLACK_ALLOWED_USERS"], "U0OWNER01,U0ENG0001,U0CD00001")
        (self.home / "profiles" / "cto" / ".env").write_text("SLACK_ALLOWED_USERS=U0OWNER01,U0ENG0001\n")
        self.assertIn("cto: ignores Slack messages from Creative Director. Fix: ./hbt update creator", self.gaps())

    def test_receivers_join_their_senders_channels(self):
        by = {r.key: r for r in self.tpl.roles}
        self.assertEqual(hbt.peer_channels(self.tpl, by["cto"]),
                         ["media-video", "media-edit", "media-newsletter", "marketing-distribution", "offers-optimization",
                          "build-engineering"])
        self.assertEqual(hbt.peer_channels(self.tpl, by["creative-director"]), ["build-architect"])
        self.assertEqual(hbt.peer_channels(self.tpl, by["ops"]), [])
        self.assertEqual(hbt.peer_channels(self.tpl, by["cto"], ["cto", "engineer", "ops"]), ["build-engineering"])

    def test_update_adds_jobs_the_template_gained(self):
        rec = {"jobs": [{"key": "morning-approvals"}, {"key": "nightly-review"}, {"key": "update-check"},
                        {"key": "comment-pull"}, {"key": "member-questions"}], "memory": {"enabled": False}}
        self.assertEqual(hbt.new_jobs(self.tpl, rec), [])  # retired jobs stay retired
        rec["memory"]["enabled"] = True
        self.assertEqual([j["key"] for j in hbt.new_jobs(self.tpl, rec)], ["memory-watchdog"])
        rec["jobs"].append({"key": "memory-watchdog"})
        self.assertEqual(hbt.new_jobs(self.tpl, rec), [])

    def test_bots_cannot_run_each_others_commands(self):
        prof = self.home / "profiles" / "cto"
        cfg = hbt.yaml.safe_load((prof / "config.yaml").read_text())
        del cfg["slack"]["group_allow_admin_from"]
        (prof / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
        self.assertIn("cto: other bots can run its commands (!approve, !restart). Fix: ./hbt update creator", self.gaps())

    def test_one_bot_without_user_memory_has_no_gap(self):
        (self.home / "profiles" / "engineer" / "memories" / "USER.md").unlink()
        self.assertEqual(self.gaps(), [])

    def test_all_role_user_memories_absent_has_no_gap(self):
        for role in self.tpl.roles:
            (self.home / "profiles" / role.key / "memories" / "USER.md").unlink()
        self.assertEqual(self.gaps(), [])

    def test_subset_ignores_uninstalled_roles_but_not_missing_profiles(self):
        import shutil
        self.rec["profiles"] = ["engineer", "ops"]
        for name in ("creative-director", "cto"):
            shutil.rmtree(self.home / "profiles" / name)
        self.assertEqual(self.gaps(), [])
        shutil.rmtree(self.home / "profiles" / "engineer")
        self.assertIn("engineer: profile is missing. Fix: ./hbt update creator", self.gaps())

    def test_drifted_copies_and_missing_sign_ins_are_found(self):
        (self.home / "profiles" / "cto" / "memories" / "USER.md").write_text("old positioning")

        (self.home / "profiles" / "cto" / "config.yaml").write_text(hbt.yaml.safe_dump(
            {"slack": {"allow_bots": "mentions", "strict_mention": True},
             "mcp_servers": {"vidiq": {"auth": "oauth"}, "malloy": {"auth": "oauth", "enabled": False}}}))
        gaps = "\n".join(self.gaps())
        self.assertNotIn("USER.md", gaps)

        self.assertIn("cto: vidiq is on but not signed in", gaps)
        self.assertNotIn("malloy", gaps)  # turned off, so not a gap

    def test_a_lost_sign_in_is_found(self):
        prof = self.home / "profiles" / "creative-director"
        cfg = hbt.yaml.safe_load((prof / "config.yaml").read_text())
        cfg["mcp_servers"] = {"vidiq": {"auth": "oauth"}}
        (prof / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
        (prof / "mcp-tokens").mkdir()
        (prof / "mcp-tokens" / "vidiq.json").write_text("{}")
        (prof / "logs").mkdir()
        log = prof / "logs" / "agent.log"
        log.write_text("2026-09-29 13:00:00,000 WARNING x: re-authenticate with `hermes mcp login vidiq`\n")
        old = (prof / "mcp-tokens" / "vidiq.json").stat().st_mtime - 60
        hbt.os.utime(prof / "mcp-tokens" / "vidiq.json", (old, old))
        self.assertIn("creative-director: vidiq lost its sign-in. Fix: hermes -p creative-director mcp login vidiq",
                      self.gaps())

    def test_failing_jobs_and_passed_offer_dates(self):
        cron = self.home / "profiles" / "ops" / "cron"
        cron.mkdir(parents=True)
        (cron / "jobs.json").write_text(hbt.json.dumps({"jobs": [{"id": "abc123def456", "last_status": "error"}]}))
        self.rec["jobs"] = [{"key": "nightly-review", "id": "abc123def456", "profile": "ops"}]
        canon = self.home / "ws" / "canon"
        canon.mkdir(parents=True)
        (canon / "offers.md").write_text("# Offers\n\n## Dates coming up\n\n- 2020-01-01 webinar\n- 2999-01-01 launch\n"
                                         "\n## Replaced decisions\n\n- 2019-05-05 old price\n")
        gaps = "\n".join(self.gaps())
        self.assertIn("ops: scheduled job nightly-review last run: error", gaps)
        self.assertIn("canon/offers.md: 2020-01-01 passed", gaps)
        self.assertNotIn("2999", gaps)
        self.assertNotIn("2019-05-05", gaps)  # replaced decisions are history, not deadlines

    def test_quiet_mode_posts_once_per_change(self):
        jobs = self.home / "profiles/ops/cron/jobs.json"
        jobs.parent.mkdir(parents=True)
        jobs.write_text(hbt.json.dumps({"jobs": [{"id": "abc123def456", "last_status": "error"}]}))
        self.rec["jobs"] = [{"key": "memory-watchdog", "id": "abc123def456", "profile": "ops"}]
        out = self.command(quiet=True)
        self.assertEqual(len(out), 1)
        self.assertIn("1 gap(s)", out[0])
        self.assertIn("ops: scheduled job memory-watchdog last run: error", out[0])
        self.assertEqual(self.command(quiet=True), [])
        jobs.write_text(hbt.json.dumps({"jobs": [{"id": "abc123def456", "last_status": "ok"}]}))
        self.assertEqual(self.command(quiet=True), [])
        self.assertEqual(self.gaps(), [])
        self.assertEqual(hbt.json.loads((hbt.record_dir("creator") / "check-state.json").read_bytes()), {})

    def test_obsolete_user_warning_cache_clears_without_memory_changes(self):
        old = ("The bots have different USER.md files, so they describe you differently. "
               "Fix: copy the one you want to every bot's memories/USER.md.")
        state = hbt.record_dir("creator") / "check-state.json"
        state.parent.mkdir(parents=True)
        state.write_text(hbt.json.dumps({"key": hbt.hashlib.sha256(old.encode()).hexdigest(),
                                         "posted": hbt._dt.date.today().isoformat()}))
        self.assertEqual(self.gaps(), [])
        self.assertEqual(state.read_bytes(), b"{}\n")



class Workspace(unittest.TestCase):
    def test_build_is_idempotent_and_keeps_owner_files(self):
        tpl = hbt.load_template("creator")
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            first = hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertTrue((ws / "canon" / "business.md").is_file())
            self.assertTrue((ws / "media" / "AGENTS.md").is_file())
            self.assertTrue((ws / "media" / "video" / "episodes" / "active").is_dir())
            (ws / "canon" / "business.md").write_text("OWNER EDIT")
            (ws / "media" / "video" / "topic-queue.md").write_text("OWNER QUEUE")
            (ws / "media" / "AGENTS.md").write_text("stale")
            second = hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertEqual((ws / "canon" / "business.md").read_text(), "OWNER EDIT")
            self.assertEqual((ws / "media" / "video" / "topic-queue.md").read_text(), "OWNER QUEUE")
            self.assertEqual((ws / "media" / "AGENTS.md").read_text(), "stale")
            self.assertTrue(all(a.startswith("retain owner/untracked") for a in second), second)
            self.assertGreater(len(first), len(second))

    def test_role_agents_lists_checks_and_roster(self):
        tpl = hbt.load_template("creator")
        cd = next(r for r in tpl.roles if r.key == "creative-director")
        text = hbt.render_role_agents(tpl, cd, tpl.roles, Path("/ws"), {"media-video": "C0ABCDEFG"})
        self.assertNotIn("Nightly checks", text)
        self.assertNotIn("Kanban board", text)
        self.assertIn("`engineer`", text)
        self.assertIn("C0ABCDEFG", text)

    def test_build_leads_see_mentions_and_the_projects_folder(self):
        """CTO hands off by @mention and by card into <projects>/<project>; both come from its AGENTS.md."""
        tpl = hbt.load_template("creator")
        cto = next(r for r in tpl.roles if r.key == "cto")
        text = hbt.render_role_agents(tpl, cto, tpl.roles, Path("/ws"), {"build-engineering": "C0ENG1234"},
                                      bots={"engineer": "U0ENG1234"}, projects="/srv/projects")
        self.assertIn("`<@U0ENG1234>`", text)
        self.assertIn("#build-engineering (C0ENG1234)", text)
        self.assertIn("`/srv/projects`", text)
        cd = next(r for r in tpl.roles if r.key == "creative-director")
        self.assertNotIn("Projects folder", hbt.render_role_agents(tpl, cd, tpl.roles, Path("/ws"), {}, projects="/p"))

    def test_dry_run_writes_nothing(self):
        tpl = hbt.load_template("creator")
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            acts = hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=True)
            self.assertTrue(acts)
            self.assertFalse(ws.exists())

    def test_agent_jobs_run_in_the_ops_folder(self):
        """Without --workdir a cron run never reads the Ops AGENTS.md (roster, board, rules)."""
        tpl = hbt.load_template("creator")
        ops = tpl.ops
        for job in tpl.jobs:
            args = hbt.job_args(tpl, job, ops, "slack:C1", Path("/ws/ops"))
            self.assertEqual(args[:3], ["cron", "create", job["schedule"]])
            if job.get("no_agent"):
                self.assertNotIn("--workdir", args)
            else:
                self.assertEqual(args[args.index("--workdir") + 1], "/ws/ops")
                self.assertTrue(args[args.index("--skill") + 1].startswith("creator-ops-"))


class Routes(unittest.TestCase):
    def test_deleted_profile_name_can_be_installed_again(self):
        """hermes profile install fails on a name Hermes marked deleted; hbt clears the marker and
        moves any leftover folder aside instead of deleting it."""
        import os
        with tempfile.TemporaryDirectory() as d:
            old = os.environ.get("HERMES_HOME")
            os.environ["HERMES_HOME"] = d
            try:
                profiles = Path(d) / "profiles"
                (profiles / ".deleted").mkdir(parents=True)
                (profiles / ".deleted" / "creator-video").write_text("deleted\n")
                (profiles / "creator-video").mkdir()
                (profiles / "creator-video" / "SOUL.md").write_text("half-made\n")
                self.assertFalse(hbt.profile_is_live("creator-video"))
                backups = Path(d) / "bk"
                hbt.clear_deleted_marker("creator-video", backups, dry=True)
                self.assertTrue((profiles / ".deleted" / "creator-video").exists())  # dry run changes nothing
                hbt.clear_deleted_marker("creator-video", backups, dry=False)
                self.assertFalse((profiles / ".deleted" / "creator-video").exists())
                self.assertFalse((profiles / "creator-video").exists())
                moved = list(backups.glob("deleted-profile-creator-video-*/SOUL.md"))
                self.assertEqual(len(moved), 1)
                hbt.clear_deleted_marker("creator-ops", backups, dry=False)  # no marker: no-op
            finally:
                if old is None:
                    os.environ.pop("HERMES_HOME", None)
                else:
                    os.environ["HERMES_HOME"] = old
    def test_merge_keeps_foreign_routes_and_is_idempotent(self):
        foreign = [{"name": "owner-route", "platform": "slack", "chat_id": "C1", "profile": "x"}]
        ours = [{"name": "hbt:creator:video", "platform": "slack", "chat_id": "C2", "profile": "creator-video"}]
        merged, added = hbt.merge_routes(foreign, ours)
        self.assertEqual(added, ["hbt:creator:video"])
        again, added2 = hbt.merge_routes(merged, ours)
        self.assertEqual(added2, [])
        self.assertEqual(len(again), 2)
        cleaned = hbt.remove_routes(again, {"hbt:creator:video", "owner-route"})
        self.assertEqual(cleaned, foreign)  # never removes a route without our prefix

    def test_config_edit_and_revert_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "config.yaml"
            original = "# owner comment\nmodel:\n  default: m\nkanban:\n  dispatch_in_gateway: false\n"
            cfg.write_text(original)
            routes = [{"name": "hbt:creator:ops", "platform": "slack", "chat_id": "C9", "profile": "creator-ops"}]
            ch = hbt.edit_main_config(cfg, routes, dispatch=True, dry=False, backup_dir=Path(d) / "bk")
            text = cfg.read_text()
            self.assertIn("# owner comment", text)
            self.assertIn("hbt:creator:ops", text)
            self.assertIn("dispatch_in_gateway: true", text)
            self.assertIn("review_dispatch: false", text)  # a role must never approve its own card
            hbt.revert_main_config(cfg, {"main_config": ch}, dry=False)
            import yaml
            self.assertEqual(yaml.safe_load(cfg.read_text()), yaml.safe_load(original))
            self.assertIn("# owner comment", cfg.read_text())

    def test_edit_keeps_every_untouched_line(self):
        """Adding routes must not reformat the owner's file: only the new lines may differ."""
        original = (
            "# owner comment\n"
            "model:\n  default: m\n"
            "skills:\n  external:\n    - one\n    - two\n"
            "long: 'a very long quoted value that goes well past eighty characters so line wrapping would show up here'\n"
            "kanban:\n  dispatch_in_gateway: false\n"
        )
        for text in (original, original.replace("    - one\n    - two\n", "  - one\n  - two\n")):
            with tempfile.TemporaryDirectory() as d:
                cfg = Path(d) / "config.yaml"
                cfg.write_text(text)
                routes = [{"name": "hbt:creator:ops", "platform": "slack", "chat_id": "C9", "profile": "creator-ops"}]
                ch = hbt.edit_main_config(cfg, routes, dispatch=True, dry=False, backup_dir=Path(d) / "bk")
                after = cfg.read_text().splitlines()
                kept = [l for l in text.splitlines() if l != "  dispatch_in_gateway: false"]
                self.assertTrue(all(l in after for l in kept), "an owner line was reformatted")
                hbt.revert_main_config(cfg, {"main_config": ch}, dry=False)
                self.assertEqual(cfg.read_text(), text)

    def test_update_keeps_the_owners_original_values(self):
        """A second edit (update) must not record our own earlier change as the owner's original."""
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "config.yaml"
            original = "kanban:\n  dispatch_in_gateway: false\n"
            cfg.write_text(original)
            r1 = [{"name": "hbt:creator:ops", "platform": "slack", "chat_id": "C9", "profile": "creator-ops"}]
            first = hbt.edit_main_config(cfg, r1, dispatch=True, dry=False, backup_dir=Path(d) / "bk")
            r2 = r1 + [{"name": "hbt:creator:video", "platform": "slack", "chat_id": "C8", "profile": "creator-video"}]
            second = hbt.edit_main_config(cfg, r2, dispatch=True, dry=False, backup_dir=Path(d) / "bk", previous=first)
            self.assertEqual(second["routes_added"], ["hbt:creator:video"])
            self.assertEqual(second["kanban_before"], first["kanban_before"])
            record = dict(second, routes_added=first["routes_added"] + second["routes_added"])
            hbt.revert_main_config(cfg, {"main_config": record}, dry=False)
            self.assertEqual(cfg.read_text(), original)

    def test_channel_parsing(self):
        self.assertEqual(hbt.parse_channels(["#creator-video=C0ABCDEFG"]), {"creator-video": "C0ABCDEFG"})
        for bad in (["creator-video"], ["creator-video=general"]):
            with self.assertRaises(SystemExit):
                hbt.parse_channels(bad)


class SlackAndCards(unittest.TestCase):
    """The per-bot Slack settings and card runners the template was proven with (Q27, Q28)."""

    def setUp(self):
        self.tpl = hbt.load_template("creator")
        self.by = {r.key: r for r in self.tpl.roles}

    def test_a_bot_answers_its_own_channels_and_only_its_owner(self):
        chans = {"media-video": "C1", "media-edit": "C2", "build-architect": "C3"}
        cfg, env = hbt.slack_settings(self.by["creative-director"], chans, "U0OWNER1", {})
        self.assertEqual(cfg["slack.free_response_channels"], "C1,C2")
        self.assertEqual(cfg["slack.ignore_other_user_mentions"], "true")
        self.assertEqual(cfg["slack.allow_bots"], "mentions")  # v0.3: hears CTO, but only by mention
        ops = next(r for r in hbt.load_template("creator").roles if r.kind == "ops")
        self.assertNotIn("slack.allow_bots", hbt.slack_settings(ops, chans, "U0OWNER1", {})[0])  # no peers
        self.assertEqual(env, {"SLACK_ALLOWED_USERS": "U0OWNER1", "SLACK_HOME_CHANNEL": "C1"})

    def test_peers_hear_each_other_only_by_mention(self):
        cfg, env = hbt.slack_settings(self.by["cto"], {"build-architect": "C3"}, "U0OWNER1", {"engineer": "U0ENG1234"})
        self.assertEqual(cfg["slack.allow_bots"], "mentions")
        self.assertEqual(cfg["slack.strict_mention"], "true")  # a thread follow-up wakes only the bot mentioned
        self.assertEqual(cfg["slack.allow_admin_from"], "U0OWNER1")  # a peer's "@cto !approve" is refused
        self.assertEqual(cfg["slack.group_allow_admin_from"], "U0OWNER1")
        self.assertEqual(env["SLACK_ALLOWED_USERS"], "U0OWNER1,U0ENG1234")
        cfg, env = hbt.slack_settings(self.by["cto"], {}, "U0OWNER1", {})  # before Engineer is connected
        self.assertEqual(env, {"SLACK_ALLOWED_USERS": "U0OWNER1"})
        self.assertNotIn("slack.free_response_channels", cfg)

    def test_card_runners_never_narrow_an_open_board(self):
        self.assertIsNone(hbt.card_takers(hbt._MISSING, ["engineer"]))  # absent: every profile already runs
        self.assertIsNone(hbt.card_takers(["engineer", "x"], ["engineer"]))
        self.assertEqual(hbt.card_takers(["x"], ["engineer"]), ["x", "engineer"])
        self.assertEqual(hbt.card_takers("x, y", ["y", "engineer"]), ["x", "y", "engineer"])

    def test_card_runner_list_is_restored_on_uninstall(self):
        import yaml
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "config.yaml"
            original = "kanban:\n  dispatch_in_gateway: true\n  review_dispatch: false\n  dispatch_profiles:\n    - mine\n"
            cfg.write_text(original)
            ch = hbt.edit_main_config(cfg, [], dispatch=True, dry=False, backup_dir=Path(d) / "bk",
                                      card_profiles=["creative-director", "engineer"])
            self.assertEqual(yaml.safe_load(cfg.read_text())["kanban"]["dispatch_profiles"],
                             ["mine", "creative-director", "engineer"])
            self.assertEqual(ch["routes_added"], [])
            self.assertNotIn("gateway", yaml.safe_load(cfg.read_text()))  # no routes, no gateway section
            hbt.revert_main_config(cfg, {"main_config": ch}, dry=False)
            self.assertEqual(yaml.safe_load(cfg.read_text()), yaml.safe_load(original))


class GuidedSetup(unittest.TestCase):
    """Setup works out the one next action from what is already true, so it can stop and resume anywhere."""

    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        self.root = Path(self.home.name)
        self.home_patch = patch.object(hbt, "hermes_home", return_value=self.root)
        self.home_patch.start()
        self.addCleanup(self.home_patch.stop)
        for role in hbt.load_template("creator").roles:
            profile = self.root / "profiles" / role.key
            profile.mkdir(parents=True)
            (profile / "config.yaml").write_text("{}\n")

    def test_steps_come_one_at_a_time_in_order(self):
        tpl = hbt.load_template("creator")
        self.assertEqual(hbt.next_setup_step(tpl, None), ("install", None))
        rec = {"version": tpl.version, "profiles": ["creative-director", "cto", "engineer", "ops"], "bots": {}, "setup": {}}
        seen = []
        for _ in range(20):
            step, role = hbt.next_setup_step(tpl, rec)
            seen.append(step + (f":{role.key}" if role else ""))
            if step == "done":
                break
            if step == "connect":
                rec["bots"][role.key] = "U0" + role.key.upper()[:6].replace("-", "X")
            elif step == "channels":
                rec["setup"].setdefault("channels_ok", []).append(role.key)
            elif step == "system-channel":
                rec["setup"]["system_channel_ok"] = True
            elif step == "restart":
                rec["setup"]["restarted"] = "now"
            elif step == "test":
                rec["setup"].setdefault("tested", []).append(role.key)

        self.assertEqual(seen, [
            "connect:creative-director", "channels:creative-director", "connect:cto", "channels:cto",
            "connect:engineer", "channels:engineer", "system-channel", "restart",
            "test:creative-director", "test:cto", "test:engineer", "done"])

    def test_incomplete_install_refuses_setup_and_status_without_writes(self):
        import copy
        tpl = hbt.load_template("creator")
        valid = {"version": tpl.version, "profiles": ["cto"], "setup": {}}
        cases = [valid | {"version": "pending"}, valid | {"target_version": tpl.version},
                 valid | {"profiles": []}, valid | {"version": ""},
                 valid | {"shared_skills": {"profiles": {"cto": {}, "engineer": {}}}},
                 valid | {"shared_skills": {"pending": {"backup": "fixture"}}},
                 valid | {"shared_skills": {"migration": "activating"}}]
        for rec in cases:
            with self.subTest(rec=rec):
                before = copy.deepcopy(rec)
                self.assertEqual(hbt.next_setup_step(tpl, rec), ("recover", None))
                with patch.object(hbt, "load_record", return_value=rec), \
                     patch.object(hbt, "save_record", side_effect=AssertionError("write")), \
                     patch.object(hbt, "_wait", side_effect=AssertionError("prompt")), \
                     patch.object(hbt, "slack_api", side_effect=AssertionError("transport")), \
                     patch.object(hbt, "say") as say:
                    args = hbt.build_parser().parse_args(["setup", "creator"])
                    self.assertEqual(hbt.cmd_setup(args), 1)
                    self.assertEqual(hbt.cmd_status(args), 1)
                    self.assertIn("uninstall creator", say.call_args.args[0])
                self.assertEqual(rec, before)
        (self.root / "profiles/cto/config.yaml").unlink()
        self.assertEqual(hbt.next_setup_step(tpl, valid), ("recover", None))

    def test_legitimate_subset_and_deleted_role(self):
        tpl = hbt.load_template("creator")
        rec = {"version": tpl.version, "profiles": ["cto"], "bots": {"cto": "U00000002"},
               "shared_skills": {"profiles": {"cto": {}}},
               "setup": {"channels_ok": ["cto"], "tested": ["cto"], "restarted": "fixture"}}
        self.assertEqual(hbt.next_setup_step(tpl, rec), ("done", None))
        marker = self.root / "profiles/.deleted/cto"
        marker.parent.mkdir()
        marker.touch()
        self.assertEqual(hbt.next_setup_step(tpl, rec), ("recover", None))

    def test_one_desk_per_editor(self):
        tpl = hbt.load_template("creator")
        desk = tpl.desks[0]
        self.assertEqual(hbt.desk_names(desk, "sam"), ("desk-editor-sam", "ext-editor-sam", "desks/editor-sam"))
        for bad in ("Sam", "sam lee", "", "../x"):
            with self.assertRaises(SystemExit):
                hbt.desk_names(desk, bad)


class Desks(unittest.TestCase):
    """A desk answers people outside the business. These pin what it can reach (Q20, Q26)."""

    def test_desk_sees_only_its_folder_offline_with_file_tools_only(self):
        import json
        cfg = hbt.desk_config(Path("/srv/biz/desks/editor"), "C0DESK123")
        self.assertEqual(json.loads(cfg["platform_toolsets.slack"]), ["file"])
        self.assertEqual(cfg["terminal.backend"], "docker")
        self.assertEqual(json.loads(cfg["terminal.docker_volumes"]), ["/srv/biz/desks/editor:/workspace"])
        self.assertEqual(cfg["terminal.docker_mount_cwd_to_workspace"], "false")
        self.assertEqual(cfg["terminal.docker_network"], "false")
        self.assertEqual(cfg["memory.memory_enabled"], "false")
        self.assertEqual(cfg["slack.allowed_channels"], "C0DESK123")
        self.assertEqual(cfg["slack.unauthorized_dm_behavior"], "ignore")
        self.assertEqual(json.loads(cfg["slack.allow_admin_from"]), ["nobody"])

    def test_desk_folders_are_outside_every_role_folder(self):
        tpl = hbt.load_template("creator")
        self.assertTrue(tpl.desks)
        for d in tpl.desks:
            for r in tpl.roles:
                self.assertFalse(d.folder == r.folder or d.folder.startswith(r.folder + "/"), (d.key, r.key))

    def test_guest_ids_are_checked(self):
        self.assertEqual(hbt.parse_guests(["U0ABCDEF1", " W0ABCDEF2 "]), ["U0ABCDEF1", "W0ABCDEF2"])
        for bad in (["@editor"], ["C0ABCDEF1"], ["u0abcdef1"]):
            with self.assertRaises(SystemExit):
                hbt.parse_guests(bad)


class MemoryWatch(unittest.TestCase):
    T0 = datetime(2026, 9, 25, 19, 0, tzinfo=timezone.utc)

    def test_down_then_quiet_then_reminder_then_up(self):
        tz = timezone.utc
        s, msg = watch.decide({}, [], self.T0, "", "fix", tz)
        self.assertEqual(msg, "")
        s, msg = watch.decide(s, ["server down"], self.T0, "svc=failed", "fix it", tz)
        self.assertIn("DOWN", msg)
        self.assertIn("fix it", msg)
        s, msg = watch.decide(s, ["server down"], self.T0 + timedelta(minutes=5), "", "fix", tz)
        self.assertEqual(msg, "")
        s, msg = watch.decide(s, ["server down"], self.T0 + timedelta(hours=6), "", "fix", tz)
        self.assertIn("still down", msg)
        s, msg = watch.decide(s, [], self.T0 + timedelta(hours=6, minutes=5), "", "fix", tz)
        self.assertIn("back up", msg)
        self.assertIn("6h 5m", msg)

    def test_unreachable_server_is_reported(self):
        cfg = {"endpoint": "http://127.0.0.1:9", "embed_endpoint": "", "services": [], "fix_hint": "", "timezone": "", "retry_delay": 0}
        self.assertTrue(watch.check(cfg))


if __name__ == "__main__":
    unittest.main()
