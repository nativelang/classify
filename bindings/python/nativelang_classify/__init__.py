"""Classify text locally using one shared worker per Python process."""

import atexit
import json
import os
import subprocess
import threading
from pathlib import Path
from typing import Optional

__all__ = ["classify", "close"]

_lock = threading.Lock()
_worker = None


def _after_fork():
    # Drop inherited pipes without signaling the parent process’s worker.
    global _worker
    try:
        if _worker is not None:
            _worker.stdin.close()
            _worker.stdout.close()
            _worker.poll()
            _worker = None
    finally:
        _lock.release()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(
        before=_lock.acquire, after_in_parent=_lock.release, after_in_child=_after_fork
    )


def _start():
    if os.name == "nt":
        powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        exe = Path(subprocess.check_output(
            [str(powershell), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(Path(__file__).with_name("install.ps1"))], encoding="utf-8",
        ).rstrip())
        command = [str(exe), "infer", "--profile", str(exe.parent / "model/profile.json")]
    else:
        command = ["/bin/sh", str(Path(__file__).with_name("bootstrap.sh"))]
    return subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )


def _stop():
    global _worker
    worker, _worker = _worker, None
    if worker is None:
        return
    try:
        worker.stdin.close()
    except BrokenPipeError:
        pass
    worker.stdout.close()
    try:
        worker.wait(timeout=3)
    except subprocess.TimeoutExpired:
        worker.kill()
        worker.wait()


def close() -> None:
    """Release the local worker. A subsequent call to classify starts it again."""
    with _lock:
        _stop()


atexit.register(close)


def classify(text: str, categories) -> Optional[str]:
    """Return the selected category ID, or None when no category fits."""
    global _worker
    request = json.dumps({"text": text, "categories": categories}, allow_nan=False)
    with _lock:
        if _worker is not None and _worker.poll() is not None:
            _stop()
        if _worker is None:
            _worker = _start()
        try:
            _worker.stdin.write(request + "\n")
            _worker.stdin.flush()
            line = _worker.stdout.readline()
            if not line:
                raise RuntimeError("Classify stopped before returning a result.")
            result = json.loads(line)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            _stop()
            raise RuntimeError("Classify could not complete the request.") from exc
        except BaseException:
            # A partial exchange cannot safely serve the next request.
            _stop()
            raise

    if isinstance(result, dict):
        error = result.get("error")
        if isinstance(error, dict):
            message = error.get("message") or "Classify could not complete the request."
            if error.get("code") == "invalid_argument":
                raise ValueError(message)
            raise RuntimeError(message)
        if result.get("status") == "unknown" and result.get("category") is None:
            return None
        if result.get("status") == "matched" and isinstance(result.get("category"), str):
            return result["category"]
    raise RuntimeError("Classify returned an unexpected result.")
