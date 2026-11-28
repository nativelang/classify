import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from build import LANGUAGES
from compare import compare
from measure import EVAL, measure
from select_runner import MODELS, RUNNERS, select


class QualificationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)

    def test_winner_needs_both_models_and_the_complete_matrix(self):
        paths = []
        for runner in RUNNERS:
            for model in MODELS:
                clients = {}
                for language in LANGUAGES:
                    speed = 1
                    if runner == "windows-11-arm":
                        if language == "rust":
                            speed = 100 if model == "compact" else 1
                        if language == "java":
                            speed = 10
                    clients[language] = dict(calls_per_second=speed, median_ms=1, p95_ms=1, first_call_ms=2)
                data = dict(version="1.0.0", runner=runner, platform=RUNNERS[runner], model=model, native_load_ms=2, clients=clients, errors={})
                path = self.folder / f"bench-{runner}-{model}.json"
                path.write_text(json.dumps(data))
                paths.append(path)
        args = self.folder, "1.0.0", self.folder / "summary.csv"
        self.assertEqual(select(*args), (200, "windows-11-arm", "java"))
        paths[-1].unlink()
        with self.assertRaisesRegex(ValueError, "Missing benchmark"):
            select(*args)

    def test_scoring_distinguishes_abstentions_and_wrong_categories(self):
        command = [sys.executable, "-u", "-c",
                   'import sys, platform\nprint(platform.machine())\nfor line in sys.stdin:\n'
                   ' print("negative" if line.startswith("This is a terrible movie") else "")']
        score = measure("python", command, os.environ, self.folder / "stderr.log", True)
        gold = [answer for group in json.loads(EVAL.read_text()) for _, answer in group["cases"]]
        self.assertEqual(score["correct"], gold.count(None))
        self.assertEqual(score["abstained"], len(gold))
        for model in MODELS:
            report = dict(version="1.0.0", release_commit="test", runner="macos-15", platform="Darwin/arm64",
                          model=model, errors={}, clients={"python": score})
            (self.folder / f"eval-{model}.json").write_text(json.dumps(report))
        self.assertIn(f"{gold.count(None)}/{len(gold)}", compare(self.folder))
        report["runner"] = "ubuntu-24.04"
        (self.folder / "eval-standard.json").write_text(json.dumps(report))
        with self.assertRaises(ValueError):
            compare(self.folder)


if __name__ == "__main__":
    unittest.main()
