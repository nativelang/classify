# Classify a movie review in Python

```sh
pip install nativelang-classify
```

Save this as `movie.py`.

```python
from nativelang_classify import classify

print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))  # negative
```

The first run downloads about 1.6 GB on Apple Silicon and Linux, or 2.5 GB on Intel Macs and Windows. Later runs work offline.

```sh
python movie.py
```

If none of your categories fit, `classify` returns `None`.

[Supported platforms](../../SPECIFICATION.md#python-platform-support)
