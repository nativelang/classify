"""Exercise packaged clients on one CI account with the just-built service executable."""
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WINDOWS = os.name == "nt"
ENV = dict(os.environ, NATIVELANG_CLASSIFY_SERVICE="1")

def run(args, cwd, **settings):
    result = subprocess.run(args, cwd=cwd, env=dict(ENV, **settings), text=True, stdout=subprocess.PIPE, timeout=360)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed ({result.returncode}): {result.stdout[-2000:]}")
    return result.stdout.strip()

def example(key, folder):
    markdown = (ROOT / f"examples/{key}/README.md").read_text()
    lang = {"node": "javascript"}.get(key, key)
    code = re.search(r"```" + lang + r"\n(.*?)\n```", markdown, re.S)[1] + "\n"
    if key == "python":
        run([sys.executable, "-m", "venv", "venv"], folder)
        python = folder / ("venv/Scripts/python.exe" if WINDOWS else "venv/bin/python")
        run([python, "-m", "pip", "install", ROOT / "bindings/python"], folder)
        output = run([python, "-c", code], folder)
    elif key == "node":
        npm = shutil.which("npm.cmd" if WINDOWS else "npm")
        run([npm, "pack", "--pack-destination", folder], ROOT / "bindings/node")
        run([npm, "install", next(folder.glob("*.tgz"))], folder)
        (folder / "movie.mjs").write_text(code)
        output = run(["node", "movie.mjs"], folder)
    elif key == "go":
        run(["go", "mod", "init", "movie"], folder)
        run(["go", "mod", "edit", "-replace", f"github.com/nativelang/classify/bindings/go={(ROOT/'bindings/go').as_posix()}"], folder)
        run(["go", "get", "github.com/nativelang/classify/bindings/go"], folder)
        (folder / "main.go").write_text(code)
        output = run(["go", "run", "."], folder)
    elif key == "rust":
        run(["cargo", "init", "--bin", "--name", "movie", "--vcs", "none"], folder)
        run(["cargo", "add", "--path", ROOT / "bindings/rust"], folder)
        (folder / "src/main.rs").write_text(code)
        output = run(["cargo", "run", "--quiet"], folder)
    elif key == "java":
        gson = folder / "gson.jar"
        with urllib.request.urlopen("https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.15.0/gson-2.15.0.jar") as source:
            gson.write_bytes(source.read())
        assert hashlib.sha256(gson.read_bytes()).hexdigest() == "96d3dd843dc2911de01cdabcd50064cb9e860353102a0a78c96fd833d396fc7d"
        run([os.environ.get("CLASSIFY_TEST_BASH", "bash"), (ROOT / "bindings/java/build.sh").as_posix(), "gson.jar", "pkg"], folder)
        (folder / "Movie.java").write_text(code)
        cp = os.pathsep.join([str(next((folder / "pkg").glob("*.jar"))), str(gson), "."])
        run(["javac", "-cp", cp, "Movie.java"], folder)
        output = run(["java", "-cp", cp, "Movie"], folder)
    elif key == "csharp":
        settings = {"NUGET_PACKAGES": str(folder / "cache")}
        run(["dotnet", "pack", ROOT / "bindings/csharp/NativeLang.Classify.csproj", "-o", "pkg"], folder, **settings)
        run(["dotnet", "new", "console", "--no-restore"], folder, **settings)
        (folder / "Program.cs").write_text(code)
        run(["dotnet", "add", "package", "NativeLang.Classify", "--source", str(folder / "pkg")], folder, **settings)
        output = run(["dotnet", "run", "--no-restore"], folder, **settings)
    else:
        raise ValueError(key)
    assert output.splitlines()[-1] == "negative", (key, output)

def main():
    source = Path(sys.argv[1]).resolve()
    languages = sys.argv[2:]
    host = {"Darwin": "darwin", "Linux": "linux", "Windows": "windows"}[platform.system()]
    arch = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "amd64"
    pins = json.loads((ROOT / "app/pack/service-hashes.json").read_text())
    dest = Path.home() / ".nativelang/classify/bin"
    dest.mkdir(parents=True, exist_ok=True)
    cli = dest / ("classify.exe" if WINDOWS else "classify")
    # CI tests the PR before a release URL exists. Only the helper download is preseeded.
    if cli.exists():
        raise RuntimeError("Binding integration tests require a clean CI account")
    shutil.copy2(source, cli)
    (dest / "service.version").write_text(pins[f"{host}-{arch}"])
    try:
        with tempfile.TemporaryDirectory() as tmp:
            first = None
            for index, language in enumerate(languages, 1):
                folder = Path(tmp) / language
                folder.mkdir()
                example(language, folder)
                state = json.loads(run([cli, "service", "status"], folder))
                first = first or state["instance"]
                assert state["instance"] == first and state["requests"] == index, state
                print(language, "reused service PID", state["pid"], flush=True)
    finally:
        run([cli, "service", "stop"], dest)

if __name__ == "__main__":
    main()
