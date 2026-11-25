# Run Classify on your own machine

Run the free Classify server when you want an app to send it text and get a category back over HTTP. The text stays on your machine. The server includes the model and can work offline after installation.

These instructions describe the planned first release. When downloads are available, pick **Docker** if you already run containers, or the **native server** to run it directly on macOS or Linux. [Classify releases](https://github.com/nativelang/classify/releases)

## Docker

Set `CLASSIFY_IMAGE` to the full image reference from the release, including its digest. The digest identifies the exact image to run. The planned image name is `ghcr.io/nativelang/classify`.

```sh
docker run --rm -p 127.0.0.1:8080:8080 "${CLASSIFY_IMAGE:?Set CLASSIFY_IMAGE to the released image reference}"
```

The server listens on `0.0.0.0:8080` inside the container. This command makes port 8080 reachable only from the same computer.

## Native macOS or Linux

Download the server archive for your operating system and processor. Check its SHA-256 fingerprint against the release, unpack it, and run this command from the unpacked directory.

```sh
./classify serve --listen 127.0.0.1:8080
```

## Try a request

With either server running, open a second terminal. Ask it whether a movie review is good or bad. The local server requires no API key.

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "This is a terrible movie",
    "categories": ["good", "bad"]
  }'
```

Look for `"category": "bad"` and `"source": "self_hosted"` in the response. Then change just the text to “The movie starts at seven.” The expected status is `unknown`, with `null` for the category and score. [All response fields](../SPECIFICATION.md#call-and-result)
