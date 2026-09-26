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
        for r in self.tpl.roles:
            d = TPL / "roles" / r.key
            self.assertTrue((d / "distribution.yaml").is_file(), r.key)
            self.assertTrue((d / "SOUL.md").is_file(), r.key)

    def test_manifest_names_match_profile_names(self):
        import yaml
        for r in self.tpl.roles:
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
            self.assertTrue(m.group(1).startswith(f"creator-{role}-"), skill)
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
        for f in list(TPL.rglob("*")) + [ROOT / "installer" / "hbt.py"]:
            if f.is_file() and f.suffix in {".md", ".yaml", ".py"}:
                text = f.read_text()
                for b in banned:
                    self.assertNotIn(b, text, f"{b!r} in {f}")

    def test_ops_is_always_selected(self):
        roles = hbt.select_roles(self.tpl, "video")
        self.assertEqual({r.key for r in roles}, {"video", "ops"})
        with self.assertRaises(SystemExit):
            hbt.select_roles(self.tpl, "video,nope")


class Workspace(unittest.TestCase):
    def test_build_is_idempotent_and_keeps_owner_files(self):
        tpl = hbt.load_template("creator")
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / "ws"
            first = hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertTrue((ws / "canon" / "business.md").is_file())
            self.assertTrue((ws / "video" / "AGENTS.md").is_file())
            (ws / "canon" / "business.md").write_text("OWNER EDIT")
            (ws / "video" / "topic-queue.md").write_text("OWNER QUEUE")
            second = hbt.build_workspace(tpl, tpl.roles, ws, {}, dry=False)
            self.assertEqual((ws / "canon" / "business.md").read_text(), "OWNER EDIT")
            self.assertEqual((ws / "video" / "topic-queue.md").read_text(), "OWNER QUEUE")
            self.assertTrue(all(a.startswith("update") for a in second), second)
            self.assertGreater(len(first), len(second))

    def test_role_agents_lists_checks_and_roster(self):
        tpl = hbt.load_template("creator")
        video = next(r for r in tpl.roles if r.key == "video")
        text = hbt.render_role_agents(tpl, video, tpl.roles, Path("/ws"), {"creator-video": "C0ABCDEFG"})
        self.assertIn("topic queue was updated in the last 35 days", text)
        self.assertIn("`creator-partnerships`", text)
        self.assertIn("C0ABCDEFG", text)

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
