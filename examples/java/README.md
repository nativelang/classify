# Classify text in Java

Use the local classifier with JDK 21 or later on Apple Silicon macOS or compatible ARM64/x64 Linux. The first call downloads the compact model and runtime to your user cache. Later calls work offline. Run these commands from this example’s directory.

```sh
curl -fLO https://github.com/nativelang/classify/releases/download/v0.2.0/classify-0.2.0.jar
curl -fLO https://repo.maven.apache.org/maven2/com/google/code/gson/gson/2.15.0/gson-2.15.0.jar
```

[Movie.java](Movie.java)

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

```sh
java -cp 'classify-0.2.0.jar:gson-2.15.0.jar' Movie.java
```

Prints `negative`. The classifier returns `null` when it declines. Reuse the instance for multiple requests.
