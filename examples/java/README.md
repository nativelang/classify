# Classify text from Java

[Start the local Classify server](../../self-hosting/README.md). Install JDK 21 or later and save [Gson 2.15.0](https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.15.0/gson-2.15.0.jar) beside `Classify.java`. This example uses Java’s HTTP client to send a movie review and Gson to read the category from the response.

Save this as `Classify.java`.

```java
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

class Classify {
    public static void main(String[] args) throws Exception {
        String review = """
            {"text":"This is a terrible movie","categories":["positive","negative","neutral"]}
            """;
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:8080/v1/classify"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(review))
            .build();
        var response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) {
            throw new IllegalStateException("Classify returned HTTP " + response.statusCode());
        }
        JsonElement category = JsonParser.parseString(response.body()).getAsJsonObject().get("category");
        System.out.println(category.isJsonNull() ? "unknown" : category.getAsString());
    }
}
```

Run it from the directory containing both files.

```sh
java --class-path gson-2.15.0.jar Classify.java
```

Output with Compact r3

```text
negative
```
