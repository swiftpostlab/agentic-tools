"""Project canonical skill text into the chat-assistant instruction files.

Every `chat-assistants/<product>/templates/<name>.template.md` holds `{{PLACEHOLDER}}`
tokens that stand for canonical blocks published by skills. This script fills them
and writes `chat-assistants/<product>/<name>.md`, which is the file a person pastes
into the product.

    python scripts/project_assistant_instructions.py            # write
    python scripts/project_assistant_instructions.py --check     # verify, write nothing

`--check` exits non-zero when a generated file no longer matches a fresh projection,
which is the only thing standing between a paste target and a silent fork of the
persona text. Wired up as `uv run poe assistants-check`.

Only templated files are projected. The short versions under `chatgpt-custom/` and
`duck-ai-custom/` are hand-written compressions with no template, because no
canonical block fits in a 500 or 1,500 character field.
"""

import argparse
import sys
from pathlib import Path

from agentic_tools.features.export.discovery import read_canonical_block

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
ASSISTANTS_ROOT = REPO_ROOT / "chat-assistants"

# Placeholder -> the skill that publishes the canonical block behind it. Skills are
# named here rather than in the templates so a rename is a one-line change.
INJECTIONS = {
    "PERSONA": "ref-sp-agents-mr-wolf-persona",
    "VERIFICATION": "ref-sp-agents-verification-discipline",
}


def render(template_path: Path) -> str:
    """Fill one template. Raises ValueError when a placeholder cannot be resolved."""
    text = template_path.read_text(encoding="utf-8")

    for placeholder, skill_name in INJECTIONS.items():
        token = "{{" + placeholder + "}}"
        if token not in text:
            continue
        block = read_canonical_block(SKILLS_ROOT / skill_name)
        if block is None:
            raise ValueError(
                f"'{skill_name}' publishes no canonical block, so {token} cannot be "
                "filled. The skill needs a '## Canonical ... text' heading followed "
                "by a fenced block."
            )
        text = text.replace(token, block)

    if "{{" in text:
        raise ValueError(f"{template_path.name} still holds an unresolved placeholder")
    return text


def output_path(template_path: Path) -> Path:
    """`<product>/templates/<name>.template.md` -> `<product>/<name>/instructions.md`.

    One folder per assistant, so a product that also needs knowledge files has
    somewhere to put them next to the instructions a person pastes.
    """
    name = template_path.name.removesuffix(".template.md")
    return template_path.parent.parent / name / "instructions.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the generated files match a fresh projection; write nothing",
    )
    args = parser.parse_args()

    templates = sorted(ASSISTANTS_ROOT.glob("*/templates/*.template.md"))
    if not templates:
        print(f"no templates found under {ASSISTANTS_ROOT}", file=sys.stderr)
        return 1

    stale: list[Path] = []
    for template_path in templates:
        try:
            rendered = render(template_path)
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 1

        destination = output_path(template_path)
        relative = destination.relative_to(REPO_ROOT)

        if args.check:
            current = (
                destination.read_text(encoding="utf-8") if destination.is_file() else ""
            )
            if current != rendered:
                stale.append(relative)
                print(f"stale: {relative}", file=sys.stderr)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
        # The instruction field limits are undocumented on every one of these
        # products, so report the size rather than let it be found on paste.
        print(f"wrote {relative} ({len(rendered):,} chars)")

    if stale:
        print(
            f"\n{len(stale)} file(s) no longer match their template. "
            "Run: uv run poe assistants-build",
            file=sys.stderr,
        )
        return 1

    if args.check:
        print(f"{len(templates)} generated file(s) match their templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
