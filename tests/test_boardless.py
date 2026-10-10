"""Boardless lifecycle and legacy retirement, isolated from the owner's installation."""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("hbt_boardless_test", Path(__file__).resolve().parents[1] / "installer/hbt.py")
assert spec is not None and spec.loader is not None
hbt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hbt
spec.loader.exec_module(hbt)


class Boardless(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        env = patch.dict(os.environ, HOME=str(self.root), HERMES_HOME=str(self.root / ".hermes"))
        env.start()
        self.addCleanup(env.stop)
        self.home = hbt.hermes_home()
        self.home.mkdir()
        self.config = self.home / "config.yaml"
        self.config.write_text("# owner formatting\nkanban:\n  dispatch_in_gateway: true\n  dispatch_profiles: [other-workflow]\n")
        self.original_config = self.config.read_bytes()
        self.tpl = copy.deepcopy(hbt.load_template("creator"))
        self.tpl.path = self.root / "template"
        shutil.copytree(hbt.load_template("creator").path, self.tpl.path)
        for role in self.tpl.roles:
            role.stock_skills = []
        self.native = {"source": "synthetic-native", "root": self.root / "native", "packages": {}, "matches": lambda *_: False}
        self.calls = []
        for name, value in [("load_template", lambda _: self.tpl), ("native_skills", lambda: self.native),
                            ("preflight", lambda _: {"hermes_version": "test", "docker": True}),
                            ("seed_shared_manual", self.seed), ("write_manifest", lambda *a: "fixture-manifest")]:
            p = patch.object(hbt, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(hbt.Runner, "hermes_cmd", self.command)
        p.start()
        self.addCleanup(p.stop)
        self.output = io.StringIO()
        p = contextlib.redirect_stdout(self.output)
        p.__enter__()
        self.addCleanup(p.__exit__, None, None, None)

    def put(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def seed(self, native, name):
        self.put(self.home / "profiles" / name / "skills/hermes-agent/SKILL.md", "---\nname: hermes-agent\n---\nFixture manual\n")

    def command(self, *args, profile=None, **kwargs):
        self.calls.append((args, profile))
        self.assertNotIn("kanban", args)
        if args[:2] == ("profile", "install"):
            source = Path(args[2])
            target = self.home / "profiles" / source.name
            shutil.copytree(source, target)
            manifest = hbt.yaml.safe_load((target / "distribution.yaml").read_text())
            manifest["source"] = str(source)
            (target / "distribution.yaml").write_text(hbt.yaml.safe_dump(manifest))
        elif args[:2] == ("profile", "update"):
            target = self.home / "profiles" / args[2]
            source = hbt.record_dir("creator") / "dist" / args[2]
            for item in ("SOUL.md", "scripts"):
                dest = target / item
                src = source / item
                if src.is_dir():
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                elif src.exists():
                    shutil.copy2(src, dest)
        elif args[:2] == ("config", "set"):
            path = self.home / "profiles" / profile / "config.yaml"
            cfg = hbt.yaml.safe_load(path.read_text()) or {}
            value = hbt.yaml.safe_load(args[3])
            node = cfg
            keys = args[2].split(".")
            for key in keys[:-1]:
                node = node.setdefault(key, {})
            node[keys[-1]] = value
            path.write_text(hbt.yaml.safe_dump(cfg))
        elif args[:2] == ("cron", "pause"):
            # Exercise the native pause API in a process scoped to the synthetic Ops profile.
            import subprocess
            code = "from cron.jobs import pause_job; assert pause_job(%r) is not None" % args[2]
            subprocess.run([sys.executable, "-c", code], check=True, capture_output=True,
                           env={**os.environ, "HERMES_HOME": str(self.home / "profiles" / profile)})
        elif args[:2] == ("cron", "create"):
            import subprocess
            self.assertIn("--no-agent", args)
            code = ("from cron.jobs import create_job; "
                    "print(create_job(None, %r, name=%r, script=%r, no_agent=True, deliver=%r)['id'])" %
                    (args[2], args[args.index("--name") + 1], args[args.index("--script") + 1],
                     args[args.index("--deliver") + 1]))
            result = subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True,
                                    env={**os.environ, "HERMES_HOME": str(self.home / "profiles" / profile)})
            return result.stdout
        elif args[:2] == ("cron", "remove"):
            path = self.home / "profiles" / profile / "cron/jobs.json"
            jobs = json.loads(path.read_text())["jobs"]
            path.write_text(json.dumps({"jobs": [j for j in jobs if j["id"] != args[2]]}))
        elif args[:2] == ("profile", "delete"):
            shutil.rmtree(self.home / "profiles" / args[2])
        else:
            self.fail(f"Unexpected native command: {args}")
        return ""

    def run_hbt(self, *args):
        return hbt.main(list(args))

    def install(self):
        return self.run_hbt("install", "creator", "--roles", "ops", "--no-memory", "-y")

    def legacy_job(self, key="nightly-review"):
        import subprocess
        code = ("import json; from cron.jobs import create_job; "
                "print(json.dumps(create_job('Synthetic retired routine', '0 21 * * *', "
                "name=%r, deliver='local')))" % ("hbt:creator:" + key))
        result = subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True,
                                env={**os.environ, "HERMES_HOME": str(self.home / "profiles/ops")})
        job = json.loads(result.stdout)
        rec = hbt.load_record("creator")
        rec["jobs"].append({"key": key, "id": job["id"], "profile": "ops"})
        rec["board"] = "creator"
        rec["main_config"].update(kanban_before={"dispatch_in_gateway": False},
                                  kanban_applied={"dispatch_in_gateway": True})
        hbt.save_record("creator", rec)
        self.put(self.home / "profiles/ops/cron/output" / job["id"] / "prior.md", "prior result\n")
        self.put(self.home / "kanban/boards/creator/history", "existing board and history\n")
        return job

    def test_upgrade_pauses_exact_owned_job_preserves_history_and_is_repeatable(self):
        self.install()
        job = self.legacy_job()
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        rec = hbt.load_record("creator")
        self.assertTrue(rec["jobs"][0]["retired"])
        live = hbt.read_jobs_without_bootstrap("ops")[0]
        self.assertEqual(live["state"], "paused")
        self.assertIs(live["enabled"], False)
        output = self.home / "profiles/ops/cron/output" / job["id"] / "prior.md"
        self.assertEqual(output.read_text(), "prior result\n")
        archives = rec["retirement_archives"]
        self.assertTrue(any((Path(p) / "profiles/ops/cron/jobs.json").is_file() for p in archives))
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertEqual(hbt.load_record("creator")["retirement_archives"], archives)
        self.assertEqual(self.config.read_bytes(), self.original_config)
        self.assertEqual(self.run_hbt("uninstall", "creator", "-y"), 0)
        self.assertEqual((self.home / "kanban/boards/creator/history").read_text(), "existing board and history\n")
        self.assertEqual(self.config.read_bytes(), self.original_config)
        self.assertTrue(any((p / "profiles/ops/cron/output" / job["id"] / "prior.md").is_file()
                            for p in (hbt.record_dir("creator") / "backups").iterdir()))

    def test_upgrade_dry_run_is_read_only(self):
        self.install()
        self.legacy_job()
        before = hbt.package_hashes(self.home)
        # Use the actual dry-run command runner, not the side-effectful native double.
        with patch.object(hbt.Runner, "hermes_cmd", lambda *a, **kw: ""):
            self.assertEqual(self.run_hbt("update", "creator", "--dry-run"), 0)
        self.assertEqual(hbt.package_hashes(self.home), before)

    def test_job_mismatch_or_claim_refuses_before_any_changes(self):
        self.install()
        job = self.legacy_job()
        path = self.home / "profiles/ops/cron/jobs.json"
        original = json.loads(path.read_text())
        for change in ({"name": "owner-job"}, {"run_claim": {"by": "writer", "at": "2099-01-01"}},
                       {"fire_claim": {"by": "writer"}}):
            with self.subTest(change=change):
                data = copy.deepcopy(original)
                next(j for j in data["jobs"] if j["id"] == job["id"]).update(change)
                path.write_text(json.dumps(data))
                before = hbt.package_hashes(self.home)
                self.calls.clear()
                with self.assertRaises(SystemExit):
                    self.run_hbt("update", "creator")
                self.assertEqual(self.calls, [])
                self.assertEqual(hbt.package_hashes(self.home), before)

    def test_owner_script_changes_refuse_before_pause_or_restaging(self):
        self.install()
        self.legacy_job()
        old = "print('retired script')\n"
        self.put(hbt.record_dir("creator") / "dist/ops/scripts/hbt_old.py", old)
        self.put(self.home / "profiles/ops/scripts/hbt_old.py", old + "# owner edit\n")
        before = hbt.package_hashes(self.home)
        self.calls.clear()
        with self.assertRaisesRegex(SystemExit, "scripts"):
            self.run_hbt("update", "creator")
        self.assertEqual(self.calls, [])
        self.assertEqual(hbt.package_hashes(self.home), before)

    def test_pristine_retired_scripts_are_archived_and_removed(self):
        self.install()
        self.legacy_job()
        old = "print('retired script')\n"
        self.put(hbt.record_dir("creator") / "dist/ops/scripts/hbt_old.py", old)
        script = self.put(self.home / "profiles/ops/scripts/hbt_old.py", old)
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertFalse(script.exists())
        rec = hbt.load_record("creator")
        self.assertEqual((Path(rec["shared_skills"]["backups"][-1]) / "profiles/ops/scripts/hbt_old.py").read_text(), old)

    def test_unrelated_job_script_dependency_refuses_retired_script_removal(self):
        self.install()
        self.legacy_job()
        old = "print('shared old script')\n"
        self.put(hbt.record_dir("creator") / "dist/ops/scripts/hbt_old.py", old)
        self.put(self.home / "profiles/ops/scripts/hbt_old.py", old)
        path = self.home / "profiles/ops/cron/jobs.json"
        data = json.loads(path.read_text())
        other = copy.deepcopy(data["jobs"][0])
        other.update(id="abcdef012345", name="owner-custom", script="hbt_old.py")
        data["jobs"].append(other)
        path.write_text(json.dumps(data))
        before = hbt.package_hashes(self.home)
        with self.assertRaisesRegex(SystemExit, "unrelated job"):
            self.run_hbt("update", "creator")
        self.assertEqual(hbt.package_hashes(self.home), before)

    def test_setup_has_no_first_card_and_reports_unverified_herdr(self):
        self.run_hbt("install", "creator", "--roles", "cto,engineer", "--no-memory", "-y")
        rec = hbt.load_record("creator")
        rec["bots"] = {"cto": "U1234567", "engineer": "U2345678"}
        rec["setup"] = {"channels_ok": ["cto", "engineer"], "tested": ["cto", "engineer"],
                        "restarted": "fixture", "system_channel_ok": "skipped"}
        self.assertEqual(hbt.next_setup_step(self.tpl, rec), ("done", None))
        hbt.setup_completion(self.tpl, rec)
        self.assertIn("Herdr handoff was not tested", self.output.getvalue())

    def skill(self, folder, name, body="old template skill"):
        return self.put(folder / name / "SKILL.md", f"---\nname: {name}\n---\n{body}\n").parent

    def test_optional_watchdog_install_update_does_not_create_other_jobs(self):
        with patch.object(hbt, "openviking_ok", return_value=True):
            self.assertEqual(self.run_hbt("install", "creator", "--roles", "ops", "-y"), 0)
        jobs = hbt.read_jobs_without_bootstrap("ops")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["name"], "hbt:creator:memory-watchdog")
        self.assertIs(jobs[0]["no_agent"], True)
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertEqual(hbt.read_jobs_without_bootstrap("ops"), jobs)

    def test_same_name_unowned_job_refuses_and_unrelated_job_is_untouched(self):
        self.install()
        job = self.legacy_job()
        rec = hbt.load_record("creator")
        rec["jobs"] = []
        hbt.save_record("creator", rec)
        before = hbt.package_hashes(self.home)
        with self.assertRaisesRegex(SystemExit, "no recorded ownership"):
            self.run_hbt("update", "creator")
        self.assertEqual(hbt.package_hashes(self.home), before)
        path = self.home / "profiles/ops/cron/jobs.json"
        data = json.loads(path.read_text())
        data["jobs"][0]["name"] = "unrelated-owner-routine"
        path.write_text(json.dumps(data))
        before_job = copy.deepcopy(data["jobs"][0])
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertEqual(hbt.read_jobs_without_bootstrap("ops"), [before_job])
        self.assertEqual(before_job["id"], job["id"])

    def test_failed_pause_readback_stops_before_restaging(self):
        self.install()
        self.legacy_job()
        stage = hbt.record_dir("creator") / "dist"
        before = hbt.package_hashes(stage)
        self.calls.clear()
        def no_pause(_runner, *args, **kwargs):
            if args[:2] == ("cron", "pause"):
                return "pretend success"
            return self.command(*args, **kwargs)
        with patch.object(hbt.Runner, "hermes_cmd", no_pause), self.assertRaisesRegex(SystemExit, "readback failed"):
            self.run_hbt("update", "creator")
        self.assertEqual(hbt.package_hashes(stage), before)
        self.assertEqual(self.calls, [])
        self.assertTrue(hbt.load_record("creator")["retirement_archives"])
        self.assertEqual(self.run_hbt("update", "creator"), 0)

    def test_deleted_legacy_job_stays_deleted(self):
        self.install()
        self.legacy_job()
        (self.home / "profiles/ops/cron/jobs.json").write_text('{"jobs": []}')
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertTrue(hbt.load_record("creator")["jobs"][0]["retired"])
        self.assertEqual(hbt.read_jobs_without_bootstrap("ops"), [])

    def test_legacy_memory_identity_and_recovery_survive_retirement(self):
        self.install()
        job = self.legacy_job("memory-draft-review")
        path = self.home / "profiles/ops/cron/jobs.json"
        data = json.loads(path.read_text())
        data["jobs"][0].update(script="hbt_memory_review.py", no_agent=True, origin={"hbt_owner": "test-owner"})
        path.write_text(json.dumps(data))
        rec = hbt.load_record("creator")
        policy = {"schema_version": 1, "mode": "add-only", "install_root": str(self.home), "enrolled": [],
                  "policy_at": "fixture", "state_path": str(hbt.record_dir("creator") / "memory-review/state.json"),
                  "recovery_path": str(hbt.record_dir("creator") / "backups/memory-review"),
                  "job": {"id": job["id"], "profile": "ops", "created_at": job["created_at"], "owner": "test-owner"}}
        rec["memory_review"] = copy.deepcopy(policy)
        hbt.save_record("creator", rec)
        recovery = self.put(Path(policy["state_path"]), '{"synthetic": "pending receipt"}')
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertEqual(hbt.load_record("creator")["memory_review"], policy)
        self.assertEqual(recovery.read_text(), '{"synthetic": "pending receipt"}')
        data = json.loads(path.read_text())
        data["jobs"][0]["origin"] = {"hbt_owner": "other-owner"}
        path.write_text(json.dumps(data))
        before = hbt.package_hashes(self.home)
        with self.assertRaisesRegex(SystemExit, "identity changed"):
            self.run_hbt("update", "creator")
        self.assertEqual(hbt.package_hashes(self.home), before)

    def test_removed_setup_and_memory_routines_are_not_available(self):
        for name in ("setup_build_pair", "_finished_card", "_owner_review_guidance", "create_memory_review_job",
                     "sync_memory_review", "_sync_memory_review_locked", "memory_review_gaps"):
            self.assertFalse(hasattr(hbt, name), name)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            hbt.build_parser().parse_args(["install", "creator", "--memory-review", "off"])
        rec = {"memory": {"enabled": True}, "jobs": []}
        jobs = hbt.new_jobs(self.tpl, rec)
        self.assertEqual([j["key"] for j in jobs], ["memory-watchdog"])
        args = hbt.job_args(self.tpl, jobs[0], self.tpl.ops, "local", self.root)
        self.assertIn("--no-agent", args)
        with self.assertRaises(SystemExit):
            hbt.job_args(self.tpl, {"key": "custom-chat", "schedule": "0 * * * *", "prompt": "chat"},
                         self.tpl.ops, "local", self.root)

    def test_retired_shared_roots_detach_without_missing_source_or_losing_custom_files(self):
        self.run_hbt("install", "creator", "--roles", "creative-director", "--no-memory", "-y")
        rec = hbt.load_record("creator")
        shared = rec["shared_skills"]
        for role, name in (("creative-director", "creator-video-script"), ("ops", "creator-ops-nightly-review")):
            rel = f"template/{role}/{name}"
            path = self.skill(Path(shared["root"]) / "template" / role, name)
            shared["packages"][rel] = {"hashes": hbt.package_hashes(path)}
            shared["profiles"][role]["selected"] = [rel]
            shared["profiles"][role]["managed"] = [str(path)]
            custom = self.skill(self.root / "custom" / role, name, "owner external skill")
            cfg = hbt._profile_cfg(role)
            cfg["skills"]["external_dirs"] = [str(path), str(custom)]
            (self.home / "profiles" / role / "config.yaml").write_text(hbt.yaml.safe_dump(cfg))
            (path / "owner.txt").write_text("owner changed the shared package")
        hbt.save_record("creator", rec)
        custom_before = hbt.package_hashes(self.root / "custom")
        self.assertEqual(self.run_hbt("update", "creator"), 2)
        result = hbt.load_record("creator")["shared_skills"]
        for role in ("creative-director", "ops"):
            self.assertEqual(result["profiles"][role]["managed"], [])
            self.assertEqual(result["profiles"][role]["selected"], [])
            self.assertEqual(len(hbt._profile_cfg(role)["skills"]["external_dirs"]), 1)
        self.assertEqual(hbt.package_hashes(self.root / "custom"), custom_before)
        self.assertTrue(result["conflicts"])
        backup = Path(result["backups"][-1])
        self.assertEqual((backup / "skills/template/creative-director/creator-video-script/owner.txt").read_text(),
                         "owner changed the shared package")
        self.assertEqual(self.run_hbt("update", "creator"), 2)
        self.assertEqual(hbt.load_record("creator")["shared_skills"]["profiles"], result["profiles"])

    def test_legacy_local_retired_skills_remove_only_pristine_packages(self):
        self.install()
        rec = hbt.load_record("creator")
        rec.pop("shared_skills")
        stage = hbt.record_dir("creator") / "dist/ops/skills"
        local = self.home / "profiles/ops/skills"
        pristine = self.skill(stage, "creator-ops-morning-list")
        custom = self.skill(stage, "creator-ops-nightly-review")
        shutil.copytree(pristine, local / pristine.name)
        shutil.copytree(custom, local / custom.name)
        self.put(local / custom.name / "owner.txt", "owner bytes")
        hbt.save_record("creator", rec)
        self.assertEqual(self.run_hbt("update", "creator"), 2)
        self.assertFalse((local / pristine.name).exists())
        self.assertEqual((local / custom.name / "owner.txt").read_text(), "owner bytes")
        result = hbt.load_record("creator")["shared_skills"]
        self.assertEqual(result["profiles"]["ops"]["selected"], [])
        archive = Path(result["backups"][-1])
        self.assertTrue((archive / "profiles/ops/skills" / pristine.name / "SKILL.md").is_file())
        self.assertEqual(self.run_hbt("update", "creator"), 2)
        self.assertFalse((local / pristine.name).exists())

    def test_fresh_lifecycle_never_changes_dispatch_or_creates_board(self):
        self.assertEqual(self.install(), 0)
        rec = hbt.load_record("creator")
        self.assertFalse(rec.get("board"))
        self.assertEqual(rec["jobs"], [])
        self.assertNotIn("memory_review", rec)
        self.assertEqual(self.config.read_bytes(), self.original_config)
        generated = (Path(rec["workspace"]) / "ops/AGENTS.md").read_text().lower()
        self.assertNotIn("nightly checks", generated)
        self.assertNotIn("kanban board", generated)
        self.assertEqual(self.run_hbt("update", "creator"), 0)
        self.assertEqual(self.run_hbt("status", "creator"), 0)
        self.assertEqual(self.run_hbt("check", "creator", "--offline"), 0)
        self.assertEqual(self.run_hbt("uninstall", "creator", "-y"), 0)
        self.assertEqual(self.config.read_bytes(), self.original_config)
        self.assertFalse((self.home / "profiles/ops").exists())


if __name__ == "__main__":
    unittest.main()
