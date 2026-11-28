# Classify API

Classify takes text and candidate categories and returns a match or an unknown result. The language bindings expose the category ID in their native return types. HTTP and C expose the full JSON result.

[Python](api/python.md) · [JavaScript and TypeScript](api/node.md) · [Java](api/java.md) · [C#](api/csharp.md) · [Go](api/go.md) · [Rust](api/rust.md) · [C](api/c.md) · [HTTP](api/http.md)

## Result

| Field | Meaning |
| --- | --- |
| `status` | `matched` when Classify chooses a category, `unknown` when it can’t choose one confidently. |
| `category` | The selected category ID, or `null` for `unknown`. |
| `score` | Match strength from 0 to 1, or `null` for `unknown`. A higher score indicates a stronger match. |
| `source` | `self_hosted` for the server, `local` for the C library. |

A tie for first place returns `unknown`. Changing the category order preserves the decision.

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

The JSON API accepts a `settings` object.

| Setting | Effect |
| --- | --- |
| `minScore` | Minimum score for a match, from 0 to 1 inclusive. The model supplies the default. |
| `maxAlternatives` | Maximum number of other categories to return. A positive integer adds an `alternatives` list of category IDs and scores, strongest first. The default is 0. |

Asking for alternatives preserves the decision. On a match, the list excludes the selected category. On `unknown`, it can help your app suggest choices.
