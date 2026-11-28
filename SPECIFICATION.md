# Classify API

The [language packages](README.md#examples) return the matching category or an empty result when Classify is unsure. If the cached installation is damaged, move its platform folder out of `~/.nativelang/classify/` and call Classify again to download a fresh copy.

## Deployment options

**Share one loaded model across apps.** Loading a model takes time and memory. If several programs on your machine use Classify, or your script starts and stops often, have them send text to one server over HTTP. The server keeps the model loaded even after a program exits. This also works on Windows and Intel Macs. [Install and start the server](self-hosting/README.md)

**Call Classify inside a C program.** Link the C library when you want your program to load the model itself. Open it at startup, classify as many texts as you need, and close it when you’re done. This works without a separate server. [Build the C example for your platform](examples/c/)

## Call and result

The server listens on `127.0.0.1:8080` by default. To use another port, [start it with `--port`](self-hosting/README.md#use-a-different-port).

```sh
curl http://127.0.0.1:8080/v1/classify \
  -H 'Content-Type: application/json' \
  -d '{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}'
```

The movie request returned this result on Apple Silicon with the compact model.

```json
{"status":"matched","category":"negative","score":0.9844168916948893,"source":"self_hosted"}
```

| Field | Meaning |
| --- | --- |
| `status` | `matched` when Classify chooses a category, `unknown` when it can’t choose one confidently. |
| `category` | The selected category ID, or `null` for `unknown`. |
| `score` | Match strength from 0 to 1, or `null` for `unknown`. A higher score indicates a stronger match. |
| `source` | `self_hosted` for the server, `local` for the C library. |

Both outcomes return HTTP 200. A tie for first place returns `unknown`. Changing the category order preserves the decision.

<a id="define-your-own-options"></a>

## Define your own categories

Send 1–16 categories. A string such as `"negative"` supplies both the ID and its description. If a category has a specific meaning in your app, give it an ID and a description. You can also include example phrases.

```json
{
  "text": "My order was due yesterday.",
  "categories": [
    {"id": "late", "description": "A delivery missed its promised date.", "examples": ["My parcel is overdue."]},
    {"id": "on_time", "description": "A delivery arrived as scheduled."}
  ]
}
```

IDs must be unique and are case-sensitive. Text, IDs, descriptions and example phrases must be nonblank.

## Optional settings

Add a `settings` object to the request to change either default.

| Setting | Effect |
| --- | --- |
| `minScore` | Minimum score for a match, from 0 to 1 inclusive. The model supplies the default. |
| `maxAlternatives` | Maximum number of other categories to return. A positive integer adds an `alternatives` list of category IDs and scores, strongest first. The default is 0. |

Asking for alternatives preserves the decision. On a match, the list excludes the selected category. On `unknown`, it can help your app suggest choices.

## Errors

The server returns HTTP 400 with `error.code` set to `invalid_argument` for an invalid classification request, such as an empty category list. A classifier failure returns HTTP 503 with code `unavailable`. Read `error.message` for the reason.
