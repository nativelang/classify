# Python

[Start the local Classify server](../../self-hosting/README.md), then install Requests in an active Python 3 virtual environment.

```sh
python -m pip install requests
```

Save this as `movie.py` and run `python movie.py`. It prints `negative`.

```python
import requests


def classify(text, categories):
    response = requests.post(
        "http://127.0.0.1:8080/v1/classify",
        json={"text": text, "categories": categories},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["category"]


print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))
```
