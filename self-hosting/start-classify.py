"""Download the local Classify server once and run it in the foreground."""

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RELEASES = "https://github.com/nativelang/classify-artifacts/releases/download"
# Each digest identifies the complete archive, including both parts where applicable.
SERVERS = {
    ("Darwin", "arm64"): ("compact-r3", "aarch64-apple-darwin.tar.gz", "64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3"),
    ("Darwin", "x86_64"): ("standard-r1", "x86_64-apple-darwin.tar.gz", "998aee9d4eb1d895222185243a0e0c6e9381c1b99f22dee74baf67dccc40d95c"),
    ("Linux", "arm64"): ("compact-r3", "aarch64-unknown-linux-gnu.tar.gz", "fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877"),
    ("Linux", "x86_64"): ("compact-r3", "x86_64-unknown-linux-gnu.tar.gz", "211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28"),
    ("Windows", "arm64"): ("standard-r1", "aarch64-pc-windows-msvc.zip", "7463ae150d1aa12fa2ce0f6b2c1a9c8723b56de862d1fe87180684648bd63030"),
    ("Windows", "x86_64"): ("standard-r1", "x86_64-pc-windows-msvc.zip", "fa7fddf19ed3ee54294d9c791a0a9f8009954cdd7dee2b00532731d524bcea0b"),
}


def install(model, target, digest, destination, executable):
    name = f"classify-server-0.1.0-dm-classify-{model}-{target}"
    tag = f"v0.1.0-dm-classify-{model}"
    if model == "standard-r1":
        tag += "-manual"
        files = [name + ".part-0001-of-0002", name + ".part-0002-of-0002"]
    else:
        files = [name]

    with tempfile.TemporaryDirectory(dir=destination.parent) as tmp:
        archive = Path(tmp) / name
        with archive.open("wb") as output:
            for filename in files:
                print(f"Downloading {filename}", flush=True)
                subprocess.run(["curl", "-q", "--fail", "--location", "--show-error",
                                f"{RELEASES}/{tag}/{filename}"], stdout=output, check=True)
        checksum = hashlib.sha256()
        with archive.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                checksum.update(block)
        if checksum.hexdigest() != digest:
            raise ValueError("Download did not match the published checksum. Run the command again.")
        unpacked = Path(tmp) / "server"
        shutil.unpack_archive(str(archive), str(unpacked))
        if not (unpacked / executable).is_file():
            raise ValueError("The server executable is missing.")
        try:
            unpacked.rename(destination)
        except OSError:
            if not (destination / executable).is_file():
                raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "start"), nargs="?",
                        help="install the server and model, or start the installed server")
    action = parser.parse_args().action
    system = platform.system()
    machine = platform.machine().lower()
    machine = {"aarch64": "arm64", "amd64": "x86_64"}.get(machine, machine)
    if (system, machine) not in SERVERS:
        sys.exit(f"No server download for {system} {machine}. See the manual installation guide.")
    model, target, digest = SERVERS[system, machine]
    cache = Path.home() / ".nativelang" / "classify"
    destination = cache / digest
    executable = "classify.exe" if system == "Windows" else "classify"
    server = destination / executable
    if not server.is_file():
        if action == "start":
            sys.exit("Install Classify first: run this script with 'install'.")
        cache.mkdir(parents=True, exist_ok=True, mode=0o700)
        install(model, target, digest, destination, executable)
    if action == "install":
        print("Classify is installed.")
        return
    print("Starting Classify. Open http://127.0.0.1:8080/health to check it is ready.", flush=True)
    if system == "Windows":
        sys.exit(subprocess.run([str(server), "serve"]).returncode)
    os.execl(str(server), str(server), "serve")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except (OSError, ValueError, subprocess.CalledProcessError, shutil.ReadError) as error:
        sys.exit(f"Could not start Classify: {error}")
