---
name: review-classify-writing
description: Write or review a Classify explanation so a first-time reader can see the idea before learning the details.
---

# Give the reader a useful first example

Describe the product in one sentence that also holds for a different use case. Put the concrete scenario in a labeled example below it. If the user gives you an example that answers it, keep the words and values that make it clear. Change it only if the change makes the idea clearer or corrects a misleading result.

*Example (pseudocode)*

```text
classify("This is a terrible movie", categories=["good", "bad"])
```

The result is `"bad"`.

**Review the example on its own.** Cover the surrounding paragraphs. Can you point to the text, name the categories, and say the answer? Keep real values inline. A movie app sorts reviews into categories, so call them categories. Show the answer directly. Fix the example before adding prose.

When the user has suggested a simpler version, compare it with the draft before merging. For each extra name, field, or step, ask what it teaches at this point. Cut anything the reader can learn later.

Check shared pseudocode against the behavior promised to customers. Keep internal data structures out of it. For a language-specific example, install the stated package version in a clean environment, run the published code exactly as shown, and check the result. Use labeled pseudocode while a binding is still planned. [API specification](../../../SPECIFICATION.md) · [Releases](https://github.com/nativelang/classify/releases)

For a setup guide, open with what will be running and where the reader’s text goes. Then give the command and what they should see when it works.
