"""Stage checksum-verified release archives in a private, per-job package cache."""
import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess

BASE = "https://github.com/nativelang/classify-artifacts/releases/download"
STANDARD = "v0.1.0-dm-classify-standard-r1"
MANIFESTS = {
    "v0.1.1-dm-classify-compact-r3": "68f080308b42e6df3587b98a22340b12c0419ffef7417decb33edf91a1134ac6",
    "v0.1.0-dm-classify-compact-r3-desktop": "57a2cc107c059f7809b4497e5c40fbf9f5a6be76ad4402c268043a9de5fc08ee",
    STANDARD: "256d64d3f8a62fb103ce9ed59eda419fb4284f2ef53281a550ee2d2de5a43d05",
}
STANDARD_INDEX = "01430ddd1a9ba0d319e561c95be4dfbe978b3f27686b6fd5b67acd091e59bf67"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def download(url, path, expected):
    subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", path, url], check=True)
    if sha256(path) != expected:
        raise ValueError(f"Checksum mismatch for {url}")


def extract(archive, destination):
    destination.mkdir(parents=True)
    # Windows' system tar (bsdtar) handles both the server ZIP and SDK ZIP.
    subprocess.run(["tar", "-xf", archive, "-C", destination], check=True)
    archive.unlink()


def platform_key():
    system = platform.system()
    arch = platform.machine().lower()
    if arch in ("arm64", "aarch64"):
        arch = {"Windows": "ARM64", "Linux": "aarch64", "Darwin": "arm64"}[system]
    elif arch in ("amd64", "x86_64"):
        arch = "AMD64" if system == "Windows" else "x86_64"
    return f"{system}/{arch}"


def stage(release, work, model):
    with (release / "app/releases.csv").open() as stream:
        row = next(r for r in csv.DictReader(stream) if r["platform"] == platform_key())
    target = row["target"]
    tag = row["tag"] if model == "compact" else STANDARD
    manifest = work / "manifest.json"
    download(f"{BASE}/{tag}/manifest.json", manifest, MANIFESTS[tag])
    sdk = json.loads(manifest.read_text())["targets"][target]["runtime"]
    archive = work / sdk["name"]
    download(sdk["url"], archive, sdk["sha256"])
    extract(archive, work / "sdk")

    suffix = ".zip" if os.name == "nt" else ".tar.gz"
    if model == "compact":
        name = f"classify-server-{row['version']}-dm-classify-{row['model']}-{target}{suffix}"
        digest = row["sha256"]
        archive = work / name
        download(f"{BASE}/{tag}/{name}", archive, digest)
    else:
        index = work / "downloads.json"
        download(f"{BASE}/{tag}-manual/downloads.json", index, STANDARD_INDEX)
        name = f"classify-server-{tag[1:]}-{target}{suffix}"
        entry = next(a for a in json.loads(index.read_text())["archives"] if a["name"] == name)
        digest = entry["sha256"]
        archive = work / name
        with archive.open("wb") as joined:
            for part in entry["parts"]:
                part_file = work / part["name"]
                download(f"{BASE}/{tag}-manual/{part['name']}", part_file, part["sha256"])
                with part_file.open("rb") as src:
                    shutil.copyfileobj(src, joined, 1024 * 1024)
                part_file.unlink()
        if sha256(archive) != digest:
            raise ValueError(f"Joined archive checksum mismatch for {name}")
    # The six packages select Compact. Scope this override to the benchmark child
    # process's otherwise empty home so Standard exercises the same public calls.
    install = work / "home/.nativelang/classify" / row["tag"] / target
    extract(archive, install)
    profile = json.loads((install / "model/profile.json").read_text())
    if profile["id"] != "dm-classify-" + (row["model"] if model == "compact" else "standard-r1"):
        raise ValueError(f"Unexpected profile in {name}")
    return install, {"profile": profile["id"], "archive": name, "sha256": digest,
                     "sdk_sha256": sdk["sha256"], "profile_sha256": sha256(install / "model/profile.json")}
