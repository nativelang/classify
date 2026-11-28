# Classify a movie review in Python

```sh
pip install nativelang-classify
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

[Supported platforms](../../SPECIFICATION.md#python-platform-support)
