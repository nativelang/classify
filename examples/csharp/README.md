# Classify a movie review in C#

In your .NET 10 console project, install Classify.

```sh
dotnet add package NativeLang.Classify
```

Replace the contents of `Program.cs` with this code. [View Program.cs](Program.cs)

```csharp
using System;
using NativeLang.Classify;

using var model = new Classifier();
string? category = model.Classify("This is a terrible movie", "positive", "negative", "neutral");
Console.WriteLine(category ?? "unknown");
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
dotnet run
```

Expected output

```text
negative
```

If no category fits, the classifier returns `null` and this example prints `unknown`. Reuse the same `Classifier` for multiple calls.

[Run Classify on Windows or an Intel Mac](../../self-hosting/README.md)
