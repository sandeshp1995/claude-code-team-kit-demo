---
name: explain
description: Explain a file, directory, or function to someone new to this codebase.
argument-hint: "<path or symbol>"
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Explain `$ARGUMENTS` to an engineer who is new to this codebase.

If no path or symbol was given, ask which one and stop.

1. Read the target. Find where it is used (search for imports/callers) and what it depends on.
2. Write the explanation in this shape:
   - **Purpose:** one or two sentences in plain language.
   - **How it fits:** who calls it, what it calls, where it sits in the request/data flow.
   - **Key parts:** the 3–6 most important functions, classes, or sections, each with one line.
   - **Gotchas:** non-obvious behaviour, side effects, error cases, performance traps.
   - **Where to start if you need to change it:** the file and function to open first, and the tests that cover it.
3. Cite file paths with line numbers (`path/to/file.py:42`) so the reader can jump there.

Stay factual. If something is unclear from the code, say so instead of guessing. Do not modify any files.
