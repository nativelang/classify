"""Offline first-install and recovery tests. Run with python3 -m unittest discover -s app/tests."""
import hashlib
import os
from pathlib import Path
import platform
import runpy
import signal
import subprocess
import tarfile
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "bootstrap.sh"
TAG = "v0.1.0-dm-classify-compact-r3"
TARGETS = {
    ("Darwin", "arm64"): ("aarch64-apple-darwin", "64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3"),
    ("Linux", "aarch64"): ("aarch64-unknown-linux-gnu", "fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877"),
    ("Linux", "x86_64"): ("x86_64-unknown-linux-gnu", "211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28"),
}


class EmbeddedBootstrapTests(unittest.TestCase):
    def test_embedded_release_data_and_package_copies(self):
        render = runpy.run_path(str(SCRIPT.with_name("sync_releases.py")))["render"]
        for path, expected in render():
            with self.subTest(path=path):
                self.assertEqual(path.read_bytes(), expected)


class BootstrapTests(unittest.TestCase):
    force_intel = False

    def setUp(self):
        host = (platform.system(), platform.machine())
        intel = self.force_intel or host == ("Darwin", "x86_64")
        if os.name != "posix" or (not intel and host not in TARGETS):
            self.skipTest("requires a supported local app platform")
        if intel:
            target = "x86_64-apple-darwin"
            pin = "998aee9d4eb1d895222185243a0e0c6e9381c1b99f22dee74baf67dccc40d95c"
        else:
            target, pin = TARGETS[host]
        tag = "v0.1.0-dm-classify-standard-r1" if intel else TAG
        self.parts = 2 if intel else 1
        directory = tempfile.TemporaryDirectory(prefix="classify app ")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.installed = self.home / ".nativelang" / "classify" / tag / target
        self.archive = self.root / "fixture.tar.gz"
        self.calls = self.root / "calls"
        self.barrier = self.root / "hold-download"
        source = self.root / "contents"
        (source / "model").mkdir(parents=True)
        (source / "model" / "profile.json").write_text("{}")
        (source / "model" / "model.gguf").write_bytes(b"fixture")
        cli = source / "classify"
        cli.write_text('#!/bin/sh\n[ "$1" = infer ] && [ "$2" = --profile ] && [ -r "$3" ] || exit 2\ncat\n')
        cli.chmod(0o755)
        with tarfile.open(self.archive, "w:gz") as package:
            package.add(source, arcname=".")
        script = SCRIPT.read_text()
        self.assertEqual(script.count(pin), 1)
        self.script = self.root / "bootstrap.sh"
        self.script.write_text(script.replace(pin, hashlib.sha256(self.archive.read_bytes()).hexdigest()))
        utilities = self.root / "bin"
        utilities.mkdir()
        if intel:
            uname = utilities / "uname"
            uname.write_text('#!/bin/sh\nif [ "$1" = -s ]; then echo Darwin; else echo x86_64; fi\n')
            uname.chmod(0o755)
            if platform.system() != "Darwin":
                lockf = utilities / "lockf"
                lockf.write_text('#!/bin/sh\nexec flock -x "$1"\n')
                lockf.chmod(0o755)
        curl = utilities / "curl"
        curl.write_text("""#!/bin/sh
set -eu
while [ "$1" != --output ]; do shift; done
case "$3" in
    "$FIXTURE_URL") action=copy ;;
    "$FIXTURE_URL.part-0001-of-0002") action=first ;;
    "$FIXTURE_URL.part-0002-of-0002") action=second ;;
    *) exit 3 ;;
esac
echo download >> "$FIXTURE_CALLS"
while [ -f "$FIXTURE_BARRIER" ]; do sleep 0.05; done
case "$action" in
    copy) cp "$FIXTURE_ARCHIVE" "$2" ;;
    first) head -c 10 "$FIXTURE_ARCHIVE" ;;
    second) tail -c +11 "$FIXTURE_ARCHIVE" ;;
esac
""")
        curl.chmod(0o755)
        self.env = dict(os.environ, HOME=str(self.home), PATH=str(utilities) + ":" + os.environ["PATH"],
                        FIXTURE_ARCHIVE=str(self.archive), FIXTURE_CALLS=str(self.calls),
                        FIXTURE_BARRIER=str(self.barrier),
                        FIXTURE_URL=f"https://github.com/nativelang/classify-artifacts/releases/download/{tag}{'-manual' if intel else ''}/"
                                    f"classify-server-{tag[1:]}-{target}.tar.gz")
        self.cmd = ["/bin/sh", str(self.script)]

    def run_once(self):
        return subprocess.run(self.cmd, env=self.env, input=b"test\n", capture_output=True, timeout=12)

    def start(self):
        p = subprocess.Popen(self.cmd, env=self.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, start_new_session=True)
        def cleanup():
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
            p.communicate()
        self.addCleanup(cleanup)
        return p

    def hold_first_download(self):
        self.barrier.touch()
        owner = self.start()
        deadline = time.monotonic() + 8
        while not self.calls.exists():
            self.assertIsNone(owner.poll())
            self.assertLess(time.monotonic(), deadline)
            time.sleep(0.025)
        self.assertFalse(self.installed.exists())
        return owner

    def test_concurrent_first_use_and_offline_reuse(self):
        owner = self.hold_first_download()
        clients = [owner] + [self.start() for _ in range(5)]
        self.barrier.unlink()
        for client in clients:
            stdout, stderr = client.communicate(b'test\n', timeout=12)
            self.assertEqual(client.returncode, 0, stderr)
            self.assertEqual(stdout, b'test\n')
        self.archive.unlink()
        warm = self.run_once()
        self.assertEqual((warm.returncode, warm.stdout, warm.stderr), (0, b'test\n', b''))
        self.assertEqual(self.calls.read_text().splitlines(), ["download"] * self.parts)

    def test_interrupted_owner_releases_lock(self):
        owner = self.hold_first_download()
        waiter = self.start()
        os.killpg(owner.pid, signal.SIGKILL)
        owner.communicate(timeout=5)
        self.barrier.unlink()
        stdout, stderr = waiter.communicate(b'test\n', timeout=12)
        self.assertEqual(waiter.returncode, 0, stderr)
        self.assertEqual(stdout, b'test\n')
        self.assertEqual(self.calls.read_text().splitlines(), ["download"] * (1 + self.parts))

    def test_corrupt_download_never_installs(self):
        original = self.archive.read_bytes()
        self.archive.write_bytes(b"invalid")
        bad = self.run_once()
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(bad.stdout, b'')
        self.assertFalse(self.installed.exists())
        self.archive.write_bytes(original)
        self.assertEqual(self.run_once().returncode, 0)


class IntelMultipartTests(BootstrapTests):
    force_intel = True


if __name__ == "__main__":
    unittest.main()
