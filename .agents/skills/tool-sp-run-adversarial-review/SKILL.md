---
name: tool-sp-run-adversarial-review
description: "Run an adversarial review of a change: probe the repo, spawn a reviewer separated from the author, and verify the user-selected dimensions (skills consistency, code conformance and scope, security, end-to-end behavior). Use when: the user asks to adversarially review, independently verify, or red-team a change; wants a separate agent to review code, skills, security, or end-to-end behavior before accepting it; or wants a structured review pass over the current diff that does more than a self-check."
argument-hint: "Which dimensions to review (skills / code / security / e2e, or all), the change or diff under review, and any authorization for active security testing"
license: "MIT"
metadata:
  shareable-skills.owner-prefix: "sp"
  shareable-skills.owner: "swiftpostlabs/agentic-tools"
  shareable-skills.domain: "agents"
  shareable-skills.tags: "verification, security, testing, review"
  shareable-skills.visibility: "public"
  shareable-skills.requires: "ref-sp-agents-adversarial-review"
  shareable-skills.suggests: "ref-sp-dev-playwright-cli, ref-sp-agents-verification-discipline"
---

# Run Adversarial Review

## Purpose

Drive an adversarial review over a change: a reviewer **separated from the author** verifies the
dimensions the user selects, each gated on an objective oracle, and reports concrete findings. This is
the runnable recipe; the method, its preconditions, and the per-dimension depth live in
`ref-sp-agents-adversarial-review` (the `requires` dependency). Read that first, then follow these
steps.

## When to use this skill

- The user asks to adversarially review, independently verify, or red-team a change.
- The user wants a *separate* agent to review code, skills, security, or end-to-end behavior before a
  change is accepted.
- The user wants a structured review pass over the current diff that does more than a self-check.

## Scope boundaries

- `ref-sp-agents-adversarial-review` — the method this recipe executes (separation, oracle, dimensions,
  degradation, authorization gate). Do not restate it; consult it for the *why*.
- Claude Code's built-in `/code-review`, `/security-review`, `/verify` — a Claude-Code user already has
  these. This skill adds what they do not: portability across harnesses, the **skills** dimension, and
  an oracle- and authorization-gated pass that orchestrates dimensions with an explicitly separated
  reviewer. Prefer the built-ins for a quick single-dimension pass on Claude Code; use this for a
  portable, multi-dimension, separation-first review.
- `ref-sp-dev-playwright-cli` — the end-to-end dimension delegates browser smoke tests to it.
- `ref-sp-agents-verification-discipline` — the method the reviewer applies to its own findings.

## First step: read the method, then probe the repo

Do not assume the target repo's stack, conventions, or harness. Before reviewing:

1. **Read `ref-sp-agents-adversarial-review`** (required) for separation, the oracle precondition, and
   the authorization gate.
2. **Probe the harness** for the separation mechanism: native subagent/task tool, automated fan-out, or
   none. Pick the strongest available (see the method's provider-support reference). Detect it; do not
   hardcode a version.
3. **Probe the repo** for what each selected dimension needs:
   - Change surface — the diff under review (branch vs base, or working changes) and the **stated task
     scope**. Scope review has no oracle without a task statement; get it first.
   - Stack and shape — web app, CLI, library, or service; the package manager and test/lint/validate
     commands that actually exist here.
   - Conventions and skills — the repo's instruction files and its own skill catalog, including any
     **vendored/imported** skills (for the skills dimension).
   - Validators — the concrete commands this repo exposes (skill validators, linters, type-checkers,
     test runners). Use the repo's own commands; do not invent them.

## Choose dimensions

Confirm which dimensions to run (default to what the user named; if unspecified, ask). Each is
independent:

- **skills** — is the skill catalog internally consistent and consistent with vendored skills?
- **code** — does the change conform to the repo's skills/guidelines and stay within task scope?
- **security** — does the change introduce a breach; is it sound? (passive by default — see the gate)
- **e2e** — does the software actually work when run?

## Core workflow

For each selected dimension:

1. **Establish the oracle.** Name the objective source of truth for this dimension in this repo (its
   validators, guidelines, advisories, or runnable smoke behavior). If the oracle is weak or absent,
   record that — the verdict will be judgment, not fact.
2. **Spawn the separated reviewer.** Using the strongest mechanism the harness allows, start a reviewer
   in its own context and give it an **explicit opposed mandate**: "find what is wrong with this
   change; do not confirm it works." Never let the author's active context review its own work.
3. **Run the dimension's checks** (recipes below), using the repo's real commands.
4. **Collect concrete findings** — each with a file/location, what is wrong, the evidence, and a
   severity. Not a pass/fail stamp.
5. **Report** in the shape in `./references/report-template.md`, grouped by dimension, most severe
   first, with the oracle and its strength stated per dimension.

## Dimension recipes

Compact steps; depth is in the method skill's `references/dimensions.md`.

- **skills** — run the repo's skill validators on the touched skills (quality + sharing spec if it has
  one). Then, from the separated context, check cross-reference resolution, duplicated/contradictory
  guidance, and — in a consumer repo — whether local skills contradict, silently re-implement, or drift
  from the **vendored** skills they extend, and whether vendored copies were edited locally.
- **code** — get the diff and the task statement. Check conformance to the repo's skills/guidelines
  (run its linters/type-checkers) and, critically, **scope**: flag unrelated edits, opportunistic
  refactors, formatting churn hiding behavior changes, and new dependencies the task did not call for.
- **security** — **passive by default**: static/design review of the diff, dependency-advisory check,
  secret scan (no credentials/keys/tokens added to source, logs, fixtures, or output), and check for
  weakened controls. **Active testing (pentest/fuzz a live target) only with recorded authorization**
  for a system the operator owns — otherwise stop and report passive findings plus the active test that
  would settle the question.
- **e2e** — run the software, do not just read its tests. Web: drive a real browser via
  `ref-sp-dev-playwright-cli` through the key smoke path the change touches, watching console/network.
  CLI: invoke the built entrypoint with representative and edge arguments; assert exit codes and output.
  Library/service: exercise the public surface or real endpoints through a minimal harness.

## Separation mechanics

- **Subagent-capable harness** (e.g. Claude Code, Gemini CLI, Copilot CLI, VS Code): spawn one reviewer
  subagent per dimension in its own context, each with the opposed mandate and its oracle. On Claude
  Code, the fan-out/grader automation may run them in parallel and loop against a rubric.
- **No subagent:** start a **fresh session with cleared context** and adopt the reviewer role there,
  human-mediated. Do not review from the author's active context.
- If no separation is possible at all, say the review could not be made adversarial rather than passing
  off a self-check as one.

## Security authorization gate

- Passive review (static, design, dependency, secret) is always in-scope.
- Active testing is permitted **only** against systems the operator **owns or is explicitly authorized
  to test**. Never launch it against third-party, shared-staging, or production targets without
  recorded authorization.
- When authorization is missing or unclear, **stop**, report passive findings, and name the active test
  that would settle the open question. Do not proceed on assumed permission.

## Gotchas

- **Do not skip the probe.** Guessing the repo's commands, stack, or conventions produces a review with
  no real oracle. Use the repo's own validators and runners.
- **Do not review from the author's context.** If the reviewer inherits the author's rationale, the
  separation is gone even though the topology looks right.
- **Do not present a weak-oracle verdict as fact.** Say "no issues found by these checks," not "secure"
  or "correct."
- **Do not expand the review's own scope** past the selected dimensions — the code dimension exists to
  catch exactly that; hold the review to it.
- **Do not run active security tests without authorization**, ever, regardless of how useful they'd be.

## Validation

- Confirm the reviewer ran in a context separated from the author (or the fresh-session fallback), not
  in-line self-review.
- Confirm each reported dimension names its oracle and the oracle's strength.
- Confirm the e2e dimension **ran** the software rather than reading its tests.
- Confirm no active security testing occurred without recorded authorization.
- Confirm findings are concrete (location + evidence + severity), not a bare pass/fail.

## References

- `ref-sp-agents-adversarial-review` — the method: separation, oracle, dimensions, provider support,
  authorization gate. Its `references/dimensions.md` and `references/provider-support.md` hold the depth.
- `./references/report-template.md` — the findings report shape this recipe emits.
- `ref-sp-dev-playwright-cli` — browser automation for the web end-to-end dimension.
- `ref-sp-agents-verification-discipline` — the same-agent verification the reviewer applies to its own
  findings before reporting them.
