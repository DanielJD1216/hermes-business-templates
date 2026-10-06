"""Offline update-advice regression: execute main, never fetch or apply updates."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shlex
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent


def load(name, path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class UpdateAdvice(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        (self.repo / ".git").mkdir(parents=True)
        self.settings = self.root / "profile/hbt-settings.json"
        self.settings.parent.mkdir()
        self.state = self.root / "profile/state/hbt-update-check.json"
        # Inventory includes both inputs and bytes the checker must never change.
        for relative in ("repo/.git/marker", "install/record.json", "profile/config.yaml",
                         "profile/memories/USER.md", "profile/memories/MEMORY.md",
                         "profile/cron/jobs.json", "repo/canon/business.md"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Synthetic preservation sentinel\r\n")
        for target in ("subprocess.run", "subprocess.Popen", "socket.socket",
                       "socket.create_connection"):
            guard = patch(target, side_effect=AssertionError("Unexpected external operation"))
            guard.start()
            self.addCleanup(guard.stop)
        # Imports also run with external commands and network refused.
        self.check = load("update_advice_check", ROOT / "templates/creator/roles/ops/scripts/hbt_update_check.py")
        self.hbt = load("update_advice_installer", ROOT / "installer/hbt.py")
        self.check.SETTINGS_PATH = self.settings
        self.check.STATE_PATH = self.state

    def inventory(self):
        return {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def configure(self, **extra):
        self.settings.write_text(json.dumps({"repo_path": str(self.repo),
                                             "installed_version": "0.5.0", **extra}))

    def run_main(self, latest, template="creator"):
        output = io.StringIO()
        before = self.inventory()
        with patch.object(self.check, "remote_version", return_value=latest) as remote:
            with contextlib.redirect_stdout(output):
                self.assertEqual(self.check.main(), 0)
        remote.assert_called_once_with(self.repo, template)
        after = self.inventory()
        key = str(self.state.relative_to(self.root))
        self.assertEqual({k: v for k, v in before.items() if k != key},
                         {k: v for k, v in after.items() if k != key})
        return output.getvalue()

    def assert_advice(self, template):
        text = self.run_main("0.6.0", template)
        self.assertEqual(text, f":package: Template update available: {template} 0.5.0 -> 0.6.0. "
                         f"To update, run on the server: cd {self.repo} && git pull && ./hbt update {template}\n")
        argv = shlex.split(text.split("&& ./hbt ", 1)[1])
        self.assertEqual(argv, ["update", template])
        parsed = self.hbt.build_parser().parse_args(argv)
        self.assertEqual((parsed.cmd, parsed.template), ("update", template))
        # Parsing only: never call parsed.func or load a synthetic template.
        self.assertEqual(json.loads(self.state.read_text()), {"announced": "0.6.0"})
        before = self.inventory()
        self.assertEqual(self.run_main("0.6.0", template), "")
        self.assertEqual(self.inventory(), before)

    def test_default_template_argument_and_repeat_silence(self):
        self.configure()
        self.assert_advice("creator")

    def test_selected_synthetic_template_argument_and_repeat_silence(self):
        self.configure(template="synthetic-example")
        self.assert_advice("synthetic-example")

    def test_empty_template_keeps_creator_default(self):
        self.configure(template="")
        self.assert_advice("creator")

    def test_no_newer_or_unavailable_version_is_silent_without_writes(self):
        self.configure()
        for latest in (None, "", "0.5.0", "0.4.9"):
            with self.subTest(latest=latest):
                before = self.inventory()
                self.assertEqual(self.run_main(latest), "")
                self.assertEqual(self.inventory(), before)
                self.assertFalse(self.state.exists())

    def test_existing_announcement_is_silent_without_rewriting_state(self):
        self.configure()
        self.state.parent.mkdir()
        self.state.write_text('{"announced": "0.6.0"}\n')
        before = self.inventory()
        self.assertEqual(self.run_main("0.6.0"), "")
        self.assertEqual(self.inventory(), before)

    def test_external_operation_guards_are_active(self):
        for operation in (lambda: subprocess.run(["git", "fetch"]),
                          lambda: subprocess.Popen(["hermes", "status"]),
                          lambda: socket.create_connection(("127.0.0.1", 1933)),
                          lambda: socket.socket()):
            with self.assertRaisesRegex(AssertionError, "Unexpected external operation"):
                operation()


class DocumentationContract(unittest.TestCase):
    def test_video_workstream_reuses_current_cards_and_keeps_approval(self):
        skills = ROOT / "templates/creator/roles/creative-director/skills"
        digest = (skills / "creator-community-question-digest/SKILL.md").read_text()
        brief = (skills / "creator-partnerships-sponsor-brief/SKILL.md").read_text()
        for text in (digest, brief):
            self.assertIn("Creative Director", text)
            self.assertIn("Video workstream", text)
            self.assertIn("move the card to review", text)
            self.assertIn("Nothing leaves the business without the owner's `approve`", text)
            self.assertNotIn("card to Video", text)
        self.assertIn("existing Ops-origin card", digest)
        self.assertIn("media/video/topic-queue.md", digest)
        self.assertIn("not a new self-handoff", digest)
        self.assertIn("current signed-deal/episode card", brief)
        self.assertIn("assign it to creative-director, never Video", brief)
        for term in ("disclosure line", "verified product claims only", "canon/standing.md"):
            self.assertIn(term, brief)

    def test_optional_services_are_owner_prerequisites_not_security_claims(self):
        text = (ROOT / "README.md").read_text()
        for term in ("hermes memory setup", "English search suitability", "costs and credentials",
                     "does not provision", "not automatic outage fallback",
                     "not an authorization or hostile-process boundary", "Ops keeps no memory",
                     "subordinate user/group IDs", "user-daemon/context setup",
                     "does not install Docker", "Actual container and native-tool enforcement remains unverified",
                     "not every deployment is unauthenticated"):
            self.assertIn(term, text)
        self.assertNotIn("so bots cannot see each other's memories", text)

    def test_historical_proof_and_remaining_gates_are_explicit(self):
        text = (ROOT / "README.md").read_text()
        for term in ("historical evidence", "not checks rerun", "52 native opt-in tests were skipped, not passed",
                     "8776cac768ca810c1a6ce60acf2a95ffe617d5cf", "NULL/empty notifier owners",
                     "legacy exact-session-key behavior", "Notification collection is not external delivery",
                     "independently approved installed native revision", "not clean bootstrap",
                     "deferred until feature-complete, not waived", "not release-ready"):
            self.assertIn(term, text)
        self.assertIn("leaves existing job delivery settings unchanged", text)
        self.assertIn("reports Ops delivery as unverified", text)


if __name__ == "__main__":
    unittest.main()
