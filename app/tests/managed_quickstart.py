"""Exercise independent installed clients against an OS-managed instance on a clean CI account."""
import concurrent.futures
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys

def main():
    cli = Path(sys.argv[1]).resolve()
    env = dict(os.environ, NATIVELANG_CLASSIFY_SERVICE="1")
    def control(action, **options):
        return subprocess.run([cli, "service", action], env=env, text=True, capture_output=True, timeout=420, **options)
    def status():
        out = control("status", check=True).stdout
        return json.loads(out) if out.strip() != "stopped" else None
    if status() is not None:
        raise RuntimeError("The test requires an account without an active Classify service")
    request = json.dumps({"text": "This is a terrible movie", "categories": ["positive", "negative", "neutral"]})
    def client():
        result = subprocess.run([cli, "infer"], env=env, input=request+"\n", text=True, capture_output=True, timeout=420)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout).get("category") == "negative", result.stdout
    try:
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            list(pool.map(lambda _: client(), range(2)))
        initial = status()
        assert initial and initial["requests"] == 2 and initial["phase"] == "ready", initial
        client()
        assert status()["instance"] == initial["instance"]
        # Exercise recovery only for the service this test created.
        if os.name == "posix":
            os.kill(initial["pid"], signal.SIGSTOP)
            client()
            assert status()["instance"] != initial["instance"]
        control("stop", check=True)
        assert status() is None
        with socket.socket() as foreign:
            foreign.bind(("127.0.0.1", 0))
            foreign.listen()
            env["NATIVELANG_CLASSIFY_PORT"] = str(foreign.getsockname()[1])
            result = control("start")
            assert result.returncode and "Unset NATIVELANG_CLASSIFY_PORT" in result.stderr, result
            foreign.getsockname()
        print("Passed concurrent startup, warm reuse, stop, and explicit port conflict.")
    except BaseException:
        print(control("logs").stdout, file=sys.stderr)
        raise
    finally:
        result = control("stop")
        if result.returncode:
            raise RuntimeError(result.stderr)

if __name__ == "__main__":
    main()
