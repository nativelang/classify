# Platforms

| OS | Processors | Runtime |
| --- | --- | --- |
| macOS 15 or later | Apple Silicon, Intel x64 | Compact selects Metal on supported Apple Silicon GPUs and can fall back to CPU. Intel uses CPU. |
| Debian 12-compatible Linux | ARM64, x64 | Compact selects compatible CPU instructions at startup, including AVX2 on supported x64 processors. |
| Windows | ARM64, x64 | Native CPU runtime. If a runtime DLL is missing, install the Microsoft Visual C++ v14 Redistributable for the app’s architecture. |

Python requires 3.9 or later. JavaScript and TypeScript require Node.js 22.18 or later. A minimal Linux installation needs compatible glibc and libstdc++, plus `curl`, `tar`, `sha256sum`, and `flock` for the first download.

## Model downloads

The standalone installer and the 0.3.0 bindings use Compact (about 1.6 GB). The first call verifies and caches the download under `~/.nativelang/classify/`. Projects under the same account reuse it offline.

Python and Node.js 0.2.3 use Compact on all six targets. Java, C#, Go and Rust 0.2.2 use Standard (about 2.5 GB) on Intel Macs and require the [standalone HTTP server](../self-hosting/README.md) on Windows.

For individual SDKs, accelerated builds, licenses and checksums, see [releases and downloads](../RELEASES.md).
