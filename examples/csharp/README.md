# C#

[Start the local server](../../self-hosting/README.md). With the .NET 10 SDK installed, save this as `Classify.cs`.

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;

const string ClassifyEndpoint = "http://127.0.0.1:8080/v1/classify";
using var client = new HttpClient();
using var review = new StringContent(
    """{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}""",
    Encoding.UTF8, "application/json");
using var response = await client.PostAsync(ClassifyEndpoint, review);
response.EnsureSuccessStatusCode();
using var result = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
Console.WriteLine(result.RootElement.GetProperty("category").GetString() ?? "unknown");
```

```sh
dotnet run --file Classify.cs
```

Prints `negative`.
