"""Regression tests for the website's versioned download links."""

from pathlib import Path

import pytest

from hooks.sui_version import on_config, on_page_markdown


@pytest.fixture
def site_config(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "Changelog.md").write_text("### Sui 0.75Z\n### Sui 0.75Y\n", encoding="utf-8")
    for name in (
        "Sui075-0.75Z-full-jar-with-dependencies.jar",
        "Sui075-0.75Z-full-minimal.jar",
        "Sui075-0.75Y-full-jar-with-dependencies.jar",
        "sui-mainframe-integration-1.0.0-SNAPSHOT-jar-with-dependencies.jar",
    ):
        (tmp_path / name).touch()
    return {
        "docs_dir": str(docs),
        "extra": {"download_base": "https://raw.githubusercontent.com/kje2lhan/SuiDistro/main"},
    }


def test_downloads_match_current_version(site_config):
    extra = on_config(site_config)["extra"]
    assert extra["sui_version"] == "0.75Z"
    assert extra["sui_full_url"].endswith("/Sui075-0.75Z-full-jar-with-dependencies.jar")
    assert extra["sui_minimal_url"].endswith("/Sui075-0.75Z-full-minimal.jar")
    assert extra["zui_url"].endswith(
        "/sui-mainframe-integration-1.0.0-SNAPSHOT-jar-with-dependencies.jar"
    )
    markdown = "{{ sui_full_url }} {{ sui_minimal_url }} {{ zui_url }} {{ other }}"
    rendered = on_page_markdown(markdown, None, site_config, None)
    for key in ("sui_full_url", "sui_minimal_url", "zui_url"):
        assert extra[key] in rendered
    assert "{{ other }}" in rendered
    assert "/releases/latest/download/" not in rendered


def test_full_jar_preferred_over_legacy_name(site_config):
    root = Path(site_config["docs_dir"]).parent
    legacy = root / "Sui075-0.75Z-jar-with-dependencies.jar"
    legacy.touch()
    assert "-full-" in on_config(site_config)["extra"]["sui_full_url"]
    (root / "Sui075-0.75Z-full-jar-with-dependencies.jar").unlink()
    assert on_config(site_config)["extra"]["sui_full_url"].endswith("/" + legacy.name)


@pytest.mark.parametrize(
    "filename",
    [
        "Sui075-0.75Z-full-jar-with-dependencies.jar",
        "Sui075-0.75Z-full-minimal.jar",
        "sui-mainframe-integration-1.0.0-SNAPSHOT-jar-with-dependencies.jar",
    ],
)
def test_missing_download_fails_build(site_config, filename):
    (Path(site_config["docs_dir"]).parent / filename).unlink()
    with pytest.raises(ValueError, match="Expected one committed JAR"):
        on_config(site_config)


def test_new_changelog_entry_selects_new_jars(site_config):
    docs = Path(site_config["docs_dir"])
    (docs / "Changelog.md").write_text("### Sui 0.76A\n### Sui 0.75Z\n", encoding="utf-8")
    for variant in ("full-jar-with-dependencies", "full-minimal"):
        (docs.parent / f"Sui076-0.76A-{variant}.jar").touch()
    extra = on_config(site_config)["extra"]
    assert extra["sui_version"] == "0.76A"
    assert "/Sui076-0.76A-" in extra["sui_full_url"]
    assert "/Sui076-0.76A-" in extra["sui_minimal_url"]
