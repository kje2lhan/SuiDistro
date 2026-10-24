"""MkDocs hook: expose the current Sui version and substitute {{ key }} placeholders.

The version is read from the first "### Sui <version>" heading in docs/Changelog.md,
so publishing a new version only needs a new Changelog entry. Placeholders are only
replaced for keys that exist in `extra`, so other double-brace text is left alone.
"""

import re
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def on_config(config):
    changelog = Path(config["docs_dir"]) / "Changelog.md"
    match = re.search(r"^###\s+Sui\s+(\S+)", changelog.read_text(encoding="utf-8"), re.MULTILINE)
    config["extra"]["sui_version"] = match.group(1) if match else "unknown"
    return config


def on_page_markdown(markdown, page, config, files):
    extra = config["extra"]

    def replace(m):
        value = extra.get(m.group(1))
        return str(value) if isinstance(value, (str, int, float)) else m.group(0)

    return PLACEHOLDER.sub(replace, markdown)
