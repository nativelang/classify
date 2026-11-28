# Classify API

## Call and result

With the [local server running](self-hosting/README.md), send it some text and the categories to choose from. Run this in a second terminal on macOS or Linux.

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
  "text": "My package arrived on time.",
  "categories": [
    {"id": "late", "description": "A delivery missed its promised date.", "examples": ["My parcel is overdue."]},
    {"id": "on_time", "description": "A delivery arrived as scheduled."}
  ]
}
```

With Compact, this request returns the category ID `on_time`.

IDs must be unique and are case-sensitive. Text, IDs, descriptions and example phrases must be nonblank.

## Optional settings

To change the server address, [start the server on a different port](self-hosting/README.md#use-a-different-port). To change how Classify selects categories, add a `settings` object to the request.

| Setting | Effect |
| --- | --- |
| `minScore` | Minimum score for a match, from 0 to 1 inclusive. The model supplies the default. |
| `maxAlternatives` | Maximum number of other categories to return. A positive integer adds an `alternatives` list of category IDs and scores, strongest first. The default is 0. |

Asking for alternatives preserves the decision. On a match, the list excludes the selected category. On `unknown`, it can help your app suggest choices.

## Where the language packages store the model

On the first call, the package downloads the Compact model and the program that runs it (about 1.6 GB together). It checks the download and saves the files under `~/.nativelang/classify/` in your home folder. Projects using the same version under your account reuse that copy, even across languages. Later calls work offline.

<a id="deployment-options"></a>

To share a model already loaded in memory, [run a local server](self-hosting/README.md). To load it directly in a C program, [use the C library](examples/c/).

## Python platform support

The Python package requires Python 3.9 or later. Its local runtime supports Apple Silicon on macOS 15 or later and [Debian 12-compatible Linux](#linux-requirements) on ARM64 or x64. On Windows and Intel Macs, applications can call the [local HTTP server](self-hosting/README.md).

## Node.js platform support

Use Node.js 22.18 or later on an Apple Silicon Mac with macOS 15 or later, or on [Debian 12-compatible Linux](#linux-requirements) on ARM64 or x64. On Windows or an Intel Mac, use the [local HTTP server](self-hosting/README.md).

For TypeScript, save the [JavaScript example](examples/node/) as `movie.mts` and run `node movie.mts`.

## Linux requirements

The language packages run on ARM64 or x64 Linux with glibc and libstdc++ compatible with Debian 12 (Bookworm). On a minimal installation, the first download needs `curl`, `tar`, `sha256sum`, and `flock`. On Debian 12, these come from the `curl`, `tar`, `coreutils`, and `util-linux` packages.

## Errors

The server returns HTTP 400 with `error.code` set to `invalid_argument` for an invalid classification request, such as an empty category list. A classifier failure returns HTTP 503 with code `unavailable`. Read `error.message` for the reason.

If a language package reports an incomplete installation, move the platform folder named in the error out of `~/.nativelang/classify/`. Run the same call again to download a fresh copy.
