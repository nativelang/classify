"""Embed app/releases.csv in standalone installers and sync vendored launchers."""
from pathlib import Path

APP = Path(__file__).resolve().parent
ROOT = APP.parent


def render():
    rows = (APP / "releases.csv").read_text().rstrip()
    for path, start, end in (
        (APP / "bootstrap.sh", "<<'CLASSIFY_RELEASES'\n", "\nCLASSIFY_RELEASES"),
        (ROOT / "self-hosting/install.sh", "<<'CLASSIFY_RELEASES'\n", "\nCLASSIFY_RELEASES"),
        (APP / "install.ps1", "$releases = @'\n", "\n'@ | ConvertFrom-Csv"),
    ):
        before, rest = path.read_text().split(start)
        _, after = rest.split(end, 1)
        yield path, (before + start + rows + end + after).encode()
    for name in ("go", "rust", "python/nativelang_classify"):
        yield ROOT / "bindings" / name / "bootstrap.sh", (APP / "bootstrap.sh").read_bytes()
    yield ROOT / "bindings/python/nativelang_classify/install.ps1", (APP / "install.ps1").read_bytes()


if __name__ == "__main__":
    for path, data in render():
        path.write_bytes(data)
