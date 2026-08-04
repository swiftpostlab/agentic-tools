"""Canonical blocks must reach an export as an exact copy.

A projection that rewrites its source is a fork, and a fork drifts silently:
the skill changes, the export keeps the old text, and nothing fails.
"""

from pathlib import Path

import pytest

from agentic_tools.features.export.config import (
    ExportConfigError,
    injections_from_config,
)
from agentic_tools.features.export.discovery import read_canonical_block
from agentic_tools.features.export.gemini_gem import render_instructions
from agentic_tools.features.export.models import Bundle, ExportPlan, SkillDocument

CANONICAL = "First paragraph of the canonical text.\n\nSecond paragraph."

SKILL_WITH_BLOCK = f"""---
name: ref-xx-persona-topic
---

# Persona

## Canonical persona text

Prose explaining that instruction files inline this verbatim.

```md
{CANONICAL}
```

Trailing prose that must not be captured.
"""


def write_skill(root: Path, name: str, text: str) -> Path:
    directory = root / name
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text(text, encoding="utf-8")
    return directory


def plan() -> ExportPlan:
    document = SkillDocument(
        name="ref-xx-demo-topic",
        domain="demo",
        visibility="public",
        description="",
        body="Body.",
    )
    return ExportPlan(
        bundles=(Bundle(name="demo", skills=(document,)),), excluded={}, notices=()
    )


def test_canonical_block_is_extracted_exactly(tmp_path: Path) -> None:
    directory = write_skill(tmp_path, "ref-xx-persona-topic", SKILL_WITH_BLOCK)

    assert read_canonical_block(directory) == CANONICAL


def test_extraction_stops_at_the_closing_fence(tmp_path: Path) -> None:
    directory = write_skill(tmp_path, "ref-xx-persona-topic", SKILL_WITH_BLOCK)

    block = read_canonical_block(directory)

    assert block is not None
    assert "Trailing prose" not in block
    assert "Prose explaining" not in block


def test_skill_without_a_canonical_block_returns_none(tmp_path: Path) -> None:
    directory = write_skill(
        tmp_path, "ref-xx-plain-topic", "---\nname: x\n---\n\n# Plain\n\nNo block.\n"
    )

    assert read_canonical_block(directory) is None


def test_a_fenced_block_under_another_heading_is_not_captured(tmp_path: Path) -> None:
    directory = write_skill(
        tmp_path,
        "ref-xx-plain-topic",
        "---\nname: x\n---\n\n## Examples\n\n```md\nnot canonical\n```\n",
    )

    assert read_canonical_block(directory) is None


def test_missing_skill_directory_returns_none(tmp_path: Path) -> None:
    assert read_canonical_block(tmp_path / "absent") is None


def test_injected_text_is_substituted_verbatim() -> None:
    rendered = render_instructions(
        plan(),
        "Before\n\n{{PERSONA}}\n\nAfter\n\n{{BUNDLE_MAP}}",
        {"PERSONA": CANONICAL},
    )

    assert CANONICAL in rendered
    assert "{{PERSONA}}" not in rendered


def test_multiple_placeholders_are_filled() -> None:
    rendered = render_instructions(
        plan(),
        "{{PERSONA}}\n---\n{{VERIFICATION}}\n{{BUNDLE_MAP}}",
        {"PERSONA": "persona text", "VERIFICATION": "verification text"},
    )

    assert "persona text" in rendered
    assert "verification text" in rendered


def test_rendering_without_injections_is_unchanged() -> None:
    rendered = render_instructions(plan(), "Just routing:\n\n{{BUNDLE_MAP}}")

    assert "demo.md" in rendered


def test_inject_config_maps_placeholders_to_skills() -> None:
    mapping = injections_from_config({"inject": {"PERSONA": "ref-xx-persona-topic"}})

    assert mapping == {"PERSONA": "ref-xx-persona-topic"}


def test_inject_config_is_optional() -> None:
    assert injections_from_config({}) == {}
    assert injections_from_config(None) == {}


def test_inject_config_rejects_a_non_object() -> None:
    with pytest.raises(ExportConfigError, match="'inject' must be an object"):
        injections_from_config({"inject": ["ref-xx-persona-topic"]})


def test_inject_config_rejects_non_string_values() -> None:
    with pytest.raises(ExportConfigError, match="inject.PERSONA"):
        injections_from_config({"inject": {"PERSONA": 3}})


def test_this_repo_publishes_the_blocks_the_wordpress_gem_injects() -> None:
    """Guards the real wiring, not a fixture: these two skills must keep publishing."""
    skills_root = Path(".agents/skills")
    for skill_name in (
        "ref-sp-agents-mr-wolf-persona",
        "ref-sp-agents-verification-discipline",
    ):
        block = read_canonical_block(skills_root / skill_name)
        assert block is not None, f"{skill_name} no longer publishes a canonical block"
        assert len(block) > 500
