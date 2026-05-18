# Package Management Checklist

Use this when reviewing a repo's version-management workflow.

- Confirm the repo has exactly one version source of truth.
- Confirm contributors are not expected to hand-edit multiple version-bearing files.
- Confirm derived manifests and any lockfiles that store the root version can be synced in one command.
- Confirm there is a drift check that fails normal validation when versions diverge.
- Confirm `CHANGELOG.md` exists at the repo root and has an `Unreleased` section.
- Confirm changelog entries summarize user-visible changes rather than raw implementation diffs.
- Confirm bump semantics are documented separately from package-sync mechanics when both concerns exist.
