#!/bin/sh
# Start the published Compact r3 CLI. Requests and responses are JSON Lines.
set -eu

version=0.1.0
model=dm-classify-compact-r3
tag="v$version-$model"
case "$(uname -s)/$(uname -m)" in
    Darwin/arm64)
        target=aarch64-apple-darwin
        sha=64d0972c97a87128d4698aa2940b724f321094e476b41b18531aa93426395dd3
        ;;
    Linux/x86_64)
        target=x86_64-unknown-linux-gnu
        sha=211b8fdb1637709e8ecb1a3c5d2be9de9b6c624cca18c8a6df93029477dc6d28
        ;;
    Linux/aarch64|Linux/arm64)
        target=aarch64-unknown-linux-gnu
        sha=fe432526cb458c4df37603917e8c4e321c340e30b631b3f2571332998c674877
        ;;
    *)
        echo 'The local Classify app supports Apple Silicon macOS and ARM64 or x64 Linux.' >&2
        exit 1
        ;;
esac

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
    archive="classify-server-$version-$model-$target.tar.gz"
    url="https://github.com/nativelang/classify-artifacts/releases/download/$tag/$archive"
    echo "Downloading $model for $target (about 1.6 GB)..." >&2
    curl -q --fail --location --silent --show-error --proto '=https' --proto-redir '=https' \
        --output "$stage/package.tar.gz" "$url"
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
