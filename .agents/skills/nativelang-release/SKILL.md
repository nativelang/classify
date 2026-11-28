---
name: nativelang-release
description: Publish or verify the NativeLang Classify service and its six official language packages from GitHub Actions. Use for Classify release requests, retrying registry jobs, or setting up release access on another computer.
---

# Release NativeLang Classify

## Another laptop

Install the GitHub CLI and sign in once with an account that can run workflows in `nativelang/classify`. Confirm access with `gh repo view nativelang/classify`. The package credentials and Maven signing key live in GitHub. A checkout includes this skill under `.agents/skills/`.

## Publish

Get the requested version from the release owner. Check that its package versions, Java build hashes and service archive pins are in the reviewed commit on main. When changing the service executable, assign a new service tag, rebuild all six archives with `app/pack/build.py`, update the launcher pins and run `python3 app/sync_releases.py`. Check the macOS, Windows and Linux lifecycle jobs before publishing.

Dispatch the workflow on main using the approved version.

```sh
gh workflow run publish-packages.yml --repo nativelang/classify --ref main -f version=0.3.0
gh run list --repo nativelang/classify --workflow publish-packages.yml --limit 5
gh run watch RUN_ID --repo nativelang/classify --exit-status
```

The preparation job publishes six service archives, the versioned language assets with SHA-256 checksums and the nested Go module tag. The registry jobs publish to npm, crates.io, NuGet, Maven Central and PyPI. The final job downloads from each public registry and the Go module proxy. Report the version and link to the successful run.

If a job fails, read its log with `gh run view RUN_ID --repo nativelang/classify --log-failed`. For an interrupted Maven upload, check the deployment ID in the job log before retrying. For a transient failure, rerun the failed jobs with `gh run rerun RUN_ID --failed --repo nativelang/classify`. Keep already-published versions immutable.

## Restore repository publishing configuration

The GitHub environments accept only the `main` branch. Normal publishing runs without manual approval. Check environment rules and secret names using `gh api repos/nativelang/classify/environments` and `gh secret list --repo nativelang/classify --env registry-release`.

| Publisher | One-time configuration |
| --- | --- |
| PyPI | Project `nativelang-classify`, GitHub repository `nativelang/classify`, workflow `publish-python.yml`, environment `pypi`. |
| npm | Package `@nativelang/classify`, GitHub repository `nativelang/classify`, workflow `publish-packages.yml`, environment `registry-release`, permission to publish. |
| crates.io | Crate `nativelang-classify`, same repository, workflow `publish-packages.yml`, environment `registry-release`. |
| NuGet | Policy owned by `NativeLang` for new versions of `NativeLang.Classify`; same repository, workflow `publish-packages.yml`, environment `registry-release`. The NuGet login action takes the policy creator’s individual username, `sdasan`. |
| Maven Central | Namespace `io.github.nativelang`. Store the base64-encoded portal token username and password pair in `CENTRAL_PORTAL_TOKEN`. The registry-release environment holds the armored dedicated CI signing key in `CENTRAL_SIGNING_KEY` and its passphrase in `CENTRAL_SIGNING_PASSPHRASE`. The public key is in `release/ci-signing-key.asc`. |
| Go | Push the `bindings/go/vVERSION` tag at the language release commit with the workflow's repository token. The module is served through the public Go proxy. |

Rotate Maven credentials only with owner authorization. For a replacement signing key, publish the public certificate to a Maven Central supported keyserver, verify its full fingerprint, update the tracked public certificate by PR and set the protected secrets through stdin. Keep a revocation certificate with the release owner. For registry account recovery, use one existing signed-in browser window.
