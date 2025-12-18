"""Extract text from the Agent Governance whitepaper PDF.

Purpose:
- Produce a searchable text artifact so maintainers can align Zone definitions and intent
    with the source document.

Local-only outputs (gitignored):
- maintainers-local/reference-pack/Agent Governance V3.txt
- maintainers-local/reference-pack/Agent Governance V3.extracted.json (page-level text)

Note:
- This repository is public. The whitepaper PDF and derived extracts are maintainer-only
    artifacts and must never be written under docs/.
"""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_REF_PACK = REPO_ROOT / "maintainers-local" / "reference-pack"

PDF_PATH = LOCAL_REF_PACK / "Agent Governance V3.pdf"
TXT_PATH = LOCAL_REF_PACK / "Agent Governance V3.txt"
JSON_PATH = LOCAL_REF_PACK / "Agent Governance V3.extracted.json"


def main() -> int:
    LOCAL_REF_PACK.mkdir(parents=True, exist_ok=True)

    if not PDF_PATH.exists():
        raise FileNotFoundError(PDF_PATH)

    reader = PdfReader(str(PDF_PATH))

    pages: list[dict[str, object]] = []
    all_text_parts: list[str] = []

    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as ex:  # noqa: BLE001
            text = ""
            pages.append({"page": i, "error": str(ex), "text": text})
        else:
            pages.append({"page": i, "text": text})

        # Add page boundary for easier searching.
        all_text_parts.append(f"\n\n===== PAGE {i} =====\n\n")
        all_text_parts.append(text)

    TXT_PATH.write_text("".join(all_text_parts), encoding="utf-8", newline="\n")
    JSON_PATH.write_text(json.dumps(pages, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    non_empty_pages = sum(1 for p in pages if (p.get("text") or "").strip())
    print(f"Extracted {len(pages)} pages ({non_empty_pages} non-empty).")
    print(f"Wrote: {TXT_PATH}")
    print(f"Wrote: {JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
