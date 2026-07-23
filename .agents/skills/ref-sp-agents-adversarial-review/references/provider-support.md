# Provider Support and Graceful Degradation

How to run a **separated** reviewer across agent harnesses, and how to degrade when the strong
mechanism is missing. The rule is **detect the capability, do not hardcode a version** — harness
features move fast, and a pinned version claim in a portable skill goes stale. Load this when choosing
how to spawn the reviewer.

## What the method actually needs

The minimum viable mechanism is one thing: **spawn a reviewer in its own context that can run tools
and report findings back, without inheriting the author's context.** Everything else (parallel
fan-out, automated grading) is an optimization, not a requirement. So the portability question reduces
to: *can this harness spawn an isolated subagent?*

## Capability detection

Before running a pass, establish the mechanism available in the current harness, in order:

1. **Native subagent / task tool** — the harness can spawn an isolated agent that runs tools and
   returns a result. Use it: one reviewer per selected dimension, each told its opposed mandate and
   its oracle.
2. **Automated fan-out + grader** — the harness can also fan out many subagents programmatically and
   loop them against a rubric until they pass. Use it only when the volume justifies it; for a single
   change, one reviewer per dimension is enough.
3. **No subagent** — the harness cannot spawn a reviewer. Fall back to a **fresh session with cleared
   context**, human-mediated: the same operator opens a clean context and adopts the reviewer role
   there. Weaker, but it keeps the reviewer off the author's context, which is the load-bearing part.

Detect, don't assume: check the harness's current docs/commands rather than trusting this file's
snapshot below.

## Harness map (snapshot — verify against current docs)

As of **mid-2026**, the separation primitive is available on all four harnesses this repo targets; only
the fan-out/grader automation is Claude-Code-specific. Treat versions and dates as *verify-before-use*,
not as guarantees.

| Harness | Separated subagent reviewer | Automated fan-out + grader | Degradation |
| --- | --- | --- | --- |
| **Claude Code** (primary) | Yes — subagents / Task tool, isolated context | Yes — dynamic workflows + performance-outcome grader | none needed |
| **Gemini CLI** | Yes — subagents, own context window, own tools | No automated grader | human plays grader |
| **GitHub Copilot CLI** | Yes — `/fleet` and subagent delegation | No automated grader | human plays grader |
| **VS Code (Copilot)** | Yes — multi-agent orchestrator | No automated grader | human plays grader |
| **Any other / older** | Maybe not | No | fresh-session fallback |

Primary sources to re-check current support:

- Claude Code subagents — <https://code.claude.com/docs/en/sub-agents>
- Claude Code dynamic workflows — <https://code.claude.com/docs/en/workflows>
- Copilot CLI `/fleet` — <https://github.blog/ai-and-ml/github-copilot/run-multiple-agents-at-once-with-fleet-in-copilot-cli/>
- Gemini CLI subagents — the Gemini CLI documentation for the installed version

## Degradation ladder

From strongest to weakest, keep as much separation as the harness allows:

1. **Separated reviewer + automated grader** (Claude Code) — one subagent per dimension, each looped
   against its oracle until it either passes or reports concrete findings.
2. **Separated reviewer, human grader** (Gemini CLI, Copilot CLI, VS Code) — one subagent per
   dimension with an explicit opposed mandate; the human decides when findings are addressed.
3. **Fresh-session reviewer** (no subagent) — a clean context adopts the reviewer role; the human
   drives the handoff. Do not let the same active context that wrote the change also "review" it.
4. **Never: same-context self-review** — this is a checklist, not adversarial review. If nothing above
   is possible, say the review could not be made adversarial rather than presenting a self-check as one.

## What is genuinely Claude-Code-only

Only the **scale/automation layer**: programmatic fan-out of many subagents in one session and the
automated grader loop that revises subagents against a rubric. The separation *primitive* — the thing
that makes review adversarial — is portable. Design the skill around the primitive; treat the
automation as a Claude-Code accelerator, not a dependency.
