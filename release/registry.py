"""Verify GitHub release bytes before publishing or retrying a registry job."""
from pathlib import Path
import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from prepare import REPO, ROOT, validate


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=45) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def asset(name, version):
    folder = Path(os.environ["RUNNER_TEMP"]) / "verified-release"
    folder.mkdir(exist_ok=True)
    subprocess.run(
        [
            "gh",
            "release",
            "download",
            "v" + version,
            "--repo",
            REPO,
            "--dir",
            folder,
            "-p",
            "SHA256SUMS",
            "-p",
            name,
            "--clobber",
        ],
        check=True,
    )
    pins = {
        n: h
        for h, n in (
            line.split() for line in (folder / "SHA256SUMS").read_text().splitlines()
        )
    }
    p = folder / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != pins[name]:
        raise RuntimeError("Release checksum mismatch for " + name)
    return p


def central_request(path, body, content_type):
    req = urllib.request.Request(
        "https://central.sonatype.com/api/v1/publisher/" + path,
        data=body,
        headers={
            "Authorization": "Bearer " + os.environ["CENTRAL_PORTAL_TOKEN"],
            "Content-Type": content_type,
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def publish_maven(version, path):
    name = f"classify-{version}.jar"
    jar = asset(name, version)
    published = fetch(
        f"https://repo.maven.apache.org/maven2/io/github/nativelang/classify/{version}/{name}"
    )
    if published is not None:
        if (
            hashlib.sha256(published).digest()
            != hashlib.sha256(jar.read_bytes()).digest()
        ):
            raise RuntimeError("Central JAR mismatch")
        print("Maven Central already has the verified JAR")
        return
    import uuid

    boundary = uuid.uuid4().hex
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="bundle"; filename="{path.name}"\r\nContent-Type: application/zip\r\n\r\n'.encode()
        + path.read_bytes()
        + f"\r\n--{boundary}--\r\n".encode()
    )
    deployment = (
        central_request(
            f"upload?publishingType=AUTOMATIC&name=classify-{version}",
            body,
            "multipart/form-data; boundary=" + boundary,
        )
        .decode()
        .strip()
        .strip('"')
    )
    uuid.UUID(deployment)
    print("Central deployment", deployment, flush=True)
    for _ in range(120):
        info = json.loads(
            central_request("status?id=" + deployment, b"", "application/json")
        )
        if info["deploymentState"] == "PUBLISHED":
            return
        if info["deploymentState"] == "FAILED":
            raise RuntimeError(str(info.get("errors", {})))
        time.sleep(15)
    raise RuntimeError("Check the reported Central deployment before retrying")


def main(registry, version):
    validate(version)
    names = {
        "python": f"nativelang_classify-{version}-py3-none-any.whl",
        "npm": f"nativelang-classify-{version}.tgz",
        "nuget": f"NativeLang.Classify.{version}.nupkg",
        "cargo": f"nativelang-classify-{version}.crate",
        "maven": f"classify-{version}-central.zip",
    }
    p = asset(names[registry], version)
    if registry == "python":
        from shutil import copyfile

        dist = Path("dist")
        dist.mkdir(exist_ok=True)
        copyfile(p, dist / p.name)
    elif registry == "maven":
        publish_maven(version, p)
    elif registry == "npm":
        existing = fetch("https://registry.npmjs.org/@nativelang%2fclassify/" + version)
        if existing:
            actual = json.loads(existing)["dist"]["integrity"]
            if (
                actual
                != "sha512-"
                + base64.b64encode(hashlib.sha512(p.read_bytes()).digest()).decode()
            ):
                raise RuntimeError("npm integrity mismatch")
            return
        subprocess.run(
            [
                "npm",
                "publish",
                p,
                "--registry=https://registry.npmjs.org",
                "--access",
                "public",
                "--tag",
                "latest",
            ],
            check=True,
        )
    elif registry == "nuget":
        url = f"https://api.nuget.org/v3-flatcontainer/nativelang.classify/{version}/nativelang.classify.{version}.nupkg"
        existing = fetch(url)
        if existing:
            # NuGet.org adds its repository signature. Compare the package content.
            import zipfile

            with zipfile.ZipFile(io.BytesIO(existing)) as remote, zipfile.ZipFile(
                p
            ) as local:
                if set(remote.namelist()) - {".signature.p7s"} != set(
                    local.namelist()
                ) or any(remote.read(n) != local.read(n) for n in local.namelist()):
                    raise RuntimeError("NuGet payload mismatch")
            return
        subprocess.run(
            [
                "dotnet",
                "nuget",
                "push",
                str(p),
                "--source",
                "https://api.nuget.org/v3/index.json",
                "--api-key",
                os.environ["NUGET_API_KEY"],
            ],
            check=True,
        )
    elif registry == "cargo":
        existing = fetch("https://index.crates.io/na/ti/nativelang-classify")
        if existing:
            entry = next(
                (
                    json.loads(row)
                    for row in existing.splitlines()
                    if json.loads(row)["vers"] == version
                ),
                None,
            )
            if entry:
                if entry["cksum"] != hashlib.sha256(p.read_bytes()).hexdigest():
                    raise RuntimeError("crates.io checksum mismatch")
                return
        subprocess.run(["git", "fetch", "--tags", "origin"], check=True)
        subprocess.run(["git", "checkout", "--detach", "v" + version], check=True)
        crate = ROOT / "bindings/rust"
        target = Path(os.environ["RUNNER_TEMP"]) / "cargo"
        subprocess.run(
            ["cargo", "package", "--locked", "--target-dir", target],
            cwd=crate,
            check=True,
        )
        built = target / "package" / p.name
        if (
            hashlib.sha256(built.read_bytes()).digest()
            != hashlib.sha256(p.read_bytes()).digest()
        ):
            raise RuntimeError("Cargo package differs from the tagged release")
        subprocess.run(
            ["cargo", "publish", "--locked", "--registry", "crates-io"],
            cwd=crate,
            check=True,
        )


if __name__ == "__main__":
    main(*sys.argv[1:])
