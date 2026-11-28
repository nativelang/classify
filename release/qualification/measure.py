"""Measure public binding calls in a fresh process and score labelled eval cases."""
import argparse
import hashlib
import json
import math
import os
import platform
import queue
import statistics
import subprocess
import tempfile
import threading
import time
import traceback
from contextlib import contextmanager
from pathlib import Path

from build import LANGUAGES, client
from models import platform_key, stage

EVAL = Path(__file__).with_name("eval.json")
MOVIE = ("This is a terrible movie", ["positive", "negative", "neutral"])
WARM = [MOVIE, ("This is an excellent film.", MOVIE[1]),
        ("My invoice has the wrong amount.", ["billing", "delivery", "account"]),
        ("Please ship my order tomorrow.", ["billing", "delivery", "account"])] * 3


@contextmanager
def worker(command, env, log):
    # One reader thread permits a per-response timeout on Windows as well as Unix.
    with log.open("w", encoding="utf-8") as errors, subprocess.Popen(
        command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
        text=True, encoding="utf-8", bufsize=1
    ) as proc:
        lines = queue.Queue()
        def read():
            try:
                for line in proc.stdout:
                    lines.put(line.rstrip("\r\n"))
            finally:
                lines.put(None)
        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        def receive():
            try:
                value = lines.get(timeout=180)
            except queue.Empty as exc:
                raise TimeoutError(f"Timed out waiting for {command[0]}") from exc
            if value is None:
                raise RuntimeError(f"Unexpected EOF from {command[0]}. See {log.name}")
            return value
        try:
            yield proc.stdin, receive
            proc.stdin.close()
            if proc.wait(timeout=15):
                raise RuntimeError(f"{command[0]} exited with {proc.returncode}")
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            proc.stdout.close()
            reader.join(timeout=2)


def milliseconds(start):
    return (time.perf_counter_ns() - start) / 1_000_000


def native_load(install, env, log):
    exe = "classify.exe" if os.name == "nt" else "classify"
    start = time.perf_counter_ns()
    with worker([install / exe, "infer", "--profile", install / "model/profile.json"], env, log) as (pipe, recv):
        # As in app/model.go, the native worker loads the model before it reads stdin.
        pipe.write("{}\n")
        pipe.flush()
        reply = json.loads(recv())
        elapsed = milliseconds(start)
        if reply.get("error", {}).get("code") != "invalid_argument":
            raise RuntimeError(f"Unexpected readiness response: {reply}")
    return elapsed


def measure(language, command, env, log, evaluation):
    with worker(command, env, log) as (pipe, recv):
        arch = recv().lower()
        native = platform.machine().lower()
        aliases = ({"amd64", "x86_64", "x64"}, {"arm64", "aarch64"})
        if not any(arch in group and native in group for group in aliases):
            raise RuntimeError(f"Expected a native {native} client, received {arch!r}")
        def classify(text, categories):
            if language == "c":
                line = json.dumps({"text": text, "categories": categories})
            else:
                if any(any(c in field for c in "\t\r\n") for field in [text, *categories]):
                    raise ValueError("Unsupported delimiter in test input")
                line = "\t".join([text, *categories])
            start = time.perf_counter_ns()
            pipe.write(line + "\n")
            pipe.flush()
            reply = recv()
            duration = milliseconds(start)
            label = json.loads(reply)["category"] if language == "c" else (reply or None)
            if label is not None and label not in categories:
                raise ValueError(f"Unexpected category {label!r}")
            return label, duration

        first, latency = classify(*MOVIE)
        if first != "negative":
            raise ValueError(f"Expected negative on first call, received {first!r}")
        if evaluation:
            predictions = []
            for group in json.loads(EVAL.read_bytes()):
                for text, expected in group["cases"]:
                    label, elapsed = classify(text, group["categories"])
                    predictions.append(dict(text=text, categories=group["categories"], expected=expected,
                                            predicted=label, latency_ms=elapsed))
            correct = sum(p["expected"] == p["predicted"] for p in predictions)
            return dict(client_arch=arch, cases=len(predictions), correct=correct, accuracy=correct / len(predictions),
                        abstained=sum(p["predicted"] is None for p in predictions),
                        eval_sha256=hashlib.sha256(EVAL.read_bytes()).hexdigest(), predictions=predictions)
        observed = [classify(text, cats) for text, cats in WARM]
        labels = [label for label, _ in observed]
        samples = [elapsed for _, elapsed in observed]
        reversed_movie = classify(MOVIE[0], list(reversed(MOVIE[1])))[0]
        if reversed_movie != first:
            raise ValueError("Reordering the movie categories changed the answer")
        functional = {
            "reversed_categories": reversed_movie,
            "single_category": classify("My parcel has not arrived.", ["delivery"])[0],
            "full_menu": classify("Could you refund this charge?",
                                  ["refund", "delivery", "exchange", "technical support", "sales", "warranty",
                                   "account", "security", "feedback", "appointment", "inventory", "directions",
                                   "pricing", "membership", "hours", "other"])[0],
            "out_of_domain": classify("I need a new pair of glasses.", ["train", "airplane"])[0],
        }
        return dict(client_arch=arch, first_call_ms=latency, warm_ms=samples, warm_labels=labels, functional=functional,
                    median_ms=statistics.median(samples),
                    p95_ms=sorted(samples)[math.ceil(len(samples) * .95) - 1],
                    calls_per_second=1000 / statistics.mean(samples))


def cpu():
    if platform.system() == "Darwin":
        return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    if os.name == "nt":
        return subprocess.check_output(["powershell", "-NoProfile", "-Command",
                                        "(Get-CimInstance Win32_Processor)[0].Name"], text=True).strip()
    info = Path("/proc/cpuinfo").read_text()
    return next((line.split(":", 1)[1].strip() for line in info.splitlines()
                 if line.startswith(("model name", "CPU part"))), platform.machine())


def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(["git", "-C", args.release, "rev-parse", "HEAD"], text=True).strip()
    result = dict(version=args.version, release_commit=commit, runner=args.runner,
                  platform=platform_key(), os=platform.platform(),
                  cpu=cpu(), cores=os.cpu_count(), model=args.model, clients={}, errors={})
    report = args.output / f"{'eval' if args.eval else 'bench'}-{args.runner}-{args.model}.json"
    def save():
        report.write_text(json.dumps(result, indent=2) + "\n")
    save()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp).resolve()
        start = time.perf_counter_ns()
        install, result["artifacts"] = stage(args.release, work, args.model)
        result["download_and_setup_ms"] = milliseconds(start)
        env = dict(os.environ, HOME=str(work / "home"), USERPROFILE=str(work / "home"),
                   NATIVELANG_CLASSIFY_SERVICE="0", PYTHONIOENCODING="utf-8")
        result["native_load_ms"] = native_load(install, env, args.output / "native.log")
        save()
        for language in ([args.eval] if args.eval else LANGUAGES):
            try:
                command = client(language, args.version, args.release, work, install)
                result["clients"][language] = measure(language, command, env, args.output / (language + ".log"), args.eval)
                profiles = list((work / "home").rglob("model/profile.json"))
                if profiles != [install / "model/profile.json"]:
                    raise RuntimeError(f"{language} installed a different runtime in the test home")
                print(args.runner, args.model, language, "OK", flush=True)
            except Exception as exc:
                result["errors"][language] = str(exc)
                traceback.print_exc()
            save()
        if not args.eval and result["clients"]:
            labels = [(m["warm_labels"], m["functional"]) for m in result["clients"].values()]
            if any(x != labels[0] for x in labels[1:]):
                result["errors"]["agreement"] = "Clients disagreed on classification results"
                save()
        if result["errors"]:
            raise SystemExit("One or more clients failed")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--version", required=True)
    p.add_argument("--runner", required=True)
    p.add_argument("--model", choices=("compact", "standard"), required=True)
    p.add_argument("--release", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--eval", choices=LANGUAGES)
    run(p.parse_args())
