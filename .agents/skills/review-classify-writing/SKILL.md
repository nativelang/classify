---
name: review-classify-writing
description: Write or review a Classify explanation so a first-time reader can see the idea before learning the details.
---

# Give the reader a useful first example

Show the input, the actual choices, and the answer together. A reader should be able to understand the first example without looking up a variable.

*Pseudocode*

```text
classify("This is a terrible movie", options=["good", "bad"])
```

The result is `"bad"`.

In shared pseudocode, leave out setup and response fields that distract from the idea. Put the complete call in the API reference for readers who need it.

For a language-specific example, install the stated package version in a clean environment. Run the published code exactly as shown, including imports and setup, and check the result it tells the reader to expect. If the binding is still planned, use labeled pseudocode until a real example can be tested.

For a setup guide, start with what will be running and where the reader’s text goes. Follow with the command and what they should see when it works.

Read just the opening as someone new to the product. Could they explain what happens in their own words? Then follow the example as a junior programmer. Put prerequisites before the step that needs them and keep exact syntax, limits, and error behavior within reach. A short example must still be accurate. [Check the API](../../../SPECIFICATION.md) and [what has shipped](https://github.com/nativelang/classify/releases).
