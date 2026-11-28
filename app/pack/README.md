# Build the managed service release

From the repository root, run `python3 app/pack/build.py dist` to cross-build the six archives and verify the pins used by the language packages. The helper uses the Go standard library, targets x64 and ARM64 on macOS, Linux and Windows, and has no external Go module dependencies.

For a new service version, update the release tag in the two launcher templates, run the build with `--write-pins`, then run `python3 app/sync_releases.py`. Attach the verified archives to the tagged source release. Each archive includes the executable and license notices for the Classify source and Go toolchain. The native model and runtime retain the provenance, checksums and notices in [Releases](../../RELEASES.md).
