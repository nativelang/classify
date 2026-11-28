"""Build independent, persistent benchmark clients against public release packages."""
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CLIENTS = Path(__file__).parent / "clients"
LANGUAGES = ("python", "javascript", "typescript", "go", "rust", "java", "csharp", "c")
EXE = ".exe" if os.name == "nt" else ""


def client(language, version, release, work, install):
    folder = work / language
    folder.mkdir()
    def run(*args):
        subprocess.run(args, cwd=folder, check=True)

    def source(name, dest=None):
        path = folder / (dest or name)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CLIENTS / name, path)
        return path

    if language == "python":
        run(sys.executable, "-m", "venv", "venv")
        python = folder / ("venv/Scripts/python.exe" if EXE else "venv/bin/python")
        run(python, "-m", "pip", "install", f"nativelang-classify=={version}")
        return [python, "-u", source("movie.py")]
    if language in ("javascript", "typescript"):
        run(shutil.which("npm"), "install", "--no-audit", "--no-fund", f"@nativelang/classify@{version}")
        return ["node", source("movie.mjs", "movie.mts" if language == "typescript" else "movie.mjs")]
    if language == "go":
        source("main.go")
        run("go", "mod", "init", "movie")
        run("go", "get", f"github.com/nativelang/classify/bindings/go@v{version}")
        run("go", "build", "-o", "movie" + EXE, ".")
        return [folder / ("movie" + EXE)]
    if language == "rust":
        run("cargo", "init", "--bin", "--name", "movie", "--vcs", "none")
        source("main.rs", "src/main.rs")
        run("cargo", "add", f"nativelang-classify@={version}")
        run("cargo", "build", "--release", "--locked")
        return [folder / "target/release" / ("movie" + EXE)]
    if language == "java":
        pom = ET.parse(release / "bindings/java/central.pom")
        gson = next(d.findtext("{*}version") for d in pom.findall(".//{*}dependency")
                    if d.findtext("{*}artifactId") == "gson")
        central = "https://repo.maven.apache.org/maven2"
        for artifact, name in [(f"io/github/nativelang/classify/{version}/classify-{version}", "classify"),
                               (f"com/google/code/gson/gson/{gson}/gson-{gson}", "gson")]:
            run("curl", "-fsSL", "--retry", "3", f"{central}/{artifact}.jar", "-o", name + ".jar")
        cp = os.pathsep.join(map(str, [folder, folder / "classify.jar", folder / "gson.jar"]))
        run("javac", "-cp", cp, source("Movie.java"))
        return ["java", "-cp", cp, "Movie"]
    if language == "csharp":
        source("Program.cs")
        project = ET.parse(release / "examples/csharp/Movie.csproj")
        package = project.find(".//PackageReference[@Include='NativeLang.Classify']")
        if package is None:
            raise ValueError("The C# example no longer references NativeLang.Classify")
        package.set("Version", f"[{version}]")
        project.write(folder / "Movie.csproj", encoding="utf-8")
        run("dotnet", "publish", "Movie.csproj", "-c", "Release", "-o", "out",
            "-p:NuGetAudit=false")
        return ["dotnet", folder / "out/Movie.dll"]
    if language != "c":
        raise ValueError(language)
    sdk = work / "sdk"
    src = source("movie.c")
    binary = folder / ("movie" + EXE)
    if EXE:
        run("cl", "/nologo", "/O2", "/std:c11", "/I" + str(sdk / "include"), src,
            sdk / "lib/classify_core.lib", "/Fe:" + str(binary))
        for dll in (sdk / "bin").glob("*.dll"):
            shutil.copy2(dll, folder)
    else:
        run("cc", "-O2", "-std=c11", "-I", sdk / "include", src, "-L", sdk / "lib",
            "-lclassify_core", f"-Wl,-rpath,{sdk / 'lib'}", "-o", binary)
    return [binary, install / "model/profile.json"]
