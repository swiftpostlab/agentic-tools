# Remediation By Check

One section per check ID emitted by this skill's `./scripts/audit_agent_repo.py`. Apply in the order listed
here — later stages assume earlier ones. Every command uses `<repo>` for the audited repository
root.

---

## W1 — local agent workspaces missing

Create the three workspaces. They are a set: tasks without a playground pushes scratch files into
the source tree, and retro without tasks has nothing to reflect on.

```bash
mkdir -p <repo>/.agents/tasks <repo>/.agents/retro <repo>/.agents/playground
```

`.agents/tasks/` and `.agents/retro/` also want their lifecycle subfolders and, for tasks, a
`TODO.md`. Do not invent that structure here — `ref-sp-agents-local-tasks` and `ref-sp-agents-retro`
own it. Create the directories, then follow those skills if the repo wants them pre-seeded.

## W2 — workspaces not gitignored

Add the rules to the repo `.gitignore`, anchored to the root so a nested `agents/` folder elsewhere
is unaffected:

```gitignore
# Agent only dirs
/.agents/playground/
/.agents/tasks/
/.agents/retro/
```

These directories hold local, per-developer state. Committing them turns one agent's scratch notes
into everyone's merge conflicts.

To keep an empty directory present after cloning, commit a placeholder inside it:

```gitignore
# <repo>/.agents/playground/.gitignore
# Ignore everything
*
!.gitignore
```

That placeholder is the one file allowed to be tracked under a workspace.

## W3 — workspace content is committed

Real content under an ignored workspace means it was added before the rule, and `.gitignore` does
not retroactively untrack. Confirm with the user, then untrack without deleting the local copies:

```bash
git -C <repo> rm -r --cached .agents/tasks .agents/retro .agents/playground
```

Check what is being untracked first. If the repo has been treating `.agents/tasks/` as shared
project planning, untracking it destroys a workflow — surface that instead of running the command.

## S1 / S2 — skills root or core skills missing

Resolve `S4` first: how skills arrive determines how the missing ones get added.

The five core skills, and why each is core:

| Skill | Role |
| --- | --- |
| `ref-sp-agents-skills-authoring` | How to write and maintain a skill at all. |
| `ref-sp-agents-instructions-authoring` | The source-of-truth and bridge model this whole baseline rests on. |
| `tool-sp-maintain-skills` | The maintenance pass that keeps the catalog from rotting. |
| `ref-sp-agents-retro` | The reflection loop that feeds improvements back into skills. |
| `ref-sp-agents-local-tasks` | The `.agents/tasks/` workspace contract. |

## S3 — skills outside `.agents/skills`

Skills found as real directories under `.claude/skills/`, `.github/skills/`, or a bare `skills/`
are a fork of the canonical location, not an alternative to it. Consolidate:

1. Confirm with the user — this moves files they wrote.
2. `git mv` each skill directory into `.agents/skills/`.
3. Replace the old location with a symlink where the client needs one (see `C2` and
   `./clients.md`).
4. Grep the repo for the old path: instruction files, CI, and scripts may reference it.

A client-specific skills directory is fine as a *link*. It is a problem as a *copy*.

## S4 — choosing a distribution mode

Three ways a repo gets shared skills. Pick one per source repo and record the choice in
`AGENTS.md`.

### Vendored — copy with a reference

Copy the skill directory into `.agents/skills/` and keep the sharing metadata that records where it
came from. Best when the repo must be self-contained: no install step, works offline, survives the
source repo disappearing.

Cost: drift is invisible unless something checks for it. `ref-sp-agents-shareable-skills` owns the
vendoring rules and the drift check — a vendored skill is a **pure copy with no rename**, because
renaming severs identity and breaks drift detection.

### Synced — declared in `.agents/config.json`

```json
{
  "skills": {
    "sources": [
      {
        "from": "package:agentic-tools",
        "skills": ["ref-sp-agents-skills-authoring", "ref-sp-agents-local-tasks"]
      }
    ]
  }
}
```

Then run the source repo's skills CLI to materialize them as links. Best when the repo already
consumes the source as a dependency and wants updates to arrive with a re-pin.

Two failure modes worth knowing before they cost an hour:

- A `package:<name>` source reads the **installed** copy at the revision the lockfile pins — not a
  local checkout sitting next to it. A skill that exists only in unpushed commits is invisible.
- Sync removes dead links in the destination before relinking, so a rename in the source repo is a
  breaking change for every consumer that has not re-pinned.

### Marketplace plugin

The consumer adds the marketplace once and installs the plugin:

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install <plugin>@<marketplace>     # marketplace NAME, not repo
copilot plugin marketplace add <owner>/<repo>    # same catalog, Copilot CLI
```

Best for skills that should be available across *all* of a user's repos rather than committed into
one. The skills then live in the client's plugin cache, so a repo-local audit will not see them —
say so in the report rather than flagging them missing.

`ref-sp-agents-plugin-marketplaces` owns the publishing side and the cache/symlink rules.

## I1 — `AGENTS.md` missing or thin

Use this skill's `./assets/agents-md-outline.md`. Fill it from the repo's real commands and structure — an
`AGENTS.md` listing commands that do not exist is worse than none, because the agent will run them.

Order of work: personality block, always-on rules, verification stance, workflow, quick commands,
skill catalog with one routing line per skill.

## I2 — provider files duplicating `AGENTS.md`

For each flagged file: merge, bridge, verify. The merge is the part that needs judgement — the
provider file usually holds a mix of guidance that belongs in `AGENTS.md`, detail that belongs in a
skill, and stale text that belongs nowhere.

Bridge forms:

```markdown
# Claude Instructions

@AGENTS.md
```

```bash
ln -s AGENTS.md <repo>/CLAUDE.md     # symlink alternative, POSIX
```

Prefer the stub. The symlink is POSIX-only in practice: Windows needs Administrator or Developer
Mode for a *file* symlink, and the junction fallback that rescues directory links does not apply to
files. A hard link works unprivileged but is not worth it — git stores it as an ordinary duplicate
file, so it does not survive a clone and silently drifts into a second source of truth. The stub is
one committed file that behaves identically on every platform.

A bridge stays under ~25 lines. Past that it is a second source of truth wearing a pointer.

## C1 / C2 / C3 — client wiring

See `./clients.md`. `C2` (the `.claude/skills` symlink) and `C3` (`chat.useAgentsMdFile`) are
documented there with the rest of the per-client matrix.

## R1 — stack markers

Markers are evidence, not a shopping list. Map them with the table in the parent `SKILL.md`, then
propose the subset the repo will actually use. Install them through the mode chosen in `S4`.
