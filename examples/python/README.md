# Classify a movie review in Python

```sh
pip install nativelang-classify
```

```python
from nativelang_classify import classify

print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))  # negative
```

The first run downloads the Compact model and runtime (about 1.6 GB). Later runs work offline.

[Supported platforms](../../SPECIFICATION.md#language-package-platform-support)
