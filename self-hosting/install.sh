#!/bin/sh
# Install the server and model together in ./classify-server.
set -eu

fail() { printf '%s\n' "$1" >&2; exit 1; }
if [ -e classify-server ] || [ -L classify-server ]; then
    fail "classify-server already exists. To install a new copy, choose an empty folder."
fi

platform="$(uname -s)/$(uname -m)"
[ "$platform" != Linux/arm64 ] || platform=Linux/aarch64
while IFS=, read -r host target version model parts sha; do
    [ "$host" != "$platform" ] || break
done <<'CLASSIFY_RELEASES'
platform,target,version,model,parts,sha256
Darwin/arm64,aarch64-apple-darwin,0.1.0,compact-r3,1,64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3
Darwin/x86_64,x86_64-apple-darwin,0.1.0,standard-r1,2,998aee9d4eb1d895222185243a0e0c6e9381c1b99f22dee74baf67dccc40d95c
Linux/aarch64,aarch64-unknown-linux-gnu,0.1.0,compact-r3,1,fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877
Linux/x86_64,x86_64-unknown-linux-gnu,0.1.0,compact-r3,1,211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28
Windows/ARM64,aarch64-pc-windows-msvc,0.1.0,standard-r1,2,7463ae150d1aa12fa2ce0f6b2c1a9c8723b56de862d1fe87180684648bd63030
Windows/AMD64,x86_64-pc-windows-msvc,0.1.0,standard-r1,2,fa7fddf19ed3ee54294d9c791a0a9f8009954cdd7dee2b00532731d524bcea0b
CLASSIFY_RELEASES
[ "$host" = "$platform" ] || { echo "No Classify download for $platform." >&2; exit 1; }
model="dm-classify-$model"
tag="v$version-$model"

work=$(mktemp -d ./.classify-install.XXXXXXXX)
trap 'rm -rf "$work"' EXIT
trap 'exit 1' HUP INT TERM

archive="$work/server.tar.gz"
name="classify-server-$version-$model-$target.tar.gz"
url="https://github.com/nativelang/classify-artifacts/releases/download/$tag"
download() {
    curl -q --fail --location --silent --show-error --proto '=https' --proto-redir '=https' --output "$1" "$2"
}
if [ "$parts" = 1 ]; then
    download "$archive" "$url/$name"
else
    i=1
    while [ "$i" -le "$parts" ]; do
        suffix=$(printf 'part-%04d-of-%04d' "$i" "$parts")
        download - "$url-manual/$name.$suffix" >> "$archive"
        i=$((i + 1))
    done
fi

verify() {
    if [ "$(uname -s)" = Darwin ]; then
        actual=$(shasum -a 256 "$1")
    else
        actual=$(sha256sum "$1")
    fi
    [ "${actual%% *}" = "$2" ] || fail "Download did not match its checksum. Run the installer again."
}
verify "$archive" "$sha"
mkdir "$work/classify-server"
tar -xzf "$archive" -C "$work/classify-server"
[ -x "$work/classify-server/classify" ] || fail "The archive is missing the server."
curl -q -fL https://raw.githubusercontent.com/nativelang/classify/90bbb5b0921ae8f013af100e08a100cf0dcdf45b/self-hosting/start -o "$work/classify-server/start"
verify "$work/classify-server/start" 4a664420a21529ff201f5c036199920a466dd3bd4be5d8078bfc4554ea946ff9
chmod +x "$work/classify-server/start"
mv -n "$work/classify-server" .
[ ! -d "$work/classify-server" ] || fail "classify-server already exists. The existing folder was kept."
printf '%s\n' 'Installed. Start the server with ./classify-server/start'
