"""Minimal regression for the package-local customer link checker."""
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_customer_guide.py"
spec = importlib.util.spec_from_file_location("customer_guide", SCRIPT)
assert spec is not None and spec.loader is not None
guide = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guide)


class CustomerGuideLinks(unittest.TestCase):
    def test_real_files_headings_and_escape_boundary(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text('# Instructions\n<a id="named"></a>\n')
            readme = root / "README.md"
            readme.write_text("[good](AGENTS.md#instructions)\n[named](AGENTS.md#named)\n")
            self.assertEqual(guide.check(root)[2], [])
            readme.write_text("[missing](absent.md)\n[heading](AGENTS.md#absent)\n[outside](../outside.md)\n")
            self.assertEqual(len(guide.check(root)[2]), 3)
        self.assertEqual(guide.check(SCRIPT.parents[1])[2], [])


class RoleTemplates(unittest.TestCase):
    def test_every_role_soul_ends_with_the_same_shared_rules(self):
        souls = sorted((SCRIPT.parents[1] / "skills/customer-onboarding/templates/souls").glob("*.md"))
        self.assertGreaterEqual(len(souls), 3)
        blocks = {p.name: p.read_text().partition("\n## Shared rules\n")[2] for p in souls}
        self.assertTrue(all(blocks.values()), "every role template needs a Shared rules section")
        self.assertEqual(len(set(blocks.values())), 1, "Shared rules drifted between role templates")


if __name__ == "__main__":
    unittest.main()
