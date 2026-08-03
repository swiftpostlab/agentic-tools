"""Read skills off disk and flatten them into single documents.

Flattening is the part that does not survive the trip to a chat assistant: a
skill's `SKILL.md` is written assuming an agent that can load `references/` on
instruction. Nothing on the other end can do that, so the references are inlined
and the load-directives that pointed at them are dropped.
"""

import re
from pathlib import Path

from agentic_tools.features.export.models import SkillDocument

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
_SCALAR = re.compile(r"^([A-Za-z0-9_.-]+):\s*(.*)$")
_LOAD_DIRECTIVE = re.compile(
    r"^\s*[-*]?\s*(?:\*\*)?(?:Load|Read|Use)\b[^\n]*`\./(?:references|scripts|assets|evals)/[^\n]*$",
    re.IGNORECASE,
)
_INLINE_DIRECTIVE = re.compile(
    r"(?:Load|Read|See|Use)\s+`\./references/([a-z0-9-]+)\.md`", re.IGNORECASE
)
_SKILL_PATH = re.compile(
    r"`?\.agents/skills/((?:ref|tool)-[a-z0-9-]+)(?:/(?:SKILL\.md|references/[a-z0-9-]+\.md))?`?"
)
_HEADING = re.compile(r"^(#{1,6})\s", re.MULTILINE)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Read the flat `key: value` pairs from a skill's YAML frontmatter.

    Only the shapes this repo's skills actually use are supported: top-level
    scalars and one level of `metadata:` nesting, which the Agent Skills spec
    restricts to string-to-string anyway. Anything else is ignored rather than
    guessed at.
    """
    match = _FRONTMATTER.match(text)
    if match is None:
        return {}

    fields: dict[str, str] = {}
    nested_prefix: str | None = None
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indented = raw_line[0] in " \t"
        scalar = _SCALAR.match(raw_line.strip())
        if scalar is None:
            continue

        key, value = scalar.group(1), _unquote(scalar.group(2).strip())
        if not value:
            nested_prefix = None if indented else key
            continue

        fields[f"{nested_prefix}.{key}" if indented and nested_prefix else key] = value

    return fields


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def strip_body(text: str) -> str:
    """Remove frontmatter and the scaffolding that only means something to an agent.

    Standalone load-directives are dropped outright. Directives embedded in a
    sentence are *rewritten* rather than removed, because the line usually
    carries real content around them — and the reference they point at is
    inlined further down, so a section pointer is the truthful replacement.
    """
    body = _FRONTMATTER.sub("", text, count=1)
    kept = [line for line in body.splitlines() if not _LOAD_DIRECTIVE.match(line)]
    rewritten = _INLINE_DIRECTIVE.sub(
        lambda match: f'see the "{_title_from_stem(match.group(1))}" section below',
        "\n".join(kept),
    )
    return _SKILL_PATH.sub(r"`\1`", rewritten).strip()


def demote_headings(text: str, *, levels: int = 1) -> str:
    """Push headings down so an inlined reference nests under its skill."""

    def replace(match: re.Match[str]) -> str:
        depth = min(len(match.group(1)) + levels, 6)
        return f"{'#' * depth} "

    return _HEADING.sub(replace, text)


def flatten_skill(skill_directory: Path) -> SkillDocument | None:
    """Build one document from a skill folder, or `None` if it has no `SKILL.md`."""
    manifest = skill_directory / "SKILL.md"
    if not manifest.is_file():
        return None

    raw = manifest.read_text(encoding="utf-8")
    fields = parse_frontmatter(raw)
    name = fields.get("name", skill_directory.name)

    sections = [strip_body(raw)]
    references = skill_directory / "references"
    if references.is_dir():
        for reference in sorted(references.glob("*.md")):
            content = demote_headings(strip_body(reference.read_text(encoding="utf-8")))
            sections.append(f"## {_title_from(reference)}\n\n{content}")

    return SkillDocument(
        name=name,
        domain=fields.get("metadata.shareable-skills.domain", "unknown"),
        visibility=fields.get("metadata.shareable-skills.visibility", "repo-local"),
        description=fields.get("description", ""),
        body="\n\n".join(section for section in sections if section),
    )


def _title_from(path: Path) -> str:
    return _title_from_stem(path.stem)


def _title_from_stem(stem: str) -> str:
    return stem.replace("-", " ").capitalize()


def discover_skills(skills_root: Path) -> tuple[SkillDocument, ...]:
    """Flatten every skill under `skills_root`, sorted by name for stable output."""
    if not skills_root.is_dir():
        return ()

    found = [
        document
        for directory in sorted(skills_root.iterdir())
        if directory.is_dir()
        for document in (flatten_skill(directory),)
        if document is not None
    ]
    return tuple(found)
