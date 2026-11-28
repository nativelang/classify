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

The first run downloads the model (about 1.6 GB). Later runs work offline.

[Run Classify on Windows or an Intel Mac](../../self-hosting/README.md)
