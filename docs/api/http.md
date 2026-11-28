# HTTP API

`POST /v1/classify` accepts a JSON classification request. Both a match and an unknown result return HTTP 200.

With the [local server running](../../self-hosting/README.md), send it some text and the categories to choose from.

```sh
curl http://127.0.0.1:8080/v1/classify \
  -H 'Content-Type: application/json' \
  -d '{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}'
```

The movie request returned this result on Apple Silicon with the Compact model.

```json
{"status":"matched","category":"negative","score":0.9844168916948893,"source":"self_hosted"}
```

<details>
<summary>Send the same request in Windows PowerShell</summary>

```powershell
$body = '{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}'
Invoke-RestMethod -Uri http://127.0.0.1:8080/v1/classify -Method Post -ContentType application/json -Body $body
```

</details>

## Errors

The server returns HTTP 400 with `error.code` set to `invalid_argument` for an invalid classification request, such as an empty category list. A classifier failure returns HTTP 503 with code `unavailable`. Read `error.message` for the reason.
