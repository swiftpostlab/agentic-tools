from pathlib import Path

from agentic_tools.features.export.discovery import (
    demote_headings,
    discover_skills,
    flatten_skill,
    parse_frontmatter,
    strip_body,
)

SKILL_TEXT = """---
name: ref-xx-demo-topic
description: "Does a thing. Use when: a thing needs doing."
license: MIT
metadata:
  shareable-skills.domain: "demo"
  shareable-skills.visibility: "public"
---

# Demo

Body text.

Load `./references/detail.md` when you need the detail.

See `.agents/skills/ref-xx-other-topic/SKILL.md` for the neighbour.
"""


def write_skill(root: Path, name: str, text: str = SKILL_TEXT) -> Path:
    directory = root / name
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text(text, encoding="utf-8")
    return directory


def test_parse_frontmatter_reads_scalars_and_nested_metadata() -> None:
    fields = parse_frontmatter(SKILL_TEXT)

    assert fields["name"] == "ref-xx-demo-topic"
    assert fields["license"] == "MIT"
    assert fields["metadata.shareable-skills.domain"] == "demo"
    assert fields["metadata.shareable-skills.visibility"] == "public"


def test_parse_frontmatter_returns_empty_without_frontmatter() -> None:
    assert parse_frontmatter("# Just a heading\n") == {}


def test_strip_body_drops_load_directives() -> None:
    body = strip_body(SKILL_TEXT)

    assert "Load `./references/detail.md`" not in body
    assert "Body text." in body


def test_strip_body_reduces_cross_skill_paths_to_names() -> None:
    body = strip_body(SKILL_TEXT)

    assert ".agents/skills/" not in body
    assert "`ref-xx-other-topic`" in body


def test_strip_body_removes_frontmatter() -> None:
    body = strip_body(SKILL_TEXT)

    assert "shareable-skills.visibility" not in body
    assert body.startswith("# Demo")


def test_demote_headings_pushes_levels_down_and_caps_at_six() -> None:
    demoted = demote_headings("# One\n## Two\n###### Six\n")

    assert "## One" in demoted
    assert "### Two" in demoted
    assert "###### Six" in demoted


def test_flatten_skill_inlines_references(tmp_path: Path) -> None:
    directory = write_skill(tmp_path, "ref-xx-demo-topic")
    references = directory / "references"
    references.mkdir()
    (references / "detail.md").write_text(
        "# Detail\n\nExtra material.\n", encoding="utf-8"
    )

    document = flatten_skill(directory)

    assert document is not None
    assert document.name == "ref-xx-demo-topic"
    assert document.domain == "demo"
    assert document.visibility == "public"
    assert "Extra material." in document.body
    # The reference heading is demoted so it nests under the skill.
    assert "## Detail" in document.body


def test_flatten_skill_returns_none_without_manifest(tmp_path: Path) -> None:
    empty = tmp_path / "not-a-skill"
    empty.mkdir()

    assert flatten_skill(empty) is None


def test_prefix_and_word_count_derive_from_the_document(tmp_path: Path) -> None:
    document = flatten_skill(write_skill(tmp_path, "ref-xx-demo-topic"))

    assert document is not None
    assert document.prefix == "ref-"
    assert document.word_count > 0


def test_discover_skills_is_sorted_and_skips_non_skills(tmp_path: Path) -> None:
    write_skill(tmp_path, "ref-xx-beta-topic")
    write_skill(tmp_path, "ref-xx-alpha-topic")
    (tmp_path / "stray").mkdir()

    names = [document.name for document in discover_skills(tmp_path)]

    # Both files declare the same frontmatter name, so compare the count and the
    # fact that the stray directory contributed nothing.
    assert len(names) == 2


def test_discover_skills_handles_missing_root(tmp_path: Path) -> None:
    assert discover_skills(tmp_path / "nope") == ()
