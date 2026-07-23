# Adversarial Review Report Template

The shape the driver emits after a pass. One block per selected dimension, findings most-severe first,
each dimension stating its oracle and that oracle's strength. Report concrete defects with evidence,
not a pass/fail stamp.

## Header

```md
# Adversarial review — <change / diff under review>

- Reviewer separation: <subagent per dimension | fresh-session fallback | NOT adversarial>
- Dimensions reviewed: <skills, code, security, e2e>
- Task scope (oracle for code/scope): <one-line statement, or "not provided">
```

## Per-dimension block

```md
## <dimension>

- Oracle: <the objective source of truth used> (strength: strong | partial | weak/absent)
- Verdict: <findings below | no issues found by these checks>

### Findings (most severe first)

1. [<severity: high|medium|low>] <file:line or location> — <what is wrong>
   - Evidence: <what shows it — validator output, command result, observed behavior, diff excerpt>
   - Fix direction: <the smallest change that addresses it>
```

## Rules for the report

- **State the oracle and its strength per dimension.** A weak/absent oracle downgrades every verdict
  under it to reviewed judgment; say so rather than implying it was checked.
- **"No issues found" is not "safe/correct."** For security especially, phrase a clean result as "no
  issues found by <these checks>," and name the residual unknowns.
- **Findings are concrete.** Location + what is wrong + the evidence that shows it + a fix direction.
  A finding with no evidence is an opinion; mark it as one or drop it.
- **Security authorization.** If active testing was withheld for lack of authorization, say so
  explicitly and list the active test that would settle each open question.
- **End-to-end evidence is observed behavior.** Cite what running the software produced (console,
  network, exit code, output), not that its unit tests passed.
- **Order by severity, then by dimension.** A high-severity security or correctness finding outranks a
  low-severity style note in another dimension.

## Example (abridged)

```md
# Adversarial review — feature/export-csv vs main

- Reviewer separation: subagent per dimension
- Dimensions reviewed: code, security, e2e
- Task scope: "add CSV export to the reports page; no other changes"

## code
- Oracle: repo lint/typecheck + task scope (strength: partial)
- Verdict: findings below
### Findings
1. [medium] src/reports/page.tsx:41 — unrelated refactor of the date filter, outside task scope
   - Evidence: diff touches filter logic the task did not mention; tests for it unchanged
   - Fix direction: revert the filter change; land it separately if wanted

## security
- Oracle: secret scan + dependency advisories + static review (strength: weak)
- Verdict: no issues found by these checks
- Residual unknown: CSV injection (formula-prefix) not exercised; active test withheld — no target auth

## e2e
- Oracle: browser smoke via playwright-cli (strength: strong)
- Verdict: findings below
### Findings
1. [high] /reports export button — download triggers a console error, no file produced
   - Evidence: ran the flow in a real browser; console shows TypeError; network shows 500 on /export
   - Fix direction: the export handler throws on empty result set — guard the empty case
```
