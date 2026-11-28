if [ "${NATIVELANG_CLASSIFY_SERVICE:-}" = 1 ]; then
    case "$(uname -s)/$(uname -m)" in
@UNIX_TARGETS@
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
