"""Verify the public downloads used by the six language package managers."""
import hashlib
import io
import json
import sys
import time
import urllib.error
import zipfile

from prepare import validate
from registry import asset, fetch


def verify(version):
    validate(version)
    project = "nativelang-classify"
    module = "github.com/nativelang/classify/bindings/go"
    jar = f"classify-{version}.jar"
    crate = f"{project}-{version}.crate"
    wheel = f"nativelang_classify-{version}-py3-none-any.whl"
    npm = f"{project}-{version}.tgz"
    nuget = f"NativeLang.Classify.{version}.nupkg"
    files = {
        wheel: f"https://pypi.org/pypi/{project}/{version}/json",
        npm: f"https://registry.npmjs.org/@nativelang/classify/-/classify-{version}.tgz",
        crate: f"https://static.crates.io/crates/{project}/{crate}",
        jar: f"https://repo.maven.apache.org/maven2/io/github/nativelang/classify/{version}/{jar}",
        nuget: f"https://api.nuget.org/v3-flatcontainer/nativelang.classify/{version}/{nuget.lower()}",
        "Go": f"https://proxy.golang.org/{module}/@v/v{version}.zip",
    }
    candidates = {
        name: asset(name, version).read_bytes() for name in files if name != "Go"
    }
    for attempt in range(60):
        for name, url in list(files.items()):
            try:
                data = fetch(url)
                if data and name == wheel:
                    entry = next(
                        f for f in json.loads(data)["urls"] if f["filename"] == wheel
                    )
                    data = fetch(entry["url"])
                if data and name == npm:
                    metadata = fetch(
                        "https://registry.npmjs.org/@nativelang%2fclassify/latest"
                    )
                    if not metadata or json.loads(metadata)["version"] != version:
                        data = None
            except (urllib.error.URLError, TimeoutError) as e:
                print(f"Waiting for {name}: {e}", flush=True)
                continue
            if not data:
                continue
            if name == "Go":
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    prefix = f"{module}@v{version}/"
                    if z.testzip() or not all(
                        prefix + n in z.namelist()
                        for n in ("go.mod", "classify.go", "LICENSE")
                    ):
                        raise RuntimeError("Invalid Go proxy archive")
            elif name == nuget:
                with zipfile.ZipFile(io.BytesIO(data)) as remote, zipfile.ZipFile(
                    io.BytesIO(candidates[name])
                ) as local:
                    if set(remote.namelist()) - {".signature.p7s"} != set(
                        local.namelist()
                    ) or any(remote.read(n) != local.read(n) for n in local.namelist()):
                        raise RuntimeError("NuGet content differs from the release")
            elif (
                hashlib.sha256(data).digest()
                != hashlib.sha256(candidates[name]).digest()
            ):
                raise RuntimeError(f"Public download differs from the release: {name}")
            print("Verified", name, flush=True)
            del files[name]
        if not files:
            return
        time.sleep(30)
    raise RuntimeError("Awaiting public availability: " + ", ".join(files))


if __name__ == "__main__":
    verify(sys.argv[1])
