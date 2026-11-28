# Classify text in C#

Use the local classifier with the .NET 10 SDK on Apple Silicon macOS or compatible ARM64/x64 Linux. The first call downloads the compact model and runtime to your user cache. Later calls work offline. Run these commands from this example’s directory.

```sh
mkdir -p packages
curl -fL https://github.com/nativelang/classify/releases/download/v0.2.0/NativeLang.Classify.0.2.0.nupkg \
  -o packages/NativeLang.Classify.0.2.0.nupkg
dotnet restore Movie.csproj --source ./packages
```

[Program.cs](Program.cs)

```csharp
using System;
using NativeLang.Classify;

using var model = new Classifier();
string? category = model.Classify("This is a terrible movie", "positive", "negative", "neutral");
Console.WriteLine(category ?? "unknown");
```

```sh
dotnet run --project Movie.csproj --no-restore
```

Prints `negative`. The classifier returns `null` when it declines. Reuse the instance for multiple requests.
