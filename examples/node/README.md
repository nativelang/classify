# Classify a movie review in JavaScript

```sh
npm install @nativelang/classify
```

```javascript
import { classify } from "@nativelang/classify";

console.log(await classify("This is a terrible movie", ["positive", "negative", "neutral"])); // negative
```

[Speed up startup with the local API service](../../docs/service.md).
