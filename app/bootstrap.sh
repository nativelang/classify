#!/bin/sh
# Start the published local CLI. Requests and responses are JSON Lines.
set -eu

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
exec "$install/classify" infer --profile "$install/model/profile.json"
