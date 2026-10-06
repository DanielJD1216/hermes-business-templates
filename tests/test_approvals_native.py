"""G3 native parser/handler proof. Requires a guarded disposable runtime.

Run with HBT_NATIVE_TEST=1 only after HOME, HERMES_HOME and TMPDIR are isolated,
credentials are hidden, lazy installs are disabled and network access is blocked.
No dispatcher, gateway, model, provider or Slack transport is started.
"""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_approvals import RECORD, SCRIPT, URL, digest



@unittest.skipUnless(os.environ.get("HBT_NATIVE_TEST") == "1", "requires isolated native runtime")
class NativeOwnerReview(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / ".hermes"
        self.home.mkdir()
        self.env = patch.dict(os.environ, {"HOME": str(self.root), "HERMES_HOME": str(self.home),
                                           "HERMES_KANBAN_HOME": str(self.home)})
        self.env.start()
        self.addCleanup(self.env.stop)
        from hermes_cli import kanban, kanban_db, kanban_db_connect, kanban_db_notify
        self.cli, self.kb, self.connect, self.notify = kanban, kanban_db, kanban_db_connect, kanban_db_notify
        self.parser = argparse.ArgumentParser()
        kanban.build_parser(self.parser.add_subparsers(dest="command"))
        self.kb.create_board("creator")
        self.scope = self.kb.scoped_current_board("creator")
        self.scope.__enter__()
        self.addCleanup(self.scope.__exit__, None, None, None)
        self.calls = []
        self.sentinels = {
            "config.yaml": b"kanban:\n  review_dispatch: false\n  dispatch_in_gateway: false\n",
            "credential-sentinel": b"synthetic-only", "canon/business.md": b"owner canon",
            "memories/USER.md": b"owner context", "memories/MEMORY.md": b"role memory",
            "business-templates/creator/memory-policy.json": b'{"mode":"add-only"}',
            "cron/jobs.json": b'{"jobs":[]}',
        }
        for name, data in self.sentinels.items():
            path = self.home / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        # This thin executable uses the real native parser and handlers, not mocked responses.
        binary = self.root / "bin/hermes"
        binary.parent.mkdir()
        binary.write_text(f"#!{sys.executable}\n"
                          "import argparse,sys\nfrom hermes_cli import kanban\n"
                          "p=argparse.ArgumentParser()\nkanban.build_parser(p.add_subparsers(dest='command'))\n"
                          "raise SystemExit(kanban.kanban_command(p.parse_args()))\n")
        binary.chmod(0o700)
        os.environ["PATH"] = str(binary.parent) + os.pathsep + os.environ["PATH"]

    def command(self, *args, expected=0):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.cli.kanban_command(self.parser.parse_args(["kanban", "--board", "creator", *args]))
        self.calls.append((args, code))
        self.assertEqual(code, expected, err.getvalue())
        return out.getvalue(), err.getvalue()

    def read(self, *args):
        return json.loads(self.command(*args)[0])

    def create_review(self):
        with self.connect.connect_closing() as conn:
            card = self.kb.create_task(conn, title="Synthetic native draft", assignee="engineer",
                                       created_by="synthetic-owner", workspace_kind="dir",
                                       workspace_path=str(self.root / "projects/hello-world"),
                                       completion_contract="local-only")
            self.notify.add_notify_sub(conn, task_id=card, platform="slack", chat_id=RECORD["chat_id"],
                                       thread_id=RECORD["thread_id"], notifier_profile="cto", delivery_mode="notify",
                                       delivery_metadata={"thread_id": RECORD["thread_id"], "scope_id": "T00000001"})
            self.notify.add_notify_sub(conn, task_id=card, platform="slack", chat_id="C00000002",
                                       notifier_profile="engineer", delivery_mode="notify")
        self.command("request-review", card, "--summary", "Synthetic checked draft",
                     "--metadata", json.dumps({"approval_thread": RECORD}))
        detail = self.read("show", card, "--json")
        self.assertEqual(detail["task"]["status"], "review")
        self.assertEqual(detail["task"]["assignee"], "engineer")
        self.assertEqual(detail["runs"][-1]["metadata"]["approval_thread"], RECORD)
        return card

    def assert_sentinels(self):
        for name, data in self.sentinels.items():
            self.assertEqual((self.home / name).read_bytes(), data, name)

    def test_owner_complete_uses_exact_command_and_preserves_assignment(self):
        card = self.create_review()
        self.command("complete", card, "--summary", "Owner approved this draft only")
        detail = self.read("show", card, "--json")
        self.assertEqual(detail["task"]["status"], "done")
        self.assertEqual(detail["task"]["assignee"], "engineer")
        self.assertEqual(detail["runs"][-1]["summary"], "Owner approved this draft only")
        self.assert_sentinels()

    def test_owner_reopen_records_reason_and_rejects_idle_request_changes(self):
        card = self.create_review()
        self.command("request-changes", card, "Required fixture change", expected=1)
        self.assertEqual(self.read("show", card, "--json")["task"]["status"], "review")
        self.command("reopen-review", card, "--reason", "Required fixture change")
        detail = self.read("show", card, "--json")
        self.assertEqual(detail["task"]["status"], "ready")
        self.assertEqual(detail["task"]["assignee"], "engineer")
        self.assertIn("CHANGES REQUESTED: Required fixture change", [c["body"] for c in detail["comments"]])
        self.assert_sentinels()

    def test_owner_archive_stops_without_done_and_preserves_record(self):
        card = self.create_review()
        self.command("archive", card)
        detail = self.read("show", card, "--json")
        self.assertEqual(detail["task"]["status"], "archived")
        self.assertEqual(detail["task"]["assignee"], "engineer")
        self.assertFalse(any(event["kind"] == "completed" for event in detail["events"]))
        self.assertNotIn(card, [c["id"] for c in self.read("list", "--status", "review", "--json")])
        self.assert_sentinels()

    def test_review_metadata_native_show_and_real_formatter_subprocess(self):
        card = self.create_review()
        subscriptions = self.read("notify-list", card, "--json")
        before = {name: (self.home / name).read_bytes() for name in self.sentinels}
        details_before = self.read("show", card, "--json")
        output = digest.format_digest(digest.collect(self.read))
        self.assertIn(f"Synthetic native draft ({card})", output)
        self.assertIn("approval thread " + URL, output)
        result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("approval thread " + URL, result.stdout)
        self.assertEqual(self.read("notify-list", card, "--json"), subscriptions)
        self.assertEqual(self.read("show", card, "--json"), details_before)
        self.assertEqual({name: (self.home / name).read_bytes() for name in self.sentinels}, before)
        # Only these native reads are invoked by the collector. Native list may recompute dependencies.
        self.assertTrue(all(args[0] in {"request-review", "show", "notify-list", "list"} for args, _ in self.calls))
        self.assert_sentinels()

    def test_native_superseded_review_never_reuses_old_link(self):
        card = self.create_review()
        self.command("reopen-review", card, "--reason", "Second draft")
        self.command("request-review", card, "--summary", "New draft without known link", "--metadata", "{}")
        detail = self.read("show", card, "--json")
        reviews = [e for e in detail["events"] if e["kind"] == "review_requested"]
        self.assertEqual(len(reviews), 2)
        self.assertNotEqual(reviews[0]["run_id"], reviews[1]["run_id"])
        output = digest.format_digest(digest.collect(self.read))
        self.assertIn("approval thread link unavailable", output)
        self.assertNotIn(URL, output)
        self.assert_sentinels()

    def test_native_empty_digest_exact_output(self):
        self.assertEqual(digest.format_digest(digest.collect(self.read)), "Nothing waiting for approval.")
        result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Nothing waiting for approval.\n")
        self.assert_sentinels()

    def test_claimed_worker_review_handoff_is_consumed(self):
        with self.connect.connect_closing() as conn:
            card = self.kb.create_task(conn, title="Claimed draft", assignee="engineer",
                                       workspace_kind="dir", workspace_path=str(self.root / "projects/hello-world"),
                                       completion_contract="local-only")
            claimed = self.kb.claim_task(conn, card, claimer="synthetic-worker")
            self.assertIsNotNone(claimed)
            self.assertTrue(self.kb.request_review(conn, card, summary="Checked worker draft",
                                                  metadata={"approval_thread": RECORD},
                                                  expected_run_id=claimed.current_run_id))
        detail = self.read("show", card, "--json")
        self.assertEqual(detail["runs"][-1]["status"], "review")
        self.assertEqual(detail["task"]["assignee"], "engineer")
        self.assertIn("approval thread " + URL, digest.format_digest(digest.collect(self.read)))
        self.assert_sentinels()


if __name__ == "__main__":
    unittest.main()
