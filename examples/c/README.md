# C

On Apple Silicon, [unpack the C SDK and model](../../PACKAGING.md#make-a-c-call-on-apple-silicon), then build and run the [example](classify.c) from the repository root.

```sh
cc -std=c11 -Isdk/include examples/c/classify.c -Lsdk/lib -lclassify_core \
  -Wl,-rpath,@executable_path/sdk/lib -o classify-example
./classify-example model/profile.json
```

For “This is a terrible movie”, the result includes `"category":"negative"`.
