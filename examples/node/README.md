# Classify a movie review in JavaScript

```sh
npm install @nativelang/classify
```

Save this as `movie.mjs`.

```javascript
import { classify } from "@nativelang/classify";

console.log(await classify("This is a terrible movie", ["positive", "negative", "neutral"])); // negative
```

The first run downloads about 1.6 GB on Apple Silicon and Linux, or 2.5 GB on Intel Macs and Windows. Later runs work offline.

```sh
node movie.mjs
```

If none of your categories fit, `classify` returns `null`.

[Supported platforms and TypeScript](../../SPECIFICATION.md#nodejs-platform-support)
