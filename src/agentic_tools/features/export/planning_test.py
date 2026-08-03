import pytest

from agentic_tools.features.export.models import (
    Bundle,
    Selection,
    SkillDocument,
    TargetLimits,
)
from agentic_tools.features.export.planning import (
    build_plan,
    bundle_by_domain,
    enforce_limits,
    select_skills,
)

LIMITS = TargetLimits(
    max_files=10, max_file_bytes=100 * 1024 * 1024, soft_words_per_bundle=40_000
)


def skill(
    name: str, domain: str = "demo", visibility: str = "public", words: int = 10
) -> SkillDocument:
    return SkillDocument(
        name=name,
        domain=domain,
        visibility=visibility,
        description="",
        body=" ".join(["word"] * words),
    )


def test_select_skills_filters_by_visibility_and_records_the_reason() -> None:
    kept, dropped = select_skills(
        (skill("ref-xx-a-topic"), skill("ref-xx-b-topic", visibility="repo-local")),
        Selection(),
    )

    assert [document.name for document in kept] == ["ref-xx-a-topic"]
    assert dropped["ref-xx-b-topic"] == "visibility is repo-local"


def test_select_skills_filters_by_prefix() -> None:
    _, dropped = select_skills((skill("tool-xx-a-topic"),), Selection())

    assert "prefix tool- is not exported" in dropped["tool-xx-a-topic"]


def test_select_skills_honours_excluded_domains() -> None:
    _, dropped = select_skills(
        (skill("ref-xx-a-topic", domain="agents"),),
        Selection(excluded_domains=("agents",)),
    )

    assert dropped["ref-xx-a-topic"] == "domain agents is excluded"


def test_explicit_exclusion_reason_wins_over_category_rules() -> None:
    _, dropped = select_skills(
        (skill("ref-xx-a-topic"),),
        Selection(excluded_skills={"ref-xx-a-topic": "needs a terminal"}),
    )

    assert dropped["ref-xx-a-topic"] == "needs a terminal"


def test_named_skills_override_other_filters() -> None:
    kept, dropped = select_skills(
        (skill("tool-xx-a-topic", visibility="repo-local"), skill("ref-xx-b-topic")),
        Selection(included_skills=("tool-xx-a-topic",)),
    )

    assert [document.name for document in kept] == ["tool-xx-a-topic"]
    assert dropped["ref-xx-b-topic"] == "not in the requested skill list"


def test_bundle_by_domain_groups_and_orders_by_size() -> None:
    bundles = bundle_by_domain(
        (
            skill("ref-xx-a-topic", domain="small", words=5),
            skill("ref-xx-b-topic", domain="big", words=100),
            skill("ref-xx-c-topic", domain="big", words=100),
        )
    )

    assert [bundle.name for bundle in bundles] == ["big", "small"]
    assert len(bundles[0].skills) == 2


def test_enforce_limits_leaves_a_compliant_set_alone() -> None:
    bundles = bundle_by_domain((skill("ref-xx-a-topic"),))

    result, notices = enforce_limits(bundles, LIMITS)

    assert len(result) == 1
    assert notices == ()


def test_enforce_limits_merges_smallest_bundles_first() -> None:
    limits = TargetLimits(
        max_files=2, max_file_bytes=10**9, soft_words_per_bundle=10**6
    )
    bundles = bundle_by_domain(
        (
            skill("ref-xx-a-topic", domain="big", words=500),
            skill("ref-xx-b-topic", domain="mid", words=100),
            skill("ref-xx-c-topic", domain="tiny", words=5),
        )
    )

    result, notices = enforce_limits(bundles, limits)

    assert len(result) == 2
    # The large domain is untouched; the two smallest were combined.
    assert "big" in [bundle.name for bundle in result]
    assert any("merged" in notice for notice in notices)
    merged = next(bundle for bundle in result if bundle.name != "big")
    assert sorted(merged.domains) == ["mid", "tiny"]


def test_strict_mode_fails_instead_of_merging() -> None:
    limits = TargetLimits(
        max_files=1, max_file_bytes=10**9, soft_words_per_bundle=10**6
    )
    bundles = bundle_by_domain(
        (skill("ref-xx-a-topic", domain="one"), skill("ref-xx-b-topic", domain="two"))
    )

    with pytest.raises(ValueError, match="exceed the 1-file limit"):
        enforce_limits(bundles, limits, strict=True)


def test_oversized_bundle_is_split_on_whole_skills() -> None:
    limits = TargetLimits(max_files=10, max_file_bytes=200, soft_words_per_bundle=10**6)
    bundles = (
        Bundle(
            name="big",
            skills=(
                skill("ref-xx-a-topic", words=40),
                skill("ref-xx-b-topic", words=40),
            ),
        ),
    )

    result, notices = enforce_limits(bundles, limits)

    assert len(result) == 2
    assert any("split" in notice for notice in notices)
    assert all(len(bundle.skills) == 1 for bundle in result)


def test_a_single_skill_over_the_byte_limit_is_not_split_further() -> None:
    limits = TargetLimits(max_files=10, max_file_bytes=10, soft_words_per_bundle=10**6)
    bundles = (Bundle(name="big", skills=(skill("ref-xx-a-topic", words=100),)),)

    result, _ = enforce_limits(bundles, limits)

    assert len(result) == 1


def test_soft_word_guideline_warns_without_splitting() -> None:
    limits = TargetLimits(max_files=10, max_file_bytes=10**9, soft_words_per_bundle=50)
    bundles = bundle_by_domain((skill("ref-xx-a-topic", words=200),))

    result, notices = enforce_limits(bundles, limits)

    assert len(result) == 1
    assert any("above the" in notice for notice in notices)


def test_build_plan_reports_totals_and_exclusions() -> None:
    plan = build_plan(
        (skill("ref-xx-a-topic", words=10), skill("tool-xx-b-topic", words=10)),
        Selection(),
        LIMITS,
    )

    assert plan.skill_count == 1
    assert plan.word_count == 10
    assert "tool-xx-b-topic" in plan.excluded
