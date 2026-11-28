# Qualify a major Classify release

After publishing a stable major version, open **Actions → Qualify a major release → Run workflow** on `main` and enter the package version, for example `1.0.0`. To start the same run from a terminal, use the release version you published.

```sh
gh workflow run major-release.yml --repo nativelang/classify --ref main -f version=1.0.0
```

This is a manual release check. It accepts published `X.0.0` versions with X ≥ 1. The first job resolves the release tag to a commit before starting the hardware jobs. The workflow uses read-only repository permissions.

## What runs

Each of the six supported OS and processor combinations gets a fresh GitHub-hosted runner for Compact and another for Standard. The matrix covers Apple Silicon and Intel macOS 15, Ubuntu 24.04 on ARM64 and x64, Windows 11 ARM64 and Windows Server 2022 x64. Each job builds clients in Python, JavaScript, TypeScript, Java, C#, Go, Rust and native C. The six language packages come from their public registries at the requested version. The C client links the verified SDK for its model and processor. JavaScript and TypeScript share the Node binding.

Each benchmark uses the default hardware selection of the portable release on that runner. The harness checks each client’s reported processor architecture. The JSON records the CPU, OS, model profile, release commit, and artifact hashes. The native logs record backend selection when the runtime reports it. Results describe the hardware GitHub supplied for that run.

The packages automatically select Compact. For this test the harness downloads the selected server archive, checks its SHA-256, verifies the model profile ID and stages it in an empty per-job home folder. This exercises Standard through the same public binding calls. The benchmark uses a fresh worker process for each client. The regular PR workflows exercise first-install and shared-service behavior.

## Read the results

Open the run summary for the fastest measured runner and language and the two model scores. Download **performance** for the CSV with all 96 combinations. The per-runner **bench-** artifacts and the **evaluation** artifact contain JSON and runtime logs, including partial results when a client fails.

- **Download and setup** measures fetching, verifying and extracting the SDK and model archive once in that job.
- **Native load** measures elapsed time from starting a fresh native worker to receiving its first readiness response with the model loaded.
- **First call** measures the first movie request through the client, including starting its worker, opening the model and producing the answer. Dependency installation and client compilation finish before timing begins. The OS file cache may already be warm.
- **Warm performance** measures 12 sequential calls across four fixed requests in the same client process. Each records wall-clock round-trip latency. The CSV includes median, p95 and calls per second. Each client must return `negative` for the first movie review, and preserve it when the categories are reversed. The suite also tests one category, the 16-category limit, and an out-of-domain request. All eight clients must agree on the results for that model and host.

The selector requires the entire matrix to pass. For each runner/language pair it adds the mean warm latency on Compact to the mean on Standard. The lowest total wins because the evaluation sends the same number of requests to each model. Both evaluations run sequentially on one fresh instance of that runner type using the winning language.

The [public evaluation set](eval.json) contains 36 labelled requests across six tasks, including cases where the expected answer is empty. Each model gets the same cases in the same order. The summary shows exact-match accuracy and abstentions. The JSON retains every prediction and latency for comparison across releases. Accuracy is reported without a release-blocking threshold.

Run the harness checks locally with Python 3.11 or later:

```sh
python3 -m unittest discover -s release/qualification
```

When changing model releases, update the SDK manifest and Standard archive-index pins in [models.py](models.py) alongside the model pins in [the release table](../../app/releases.csv).
