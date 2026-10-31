#!/usr/bin/env python3
"""Run the guide's three OpenViking memory checks on a throwaway server.

The owner's memory is never touched: the server gets its own data folder and its
own loopback port, and both are removed afterwards. Embeddings use the owner's
own embedding settings through a local counting proxy with a hard request cap.
The summary model is replaced by a local stub, so no chat model is called.
Output is JSON with results and counts only: no keys, no memory text.

Checks (references/memory-reliability.md):
  long_memory  a source grows to 3 times the embedder's input limit; at each size
               its newest fact, placed last, must score above a control copy
               that has a plain sentence in its place (equal scores mean the
               fact was never indexed)
  two_sources  a long and a short source on one topic both come back at limit 2
  restart      the server is killed right after a write; after a restart the
               source must be indexed and keep every written byte

Exit 0: all passed. 1: a check failed. 2: could not run (setup, budget, time).
"""
import argparse
import json
import os
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = "viking://user/default/memories/memory-check"
FILLER = [
    "The morning train was a few minutes late because of a signal check near the bridge.",
    "Fresh bread tastes better when the dough rests overnight in a cool kitchen.",
    "The library extended its weekend hours after many students asked for more study space.",
    "A light rain fell over the city while people waited for the evening bus.",
    "The office printer needs new paper every Thursday before the team meeting.",
    "Coffee beans keep their flavour longer in a sealed jar away from sunlight.",
    "The museum added a small room about old maps and early sailing routes.",
    "Children at the park built a sand castle with towers and a narrow moat.",
    "The bakery on the corner sells out of cinnamon rolls before nine most days.",
    "Wind from the west kept the harbour flags moving all afternoon.",
    "The new bicycle lane runs along the river from the market to the stadium.",
    "A neighbour repaired the old fence with cedar boards and bright brass screws.",
]
GROWTH = [  # (fact appended at the end of the source, question that should find it)
    ("The spare key for the blue garden shed is kept under the third clay flowerpot.",
     "Where is the spare key for the blue garden shed kept?"),
    ("The emergency water valve for the north greenhouse sits behind the red ladder.",
     "Where is the emergency water valve for the north greenhouse?"),
    ("The winter bulb order goes to the Larkspur nursery on the second Monday of March.",
     "When does the winter bulb order go to the Larkspur nursery?"),
]
NEUTRAL = "The town hall clock was cleaned last spring and its old brass hands were polished."
TOPIC = "The sailing boat engine is serviced at the marina workshop every April before launch."
TOPIC_Q = "When is the sailing boat engine serviced at the marina workshop?"
RESTART = ("The backup generator test runs on the first Friday of each month at seven in the morning.",
           "When does the backup generator test run?")
SIZES = (0.5, 1.5, 3.0)  # source length as a multiple of the embedder's input limit
MIN_GAIN = 0.001  # a never-indexed fact leaves the two copies with identical vectors, so a gain of exactly 0


class Budget:
    def __init__(self, cap):
        self.cap, self.used, self.errors, self.stub_calls, self.exhausted = cap, 0, 0, 0, False
        self.lock = threading.Lock()

    def take(self):
        with self.lock:
            if self.used >= self.cap:
                self.exhausted = True
                return False
            self.used += 1
            return True


def serve(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def proxy(upstream, budget):
    """Forward to the owner's embedding service; every POST counts against the cap."""
    target = urllib.parse.urlsplit(upstream)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _forward(self, counted):
            if counted and not budget.take():
                self.send_response(429)
                self.end_headers()
                return
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            headers = {k: v for k, v in self.headers.items()
                       if k.lower() not in {"host", "content-length", "connection", "accept-encoding"}}
            req = urllib.request.Request(f"{target.scheme}://{target.netloc}{self.path}", data=body or None,
                                         headers=headers, method=self.command)
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    status, ctype, data = r.status, r.headers.get("Content-Type", ""), r.read()
            except urllib.error.HTTPError as e:
                status, ctype, data = e.code, e.headers.get("Content-Type", ""), e.read()
            except OSError:
                status, ctype, data = 502, "text/plain", b"upstream unreachable"
            if counted and status >= 400:
                with budget.lock:
                    budget.errors += 1
            self.send_response(status)
            self.send_header("Content-Type", ctype or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            self._forward(True)

        def do_GET(self):
            self._forward(False)

    server = serve(Handler)
    return server, f"http://127.0.0.1:{server.server_port}{target.path}"


def stub_model(budget):
    """OpenAI-compatible chat endpoint that answers every summary request with one fixed line."""
    reply = json.dumps({"id": "stub", "object": "chat.completion", "created": 0, "model": "stub",
                        "choices": [{"index": 0, "finish_reason": "stop",
                                     "message": {"role": "assistant", "content": "Test note."}}],
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}}).encode()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            with budget.lock:
                budget.stub_calls += 1
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(reply)))
            self.end_headers()
            self.wfile.write(reply)

    server = serve(Handler)
    return server, f"http://127.0.0.1:{server.server_port}/v1"


def text(chars, facts=(), seed=0):
    """Natural filler up to about `chars`, with each fact placed at its relative position (0..1)."""
    out, n, placed = [], seed, set()
    while sum(len(s) + 1 for s in out) < chars:
        pos = sum(len(s) + 1 for s in out) / chars
        for i, (fact, at) in enumerate(facts):
            if i not in placed and pos >= at:
                out.append(fact)
                placed.add(i)
        out.append(FILLER[n % len(FILLER)])
        n += 1
    out.extend(fact for i, (fact, _) in enumerate(facts) if i not in placed)
    return " ".join(out) + "\n"


class Server:
    def __init__(self, binary, conf, work, port):
        self.cmd = [*binary, "--config", str(conf), "--host", "127.0.0.1", "--port", str(port)]
        self.url, self.work, self.proc = f"http://127.0.0.1:{port}", work, None
        # Only what the server needs: no OpenViking settings, keys or other variables from the owner's environment.
        passed = {name: os.environ.get(name) for name in ("PATH", "LANG", "SSL_CERT_FILE")}
        self.env = {name: value for name, value in passed.items() if value}
        self.env.update(HOME=str(work / "home"), TMPDIR=str(work / "tmp"))

    def start(self, deadline):
        log = open(self.work / "server.log", "ab")
        self.proc = subprocess.Popen(self.cmd, cwd=self.work, env=self.env, stdout=log, stderr=subprocess.STDOUT,
                                     start_new_session=True)
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError("server exited during startup")
            try:
                urllib.request.urlopen(self.url + "/health", timeout=2)
                return
            except OSError:
                time.sleep(1)
        raise RuntimeError("server did not start in time")

    def stop(self, sig=signal.SIGTERM):
        if self.proc and self.proc.poll() is None:
            os.killpg(self.proc.pid, sig)
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait(timeout=30)

    def call(self, method, path, body=None):
        req = urllib.request.Request(self.url + path, method=method, headers={"Content-Type": "application/json"},
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            return e.code, {}

    def write(self, uri, content, mode, wait=True):
        status, _ = self.call("POST", "/api/v1/content/write",
                              {"uri": uri, "content": content, "mode": mode, "wait": wait, "timeout": 240})
        if status != 200:
            raise RuntimeError(f"write returned {status}")

    def find(self, query, limit, folder):
        status, body = self.call("POST", "/api/v1/search/find", {"query": query, "target_uri": folder, "limit": limit})
        if status != 200:
            raise RuntimeError(f"find returned {status}")
        found = []
        for group in ("memories", "resources", "skills"):
            found += [(item.get("uri", ""), item.get("score") or 0.0) for item in (body.get("result") or {}).get(group) or []]
        return found

    def settle(self, seconds=240):
        """Wait until the server has finished all indexing; embeds nothing."""
        status, _ = self.call("POST", "/api/v1/system/wait", {"timeout": seconds})
        if status != 200:
            raise RuntimeError(f"wait returned {status}")

    def read(self, uri):
        status, body = self.call("GET", "/api/v1/content/read?raw=true&uri=" + urllib.parse.quote(uri, safe=""))
        return body.get("result") if status == 200 else None


def files(found, folder):
    """Best score per test file in `folder`, in result order (folder entries and repeat sections skipped)."""
    best = {}
    for uri, score in found:
        base = uri.split("#", 1)[0]
        if base.startswith(folder + "/") and base.endswith(".md"):
            best[base] = max(score, best.get(base, score))
    return best


def long_memory(srv, limit_chars):
    folder = f"{ROOT}/long"
    target, control, mode, steps = f"{folder}/notes.md", f"{folder}/control.md", "create", []
    for step, (size, (fact, question)) in enumerate(zip(SIZES, GROWTH)):
        earlier = [(GROWTH[i][0], 0.1 + 0.3 * i) for i in range(step)]  # older facts stay, the new one goes last
        body = text(int(size * limit_chars), earlier + [(fact, 1.0)])
        srv.write(target, body, mode)
        srv.write(control, body.replace(fact, NEUTRAL), mode)
        mode = "replace"
        srv.settle()
        best = files(srv.find(question, 10, folder), folder)
        gain = round(best.get(target, 0.0) - best.get(control, 0.0), 4)
        steps.append({"size_x_limit": size, "score_gain_over_control": gain})
    return {"passed": all(s["score_gain_over_control"] > MIN_GAIN for s in steps), "steps": steps}


def two_sources(srv, limit_chars):
    folder = f"{ROOT}/two"
    long_uri, short_uri = f"{folder}/topic-long.md", f"{folder}/topic-short.md"
    srv.write(long_uri, text(int(3 * limit_chars), [(TOPIC, 0.05), (TOPIC, 0.35), (TOPIC, 0.65), (TOPIC, 0.95)], 5),
              "create")
    srv.write(short_uri, TOPIC + " " + FILLER[3] + "\n", "create")
    srv.settle()
    top = list(files(srv.find(TOPIC_Q, 2, folder), folder))
    return {"passed": set(top) == {long_uri, short_uri}, "returned_files": len(top)}


def restart(srv, limit_chars):
    folder = f"{ROOT}/restart"
    fact, question = RESTART
    uri, body = f"{folder}/notes.md", text(int(0.8 * limit_chars), [(fact, 0.5)], 9)
    srv.write(uri, body, "create", wait=False)
    srv.stop(signal.SIGKILL)  # the crash: no shutdown handling
    srv.start(time.time() + 180)
    srv.settle()
    indexed = uri in files(srv.find(question, 5, folder), folder)
    stored = srv.read(uri)
    # OpenViking appends its own MEMORY_FIELDS block to a stored memory; every written byte must come first, unchanged.
    kept = isinstance(stored, str) and stored.startswith(body)
    return {"passed": indexed and kept, "indexed_after_restart": indexed, "written_text_kept": kept}


CHECKS = {"long_memory": long_memory, "two_sources": two_sources, "restart": restart}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=Path.home() / ".openviking/ov.conf",
                    help="the owner's OpenViking config; only its embedding section is used")
    ap.add_argument("--server", default=shutil.which("openviking-server") or "openviking-server",
                    help="the installed openviking-server command to test")
    ap.add_argument("--max-requests", type=int, default=400, help="hard cap on embedding requests (default 400)")
    ap.add_argument("--time-limit", type=int, default=1200, help="seconds before the run stops (default 1200)")
    ap.add_argument("--plan", action="store_true", help="show what would run, start nothing")
    args = ap.parse_args()

    try:
        embedding = json.loads(args.config.read_text())["embedding"]
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({"status": "not-run", "reason": "cannot read the embedding section of the config"}))
        return 2
    bases = {name: (part or {}).get("api_base") for name, part in embedding.items() if isinstance(part, dict)}
    if not bases.get("dense") or not all(bases.values()):
        print(json.dumps({"status": "not-run", "reason": "every embedding service needs an api_base, "
                          "so its requests can be counted and capped"}))
        return 2
    limit_tokens = int(embedding.get("max_input_tokens") or 4096)
    limit_chars = 4 * limit_tokens  # shortcut: about 4 characters per token in English; sizes use 1.5x and 3x margins
    plan = {"server": args.server, "embedding_services": sorted(bases), "max_input_tokens": limit_tokens,
            "source_sizes_chars": [int(s * limit_chars) for s in SIZES], "max_requests": args.max_requests,
            "time_limit_s": args.time_limit, "summary_model": "local stub, no model calls",
            "owner_memory": "not touched: throwaway data folder and port"}
    if args.plan:
        print(json.dumps({"status": "plan", **plan}, indent=2))
        return 0

    budget = Budget(args.max_requests)
    work = Path(tempfile.mkdtemp(prefix="memory-check-"))
    servers, srv, report = [], None, {"status": "not-run", **plan}
    try:
        os.chmod(work, 0o700)
        (work / "home").mkdir()
        (work / "tmp").mkdir()
        local = json.loads(json.dumps(embedding))
        for name, base in bases.items():
            server, local[name]["api_base"] = proxy(base, budget)
            servers.append(server)
        stub, stub_url = stub_model(budget)
        servers.append(stub)
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        conf = work / "ov.conf"
        conf.write_text(json.dumps({
            "storage": {"workspace": str(work / "data")}, "embedding": local,
            "vlm": {"provider": "openai", "model": "stub", "api_base": stub_url, "api_key": "stub",
                    "temperature": 0, "max_retries": 0},
            "server": {"host": "127.0.0.1", "port": port}}))
        conf.chmod(0o600)
        deadline = time.time() + args.time_limit
        srv = Server(shlex.split(args.server), conf, work, port)
        srv.start(min(deadline, time.time() + 180))
        report["checks"] = results = {}
        for name, check in CHECKS.items():
            if budget.exhausted or time.time() > deadline:
                results[name] = {"passed": None, "reason": "request cap or time limit reached"}
                continue
            used = budget.used
            try:
                results[name] = check(srv, limit_chars)
            except RuntimeError as error:  # one check failing to run does not hide the others
                results[name] = {"passed": None, "reason": str(error)[:200]}
                srv.stop()
                srv.start(min(deadline, time.time() + 180))
            if budget.exhausted:
                results[name] = {"passed": None, "reason": "request cap reached during this check"}
            results[name]["embedding_requests"] = budget.used - used
        outcomes = [r["passed"] for r in results.values()]
        report["status"] = ("not-run" if None in outcomes else "passed" if all(outcomes) else "failed")
        if None in outcomes:
            report["reason"] = "a check could not finish; see checks"
    except (OSError, RuntimeError, ValueError) as error:
        report.update(status="not-run", reason=str(error)[:200])
    finally:
        if srv:
            srv.stop()
        for server in servers:
            server.shutdown()
        report.update(embedding_requests=budget.used, embedding_errors=budget.errors,
                      summary_stub_calls=budget.stub_calls)
        shutil.rmtree(work, ignore_errors=True)
        report["throwaway_folder_removed"] = not work.exists()
    print(json.dumps(report, indent=2))
    return {"passed": 0, "failed": 1}.get(report["status"], 2)


if __name__ == "__main__":
    sys.exit(main())
