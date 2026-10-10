"""Guided role selection and resume. Native and Slack edges are synthetic."""
from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from test_installer import hbt
from test_shared_skills import put_skill

SUBSETS = ("ops", "cto", "engineer", "creative-director", "cto,engineer", "")


class RoleSelection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / ".hermes"
        self.home.mkdir()
        env = patch.dict(os.environ, {"HOME": str(self.root), "HERMES_HOME": str(self.home)})
        env.start()
        self.addCleanup(env.stop)
        self.tpl = hbt.load_template("creator")
        self.args = hbt.build_parser().parse_args(["setup", "creator"])

    def test_fresh_selection_canonical_forwarding_and_mandatory_ops(self):
        for wanted in SUBSETS + (" engineer , cto,engineer ",):
            with self.subTest(wanted=wanted):
                expected = [r.key for r in hbt.select_roles(self.tpl, wanted)]
                answers = [wanted, "Etc/UTC"]
                if "engineer" in expected:
                    answers.append(str(self.root / "projects"))
                answers.append("U00000001")
                before = hbt.package_hashes(self.root)
                with patch("builtins.input", side_effect=answers), patch.object(hbt, "cmd_install", return_value=1) as install, \
                     patch.object(hbt, "say") as say:
                    self.assertEqual(hbt.cmd_setup(self.args), 1)
                forwarded = install.call_args.args[0]
                self.assertEqual(forwarded.roles, ",".join(expected))
                self.assertEqual(forwarded.hermes, self.args.hermes)
                self.assertEqual(forwarded.template, "creator")
                self.assertEqual([r["key"] for r in forwarded.team_definition["roles"]], expected)
                self.assertIn("Selected: " + ", ".join(expected), [c.args[0] for c in say.call_args_list])
                self.assertEqual(before, hbt.package_hashes(self.root))

    def test_invalid_selection_reprompts_before_any_write(self):
        before = hbt.package_hashes(self.root)
        answers = iter(["unknown", ", ,", "cto"])
        def answer(_):
            self.assertEqual(before, hbt.package_hashes(self.root))
            return next(answers)
        with patch("builtins.input", side_effect=answer), patch.object(hbt, "say") as say:
            self.assertEqual([r.key for r in hbt.ask_setup_roles(self.tpl)], ["cto", "ops"])
        text = "\n".join(c.args[0] for c in say.call_args_list)
        self.assertIn("Unknown role(s)", text)
        self.assertIn("at least one role key", text)
        self.assertEqual(before, hbt.package_hashes(self.root))
        # Keep the existing explicit install CLI's separator semantics unchanged.
        self.assertEqual([r.key for r in hbt.select_roles(self.tpl, ",,")], ["ops"])

    def test_eof_and_interrupt_stop_before_installation(self):
        for exception in (EOFError, KeyboardInterrupt):
            for prefix in ([], ["cto"], ["cto", "Etc/UTC"]):
                with self.subTest(exception=exception, prefix=prefix):
                    before = hbt.package_hashes(self.root)
                    with patch("builtins.input", side_effect=prefix + [exception]), \
                         patch.object(hbt, "cmd_install", side_effect=AssertionError("install")), \
                         patch.object(hbt, "save_record", side_effect=AssertionError("write")), patch.object(hbt, "say"):
                        self.assertEqual(hbt.main(["setup", "creator"]), 1)
                    self.assertEqual(before, hbt.package_hashes(self.root))

    def record(self, wanted, legacy=False):
        roles = hbt.select_roles(self.tpl, wanted)
        keys = [r.key for r in roles]
        bots = [r.key for r in roles if r.kind != "ops"]
        for role in roles:
            p = self.home / "profiles" / role.key
            p.mkdir(parents=True, exist_ok=True)
            (p / "config.yaml").write_text("{}\n")
        (self.home / "config.yaml").write_text("kanban:\n  review_dispatch: false\n")
        rec = {"version": self.tpl.version, "installed_at": "fixture", "profiles": keys,
               "workspace": str(self.home / "workspace"), "projects": str(self.root / "projects"),
               "memory": {"enabled": False}, "channels": {},
               "bots": {r.key: f"U0000000{i}" for i, r in enumerate(self.tpl.roles)},
               "jobs": [{"id": "000000000001", "profile": "ops", "key": "memory-watchdog"}],
               "setup": {"channels_ok": list(bots), "tested": list(bots), "restarted": "fixture", "system_channel_ok": "skipped"}}
        if not legacy:
            rec["shared_skills"] = {"schema": 1, "root": str(hbt.record_dir("creator") / "skills"),
                                    "source": "fixture", "source_version": "fixture", "migration": "complete", "backups": [],
                                    "packages": {}, "profiles": {key: {"selected": []} for key in keys}}
        if "cto" in keys and "engineer" in keys:
            rec["setup"]["first_card"] = "t_00000001"
        hbt.save_record("creator", rec)
        return rec

    def test_complete_and_legacy_subsets_resume_without_mutation(self):
        for legacy in (False, True):
            for wanted in SUBSETS:
                with self.subTest(legacy=legacy, wanted=wanted):
                    rec = self.record(wanted, legacy)
                    for name, data in {"memories/USER.md": "owner context", "memories/MEMORY.md": "role memory",
                                       "workspace/canon/business.md": "owner canon", "cron/jobs.json": '[{"state":"paused"}]'}.items():
                        p = self.home / name
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text(data)
                    before = hbt.package_hashes(self.root)
                    with patch.object(hbt, "cmd_install", side_effect=AssertionError("install")), \
                         patch.object(hbt, "_ask", side_effect=AssertionError("selection prompt")), \
                         patch.object(hbt, "_wait", side_effect=AssertionError("prompt")), \
                         patch.object(hbt.Runner, "hermes_cmd", side_effect=AssertionError("native")), \
                         patch.object(hbt, "slack_api", side_effect=AssertionError("Slack")), patch.object(hbt, "say") as say:
                        for _ in range(2):
                            self.assertEqual(hbt.cmd_setup(self.args), 0)
                            self.assertEqual(hbt.cmd_status(self.args), 0)
                    self.assertEqual(before, hbt.package_hashes(self.root))
                    self.assertEqual(rec, hbt.load_record("creator"))
                    text = "\n".join(c.args[0] for c in say.call_args_list)
                    self.assertNotIn("demonstration passed", text)
                    self.assertIn("Herdr", text)
                    if wanted == "ops":
                        self.assertIn("No conversational bots", text)
                    self.assertIn("Ops job delivery is unverified", text)
                    self.assertIn("Slack delivery was not tested", text)

    def test_connect_then_skipped_main_route_preserves_delivery_on_setup_rerun(self):
        rec = self.record("creative-director")
        rec["setup"].pop("system_channel_ok")
        hbt.save_record("creator", rec)
        role = next(r for r in self.tpl.roles if r.key == "creative-director")
        jobs = self.home / "cron/jobs.json"
        jobs.parent.mkdir()
        jobs.write_text(json.dumps([{"id": "000000000001", "deliver": "local", "state": "paused"}]))

        def native(*args, **kwargs):
            if args[:2] == ("cron", "edit"):
                self.assertEqual(args, ("cron", "edit", "000000000001", "--deliver", "slack:C00000001"))
                state = json.loads(jobs.read_text())
                state[0]["deliver"] = args[4]
                jobs.write_text(json.dumps(state))
            return ""

        # Exercise real connect and wire_system_channel, replacing only external edges.
        with patch.object(hbt, "read_env_value", return_value="synthetic-token"), \
             patch.object(hbt, "slack_api", return_value={"ok": True, "user_id": rec["bots"][role.key]}), \
             patch.object(hbt, "find_channels", return_value={
                 name: {"id": "C00000001", "member": True}
                 for name in role.channels + [self.tpl.system_channel]}), \
             patch.object(hbt.Runner, "hermes_cmd", side_effect=native) as commands, patch.object(hbt, "say"):
            args = hbt.build_parser().parse_args(["connect", "creator", role.key])
            self.assertEqual(hbt.cmd_connect(args), 0)
        self.assertTrue(any(c.args[:2] == ("cron", "edit") for c in commands.call_args_list))
        self.assertEqual(json.loads(jobs.read_text())[0],
                         {"id": "000000000001", "deliver": "slack:C00000001", "state": "paused"})
        before = hbt.package_hashes(self.root)
        with patch.object(hbt, "_wait", side_effect=AssertionError("prompt")), \
             patch.object(hbt.Runner, "hermes_cmd", side_effect=AssertionError("native call on resume")), \
             patch.object(hbt, "slack_api", side_effect=AssertionError("Slack access")), patch.object(hbt, "say") as say:
            self.assertEqual(hbt.cmd_setup(self.args), 0)
            self.assertEqual(hbt.cmd_status(self.args), 0)
            after = hbt.package_hashes(self.root)
            record_path = str((hbt.record_dir("creator") / "record.json").relative_to(self.root))
            self.assertEqual([p for p in before.keys() | after.keys() if before.get(p) != after.get(p)], [record_path])
            for _ in range(2):
                self.assertEqual(hbt.cmd_setup(self.args), 0)
                self.assertEqual(hbt.cmd_status(self.args), 0)
                self.assertEqual(after, hbt.package_hashes(self.root))
        current = hbt.load_record("creator")
        self.assertEqual(current["setup"]["system_channel_ok"], "skipped")
        self.assertNotIn("first_card", current["setup"])
        text = "\n".join(c.args[0] for c in say.call_args_list)
        self.assertIn("main-agent Slack routing check is skipped", text)
        self.assertIn("Ops job delivery is unverified", text)
        self.assertNotIn("Ops output stays local", text)
        self.assertNotIn("Ops output stays on the server", text)

    def test_legacy_without_ops_is_not_expanded(self):
        rec = self.record("cto", legacy=True)
        rec["profiles"] = ["cto"]
        rec["setup"].pop("system_channel_ok")
        hbt.save_record("creator", rec)
        before = hbt.package_hashes(self.root)
        with patch.object(hbt, "_wait", side_effect=AssertionError("prompt")), patch.object(hbt, "say"):
            self.assertEqual(hbt.cmd_setup(self.args), 0)
        self.assertEqual(before, hbt.package_hashes(self.root))
        self.assertEqual(hbt.load_record("creator")["profiles"], ["cto"])

    def test_retired_demo_choices_never_start_a_card_or_claim_herdr_success(self):
        for choice in (None, False, True):
            rec = self.record("cto,engineer")
            rec["setup"].pop("first_card")
            rec["setup"]["build_demo"] = choice
            hbt.save_record("creator", rec)
            before = hbt.package_hashes(self.root)
            with patch("builtins.input", side_effect=AssertionError("retired demo prompt")), \
                 patch.object(hbt.Runner, "hermes_cmd", side_effect=AssertionError("native call")), \
                 patch.object(hbt, "say") as say:
                self.assertEqual(hbt.cmd_setup(self.args), 0)
            self.assertEqual(hbt.package_hashes(self.root), before)
            text = "\n".join(c.args[0] for c in say.call_args_list)
            self.assertIn("Herdr", text)
            self.assertNotIn("demonstration passed", text)

    def test_interrupted_and_deleted_selected_roles_fail_closed(self):
        hbt.save_record("creator", {})
        before = hbt.package_hashes(self.root)
        with patch.object(hbt, "ask_setup_roles", side_effect=AssertionError("selection")), patch.object(hbt, "say"):
            self.assertEqual(hbt.cmd_setup(self.args), 1)
            self.assertEqual(hbt.cmd_status(self.args), 1)
        self.assertEqual(before, hbt.package_hashes(self.root))
        for legacy in (False, True):
            rec = self.record("cto,engineer", legacy)
            mutations = [dict(version="pending"), dict(target_version="future"), dict(profiles=[])]
            if not legacy:
                mutations += [dict(profiles=["cto", "ops"]),
                              dict(shared_skills=rec["shared_skills"] | {"pending": {"archive": "fixture"}}),
                              dict(shared_skills=rec["shared_skills"] | {"migration": "activating"})]
            for mutation in mutations:
                hbt.save_record("creator", rec | mutation)
                before = hbt.package_hashes(self.root)
                with patch.object(hbt, "ask_setup_roles", side_effect=AssertionError("selection")), \
                     patch.object(hbt, "cmd_install", side_effect=AssertionError("install")), patch.object(hbt, "say"):
                    self.assertEqual(hbt.cmd_setup(self.args), 1)
                    self.assertEqual(hbt.cmd_status(self.args), 1)
                self.assertEqual(before, hbt.package_hashes(self.root))
            hbt.save_record("creator", rec)
            profile = self.home / "profiles/engineer"
            shutil.rmtree(profile)
            self.assertEqual(hbt.next_setup_step(self.tpl, rec), ("recover", None))
            profile.mkdir()
            (profile / "config.yaml").write_text("{}")
            marker = self.home / "profiles/.deleted/engineer"
            marker.parent.mkdir(exist_ok=True)
            marker.touch()
            self.assertEqual(hbt.next_setup_step(self.tpl, rec), ("recover", None))
            marker.unlink()

    def test_selected_only_peer_invites_allowlists_and_rosters(self):
        for wanted in SUBSETS:
            roles = hbt.select_roles(self.tpl, wanted)
            keys = [r.key for r in roles]
            rec = {"profiles": keys, "owner": "U00000001", "channels": {},
                   "bots": {r.key: f"U0000000{i+2}" for i, r in enumerate(self.tpl.roles)}}
            original = copy.deepcopy(rec)
            for role in roles:
                if role.kind == "ops":
                    continue
                runner = Mock()
                with patch.object(hbt, "set_env_values") as write:
                    hbt.apply_slack(runner, self.tpl, role, rec, False)
                env = write.call_args.args[1]
                expected = [rec["owner"]] + [rec["bots"][key] for key in role.peers if key in keys]
                self.assertEqual(env["SLACK_ALLOWED_USERS"], ",".join(expected))
                cfg = {c.args[2]: c.args[3] for c in runner.hermes_cmd.call_args_list}
                self.assertEqual(cfg["slack.allow_admin_from"], rec["owner"])
                self.assertEqual(cfg["slack.group_allow_admin_from"], rec["owner"])
                expected_channels = [c for r in roles if role.key in r.peers for c in r.channels if c not in role.channels]
                self.assertEqual(hbt.peer_channels(self.tpl, role, keys), expected_channels)
            self.assertEqual(rec, original)
            text = hbt.render_roster(self.tpl, roles, self.root / "workspace", {}, rec["bots"])
            for role in self.tpl.roles:
                self.assertEqual(f"| {role.title} |" in text, role.key in keys)
                if role.key not in keys:
                    self.assertNotIn(rec["bots"][role.key], text)
            self.assertIn("Absent roles cannot receive", text)

    def test_connect_requests_only_installed_peer_channels(self):
        for wanted in ("cto", "engineer", "creative-director", "cto,engineer"):
            rec = self.record(wanted)
            roles = [r for r in self.tpl.roles if r.key in rec["profiles"]]
            for role in roles:
                if role.kind == "ops":
                    continue
                wanted_channels = role.channels + hbt.peer_channels(self.tpl, role, rec["profiles"]) + [self.tpl.system_channel]
                def channels(token, names):
                    self.assertEqual(names, wanted_channels)
                    return {name: {"id": f"C0000000{i}", "member": False} for i, name in enumerate(names)}
                with patch.object(hbt, "read_env_value", return_value="synthetic-token"), \
                     patch.object(hbt, "slack_api", return_value={"ok": True, "user_id": rec["bots"][role.key]}), \
                     patch.object(hbt, "find_channels", side_effect=channels), \
                     patch.object(hbt, "apply_slack") as apply, patch.object(hbt, "wire_system_channel"), \
                     patch.object(hbt, "say") as say:
                    args = hbt.build_parser().parse_args(["connect", "creator", role.key])
                    self.assertEqual(hbt.cmd_connect(args), 2)
                updated = [call.args[2].key for call in apply.call_args_list]
                self.assertTrue(set(updated).issubset(rec["profiles"]))
                expected = role.channels + hbt.peer_channels(self.tpl, role, rec["profiles"])
                text = "\n".join(call.args[0] for call in say.call_args_list)
                self.assertIn("Not invited yet: " + ", ".join("#" + name for name in expected), text)

    def test_install_selected_assets_with_synthetic_native_edges(self):
        # Real installer/shared-library/rendering writes, with a synthetic native
        # command boundary. This is not native compatibility or live-install proof.
        for wanted in SUBSETS:
            with self.subTest(wanted=wanted), tempfile.TemporaryDirectory(dir=self.root) as d:
                home = Path(d) / ".hermes"
                home.mkdir()
                with patch.dict(os.environ, {"HOME": d, "HERMES_HOME": str(home)}):
                    roles = hbt.select_roles(self.tpl, wanted)
                    keys = [r.key for r in roles]
                    stock = Path(d) / "stock"
                    packages = {name: put_skill(stock / "category", name) for r in self.tpl.roles for name in r.stock_skills}
                    native = {"source": "synthetic", "root": stock, "packages": packages, "matches": lambda *a: False}
                    calls = []
                    def run(*args, **kwargs):
                        calls.append((args, kwargs))
                        if args[:2] == ("profile", "install"):
                            src = Path(args[2])
                            dest = home / "profiles" / src.name
                            shutil.copytree(src, dest, dirs_exist_ok=True)
                        elif args[:2] == ("slack", "manifest"):
                            Path(args[args.index("--write") + 1]).write_text("{}")
                        elif args[:2] == ("cron", "create"):
                            return f"{len(calls):012x}"
                        return ""
                    # No credential reads/network or native profile/bootstrap code.
                    with patch.object(hbt, "preflight", return_value={"hermes_version": "synthetic", "docker": False}), \
                         patch.object(hbt, "native_skills", return_value=native), \
                         patch.object(hbt, "seed_shared_manual"), \
                         patch.object(hbt.Runner, "hermes_cmd", side_effect=run), \
                         patch.object(hbt, "slack_api", side_effect=AssertionError("Slack")), patch.object(hbt, "say"):
                        args = hbt.build_parser().parse_args(["install", "creator", "--yes", "--no-memory",
                                                             "--roles", ",".join(keys), "--owner", "U00000001"])
                        self.assertEqual(hbt.cmd_install(args), 0)
                    rec = hbt.load_record("creator")
                    self.assertEqual(rec["profiles"], keys)
                    self.assertEqual(set(rec["shared_skills"]["profiles"]), set(keys))
                    self.assertEqual(set(rec["manifests"]), {r.key for r in roles if r.kind != "ops"})
                    self.assertEqual({p.name for p in (home / "profiles").iterdir()}, set(keys))
                    ws = Path(rec["workspace"])
                    for role in self.tpl.roles:
                        self.assertEqual((ws / role.folder).is_dir(), role in roles)
                    for role in roles:
                        selected = rec["shared_skills"]["profiles"][role.key]["selected"]
                        stock_paths = {"bundled/" + packages[n].relative_to(stock).as_posix() for n in role.stock_skills}
                        self.assertEqual({p for p in selected if p.startswith("bundled/")}, stock_paths)
                        self.assertTrue(all(not p.startswith("template/") or p.startswith(f"template/{role.key}/") for p in selected))
                        self.assertEqual(set(hbt._profile_cfg(role.key)["skills"]["external_dirs"]),
                                         set(rec["shared_skills"]["profiles"][role.key]["managed"]))
                    created = [Path(args[2]).name for args, _ in calls if args[:2] == ("profile", "install")]
                    self.assertEqual(created, keys)
                    cfg = hbt.yaml.safe_load((home / "config.yaml").read_text()) if (home / "config.yaml").exists() else {}
                    self.assertNotIn("kanban", cfg or {})
                    self.assertFalse(any(args[0] == "kanban" for args, _ in calls))
                    self.assertEqual(rec["jobs"], [])  # no OpenViking, no watchdog
                    self.assertTrue(all(j["profile"] == "ops" for j in rec["jobs"]))


if __name__ == "__main__":
    unittest.main()
