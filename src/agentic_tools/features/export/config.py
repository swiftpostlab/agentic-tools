"""Load an export request from presets, an arbitrary config file, and flags.

Precedence, weakest first: preset, then config file, then explicit flags. An
export config is deliberately *not* repository policy — it is a request that is
usually one-off, so it is read from any path the caller names and never has to
be checked in.

Presets stay generic (visibility, prefix, domain). A preset that named concrete
skills would be meaningless in a consuming repo running the same CLI.
"""

import json
from pathlib import Path
from typing import Any, cast

from agentic_tools.features.export.models import Selection

PRESETS: dict[str, Selection] = {
    # Subject-matter guidance: what someone reaching for an assistant usually
    # wants. Excludes the meta-domain about authoring skills themselves.
    "knowledge": Selection(
        visibilities=("public",),
        prefixes=("ref-",),
        excluded_domains=("agents",),
    ),
    # Everything portable, meta included.
    "everything": Selection(visibilities=("public",), prefixes=("ref-",)),
}


class ExportConfigError(Exception):
    """Raised when a config file cannot be understood."""


def load_config_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ExportConfigError(f"config file not found: {path}")
    try:
        parsed: Any = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ExportConfigError(
            f"config file is not valid JSON: {path} ({error})"
        ) from error
    if not isinstance(parsed, dict):
        raise ExportConfigError(f"config file must contain a JSON object: {path}")
    # JSON objects always have string keys, which `json.loads` cannot express.
    return cast(dict[str, Any], parsed)


def _as_str_tuple(value: Any, *, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ExportConfigError(f"'{field}' must be a list of strings")
    items: list[str] = []
    for item in value:  # pyright: ignore[reportUnknownVariableType]
        if not isinstance(item, str):
            raise ExportConfigError(f"'{field}' must contain only strings")
        items.append(item)
    return tuple(items)


def _as_reason_map(value: Any, *, field: str) -> dict[str, str]:
    """Read `excludeSkills`, which is an object so every exclusion carries a reason."""
    if value is None:
        return {}
    if isinstance(value, list):
        raise ExportConfigError(
            f"'{field}' must be an object mapping skill name to a reason, not a list — "
            "an exclusion without a recorded reason becomes folklore"
        )
    if not isinstance(value, dict):
        raise ExportConfigError(
            f"'{field}' must be an object mapping skill name to a reason"
        )
    reasons: dict[str, str] = {}
    for key, reason in value.items():  # pyright: ignore[reportUnknownVariableType]
        if not isinstance(key, str) or not isinstance(reason, str):
            raise ExportConfigError(f"'{field}' keys and values must both be strings")
        reasons[key] = reason
    return reasons


def selection_from_config(config: dict[str, Any], *, base: Selection) -> Selection:
    """Overlay a config file's `select` block onto a base selection."""
    raw: Any = config.get("select")
    if raw is None:
        return base
    if not isinstance(raw, dict):
        raise ExportConfigError("'select' must be an object")
    select = cast(dict[str, Any], raw)

    return Selection(
        visibilities=_as_str_tuple(select.get("visibility"), field="select.visibility")
        or base.visibilities,
        prefixes=_as_str_tuple(select.get("prefixes"), field="select.prefixes")
        or base.prefixes,
        domains=_as_str_tuple(select.get("domains"), field="select.domains")
        or base.domains,
        excluded_domains=_as_str_tuple(
            select.get("excludeDomains"), field="select.excludeDomains"
        )
        or base.excluded_domains,
        included_skills=_as_str_tuple(select.get("skills"), field="select.skills")
        or base.included_skills,
        excluded_skills={
            **base.excluded_skills,
            **_as_reason_map(select.get("excludeSkills"), field="select.excludeSkills"),
        },
    )


def resolve_selection(
    *,
    preset: str,
    config: dict[str, Any] | None,
    domains: tuple[str, ...],
    excluded_skills: tuple[str, ...],
) -> Selection:
    """Combine preset, config file, and flags into one selection."""
    if preset not in PRESETS:
        raise ExportConfigError(
            f"unknown preset '{preset}'. Available: {', '.join(sorted(PRESETS))}"
        )

    selection = PRESETS[preset]
    if config is not None:
        selection = selection_from_config(config, base=selection)

    if domains:
        selection = Selection(
            visibilities=selection.visibilities,
            prefixes=selection.prefixes,
            domains=domains,
            excluded_domains=selection.excluded_domains,
            included_skills=selection.included_skills,
            excluded_skills=selection.excluded_skills,
        )

    if excluded_skills:
        selection = Selection(
            visibilities=selection.visibilities,
            prefixes=selection.prefixes,
            domains=selection.domains,
            excluded_domains=selection.excluded_domains,
            included_skills=selection.included_skills,
            excluded_skills={
                **selection.excluded_skills,
                **{name: "excluded on the command line" for name in excluded_skills},
            },
        )

    return selection
