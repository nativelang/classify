#include <stdio.h>
#include "classify.h"

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s PATH/TO/profile.json\n", argv[0]);
        return 1;
    }

    const char *request =
        "{\"text\":\"This is a terrible movie\",\"categories\":[\"good\",\"bad\"]}";
    char *error = NULL;
    classify_handle *model = classify_open(argv[1], &error);
    char *result = NULL;
    if (model != NULL) {
        result = classify_infer(model, request, &error);
    }

    int failed = result == NULL;
    if (failed) {
        fprintf(stderr, "%s\n", error != NULL ? error : "Classification failed");
    } else {
        puts(result);
    }
    classify_free(result);
    classify_free(error);
    classify_close(model);
    return failed;
}
