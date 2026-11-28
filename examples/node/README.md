# JavaScript and TypeScript

[Start the local Classify server](../../self-hosting/README.md). With Node.js 22.18 or later, the same example runs as JavaScript or TypeScript using the built-in `fetch`.

Save it as `movie.mjs` and run `node movie.mjs`. For TypeScript, save it as `movie.mts` and run `node movie.mts`. Both print `negative`.

```javascript
const request = {
  text: "This is a terrible movie",
  categories: ["positive", "negative", "neutral"],
};

const response = await fetch("http://127.0.0.1:8080/v1/classify", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(request),
});
if (!response.ok) throw new Error(await response.text());
console.log((await response.json()).category);
```
