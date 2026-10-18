---
name: code-review-basics
description: Review code changes for correctness, readability, tests, and obvious security problems. Use when the user asks for a review of their changes, a diff, or a branch, or before they open a merge request.
allowed-tools: Bash(git diff *) Bash(git status *) Bash(git log *) Read Grep Glob
---

# Code review basics

Review the changes the user points to. If they don't specify, review the current branch against its base:

1. Find the base: try `git merge-base HEAD origin/main`, then `origin/master`, then `origin/develop`. If none exist, review uncommitted changes (`git diff HEAD`).
2. Read the full diff, then open the surrounding code for any change you can't judge from the diff alone.

## Checklist

Work through each item. Only report items with a real finding.

**Correctness**
- Does the code do what the change intends? Look for off-by-one errors, wrong conditions, unhandled `None`/null, and swallowed exceptions.
- Are edge cases handled: empty input, very large input, concurrent calls, retries?

**Tests**
- Is every behaviour change covered by a test that would fail without it?
- Do the tests check behaviour, not implementation details?

**Readability**
- Are names accurate? Would a new joiner understand this in one read?
- Is there dead code, debug output, or commented-out code left behind?

**Security (basics)**
- No secrets, tokens, or credentials in code, config, or logs.
- User input is validated, and queries are parameterised, never built by string concatenation.

**Consistency**
- Does it follow the conventions in CLAUDE.md and the surrounding code?

## Output

Group findings by severity:

- **Must fix**: bugs, security issues, missing tests for risky logic.
- **Should fix**: maintainability problems that will cost time later.
- **Nit**: optional polish. Keep these few.

For each finding give `file:line`, the problem, and a concrete suggested fix. End with a one-line verdict: *ready to merge*, *ready after must-fixes*, or *needs another pass*. If you find nothing in a category, leave the category out. Do not invent issues to fill space.

> The Pro edition adds full security, performance, accessibility, and API-design checklists and a `/review` command that picks the right ones for the diff.
