---
name: plan-task
description: Turn a pasted task or ticket description into a concrete implementation plan for this repo.
argument-hint: "<paste the task description>"
disable-model-invocation: true
allowed-tools: Read Grep Glob
---

Create an implementation plan for this task:

$ARGUMENTS

If no task text was given, ask the user to paste it and stop.

Steps:

1. Restate the goal in one sentence and list acceptance criteria (derive them if the task doesn't state any, and mark them "assumed").
2. Explore the codebase to find where the change belongs. Do not edit anything.
3. Produce the plan:
   - **Files to change**, each with a one-line reason.
   - **Steps** in the order you would do them, each small enough to review on its own.
   - **Tests** to add or update.
   - **Risks and open questions**: anything that needs a decision from a human before coding starts.
   - **Rough size**: S (under an hour), M (half a day), L (more; suggest how to split).
4. End by asking whether to start on step 1.

> The Pro edition includes `/ticket-to-plan`, which pulls the ticket straight from Jira or GitLab instead of needing a paste.
