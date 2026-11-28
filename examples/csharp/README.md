# Classify a movie review in C#

```sh
dotnet add package NativeLang.Classify
```

```csharp
using System;
using NativeLang.Classify;

using var model = new Classifier();
string? category = model.Classify("This is a terrible movie", "positive", "negative", "neutral");
Console.WriteLine(category); // negative
```

[Speed up startup with the local API service](../../docs/service.md).
