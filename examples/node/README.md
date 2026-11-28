# Classify a movie review in JavaScript

```sh
npm install @nativelang/classify
```

```javascript
import { classify } from "@nativelang/classify";

console.log(await classify("This is a terrible movie", ["positive", "negative", "neutral"])); // negative
```

The first run downloads the Compact model and runtime (about 1.6 GB). Later runs work offline.

[Supported platforms and TypeScript](../../SPECIFICATION.md#language-package-platform-support)
