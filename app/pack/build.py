"""Build reproducible service archives with the Go standard library and its license."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

APP = Path(__file__).resolve().parents[1]
GO = "go1.26.11"
TARGETS = [(os_name, arch) for os_name in ("darwin", "linux", "windows") for arch in ("amd64", "arm64")]

def build(folder):
    env = dict(os.environ, GOTOOLCHAIN=GO, CGO_ENABLED="0")
    root = Path(subprocess.check_output(["go", "env", "GOROOT"], env=env, cwd=APP, text=True).strip())
    license_text = (APP.parent / "LICENSE").read_bytes() + b"\nGo standard library and runtime (" + GO.encode() + b", https://go.dev/src/):\n" + (root / "LICENSE").read_bytes()
    # Include bundled licenses shipped with the toolchain, including vendored stdlib code.
    for path in sorted((root / "src").rglob("LICENSE*")):
        if path.is_file():
            license_text += b"\n" + str(path.relative_to(root)).encode() + b"\n" + path.read_bytes()
    folder.mkdir(parents=True, exist_ok=True)
    pins = {}
    with tempfile.TemporaryDirectory() as temp:
        for system, arch in TARGETS:
            target = system + "-" + arch
            exe = "classify.exe" if system == "windows" else "classify"
            binary = Path(temp) / exe
            subprocess.run(["go", "build", "-trimpath", "-buildvcs=false", "-ldflags=-s -w -buildid=", "-o", binary, "."],
                           env=dict(env, GOOS=system, GOARCH=arch), cwd=APP, check=True)
            path = folder / f"classify-service-{target}.tar.gz"
            with path.open("wb") as f, gzip.GzipFile(filename="", fileobj=f, mode="wb", mtime=0, compresslevel=9) as gz, tarfile.open(fileobj=gz, mode="w") as tar:
                for name, data, mode in ((exe, binary.read_bytes(), 0o755), ("LICENSE.txt", license_text, 0o644)):
                    item = tarfile.TarInfo(name)
                    item.size = len(data)
                    item.mode = mode
                    tar.addfile(item, io.BytesIO(data))
            pins[target] = hashlib.sha256(path.read_bytes()).hexdigest()
            print(target, pins[target], flush=True)
    return pins

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--write-pins", action="store_true")
    args = parser.parse_args()
    pins = build(args.output.resolve())
    path = APP / "pack/service-hashes.json"
    if args.write_pins:
        path.write_text(json.dumps(pins, indent=2) + "\n")
    elif pins != json.loads(path.read_text()):
        raise SystemExit("Built archives differ from the pinned release")
