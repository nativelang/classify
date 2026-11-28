"""Render native release pins and the package launchers from their shared sources."""
import json
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = APP.parent

def render():
    rows = (APP / "releases.csv").read_text().rstrip()
    sources = {}
    for path, start, end in (
        (APP / "native-bootstrap.sh", "<<'CLASSIFY_RELEASES'\n", "\nCLASSIFY_RELEASES"),
        (ROOT / "self-hosting/install.sh", "<<'CLASSIFY_RELEASES'\n", "\nCLASSIFY_RELEASES"),
        (APP / "native-install.ps1", "$releases = @'\n", "\n'@ | ConvertFrom-Csv"),
    ):
        before, rest = path.read_text().split(start)
        _, after = rest.split(end, 1)
        sources[path.name] = before + start + rows + end + after
        yield path, sources[path.name].encode()

    pins = json.loads((APP / "pack/service-hashes.json").read_text())
    hosts = {"darwin-arm64": "Darwin/arm64", "darwin-amd64": "Darwin/x86_64",
             "linux-arm64": "Linux/aarch64|Linux/arm64", "linux-amd64": "Linux/x86_64"}
    cases = [f"        {host}) target={target}; sha={pins[target]} ;;"
             for target, host in hosts.items()]
    dispatch = (APP / "pack/launcher.sh").read_text().replace("@UNIX_TARGETS@", "\n".join(cases))
    shell = sources["native-bootstrap.sh"].replace("set -eu\n", "set -eu\n" + dispatch, 1).encode()
    hosts = {"windows-arm64": 12, "windows-amd64": 9}
    cases = [f"        {cpu} {{ $target = '{target}'; $sha = '{pins[target]}' }}" for target, cpu in hosts.items()]
    dispatch = (APP / "pack/launcher.ps1").read_text().replace("@WINDOWS_TARGETS@", "\n".join(cases))
    ps = sources["native-install.ps1"].replace("$releases = ", dispatch + "$releases = ", 1)
    yield APP / "bootstrap.sh", shell
    yield APP / "install.ps1", ps.encode()
    for name in ("go", "rust", "python/nativelang_classify"):
        yield ROOT / "bindings" / name / "bootstrap.sh", shell
    yield ROOT / "bindings/python/nativelang_classify/install.ps1", ps.encode()
    for name in ("go", "rust"):
        yield ROOT / "bindings" / name / "install.ps1", ps.encode()

if __name__ == "__main__":
    for path, data in render():
        path.write_bytes(data)
