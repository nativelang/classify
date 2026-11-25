# Classify by NativeLang

Give Classify a movie review and the choices your app cares about.

*Pseudocode*

```text
classify("This is a terrible movie", options=["good", "bad"])
```

The result is `"bad"`.

“The movie starts at seven” gives no opinion, so Classify can return `unknown`. Use your own choices to sort other kinds of text in your app. [See how to define the choices](SPECIFICATION.md#define-your-own-options)

The API design and guides are available today. The first release will let you run Classify for free inside your app or on your own machine, even offline. [Choose how to run Classify](PACKAGING.md) · [Check for releases](https://github.com/nativelang/classify/releases)

The public code and guides use the [MIT License](LICENSE). Downloadable software and models will include their own terms.
