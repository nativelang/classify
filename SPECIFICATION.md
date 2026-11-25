# Using Classify in your app

## First call

*Example (pseudocode)*

```text
classify("This is a terrible movie", categories=["good", "bad"])
```

The result is `"bad"`.

“The movie starts at seven” gives no opinion. Classify can return `unknown` so your app can leave that review unlabeled.

<a id="define-your-own-options"></a>

## Define your own categories

In the proposed v1 API, category names alone are enough. Classify uses each name as both its ID and its description. If a name has a special meaning in your app, give the category a description. You can also add examples.

For instance, a shop might use `"late"` for deliveries that missed a promised arrival date. This pseudocode gives that category a more precise meaning.

```text
delivery = [
  {id: "late", description: "A package arrived after its promised date."},
  {id: "on_time", description: "A package arrived by its promised date."}
]
```

You can also use a built-in set of categories. If your app asks “Should I send this message?”, `classify("Go ahead", "builtins.confirmation")` can pick `yes`. “Please hold off” means `no`. “Who will receive it?” fits neither.

## Call and result

Call `classify(text, categories, settings?)` with at least one category. Each list entry can be a name or an object with `id`, `description`, and an optional list of `examples`. Text, names, IDs, descriptions and individual examples must be nonblank strings. IDs are case-sensitive and unique within a set. The result includes these fields.

| Field | What your app receives |
| --- | --- |
| `status` | `matched` when one category fits. `unknown` when none fits, several apply, or the evidence is weak. |
| `category` | The exact ID you supplied for the selected category, or `null` for `unknown`. |
| `score` | Match strength from 0 to 1, or `null` for `unknown`. Higher means stronger. A score of 0.9 does not imply a 90% chance of being correct. |
| `source` | `local` for a decision inside the app, `self_hosted` for a server you run (even on the same machine), or `hosted` for NativeLang’s service. |
| `alternatives` | When requested, other candidates with a `category` ID and a `score`, strongest first. On `unknown`, these can help your app ask a follow-up. |

Start with the defaults. Two settings change what you receive.

- Set `minScore` to a number from 0 to 1 to set the lowest match strength you will accept. Omitting it uses the library or service default. A category can meet the minimum and still be ambiguous.
- Set `maxAlternatives` to a nonnegative integer to limit the list of alternatives. The default, 0, omits the field. The list excludes the selected category. Requesting it leaves the decision unchanged.

Reordering the categories preserves the local decision. If two categories both apply or tie for first place, the local result is `unknown`. Invalid input produces an `invalid_argument` error.

## Name a set or compile a catalog

If you use the same categories repeatedly, give the list a name on your client. Your names start with `app.` and built-in names start with `builtins.`. Each name selects one set. Both examples below use pseudocode.

```text
app = client()
app.defineCategories("app.ratings", ["good", "bad"])
app.classify("I loved every minute", "app.ratings")
```

If you ship several named sets with your app, you can prepare them once and save them together in a **catalog**. Compile it during release preparation, then open the saved folder at startup. This is available in every planned edition.

```text
sets = {"app.ratings": ["good", "bad"]}
catalog = compileCatalog(sets, "./catalogs/reviews-v1")

# At startup
app = client(catalog = openCatalog("./catalogs/reviews-v1"))
app.classify("I loved every minute", "app.ratings")
```

Compiling validates every set and returns a read-only handle. You can copy the folder with your app and open it offline with a compatible installation. Given the same categories, settings and local runtime, a saved set gives the same decision as passing its list directly. To update the catalog, compile to a new folder. A failed compile leaves existing catalogs usable. An unknown name or an incompatible catalog produces an error.

## Free embedded and server use

The free edition is designed to run inside your app or on a server you run. Both work offline after installation and require no account. To call a server directly, send `POST /v1/classify` with a JSON body containing `text`, the list of `categories`, and optional `settings`. Expand a named set to its definitions before sending it.

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "This is a terrible movie",
    "categories": ["good", "bad"]
  }'
```

A successful response uses HTTP 200 for either `matched` or `unknown`. For this example you might receive

```json
{"status": "matched", "category": "bad", "score": 0.91, "source": "self_hosted"}
```

The native server defaults to `http://127.0.0.1:8080` on your machine. You can change its address and port. The [server guide](self-hosting/README.md) shows how to start the native or Docker server and reach it from the same machine.

## Opt-in fallback and paid offerings

Normally the library handles the request inside your app. If you want a second opinion when it returns `unknown`, configure a **fallback** on the client. A local match always ends the call.

| Client setup | Where an uncertain request goes |
| --- | --- |
| `client()` | It stays inside the app. This is the default. |
| `client(fallback = selfHosted(endpoint, credentials))` | To the server you specify. Pass `null` for credentials on the free local endpoint, or supply the credentials your server requires. |
| `client(fallback = hosted(apiKey))` | To the planned paid NativeLang service. |

Use `client.classify(text, categories, settings?)` with any of these clients. An enabled fallback sends the text, settings and just the selected set of category IDs, descriptions and examples. The server returns a final `matched` or `unknown`. If you run the server, its configuration determines whether it sends data to another service.

You can also call a server directly even when the library could answer. The planned managed service uses the same HTTP request with a bearer API key. [Hosted and licensed deployments](PACKAGING.md#hosted-and-premium-delivery)

If the server cannot complete a request, including a fallback, your app receives an error. HTTP errors have an `error.code` for code and an `error.message` for people. Bindings use the same codes. Codes include `invalid_argument` (400), `unauthenticated` (401), `forbidden` (403), `rate_limited` (429), and `unavailable` for a backend failure, timeout or connection failure.
