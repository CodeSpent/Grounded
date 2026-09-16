# Grounded

A GitHub Copilot CLI skill for verifying claims/changes against **real external
ground truth** instead of self-graded opinion. One skill, multiple inferred modes:

- **AC Compliance** — does a PR's actual diff satisfy its linked Jira ticket's
  Acceptance Criteria / DoD?
- **Release Risk Assessment** — release-wide risk table (the standard 14-item
  template), cross-referencing every included ticket, live LaunchDarkly flag
  state, and structural risk signals in the diff — written back to the Jira
  ticket's **Risk Documentation** field (`customfield_12982`) for future
  reference.
- **Mid-build Drift Check** — during a large multi-step feature build, re-reads
  the original ticket/spec fresh (not from conversation memory) and diffs it
  against the change so far in **both directions**: missing requirements and
  invented/hallucinated scope creep. Meant to be invoked partway through a
  build, not just at PR time, so drift is caught while still cheap to correct.
- **Ad hoc Grounded Check** — any other "does X actually satisfy Y" claim
  against a nameable external source.

## Why

Self-critique loops where a model grades its own output don't reliably work —
if it missed something while generating, there's no new information to catch
that gap while grading itself. This skill only produces a verdict when it's
backed by a citation to something external: a diff, a ticket, a test result, a
live flag state, a prior document. No citation, no PASS.

## Install

```bash
ln -s $(pwd)/.copilot/skills/grounded ~/.copilot/skills/grounded
```

Then restart the Copilot CLI (skills are scanned at process start) and run
`/skills` to confirm `grounded` is listed.

## Requirements

- `gh` (GitHub CLI), `jira` (jira-cli, ankitpokhrel), authenticated.
- `$LAUNCHDARKLY_API_TOKEN` set for release risk assessments that touch flags.
- A high-capability model for the actual verdict/synthesis steps — see the
  skill's "Model requirement" section.

## Maintaining this

- The Evidence Table format (`Criterion | Status | Evidence | Source`) is the
  one convention every mode shares — don't let a new mode skip it.
- If Nextech's Jira custom field IDs change (`customfield_12982` for Risk
  Documentation), update the "Writing the result back to Jira" section — these
  IDs are per-instance, not portable across Jira Cloud sites.
- This skill is intentionally self-contained: it should never assume another
  skill has already run.
