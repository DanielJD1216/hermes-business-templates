"""Pure proposal/response validation. Native integration needs isolated proof."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "templates/creator/roles/ops/scripts/hbt_memory_review.py"
spec = importlib.util.spec_from_file_location("hbt_memory_review", SCRIPT)
assert spec is not None and spec.loader is not None
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewSchema(unittest.TestCase):
    def test_original_add(self):
        self.assertTrue(review.valid_payload({"action": "add", "target": "memory", "content": "Durable fact."}, "add-only"))

    def test_replace_requires_mode_and_original_pin(self):
        payload = {"action": "replace", "target": "user", "content": "New fact.", "old_text": "Old", "matched_entry": "Old fact."}
        self.assertFalse(review.valid_payload(payload, "add-only"))
        self.assertTrue(review.valid_payload(payload, "add-replace"))
        del payload["matched_entry"]
        self.assertFalse(review.valid_payload(payload, "add-replace"))

    def test_remove_rejects_entire_batch(self):
        payload = {"action": "batch", "target": "memory", "operations": [
            {"action": "add", "content": "Fact."},
            {"action": "remove", "old_text": "old", "matched_entry": "old"}]}
        self.assertFalse(review.valid_payload(payload, "add-replace"))

    def test_extra_mutation_field_rejected(self):
        drafts = [{"review": {"profile": "engineer", "id": "01234567"}}]
        decision = {"profile": "engineer", "id": "01234567", "decision": "apply", "reason": "durable"}
        for later in ({**decision, "ops": []}, {**decision, "id": "87654321"}, decision):
            with self.subTest(later=later), self.assertRaises(review.Refused):
                review.decisions(review.encoded({"decisions": [decision, later]}), drafts)

    def test_strict_json_does_not_scrape(self):
        for raw in ('prefix {"decisions": []}', '{"decisions": [], "decisions": []}', '{"decisions": NaN}'):
            with self.subTest(raw=raw), self.assertRaises((ValueError, review.Refused)):
                review.decisions(raw, [])

    def test_missing_decision_retains(self):
        self.assertEqual(review.decisions('{"decisions": []}', [{"review": {"profile": "cto", "id": "01234567"}}]), {})


if __name__ == "__main__":
    unittest.main()
