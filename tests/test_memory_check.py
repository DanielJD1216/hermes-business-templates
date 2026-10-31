"""Exercise the memory check's safety logic without an OpenViking server: plan mode, the cap, the stub."""
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/dooing-onboarding/scripts/memory_check.py"
sys.path.insert(0, str(SCRIPT.parent))
import memory_check as mc  # noqa: E402


def post(url, body=b"{}"):
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


class MemoryCheck(unittest.TestCase):
    def run_cli(self, config, *args):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ov.conf"
            path.write_text(json.dumps(config))
            result = subprocess.run([sys.executable, str(SCRIPT), "--config", str(path),
                                     "--server", "/nonexistent/openviking-server", *args],
                                    capture_output=True, text=True, timeout=30)
            return result.returncode, json.loads(result.stdout)

    def test_plan_starts_nothing_and_shows_the_budget(self):
        code, report = self.run_cli({"embedding": {"max_input_tokens": 1000,
                                                   "dense": {"api_base": "http://127.0.0.1:9/v1"}}}, "--plan")
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "plan")
        self.assertEqual(report["source_sizes_chars"], [2000, 6000, 12000])
        self.assertEqual(report["max_requests"], 400)

    def test_refuses_an_embedding_service_it_cannot_cap(self):
        for embedding in ({"dense": {"provider": "openai"}}, {"dense": {"api_base": "http://x"}, "sparse": {}}):
            with self.subTest(embedding=embedding):
                code, report = self.run_cli({"embedding": embedding})
                self.assertEqual(code, 2)
                self.assertEqual(report["status"], "not-run")
                self.assertIn("api_base", report["reason"])

    def test_proxy_stops_at_the_request_cap(self):
        seen = {"POST": 0, "GET": 0}

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def reply(self):
                seen[self.command] += 1
                self.rfile.read(int(self.headers.get("Content-Length") or 0))
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"{}")

            do_POST = do_GET = reply

        upstream = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
        Thread(target=upstream.serve_forever, daemon=True).start()
        budget = mc.Budget(2)
        server, base = mc.proxy(f"http://127.0.0.1:{upstream.server_port}/v1", budget)
        try:
            self.assertTrue(base.endswith("/v1"))
            statuses = [post(base + "/embeddings")[0] for _ in range(3)]
            self.assertEqual(statuses, [200, 200, 429])
            self.assertEqual((seen["POST"], budget.used, budget.exhausted), (2, 2, True))
            with urllib.request.urlopen(base + "/models", timeout=10) as r:  # reads are not counted
                self.assertEqual(r.status, 200)
            self.assertEqual(budget.used, 2)
        finally:
            server.shutdown()
            upstream.shutdown()

    def test_summary_stub_answers_without_a_model(self):
        budget = mc.Budget(1)
        server, base = mc.stub_model(budget)
        try:
            status, body = post(base + "/chat/completions")
            self.assertEqual(status, 200)
            self.assertEqual(json.loads(body)["choices"][0]["message"]["content"], "Test note.")
            self.assertEqual((budget.stub_calls, budget.used), (1, 0))
        finally:
            server.shutdown()

    def test_input_limit_override_shows_in_the_plan(self):
        config = {"embedding": {"max_input_tokens": 4096, "dense": {"api_base": "http://127.0.0.1:9/v1"}}}
        code, report = self.run_cli(config, "--plan", "--max-input-tokens", "1500")
        self.assertEqual(code, 0)
        self.assertEqual((report["max_input_tokens"], report["max_input_tokens_from"]), (1500, "--max-input-tokens"))
        self.assertEqual(report["source_sizes_chars"], [3000, 9000, 18000])
        code, report = self.run_cli(config, "--plan", "--max-input-tokens", "50")
        self.assertEqual((code, report["status"]), (2, "not-run"))

    def test_a_copy_that_was_never_indexed_fails_the_step(self):
        folder = mc.ROOT + "/long"

        class OnlyTarget:  # the control copy was rejected, so search returns the target alone
            def write(self, *args, **kwargs):
                pass

            def settle(self):
                pass

            def find(self, question, limit, where):
                return [(folder + "/notes.md", 0.6)]

        result = mc.long_memory(OnlyTarget(), 1000)
        self.assertFalse(result["passed"])
        self.assertEqual({s["both_copies_indexed"] for s in result["steps"]}, {False})
        self.assertEqual({s["score_gain_over_control"] for s in result["steps"]}, {None})

    def test_rejected_requests_fail_the_check_and_keep_a_safe_reason(self):
        self.assertEqual(mc.mark_rejections({"passed": True}, 2)["passed"], False)
        self.assertEqual(mc.mark_rejections({"passed": True}, 0), {"passed": True, "embedding_rejections": 0})
        self.assertIsNone(mc.mark_rejections({"passed": None}, 1)["passed"])
        body = json.dumps({"error": {"message": "the input length exceeds the context length (key sk-proj-abcdefghijklmnop1234)"}})
        text = mc.rejection_text(400, body.encode())
        self.assertTrue(text.startswith("HTTP 400: the input length exceeds the context length"))
        self.assertNotIn("abcdefghijklmnop", text)

    def test_results_keep_the_best_score_per_test_file(self):
        folder = mc.ROOT + "/long"
        found = [(folder + "/notes.md#2", 0.2), (folder + "/notes.md", 0.5), (folder + "/", 0.9),
                 (mc.ROOT + "/two/a.md", 0.8), (folder + "/control.md", 0.4)]
        self.assertEqual(mc.files(found, folder), {folder + "/notes.md": 0.5, folder + "/control.md": 0.4})

    def test_the_newest_fact_is_written_last(self):
        fact = mc.GROWTH[0][0]
        body = mc.text(3000, [(fact, 1.0)])
        self.assertGreaterEqual(len(body), 3000)
        self.assertTrue(body.rstrip().endswith(fact))
        self.assertEqual(body.replace(fact, mc.NEUTRAL).count(fact), 0)


if __name__ == "__main__":
    unittest.main()
