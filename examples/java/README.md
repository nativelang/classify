# Classify a movie review in Java

Add Classify under `<dependencies>` in your Maven `pom.xml`.

```xml
<dependency>
  <groupId>io.github.nativelang</groupId>
  <artifactId>classify</artifactId>
  <version>0.2.2</version>
</dependency>
```

```java
import io.nativelang.classify.Classifier;

public class Movie {
    public static void main(String[] args) throws Exception {
        try (var model = new Classifier()) {
            String category = model.classify("This is a terrible movie", "positive", "negative", "neutral");
            System.out.println(category); // negative
        }
    }
}
```

[Speed up startup with the local API service](../../docs/service.md).
