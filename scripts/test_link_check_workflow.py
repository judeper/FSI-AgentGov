import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_markdown_link_retry_remains_fail_closed():
    workflow = (
        ROOT / ".github" / "workflows" / "link-check.yml"
    ).read_text(encoding="utf-8")

    assert workflow.count(
        "uses: gaurav-nelson/github-action-markdown-link-check@v1"
    ) == 2
    assert "id: markdown_link_check" in workflow
    assert "continue-on-error: true" in workflow

    retry = workflow.split("- name: Retry markdown links", 1)[1].split(
        "\n  control-consistency:", 1
    )[0]
    assert "if: steps.markdown_link_check.outcome == 'failure'" in retry
    assert "continue-on-error" not in retry
    assert "config-file: '.github/workflows/mlc-config.json'" in retry
    assert "check-modified-files-only:" in retry


def test_federal_register_failures_are_retried_not_accepted():
    config = json.loads(
        (
            ROOT / ".github" / "workflows" / "mlc-config.json"
        ).read_text(encoding="utf-8")
    )

    assert not set(range(500, 600)) & set(config["aliveStatusCodes"])
    federal_headers = [
        item["headers"]
        for item in config["httpHeaders"]
        if item["urls"] == ["https://www.federalregister.gov"]
    ]
    assert len(federal_headers) == 1
    assert federal_headers[0]["User-Agent"].startswith("Mozilla/5.0")
