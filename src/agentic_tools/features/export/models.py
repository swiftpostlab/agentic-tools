"""Data shapes for skill exports.

An export is a *request*, not repository policy: "give me these skills, in this
shape, now". Nothing here is meant to be checked in, which is why the config is
loaded from an arbitrary path or assembled from flags rather than living in
`.agents/config.json`.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SkillDocument:
    """One discovered skill, flattened from `SKILL.md` plus its `references/`."""

    name: str
    domain: str
    visibility: str
    description: str
    body: str

    @property
    def prefix(self) -> str:
        """The role prefix (`ref-`, `tool-`) used for selection."""
        return f"{self.name.split('-', 1)[0]}-"

    @property
    def word_count(self) -> int:
        return len(self.body.split())


@dataclass(frozen=True)
class Selection:
    """Which skills a request wants.

    Empty tuples mean "no constraint on this axis". `excluded_skills` maps a
    skill name to the reason it was left out, so an exclusion stays reviewable
    instead of becoming folklore.
    """

    visibilities: tuple[str, ...] = ("public",)
    prefixes: tuple[str, ...] = ("ref-",)
    domains: tuple[str, ...] = ()
    excluded_domains: tuple[str, ...] = ()
    included_skills: tuple[str, ...] = ()
    excluded_skills: dict[str, str] = field(default_factory=dict[str, str])


@dataclass(frozen=True)
class TargetLimits:
    """Hard and soft ceilings imposed by the destination.

    `max_files` and `max_file_bytes` are enforced. `soft_words_per_bundle` only
    warns: splitting on it would trade retrieval coherence for a number nobody
    set, which is the wrong trade.
    """

    max_files: int
    max_file_bytes: int
    soft_words_per_bundle: int


@dataclass(frozen=True)
class ExportRequest:
    """A complete, self-contained export request."""

    target: str
    selection: Selection
    limits: TargetLimits
    skills_root: Path
    out_dir: Path
    instructions_template: Path | None = None
    strict: bool = False


@dataclass(frozen=True)
class Bundle:
    """One output file: a group of skills that belong together for retrieval."""

    name: str
    skills: tuple[SkillDocument, ...]

    @property
    def word_count(self) -> int:
        return sum(skill.word_count for skill in self.skills)

    @property
    def domains(self) -> tuple[str, ...]:
        seen: list[str] = []
        for skill in self.skills:
            if skill.domain not in seen:
                seen.append(skill.domain)
        return tuple(seen)


@dataclass(frozen=True)
class ExportPlan:
    """What an export would produce, before anything is written."""

    bundles: tuple[Bundle, ...]
    excluded: dict[str, str]
    notices: tuple[str, ...]

    @property
    def skill_count(self) -> int:
        return sum(len(bundle.skills) for bundle in self.bundles)

    @property
    def word_count(self) -> int:
        return sum(bundle.word_count for bundle in self.bundles)
