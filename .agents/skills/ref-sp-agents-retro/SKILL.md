---
name: ref-sp-agents-retro
description: "Reference guidance for using `.agents/retro/` as a gitignored local workspace where an agent records a short, descriptive retrospective at the end of a substantial task: what went well, what went wrong and how each problem was solved or worked around, new information learned about the repo or tools, and improvement hypotheses a future agent can weigh when approaching similar work. Use when: finishing a substantial task and capturing a retro, recording how a problem was solved or worked around, noting new facts discovered about the repo or tooling, reading past retros before starting similar work to calibrate an approach, writing or naming a retro entry under `.agents/retro/`, triaging a captured retro from `10-new/` to `90-closed/`, setting its `status`, `created`, `updated`, or prose `outcome` frontmatter, or deciding whether a recurring retro observation should be promoted into a skill or instruction."
license: "MIT"
metadata:
  shareable-skills.owner-prefix: "sp"
  shareable-skills.owner: "swiftpostlabs/agentic-tools"
  shareable-skills.domain: "agents"
  shareable-skills.visibility: "public"
  shareable-skills.tags: "retro,reflection"
---

# Agents Retro

## Purpose

Define how this repo uses `.agents/retro/` as a gitignored local workspace for **retrospectives**: short, descriptive notes an agent writes at the end of a substantial task recording what went well, what went wrong, and hypotheses for doing it better next time.

A retro is **descriptive, not prescriptive**. It records what actually happened on one task and an honest read of why, so that a future agent reading accumulated retros can *calibrate its own approach* — not so it can follow a rule. A retro says "last time I did X this way and it cost two extra round-trips; a lighter path might be Y," not "always do Y." The future agent still exercises judgment; the retro is evidence, not instruction.

A retro carries two kinds of payload beyond sentiment, and both are what make it worth reading later:

- **How problems were handled.** When something went wrong, record whether and how it was solved or worked around — the actual fix, the workaround, or that it is still open. A future agent hitting the same wall benefits far more from "resolved by doing Z" than from "this was hard."
- **New information learned.** Facts discovered during the task — a repo constraint, a tool's real behavior, a non-obvious dependency, an environment quirk — that a future agent would otherwise have to rediscover. If such a fact is durable and general, it is also a promotion candidate.

This is a distinct layer from the other `.agents/` workspaces and from durable guidance:

- **`.agents/tasks/`** — active work state: what to do, what is in progress, what is done.
- **`.agents/playground/`** — scratch artifacts and throwaway helper scripts.
- **`.agents/retro/`** — reflective observations *after* work: what happened and why, to inform future approach.
- **Skills and instructions** — the durable, *prescriptive* layer. When a retro observation proves durable and general, it gets **promoted** into a skill or instruction; the retro itself stays descriptive.

Expect promotion to be common, not rare. `.agents/retro/` is a staging ground: many of the observations worth writing down are exactly the ones that should graduate into a skill or instruction, and the retro is where you notice that. Treat "does this belong in a skill?" as the default question at triage, not an exception — the retro captures the episode, and the durable lesson moves to where it will actually shape future behavior.

Treat `.agents/tasks/`, `.agents/playground/`, and `.agents/retro/` as the default local workspace set unless the current repo explicitly documents a different convention.

## When to use this skill

- Finishing a substantial task and capturing a retro under `.agents/retro/10-new/`.
- Reading past retros before starting similar work, to calibrate an approach.
- Writing or naming a retro entry.
- Triaging a captured retro — promoting or dismissing it and moving it from `10-new/` to `90-closed/`.
- Deciding whether a recurring retro observation should be promoted into a skill or instruction.

## Scope boundaries

This skill owns the **format and conventions** of `.agents/retro/`: the directory model, the `10-new/` → `90-closed/` lifecycle, entry naming, frontmatter fields, entry structure, and the descriptive-not-prescriptive stance.

- `ref-sp-agents-local-tasks` — the active-work workspace under `.agents/tasks/`. A retro is written *about* a task; it does not replace the task's closeout summary.
- `ref-sp-agents-skills-authoring` — how to promote a durable, general retro observation into a well-formed skill.
- `ref-sp-dev-repo-conventions` — where `.agents/retro/`, `.agents/tasks/`, and `.agents/playground/` sit in this repo's layout.
- The user's cross-session agent memory and any committed docs are out of scope. `.agents/retro/` is the local, gitignored reflection log only; durable lessons belong in committed skills or instructions, not here.

## Core Workflow

1. Before starting work that resembles something done before, scan both `.agents/retro/10-new/` and `.agents/retro/90-closed/` for relevant past entries and let them inform — not dictate — the approach.
2. Do the task.
3. When a substantial task finishes, decide whether it produced anything worth reflecting on. If it was a trivial, well-trodden chore with no surprises, skip the retro.
4. Write a retro entry at `.agents/retro/10-new/<YYYY-MM-DD-task-slug>.md` with `status: new`, `created`, `updated`, and a prose `outcome`, describing what went well, what went wrong and how each problem was solved or worked around, any new information learned about the repo or tooling, and improvement hypotheses. Keep it short and honest.
5. Anchor observations to specifics — the actual command, file, decision, round-trip, fix, or discovered fact — not vague sentiment. For each problem, record the resolution, the workaround, or that it is still open.
6. Triage the retro: if it carries durable, general observations, promote them into the owning skill or instruction (see `ref-sp-agents-skills-authoring`), note in the retro where they went, set `status: promoted`, bump `updated`, and move the file to `.agents/retro/90-closed/`. If nothing is worth acting on, set `status: dismissed` and move it to `90-closed/` as-is — it stays readable as calibration evidence.
7. Keep `10-new/` short: an untriaged pile there means triage is overdue, not that more retros are needed. Prune `90-closed/` retros that have been fully superseded by promoted guidance or that no longer reflect how the repo works.

## Directory Model

| Path | Role |
| --- | --- |
| `.agents/retro/` | Gitignored local log of task retrospectives. |
| `.agents/retro/10-new/<YYYY-MM-DD-task-slug>.md` | A captured retro whose observations have not yet been triaged (`status: new`). |
| `.agents/retro/90-closed/<YYYY-MM-DD-task-slug>.md` | A triaged retro whose observations were acted on or dismissed (`status: promoted \| dismissed`). |

Each retro is a single dated, slugged Markdown file that lives in exactly one lifecycle subfolder and moves from `10-new/` to `90-closed/` when it is triaged. Naming with the ISO date first keeps each subfolder chronologically ordered and greppable by topic slug.

The subfolder numbers match `.agents/tasks/` deliberately: **10 is intake, 90 is terminal** in both workspaces. Retro skips `20-` because it has no active stage — see the lifecycle section below — so the gap in the numbering is the point, not an oversight. `ref-sp-dev-projects-architecture` records where this fixed-width numeric-prefix convention comes from and why the width matters.

## Retro Lifecycle

A retro has just two states, and deliberately **no `20-open/`** — unlike a task, a retro is not worked over time. It is captured once, then triaged once (act on it or let it go), then closed. There is no in-progress middle state to model, which is why the `20-` slot stays empty.

| Subfolder | Meaning | Valid `status` values |
| --- | --- | --- |
| `10-new/` | Captured but not yet triaged — its improvement hypotheses and promotion candidates are still pending a decision. | `new` |
| `90-closed/` | Triaged and settled — no further action expected. | `promoted`, `dismissed` |

Two closure paths, both ending in `90-closed/`:

- **Promote, then close** (`status: promoted`) — the retro's durable, general observations were turned into a task, skill, or instruction change. The retro records where they went and moves to `90-closed/`.
- **Dismiss, then close** (`status: dismissed`) — the observations were episode-specific or not worth acting on. The retro moves to `90-closed/` as-is; it stays readable as calibration evidence even though nothing was promoted.

**Core invariant — the subfolder and the `status` must always agree.** A file in `10-new/` is `status: new`; a file in `90-closed/` is `status: promoted` or `status: dismissed`. Move the file and update `status` in the same step; never do one without the other. A retro is never left in `10-new/` indefinitely — an untriaged pile in `10-new/` is the signal to triage, not to keep writing more.

## Retro Entry Structure

Each entry starts with light frontmatter and then a few descriptive sections. Keep the whole thing short; a retro that takes longer to write than it saves a future agent is over-produced. Drop a section when it has nothing real to say — a task with no problems does not need an empty "Problems" heading.

```markdown
---
task: add-retro-skill
status: new              # retro lifecycle: new (in 10-new/) | promoted | dismissed (in 90-closed/)
created: 2026-07-24T18:22:41+02:00
updated: 2026-07-24T18:22:41+02:00
outcome: "Done, but the folder-numbering question was reopened mid-task and forced a rewrite of
  the directory tables — the skill shipped a day later than it needed to."
---

# Retro: add the retro skill

## Context

One or two sentences on what the task was and anything about the situation that
shaped how it went.

## What went well

- Concrete thing that worked, tied to the actual command/file/decision.

## Problems and how they were handled

- What went wrong, and — descriptively — why it happened, followed by whether and
  how it was resolved. Not "be more careful"; rather "assumed X was gitignored, it
  was not, which cost a re-run — resolved by adding it to `.gitignore` first."
- If a problem was worked around rather than fixed, say so and how. If it is still
  open, say that plainly and note what would settle it.

## What I learned

- New, non-obvious facts discovered during the task — a repo constraint, real tool
  behavior, an environment quirk, a dependency — that a future agent would otherwise
  rediscover. Mark durable, general facts as **promote →** `<owning-skill-or-instruction>`.

## Improvement hypotheses

- A *candidate* better approach for next time, stated as a hypothesis, not a rule.
- Mark anything durable and general as **promote →** `<owning-skill-or-instruction>`.

## Outcome

- How the task ended — done, partial, or abandoned — and, more importantly, *why*
  it ended that way. "Abandoned: the approach hit constraint X, so we chose to stop
  rather than force it." A partial or abandoned task is often the most useful retro;
  do not skip it because it "failed."
```

The frontmatter fields:

- `task` — short kebab-case slug identifying the task (matches the filename slug).
- `status` — the *retro's* lifecycle position, which must agree with its subfolder: `new` in `10-new/`; `promoted` or `dismissed` in `90-closed/`.
- `created` — ISO 8601 timestamp with offset, from `date -Iseconds`. Its date part matches the filename prefix.
- `updated` — same format, bumped on triage or any later edit.
- `outcome` — how the *task* ended, in **prose, not an enum**: one or two sentences covering done, partial, or abandoned, and why.

Note that `status` and `outcome` answer different questions and both are needed. `status` is the *retro's* lifecycle (has it been triaged?) and drives the directory invariant. `outcome` is the *task's* result, which is why a retro can be `status: dismissed` about a task that went badly, or `status: promoted` about one that went fine.

`outcome` is prose because the *motivation* behind how a task ended carries the signal and an enum cannot hold it — "abandoned: the approach hit constraint X, so we stopped rather than force it" is the sentence worth keeping, and `outcome: abandoned` throws it away. Keeping it in frontmatter makes it greppable across the directory without opening every file; keeping it prose preserves the reason. The body **Outcome** section stays, and carries the full reasoning: frontmatter is the one-glance summary, not the place for a long argument. YAML has no markdown rendering and is indentation-sensitive, so anything longer than a couple of sentences belongs in the body.

## Descriptive, Not Prescriptive

This is the property that makes a retro different from a skill, and it is easy to get wrong.

- **Describe the episode, not a directive.** "This time the type-check failed because Node 14 shadowed nvm" is a retro. "Always check the Node version first" is a rule — and if it is durable, it belongs in a skill, not the retro.
- **State improvement as a hypothesis.** "A lighter path might be Y" invites the next agent to evaluate Y in its own context. "Do Y" pretends one episode settled it.
- **Keep confidence honest.** One task is one data point. Say what you observed and how sure you are, not more.
- **Let the reader judge.** The value of a retro is that a future agent reads several and forms its own calibrated view. Prescription short-circuits that; it also rots, because a rule with no episode attached cannot be re-evaluated when the repo changes.

When an observation genuinely is a rule — durable, general, worth enforcing — that is a signal to **promote it**, not to write it prescriptively in the retro. The retro then notes the promotion and points at where the rule now lives.

## Decision Rules

- Treat `.agents/retro/` as local reflective state, not committed product documentation; it is gitignored like `.agents/tasks/` and `.agents/playground/`.
- Write a retro for substantial tasks — feature work, broad refactors, multi-file skill or instruction changes, anything with real decisions, friction, or surprises. Skip it for trivial, uneventful chores.
- Name each entry `<YYYY-MM-DD-task-slug>.md` and place it under `10-new/` on capture, so entries sort by date and are greppable by topic.
- Record the task's result as prose in the frontmatter `outcome`, and bump `updated` whenever the entry is edited or triaged.
- Use only two lifecycle states: `10-new/` for captured-but-untriaged retros and `90-closed/` for triaged ones. There is deliberately no `20-open/`; a retro is captured then triaged once, not worked over time.
- Keep the subfolder and `status` in sync: `10-new/` → `status: new`; `90-closed/` → `status: promoted` or `status: dismissed`. Move the file and update `status` in the same step.
- Close every retro one of two ways: promote its durable observations into a task, skill, or instruction (`status: promoted`), or dismiss it as episode-specific (`status: dismissed`). Either way it lands in `90-closed/` and stays readable.
- Do not let `10-new/` accumulate; a growing untriaged pile means triage is overdue.
- Keep entries descriptive: record what happened and why, and frame improvements as hypotheses the next agent can weigh — never as rules it must follow.
- For every problem recorded, capture the resolution: how it was solved, how it was worked around, or that it remains open and what would settle it. A future agent hitting the same wall benefits most from the fix, not the complaint.
- Record new, non-obvious information learned during the task — repo constraints, real tool behavior, environment quirks, dependencies — so a future agent does not rediscover it; promote the durable, general ones.
- Anchor every observation to a concrete command, file, decision, round-trip, fix, or discovered fact; drop vague "do better" sentiment.
- Write retros for partial and abandoned tasks too; a task that went wrong is usually the most informative one to reflect on.
- Before similar work, read relevant past retros to calibrate; do not treat them as authoritative instructions.
- When a retro observation is durable and general, promote it into the owning skill or instruction using `ref-sp-agents-skills-authoring`, and note the promotion in the retro instead of leaving a de facto rule buried in a reflection note.
- Do not duplicate the task's closeout summary here; the closeout (in `.agents/tasks/` or the user-facing answer) says what was done, the retro says how it went and how to do it better.
- Prune `90-closed/` retros that have been superseded by promoted guidance or no longer match how the repo works, so the directory stays a useful signal rather than a graveyard.

## Gotchas

- `.agents/retro/` is gitignored, so retros do not survive a fresh clone and are not visible to collaborators. Anything that must persist or be shared has to be promoted into committed skills or instructions.
- A prescriptive line hidden in a retro ("always X") is worse than useless: it carries the authority of a rule without the review a skill gets, and it cannot be re-evaluated later because the episode behind it is gone. Keep rules in skills; keep episodes in retros.
- One retro is one data point. Do not generalize from a single episode as if it were settled; that is what accumulation across entries is for.
- A retro is not a substitute for actually fixing durable guidance. If the same observation shows up across several retros, that is overdue promotion, not a fourth retro.
- Over-producing retros defeats the purpose. If writing the retro costs more than it will ever save a future agent, keep it to a few honest lines or skip it.

## Validation

- Each entry lives under `10-new/` or `90-closed/`, is named `<YYYY-MM-DD-task-slug>.md`, and has `task` plus the date part of `created` matching the filename.
- Each entry carries `created` and `updated` as ISO 8601 timestamps with offset, and `updated` was bumped on the last edit or triage.
- Each entry has a prose `outcome` in frontmatter and closes with an Outcome section stating how the task ended and, crucially, why. Neither is an enum standing in for the other.
- Each entry's `status` agrees with its subfolder: `new` in `10-new/`; `promoted` or `dismissed` in `90-closed/`. No retro sits in a subfolder its `status` contradicts.
- No retro is left untriaged in `10-new/` once its task is well behind you; `10-new/` is a short queue, not an archive.
- Entries read as descriptions of what happened plus hypotheses, not as prescriptive rules; any "always/never" rule has been promoted to a skill or instruction and referenced, not left in the retro.
- Each recorded problem states its resolution — how it was fixed or worked around, or that it is still open with what would settle it.
- New, non-obvious facts learned during the task are captured, and durable general ones are marked for promotion.
- Observations are anchored to concrete commands, files, decisions, fixes, or discovered facts rather than generic advice.
- Recurring observations across multiple retros have been promoted into durable guidance rather than re-recorded.
- The directory does not accumulate stale retros that contradict how the repo currently works.
