"""Summarize the paired evaluations in GitHub Actions; full predictions stay in JSON."""
import json
import os
from pathlib import Path


def compare(folder):
    reports = {}
    for path in folder.rglob("eval-*.json"):
        report = json.loads(path.read_text())
        if report["model"] in reports or report["errors"] or len(report["clients"]) != 1:
            raise ValueError(f"Invalid eval report: {path}")
        reports[report["model"]] = report
    reference = reports["compact"]
    language, compact = next(iter(reference["clients"].items()))
    other = reports["standard"]
    standard = other["clients"][language]
    for field in ("runner", "version", "platform", "release_commit"):
        if other[field] != reference[field]:
            raise ValueError(f"Evaluation {field} differs")
    if compact["eval_sha256"] != standard["eval_sha256"]:
        raise ValueError("Models were evaluated on different cases")
    header = f"## Evaluation of {reference['version']} on {reference['runner']} with {language}"
    lines = [header, "", "| Model | Correct | Accuracy | Abstentions | Correct abstentions |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for name, result in (("Compact", compact), ("Standard", standard)):
        unknowns = [p for p in result["predictions"] if p["expected"] is None]
        correct_unknown = sum(p["predicted"] is None for p in unknowns)
        lines.append(f"| {name} | {result['correct']}/{result['cases']} | {result['accuracy']:.1%} | "
                     f"{result['abstained']} | {correct_unknown}/{len(unknowns)} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    summary = compare(Path("scores"))
    print(summary)
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as out:
        out.write(summary)
