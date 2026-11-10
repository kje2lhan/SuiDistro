"""MkDocs hook: expose the current Sui version and substitute {{ key }} placeholders.

The version is read from the first "### Sui <version>" heading in docs/Changelog.md.
Download links use matching jars committed alongside the docs. Placeholders are only
replaced for keys that exist in `extra`, so other double-brace text is left alone.
"""

import re
from pathlib import Path
from urllib.parse import quote

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def on_config(config):
    changelog = Path(config["docs_dir"]) / "Changelog.md"
    match = re.search(r"^###\s+Sui\s+(\S+)", changelog.read_text(encoding="utf-8"), re.MULTILINE)
    config["extra"]["sui_version"] = match.group(1) if match else "unknown"
    version = config["extra"]["sui_version"]
    root = changelog.parent.parent
    patterns = {
        "sui_full_url": (
            f"Sui*-{version}-full-jar-with-dependencies.jar",
            f"Sui*-{version}-jar-with-dependencies.jar",
        ),
        "sui_minimal_url": (f"Sui*-{version}-*minimal.jar",),
        "zui_url": ("sui-mainframe-integration-*-jar-with-dependencies.jar",),
    }
    for key, candidates in patterns.items():
        for pattern in candidates:
            jars = sorted(path for path in root.glob(pattern) if path.is_file())
            if jars:
                break
        if len(jars) != 1:
            raise ValueError(f"Expected one committed JAR for {key} (Sui {version}), found {len(jars)}")
        config["extra"][key] = f'{config["extra"]["download_base"].rstrip("/")}/{quote(jars[0].name)}'
    return config


def on_page_markdown(markdown, page, config, files):
    extra = config["extra"]

    def replace(m):
        value = extra.get(m.group(1))
        return str(value) if isinstance(value, (str, int, float)) else m.group(0)

    return PLACEHOLDER.sub(replace, markdown)
