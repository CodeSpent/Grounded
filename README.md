# Grounded

*HAL never failed a self-diagnostic.*

An agent grading its own work has the same problem: it's the one insisting
everything's fine, right up until it isn't. Grounded is the outside check HAL
never had. It pulls up the diff, opens the ticket, checks the flag state
itself, built into a GitHub Copilot CLI skill.

## Before / after

**Without Grounded**, an agent asked "does this PR satisfy the ticket?" reads
its own PR description, agrees with itself, and reports back "yes, fully
compliant."

**With Grounded**, the same question gets answered like this:

| Criterion | Status | Evidence | Source |
|---|---|---|---|
| Hide tax row at 0% | Not met | No `taxRate === 0` guard anywhere in the diff | `pr.diff` |
| Works for USD, EUR, GBP | Not met | Ternary only checks `USD`/`EUR`; GBP falls through | `pr.diff` |
| Unit tests for 0% case | Not met | Diff touches only `CheckoutSummary.jsx`, no test file added | `pr.diff` |
| PR description's guard clause example | Flagged as false | Snippet in the description does not appear anywhere in the diff | `pr_body.md` vs `pr.diff` |

No citation, no pass. A status with no evidence gets marked unverifiable, not
approved.

## What it does

One skill, four modes. It infers which one you need from what you ask.

| Mode | You ask | It checks against | You get |
|---|---|---|---|
| **AC Compliance** | "Does this PR satisfy AR-1234?" | The Jira ticket's AC/DoD vs. the actual `gh pr diff` | Per-criterion evidence table, verdict: compliant / gaps / send back |
| **Release Risk Assessment** | "Risk-assess the 4.12 release" | Every ticket in the release, live LaunchDarkly flag state, migration/dependency diffs | The standard 14-item risk template, written back to the ticket's Risk Documentation field |
| **Mid-build Drift Check** | Nothing. It self-triggers (see below) | The original ticket/spec, re-read fresh, vs. the change so far | What's missing, what's invented scope creep, called out in both directions |
| **Ad hoc Grounded Check** | "Does this endpoint actually match the spec?" | Whatever external source you name: spec, schema, contract, style guide | Same evidence table, no source named means it asks instead of guessing |

## The loop

This is not a one-shot check. Once the skill is active, it keeps re-grounding
itself for the rest of the build, not just for the single request that loaded
it. It self-invokes a Mid-build Drift Check at these checkpoints, unprompted:

| Checkpoint | Why |
|---|---|
| After finishing each subtask in a multi-step plan | Catch drift before the next subtask builds on top of it |
| Before stating any completion claim ("this covers all cases", "done", "low risk") | The claim gets grounded before it gets said, not after |
| Every 10-15 tool-call turns on a long build | Drift compounds quietly; a fixed cadence catches it early |
| Right after a context compaction/summarization event | This is exactly when memory of the original ask degrades |
| Right before opening a PR or handing work back | Last chance to catch it while it's still cheap to fix |

A clean checkpoint gets a one-line "still on track" and the build keeps moving.
A dirty one stops the build and reports what's missing and what's invented,
before another turn is spent on top of it.

## Why this exists

Self-critique doesn't work. If an agent missed something while writing the
code, it has no new information to catch that gap while grading its own work.
Grounded refuses to answer from memory. It goes and looks: the real diff, the
real ticket, the real flag state, the real test output. A claim in a PR
description or a status update is a claim to verify, not evidence.

It also runs mid-build, on a loop, not just at PR time. On long sessions,
context drifts: early instructions get deprioritized, scope quietly expands,
requirements quietly get dropped. Catching that on turn 40 is cheap. Catching
it after the PR is open is not, and waiting for someone to remember to ask is
the same failure mode with extra steps.

## Install

```bash
ln -s $(pwd)/.copilot/skills/grounded ~/.copilot/skills/grounded
```

Restart the Copilot CLI (skills are scanned at process start), then run
`/skills` to confirm `grounded` is listed.

## Quickstart

```text
"Does PR #501 actually satisfy AR-25193's acceptance criteria?"
→ Mode A, pulls the ticket + diff, returns an evidence table and a verdict.

"We're 40 turns into building the export feature, are we still on track?"
→ Mode D, re-reads the ticket fresh, flags drift in either direction. It would
  have already fired on its own at the last checkpoint even without asking.

"Risk-assess the 4.12 release before go-live."
→ Mode B, walks every ticket + flag in the release, fills the risk template.

"Does the comments endpoint actually enforce the 200-char limit from the spec?"
→ Mode C, names the spec as the grounding source, checks the real code path.
```

If the mode is ambiguous or no grounding source can be named, it asks instead
of guessing.

## Requirements

- `gh` (GitHub CLI) and `jira` (jira-cli, ankitpokhrel), authenticated.
- `$LAUNCHDARKLY_API_TOKEN` set for release risk assessments that touch flags.
- A high-capability model for the verdict/synthesis steps. Mechanical data
  pulls (one `jira issue view`, one `gh pr diff`) can run on a cheap model. The
  judgment can't. See the skill's "Model requirement" section.

## Testing this skill

Before trusting this on real tickets and PRs, run it against the mocked
scenarios in [`tests/`](tests/README.md). Each fixture set has a known answer
key with deliberately planted gaps: a missing requirement, a wrong limit, a
fabricated claim, invented scope. A correct run has to catch every one of them
on its own, not by reading the answer key. Re-run these after any edit to
`SKILL.md`, and point new engineers at them before they trust this skill's
verdicts.

## Maintaining this

- The Evidence Table format (`Criterion | Status | Evidence | Source`) is the
  one convention every mode shares. Don't let a new mode skip it.
- If Nextech's Jira custom field IDs change (`customfield_12982` for Risk
  Documentation), update the "Writing the result back to Jira" section. These
  IDs are per-instance, not portable across Jira Cloud sites.
- This skill is intentionally self-contained. It should never assume another
  skill has already run.
