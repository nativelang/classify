# Run Classify on your own machine

Run the free Classify server when you want an app to send it text and get a category back over HTTP. The text stays on your machine. The server includes the model and can work offline after installation.

These instructions describe the planned first release. When downloads are available, pick **Docker** if you already run containers, or the **native server** to run it directly on Windows, macOS, or Linux. [Classify releases](https://github.com/nativelang/classify/releases)

## Docker

Use Docker with Linux containers. Set the shell variable `CLASSIFY_IMAGE` to the full image reference from the release, including its digest. The planned image name is `ghcr.io/nativelang/classify`.

```sh
docker run --rm -p 127.0.0.1:8080:8080 "$CLASSIFY_IMAGE"
```

The server listens on `0.0.0.0:8080` inside the container. This command makes port 8080 reachable only from the same computer.

## Native server

Download the server archive for your operating system and processor. Check its SHA-256 fingerprint against the release, unpack it, and open a terminal in the unpacked directory.

**Windows (PowerShell)**

```powershell
.\classify.exe serve --listen 127.0.0.1:8080
```

<a id="native-macos-or-linux"></a>

**macOS or Linux**

```sh
./classify serve --listen 127.0.0.1:8080
```

## Try a request

With either server running, open a second terminal. Ask it whether a movie review is good or bad. The local server requires no API key.

**Windows (PowerShell)**

```powershell
$review = '{"text":"This is a terrible movie","categories":["good","bad"]}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/v1/classify' -Method Post -ContentType 'application/json' -Body $review
```

**macOS or Linux**

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "This is a terrible movie",
    "categories": ["good", "bad"]
  }'
```

The response should show `bad` for the category and `self_hosted` for the source. Then change just the text to “The movie starts at seven.” The expected status is `unknown`, with `null` for the category and score. [All response fields](../SPECIFICATION.md#call-and-result)
