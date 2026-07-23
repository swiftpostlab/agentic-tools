---
name: ref-sp-agents-adversarial-review
description: "Reference for adversarial review: verifying a change with a reviewer that is structurally separated from the author, under an opposed find-fault mandate, gated on an objective oracle, across selectable dimensions (skills, code, security, end-to-end behavior). Use when: designing or running a review that a separate agent performs, deciding whether a change is safe to accept, checking code against a repo's own skills and scope, reviewing for introduced security risk, smoke-testing an app end-to-end, or reasoning about why self-review misses defects."
license: "MIT"
metadata:
  shareable-skills.owner-prefix: "sp"
  shareable-skills.owner: "swiftpostlabs/agentic-tools"
  shareable-skills.domain: "agents"
  shareable-skills.tags: "verification, security, testing, review"
  shareable-skills.visibility: "public"
  shareable-skills.suggests: "ref-sp-agents-verification-discipline, ref-sp-dev-playwright-cli"
---

# Adversarial Review

## Purpose

Define adversarial review as a portable method: a change is verified by a reviewer that is
**structurally separated** from the agent that produced it, holding an **opposed mandate** (find
fault, not confirm success), and every verdict is **gated on an objective oracle**. The method runs
across one or more selectable dimensions — skills consistency, code conformance and scope, security,
and end-to-end behavior — and degrades gracefully across agent harnesses.

This skill owns the **method and its preconditions**. The runnable step-by-step workflow lives in the
driver skill (`tool-sp-run-adversarial-review`); read this to understand *why* the pieces are shaped
the way they are, and consult it to actually run a pass.

## When to use this skill

- Designing or running a review that a separate agent (not the author) performs.
- Deciding whether a change is safe to accept, and what evidence that decision rests on.
- Reviewing code against a repo's own skills, guidelines, and stated task scope.
- Reviewing a change for introduced security risk, or deciding whether active testing is warranted.
- Smoke-testing an application end-to-end after a change.
- Reasoning about why an agent reviewing its own work misses defects.

## Scope boundaries

- `ref-sp-agents-verification-discipline` — the **same agent checking its own claims** against ground
  truth (two dials, enumerate/route/prune/abstain). Adversarial review is its *structural*
  complement: a **different** agent, fresh context, opposed mandate. They compose — the reviewer agent
  applies verification discipline internally; separation is what this skill adds. Do not restate the
  two-dials method here.
- `ref-sp-dev-playwright-cli` — how to drive a real browser from the terminal. The end-to-end
  dimension **delegates** browser smoke tests to it; this skill does not re-teach Playwright.
- `ref-sp-agents-skills-authoring` / `ref-sp-agents-shareable-skills` — what a good/shareable skill
  *is*. The skills dimension reviews a catalog against those bars; it does not redefine them.
- `ref-sp-agents-security` — the agent's own protected-file access policy. That is not this skill's
  security dimension, which reviews the **change under review** for introduced risk.
- `tool-sp-run-adversarial-review` — the guided recipe that executes this method against a repo.

## Separation is the mechanism

Adversarial review is not a checklist run in the same breath as the work. What makes it *adversarial*,
and what gives it its power, is that the reviewer **is not the author**:

- **Different agent, fresh context.** The reviewer does not carry the author's justifications,
  assumptions, or attachment to the approach.
- **Opposed mandate.** The author's implicit goal is to get the change accepted; the reviewer's
  explicit goal is to find what is wrong with it. The agent that wrote the code wants the code to
  pass; a separate agent asked to break it has no such incentive.
- **The failure it defeats** is self-preferential bias: an agent grading its own output rates it
  higher than an independent grader does. Same-context self-review inherits every blind spot that
  produced the defect.

If a "review" runs in the author's own context with a confirm-it-works framing, it is a checklist, not
adversarial review, and it will miss the class of defects that matter most. The separation is the
feature; preserve it even when the mechanism is weak (see Provider support).

## The oracle precondition

A review is only as trustworthy as the oracle its verdict rests on. An **oracle** is a source of truth
that is:

1. **objective** — it decides pass/fail without the reviewer's opinion,
2. **outside the changeset** — not something the change itself defines, and
3. **not editable by the agent doing the work** — the author cannot move the goalposts to pass.

Without such an oracle, review — and especially fan-out to many reviewers — does not verify anything;
it *amplifies* unverified output and launders it as checked. This is the central, well-founded
criticism of agent-at-scale migration: volume past a weak oracle produces confident, unreviewed work.

Name the oracle for each dimension **before** trusting its verdict:

| Dimension | Oracle | Strength |
| --- | --- | --- |
| skills | the repo's skill validators (structural) + cross-skill coherence (judgment) | strong for structure, judgment for coherence |
| code | the repo's own skills/guidelines + the stated task scope | partly objective, partly judgment |
| security | dependency advisories, secret scanners, static analysis; design review | weak; judgment-heavy |
| end-to-end | the app's actual smoke behavior when run | strong where the app is runnable |

When a dimension's oracle is weak or absent, say so and lower the confidence of the verdict rather
than presenting judgment as if it were a checked fact.

## The dimensions

Each dimension is a separable review the user may select. Depth per dimension is in
`./references/dimensions.md`; the always-needed shape:

- **Skills** — are the repo's skills internally consistent and consistent with each other, and (in a
  consumer repo) consistent with skills **vendored/imported** from an upstream source? Checks:
  validator conformance, cross-reference resolution, duplicated or contradictory guidance, and local
  skills that fight or silently diverge from the vendored ones they extend. Oracle: the repo's own
  skill validators plus coherence judgment.
- **Code** — does the change conform to the repo's guidelines and skills, and does it stay **within
  the task's scope**? Checks: guideline/skill conformance, scope creep (unrelated edits, opportunistic
  refactors, new dependencies the task did not call for), and drift from the stated intent. Oracle: the
  repo's own skills/guidelines and the task definition.
- **Security** — does the change introduce a breach, and is the implementation sound? Checks:
  introduced vulnerabilities, secret leakage, injection and authorization gaps, and risky new
  dependencies. **Default to static/design review plus dependency and secret scanning.** Active
  testing (pentesting, fuzzing a running target) is gated — see Security authorization gate.
- **End-to-end** — does the thing actually work when run? Web: drive a real browser through the key
  smoke paths (delegate to `ref-sp-dev-playwright-cli`) and watch for console/network errors. CLI:
  invoke the built entrypoint with representative arguments and assert exit codes and output.
  Library/service: exercise the public surface through a minimal harness. The reviewer **runs** the
  software; reading the tests is not the same as observing behavior.

## Provider support and graceful degradation

The separation primitive — spawn a reviewer in its own context that can run tools and report back — is
now available on the major agent harnesses, so the *core* of the method is portable. **Detect the
capability; do not assume a version.** Full mechanism map and the dated capability note are in
`./references/provider-support.md`.

- **Claude Code (primary target):** native subagents/Task tool for a separated reviewer, plus
  programmatic fan-out (dynamic workflows) and an automated grader loop for the heavier cases.
- **Gemini CLI, GitHub Copilot CLI, VS Code (Copilot):** a separated-context subagent reviewer is
  available; the *stance* is identical, but automated fan-out/grading is not — a human plays grader.
- **No-subagent fallback:** where a harness cannot spawn a reviewer, start a **fresh session with
  cleared context** and adopt the reviewer role there, human-mediated. Weaker, but it preserves the
  one thing that matters: the reviewer is not carrying the author's context.

The honest framing is *adversarial separation everywhere; Claude Code additionally automates fan-out
and grading.* Only the scale/automation layer is Claude-specific — not the separation itself.

## Security authorization gate

The security dimension is the one that can cause harm, so it carries a hard gate:

- **Default is passive:** static and design review, dependency-advisory checks, secret scanning, and
  reasoning about the diff. This is always in-scope.
- **Active testing** — running exploits, fuzzing, or pentesting against a live target — is permitted
  **only** against systems the operator **owns or is explicitly authorized to test**. Never launch
  active testing against third-party services, shared staging, or production without recorded
  authorization.
- When active testing would help but authorization is absent or unclear, **stop and say so**; report
  the passive findings and name what active test would settle the open question. Do not proceed on
  assumed permission.

## Defaults

- Separate the reviewer from the author before anything else; a same-context review is a checklist.
- Name the oracle before the verdict; mark weak-oracle dimensions as judgment, not fact.
- Review only the selected dimensions; do not silently expand scope (the code dimension exists to catch
  exactly that in the work under review — hold the review to the same standard).
- Prefer running the software over reading its tests for the end-to-end dimension.
- Default security to passive; gate active testing on explicit authorization.
- Report findings as concrete defects with the evidence that supports each, not as a pass/fail stamp.

## Evidence honesty

The most-cited public account of agents-at-scale review (the Bun Zig→Rust rewrite) is largely a single
vendor self-report, and its outcome numbers are contested. This skill carries the **reasoning**, which
stands on its own — separation defeats self-preferential bias; an oracle is a precondition — and not
the outcome claims. When you cite the method's provenance, cite the argument, not the numbers. This is
itself an application of verification discipline: match stated confidence to the evidence.

## Gotchas

- **A weak oracle makes review theater.** Fan-out multiplies unchecked output; more reviewers do not
  substitute for a real oracle. Fix the oracle before scaling the reviewers.
- **Separation collapses silently.** If the "reviewer" reads the author's context, its rationale, or
  its self-assessment, the independence is gone even though the topology looks right.
- **The reviewer can rubber-stamp.** An opposed mandate has to be stated to the reviewer explicitly
  ("find what is wrong with this"), or it drifts back to confirmation.
- **End-to-end that never runs the app proves nothing.** Passing unit tests and a green typecheck are
  the author's oracle, not the reviewer's; the reviewer observes real behavior.
- **Security judgment is not a security guarantee.** Absence of found issues under passive review is
  not proof of safety; report it as "no issues found by these checks," not "secure."
- **A green badge can be a skipped check.** A skipped test and a passing test produce the same green;
  confirm the oracle actually ran over the change — tests executed rather than filtered out, the
  validator actually covered the touched files — instead of trusting the color. This is the one check
  that cannot be delegated to the system under review.

## References

- `./references/dimensions.md` — per-dimension depth: what the reviewer checks, its oracle, what good
  looks like, and common failure modes.
- `./references/provider-support.md` — the harness capability map, the degradation ladder, capability
  detection, and the dated note on current subagent support with primary links.
- `ref-sp-agents-verification-discipline` — the same-agent verification method the reviewer applies
  internally; this skill adds the separation.
- `ref-sp-dev-playwright-cli` — browser automation the end-to-end dimension delegates to for web apps.
- `tool-sp-run-adversarial-review` — the guided recipe that runs this method against a repo.
