# Classify by NativeLang

Classify is the classification library maintained by the NativeLang organization in [nativelang/classify](https://github.com/nativelang/classify). It classifies text against the options supplied by an application. This is the proposed version 1 contract for the planned packages and services. Examples use language-neutral notation unless they show HTTP or JSON.

## First call

Give `classify` a short string and the meanings your application recognizes. For a chat app asking “Should I send this message?”, the built-in `confirmation` option set supplies two IDs, `yes` and `no`.

```text
result = classify("Go ahead and send it", "builtins.confirmation")

match result.status
  "matched" → handle_confirmation(result.option)
  "unknown" → ask_for_clarification()
```

“Go ahead and send it” expresses `yes`. “Please hold off” expresses `no`. “Who will receive it?” fits neither and should yield `unknown`. Each call interprets only the supplied text and option definitions. The caller supplies any context needed to distinguish the options.

## Define your own options

An **option** has a stable string `id` for application code, a plain-language `description` of its meaning, and optional `examples` of text expressing that meaning. An **option set** is a reusable list of these options. Built-in and custom sets work the same way.

```text
errors = [
  {id: "temporary", description: "The message says the failure is temporary.",
   examples: ["Service busy. Try again later."]},
  {id: "invalid_input", description: "The message says the request contains invalid data.",
   examples: ["Missing a required field."]}
]

classify("Capacity exhausted. Please try again in a minute.", errors)
→ {status: "matched", option: "temporary", score: 0.91, source: "local"}

classify("Operation failed.", errors)
→ {status: "unknown", option: null, score: null, source: "local"}
```

The score is illustrative. The classification describes what the error message says. The application decides whether repeating that particular operation is safe.

## Name a set or compile a catalog

For a single call, pass the option list directly. To reuse a list by name, register it with the client that will use it. The name selects exactly one set. Classify supplies names under `builtins.*`, and customers define names under `app.*`.

```text
app = client()
app.defineOptions("app.errors", errors)
app.classify("Service busy.", "app.errors")
```

A **catalog** is a saved collection of named option sets. When an application has many sets or examples, it can compile them once during development or release preparation. Give `compileCatalog` a mapping of names to option lists and a destination folder. It validates all sets, saves the prepared catalog, and returns a read-only handle ready to use.

```text
sets = {"app.errors": errors, "app.support": supportOptions}
catalog = compileCatalog(sets, "./catalogs/support-v1")

# Later, at application startup
app = client(catalog = openCatalog("./catalogs/support-v1"))
app.classify("Service busy.", "app.errors")
```

The folder contains everything needed to reuse those sets with a compatible Classify installation. Customers can copy it with their application and open it once per process, even offline. To update a catalog, compile the revised definitions into a new folder and open that version. An unknown set name or an incompatible catalog produces an error. A failed compile leaves existing catalogs usable.

Catalogs are available in every tier. With the same options, settings, and local runtime, a compiled set yields the same local decision as its inline list. If fallback is enabled, only the selected set's definitions accompany the input and settings to the backend. Other sets stay local.

## Call and result

`classify(text, options, settings?)` returns one result. Option IDs are case-sensitive and unique within a set. The text, IDs, and descriptions must be nonblank strings, and the set must contain at least one option. When supplied, `examples` is a list of nonblank strings.

| Field | Meaning |
| --- | --- |
| `status` | `matched` when the text supports one clear choice. `unknown` when the evidence is weak, multiple options apply, or the text fits none of them. |
| `option` | The exact ID of the selected option, or `null` for `unknown`. |
| `score` | Strength of the selected match on a scale from 0 to 1, or `null` for `unknown`. Higher means a stronger match. A score of 0.9 does not imply a 90% chance of correctness. |
| `source` | Where the final decision was made. `local` means the Classify library running in the application process, `self_hosted` means a customer-operated server (including one on loopback), and `hosted` means the managed service. |
| `alternatives` | When requested, a ranked list of other candidates with their `option` IDs and scores. An `unknown` result can include candidates for a clarification prompt. |

Reordering a set preserves the local decision. If adding a second option makes two choices apply to the same text, the expected result is `unknown`.

Two settings are optional. Defaults suit a first call.

- `minScore` sets a minimum acceptable match score in [0, 1]. Omitting it uses the service or library default. A candidate that clears the minimum can still be ambiguous. Reordering the options never resolves a tie.
- `maxAlternatives` is a nonnegative integer limiting how many candidates to return, highest score first, excluding a selected option. It defaults to 0, which omits the field. Asking for alternatives leaves the decision unchanged.

Invalid inputs or settings produce an `invalid_argument` error. A valid but inconclusive request succeeds with `unknown`.

## Free embedded and server use

The free edition of Classify can run inside the application via `classify(text, options, settings?)`, or as a customer-operated HTTP server using Docker or a native macOS or Linux executable. Both forms work offline and require no account. Remote fallback is disabled by default.

The native server defaults to `http://127.0.0.1:8080`. The Docker image binds `0.0.0.0:8080` inside the container and the documented run command publishes it on host loopback. The listen address and port are configurable. To classify directly, send `POST /v1/classify` with a JSON body containing `text`, the `options` list, and optional `settings`. When using a named set, resolve it to its option definitions for the HTTP body. The free loopback endpoint requires no credentials.

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "Capacity exhausted. Please try again in a minute.",
    "options": [
      {"id": "temporary", "description": "The message says the failure is temporary.",
       "examples": ["Service busy. Try again later."]},
      {"id": "invalid_input", "description": "The message says the request contains invalid data.",
       "examples": ["Missing a required field."]}
    ]
  }'
```

The server classifies the request immediately. HTTP 200 carries the same result fields for both `matched` and `unknown`. For this example the server could return

```json
{"status": "matched", "option": "temporary", "score": 0.91, "source": "self_hosted"}
```

## Opt-in fallback and paid offerings

An application that wants a second decision on an embedded `unknown` configures fallback on its client.

| Client | Behavior |
| --- | --- |
| `client()` | Uses Classify in process. The input stays in the application process. |
| `client(fallback = hosted(apiKey))` | Sends an uncertain request to the paid managed service. |
| `client(fallback = selfHosted(endpoint, credentials))` | Sends an uncertain request to the configured customer-operated endpoint. Pass `null` for credentials on the free loopback endpoint or supply credentials for a protected endpoint. |

Call `client.classify(text, options, settings?)` just as in the first example. A local match completes immediately. On a local `unknown`, an enabled fallback receives the input text, option IDs, descriptions, examples, and classification settings. It returns a final `matched` or `unknown` under the same contract. A self-hosted client contacts only its configured backend. The customer's deployment determines which LLM service, if any, subsequently receives the request.

The customer-operated server and the proposed paid managed service expose the same `POST /v1/classify` contract. Managed calls use a bearer API key. Direct HTTP calls go straight to the chosen server even when the embedded library could have answered.

Premium models are a separate licensed offering. A customer can embed a premium model with Classify when its license permits. Premium package details and paid managed-service terms are still to be determined. [Packaging and licenses](PACKAGING.md)

When an enabled fallback cannot complete, the call reports an operational error so the application can choose how to proceed. HTTP errors carry a stable `error.code` and a human-readable `error.message`. Bindings expose the same codes, including `invalid_argument` (400), `unauthenticated` (401), `forbidden` (403), `rate_limited` (429), and `unavailable` (backend failure, timeout, or connection failure).
