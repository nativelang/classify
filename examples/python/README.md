# Python

Install the package with Python 3.9 or later on an Apple Silicon Mac (macOS 15+) or Linux (ARM64 or x64 with Debian 12–compatible libraries).

```sh
pip install https://github.com/nativelang/classify/releases/download/v0.2.0/nativelang_classify-0.2.0-py3-none-any.whl
```

```python
from nativelang_classify import classify

print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))
```

Save as `movie.py` and run `python movie.py`. It prints `negative`. The first call downloads the model and runtime (about 1.6 GB); subsequent calls work offline. On a minimal Linux installation, the download requires `curl`, `tar`, `sha256sum`, and `flock`. If Classify declines to choose, it returns `None`.
