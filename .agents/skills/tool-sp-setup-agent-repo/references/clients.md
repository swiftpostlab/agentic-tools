# Client Wiring Matrix

How each agent client reaches the repo's `AGENTS.md`, and what extra wiring it needs. Only wire
clients the repo shows traces of, or that the user names.

**Verification status.** The paths and settings keys below were checked against provider docs on
**2026-08-02**. Client surfaces move. Before asserting a key or path to the user, re-check it if the
row says so, or if the repo's client is on a much newer version than the audit assumes.

---

## Reads `AGENTS.md` natively

These need no bridge file. Do not create one.

| Client | Notes |
| --- | --- |
| GitHub Copilot (CLI, coding agent, VS Code) | Reads root `AGENTS.md`. In VS Code it is gated on a setting — see below. |
| Cursor | Root `AGENTS.md` is documented as an alternative to `.cursor/rules`; nested files supported. |
| OpenAI Codex | Reads `AGENTS.md`, including a user-level `~/.codex/AGENTS.md`. |
| Others in the ecosystem (Jules, Aider, Zed, Warp, Devin, …) | The standard is stewarded by the Agentic AI Foundation with 25+ agents supporting it. Assume support, verify if it matters. |

## Needs a bridge

| Client | File | Bridge |
| --- | --- | --- |
| Claude Code | `CLAUDE.md` or `.claude/CLAUDE.md` | `@AGENTS.md` import, or a `CLAUDE.md -> AGENTS.md` symlink. Claude's own docs recommend exactly this. Prefer the import on Windows. |
| Google Gemini CLI | `GEMINI.md` | Thin file importing `AGENTS.md`. Gemini concatenates its hierarchical context (global → project → component); the filename is configurable, so a repo that changed it needs the bridge under the configured name. |
| Cursor (rules-based repos) | `.cursor/rules/*.mdc` | Only if the repo already invested in `.mdc` rules. Otherwise use `AGENTS.md` and skip the rules directory. |

`.claude/CLAUDE.md` and root `CLAUDE.md` are both read; a repo needs one, not both. Root is the
simpler default. When the repo already has one in `.claude/`, leave it there and bridge with
`@../AGENTS.md`.

## Per-client extra wiring

### Claude Code

1. **Skills symlink** (`C2`). Claude looks for skills under `.claude/skills`. Point it at the
   canonical root instead of copying:

   ```bash
   ln -s ../.agents/skills <repo>/.claude/skills
   ```

2. **Ignore the link**, so the symlink is a local wiring detail rather than a committed artifact:

   ```gitignore
   # <repo>/.claude/.gitignore
   # Ignore .claude/skills, it just symlinks .agents/skills
   skills
   ```

   On Windows, a directory symlink needs Administrator rights or Developer Mode; a directory
   junction is the fallback.

3. **Settings** (`.claude/settings.json`) carry permissions and deny rules, not instructions. Leave
   instruction content out of them.

### GitHub Copilot / VS Code

Copilot reads `AGENTS.md` natively, so `.github/copilot-instructions.md` should be a bridge or
absent — never a parallel body.

VS Code gates the feature on settings (verified 2026-08-02):

| Setting | Effect |
| --- | --- |
| `chat.useAgentsMdFile` | Enables root `AGENTS.md`. This is `C3`. |
| `chat.useNestedAgentsMdFiles` | Enables per-subfolder `AGENTS.md` (experimental); useful in monorepos. |
| `chat.useClaudeMdFile` | Enables `CLAUDE.md` detection. Leave off when the bridge already routes to `AGENTS.md` — enabling both loads the same guidance twice. |
| `chat.instructionsFilesLocations` | Where `.instructions.md` files are discovered. |

```jsonc
// <repo>/.vscode/settings.json
{
  "chat.useAgentsMdFile": true
}
```

Instruction precedence in Copilot is personal > repository > organization, so a personal instruction
file can override the repo's `AGENTS.md`. Worth saying out loud when a user reports the repo rules
being ignored.

### Google Gemini CLI

`GEMINI.md` is the bridge. The context filename is configurable in Gemini's settings, and the
effective context can be inspected with `/memory show` and reloaded with `/memory reload` — the
fastest way to prove the bridge actually loaded.

Gemini also honours `.aiexclude` for file exclusions. That is policy, not instructions; keep it out
of the bridge.

### Hermes (Nous)

No repo-level bridge file to create. Hermes auto-injects `.hermes.md`, `AGENTS.md`, `CLAUDE.md`, and
`.cursorrules` when present, each truncated to `context_file_max_chars` (default 20,000). So a
repo's existing `AGENTS.md` already reaches Hermes.

Two consequences: a very long `AGENTS.md` gets silently cut, and the user-level surface is
`~/.hermes/SOUL.md` — an identity file, so durable personal voice goes there rather than into a
one-line bridge.

### OpenClaw

Workspace-centric rather than repo-centric. Its `AGENTS.md` lives in the agent workspace (default
`~/.openclaw/workspace`, set by `agents.defaults.workspace` in `~/.openclaw/openclaw.json`) and is
injected at session start, alongside `SOUL.md`, `USER.md`, `IDENTITY.md`, and an optional
`MEMORY.md`.

Relevant config keys: `agents.defaults.repoRoot` (auto-detected by walking up from the workspace when
unset), `agents.defaults.skills` and `agents.entries.*.skills` (skill allowlists — the per-agent list
**replaces** the defaults rather than merging), and `agents.defaults.skipBootstrap` to stop it
generating workspace files.

For a repo, this means: the repo's `AGENTS.md` is not automatically the one OpenClaw loads. Point
the workspace at the repo (`repoRoot`, `workspace`) or accept that OpenClaw runs off its own
workspace files. Confirm the current shape against OpenClaw's docs before wiring — this client has
been renamed before and its config has moved with it.

## A client not on this list

Do not guess a path. Guessing produces a file no agent reads, and the user finds out weeks later.

1. Look for repo-local traces first: a dotfolder, a vendor-named Markdown file, an entry in
   `.gitignore`, a mention in the README.
2. Check whether the client is in the `AGENTS.md` ecosystem (<https://agents.md/>). If it is, there
   is nothing to wire.
3. Otherwise read the client's current docs for its instruction file and, separately, its skills
   directory. They are usually different mechanisms.
4. Apply the same shape as every row above: **one body in `AGENTS.md`, a thin bridge in the vendor
   file, a symlink for the skills directory.**
5. Record what was verified and the date, so the next pass knows whether to re-check.
