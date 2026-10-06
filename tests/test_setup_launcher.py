"""Actual Bash launcher tests. All prerequisites are synthetic, never installed."""
from __future__ import annotations

import hashlib
import json
import os
import pty
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL = "curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"


class Launcher(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "home"
        (self.home / ".hermes").mkdir(parents=True)
        self.modules = self.root / "modules"
        (self.modules / "ruamel").mkdir(parents=True)
        (self.modules / "yaml.py").write_text("")
        (self.modules / "ruamel/__init__.py").write_text("")
        (self.modules / "ruamel/yaml.py").write_text("")
        self.traps = self.root / "traps"
        self.probes = self.root / "probes"
        self.dispatch = self.root / "dispatch.json"
        self.env = {"HOME": str(self.home), "HERMES_HOME": str(self.home / ".hermes"),
                    "PATH": str(self.bin), "TMPDIR": str(self.root), "PYTHONDONTWRITEBYTECODE": "1",
                    "HERMES_DISABLE_LAZY_INSTALLS": "1", "PYTHONPATH": str(self.modules)}
        for command in ("dirname", "readlink", "grep", "head"):
            executable = shutil.which(command)
            assert executable is not None
            (self.bin / command).symlink_to(executable)
        for command in ("curl", "sudo", "pip", "pip3", "uv", "bash", "wget"):
            self.trap(self.bin / command)
        self.recorder = self.root / "record.py"
        self.recorder.write_text("import json,sys\nfrom pathlib import Path\n"
                                 f"Path({str(self.dispatch)!r}).write_text(json.dumps(sys.argv[1:]))\n")
        self.python = self.bin / "python3"
        self.make_python(self.python)

    def script(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/bash\n" + text)
        path.chmod(0o755)
        return path

    def trap(self, path):
        return self.script(path, f"printf '%s\\n' {shlex.quote(path.name)} >> {shlex.quote(str(self.traps))}\nexit 97\n")

    def make_python(self, path, real_dispatch=False):
        # Probe actual imports under -S with controlled fixture packages. Dispatch
        # records exact argv unless the test explicitly requests the real installer.
        python = shlex.quote(sys.executable)
        dispatch = f'exec {python} "$@"' if real_dispatch else f'exec {python} {shlex.quote(str(self.recorder))} "$@"'
        return self.script(path, f'if [[ "${{1-}}" == -c ]]; then\n'
                           f'  printf "probe\\n" >> {shlex.quote(str(self.probes))}\n'
                           f'  exec {python} -S "$@"\nfi\n{dispatch}\n')

    def inventory(self):
        return {str(p.relative_to(self.root)): ("dir" if p.is_dir() else
                "link:" + os.readlink(p) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest())
                for p in self.root.rglob("*") if p not in (self.probes, self.dispatch)}

    def invoke(self, args=("setup", "creator"), answer=None, interactive=False):
        before = self.inventory()
        cmd = ["/bin/bash", str(ROOT / "hbt"), *args]
        if interactive:
            master, slave = pty.openpty()
            try:
                p = subprocess.Popen(cmd, cwd=ROOT, env=self.env, stdin=slave,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                os.close(slave)
                slave = None
                os.write(master, (answer if answer is not None else "\x04").encode())
                out = p.communicate(timeout=10)[0].decode()
            finally:
                os.close(master)
                if slave is not None:
                    os.close(slave)
        else:
            p = subprocess.run(cmd, cwd=ROOT, env=self.env, input=answer, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
            out = p.stdout
        self.assertFalse(self.traps.exists(), "An installer or native launcher executed")
        self.assertEqual(before, self.inventory(), "Launcher changed state outside probe/dispatch counters")
        return p.returncode, out

    def test_missing_hermes_consent_matrix_has_no_side_effects(self):
        for answer in ("n\n", "\n", "maybe\n", None, "y\n", "yes\n", "YES\n"):
            with self.subTest(answer=answer):
                code, output = self.invoke(answer=answer, interactive=True)
                self.assertNotEqual(code, 0)
                self.assertIn("Hermes was not found", output)
                self.assertIn("will not download, install, modify the host or continue setup", output)
                self.assertIn("prerequisites unresolved; setup not completed", output)
                self.assertEqual(INSTALL in output, answer in ("y\n", "yes\n", "YES\n"))
                self.assertFalse(self.probes.exists())
                self.assertFalse(self.dispatch.exists())

    def test_redirected_yes_eof_and_nonsetup_never_offer_consent(self):
        for answer in ("yes\n", "", None):
            code, output = self.invoke(answer=answer)
            self.assertNotEqual(code, 0)
            self.assertNotIn("[y/N]", output)
            self.assertNotIn(INSTALL, output)
        self.python.unlink()
        code, output = self.invoke(("install", "creator", "--yes"), answer="yes\n", interactive=True)
        self.assertNotEqual(code, 0)
        self.assertNotIn("[y/N]", output)
        self.assertNotIn(INSTALL, output)
        self.assertFalse(self.dispatch.exists())

    def test_missing_python_or_either_dependency(self):
        self.trap(self.bin / "hermes")
        for missing in ("python", "yaml", "ruamel"):
            with self.subTest(missing=missing):
                path = {"python": self.python, "yaml": self.modules / "yaml.py",
                        "ruamel": self.modules / "ruamel/yaml.py"}[missing]
                saved = path.read_bytes()
                path.unlink()
                code, output = self.invoke(answer="yes\n", interactive=True)
                self.assertNotEqual(code, 0)
                self.assertIn("No usable Python", output)
                self.assertNotIn("Hermes was not found", output)
                self.assertIn(INSTALL, output)
                self.assertFalse(self.dispatch.exists())
                path.write_bytes(saved)
                if missing == "python":
                    path.chmod(0o755)

    def test_invalid_explicit_overrides_never_fall_back(self):
        self.trap(self.bin / "hermes")
        for key in ("HBT_PYTHON", "HBT_HERMES"):
            for value in ("", str(self.root / "not executable"), "missing-command"):
                with self.subTest(key=key, value=value):
                    self.env[key] = value
                    code, output = self.invoke(answer="n\n", interactive=True)
                    self.assertNotEqual(code, 0)
                    self.assertIn("explicit", output.lower())
                    self.assertIn("no fallback", output.lower())
                    self.assertFalse(self.dispatch.exists())
                    del self.env[key]
        for args in (("--hermes", "missing-command", "setup", "creator"),
                     ("--hermes=missing-command", "setup", "creator")):
            code, output = self.invoke(args, answer="yes\n", interactive=True)
            self.assertNotEqual(code, 0)
            self.assertIn(INSTALL, output)

    def test_explicit_python_with_missing_dependency_is_not_accepted(self):
        self.trap(self.bin / "hermes")
        self.env["HBT_PYTHON"] = str(self.python)
        (self.modules / "yaml.py").unlink()
        code, output = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertIn("HBT_PYTHON is not usable", output)
        self.assertFalse(self.dispatch.exists())

    def test_supported_paths_spaces_and_exact_argument_forwarding(self):
        hermes = self.trap(self.root / "custom tools/venv/bin/hermes")
        python = self.make_python(hermes.parent / "python")
        self.env["HBT_HERMES"] = "unavailable-default"
        variants = [("--hermes", str(hermes), "--verbose", "setup", "creator"),
                    ("-v", "--hermes=" + str(hermes), "setup", "creator")]
        for args in variants:
            code, output = self.invoke(args)
            self.assertEqual(code, 0, output)
            self.assertEqual(json.loads(self.dispatch.read_text()), [str(ROOT / "installer/hbt.py"), *args])
            self.assertTrue(self.probes.exists())
        self.env["HBT_HERMES"] = str(hermes)
        self.env["HBT_PYTHON"] = str(python)
        args = ("install", "creator", "--roles", "cto,ops", "--projects", "folder with spaces", "--yes")
        code, output = self.invoke(args)
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(self.dispatch.read_text()), [str(ROOT / "installer/hbt.py"), *args])

    def test_unusable_adjacent_python_is_probed_then_fallback_validated(self):
        hermes = self.trap(self.root / "custom tools/hermes")
        self.script(hermes.parent / "python", "exit 1\n")
        self.env["HBT_HERMES"] = str(hermes)
        code, output = self.invoke()
        self.assertEqual(code, 0, output)
        self.assertTrue(self.probes.exists())
        self.assertTrue(self.dispatch.exists())

    def test_nonsetup_dispatch_without_hermes_is_preserved(self):
        code, output = self.invoke(("--help",))
        self.assertEqual(code, 0, output)
        self.assertEqual(json.loads(self.dispatch.read_text()), [str(ROOT / "installer/hbt.py"), "--help"])

    def test_reinvocation_rediscovers_prerequisites_and_keeps_incomplete_install(self):
        code, _ = self.invoke(answer="yes\n", interactive=True)
        self.assertNotEqual(code, 0)
        code, _ = self.invoke()
        self.assertNotEqual(code, 0)
        self.trap(self.bin / "hermes")
        code, output = self.invoke()
        self.assertEqual(code, 0, output)
        self.assertTrue(self.dispatch.exists())
        # Switch only the fixture interpreter's dispatch to exercise the actual
        # installer. Its dependency-complete runtime is already present, not bootstrapped.
        self.make_python(self.python, real_dispatch=True)
        del self.env["PYTHONPATH"]
        self.env["HBT_PYTHON"] = sys.executable
        record = self.home / ".hermes/business-templates/creator/record.json"
        record.parent.mkdir(parents=True)
        record.write_text(json.dumps({"version": "pending", "profiles": [], "setup": {}}))
        for _ in range(2):
            code, output = self.invoke()
            self.assertEqual(code, 1, output)
            self.assertIn("Installation is incomplete", output)
            self.assertNotIn("Select roles", output)

    def test_real_setup_rechecks_after_only_hermes_availability_changes(self):
        self.env["HBT_PYTHON"] = sys.executable
        del self.env["PYTHONPATH"]
        for _ in range(2):
            code, output = self.invoke()
            self.assertEqual(code, 1)
            self.assertIn("Hermes was not found", output)
        self.trap(self.bin / "hermes")
        # No record exists: real setup reaches fresh role selection, then EOF.
        code, output = self.invoke(answer="")
        self.assertEqual(code, 1, output)
        self.assertIn("Select roles", output)
        self.assertIn("Setup stopped", output)
        self.assertFalse((self.home / ".hermes/business-templates").exists())
        # A complete legacy Ops subset resumes without adding roles or testing bots.
        profile = self.home / ".hermes/profiles/ops"
        profile.mkdir(parents=True)
        (profile / "config.yaml").write_text("{}")
        record = self.home / ".hermes/business-templates/creator/record.json"
        record.parent.mkdir(parents=True)
        record.write_text(json.dumps({"version": "fixture", "profiles": ["ops"],
                                     "workspace": str(self.home / "workspace"),
                                     "setup": {"system_channel_ok": "skipped", "restarted": "fixture"}}))
        code, output = self.invoke()
        self.assertEqual(code, 0, output)
        self.assertIn("No conversational bots", output)
        self.assertIn("demonstration was not run", output)
        self.assertNotIn("Select roles", output)


if __name__ == "__main__":
    unittest.main()
