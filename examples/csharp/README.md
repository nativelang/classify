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

The first call downloads the model. Later calls work offline.

[Platforms, download sizes and Windows setup](../../SPECIFICATION.md#language-package-platform-support)
