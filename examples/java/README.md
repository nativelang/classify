# Classify a movie review in Java

Add Classify to the dependencies in your `pom.xml`.

```xml
<dependency>
  <groupId>io.github.nativelang</groupId>
  <artifactId>classify</artifactId>
  <version>0.2.0</version>
</dependency>
```

```java
import io.nativelang.classify.Classifier;

public class Movie {
    public static void main(String[] args) throws Exception {
        try (var model = new Classifier()) {
            String category = model.classify("This is a terrible movie", "positive", "negative", "neutral");
            System.out.println(category == null ? "unknown" : category);
        }
    }
}
```

With JDK 21 or later, run the example from the directory containing its [pom.xml](pom.xml).

```sh
mvn -q compile exec:java
```

The first run downloads the model (about 1.6 GB) and prints `negative`. Later calls use the cached model. If no category fits, the classifier returns `null` and this example prints `unknown`.
