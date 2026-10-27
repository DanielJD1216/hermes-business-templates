"""Exercise the private progress checker through its actual read-only CLI."""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/dooing-onboarding"
CHECKER = SKILL / "scripts/check_progress.py"
BASELINE = SKILL / "references/baseline.md"


def record():
    baseline = BASELINE.read_text()
    rows = baseline.split("| Component |", 1)[1].split("\n\n", 1)[0].splitlines()[2:]
    names = [row.split("|")[1].strip() for row in rows]
    text = f"""# Private onboarding progress
- Template revision: {'a' * 40}
- Baseline SHA256: {hashlib.sha256(BASELINE.read_bytes()).hexdigest()}

## Baseline evidence
| Component | State | Evidence basis | Evidence / observed time | Limitation | Next action / actor |
|---|---|---|---|---|---|
"""
    for index, name in enumerate(names):
        if index < 7:
            basis = "owner-relayed" if index < 2 else "fresh"
            text += f"| {name} | verified | {basis} | private receipt {index} | scoped check | none |\n"
        else:
            text += f"| {name} | not-tested | none | | | run approved check / agent |\n"
    text += """
## Owner decisions
| Decision | State | Implementation / reason | Owner authority reference | Affected baseline row |
|---|---|---|---|---|
"""
    decisions = (SKILL / "templates/progress.md").read_text().split("| Decision |", 1)[1].split("\n\n", 1)[0].splitlines()[2:]
    for row in decisions:
        name = row.split("|")[1].strip()
        text += f"| {name} | selected | reviewed no-change | owner instruction | Main assistant |\n"
    text += """
## Current checkpoint and resume
- Checkpoint state: continue
- Current component: Scheduled index refresh
- Just verified: Current-source lookup passed
- Next incomplete action and prerequisite: Verify the approved refresh schedule
- Next actor: agent
- Owner action needed: none
- Blocker: none
- Continuation evidence: none
- Additional owner-required outcomes: unknown
- Setup complete: no
"""
    return text


class ProgressCheckpoint(unittest.TestCase):
    def run_check(self, text):
        self.assertTrue(CHECKER.is_file(), "The progress checker has not been implemented")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "progress.md"
            path.write_text(text)
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(CHECKER), str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(path.read_bytes(), before, "Checker must not rewrite the private record")
            return result, json.loads(result.stdout)

    def test_reports_evidence_coverage_and_exact_next_action(self):
        result, report = self.run_check(record())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((report["verified"], report["total"], report["percent"]), (7, 18, 38.9))
        self.assertEqual(report["owner_confirmed"], 2)
        self.assertFalse(report["complete"])
        self.assertIn("7/18", report["footer"])
        self.assertIn("Verify the approved refresh schedule", report["footer"])
        self.assertIn("Your action: none", report["footer"])

    def test_rejects_false_progress_and_vague_continuation(self):
        valid = record()
        row = next(line for line in valid.splitlines() if line.startswith("| Hermes and model access |"))
        decision = next(line for line in valid.splitlines() if "| selected |" in line)
        cases = {
            "missing component": valid.replace(row + "\n", ""),
            "duplicate component": valid.replace(row, row + "\n" + row),
            "unknown component": valid.replace("| Main assistant | verified", "| Invented component | verified"),
            "untrusted baseline": valid.replace(hashlib.sha256(BASELINE.read_bytes()).hexdigest(), "0" * 64),
            "unpinned revision": valid.replace("a" * 40, "main"),
            "missing evidence": valid.replace("private receipt 0", "[evidence]"),
            "missing evidence basis": valid.replace("verified | owner-relayed", "verified | none", 1),
            "unknown state": valid.replace("| not-tested |", "| installed |", 1),
            "missing decision": valid.replace(decision + "\n", ""),
            "empty next action": valid.replace("Verify the approved refresh schedule", ""),
            "placeholder next action": valid.replace("Verify the approved refresh schedule", "[next step]"),
            "duplicate field": valid + "\n- Next actor: owner\n",
            "repeat verified component": valid.replace("Current component: Scheduled index refresh", "Current component: Main assistant"),
            "premature completion": valid.replace("Checkpoint state: continue", "Checkpoint state: complete"),
            "waiting without callback": valid.replace("Checkpoint state: continue", "Checkpoint state: waiting").replace("Next actor: agent", "Next actor: job"),
            "owner action unspecified": valid.replace("Checkpoint state: continue", "Checkpoint state: owner-action").replace("Next actor: agent", "Next actor: owner"),
            "blocker unspecified": valid.replace("Checkpoint state: continue", "Checkpoint state: blocked"),
            "contradictory actor": valid.replace("Next actor: agent", "Next actor: owner"),
            "wrong headers": valid.replace("| Evidence basis | Evidence / observed time |", "| Limitation | Evidence basis |"),
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                result, report = self.run_check(text)
                self.assertNotEqual(result.returncode, 0, label)
                self.assertEqual(report["status"], "invalid")
                self.assertNotIn("percent", report)

    def test_completion_is_stricter_than_full_baseline_coverage(self):
        full = record().replace("| not-tested | none | | | run approved check / agent |",
                                "| verified | fresh | private completion receipt | scoped | none |")
        full = full.replace("Current component: Scheduled index refresh",
                            "Current component: Owner decisions and additional outcomes")
        result, report = self.run_check(full)
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["percent"], 100.0)
        self.assertFalse(report["complete"], "Unknown owner outcomes still block completion")
        done = full.replace("Checkpoint state: continue", "Checkpoint state: complete")
        done = done.replace("Current component: Owner decisions and additional outcomes", "Current component: none")
        done = done.replace("Next actor: agent", "Next actor: none")
        done = done.replace("Verify the approved refresh schedule", "none")
        done = done.replace("Additional owner-required outcomes: unknown", "Additional owner-required outcomes: none outstanding")
        done = done.replace("Setup complete: no", "Setup complete: yes")
        result, report = self.run_check(done)
        self.assertEqual(result.returncode, 0, report)
        self.assertTrue(report["complete"])
        roster = next(line for line in done.splitlines() if line.startswith("| Required EA,"))
        declined = roster.replace("| selected |", "| declined |").replace("| Main assistant |", "| Responsibilities and roster |")
        for invalid in (done.replace("| selected |", "| deferred |", 1),
                        done.replace(roster, declined),
                        done.replace(roster, declined.replace("| Responsibilities and roster |", "| |")),
                        done.replace("|---|---|---|---|---|---|", "|---|"),
                        done.replace("|---|---|---|---|---|---|", "| |"),
                        done.replace("|---|---|---|---|---|---|", "x|---|---|---|---|---|---|x"),
                        done.replace("none outstanding", "unknown"),
                        done.replace("Setup complete: yes", "Setup complete: no")):
            with self.subTest(record=invalid):
                self.assertNotEqual(self.run_check(invalid)[0].returncode, 0)
        optional = "| Optional phone interface | declined | not needed | owner instruction | none |\n"
        with_optional = done.replace("\n## Current checkpoint", "\n" + optional + "\n## Current checkpoint")
        self.assertTrue(self.run_check(with_optional)[1]["complete"])
        incomplete = record().replace(roster, declined)
        incomplete = re.sub(r"^\| Responsibilities and roster \|.*$",
                            "| Responsibilities and roster | not-tested | none | | declined | resolve required roster / owner |",
                            incomplete, flags=re.M)
        result, report = self.run_check(incomplete)
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["unresolved_decisions"], 1)
        self.assertFalse(report["complete"])

    def test_supported_stop_states(self):
        for state, actor, action, blocker, continuation in (
            ("owner-action", "owner", "On the host, approve the OS dialog; confirm it closes", "none", "none"),
            ("paused", "owner", "Resume explicitly when ready", "none", "none"),
            ("blocked", "external", "none", "Provider outage confirmed by its status page", "none"),
            ("waiting", "job", "none", "none", "fixture job 1; completion callback registered to private origin"),
        ):
            with self.subTest(state=state):
                text = record().replace("Checkpoint state: continue", "Checkpoint state: " + state)
                text = text.replace("Next actor: agent", "Next actor: " + actor)
                text = text.replace("Owner action needed: none", "Owner action needed: " + action)
                text = text.replace("Blocker: none", "Blocker: " + blocker)
                text = text.replace("Continuation evidence: none", "Continuation evidence: " + continuation)
                result, report = self.run_check(text)
                self.assertEqual(result.returncode, 0, report)
                self.assertFalse(report["complete"])

    def test_bundled_template_can_be_initialized_without_another_tracker(self):
        initialized = (SKILL / "templates/progress.md").read_text()
        fields = re.findall(r"^- ([^:\n]+): (.*)$", record(), re.M)
        for name, value in fields:
            initialized = re.sub(r"^- " + re.escape(name) + r":.*$",
                                 lambda match: "- " + name + ": " + value, initialized, flags=re.M)
        initialized = initialized.replace("| not-tested | none | | | |",
                                          "| not-tested | none | | | inspect approved state / agent |")
        result, report = self.run_check(initialized)
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["verified"], 0)
        self.assertGreater(report["unresolved_decisions"], 0)
        description = subprocess.run([sys.executable, str(CHECKER), "--describe"], capture_output=True, text=True)
        self.assertEqual(description.returncode, 0, description.stderr)
        self.assertEqual(json.loads(description.stdout)["baseline_sha256"], hashlib.sha256(BASELINE.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
