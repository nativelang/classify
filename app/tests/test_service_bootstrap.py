"""Verify the package's actual service installer before any executable runs."""
import hashlib
import os
from pathlib import Path
import platform
import re
import subprocess
import tarfile
import tempfile
import unittest

APP = Path(__file__).resolve().parents[1]

@unittest.skipUnless(os.name == "posix", "POSIX package launcher")
class ServiceBootstrapTest(unittest.TestCase):
    def test_verify_install_and_reuse(self):
        host = {"Darwin": "darwin", "Linux": "linux"}[platform.system()]
        arch = "arm64" if platform.machine() in ("arm64", "aarch64") else "amd64"
        target = f"{host}-{arch}"
        with tempfile.TemporaryDirectory(prefix="service install ") as tmp:
            work = Path(tmp)
            bin_dir = work / "tools"
            bin_dir.mkdir()
            curl = bin_dir / "curl"
            curl.write_text('#!/bin/sh\nwhile [ "$1" != "-o" ]; do shift; done\ncp "$ARCHIVE" "$2"\n')
            curl.chmod(0o755)
            exe = work / "classify"
            exe.write_text('#!/bin/sh\nprintf "%s\\n" "$1"\n')
            exe.chmod(0o755)
            license_file = work / "LICENSE.txt"
            license_file.write_text("test fixture")
            archive = work / "package.tgz"
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(exe, arcname="classify")
                tar.add(license_file, arcname="LICENSE.txt")
            good = archive.read_bytes()
            shell = (APP / "bootstrap.sh").read_text()
            shell, count = re.subn(f"target={target}; sha=[0-9a-f]{{64}}", f"target={target}; sha={hashlib.sha256(good).hexdigest()}", shell)
            self.assertEqual(count, 1)
            env = dict(os.environ, HOME=tmp, PATH=str(bin_dir)+":"+os.environ["PATH"], ARCHIVE=str(archive), NATIVELANG_CLASSIFY_SERVICE="1")
            def launch():
                return subprocess.run(["/bin/sh", "-c", shell], env=env, capture_output=True, text=True, timeout=10)
            archive.write_bytes(b"bad")
            self.assertNotEqual(launch().returncode, 0)
            self.assertFalse((work / ".nativelang/classify/bin/classify").exists())
            archive.write_bytes(good)
            self.assertEqual(launch().stdout, "infer\n")
            archive.unlink()
            self.assertEqual(launch().stdout, "infer\n")
