---
name: grounding
description: Verify a claim, change, or in-progress build against real external ground truth — a Jira ticket's AC/DoD, a PR/release diff, live LaunchDarkly flag state, CI/test results, a spec, or prior risk documentation — and produce a cited evidence table, never a self-graded opinion. Infers the right mode from context: single-story/PR acceptance-criteria compliance, whole-release risk assessment, a mid-build drift check during a large multi-step feature, or an ad hoc "does X actually satisfy Y" check. Use whenever asked to verify, audit, or risk-assess a change against something concrete, when a claim ("this covers all cases", "this is low risk") needs proof instead of trust, or periodically during a long feature build to catch scope drift/hallucinated requirements before they compound.
user-invocable: true
---

# Grounding

Grounding exists because self-graded verification doesn't work: an agent asked to
critique its own claim will often just rubber-stamp it, because if it missed something
while generating, it has no new information to catch that gap while grading itself.
The only verification worth trusting is checked against something **external** — a
diff, a ticket, a test result, a live flag state, a prior document — with **cited
evidence**, not a restated opinion.

This is a single self-contained skill: it gathers its own grounding sources directly
(via `gh`, `jira`, `git`, LaunchDarkly's REST API, etc.) and does not depend on, or
require, any other skill to function.

### Why this matters mid-build, not just post-hoc

On large, multi-step feature work, an agent's understanding of "what was asked" can
drift over the course of a long session — context gets summarized/compacted, early
instructions get deprioritized against more recent turns, and it's easy to quietly
invent scope that was never requested or drop a requirement that was. Waiting until
a PR is opened to check this means the drift already cost the full build. This skill
is also meant to be invoked **mid-build**, re-reading the original ticket/spec fresh
(not from conversation memory) and comparing it against the current state of the
change — see Mode D.

## Model requirement

Judgment steps here (classifying risk, tracing whether a diff actually satisfies a
requirement, writing the riskiest-item narrative) require a high-capability reasoning
model — do not run those steps on a cheap/fast model. Mechanical raw data pulls (a
single `jira issue view`, a single `gh pr diff`, a single LD flag lookup) can be
delegated to a cheap `task` sub-agent; the verdict itself cannot.

## Step 0 — Infer the mode from what's being asked

| Signal | Mode |
| --- | --- |
| A single PR/story + a Jira ticket with AC/DoD | **AC Compliance** |
| A release branch/tag, or "diff release X against Y" | **Release Risk Assessment** |
| Mid-flight on a large feature build — "are we still on track", a natural milestone, or a long session that has touched many files/turns | **Mid-build Drift Check** |
| Any other "does X actually satisfy/match/cover Y" claim with a nameable external source | **Ad hoc Grounded Check** |

If the mode is ambiguous, ask rather than guess — the grounding source and evidence
table shape differ per mode.

## Universal rule: the Evidence Table

Every mode ends in a table shaped like this. Never emit a status without a citation —
a status with no evidence is treated as `❓ Unverifiable`, not a pass.

| Criterion | Status | Evidence | Source |
| --- | --- | --- | --- |
| ... | ✅ Met / ❌ Not met / ⚠️ Partial / ❓ Unverifiable | file:line, test name, LD flag state, ticket field, etc. | which grounding source this came from |

- ✅ **Met** — cite the specific file/line/logic/flag-state that satisfies it.
- ❌ **Not met** — cite what's missing or what actually happens instead.
- ⚠️ **Partial** — works for the primary path but not an explicitly named edge case —
  name the edge case and why it's not covered.
- ❓ **Unverifiable** — no grounding source exists to check this; say so plainly rather
  than inferring a pass.

For any claim in the source material ("applies everywhere", "low risk", "fully
covered") — do not accept it. Independently re-derive it: grep for other consumers of
a shared component, re-check the live system state, re-read the actual diff. A
claim is a claim to verify, not evidence.

* * *

## Mode A — AC Compliance

Verifies a PR's actual diff against its linked Jira ticket's Acceptance Criteria and
Definition of Done — not the PR description's narrative of itself.

1. **Get the real diff**: `gh pr view <pr> --repo <owner/repo> --json title,body,files,additions,deletions` and `gh pr diff <pr> --repo <owner/repo>`. Read the full diff yourself — never take the PR description's snippets as ground truth for what the code does.
2. **Get the ticket**: extract the key from the PR title/branch/body (e.g. `copilot/ar-25193-...` → `AR-25193`), then `jira issue view <KEY> --plain`. Pull the AC, Constraints, DoD, and any Gherkin/scenario blocks verbatim — these are the bar, not the PR description.
3. **Build the Evidence Table** — one row per discrete AC/Constraint/DoD line. For each named edge case, mentally execute the actual code path line by line; a function name matching the requirement is not proof it works.
4. **Cross-check the description against the diff explicitly** as a separate finding: code snippets in the description that don't appear in the diff, "applies everywhere" claims not backed by grepping every other call site of the same shared component, scope claims broader/narrower than the ticket.
5. **Check DoD test requirements literally** — a new behavior in a different layer with zero test file does not inherit coverage from "tests exist for the underlying service."
6. **Verdict**: Compliant — approve / Compliant with minor gaps (list, non-blocking) / Not compliant — send back (quote the ticket's own wording for each blocking item).

## Mode B — Release Risk Assessment

Produces a release-wide risk table for a go-live review, cutting across potentially
dozens of tickets/repos — not a single-story check (use Mode A for that).

**Gather inputs first** (ask if not given): repo(s) in this release, the version and
its git tag/branch convention (discover via `git ls-remote`, don't guess), the prior
version to diff against, and the Jira project key(s) involved (a release can span
several prefixes).

1. **Resolve the ref range**: `git ls-remote --tags/--heads <repo>` to find the prior tag and new branch/tag; shallow-clone and confirm both refs resolve.
2. **Extract commits + ticket keys**: `git log --oneline <prior>..<new>` and `git log <prior>..<new> --format=%s | grep -oE '[A-Z]{2,5}-[0-9]+' | sort -u`.
3. **Structural risk signals** — grep the diff for migrations/SQL, dependency manifests, and config/feature-flag files; for each hit, `git show <ref>:<path>` and read it, don't just count files. For SQL, confirm additive/idempotent vs. destructive. For feature flags, diff the flag-definitions file for new constants, then grep the whole diff for where each is actually *checked* (not just declared), and check the flag-check helper's fail-open/fail-closed default.
4. **Cross-check live LaunchDarkly state** for every new/referenced flag — code showing a flag is checked only proves it's gate-able, not that it's safely off in prod right now:
   ```bash
   curl -s -H "Authorization: $LAUNCHDARKLY_API_TOKEN" "https://app.launchdarkly.com/api/v2/projects?limit=50" | jq -r '.items[] | "\(.key) - \(.name)"'
   curl -s -H "Authorization: $LAUNCHDARKLY_API_TOKEN" "https://app.launchdarkly.com/api/v2/flags/<ld-project-key>/<flag-key>" | jq '.environments.production | {on, fallthrough, offVariation, rules: (.rules | length), prerequisites}'
   ```
   Report on/off state, targeting rules vs. everyone, and flag any mismatch between the code's default and LD's `offVariation` as its own finding.
5. **Cross-reference every ticket key with Jira** (batch via `jira-cli`, don't narrate one-by-one):
   ```bash
   for k in <keys>; do
     out=$(jira issue view "$k" --raw 2>&1 | awk '/^[\[{]/{p=1} p')
     echo "$k | $(echo "$out" | jq -r '.fields.issuetype.name') | $(echo "$out" | jq -r '.fields.status.name') | $(echo "$out" | jq -r '.fields.summary')"
   done
   ```
   Flag any ticket not Done/Closed while its commits are already in the release diff.
6. **Classify feature-flag coverage per ticket**: flagged (name it) / flagged via parent epic / defect fix (excluded) / non-customer-facing / **not flagged** — call out anything not-flagged as losing the flip-a-flag rollback path.
7. **Identify the riskiest item** — score on PHI/PII/payment data touched, blast radius, whether the story is still open despite merged code, rework/churn, backward-incompatibility, non-flagged status. Write it up with the specific failure mode and concrete customer/business consequence, **and** the mitigations already present in the code (safe defaults, validation, PII stripping) — read the implementation, don't assume.
8. **If a prior release's risk assessment exists** (check the previous release ticket's Risk Documentation field, Step below), diff this release's findings against the prior mitigation plan and explicitly confirm whether each stated mitigation actually held (e.g. "prior release said flag X would stay off until Y — verify it still is").
9. **Compile the standard template** — a 3-column table `Item | <Project> | Talking Points`, in this exact row order:
   1. Risk review buddy? *(ask the user)*
   2. Sufficient technical coverage day after? *(ask the user)*
   3. Architecture/infrastructure changes complete in prod?
   4. Performance/resource utilization concerns?
   5. Any changes not feature flagged (aside from defect fixes)?
   6. Any slow data changes? (duration for enterprise customer)
   7. New dependencies installed in prod?
   8. Blocked by other deploys?
   9. New configuration values set in the pipeline or in prod?
   10. Any API/DB changes that are not backward-compatible?
   11. Any changes related to an upcoming seasonal launch?
   12. Worst thing that can happen to customers (riskiest item) — include the Step 7 write-up and its mitigations in Talking Points.
   13. Monitoring and rollback plan *(ask, but suggest a concrete path from what you found)*.
   14. Overall risk level (Low/Medium/High).

   Talking Points should read as spoken-register meeting notes, not a repeat of the raw finding.
10. Cite your evidence trail at the end (git ref range + commit/file counts, N Jira tickets across which projects, LD flags checked).

### Writing the result back to Jira (Risk Documentation)

Nextech Jira tickets carry a **Risk Documentation** field (`customfield_12982`,
string/text) for exactly this artifact — so risk assessments are addressable and
re-checkable later, not just posted in chat.

1. **Never write silently.** Show the compiled table to the user first and get explicit
   confirmation before writing to Jira.
2. Confirm the field is present on the target ticket/project (`customfield_12982` may
   not be on every project's screen scheme — check via `jira issue view <KEY> --raw | jq '.fields.customfield_12982'` existing, or ask if the write fails).
3. On confirmation, write it:
   ```bash
   jira issue edit <TICKET-KEY> --custom "Risk Documentation=<rendered table + narrative>" --no-input
   ```
4. If multiple tickets are covered by one release assessment, ask which ticket (usually
   the release/go-live ticket, not every individual story) should carry the
   documentation — don't assume.

## Mode D — Mid-build Drift Check

For long, multi-step feature builds, invoked partway through (not just at PR time) to
catch drift before it compounds across many more turns.

1. **Re-fetch the original grounding source fresh** — the Jira ticket, spec, or design
   doc — via `jira issue view <KEY> --plain` or the source doc, not from what's already
   in conversation context. Context can itself have drifted (summarized, compacted, or
   just imperfectly recalled over a long session) — treat the freshly-fetched source as
   the only ground truth, not your own running memory of "what we agreed."
2. **Get the actual current state of the change**: `git diff` / `git status` against
   the base branch, or list files touched so far this session.
3. **Check both directions**, not just one:
   - **Missing** — requirements in the source not yet reflected in the current change.
   - **Invented / scope creep** — code, abstractions, or behavior in the current change
     that was never asked for in the source (a common hallucination pattern: adding
     "nice to have" generalization, extra config options, or entire subsystems the
     ticket never mentioned). Name it explicitly and ask whether it's intentional
     scope expansion or drift to be cut.
4. **Evidence Table** as usual, but each row should be tagged `expected` (in source),
   `missing`, or `unrequested` so drift is visually distinct from incompleteness.
5. **Report early and plainly.** If drift is found, stop and flag it before continuing
   the build — don't quietly keep going on a diverged path. This mode's entire value is
   catching it while it's still cheap to correct, not after another dozen turns.

## Mode C — Ad hoc Grounded Check

For any other "does X satisfy Y" request with a nameable external source (a spec doc, a
schema, an API contract, a security finding, a style guide): identify the concrete
grounding source explicitly before generating anything, then apply the same Evidence
Table rule. If no concrete grounding source can be named, say so and ask for one rather
than defaulting to a self-graded opinion — that is exactly the failure mode this skill
exists to avoid.

## When not to use this skill

- Purely subjective/open-ended writing with no external criteria to check against —
  there's nothing to ground it in, so this just adds latency for no verification value.
- You already have the diff and ticket/spec in hand and just need the comparison logic
  — skip straight to the Evidence Table step of the relevant mode.
