# Python

[Start the local Classify server](../../self-hosting/README.md). In a second terminal, install Requests.

```sh
pip install requests
```

Save this as `movie.py` and run `python movie.py`. It prints `negative`.

```python
import requests

CLASSIFY_URL = "http://127.0.0.1:8080/v1/classify"


def classify(text, categories):
    response = requests.post(CLASSIFY_URL, json={"text": text, "categories": categories})
    response.raise_for_status()
    return response.json()["category"]


print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))
```
