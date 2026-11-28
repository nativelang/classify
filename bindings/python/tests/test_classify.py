from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import nativelang_classify as app


def start_worker():
    script = """
import json, sys
for line in sys.stdin:
    request = json.loads(line)
    if request["text"] == "stop":
        sys.exit(1)
    if not request["categories"]:
        response = {"error": {"code": "invalid_argument", "message": "Missing categories"}}
    elif request["text"] in request["categories"]:
        response = {"status": "matched", "category": request["text"]}
    else:
        response = {"status": "unknown", "category": None}
    print(json.dumps(response), flush=True)
"""
    return subprocess.Popen(
        [sys.executable, "-c", script],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8",
    )


class WorkerTests(unittest.TestCase):
    def setUp(self):
        app.close()
        self.addCleanup(app.close)

    def test_concurrent_calls_keep_their_responses(self):
        def call(i):
            text = f"category-{i}"
            return app.classify(text, [text])

        with patch.object(app, "_start", side_effect=start_worker) as start:
            with ThreadPoolExecutor(max_workers=8) as threads:
                self.assertEqual(list(threads.map(call, range(32))), [f"category-{i}" for i in range(32)])
            start.assert_called_once()
            self.assertIsNone(app.classify("other", ["a"]))
            with self.assertRaisesRegex(ValueError, "Missing categories"):
                app.classify("invalid", [])
            self.assertEqual(app.classify("a", ["a"]), "a")
            self.assertEqual(start.call_count, 1)

    def test_next_call_after_exit_or_close_starts_a_new_worker(self):
        with patch.object(app, "_start", side_effect=start_worker) as start:
            with self.assertRaisesRegex(RuntimeError, "stopped"):
                app.classify("stop", ["a"])
            self.assertEqual(app.classify("a", ["a"]), "a")
            app.close()
            app.close()
            self.assertIsNone(app.classify("other", ["a"]))
            self.assertEqual(start.call_count, 3)

    @unittest.skipUnless(hasattr(os, "fork"), "requires fork")
    def test_child_does_not_control_parent_worker(self):
        with patch.object(app, "_start", side_effect=start_worker):
            self.assertEqual(app.classify("a", ["a"]), "a")
            parent_worker = app._worker.pid
            child = os.fork()
            if child == 0:
                try:
                    ok = app.classify("b", ["b"]) == "b" and app._worker.pid != parent_worker
                    app.close()
                except BaseException:
                    os._exit(1)
                os._exit(0 if ok else 1)
            self.assertEqual(os.waitpid(child, 0)[1], 0)
            self.assertEqual(app.classify("a", ["a"]), "a")
            self.assertEqual(app._worker.pid, parent_worker)

    def test_packaged_bootstrap_matches_canonical_script(self):
        root = Path(__file__).resolve().parents[3]
        packaged = Path(app.__file__).with_name("bootstrap.sh")
        self.assertEqual(packaged.read_bytes(), (root / "app" / "bootstrap.sh").read_bytes())
