#!/bin/sh
# Install the server and model together in ./classify-server.
set -eu

fail() { printf '%s\n' "$1" >&2; exit 1; }
if [ -e classify-server ] || [ -L classify-server ]; then
    fail "classify-server already exists. To install a new copy, choose an empty folder."
fi

model=compact-r3
case "$(uname -s)/$(uname -m)" in
    Darwin/arm64)
        target=aarch64-apple-darwin
        sha=64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3 ;;
    Darwin/x86_64)
        model=standard-r1
        target=x86_64-apple-darwin
        sha=998aee9d4eb1d895222185243a0e0c6e9381c1b99f22dee74baf67dccc40d95c ;;
    Linux/aarch64|Linux/arm64)
        target=aarch64-unknown-linux-gnu
        sha=fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877 ;;
    Linux/x86_64)
        target=x86_64-unknown-linux-gnu
        sha=211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28 ;;
    *) fail "No Classify server download for $(uname -s) $(uname -m)." ;;
esac

work=$(mktemp -d ./.classify-install.XXXXXXXX)
trap 'rm -rf "$work"' EXIT
trap 'exit 1' HUP INT TERM

name="classify-server-0.1.0-dm-classify-${model}-${target}.tar.gz"
url="https://github.com/nativelang/classify-artifacts/releases/download/v0.1.0-dm-classify-${model}"
archive="$work/server.tar.gz"
if [ "$model" = standard-r1 ]; then
    for part in 0001 0002; do
        curl -q -fL "$url-manual/$name.part-$part-of-0002" >> "$archive"
    done
else
    curl -q -fL "$url/$name" -o "$archive"
fi

if [ "$(uname -s)" = Darwin ]; then
    actual=$(shasum -a 256 "$archive")
else
    actual=$(sha256sum "$archive")
fi
[ "${actual%% *}" = "$sha" ] || fail "Download did not match its checksum. Run the installer again."
mkdir "$work/classify-server"
tar -xzf "$archive" -C "$work/classify-server"
[ -x "$work/classify-server/classify" ] || fail "The archive is missing the server."
mv "$work/classify-server" .
printf '%s\n' 'Installed. Start the server with ./classify-server/classify serve'
