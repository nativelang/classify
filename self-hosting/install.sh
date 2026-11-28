#!/bin/sh
# Install the server and model together in ./classify-server.
set -eu

fail() { printf '%s\n' "$1" >&2; exit 1; }
if [ -e classify-server ] || [ -L classify-server ]; then
    fail "classify-server already exists. To install a new copy, choose an empty folder."
fi

platform="$(uname -s)/$(uname -m)"
[ "$platform" != Linux/arm64 ] || platform=Linux/aarch64
while IFS=, read -r host target version model tag parts sha; do
    [ "$host" != "$platform" ] || break
done <<'CLASSIFY_RELEASES'
platform,target,version,model,tag,parts,sha256
Darwin/arm64,aarch64-apple-darwin,0.1.1,compact-r3,v0.1.1-dm-classify-compact-r3,1,666b9583ff4794f1537af8b6d2b60e98c383ebb87892b990066c68a1c02d219b
Darwin/x86_64,x86_64-apple-darwin,0.1.0,compact-r3,v0.1.0-dm-classify-compact-r3-desktop,1,64f13c257f242d79348f75f8d5621ffb8a938d7ea4d88000a5dcf71ed0709988
Linux/aarch64,aarch64-unknown-linux-gnu,0.1.1,compact-r3,v0.1.1-dm-classify-compact-r3,1,2daf0fde2c1a663c31e9913b0563070087d6bc8e3a02e2bb3cd0bf3295c9894a
Linux/x86_64,x86_64-unknown-linux-gnu,0.1.1,compact-r3,v0.1.1-dm-classify-compact-r3,1,f245e326547df8a090ea6a2d551c0658409346451f764528b6f837dd391d74c5
Windows/ARM64,aarch64-pc-windows-msvc,0.1.0,compact-r3,v0.1.0-dm-classify-compact-r3-desktop,1,b5ef5a9dbccef6f4a69de7bb1248f6f3cb6a1fe6ffb4b20c02b41254b24aa7a5
Windows/AMD64,x86_64-pc-windows-msvc,0.1.0,compact-r3,v0.1.0-dm-classify-compact-r3-desktop,1,683798bee161c422bd97391bd8ed194f3922314609a703d0f3a048ea94dd99cb
CLASSIFY_RELEASES
[ "$host" = "$platform" ] || { echo "No Classify download for $platform." >&2; exit 1; }
model="dm-classify-$model"

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
