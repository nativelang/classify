"""Assemble a signed Maven Central bundle of Classify's v0.2.0 Java release."""

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gson", type=Path, help="Gson 2.15.0 JAR")
    parser.add_argument("fingerprint", help="full fingerprint of the release signing key")
    parser.add_argument("output", type=Path, help="new output ZIP")
    args = parser.parse_args()
    if not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", args.fingerprint):
        parser.error("supply a full signing key fingerprint")
    if args.output.exists():
        parser.error("output already exists")

    java = Path(__file__).resolve().parent
    root = java.parent.parent
    gson = args.gson.resolve()
    package = Path("io/nativelang/classify")
    artifact = "classify-0.2.0"
    prefix = "io/github/nativelang/classify/0.2.0"

    with tempfile.TemporaryDirectory(dir=args.output.resolve().parent) as tmp:
        work = Path(tmp)
        files = work / "artifacts"
        subprocess.run(["sh", java / "build.sh", gson, files], check=True)
        binary = files / f"{artifact}.jar"
        if hashlib.sha256(binary.read_bytes()).hexdigest() != (
            "f8f4afe48dda1350743b536a89935252c3d959308390b033e07c47f75adbd1f8"
        ):
            raise SystemExit("Binary differs from the v0.2.0 release. Use the documented JDK and source.")

        date = "--date=2020-01-01T00:00:00Z"
        sources = work / "sources"
        (sources / package).mkdir(parents=True)
        shutil.copyfile(java / "src" / package / "Classifier.java", sources / package / "Classifier.java")
        shutil.copyfile(root / "app/bootstrap.sh", sources / package / "bootstrap.sh")
        docs = work / "docs"
        subprocess.run(["javadoc", "-quiet", "-notimestamp", "--release", "21",
                        "-classpath", gson, "-d", docs, sources / package / "Classifier.java"], check=True)
        for folder, classifier in [(sources, "sources"), (docs, "javadoc")]:
            shutil.copyfile(root / "LICENSE", folder / "LICENSE")
            subprocess.run(["jar", "--create", date, "--file", files / f"{artifact}-{classifier}.jar",
                            "-C", folder, "."], check=True)
        shutil.copyfile(java / "central.pom", files / f"{artifact}.pom")

        for path in sorted(files.iterdir()):
            subprocess.run(["gpg", "--armor", "--local-user", args.fingerprint,
                            "--detach-sign", path], check=True)
            data = path.read_bytes()
            for algorithm in ("md5", "sha1", "sha256", "sha512"):
                checksum = hashlib.new(algorithm, data).hexdigest()
                Path(f"{path}.{algorithm}").write_text(checksum, encoding="ascii")

        bundle = work / "bundle.zip"
        with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
            for path in sorted(files.iterdir()):
                archive.write(path, f"{prefix}/{path.name}")
        # Expose the complete bundle without replacing an existing file.
        args.output.hardlink_to(bundle)


if __name__ == "__main__":
    main()
