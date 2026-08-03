"""Choose which skills go out, and group them into files.

Bundling optimises for **retrieval coherence**, not for packing bytes. A
destination that retrieves over knowledge files scores a chunk against the
query, so a bundle mixing unrelated domains retrieves worse than a narrow one.
Domains are already a coherence judgement recorded in skill metadata, so they
are the grouping key.

The destination's limits are guardrails, not objectives. They are enforced when
they bind, loudly, and ignored the rest of the time.
"""

from agentic_tools.features.export.models import (
    Bundle,
    ExportPlan,
    Selection,
    SkillDocument,
    TargetLimits,
)


def select_skills(
    skills: tuple[SkillDocument, ...], selection: Selection
) -> tuple[tuple[SkillDocument, ...], dict[str, str]]:
    """Apply a request's filters, recording why each dropped skill was dropped."""
    kept: list[SkillDocument] = []
    dropped: dict[str, str] = {}

    for skill in skills:
        reason = _rejection_reason(skill, selection)
        if reason is None:
            kept.append(skill)
        else:
            dropped[skill.name] = reason

    return tuple(kept), dropped


def _rejection_reason(skill: SkillDocument, selection: Selection) -> str | None:
    if skill.name in selection.excluded_skills:
        return selection.excluded_skills[skill.name]

    # An explicit include list overrides every other filter: naming a skill is a
    # stronger signal than any category rule it happens to fall outside of.
    if selection.included_skills:
        if skill.name in selection.included_skills:
            return None
        return "not in the requested skill list"

    if selection.visibilities and skill.visibility not in selection.visibilities:
        return f"visibility is {skill.visibility}"
    if selection.prefixes and skill.prefix not in selection.prefixes:
        return f"prefix {skill.prefix} is not exported"
    if selection.domains and skill.domain not in selection.domains:
        return f"domain {skill.domain} is not in the requested domains"
    if skill.domain in selection.excluded_domains:
        return f"domain {skill.domain} is excluded"
    return None


def bundle_by_domain(skills: tuple[SkillDocument, ...]) -> tuple[Bundle, ...]:
    """Group skills into one bundle per domain, largest bundle first."""
    grouped: dict[str, list[SkillDocument]] = {}
    for skill in skills:
        grouped.setdefault(skill.domain, []).append(skill)

    bundles = tuple(
        Bundle(name=domain, skills=tuple(members))
        for domain, members in sorted(grouped.items())
    )
    return tuple(sorted(bundles, key=lambda bundle: bundle.word_count, reverse=True))


def enforce_limits(
    bundles: tuple[Bundle, ...], limits: TargetLimits, *, strict: bool = False
) -> tuple[tuple[Bundle, ...], tuple[str, ...]]:
    """Bring a bundle set inside the destination's hard limits.

    Over the file ceiling, the *smallest* bundles are merged first: they carry
    the least content, so mixing them costs the least retrieval quality. Merging
    into a large bundle would dilute the one people actually query.
    """
    notices: list[str] = []
    working = list(bundles)

    while len(working) > limits.max_files:
        if strict:
            raise ValueError(
                f"{len(working)} bundles exceed the {limits.max_files}-file limit "
                f"for this target: {', '.join(bundle.name for bundle in working)}"
            )
        working.sort(key=lambda bundle: bundle.word_count)
        first, second = working.pop(0), working.pop(0)
        merged = Bundle(
            name=f"{first.name}-{second.name}", skills=first.skills + second.skills
        )
        notices.append(
            f"merged '{first.name}' ({first.word_count} words) and '{second.name}' "
            f"({second.word_count} words) into '{merged.name}' to stay within the "
            f"{limits.max_files}-file limit"
        )
        working.append(merged)

    expanded: list[Bundle] = []
    for bundle in working:
        parts = _split_oversized(bundle, limits.max_file_bytes)
        if len(parts) > 1:
            notices.append(
                f"split '{bundle.name}' into {len(parts)} files to stay under "
                f"{limits.max_file_bytes} bytes per file"
            )
        expanded.extend(parts)

    for bundle in expanded:
        if bundle.word_count > limits.soft_words_per_bundle:
            notices.append(
                f"'{bundle.name}' is {bundle.word_count} words, above the "
                f"{limits.soft_words_per_bundle}-word guideline; retrieval may be "
                "noisier. Consider selecting fewer skills for this bundle."
            )

    ordered = tuple(
        sorted(expanded, key=lambda bundle: bundle.word_count, reverse=True)
    )
    return ordered, tuple(notices)


def _split_oversized(bundle: Bundle, max_bytes: int) -> tuple[Bundle, ...]:
    """Split a bundle by whole skills until every part fits.

    Skills are the natural sub-unit: splitting mid-skill would separate guidance
    from the reasoning that justifies it.
    """
    if _byte_size(bundle) <= max_bytes or len(bundle.skills) <= 1:
        return (bundle,)

    parts: list[Bundle] = []
    current: list[SkillDocument] = []
    for skill in bundle.skills:
        candidate = current + [skill]
        if current and _skills_byte_size(tuple(candidate)) > max_bytes:
            parts.append(
                Bundle(name=f"{bundle.name}-{len(parts) + 1}", skills=tuple(current))
            )
            current = [skill]
        else:
            current = candidate

    if current:
        parts.append(
            Bundle(name=f"{bundle.name}-{len(parts) + 1}", skills=tuple(current))
        )
    return tuple(parts)


def _byte_size(bundle: Bundle) -> int:
    return _skills_byte_size(bundle.skills)


def _skills_byte_size(skills: tuple[SkillDocument, ...]) -> int:
    return sum(len(skill.body.encode("utf-8")) for skill in skills)


def build_plan(
    skills: tuple[SkillDocument, ...],
    selection: Selection,
    limits: TargetLimits,
    *,
    strict: bool = False,
) -> ExportPlan:
    """Select, bundle, and fit an export without writing anything."""
    kept, excluded = select_skills(skills, selection)
    bundles, notices = enforce_limits(bundle_by_domain(kept), limits, strict=strict)
    return ExportPlan(bundles=bundles, excluded=excluded, notices=notices)
