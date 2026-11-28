#!/bin/sh
# Start the published local CLI. Requests and responses are JSON Lines.
set -eu
if [ "${NATIVELANG_CLASSIFY_SERVICE:-}" = 1 ]; then
    case "$(uname -s)/$(uname -m)" in
        Darwin/arm64) target=darwin-arm64; sha=b1519efc9e4f29bb5596d610b56df22397187e81ed024ec46cc59e66b9f91a7e ;;
        Darwin/x86_64) target=darwin-amd64; sha=410b4aaa1a0028182305c3d400c03493f8eff486a57bd4be2ae5f2fe1cf3c264 ;;
        Linux/aarch64|Linux/arm64) target=linux-arm64; sha=5e9511157280cba16a60dc34353338f95403d55d208610c894dbca72b56c4161 ;;
        Linux/x86_64) target=linux-amd64; sha=441f5fdca5564c62a889af7da7d81001c88ae0a65693ff8125c24590ca270dd4 ;;
        *) echo 'Unsupported Classify service platform' >&2; exit 1 ;;
    esac
    umask 077
    bin="${HOME:?}/.nativelang/classify/bin"
    cli="$bin/classify"
    mkdir -p "$bin"
    # The executable is replaced atomically. Concurrent installs verify the same bytes.
    if [ ! -x "$cli" ] || [ "$(cat "$bin/service.version" 2>/dev/null)" != "$sha" ]; then
        tmp=$(mktemp -d "$bin/.install.XXXXXXXX")
        trap 'rm -rf "$tmp"' EXIT
        curl -q -fsSL --proto '=https' --proto-redir '=https' --retry 2 -o "$tmp/sdk.tgz" \
          "https://github.com/nativelang/classify/releases/download/service-v1.0.0/classify-service-$target.tar.gz"
        case "$target" in darwin-*) digest="shasum -a 256" ;; *) digest=sha256sum ;; esac
        (cd "$tmp" && printf '%s  sdk.tgz\n' "$sha" | $digest -c - >&2)
        tar -xzf "$tmp/sdk.tgz" -C "$tmp"
        chmod 700 "$tmp/classify"
        mv "$tmp/LICENSE.txt" "$bin/service-LICENSE.txt"
        mv "$tmp/classify" "$cli"
        printf '%s\n' "$sha" > "$tmp/version"
        mv "$tmp/version" "$bin/service.version"
        rm -rf "$tmp"
        trap - EXIT
    fi
    exec "$cli" infer
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

root="${HOME:?Set HOME to your home directory}/.nativelang/classify/$tag"
install="$root/$target"
ready() {
    [ -x "$install/classify" ] && [ -f "$install/model/profile.json" ] && [ -f "$install/model/model.gguf" ]
}

if ! ready; then (
    umask 077
    mkdir -p "$root"
    # A kernel lock survives waiting installers and releases on process exit.
    # Close it at the end of this subshell, before running inference.
    exec 9>>"$root/.$target.lock"
    case "$target" in
        *-darwin) lockf 9 ;;
        *) flock -x 9 ;;
    esac
    if ready; then exit 0; fi
    if [ -e "$install" ] || [ -L "$install" ]; then
        echo "Incomplete Classify installation at $install; move it aside and try again." >&2
        exit 1
    fi

    stage="$root/.$target.partial"
    rm -rf "$stage"
    mkdir -p "$stage/unpacked"
    trap 'rm -rf "$stage"' EXIT
    archive="$stage/package.tar.gz"
    echo "Downloading $model for $target..." >&2
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
    echo 'Verifying Classify download...' >&2
    (
        cd "$stage"
        case "$target" in
            *-darwin) set -- shasum -a 256 ;;
            *) set -- sha256sum ;;
        esac
        printf '%s  package.tar.gz\n' "$sha" | "$@" -c - >&2
    )
    echo 'Unpacking Classify...' >&2
    tar -xzf "$stage/package.tar.gz" -C "$stage/unpacked"
    test -x "$stage/unpacked/classify"
    test -f "$stage/unpacked/model/profile.json"
    test -f "$stage/unpacked/model/model.gguf"
    mv "$stage/unpacked" "$install"
); fi
if [ "${1:-}" = --locate ]; then printf '%s\n' "$install/classify"; exit 0; fi
exec "$install/classify" infer --profile "$install/model/profile.json"
