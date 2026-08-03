import json
from pathlib import Path

import pytest

from agentic_tools.features.export.config import (
    PRESETS,
    ExportConfigError,
    load_config_file,
    resolve_selection,
)


def write_config(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "export.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_knowledge_preset_excludes_the_meta_domain() -> None:
    assert "agents" in PRESETS["knowledge"].excluded_domains
    assert PRESETS["everything"].excluded_domains == ()


def test_presets_name_no_concrete_skills() -> None:
    # A preset naming real skills would be meaningless in a consuming repo.
    for selection in PRESETS.values():
        assert selection.included_skills == ()
        assert selection.excluded_skills == {}


def test_load_config_file_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ExportConfigError, match="not found"):
        load_config_file(tmp_path / "absent.json")


def test_load_config_file_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "export.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ExportConfigError, match="not valid JSON"):
        load_config_file(path)


def test_load_config_file_rejects_a_non_object(tmp_path: Path) -> None:
    with pytest.raises(ExportConfigError, match="JSON object"):
        load_config_file(write_config(tmp_path, [1, 2]))


def test_config_overrides_the_preset(tmp_path: Path) -> None:
    config = load_config_file(
        write_config(tmp_path, {"select": {"domains": ["web", "ux"]}})
    )

    selection = resolve_selection(
        preset="knowledge", config=config, domains=(), excluded_skills=()
    )

    assert selection.domains == ("web", "ux")


def test_flags_override_the_config(tmp_path: Path) -> None:
    config = load_config_file(write_config(tmp_path, {"select": {"domains": ["web"]}}))

    selection = resolve_selection(
        preset="knowledge", config=config, domains=("db",), excluded_skills=()
    )

    assert selection.domains == ("db",)


def test_excluded_skills_must_carry_reasons(tmp_path: Path) -> None:
    config = load_config_file(
        write_config(tmp_path, {"select": {"excludeSkills": ["ref-xx-a-topic"]}})
    )

    with pytest.raises(ExportConfigError, match="folklore"):
        resolve_selection(
            preset="knowledge", config=config, domains=(), excluded_skills=()
        )


def test_exclusion_reasons_survive_into_the_selection(tmp_path: Path) -> None:
    config = load_config_file(
        write_config(
            tmp_path,
            {"select": {"excludeSkills": {"ref-xx-a-topic": "needs a terminal"}}},
        )
    )

    selection = resolve_selection(
        preset="knowledge", config=config, domains=(), excluded_skills=()
    )

    assert selection.excluded_skills["ref-xx-a-topic"] == "needs a terminal"


def test_command_line_exclusions_record_their_own_reason() -> None:
    selection = resolve_selection(
        preset="knowledge", config=None, domains=(), excluded_skills=("ref-xx-a-topic",)
    )

    assert "command line" in selection.excluded_skills["ref-xx-a-topic"]


def test_unknown_preset_is_rejected_with_the_available_names() -> None:
    with pytest.raises(ExportConfigError, match="knowledge"):
        resolve_selection(preset="nope", config=None, domains=(), excluded_skills=())


def test_select_must_be_an_object(tmp_path: Path) -> None:
    config = load_config_file(write_config(tmp_path, {"select": "web"}))

    with pytest.raises(ExportConfigError, match="'select' must be an object"):
        resolve_selection(
            preset="knowledge", config=config, domains=(), excluded_skills=()
        )
