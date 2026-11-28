# Classify a movie review in C

[Download the SDK and model for your platform](BUILD.md#download-the-sdk-and-model).

```c
const char *request =
    "{\"text\":\"This is a terrible movie\",\"categories\":[\"positive\",\"negative\",\"neutral\"]}";
char *result = classify_infer(model, request, &error);  // JSON contains "category":"negative".
classify_free(result);
```

[Full C example](classify.c) · [Build instructions](BUILD.md)
