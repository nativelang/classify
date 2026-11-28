# Classify text from C#

[Start the local Classify server](../../self-hosting/README.md) and install the .NET 10 SDK. This example sends a movie review with `HttpClient` and reads the category with `System.Text.Json`. Both libraries are included in .NET.

Save this as `Classify.cs`.

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;

using var client = new HttpClient();
using var review = new StringContent(
    """{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}""",
    Encoding.UTF8, "application/json");
using var response = await client.PostAsync("http://127.0.0.1:8080/v1/classify", review);
response.EnsureSuccessStatusCode();
using var result = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
Console.WriteLine(result.RootElement.GetProperty("category").GetString() ?? "unknown");
```

Run it from the directory containing the file.

```sh
dotnet run --file Classify.cs
```

Output with Compact r3

```text
negative
```
