"""Synthetic G3 owner guidance and recorded-thread digest checks, no transport."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import subprocess
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import test_installer
from test_installer import TPL, hbt, load

SCRIPT = TPL / "roles/ops/skills/creator-ops-morning-list/scripts/format_approvals.py"
digest = load("format_approvals", SCRIPT)
NOW = 1800000000
THREAD = "1799990000.123456"
CHANNEL = "C00000001"
URL = f"https://fixture-workspace.slack.com/archives/{CHANNEL}/p{THREAD.replace('.', '')}"
RECORD = dict(platform="slack", workspace_url="https://fixture-workspace.slack.com",
              chat_id=CHANNEL, thread_id=THREAD, url=URL)


def entry(card_id="t_00000001", role="engineer", age=3600):
    return ({"task": {"id": card_id, "status": "review", "assignee": role,
                      "title": "Synthetic draft", "created_at": 1},
             "events": [{"kind": "review_requested", "run_id": 7, "created_at": NOW - age}],
             "runs": [{"id": 7, "outcome": "review_requested", "status": "review",
                       "metadata": {"approval_thread": copy.deepcopy(RECORD)}}]}, [])


class RecordedThreads(unittest.TestCase):
    def test_valid_recorded_root_and_query_returned_unchanged(self):
        for suffix in ("", f"?thread_ts={THREAD}&cid={CHANNEL}", f"?cid={CHANNEL}"):
            with self.subTest(suffix=suffix):
                detail, subs = entry()
                detail["runs"][0]["metadata"]["approval_thread"]["url"] += suffix
                self.assertEqual(digest.format_digest([(detail, subs)], NOW),
                                 "engineer:\n- Synthetic draft (t_00000001), waiting 1h 0m, approval thread " + URL + suffix)

    def test_invalid_and_missing_provenance_retains_card_identity(self):
        records = [None, [], {}, "legacy", RECORD | {"platform": "tui"},
                   RECORD | {"workspace_url": "https://other-workspace.slack.com"},
                   RECORD | {"chat_id": "C00000002"}, RECORD | {"thread_id": "1799990000.654321"},
                   RECORD | {"chat_id": "not-a-channel"}, RECORD | {"thread_id": "123.4"},
                   RECORD | {"url": ""}]
        bad_urls = ["http://fixture-workspace.slack.com/archives/" + CHANNEL + "/p" + THREAD.replace('.', ''),
                    URL.replace(".slack.com", ".slack.com.evil.test"), URL.replace("https://", "https://user@"),
                    URL.replace(".com/", ".com:443/"), URL + "#fragment", URL + "#", URL.replace("p179999", "p179998"),
                    "/archives/" + CHANNEL, URL.rsplit("/", 1)[0], URL + "?cid=C00000002",
                    URL + f"?cid={CHANNEL}&cid={CHANNEL}", URL + "?thread_ts=1799990000.654321",
                    URL + "?broken", URL + "?unknown=value", URL + "\n", URL.replace("https:", "https:\t")]
        records += [RECORD | {"url": url} for url in bad_urls]
        for origin in ("https://slack.com", "https://api.slack.com", "https://x.slack.com.evil.test",
                       "https://fixture-workspace.slack.com/", "https://user@fixture-workspace.slack.com",
                       "https://fixture-workspace.slack.com:443", "https://fixture-workspace.slack.com?",
                       "https://fixture-workspace.slack.com#", "https://bad_name.slack.com"):
            records.append(RECORD | {"workspace_url": origin})
        for record in records:
            with self.subTest(record=record):
                detail, subs = entry()
                detail["runs"][0]["metadata"]["approval_thread"] = record
                out = digest.format_digest([(detail, subs)], NOW)
                self.assertIn("Synthetic draft (t_00000001)", out)
                self.assertIn("approval thread link unavailable (", out)
                self.assertNotIn("https://", out)

    def test_subscriptions_only_corroborate_identified_origin(self):
        detail, _ = entry()
        origin = dict(platform="slack", chat_id=CHANNEL, thread_id=THREAD,
                      delivery_metadata={"thread_id": THREAD, "scope_id": "T00000001"})
        result = dict(platform="slack", chat_id="C00000002", thread_id="",
                      delivery_metadata=None, notifier_profile="engineer", delivery_mode="notify")
        for subscriptions in ([], [origin], [result, origin], [origin, result], [result]):
            self.assertIn("approval thread " + URL, digest.format_digest([(detail, subscriptions)], NOW))
        detail["runs"][0]["metadata"] = {}
        for subscriptions in ([result], [origin, result]):
            self.assertIn("link unavailable", digest.format_digest([(detail, subscriptions)], NOW))

    def test_conflicting_identified_origin_is_unavailable(self):
        detail, _ = entry()
        sub: dict[str, Any] = dict(platform="slack", chat_id=CHANNEL, thread_id=THREAD)
        for key in RECORD:
            sub["delivery_metadata"] = {key: "contradiction"}
            self.assertIn("conflicting identified-origin evidence", digest.format_digest([(detail, [sub])], NOW))
        sub["delivery_metadata"] = "invalid"
        self.assertIn("malformed identified-origin evidence", digest.format_digest([(detail, [sub])], NOW))

    def test_latest_review_not_completion_comments_or_old_handoff(self):
        detail, subs = entry()
        detail["comments"] = [{"body": URL}]
        detail["events"].append({"kind": "review_requested", "run_id": 9, "created_at": NOW - 60})
        detail["runs"].extend([
            {"id": 8, "status": "done", "outcome": "completed", "metadata": {"approval_thread": RECORD}},
            {"id": 9, "status": "review", "outcome": "review_requested", "metadata": {}}])
        out = digest.format_digest([(detail, subs)], NOW)
        self.assertIn("waiting 0h 1m", out)
        self.assertIn("link unavailable", out)
        self.assertNotIn(URL, out)

    def test_missing_or_ambiguous_current_event_run(self):
        cases = []
        for field, value in [("events", []), ("events", None), ("runs", []), ("runs", None)]:
            detail, subs = entry()
            detail[field] = value
            cases.append((detail, subs))
        for mutation in ("duplicate-run", "duplicate-event", "wrong-outcome", "missing-metadata", "missing-run-id", "bad-status"):
            detail, subs = entry()
            if mutation == "duplicate-run":
                detail["runs"].append(copy.deepcopy(detail["runs"][0]))
            elif mutation == "duplicate-event":
                detail["events"].append(copy.deepcopy(detail["events"][0]))
            elif mutation == "wrong-outcome":
                detail["runs"][0]["outcome"] = "completed"
            elif mutation == "missing-metadata":
                detail["runs"][0].pop("metadata")
            elif mutation == "bad-status":
                detail["runs"][0]["status"] = []
            else:
                detail["events"][0].pop("run_id")
            cases.append((detail, subs))
        for detail, subs in cases:
            with self.subTest(detail=detail):
                self.assertIn("link unavailable", digest.format_digest([(detail, subs)], NOW))

    def test_grouping_current_age_and_label_sanitation(self):
        young = entry("t_00000002", age=60)
        old = entry("t_00000001", age=90000)
        other = entry("t_00000003", role="creative-director")
        unknown = entry("t_00000004")
        unknown[0]["events"][0]["created_at"] = None
        young[0]["task"]["title"] = "Line\n\x00two\u2014done\u2013yes"
        out = digest.format_digest([young, unknown, old, other], NOW)
        self.assertLess(out.index("creative-director:"), out.index("engineer:"))
        self.assertLess(out.index("t_00000001"), out.index("t_00000002"))
        self.assertLess(out.index("t_00000002"), out.index("t_00000004"))
        self.assertIn("waiting 1d 1h", out)
        self.assertIn("Line two-done-yes", out)
        self.assertIn("waiting time unavailable", out)
        for char in ("\x00", "\u2013", "\u2014"):
            self.assertNotIn(char, out)
        for value in (None, True, float("nan"), float("inf"), 10 ** 1000, -1, "yesterday", "2027-01-01", NOW + 1):
            detail, subs = entry()
            detail["events"][0]["created_at"] = value
            self.assertIn("waiting time unavailable", digest.format_digest([(detail, subs)], NOW))
        detail, subs = entry()
        detail["events"][0]["created_at"] = digest.dt.datetime.fromtimestamp(NOW - 3600, digest.dt.timezone.utc).isoformat()
        self.assertIn("waiting 1h 0m", digest.format_digest([(detail, subs)], NOW))

    def test_collection_only_reads_exact_native_commands(self):
        detail, subs = entry()
        read = Mock(side_effect=[[detail["task"]], detail, subs])
        self.assertEqual(digest.collect(read), [(detail, subs)])
        self.assertEqual([c.args for c in read.call_args_list], [
            ("list", "--status", "review", "--json"), ("show", "t_00000001", "--json"),
            ("notify-list", "t_00000001", "--json")])
        with patch.object(digest.subprocess, "run", return_value=Mock(stdout="[]")) as run:
            self.assertEqual(digest.read_json("list", "--status", "review", "--json"), [])
        self.assertEqual(run.call_args.args[0], ["hermes", "kanban", "--board", "creator", "list", "--status", "review", "--json"])
        self.assertTrue(run.call_args.kwargs["check"])
        self.assertEqual(run.call_args.kwargs["timeout"], 30)

    def test_command_failure_and_empty_success_are_distinct(self):
        for error in (OSError("private"), subprocess.CalledProcessError(1, "hermes", output="private"),
                      subprocess.TimeoutExpired("hermes", 30)):
            with patch.object(digest.subprocess, "run", side_effect=error):
                with self.assertRaisesRegex(digest.DigestError, "local Kanban read failed"):
                    digest.read_json("list")
        with patch.object(digest.subprocess, "run", return_value=Mock(stdout="not JSON")):
            with self.assertRaises(digest.DigestError):
                digest.read_json("list")
        for collected, code, expected in [([], 0, "Nothing waiting for approval.\n"),
                                          (digest.DigestError("local Kanban read failed"), 1,
                                           "Approval digest failed (local Kanban read failed).\n")]:
            out = io.StringIO()
            collect_mock = Mock(side_effect=collected) if isinstance(collected, Exception) else Mock(return_value=collected)
            with patch.object(digest, "collect", collect_mock), contextlib.redirect_stdout(out):
                self.assertEqual(digest.main(), code)
            self.assertEqual(out.getvalue(), expected)

    def test_malformed_collections_fail_honestly(self):
        for cards in ({}, None, [None], [{"id": "bad"}], [{"id": "t_00000001"}] * 2):
            detail, subs = entry()
            with self.assertRaises(digest.DigestError):
                digest.collect(Mock(side_effect=[cards, detail, subs]))
        detail, subs = entry()
        with self.assertRaises(digest.DigestError):
            digest.collect(Mock(side_effect=[[{"id": "t_00000002"}], detail, subs]))
        for field, value in (("status", "done"), ("id", "bad")):
            detail, subs = entry()
            detail["task"][field] = value
            with self.assertRaises(digest.DigestError):
                digest.format_digest([(detail, subs)])
        with self.assertRaises(digest.DigestError):
            digest.format_digest([entry(), entry()])
        with self.assertRaises(digest.DigestError):
            digest.format_digest([(entry()[0], [None])])


class FirstCard(unittest.TestCase):
    def setUp(self):
        self.tpl = hbt.load_template("creator")
        self.card = dict(id="t_00000001", assignee="engineer", status="done", created_at=NOW,
                         workspace_kind="dir", workspace_path="/srv/projects/hello-world", title="Hello")

    def finished(self, cards, since: float = NOW, workspace="/srv/projects/hello-world"):
        runner = Mock()
        runner.hermes_cmd.return_value = json.dumps(cards)
        with patch("time.time", return_value=NOW + 10):
            result = hbt._finished_card(runner, self.tpl, "engineer", since, workspace)
        if runner.hermes_cmd.called:
            self.assertEqual(runner.hermes_cmd.call_args.args,
                             ("kanban", "--board", "creator", "list", "--assignee", "engineer", "--status", "done", "--json"))
            self.assertFalse(runner.hermes_cmd.call_args.kwargs["mutate"])
        return result

    def test_exact_workspace_epoch_iso_and_normalization(self):
        for created in (NOW, float(NOW), digest.dt.datetime.fromtimestamp(NOW, digest.dt.timezone.utc).isoformat()):
            card = self.card | {"created_at": created, "workspace_path": "/srv/projects/./hello-world/"}
            self.assertEqual(self.finished([card]), card)
            self.assertEqual(self.finished({"tasks": [card]}), card)

    def test_reject_unrelated_incomplete_ambiguous_and_invalid(self):
        mutations = [dict(status=status) for status in ("review", "ready", "todo", "archived", "blocked", "running")]
        mutations += [dict(assignee="cto"), dict(assignee=None), dict(workspace_kind="scratch"),
                      dict(workspace_path="/srv/projects/other"), dict(workspace_path=None),
                      dict(workspace_path="hello-world"), dict(id=None), dict(id="bad")]
        mutations += [dict(created_at=value) for value in (NOW - 61, NOW + 60, True, None, -1, 0, 10 ** 1000,
                      float("nan"), float("inf"), "invalid", "2026-01-01T00:00:00")]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.assertIsNone(self.finished([self.card | mutation]))
        for cards in (None, {}, [None], [self.card, self.card], [self.card, self.card | {"id": "t_00000002"}]):
            self.assertIsNone(self.finished(cards))
        self.assertIsNone(self.finished([self.card], workspace="relative"))
        self.assertIsNone(self.finished([self.card], since=float("nan")))
        self.assertEqual(self.finished([self.card | {"created_at": NOW - 60}])["id"], self.card["id"])
        for raw in ("not JSON", "", None):
            self.assertIsNone(hbt._finished_card(Mock(hermes_cmd=Mock(return_value=raw)), self.tpl,
                                               "engineer", NOW, "/srv/projects/hello-world"))

    def test_known_id_guidance(self):
        out = hbt._owner_review_guidance("creator", self.card["id"])
        for verb in ("complete", "reopen-review", "archive"):
            self.assertIn(f"!kanban --board creator {verb} t_00000001", out)
        self.assertNotIn("--force", out)
        self.assertNotIn("--rm", out)
        self.assertIn("without reviewer reassignment", out)
        self.assertIn("not a second confirmation", out)


class SetupOwnerReview(unittest.TestCase):
    root: Path
    setUp = test_installer.GuidedSetup.setUp

    def run_first_card(self, status):
        tpl = hbt.load_template("creator")
        rec = {"version": tpl.version, "profiles": ["cto", "engineer"], "projects": str(self.root / "projects"),
               "workspace": str(self.root / "workspace"),
               "bots": {"cto": "U00000001", "engineer": "U00000002"},
               "setup": {"channels_ok": ["cto", "engineer"], "tested": ["cto", "engineer"], "restarted": "fixture",
                         "build_demo": True}}
        hbt.save_record(tpl.name, rec)
        sentinels = {"config.yaml": b"kanban:\n  review_dispatch: false\n",
                     "credential-sentinel": b"synthetic-not-a-credential", "canon/business.md": b"owner canon",
                     "memories/USER.md": b"owner context", "memories/MEMORY.md": b"role memory",
                     "memory-policy.json": b'{"mode":"add-only"}', "cron/jobs.json": b'{"jobs":[]}',
                     "subscriptions.json": b'[{"platform":"tui","chat_id":"synthetic"}]'}
        for name, data in sentinels.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        before = hbt.package_hashes(self.root)
        card = dict(id="t_00000001", assignee="engineer", status=status, created_at=NOW,
                    workspace_kind="dir", workspace_path=str(self.root / "projects/hello-world"), title="Hello")
        messages = []
        def query(*args, **kwargs):
            self.assertTrue(any("Approve draft: !kanban" in text for text in messages))
            return json.dumps([] if status == "timeout" else [card])
        with patch.object(hbt, "_wait", side_effect=messages.append), patch.object(hbt, "say", side_effect=messages.append), \
             patch.object(hbt.Runner, "hermes_cmd", side_effect=query), patch("time.time", return_value=NOW), \
             patch("time.sleep"), patch.object(hbt, "slack_api", side_effect=AssertionError("no transport")):
            code = hbt.cmd_setup(hbt.build_parser().parse_args(["setup", "creator"]))
        after = hbt.package_hashes(self.root)
        changed = {key for key in before.keys() | after.keys() if before.get(key) != after.get(key)}
        record_path = str((hbt.record_dir("creator") / "record.json").relative_to(self.root))
        self.assertEqual(changed, {record_path} if status == "done" else set())
        for name, data in sentinels.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        return code, hbt.load_record("creator"), "\n".join(messages)

    def test_pending_verdicts_and_timeout_do_not_finish_setup(self):
        for state in ("review", "ready", "todo", "archived", "blocked", "text-only-approve", "timeout"):
            with self.subTest(state=state):
                code, rec, output = self.run_first_card(state)
                self.assertEqual(code, 1)
                self.assertNotIn("first_card", rec["setup"])
                self.assertIn("No automatic approval was recorded", output)
                self.assertIn("original approval thread", output)

    def test_exact_done_card_records_exact_id(self):
        code, rec, _ = self.run_first_card("done")
        self.assertEqual(code, 0)
        self.assertEqual(rec["setup"]["first_card"], "t_00000001")

    def test_missing_project_identity_does_not_prompt_or_finish(self):
        tpl = hbt.load_template("creator")
        role = next(r for r in tpl.roles if r.key == "engineer")
        for projects in (None, "relative", 1):
            with patch.object(hbt, "next_setup_step", return_value=("first-card", role)), \
                 patch.object(hbt, "load_record", return_value={"projects": projects}), \
                 patch.object(hbt, "_wait", side_effect=AssertionError("prompt")), \
                 patch.object(hbt, "save_record", side_effect=AssertionError("write")), patch.object(hbt, "say"):
                self.assertEqual(hbt.cmd_setup(hbt.build_parser().parse_args(["setup", "creator"])), 1)


if __name__ == "__main__":
    unittest.main()
