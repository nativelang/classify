# Using Classify in your app

## First call

*Example (pseudocode)*

```text
classify("This is a terrible movie", categories=["positive", "negative", "neutral"])
```

The result is `"negative"`.

<a id="define-your-own-options"></a>

## Define your own categories

Category names alone are enough. Classify uses each name as both its ID and its description. If a name has a special meaning in your app, give the category a description. You can also add examples.

For instance, a shop might use `"late"` for deliveries that missed a promised arrival date. This pseudocode gives that category a more precise meaning.

```text
delivery = [
  {id: "late", description: "A package arrived after its promised date."},
  {id: "on_time", description: "A package arrived by its promised date."}
]
```

## Call and result

The C SDK and HTTP server accept one to sixteen categories per request. Each list entry can be a name or an object with `id`, `description`, and an optional list of `examples`. Text, names, IDs, descriptions and individual examples must be nonblank strings. IDs are case-sensitive and unique within a set. The result includes these fields.

| Field | What your app receives |
| --- | --- |
| `status` | `matched` when one category fits. `unknown` when none fits, several apply, or the evidence is weak. |
| `category` | The exact ID you supplied for the selected category, or `null` for `unknown`. |
| `score` | Match strength from 0 to 1, or `null` for `unknown`. Higher means stronger. A score of 0.9 does not imply a 90% chance of being correct. |
| `source` | `local` for a decision inside the app, `self_hosted` for a server you run (even on the same machine), or `hosted` for NativeLang’s service. |
| `alternatives` | When requested, other candidates with a `category` ID and a `score`, strongest first. On `unknown`, these can help your app ask a follow-up. |

With the same three categories, Compact r3 returned `positive` for “This movie was fantastic!” and `neutral` for “I neither liked nor disliked this movie.” For “The movie starts at seven.” it returned `unknown`, with a null category.

Start with the defaults. Two settings change what you receive.

- Set `minScore` to a number from 0 to 1 to set the lowest match strength you will accept. Omitting it uses the library or service default. A category can meet the minimum and still be ambiguous.
- Set `maxAlternatives` to a nonnegative integer to limit the list of alternatives. The default, 0, omits the field. The list excludes the selected category. Requesting it leaves the decision unchanged.

Reordering the categories preserves the local decision. A tie for first place yields `unknown`. Invalid input produces an `invalid_argument` error.

## Name a set or compile a catalog

The following examples describe a planned client API. With the current C SDK and server, keep reusable lists in your app and pass their definitions on each call. In the planned API, you can give a list a name on your client. Your names start with `app.` and built-in names start with `builtins.`. Each name selects one set. Both examples below use pseudocode.

```text
app = client()
app.defineCategories("app.ratings", ["positive", "negative", "neutral"])
app.classify("I loved every minute", "app.ratings")
```

If you ship several named sets with your app, you can prepare them once and save them together in a **catalog**. Compile it during release preparation, then open the saved folder at startup. This is available in every planned edition.

```text
sets = {"app.ratings": ["positive", "negative", "neutral"]}
catalog = compileCatalog(sets, "./catalogs/reviews-v1")

# At startup
app = client(catalog = openCatalog("./catalogs/reviews-v1"))
app.classify("I loved every minute", "app.ratings")
```

Compiling validates every set and returns a read-only handle. You can copy the folder with your app and open it offline with a compatible installation. Given the same categories, settings and local runtime, a saved set gives the same decision as passing its list directly. To update the catalog, compile to a new folder. A failed compile leaves existing catalogs usable. An unknown name or an incompatible catalog produces an error. A planned built-in confirmation set will also let callers use `builtins.confirmation` for yes/no requests.

## Free embedded and server use

You can embed the C SDK or run the HTTP server on your own machine. Both work offline after installation and require no account. To call a server directly, send `POST /v1/classify` with a JSON body containing `text`, the list of `categories`, and optional `settings`. Expand a named set to its definitions before sending it.

```sh
curl --request POST 'http://127.0.0.1:8080/v1/classify' \
  --header 'Content-Type: application/json' \
  --data '{
    "text": "This is a terrible movie",
    "categories": ["positive", "negative", "neutral"]
  }'
```

A successful response uses HTTP 200 for either `matched` or `unknown`. Compact r3 on Apple Silicon returned

```json
{"status": "matched", "category": "negative", "score": 0.9844168916948893, "source": "self_hosted"}
```

The native server defaults to `http://127.0.0.1:8080` on your machine. You can change its address and port. The [server guide](self-hosting/README.md) shows how to start the native or Docker server and reach it from the same machine.

## Opt-in fallback and paid offerings

The released C SDK handles requests inside your app. The following fallback settings are planned for client libraries. They let the client ask a server for a second opinion when a local request returns `unknown`. A local match always ends the call.

| Client setup | Where an uncertain request goes |
| --- | --- |
| `client()` | It stays inside the app. This is the default. |
| `client(fallback = selfHosted(endpoint, credentials))` | To the server you specify. Pass `null` for credentials on the free local endpoint, or supply the credentials your server requires. |
| `client(fallback = hosted(apiKey))` | To the planned paid NativeLang service. |

Use `client.classify(text, categories, settings?)` with any of these clients. An enabled fallback sends the text, settings and just the selected set of category IDs, descriptions and examples. The server returns a final `matched` or `unknown`. If you run the server, its configuration determines whether it sends data to another service.

You can also call a server directly even when the library could answer. The planned managed service uses the same HTTP request with a bearer API key. [Hosted and licensed deployments](PACKAGING.md#hosted-and-premium-delivery)

If the server cannot complete a request, including a fallback, your app receives an error. HTTP errors have an `error.code` for code and an `error.message` for people. Bindings use the same codes. Codes include `invalid_argument` (400), `unauthenticated` (401), `forbidden` (403), `rate_limited` (429), and `unavailable` for a backend failure, timeout or connection failure.
