"""Select one measured runner and language for the paired evaluation."""
import csv
import json
import math
import os
import sys
from pathlib import Path

from build import LANGUAGES

RUNNERS = {
    "ubuntu-24.04": "Linux/x86_64", "ubuntu-24.04-arm": "Linux/aarch64",
    "macos-15": "Darwin/arm64", "macos-15-intel": "Darwin/x86_64",
    "windows-2022": "Windows/AMD64", "windows-11-arm": "Windows/ARM64",
}
MODELS = ("compact", "standard")


def select(directory, version, csv_path):
    rows = {}
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["runner", "language", "model", "native_load_ms", "first_call_ms",
                         "median_ms", "p95_ms", "calls_per_second"])
        for path in sorted(directory.rglob("bench-*.json")):
            data = json.loads(path.read_text())
            runner, model = data["runner"], data["model"]
            if (data["version"] != version or data["errors"] or set(data["clients"]) != set(LANGUAGES)
                    or RUNNERS.get(runner) != data["platform"] or model not in MODELS):
                raise ValueError(f"Incomplete or unexpected result in {path}")
            for lang, metrics in data["clients"].items():
                key = (runner, lang, model)
                speed = metrics["calls_per_second"]
                if key in rows or not math.isfinite(speed) or speed <= 0:
                    raise ValueError(f"Invalid result for {key}")
                rows[key] = 1000 / speed
                writer.writerow([runner, lang, model, data["native_load_ms"], metrics["first_call_ms"],
                                 metrics["median_ms"], metrics["p95_ms"], speed])
    # Equal-sized evaluations on both models: minimize combined warm time per pair.
    expected = {(runner, lang, model) for runner in RUNNERS for lang in LANGUAGES for model in MODELS}
    missing = expected - rows.keys()
    if missing:
        raise ValueError(f"Missing benchmark measurements: {sorted(missing)}")
    ranked = sorted((sum(rows[runner, lang, model] for model in MODELS), runner, lang)
                    for runner in RUNNERS for lang in LANGUAGES)
    return ranked[0]


if __name__ == "__main__":
    cost, runner, lang = select(Path(sys.argv[1]), sys.argv[2], Path("performance.csv"))
    print(f"Fastest measured combination: {runner}, {lang} ({cost:.2f} ms per pair)")
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"runner={runner}\nlanguage={lang}", file=f)
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
        print(f"Fastest measured combination for both models: **{runner} / {lang}** "
              f"({cost:.2f} ms per pair of warm calls). See `performance.csv` for the full matrix.", file=f)
