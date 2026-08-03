from pathlib import Path

from agentic_tools.features.export.gemini_gem import (
    GEMINI_GEM_LIMITS,
    render_bundle,
    render_bundle_map,
    render_instructions,
    render_readme,
    write_export,
)
from agentic_tools.features.export.models import Bundle, ExportPlan, SkillDocument


def skill(
    name: str = "ref-xx-demo-topic", description: str = "", body: str = "Body."
) -> SkillDocument:
    return SkillDocument(
        name=name,
        domain="demo",
        visibility="public",
        description=description,
        body=body,
    )


def plan_with(*skills: SkillDocument, notices: tuple[str, ...] = ()) -> ExportPlan:
    return ExportPlan(
        bundles=(Bundle(name="demo", skills=skills),), excluded={}, notices=notices
    )


def test_gem_limits_match_the_documented_ceilings() -> None:
    assert GEMINI_GEM_LIMITS.max_files == 10
    assert GEMINI_GEM_LIMITS.max_file_bytes == 100 * 1024 * 1024


def test_render_bundle_keeps_each_skill_identifiable() -> None:
    rendered = render_bundle(
        Bundle(
            name="demo", skills=(skill(description="Does a thing. Use when: asked."),)
        )
    )

    assert "# ref-xx-demo-topic" in rendered
    assert "When this applies" in rendered
    assert "Body." in rendered


def test_render_bundle_omits_the_context_line_without_a_description() -> None:
    rendered = render_bundle(Bundle(name="demo", skills=(skill(),)))

    assert "When this applies" not in rendered
    assert "# ref-xx-demo-topic" in rendered


def test_bundle_map_uses_the_use_when_clause() -> None:
    rendered = render_bundle_map(
        plan_with(
            skill(description="Explains things. Use when: a page feels cluttered.")
        )
    )

    assert "a page feels cluttered." in rendered
    assert "Explains things" not in rendered


def test_bundle_map_falls_back_to_the_whole_description() -> None:
    rendered = render_bundle_map(
        plan_with(skill(description="No trigger clause here."))
    )

    assert "No trigger clause here." in rendered


def test_bundle_map_truncates_a_very_long_trigger() -> None:
    rendered = render_bundle_map(
        plan_with(skill(description="Use when: " + "word " * 200))
    )

    assert "…" in rendered


def test_render_instructions_replaces_the_placeholder() -> None:
    rendered = render_instructions(plan_with(skill()), "Header\n\n{{BUNDLE_MAP}}\n")

    assert "{{BUNDLE_MAP}}" not in rendered
    assert "demo.md" in rendered


def test_render_instructions_appends_routing_when_no_placeholder() -> None:
    rendered = render_instructions(plan_with(skill()), "Header only.")

    assert rendered.startswith("Header only.")
    assert "Knowledge files" in rendered
    assert "demo.md" in rendered


def test_readme_reports_notices_and_exclusions() -> None:
    plan = ExportPlan(
        bundles=(Bundle(name="demo", skills=(skill(),)),),
        excluded={"ref-xx-other-topic": "needs a terminal"},
        notices=("merged two bundles",),
    )

    rendered = render_readme(plan, Path("out"))

    assert "merged two bundles" in rendered
    assert "needs a terminal" in rendered
    assert "ref-xx-other-topic" in rendered


def test_write_export_produces_knowledge_instructions_and_readme(
    tmp_path: Path,
) -> None:
    written = write_export(plan_with(skill()), tmp_path, "Template {{BUNDLE_MAP}}")

    names = sorted(path.name for path in written)
    assert names == ["README.md", "demo.md", "instructions.md"]
    assert (
        (tmp_path / "demo.md")
        .read_text(encoding="utf-8")
        .startswith("# demo knowledge")
    )
    assert "demo.md" in (tmp_path / "instructions.md").read_text(encoding="utf-8")
