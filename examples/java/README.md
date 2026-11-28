# Classify a movie review in Java

You’ll need JDK 21 or later. Use an Apple Silicon Mac with macOS 15 or later, or [Debian 12-compatible Linux](../../SPECIFICATION.md#linux-requirements) on ARM64 or x64. On Windows or an Intel Mac, [run the local server](../../self-hosting/README.md).

In an empty folder, download Classify and the Gson library it uses.

```sh
curl -fLO https://github.com/nativelang/classify/releases/download/v0.2.0/classify-0.2.0.jar
curl -fLO https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.15.0/gson-2.15.0.jar
```

Save this as `Movie.java`. [View Movie.java](Movie.java)

```java
import io.nativelang.classify.Classifier;

class Movie {
    public static void main(String[] args) throws Exception {
        try (var model = new Classifier()) {
            String category = model.classify("This is a terrible movie", "positive", "negative", "neutral");
            System.out.println(category == null ? "unknown" : category);
        }
    }
}
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
java -cp 'classify-0.2.0.jar:gson-2.15.0.jar' Movie.java
```

Expected output

```text
negative
```

If no category fits, the classifier returns `null` and this example prints `unknown`. Reuse the same `Classifier` for multiple calls.
