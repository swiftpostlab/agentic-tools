"""Run the grouped agentic-tools CLI.

Canonical usage:
- `uv run agentic-tools policy sync`
- `uv run agentic-tools policy check`
- `uv run agentic-tools policy import-vscode`
- `uv run agentic-tools skills sync`
"""

from argparse import ArgumentParser
from collections.abc import Sequence
import os
from pathlib import Path
import sys

import agentic_tools.agents_policy.main as agents_policy_main
import agentic_tools.skills_management.main as skills_management_main


def add_workspace_argument(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-w",
        "--workspace",
        dest="workspace",
        help="Run the selected command from this workspace directory.",
    )


def add_config_argument(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        help="Path to the policy file.",
    )


def build_root_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="agentic-tools",
        description="Run shared policy and skills workflows from one grouped CLI.",
    )
    add_workspace_argument(parser)
    subparsers = parser.add_subparsers(dest="scope")

    policy_parser = subparsers.add_parser(
        "policy",
        help="Sync or check generated agent policy files.",
    )
    policy_subparsers = policy_parser.add_subparsers(dest="policy_command")

    policy_sync_parser = policy_subparsers.add_parser(
        "sync",
        help="Sync generated policy files from .agents/policy.json.",
    )
    add_config_argument(policy_sync_parser)

    policy_check_parser = policy_subparsers.add_parser(
        "check",
        help="Report drift without rewriting generated policy files.",
    )
    add_config_argument(policy_check_parser)

    policy_import_parser = policy_subparsers.add_parser(
        "import-vscode",
        help="Import VS Code approvals into the policy file before syncing.",
    )
    add_config_argument(policy_import_parser)

    subparsers.add_parser(
        "skills",
        help="List, link, sync, and unlink shared skills.",
    )
    return parser


def build_root_option_parser() -> ArgumentParser:
    parser = ArgumentParser(add_help=False)
    add_workspace_argument(parser)
    return parser


def parse_root_arguments(arguments: Sequence[str]) -> tuple[str | None, list[str]]:
    parser = build_root_option_parser()
    args, remaining = parser.parse_known_args(list(arguments))
    return args.workspace, remaining


def resolve_workspace(raw_workspace: str | None) -> Path | None:
    if raw_workspace is None:
        return None

    workspace = Path(raw_workspace).expanduser().resolve()
    if not workspace.is_dir():
        raise ValueError(f"Could not find workspace directory at {workspace}")
    return workspace


def normalize_exit_code(error: SystemExit) -> int:
    code = error.code
    if isinstance(code, int):
        return code
    if code is None:
        return 0
    return 1


def build_policy_arguments(*, command: str, config: str | None) -> list[str]:
    arguments: list[str] = []
    if command == "check":
        arguments.append("--check")
    elif command == "import-vscode":
        arguments.append("--import-vscode")

    if config is not None:
        arguments.extend(["--config", config])

    return arguments


def run_policy_scope(arguments: Sequence[str]) -> int:
    parser = build_root_parser()
    if not arguments:
        parser.print_help()
        return 1

    try:
        args = parser.parse_args(["policy", *arguments])
    except SystemExit as error:
        return normalize_exit_code(error)

    policy_command = getattr(args, "policy_command", None)
    if not isinstance(policy_command, str):
        parser.print_help()
        return 1

    return agents_policy_main.run(
        build_policy_arguments(command=policy_command, config=args.config)
    )


def run_skills_scope(arguments: Sequence[str]) -> int:
    return skills_management_main.main(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    parser = build_root_parser()
    argv = list(arguments) if arguments is not None else sys.argv[1:]

    try:
        raw_workspace, remaining = parse_root_arguments(argv)
    except SystemExit as error:
        return normalize_exit_code(error)

    if not remaining:
        parser.print_help()
        return 1

    try:
        workspace = resolve_workspace(raw_workspace)
    except ValueError as error:
        print(error)
        return 1

    previous_cwd: Path | None = None
    if workspace is not None:
        previous_cwd = Path.cwd()
        os.chdir(workspace)

    try:
        scope, *scope_arguments = remaining
        if scope == "policy":
            return run_policy_scope(scope_arguments)
        if scope == "skills":
            return run_skills_scope(scope_arguments)
    finally:
        if previous_cwd is not None:
            os.chdir(previous_cwd)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
