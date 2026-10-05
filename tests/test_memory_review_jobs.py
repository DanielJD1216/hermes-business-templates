"""Native owned-job lifecycle tests, opt-in only in an isolated runtime."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("hbt_memory_jobs_test", Path(__file__).resolve().parents[1] / "installer/hbt.py")
assert spec is not None and spec.loader is not None
hbt = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hbt
spec.loader.exec_module(hbt)


@unittest.skipUnless(os.environ.get("HBT_NATIVE_TEST") == "1", "requires isolated native runtime")
class MemoryJobs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {"HERMES_HOME": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.ops = self.root / "profiles/ops"
        (self.ops / "scripts").mkdir(parents=True)
        self.tpl = hbt.load_template("creator")
        (self.ops / "scripts/hbt_memory_review.py").write_bytes((self.tpl.path / "roles/ops/scripts/hbt_memory_review.py").read_bytes())
        (self.ops / "config.yaml").write_text("memory:\n  memory_enabled: false\n  user_profile_enabled: false\n")
        (self.ops / "hbt-settings.json").write_text('{"owner_setting": "keep"}')
        self.rec = {"profiles": ["ops", "engineer"], "jobs": [], "workspace": str(self.root / "workspace")}
        from cron import jobs
        self.native = jobs
        test = self
        class Runner:
            dry_run = False
            def hermes_cmd(self, *args, profile=None):
                assert profile == "ops"
                with patch.dict(os.environ, {"HERMES_HOME": str(test.ops)}):
                    return getattr(jobs, args[1] + "_job")(args[2])
        self.runner = Runner()

    def sync(self, mode=None):
        hbt.sync_memory_review(self.tpl, self.rec, mode, self.runner)

    def job(self):
        identity = self.rec["memory_review"]["job"]["id"]
        result = next((j for j in hbt.read_jobs_without_bootstrap("ops") if j["id"] == identity), None)
        assert result is not None
        return result

    def test_defaults_off_local_with_settings_preserved(self):
        self.sync()
        self.assertEqual(self.rec["memory_review"]["mode"], "off")
        self.assertEqual(self.rec["memory_review"]["enrolled"], ["engineer"])
        job = self.job()
        self.assertEqual(job["deliver"], "local")
        self.assertEqual(job["failure_deliver"], "local")
        self.assertFalse(job["enabled"])
        self.assertTrue(job["no_agent"])
        self.assertEqual(job["schedule"]["expr"], "30 21 * * *")
        self.assertEqual(json.loads((self.ops / "hbt-settings.json").read_bytes())["owner_setting"], "keep")

    def test_repeat_preserves_identity_pause_and_schedule(self):
        self.sync("add-only")
        identity = self.job()["id"]
        with patch.dict(os.environ, {"HERMES_HOME": str(self.ops)}):
            self.native.pause_job(identity)
            self.native.update_job(identity, {"schedule": self.native.parse_schedule("0 22 * * *")})
        self.sync()
        self.assertEqual(self.job()["id"], identity)
        self.assertFalse(self.job()["enabled"])
        self.assertEqual(self.job()["schedule"]["expr"], "0 22 * * *")
        self.assertEqual(len(hbt.read_jobs_without_bootstrap("ops")), 1)
        self.sync("add-replace")
        self.assertTrue(self.job()["enabled"])
        self.sync("off")
        self.assertFalse(self.job()["enabled"])

    def test_owner_deleted_job_not_recreated(self):
        self.sync("add-only")
        identity = self.job()["id"]
        with patch.dict(os.environ, {"HERMES_HOME": str(self.ops)}):
            self.native.remove_job(identity)
        self.sync("add-replace")
        self.assertEqual(hbt.read_jobs_without_bootstrap("ops"), [])

    def test_create_before_checkpoint_recovers_exact_nonce(self):
        create = hbt.create_memory_review_job
        def interrupted(policy):
            create(policy)
            raise OSError("synthetic create/checkpoint interruption")
        with patch.object(hbt, "create_memory_review_job", side_effect=interrupted), self.assertRaises(OSError):
            self.sync("add-only")
        original = hbt.read_jobs_without_bootstrap("ops")[0]
        self.rec = hbt.load_record("creator")
        self.sync()
        self.assertEqual(self.job()["id"], original["id"])
        self.assertEqual(len(hbt.read_jobs_without_bootstrap("ops")), 1)
        # Recovery without a new opt-in preserves the newly created paused state.
        self.assertFalse(self.job()["enabled"])

    def test_same_name_is_not_adopted(self):
        with patch.dict(os.environ, {"HERMES_HOME": str(self.ops)}):
            foreign = self.native.create_job("synthetic owner work", "0 12 * * *", name="hbt:creator:memory-draft-review", deliver="local")
        before = (self.ops / "cron/jobs.json").read_bytes()
        with self.assertRaises(SystemExit):
            self.sync("add-only")
        self.assertEqual((self.ops / "cron/jobs.json").read_bytes(), before)
        self.assertEqual(hbt.read_jobs_without_bootstrap("ops")[0]["id"], foreign["id"])

    def test_reused_identity_or_changed_transport_refused(self):
        self.sync()
        path = self.ops / "cron/jobs.json"
        pristine = path.read_bytes()
        for key, value in [("origin", {}), ("created_at", "changed"), ("deliver", "slack:synthetic")]:
            data = json.loads(pristine)
            data["jobs"][0][key] = value
            path.write_text(json.dumps(data))
            with self.assertRaises(SystemExit):
                self.sync("add-only")
        path.write_bytes(pristine)

    def test_dry_run_writes_nothing(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.runner.dry_run = True
        self.sync("add-only")
        after = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertNotIn("memory_review", self.rec)

    def test_slack_wiring_excludes_memory_review(self):
        self.sync()
        identity = self.job()["id"]
        self.rec["channels"] = {self.tpl.system_channel: "synthetic-channel"}
        calls = []
        with patch.object(self.runner, "hermes_cmd", side_effect=lambda *args, **kw: calls.append(args)), patch.object(hbt, "edit_main_config", return_value={"routes_added": []}):
            hbt.wire_system_channel(self.runner, self.tpl, self.rec, False)
        self.assertFalse(any(identity in args for args in calls))
        self.assertEqual(self.job()["deliver"], "local")


if __name__ == "__main__":
    unittest.main()
