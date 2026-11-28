#include <stdio.h>
#include "classify.h"

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    setvbuf(stdout, NULL, _IONBF, 0);
#if defined(__aarch64__) || defined(_M_ARM64)
    puts("arm64");
#elif defined(__x86_64__) || defined(_M_X64)
    puts("x64");
#else
#error Unsupported target architecture
#endif
    char request[8192];
    char *error = NULL;
    classify_handle *model = NULL;
    int status = 0;
    while (fgets(request, sizeof request, stdin)) {
        if (!model) model = classify_open(argv[1], &error);
        char *reply = model ? classify_infer(model, request, &error) : NULL;
        if (!reply) {
            fprintf(stderr, "%s\n", error ? error : "Failed to classify");
            status = 1;
            break;
        }
        puts(reply);
        classify_free(reply);
    }
    classify_free(error);
    if (model) classify_close(model);
    return status;
}
