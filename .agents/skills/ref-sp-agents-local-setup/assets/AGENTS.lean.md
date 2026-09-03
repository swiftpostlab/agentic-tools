<!--
Template: a lean AGENTS.md for small local models.

Why this exists. A full AGENTS.md is written for a frontier model with a large
context budget and strong instruction-following. A local 4B to 14B model reads
the same file and does worse with it, for three reasons:

  1. Attention budget. Every rule competes with the actual task. Past roughly a
     dozen rules, a small model starts dropping them, and it drops them
     silently rather than telling you.
  2. Prefill cost. Instruction files are re-sent on every turn. On a machine
     doing 10 tokens/second, a 6,000-token instruction file is a tax paid per
     message, not once.
  3. Truncation. Some clients cap injected context files. Hermes truncates at
     context_file_max_chars, default 20,000 characters, and does it silently.

So: keep this file short, imperative, and concrete. Rules a small model can
check itself against, not principles it has to interpret. Target under 20,000
characters, and aim far below that.

How to use it. Copy to the repo root as AGENTS.md when the repo is driven
mainly by a local model, or to a separate path and point the local client at
that path when a full AGENTS.md already serves hosted agents.

Replace every <PLACEHOLDER>. Delete sections that do not apply. Delete this
comment block.
-->

# <PROJECT NAME>

<ONE SENTENCE: what this project is.>

## Commands

Run these exactly. Do not invent alternatives.

| Task | Command |
| --- | --- |
| Install dependencies | `<INSTALL COMMAND>` |
| Run tests | `<TEST COMMAND>` |
| Lint | `<LINT COMMAND>` |
| Type-check | `<TYPECHECK COMMAND>` |
| Build | `<BUILD COMMAND>` |

Before saying a change is done: run the test command and the lint command. If
either fails, fix it or say plainly that it failed.

## Where code goes

| What | Where |
| --- | --- |
| <APPLICATION CODE> | `<PATH>` |
| <TESTS> | `<PATH>` |
| <SCRIPTS> | `<PATH>` |

Put new files in the folder that matches. Do not create new top-level folders.

## Rules

1. Read a file before you edit it.
2. Change only what the task asks for. No drive-by refactors, renames, or
   reformatting.
3. Match the style of the surrounding code.
4. Do not add a dependency. If one seems necessary, stop and ask.
5. Do not read or print `.env`, key files, or credentials.
6. If the task is unclear, ask one specific question instead of guessing.
7. If you did not run a command, do not say you ran it.

## Style

- <LANGUAGE AND VERSION, e.g. "Python 3.14, type annotations on every function">
- <NAMING RULE, e.g. "snake_case for functions, PascalCase for classes">
- <TESTING RULE, e.g. "one test file per module, named <module>_test.py">
- <COMMENT RULE, e.g. "comment why, not what">

## Done means

- The change does what was asked, and nothing else.
- Tests pass.
- Lint and type-check pass.
- You said what you changed, in one or two sentences.

<!--
Trimming guidance, if this is still too long for the model in use:

  Keep      Commands, folder map, the numbered rules.
  Cut first Style detail, rationale, anything a linter already enforces.
  Cut next  The "Done means" list, down to one line.

A rule a linter enforces does not need to be in this file. The linter is
deterministic and free; the model's attention is neither.

Check the real cost rather than guessing:
  wc -c AGENTS.md          # against the client's truncation cap
  hermes prompt-size       # Hermes: what the fixed prompt actually costs
-->
