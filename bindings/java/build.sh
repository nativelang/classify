#!/bin/sh
# Run with JDK 21+ on PATH and the pinned Gson JAR as the first argument.
set -eu
if [ "$#" -ne 2 ]; then
    echo 'Usage: build.sh GSON_JAR OUTPUT_DIRECTORY' >&2
    exit 2
fi
gson=$1
out=$2
root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
if command -v sha256sum >/dev/null 2>&1; then
    hash=$(sha256sum < "$gson")
else
    hash=$(shasum -a 256 < "$gson")
fi
if [ "${hash%% *}" != 96d3dd843dc2911de01cdabcd50064cb9e860353102a0a78c96fd833d396fc7d ]; then
    echo 'Unexpected Gson JAR checksum' >&2
    exit 1
fi
classes=$(mktemp -d)
trap 'rm -rf "$classes"' EXIT
mkdir -p "$out"
javac --release 21 -classpath "$gson" -d "$classes" \
    "$root/bindings/java/src/io/nativelang/classify/Classifier.java"
cp "$root/app/bootstrap.sh" "$classes/io/nativelang/classify/bootstrap.sh"
jar --create --date=2020-01-01T00:00:00Z --file "$out/classify-0.2.2.jar" \
    -C "$classes" . -C "$root" LICENSE
