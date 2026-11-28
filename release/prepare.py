"""Build the tagged source and publish its immutable GitHub assets and Go module tag."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = "nativelang/classify"


def run(*args, cwd=ROOT, **kw):
    return subprocess.run(args, cwd=cwd, check=True, **kw)


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def release_info(tag):
    proc = subprocess.run(
        ["gh", "api", f"repos/{REPO}/releases/tags/{tag}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode and "HTTP 404" in proc.stderr:
        return None
    proc.check_returncode()
    return json.loads(proc.stdout)


def publish_assets(tag, sha, files, latest):
    info = release_info(tag)
    if info:
        actual = {a["name"]: a["digest"] for a in info["assets"]}
        if info["draft"] or any(
            actual.get(p.name) != "sha256:" + digest(p) for p in files
        ):
            raise RuntimeError(
                f"Existing {tag} release differs from the verified artifacts"
            )
        return
    run(
        "gh",
        "release",
        "create",
        tag,
        *files,
        "--repo",
        REPO,
        "--target",
        sha,
        "--title",
        "Classify " + tag,
        "--notes",
        "Verified release artifacts for " + tag + ".",
        "--latest=" + str(latest).lower(),
    )


def validate(version):
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version):
        raise ValueError("Expected a release version such as 0.3.0")
    return version


def go_tag(version, sha):
    tag = "bindings/go/v" + version
    existing = output("git", "ls-remote", "origin", "refs/tags/" + tag)
    if existing:
        if existing.split()[0] != sha:
            raise RuntimeError(f"Existing Go tag {tag} has a different commit")
    else:
        run("git", "push", "origin", sha + ":refs/tags/" + tag)


def main(version):
    validate(version)
    signing_key = os.environ.pop("CENTRAL_SIGNING_KEY")
    passphrase = os.environ.pop("CENTRAL_SIGNING_PASSPHRASE")
    tag = "v" + version
    info = release_info(tag)
    if info:
        sha = output("git", "rev-parse", tag + "^{commit}")
        run("git", "merge-base", "--is-ancestor", sha, "HEAD")
        if info["draft"] or not any(a["name"] == "SHA256SUMS" for a in info["assets"]):
            raise RuntimeError("Incomplete existing release")
        go_tag(version, sha)
        print("Reusing released artifacts at", sha)
        return
    sha = output("git", "rev-parse", "HEAD")
    if (
        json.loads((ROOT / "bindings/node/package.json").read_text())["version"]
        != version
    ):
        raise RuntimeError("Release version differs from the checked-out package")
    with tempfile.TemporaryDirectory() as temp:
        out = Path(temp) / "dist"
        out.mkdir()
        service = Path(temp) / "service"
        run(sys.executable, "app/pack/build.py", service)
        service_tag = re.search(
            r"releases/download/(service-v[\d.]+)/",
            (ROOT / "app/pack/launcher.sh").read_text(),
        )[1]
        run(
            "cargo",
            "package",
            "--locked",
            "--target-dir",
            str(Path(temp) / "cargo"),
            cwd=ROOT / "bindings/rust",
        )
        shutil.copyfile(
            Path(temp) / "cargo/package" / f"nativelang-classify-{version}.crate",
            out / f"nativelang-classify-{version}.crate",
        )
        run(
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "-w",
            out,
            "./bindings/python",
        )
        run("npm", "pack", "--pack-destination", out, cwd=ROOT / "bindings/node")
        run(
            "dotnet",
            "pack",
            "bindings/csharp/NativeLang.Classify.csproj",
            "-c",
            "Release",
            "-o",
            out,
        )
        gson = Path(temp) / "gson.jar"
        for host in (
            "https://repo.maven.apache.org/maven2",
            "https://repo1.maven.org/maven2",
            "https://maven-central.storage-download.googleapis.com/maven2",
        ):
            if (
                subprocess.run(
                    [
                        "curl",
                        "-fsSL",
                        "--retry",
                        "2",
                        "-o",
                        gson,
                        host + "/com/google/code/gson/gson/2.15.0/gson-2.15.0.jar",
                    ]
                ).returncode
                == 0
            ):
                break
        fp = next(
            row.split(":")[9]
            for row in output(
                "gpg", "--with-colons", "--show-keys", "release/ci-signing-key.asc"
            ).splitlines()
            if row.startswith("fpr:")
        )
        run(
            "gpg",
            "--batch",
            "--import",
            input=signing_key.encode(),
            stdout=subprocess.DEVNULL,
        )
        central = out / f"classify-{version}-central.zip"
        run(
            sys.executable,
            "bindings/java/central-bundle.py",
            gson,
            fp,
            central,
            env=dict(os.environ, CENTRAL_SIGNING_PASSPHRASE=passphrase),
        )
        with zipfile.ZipFile(central) as z:
            name = f"classify-{version}.jar"
            (out / name).write_bytes(
                z.read(f"io/github/nativelang/classify/{version}/{name}")
            )
        expected = {
            f"nativelang_classify-{version}-py3-none-any.whl",
            f"nativelang-classify-{version}.tgz",
            f"NativeLang.Classify.{version}.nupkg",
            f"nativelang-classify-{version}.crate",
            central.name,
            name,
        }
        if {p.name for p in out.iterdir()} != expected:
            raise RuntimeError("Unexpected language release inventory")
        (out / "SHA256SUMS").write_text(
            "".join(f"{digest(p)}  {p.name}\n" for p in sorted(out.iterdir()))
        )
        publish_assets(service_tag, sha, sorted(service.iterdir()), False)
        publish_assets(tag, sha, sorted(out.iterdir()), True)
        go_tag(version, sha)


if __name__ == "__main__":
    main(sys.argv[1])
