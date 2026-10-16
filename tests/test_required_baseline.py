"""Required onboarding scope and progress must not silently diverge."""
import importlib.util
import json
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capabilities", ROOT / "scripts/check_capabilities.py")
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class RequiredBaseline(unittest.TestCase):
    def test_required_scope_and_progress_agree(self):
        catalog = json.loads((ROOT / "capabilities/catalog.json").read_text())
        sources = json.loads((ROOT / "capabilities/sources.json").read_text())
        self.assertTrue(catalog["safety"]["fixed_roster"])
        self.assertEqual(catalog["safety"]["required_tools"], ["LEANN", "Obsidian", "Parsec"])
        self.assertEqual(checker.check(catalog, sources)["result"], "PASS")
        for mutation in ({"fixed_roster": False}, {"baseline_schedule": "memory-watchdog only"},
                         {"required_tools": ["Obsidian"]},
                         {"required_tools": ["LEANN", "Obsidian"]}):
            invalid = deepcopy(catalog)
            invalid["safety"].update(mutation)
            with self.assertRaises(ValueError):
                checker.check(invalid, sources)
        baseline = (ROOT / "skills/customer-onboarding/references/baseline.md").read_text()
        progress = (ROOT / "skills/customer-onboarding/templates/progress.md").read_text()
        # Read the contiguous rendered table, not unrelated rows below a blank line.
        required = [line.split("|")[1].strip() for line in
                    baseline.split("| Component |", 1)[1].split("\n\n", 1)[0].splitlines()[2:]]
        tracked = [line.split("|")[1].strip() for line in
                   progress.split("| Component |", 1)[1].split("\n\n", 1)[0].splitlines()[2:]]
        self.assertEqual(required, tracked)
        self.assertEqual(len(required), 18)
        self.assertIn("Scheduled index refresh", required)
        self.assertIn("Parsec remote debugging", required)
        self.assertNotIn("Remote recovery", required)


if __name__ == "__main__":
    unittest.main()
