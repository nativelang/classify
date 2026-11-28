# Go API

`classify.Classify(text string, categories []string) (*string, error)`

Returns a pointer to the category ID on a match, `nil, nil` on abstention, and a non-nil error on failure.

[Working example](../../examples/go/)
