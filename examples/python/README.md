# Classify a movie review in Python

```sh
pip install nativelang-classify
```

```python
from nativelang_classify import classify

print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))  # negative
```

[Speed up startup with the local API service](../../docs/service.md).
