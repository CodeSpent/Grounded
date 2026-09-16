# Testing the grounded skill

This skill is prompt-based, not code, so there's no unit-test framework that can
assert against it. Instead, each fixture set below is a mocked scenario with a
known, pre-written answer key: a ticket/spec plus a diff or code sample with
deliberately planted gaps, a fabricated claim, and (for Mode D) invented scope.
A correct run of the skill has to independently re-derive every row in the
answer key from the fixture content, not from the answer key itself.

Use this to:
- Validate the skill after any edit to `SKILL.md` (regression check).
- Onboard a new engineer to what "grounded" output should look like before they
  trust it on real tickets/PRs.
- Sanity-check a different model tier before relying on it for the judgment
  steps this skill requires (see "Model requirement" in `SKILL.md`).

## Layout

```
tests/fixtures/
  mode-a-ac-compliance/   ticket.md, pr_body.md, pr.diff, answer-key.md
  mode-c-adhoc/           spec.md, comments_api.py, answer-key.md
  mode-d-drift/           ticket.md, current_diff.patch, answer-key.md
```

## How to run a fixture

1. Invoke the skill (`/grounded` or asking Copilot CLI to verify something,
   it should self-select the right mode) and point it at a fixture directory's
   files instead of live `gh`/`jira` calls, e.g.:

   > "Using `tests/fixtures/mode-a-ac-compliance/ticket.md` as the Jira ticket
   > and `tests/fixtures/mode-a-ac-compliance/pr.diff` as the PR diff (with
   > `pr_body.md` as the PR description), run an AC Compliance check."

2. Compare the resulting Evidence Table row-by-row against that fixture's
   `answer-key.md`.
3. A pass means every row's status matches and the citation actually points at
   the planted evidence, not a vague restatement. Pay special attention to:
   - Mode A: does it catch the hallucinated code snippet in `pr_body.md` that
     never appears in `pr.diff`?
   - Mode C: does it catch the specific wrong number (500 vs. spec's 200), not
     just "there's a length check"?
   - Mode D: does it flag both the missing filter behavior and the two
     unrequested features, quoting the ticket's own "do not add" line?

## Testing the loop itself

The fixtures above test whether a single Mode D pass reasons correctly once
triggered. They don't test whether the skill actually self-triggers at a
checkpoint without being asked, since that's a behavior over time, not a
gradable single answer. To check that separately: run a multi-step build with
the skill loaded, don't ask for a drift check at all, and confirm it fires on
its own at one of the checkpoints in the README's "The loop" section (after a
subtask, before a completion claim, around the 10-15 turn mark). If it stays
silent through an obvious checkpoint, that's a regression in the "The loop"
section of `SKILL.md`, not in Mode D's reasoning itself.

## Adding a new fixture

Plant at least one of each failure class so a run can't pass by rubber-stamping:
- something genuinely met
- something not met
- something partial (works on the happy path, not a named edge case)
- a false or hallucinated claim in the description or source narrative
- (Mode D only) invented scope the source explicitly didn't ask for

Write the `answer-key.md` before running the skill against it, so grading stays
independent of whatever the skill happens to output.
