# Python

[Start the local Classify server](../../self-hosting/README.md). Create a virtual environment with `python3 -m venv .venv` on macOS or Linux, or `py -m venv .venv` on Windows. Activate it with `source .venv/bin/activate` or, in PowerShell, `.\.venv\Scripts\Activate.ps1`. Then install Requests.

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
        timeout=(5, 1800),
    )
    response.raise_for_status()
    return response.json()["category"]


print(classify("This is a terrible movie", ["positive", "negative", "neutral"]))
```
