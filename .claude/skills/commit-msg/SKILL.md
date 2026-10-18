---
name: commit-msg
description: Write a commit message for the currently staged changes. Use when the user asks for a commit message.
argument-hint: "[optional context, e.g. ticket key]"
disable-model-invocation: true
allowed-tools: Bash(git diff *) Bash(git status *) Bash(git log *)
---

## Staged changes

!`git diff --cached --stat || true`

!`git diff --cached || true`

## Recent commit style in this repo

!`git log -n 10 --pretty=format:'%s' || true`

## Task

Write one commit message for the staged changes above.

- If nothing is staged, say so and stop. Suggest `git add -p`.
- Follow the commit style used in the recent history. If the history uses Conventional Commits (`feat:`, `fix:`, `chore:` ...), use them; if CLAUDE.md specifies a format, that wins.
- Subject line: imperative mood, at most 72 characters, no trailing period.
- Body (only if the change is not obvious): what changed and **why**, wrapped at 72 characters. Skip a body for trivial changes.
- Extra context from the user, if any: $ARGUMENTS. If it contains a ticket key (e.g. `ABC-123`), include it the way recent history does, or as a `Refs: ABC-123` trailer.
- If the staged diff mixes unrelated changes, say so and suggest how to split it.

Output only the message in a code block, ready to paste. Do not run `git commit`.
