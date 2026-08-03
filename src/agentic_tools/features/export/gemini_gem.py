"""Emit an export shaped for a Gemini Gem.

A Gem gives back two of the three mechanisms a skill relies on: the instruction
field behaves like an always-loaded routing document, and Knowledge files are
retrieved when relevant. What it cannot do is run anything, so the export is
prose only.

Routing lives in the instructions rather than in a knowledge file. Retrieval
picks *within* the corpus; it cannot tell the model when to reach for the corpus
at all, which is exactly what the always-loaded layer is for.
"""

from pathlib import Path

from agentic_tools.features.export.models import Bundle, ExportPlan, TargetLimits

# Google documents 10 knowledge files per Gem and 100 MB per file. The word
# guideline is ours: nothing enforces it, but bundles far past it retrieve
# noisily. See references in the export README this module writes.
GEMINI_GEM_LIMITS = TargetLimits(
    max_files=10,
    max_file_bytes=100 * 1024 * 1024,
    soft_words_per_bundle=40_000,
)

_BUNDLE_MAP_PLACEHOLDER = "{{BUNDLE_MAP}}"


def bundle_filename(bundle: Bundle) -> str:
    return f"{bundle.name}.md"


def render_bundle(bundle: Bundle) -> str:
    """Render one knowledge file.

    Each skill keeps its own heading and description so a retrieved chunk still
    carries the context that says what it is and when it applies.
    """
    header = [
        f"# {bundle.name} knowledge",
        "",
        f"Covers {len(bundle.skills)} topics: "
        + ", ".join(skill.name for skill in bundle.skills)
        + ".",
        "",
    ]
    sections = [
        (
            f"---\n\n# {skill.name}\n\n_When this applies: {skill.description}_\n\n{skill.body}"
            if skill.description
            else f"---\n\n# {skill.name}\n\n{skill.body}"
        )
        for skill in bundle.skills
    ]
    return "\n".join(header) + "\n\n".join(sections) + "\n"


def render_bundle_map(plan: ExportPlan) -> str:
    """The routing block injected into the instruction template.

    Bundle-level, not skill-level: eight lines instead of fifty, which is what
    keeps the always-loaded layer small enough to survive an instruction-field
    limit. Retrieval does the fine-grained selection.
    """
    lines: list[str] = []
    for bundle in plan.bundles:
        lines.append(f"**`{bundle_filename(bundle)}`**")
        lines.append("")
        for skill in bundle.skills:
            topic = skill.name.split("-", 3)[-1].replace("-", " ")
            lines.append(f"- *{topic}* — {_trigger_from(skill.description)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _trigger_from(description: str) -> str:
    """Pull the activation clause out of a skill description.

    Descriptions in this repo are written as "<what it does>. Use when: <triggers>".
    The trigger half is the part that answers "reach for it when", so prefer it and
    fall back to the whole description when the convention was not followed.
    """
    lowered = description.lower()
    marker = lowered.find("use when:")
    trigger = description[marker + len("use when:") :] if marker != -1 else description
    collapsed = " ".join(trigger.split())
    if len(collapsed) <= 300:
        return collapsed
    return f"{collapsed[:297].rsplit(' ', 1)[0]}…"


def render_instructions(plan: ExportPlan, template: str) -> str:
    """Fill a hand-written instruction template with the generated routing.

    The template is authored, not derived: an instruction file assembled by
    cutting sections out of a repo's `AGENTS.md` inherits its audience, its
    tooling references, and its assumption of file access.
    """
    if _BUNDLE_MAP_PLACEHOLDER not in template:
        return (
            f"{template.rstrip()}\n\n## Knowledge files\n\n{render_bundle_map(plan)}\n"
        )
    return template.replace(_BUNDLE_MAP_PLACEHOLDER, render_bundle_map(plan))


def render_readme(plan: ExportPlan, out_dir: Path) -> str:
    """Explain what to do with the generated files."""
    lines = [
        "# Gemini Gem export",
        "",
        "Generated. Re-run the exporter rather than editing these files by hand.",
        "",
        "## How to use",
        "",
        "1. Create a Gem at <https://gemini.google.com>.",
        "2. Paste `instructions.md` into the Gem's instructions field. Its length limit is "
        "undocumented; if it is rejected, shorten the prose rather than the routing block — "
        "routing is the part retrieval cannot replace.",
        f"3. Upload the {len(plan.bundles)} `.md` files below under **Knowledge**.",
        "",
        "## Contents",
        "",
        "| File | Skills | Words | KB |",
        "| --- | --- | --- | --- |",
    ]
    for bundle in plan.bundles:
        size_kb = len(render_bundle(bundle).encode("utf-8")) / 1024
        lines.append(
            f"| `{bundle_filename(bundle)}` | {len(bundle.skills)} | "
            f"{bundle.word_count:,} | {size_kb:,.0f} |"
        )

    lines += [
        "",
        f"**{plan.skill_count} skills, {plan.word_count:,} words** across "
        f"{len(plan.bundles)} of {GEMINI_GEM_LIMITS.max_files} allowed knowledge files.",
        "",
    ]

    if plan.notices:
        lines += ["## Notices", ""] + [f"- {notice}" for notice in plan.notices] + [""]

    if plan.excluded:
        lines += [
            "## Excluded, and why",
            "",
            "| Skill | Reason |",
            "| --- | --- |",
        ]
        lines += [
            f"| `{name}` | {reason} |" for name, reason in sorted(plan.excluded.items())
        ]
        lines.append("")

    lines += [
        "## Limits this export respects",
        "",
        "- 10 knowledge files per Gem, 100 MB per file "
        "(<https://support.google.com/gemini/answer/14903178>).",
        "- Bundles are grouped by skill domain for retrieval coherence, not packed by size.",
        f"- Output directory: `{out_dir}`.",
        "",
    ]
    return "\n".join(lines)


def write_export(
    plan: ExportPlan, out_dir: Path, instructions_template: str
) -> tuple[Path, ...]:
    """Write the knowledge files, instructions, and README. Returns what it wrote."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for bundle in plan.bundles:
        path = out_dir / bundle_filename(bundle)
        path.write_text(render_bundle(bundle), encoding="utf-8")
        written.append(path)

    instructions = out_dir / "instructions.md"
    instructions.write_text(
        render_instructions(plan, instructions_template), encoding="utf-8"
    )
    written.append(instructions)

    readme = out_dir / "README.md"
    readme.write_text(render_readme(plan, out_dir), encoding="utf-8")
    written.append(readme)

    return tuple(written)
