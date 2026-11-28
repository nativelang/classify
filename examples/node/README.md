# Classify a movie review in JavaScript

```sh
npm install @nativelang/classify
```

Save this as `movie.mjs`.

```javascript
import { classify } from "@nativelang/classify";

console.log(await classify("This is a terrible movie", ["positive", "negative", "neutral"]));
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
node movie.mjs
```

Expected output

```text
negative
```

If none of your categories fit, `classify` returns `null`.

[Supported platforms and TypeScript](../../SPECIFICATION.md#nodejs-platform-support)
