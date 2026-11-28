# Java

[Start the local server](../../self-hosting/README.md). Use JDK 21 or later and download [Gson 2.15.0](https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.15.0/gson-2.15.0.jar) to your example folder.

Save as `Classify.java`.

```java
import com.google.gson.JsonParser;
import java.net.URI;
import java.net.http.*;

class Classify {
    private static final URI CLASSIFY_ENDPOINT = URI.create("http://127.0.0.1:8080/v1/classify");

    public static void main(String[] args) throws Exception {
        String review = """
            {"text":"This is a terrible movie","categories":["positive","negative","neutral"]}
            """;
        var request = HttpRequest.newBuilder(CLASSIFY_ENDPOINT)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(review))
            .build();
        var response = HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() != 200) {
            throw new IllegalStateException("Classify returned HTTP " + response.statusCode());
        }
        var category = JsonParser.parseString(response.body()).getAsJsonObject().get("category");
        System.out.println(category.isJsonNull() ? "unknown" : category.getAsString());
    }
}
```

Run from the same folder. The example prints `negative`.

```sh
java --class-path gson-2.15.0.jar Classify.java
```
