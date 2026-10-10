"""Global read-only uninstall refusal and bounded preservation, synthetic data only."""
import copy
import contextlib
import io
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("hbt_uninstall_test", Path(__file__).resolve().parents[1] / "installer/hbt.py")
assert spec is not None and spec.loader is not None
hbt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hbt
spec.loader.exec_module(hbt)


class UninstallPreflight(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {"HERMES_HOME": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.rec = {"profiles": ["engineer", "ops"], "jobs": [], "version": "0.4.0", "workspace": str(self.root / "workspace")}
        for name in self.rec["profiles"]:
            self.put(name, "config.yaml", "memory: {}\n")
        hbt.record_dir("creator").mkdir(parents=True)

    def put(self, name, relative, text):
        p = self.root / "profiles" / name / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def refusal(self):
        before = self.snapshot()
        with self.assertRaises(SystemExit):
            hbt.uninstall_inventory("creator", self.rec)
        self.assertEqual(before, self.snapshot())

    def test_later_profile_unknown_data_refuses_without_writes(self):
        self.put("ops", "owner-notes.txt", "synthetic owner note")
        self.refusal()

    def test_unowned_jobs_all_states_refuse(self):
        for enabled, state in [(True, "scheduled"), (False, "paused"), (False, "disabled")]:
            with self.subTest(state=state):
                self.put("ops", "cron/jobs.json", json.dumps({"jobs": [{"id": "abcdef012345", "name": "hbt:creator:memory-draft-review", "enabled": enabled, "state": state}]}))
                self.refusal()

    def test_owned_jobs_and_deleted_jobs_are_safe(self):
        self.rec["jobs"] = [{"profile": "ops", "id": "abcdef012345", "key": "morning-approvals"}]
        self.put("ops", "cron/jobs.json", json.dumps({"jobs": [{"id": "abcdef012345", "name": "hbt:creator:morning-approvals", "state": "paused"}]}))
        hbt.uninstall_inventory("creator", self.rec)
        self.put("ops", "cron/jobs.json", '{"jobs": []}')
        hbt.uninstall_inventory("creator", self.rec)

    def test_malformed_duplicate_or_missing_id_refuse(self):
        for value in ["bad", "{}", '{"jobs": [{}]}', json.dumps({"jobs": [{"id": "abcdef012345"}] * 2})]:
            self.put("ops", "cron/jobs.json", value)
            self.refusal()

    def test_covered_custom_files_have_exact_private_archives(self):
        names = ["skills/custom/SKILL.md", "memories/USER.md", "pending/memory/01234567.json", "backups/config/config.yaml.good.20260101-010101", "logs/agent.log", "logs/errors.log.1", "auth.lock"]
        for relative in names:
            self.put("ops", relative, "synthetic current bytes: " + relative)
        before = self.snapshot()
        inventory = hbt.uninstall_inventory("creator", self.rec)
        self.assertEqual(before, self.snapshot())
        archive = hbt.archive_uninstall_inventory("creator", self.rec, inventory)
        for relative in names:
            p = archive / "profiles/ops" / relative
            self.assertEqual(p.read_bytes(), (self.root / "profiles/ops" / relative).read_bytes())
            self.assertEqual(p.stat().st_mode & 0o777, 0o600)
        self.assertEqual(archive.stat().st_mode & 0o777, 0o700)

    def test_same_directory_sentinels_refuse(self):
        for relative in ["logs/owner-note", "backups/config/owner-note", "scripts/owner.py", "pending/skills/01234567.json", "auth.json", "auth.lock.backup"]:
            p = self.put("ops", relative, "synthetic")
            self.refusal()
            p.unlink()

    def test_changed_covered_bytes_are_not_justified_by_stale_archive(self):
        p = self.put("ops", "logs/agent.log", "old synthetic")
        old = hbt.uninstall_inventory("creator", self.rec)
        hbt.archive_uninstall_inventory("creator", self.rec, old)
        p.write_text("new synthetic")
        current = hbt.uninstall_inventory("creator", self.rec)
        self.assertNotEqual(old, current)
        fresh = hbt.archive_uninstall_inventory("creator", self.rec, current)
        self.assertEqual((fresh / "profiles/ops/logs/agent.log").read_text(), "new synthetic")

    def test_symlinks_refuse(self):
        p = self.root / "profiles/ops/logs"
        p.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(SystemExit):
            hbt.uninstall_inventory("creator", self.rec)

    def test_backup_failure_does_not_change_source(self):
        self.put("ops", "logs/agent.log", "synthetic log")
        inventory = hbt.uninstall_inventory("creator", self.rec)
        with patch.object(hbt, "private_archive_file", side_effect=PermissionError), self.assertRaises(PermissionError):
            hbt.archive_uninstall_inventory("creator", self.rec, inventory)
        self.assertEqual((self.root / "profiles/ops/logs/agent.log").read_text(), "synthetic log")
        self.assertNotIn("memory_uninstall_archives", self.rec)

    def test_ancestor_skill_does_not_cover_sibling(self):
        self.put("engineer", "config.yaml", "skills:\n  external_dirs:\n    - " + str(self.root / "profiles") + "\n")
        self.put("ops", "custom/example/SKILL.md", "---\nname: example\n---\nSynthetic skill")
        hbt.uninstall_inventory("creator", self.rec)
        self.put("ops", "custom/owner-note", "synthetic note")
        self.refusal()


    def uninstall_args(self, dry=False):
        self.rec.setdefault("memory", {"accounts": []})
        hbt.save_record("creator", self.rec)
        return hbt.build_parser().parse_args(["uninstall", "creator", "-y"] + (["--dry-run"] if dry else []))

    def test_global_command_refuses_combined_conflicts_before_native_calls(self):
        self.put("ops", "owner-note", "synthetic owner note")
        self.put("ops", "cron/jobs.json", json.dumps({"jobs": [{"id": "abcdef012345", "name": "synthetic owner workload", "enabled": False, "state": "paused"}]}))
        for dry in (False, True):
            args = self.uninstall_args(dry)
            before = self.snapshot()
            with patch.object(hbt.Runner, "hermes_cmd", side_effect=AssertionError("native mutation forbidden")) as native, self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
                hbt.cmd_uninstall(args)
            native.assert_not_called()
            self.assertEqual(before, self.snapshot())

    def test_native_empty_env_only_is_disposable(self):
        self.put("engineer", ".env", "\n")
        hbt.uninstall_inventory("creator", self.rec)
        self.put("engineer", ".env", "SYNTHETIC_SETTING=fixture\n")
        self.refusal()

    def test_unreadable_store_refuses(self):
        path = self.put("ops", "cron/jobs.json", '{"jobs": []}')
        path.chmod(0)
        with self.assertRaises(SystemExit):
            hbt.uninstall_inventory("creator", self.rec)
        path.chmod(0o600)

    def test_stale_archive_does_not_cover_unknown_changed_file(self):
        archive = hbt.record_dir("creator") / "backups/known"
        archived = archive / "profiles/ops/owner-note"
        archived.parent.mkdir(parents=True)
        archived.write_text("old synthetic")
        self.rec["memory_uninstall_archives"] = [str(archive)]
        self.put("ops", "owner-note", "old synthetic")
        hbt.uninstall_inventory("creator", self.rec)
        self.put("ops", "owner-note", "new synthetic")
        self.refusal()

    def test_inventory_race_stops_before_native_delete(self):
        args = self.uninstall_args()
        original = hbt.archive_uninstall_inventory
        def changed(*a):
            result = original(*a)
            self.put("ops", "logs/agent.log", "new synthetic writer")
            return result
        with patch.object(hbt, "archive_uninstall_inventory", side_effect=changed), patch.object(hbt.Runner, "hermes_cmd") as native, contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            hbt.cmd_uninstall(args)
        native.assert_not_called()
        self.assertTrue((self.root / "profiles/engineer").exists())
        self.assertTrue(list((hbt.record_dir("creator") / "backups").glob("memory-uninstall-*")))

    def test_job_race_stops_before_native_delete(self):
        args = self.uninstall_args()
        original = hbt.archive_uninstall_inventory
        def changed(*a):
            result = original(*a)
            self.put("ops", "cron/jobs.json", json.dumps({"jobs": [{"id": "abcdef012345", "name": "new synthetic workload"}]}))
            return result
        with patch.object(hbt, "archive_uninstall_inventory", side_effect=changed), patch.object(hbt.Runner, "hermes_cmd") as native, contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            hbt.cmd_uninstall(args)
        native.assert_not_called()
        self.assertTrue((self.root / "profiles/engineer").exists())

    def test_permission_failure_stops_before_native_delete(self):
        args = self.uninstall_args()
        with patch.object(hbt, "private_archive_file", side_effect=PermissionError), patch.object(hbt.Runner, "hermes_cmd") as native, contextlib.redirect_stdout(io.StringIO()), self.assertRaises(PermissionError):
            hbt.cmd_uninstall(args)
        native.assert_not_called()
        self.assertTrue((self.root / "profiles/engineer").exists())


if __name__ == "__main__":
    unittest.main()
