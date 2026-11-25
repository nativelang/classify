# Classify by NativeLang

Classify sorts text into categories you choose. Here’s a movie review.

*Pseudocode*

```text
classify("This is a terrible movie", categories=["good", "bad"])
```

The result is `"bad"`.

“The movie starts at seven” gives no opinion, so Classify can return `unknown`. Use your own categories to sort other kinds of text in your app. [See how to define the categories](SPECIFICATION.md#define-your-own-categories)

The API design and guides are available today. The first release will let you run Classify for free inside your app or on your own machine, even offline. [Choose how to run Classify](PACKAGING.md) · [Check for releases](https://github.com/nativelang/classify/releases)

The public code and guides use the [MIT License](LICENSE). Downloadable software and models will include their own terms.
