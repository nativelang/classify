# JavaScript and TypeScript

[Start Classify](../../self-hosting/README.md). Use Node.js 22.18 or later.

```javascript
const CLASSIFY_URL = "http://127.0.0.1:8080/v1/classify";

const response = await fetch(CLASSIFY_URL, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "This is a terrible movie",
    categories: ["positive", "negative", "neutral"],
  }),
});
if (!response.ok) throw new Error(await response.text());
console.log((await response.json()).category);
```

Save as `movie.mjs` and run `node movie.mjs`. For TypeScript, use `movie.mts` and run `node movie.mts`. Both print `negative`.
