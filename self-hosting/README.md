# Running the free Classify server

Docker and the native macOS or Linux server expose the same `POST /v1/classify` API. Each distribution includes the free model and inference library. These commands describe the planned first release. Use the image or native archive listed for your platform on the [releases page](https://github.com/nativelang/classify/releases).

## Docker

Set `CLASSIFY_IMAGE` to the full image reference from the release manifest, including its digest. The planned repository is `ghcr.io/nativelang/classify`. The image entrypoint starts the server on `0.0.0.0:8080` inside the container. This command exposes it only on the host’s loopback interface.

```sh
docker run --rm -p 127.0.0.1:8080:8080 "${CLASSIFY_IMAGE:?Set CLASSIFY_IMAGE to the released image reference}"
```

## Native macOS or Linux

Download the native server archive for your OS and processor, verify the SHA-256 from the release and unpack it. From the unpacked directory, start the bundled server with its included model.

```sh
./classify serve --listen 127.0.0.1:8080
```

The language binding can be installed on the same machine. It can classify in the application process, or you can call the server directly from any HTTP client.

## Try a request

In another terminal, send a request to the local server. The loopback endpoint does not require a key.

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{"text":"Move my appointment to Monday, please.","options":[{"id":"reschedule","description":"Change the time or day of an existing appointment."},{"id":"cancel","description":"Cancel an existing appointment."}]}'
```

A matching response for this example has `status` equal to `matched`, `option` equal to `reschedule`, and `source` equal to `self_hosted`. To exercise the `unknown` path, try “Where is my appointment?” with the same options. An `unknown` response has a null `option` and `score`. [Full response and error contract](../SPECIFICATION.md#call-and-result)
