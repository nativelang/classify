# Classify a movie review in C#

You’ll need the .NET 10 SDK. Use an Apple Silicon Mac with macOS 15 or later, or [Debian 12-compatible Linux](../../SPECIFICATION.md#linux-requirements) on ARM64 or x64. On Windows or an Intel Mac, [run the local server](../../self-hosting/README.md).

In an empty folder, create a console app and add the Classify package.

```sh
dotnet new console --name Movie --output . --no-restore
mkdir -p packages
curl -fL https://github.com/nativelang/classify/releases/download/v0.2.0/NativeLang.Classify.0.2.0.nupkg \
  -o packages/NativeLang.Classify.0.2.0.nupkg
dotnet add Movie.csproj package NativeLang.Classify --version 0.2.0 --source ./packages
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
dotnet run --project Movie.csproj --no-restore
```

Expected output

```text
negative
```

If no category fits, the classifier returns `null` and this example prints `unknown`. Reuse the same `Classifier` for multiple calls.
