"""`agentic-tools export` — build a skill export for a chat assistant."""

from pathlib import Path
from typing import Annotated

import typer

from agentic_tools.core.i18n.main import translate
from agentic_tools.features.export.config import (
    ExportConfigError,
    injections_from_config,
    load_config_file,
    resolve_selection,
)
from agentic_tools.features.export.discovery import (
    discover_skills,
    read_canonical_block,
)
from agentic_tools.features.export.gemini_gem import (
    GEMINI_GEM_LIMITS,
    bundle_filename,
    render_bundle,
    render_instructions,
    write_export,
)
from agentic_tools.features.export.models import ExportPlan
from agentic_tools.features.export.planning import build_plan

GEMINI_GEM = "gemini-gem"
_DEFAULT_INSTRUCTIONS = (
    "You are a focused assistant. Answer from the attached knowledge files when they "
    "cover the question, and say plainly when they do not.\n\n"
    "## Knowledge files\n\n{{BUNDLE_MAP}}\n"
)

app = typer.Typer(
    add_completion=False,
    help=translate("export.description"),
    invoke_without_command=True,
)


@app.callback()
def export_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=1)


@app.command("build", help=translate("export.build.help"))
def build(
    target: Annotated[
        str, typer.Option("--target", help=translate("export.build.target"))
    ] = GEMINI_GEM,
    preset: Annotated[
        str, typer.Option("--preset", help=translate("export.build.preset"))
    ] = "knowledge",
    config_path: Annotated[
        Path | None, typer.Option("--config", help=translate("export.build.config"))
    ] = None,
    domains: Annotated[
        str | None, typer.Option("--domains", help=translate("export.build.domains"))
    ] = None,
    exclude: Annotated[
        list[str] | None,
        typer.Option("--exclude", help=translate("export.build.exclude")),
    ] = None,
    skills_root: Annotated[
        Path, typer.Option("--skills-root", help=translate("export.build.skills_root"))
    ] = Path(".agents/skills"),
    out_dir: Annotated[
        Path | None, typer.Option("--out", help=translate("export.build.out"))
    ] = None,
    instructions: Annotated[
        Path | None,
        typer.Option("--instructions", help=translate("export.build.instructions")),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help=translate("export.build.dry_run"))
    ] = False,
    strict: Annotated[
        bool, typer.Option("--strict", help=translate("export.build.strict"))
    ] = False,
) -> int:
    if target != GEMINI_GEM:
        typer.echo(translate("export.build.unknown_target", target=target), err=True)
        return 2

    try:
        config = load_config_file(config_path) if config_path is not None else None
        selection = resolve_selection(
            preset=preset,
            config=config,
            domains=(
                tuple(part.strip() for part in domains.split(",") if part.strip())
                if domains
                else ()
            ),
            excluded_skills=tuple(exclude or ()),
        )
    except ExportConfigError as error:
        typer.echo(str(error), err=True)
        return 2

    skills = discover_skills(skills_root)
    if not skills:
        typer.echo(translate("export.build.no_skills", path=str(skills_root)), err=True)
        return 1

    try:
        plan = build_plan(skills, selection, GEMINI_GEM_LIMITS, strict=strict)
    except ValueError as error:
        typer.echo(str(error), err=True)
        return 1

    if not plan.bundles:
        typer.echo(translate("export.build.empty_selection"), err=True)
        return 1

    _report(plan)

    if dry_run:
        typer.echo(translate("export.build.dry_run_notice"))
        return 0

    template = _resolve_template(config, instructions)
    try:
        injections = _resolve_injections(config, skills_root)
    except ExportConfigError as error:
        typer.echo(str(error), err=True)
        return 2

    destination = out_dir or Path(".agents/playground/export") / target
    written = write_export(plan, destination, template, injections)

    for placeholder in sorted(injections):
        typer.echo(translate("export.build.injected", placeholder=placeholder))

    # The Gem instruction field's limit is undocumented, so report the size
    # rather than let it be discovered on paste.
    instruction_chars = len(render_instructions(plan, template, injections))
    typer.echo(
        translate("export.build.instruction_size", chars=f"{instruction_chars:,}")
    )
    typer.echo(
        translate("export.build.wrote", count=len(written), path=str(destination))
    )
    return 0


def _resolve_template(
    config: dict[str, object] | None, instructions: Path | None
) -> str:
    """Flag beats config beats built-in default."""
    if instructions is not None:
        return instructions.read_text(encoding="utf-8")
    if config is not None:
        configured = config.get("instructions")
        if isinstance(configured, str):
            return Path(configured).read_text(encoding="utf-8")
    return _DEFAULT_INSTRUCTIONS


def _resolve_injections(
    config: dict[str, object] | None, skills_root: Path
) -> dict[str, str]:
    """Project each configured skill's canonical block into a placeholder value.

    A missing block is an error rather than a silent empty substitution: an
    instruction file quietly shipped without its persona still looks fine.
    """
    resolved: dict[str, str] = {}
    for placeholder, skill_name in injections_from_config(config).items():
        block = read_canonical_block(skills_root / skill_name)
        if block is None:
            raise ExportConfigError(
                f"'{skill_name}' publishes no canonical block, so {{{{{placeholder}}}}} "
                "cannot be filled. The skill needs a '## Canonical ... text' heading "
                "followed by a fenced block."
            )
        resolved[placeholder] = block
    return resolved


def _report(plan: ExportPlan) -> None:
    """Print the plan so bundling can be judged before anything is written."""
    typer.echo(
        translate(
            "export.build.summary",
            skills=plan.skill_count,
            words=f"{plan.word_count:,}",
            files=len(plan.bundles),
            max_files=GEMINI_GEM_LIMITS.max_files,
        )
    )
    for bundle in plan.bundles:
        size_kb = len(render_bundle(bundle).encode("utf-8")) / 1024
        names = ", ".join(skill.name for skill in bundle.skills)
        typer.echo(
            f"  {bundle_filename(bundle):<28} {len(bundle.skills):>2} skills  "
            f"{bundle.word_count:>7,} words  {size_kb:>7,.0f} KB"
        )
        typer.echo(f"  {'':<28} {names}")

    for notice in plan.notices:
        typer.echo(translate("export.build.notice", notice=notice))
