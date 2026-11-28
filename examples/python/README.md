# Classify a movie review in Python

You’ll need Python 3.9 or later. Use an Apple Silicon Mac with macOS 15 or later, or [Debian 12-compatible Linux](../../SPECIFICATION.md#where-the-language-packages-store-the-model) on ARM64 or x64. On Windows or an Intel Mac, [run the local server](../../self-hosting/README.md).

In an empty folder, create a virtual environment and install Classify. On Debian, install `python3-venv` if you need it.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install https://github.com/nativelang/classify/releases/download/v0.2.0/nativelang_classify-0.2.0-py3-none-any.whl
```

Save this as `movie.py`.

```python
from nativelang_classify import classify

print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
python movie.py
```

Expected output

```text
negative
```

If none of your categories fit, `classify` returns `None`.
