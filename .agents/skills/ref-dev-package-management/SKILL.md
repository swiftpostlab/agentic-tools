---
name: ref-dev-package-management
description: "Portable package-management guidance for coordinating versions across multiple manifests, keeping changelogs current, and choosing one source of truth for release metadata. Use when: syncing package versions across pyproject.toml and package.json, defining a changelog workflow, or designing a release-management command for a multi-ecosystem repo."
metadata:
  agentic-tools-category: "dev"
  shareable-skills.visibility: "shareable"
  shareable-skills.requires: "ref-dev-semantic-versioning"
---

# Package Management

## Purpose

Provide portable defaults for keeping package metadata, version sources, changelogs, and release commands aligned when a repository spans more than one package-management surface.

## When to use this skill

- Designing or revising a repo's version-management workflow.
- Keeping `pyproject.toml`, `package.json`, lockfiles, and related metadata in sync.
- Choosing whether one manifest or a dedicated `VERSION` file should own the release version.
- Adding or reviewing changelog conventions.
- Defining a contributor-facing command for version bumps or release prep.

## Scope Boundaries

- Use `.agents/skills/ref-dev-semantic-versioning/SKILL.md` when deciding the meaning of a bump level or a dependency range.
- Use `.agents/skills/ref-py-commitizen/SKILL.md` when the release workflow specifically uses the Python `commitizen` package, `cz bump`, Commitizen version providers, or Commitizen-generated changelogs.
- Use this skill for workflow, source-of-truth, manifest-alignment, and changelog policy.

## Defaults

- Keep one version source of truth.
- In multi-manifest repos, prefer a dedicated `VERSION` file when neither ecosystem should dominate the other.
- If the repo already enforces conventional commits and one release tool can update every version-bearing surface consistently, prefer that tool over maintaining a second custom bump script.
- Sync derived manifests from that source of truth with one explicit command instead of hand-editing several files.
- Add a validation command so version drift fails fast in normal repo checks.
- Keep a root `CHANGELOG.md` with an `Unreleased` section and versioned release sections.
- Prefer generated changelog entries from commit history when commit discipline is enforced and the output quality is acceptable; treat manual curation as the exception, not the default.
- Update the changelog in the same change as the version bump or release-prep work.

## Task Framing

| Command or action | What | Why | When | Expected outcome |
| --- | --- | --- | --- | --- |
| Choose a version authority | Pick the one file or manifest that owns the project version. | Multiple editable version sources inevitably drift without a clear owner. | When the repo has more than one publishable or package-managed surface. | Every other version-bearing file is derived from one canonical value. |
| Sync derived metadata | Rewrite secondary manifests and lockfile metadata from the source of truth. | Manual multi-file edits create avoidable release errors. | When bumping, setting, or validating the repo version. | Version-bearing files agree across ecosystems. |
| Maintain the changelog | Keep `Unreleased` and released version sections current. | Version numbers alone do not explain what changed or why users should care. | When preparing a release or landing user-visible behavior changes. | The changelog explains the version history instead of merely recording numbers. |

## Core Rules

### Source of truth

- Choose exactly one authoritative version source.
- If the repo publishes through one ecosystem only, that manifest can usually be the source of truth.
- If the repo spans multiple ecosystems equally, a dedicated `VERSION` file is often simpler and more neutral.
- Do not ask contributors to hand-edit multiple version fields and trust memory to keep them aligned.

### Automation

- Provide one contributor-facing command for version changes.
- Support both exact version setting and routine stable bumps when the release workflow needs both.
- Prefer one release-prep command that updates the version and changelog together when the toolchain can do so reliably.
- Add a check command that fails when derived metadata drifts from the source of truth.
- Keep the sync logic deterministic and file-local; version management should not require network access.
- Keep fallback custom scripts only for the gaps the main release tool cannot cover.

### Manifest and lockfile alignment

- Sync every manifest that exposes the project version, not just the most visible one.
- If the repo commits lockfiles and they record the root package version, keep them aligned too.
- Remember that drift can hide in generated metadata, not only in top-level manifests.
- Keep package names and versions coherent across ecosystems when the repo is presenting one shared project.

### Changelog workflow

- Keep the changelog at the repo root as `CHANGELOG.md`.
- Start with an `Unreleased` section so pending changes have a stable place to accumulate.
- When cutting a release, move the relevant entries from `Unreleased` into a versioned section.
- Prefer generated release entries when the repository enforces conventional commits or an equivalent structured history.
- Prefer concise user-facing summaries over internal implementation noise.

## Gotchas

- A single bump command without a matching drift check still allows silent regressions later.
- Lockfiles may record the root package version even when dependencies did not change.
- A changelog that is updated only after release is usually already stale.
- Multi-ecosystem repos become confusing when one manifest version changes and another stays behind.

## Validation

- There is exactly one version source of truth or one unambiguous release tool that deterministically updates every version-bearing file.
- Contributors have one explicit command for version changes.
- Derived manifests and any relevant lockfiles stay synchronized.
- `CHANGELOG.md` exists, includes `Unreleased`, and reflects user-visible changes.
- The workflow states where semver decisions come from instead of mixing bump meaning with file-sync mechanics.

## References

- Read `.agents/skills/ref-dev-semantic-versioning/SKILL.md` for bump semantics and dependency-range guidance.
- Read `.agents/skills/ref-py-commitizen/SKILL.md` for Commitizen-specific release command and configuration guidance.
- Read `./references/checklist.md` for a quick package-management review pass.
