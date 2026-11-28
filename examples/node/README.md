# JavaScript and TypeScript

Install the package and run the example with Node.js 22.18 or later on macOS 15+ with Apple Silicon or Debian 12-compatible Linux on ARM64 or x64.

```sh
npm install https://github.com/nativelang/classify/releases/download/v0.2.0/nativelang-classify-0.2.0.tgz
```

```javascript
import { classify } from "@nativelang/classify";

const category = await classify("This is a terrible movie", ["positive", "negative", "neutral"]);
console.log(category);
```

Save as `movie.mjs` and run `node movie.mjs`. For TypeScript, save as `movie.mts` and run `node movie.mts`. Both print `negative`. If no category fits, `classify` returns `null`.

The first call downloads and verifies the local runtime and model. Later runs reuse the download, including offline. Calls in the same app reuse the running classifier.
