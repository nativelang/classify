# Contributing to Classify

## Writing for developers

- Write for someone trying Classify for the first time. Show what it does, one working call and its answer. Introduce each requirement when the reader needs it.
- Keep the movie review, its three categories and the answer together. Label pseudocode and put its result in a comment.
- Put deployment choices in a linked guide. Explain why someone would choose each option before giving the command. For example, several scripts can share a server to avoid loading the model each time they start.
- Follow each platform’s instructions from a clean folder. Check prerequisites, links and commands. A Linux reader should be able to run the example without translating a Mac command. For language examples, install the dependencies, run the published code as written and verify the output before merging.
- Put optional settings and error cases in the [API reference](SPECIFICATION.md). Keep upcoming features separate from working instructions. Cut sentences that repeat a command or explain a detail the reader can ignore.

Use IBM Plex Sans for the Classify name, headings and body text on pages we style, and IBM Plex Mono for code. In the GitHub README, use the wordmark for the title and keep code copyable.

## Pull requests

Use a branch and pull request for every change. Merge into `main` after required checks and reviews pass.
