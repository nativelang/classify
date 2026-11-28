# Classify a movie review in JavaScript or TypeScript

You’ll need Node.js 22.18 or later. Use an Apple Silicon Mac with macOS 15 or later, or [Debian 12-compatible Linux](../../SPECIFICATION.md#linux-requirements) on ARM64 or x64. On Windows or an Intel Mac, [run the local server](../../self-hosting/README.md).

Install Classify in an empty folder.

```sh
npm install @nativelang/classify
```

Save this as `movie.mjs`.

```javascript
import { classify } from "@nativelang/classify";

const category = await classify("This is a terrible movie", ["positive", "negative", "neutral"]);
console.log(category);
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
node movie.mjs
```

Expected output

```text
negative
```

For TypeScript, save the same code as `movie.mts` and run `node movie.mts`. Both versions return `null` when no category fits. Calls in the same app reuse the running classifier.
