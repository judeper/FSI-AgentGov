#!/usr/bin/env python3
"""Build the FSI-AgentGov external-reviewer package.

Produces a self-contained, link-flattened, multi-format package so external
research agents can critique the *user experience* WITHOUT repo or live-site
access. Output goes to ``maintainers-local/researcher-package/`` (gitignored).

Review model (see the 7 briefs in scripts/review_package_templates/): every
agent gets the same full package; each gets a different targeted task brief.

Usage::

    python scripts/build_review_package.py            # full build (md + site-map + manifest + briefs)
    python scripts/build_review_package.py --site      # also `mkdocs build` -> _rendered-site/
    python scripts/build_review_package.py --pdf       # also render PDFs (needs a PDF tool)
    python scripts/build_review_package.py --zip       # also zip the package folder

This is the successor to compile_researcher_package.py: dynamic discovery (no
hardcoded control ranges), all six content areas, plus START-HERE / SITE-MAP /
MANIFEST / briefs.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DOCS = BASE_DIR / "docs"
MKDOCS = BASE_DIR / "mkdocs.yml"
TEMPLATES = SCRIPT_DIR / "review_package_templates"
OUTPUT = BASE_DIR / "maintainers-local" / "researcher-package"
PUBLIC_URL = "https://judeper.github.io/FSI-AgentGov/"

PILLARS = {
    1: ("Security", "pillar-1-security"),
    2: ("Management", "pillar-2-management"),
    3: ("Reporting", "pillar-3-reporting"),
    4: ("SharePoint", "pillar-4-sharepoint"),
}

# Playbooks: include FULL content only for a representative sample (the suite is
# ~390 files); everything else is listed structurally so reviewers see the scope
# without an unreadable mega-file.
PLAYBOOK_SAMPLE_CONTROLS = {"1.1", "2.1", "3.1"}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def flatten_links(text: str) -> str:
    """Make markdown self-contained: turn internal links into plain references."""
    text = re.sub(r"\[Control (\d+\.\d+)\]\([^)]+\)", r"Control \1", text)
    text = re.sub(r"\[([^\]]+)\]\((?:\.\./)+[^)]*\)", r"\1", text)  # ../ relative links
    text = re.sub(r"\[([^\]]+)\]\((?!https?://)[^)]*\.md[^)]*\)", r"\1", text)  # *.md links
    text = re.sub(r"!\[([^\]]*)\]\((?:\.\./)*images/[^)]+\)", r"[Image: \1]", text)
    return text


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def h1_of(path: Path) -> str:
    for line in read(path).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=BASE_DIR, text=True
        ).strip()
    except Exception:
        return "unknown"


def framework_version() -> str:
    v = read(BASE_DIR / "VERSION").strip()
    return v or "unknown"


PROVENANCE = ""  # filled in main()


def section(title: str) -> str:
    return f"\n\n{'=' * 78}\n# {title}\n{'=' * 78}\n\n"


# --------------------------------------------------------------------------- #
# site map (parse the mkdocs nav block textually — mkdocs.yml has custom tags)
# --------------------------------------------------------------------------- #
def build_site_map() -> str:
    lines = read(MKDOCS).splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.rstrip() == "nav:")
    except StopIteration:
        return "# Site Map\n\n(nav not found)\n"
    out = ["# Site Map — Information Architecture", "",
           "The published navigation, as a tree. Labels are the visible nav titles;",
           "`file` notes the underlying page. This is the primary artifact for the",
           "Framework & IA agent and a key input for the UX & Adoption agent.", "", "```"]
    for ln in lines[start + 1:]:
        if ln and not ln.startswith((" ", "\t")):
            break  # next top-level key
        if not ln.strip():
            continue
        indent = len(ln) - len(ln.lstrip())
        item = ln.strip().lstrip("- ").strip()
        if ":" in item:
            label, ref = item.split(":", 1)
            ref = ref.strip()
            label = label.strip()
            suffix = f"  (file: {ref})" if ref and ref.endswith(".md") else ""
            out.append(" " * indent + f"- {label}{suffix}")
        else:
            # bare page reference -> derive a label from its H1
            ref = item
            label = h1_of(DOCS / ref) if ref.endswith(".md") else ref
            out.append(" " * indent + f"- {label}  (file: {ref})")
    out.append("```")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# content areas
# --------------------------------------------------------------------------- #
def build_controls() -> str:
    parts = ["# Area 1 — Controls (Research Review Package)", PROVENANCE,
             "\nThe 79-control catalog (4 pillars). Each control follows a 10-section",
             "template. The template and master index are included first so you can",
             "judge the *pattern*, then every control in full (internal links flattened).\n"]
    parts.append(section("Control Authoring Template (the 10-section pattern)"))
    parts.append(flatten_links(read(DOCS / "templates" / "control-setup-template.md")))
    parts.append(section("Master Control Index"))
    parts.append(flatten_links(read(DOCS / "controls" / "CONTROL-INDEX.md")))
    for pnum, (pname, folder) in PILLARS.items():
        pdir = DOCS / "controls" / folder
        parts.append(section(f"Pillar {pnum} — {pname}"))
        parts.append(flatten_links(read(pdir / "index.md")))
        files = sorted(pdir.glob(f"{pnum}.*.md"),
                       key=lambda p: [int(x) for x in p.stem.split("-")[0].split(".")])
        for f in files:
            parts.append("\n\n---\n\n")
            parts.append(flatten_links(read(f)))
    return "\n".join(parts)


def build_playbooks() -> str:
    pb = DOCS / "playbooks"
    parts = ["# Area 2 — Playbooks (Research Review Package)", PROVENANCE,
             "\nStep-by-step implementation procedures. The suite is large (~390 files,",
             "4 standard playbooks per control), so this package gives you: every category",
             "overview in full, a FULL representative sample (controls "
             + ", ".join(sorted(PLAYBOOK_SAMPLE_CONTROLS)) + "), and a complete structural",
             "listing of all playbooks so you can judge organisation and coverage.\n"]
    # category overviews / index pages
    parts.append(section("Playbook categories & overviews"))
    for idx in sorted(pb.rglob("index.md")):
        parts.append(f"\n### {idx.relative_to(pb).as_posix()}\n")
        parts.append(flatten_links(read(idx)))
    # representative full samples
    parts.append(section("Representative full playbooks"))
    ci = pb / "control-implementations"
    for ctrl in sorted(PLAYBOOK_SAMPLE_CONTROLS):
        d = ci / ctrl
        if not d.exists():
            continue
        parts.append(f"\n## Control {ctrl} — full playbook set\n")
        for f in sorted(d.glob("*.md")):
            parts.append("\n---\n")
            parts.append(flatten_links(read(f)))
    # full structural listing
    parts.append(section("Complete playbook inventory (structure)"))
    for f in sorted(pb.rglob("*.md")):
        rel = f.relative_to(pb).as_posix()
        parts.append(f"- {rel} — {h1_of(f)}")
    return "\n".join(parts)


def build_assessment() -> str:
    parts = ["# Area 3 — Assessment (Research Review Package)", PROVENANCE,
             "\nAn interactive, client-side **readiness assessment SPA** (no server). Because",
             "it is a JavaScript app, this package gives you: the page wrapper, the SPA's",
             "user-facing strings (labels/questions/results copy), and a walkthrough. To",
             "*see and run* it, open `_rendered-site/assessment/index.html` from the package",
             "(or the public URL). The Python scoring engine is summarised — it is back-end,",
             "less UX-relevant.\n"]
    parts.append(section("Assessment landing page (assessment/index.md)"))
    parts.append(flatten_links(read(DOCS / "assessment" / "index.md")))
    parts.append(section("SPA user-facing strings (i18n/en.json)"))
    en = read(DOCS / "assessment" / "i18n" / "en.json")
    parts.append("```json\n" + en + "\n```")
    parts.append(section("Scoring engine (summary)"))
    parts.append(flatten_links(read(BASE_DIR / "assessment" / "README.md"))[:8000]
                 or "(see assessment/README.md in the repo)")
    return "\n".join(parts)


def build_simple_area(num: int, title: str, subdir: str, blurb: str) -> str:
    d = DOCS / subdir
    parts = [f"# Area {num} — {title} (Research Review Package)", PROVENANCE, "\n" + blurb + "\n"]
    for f in sorted(d.rglob("*.md")):
        parts.append(section(f"{f.relative_to(d).as_posix()}"))
        parts.append(flatten_links(read(f)))
    return "\n".join(parts)


def build_start_here() -> str:
    return f"""# START HERE — FSI-AgentGov UX Review Package

{PROVENANCE}

## What this is
A self-contained snapshot of the **FSI Agent Governance Framework** documentation
site, packaged for external review. The site is a governance framework for
**Microsoft 365 AI agents in US financial-services organisations**.

- **Primary audience:** M365 administrators at US banks / broker-dealers / RIAs.
- **Secondary:** compliance officers, AI-governance leads. **Not** developers or end users.
- **Live site (optional):** {PUBLIC_URL}

## Why we're asking
The site sees **low traffic and is often perceived as dry technical documentation**.
We want it to be genuinely **useful, approachable, and engaging** for the audience
above — while staying accurate and appropriately hedged on compliance claims.

## How the package is organised
- `00-SITE-MAP.md` — the full navigation / information architecture.
- `area-1-controls.md` … `area-6-reference-and-downloads.md` — the content, by area,
  with internal links flattened so everything is self-contained.
- `_rendered-site/` — the actual built HTML site (open `index.html`) for true look-and-feel.
- `_pdf/` — PDF renditions (visual fidelity).
- `briefs/` — your task brief + the shared reviewer rubric + the response template.

## Your task
You will be assigned **one** brief in `briefs/` (Controls, Playbooks, Assessment,
Getting-Started & Onboarding, Framework & IA, Reference & Downloads, or UX & Adoption).
Review **only** your area, follow `briefs/REVIEWER-RUBRIC.md`, and return findings in
`briefs/RESPONSE-TEMPLATE.md` format. Critique what exists and propose concrete
improvements — you do **not** need repository access.
"""


def build_manifest(areas: dict[str, Path]) -> str:
    data = {
        "package": "FSI-AgentGov UX Review Package",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "framework_version": framework_version(),
        "commit": git_sha(),
        "public_url": PUBLIC_URL,
        "audience": "US financial-services M365 administrators",
        "review_model": "7 independent agents; everyone gets this full package, each a different brief",
        "areas": {k: v.name for k, v in areas.items()},
        "files": sorted(p.name for p in areas.values()),
    }
    return json.dumps(data, indent=2)


def copy_briefs(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if not TEMPLATES.exists():
        print(f"  WARNING: {TEMPLATES} not found — briefs not copied.")
        return
    for f in sorted(TEMPLATES.glob("*.md")):
        body = f.read_text(encoding="utf-8").replace("{{PROVENANCE}}", PROVENANCE.strip())
        (dest / f.name).write_text(body, encoding="utf-8")
        print(f"  brief: {f.name}")


def render_site(dest: Path) -> None:
    print("  building site (mkdocs build)...")
    try:
        subprocess.run(["mkdocs", "build", "-d", str(dest), "--quiet"],
                       cwd=BASE_DIR, check=True)
    except Exception as e:  # noqa: BLE001
        print(f"  WARNING: mkdocs build failed ({e}); skipping rendered site.")


def _find_browser() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ):
        if Path(p).exists():
            return p
    return None


def render_pdf(site_dir: Path, pdf_dir: Path) -> None:
    """Print a curated set of key built pages to PDF (visual fidelity).

    Uses a headless Chromium/Edge browser (commonly available locally and on CI);
    skips gracefully if none is found. Per-page PDFs of the highest-signal pages
    are enough to show reviewers "how it looks"; the full visual experience is the
    `_rendered-site/` HTML.
    """
    pdf_dir.mkdir(parents=True, exist_ok=True)
    browser = _find_browser()
    if not browser:
        print("  WARNING: no Chromium/Edge browser found; skipping PDF. "
              "Open _rendered-site/ and print to PDF manually.")
        return
    candidates = {
        "01-home": site_dir / "index.html",
        "02-getting-started": site_dir / "getting-started" / "index.html",
        "03-assessment": site_dir / "assessment" / "index.html",
        "04-framework": site_dir / "framework" / "index.html",
    }
    ctrl = next(iter(sorted((site_dir / "controls" / "pillar-1-security").glob("1.1-*/index.html"))), None)
    if ctrl:
        candidates["05-control-1.1"] = ctrl
    print(f"  rendering key-page PDFs via {Path(browser).name}...")
    for name, html in candidates.items():
        if not html.exists():
            continue
        out = pdf_dir / f"{name}.pdf"
        try:
            subprocess.run(
                [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
                 f"--print-to-pdf={out}", "--print-to-pdf-no-header", html.resolve().as_uri()],
                check=True, timeout=120,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            print(f"    {out.name}")
        except Exception as e:  # noqa: BLE001
            print(f"    WARNING: PDF failed for {name}: {e}")


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    global PROVENANCE
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--site", action="store_true", help="also build the rendered HTML site")
    ap.add_argument("--pdf", action="store_true", help="also render PDFs (needs weasyprint)")
    ap.add_argument("--zip", action="store_true", help="also zip the package folder")
    args = ap.parse_args(argv)

    PROVENANCE = (
        f"> Snapshot: framework v{framework_version()} · commit `{git_sha()}` · "
        f"{datetime.now(timezone.utc):%Y-%m-%d} UTC · source {PUBLIC_URL}\n"
    )

    pkg = OUTPUT / "FSI-AgentGov-Review-Package"
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True, exist_ok=True)
    print(f"Building review package -> {pkg}")

    (pkg / "00-START-HERE.md").write_text(build_start_here(), encoding="utf-8")
    (pkg / "00-SITE-MAP.md").write_text(build_site_map(), encoding="utf-8")
    if (BASE_DIR / "README.md").exists():
        (pkg / "README.md").write_text(flatten_links(read(BASE_DIR / "README.md")), encoding="utf-8")

    areas = {
        "controls": pkg / "area-1-controls.md",
        "playbooks": pkg / "area-2-playbooks.md",
        "assessment": pkg / "area-3-assessment.md",
        "getting-started": pkg / "area-4-getting-started.md",
        "framework-ia": pkg / "area-5-framework-and-ia.md",
        "reference-downloads": pkg / "area-6-reference-and-downloads.md",
    }
    areas["controls"].write_text(build_controls(), encoding="utf-8")
    areas["playbooks"].write_text(build_playbooks(), encoding="utf-8")
    areas["assessment"].write_text(build_assessment(), encoding="utf-8")
    areas["getting-started"].write_text(
        build_simple_area(4, "Getting Started & Onboarding", "getting-started",
                          "The first-run onboarding path for a new M365 admin."), encoding="utf-8")
    fw = build_simple_area(5, "Framework & Information Architecture", "framework",
                           "The conceptual/governance layer. Pair this with 00-SITE-MAP.md "
                           "(the global navigation) — your remit is how the WHOLE site is "
                           "structured and how the framework concepts hang together.")
    areas["framework-ia"].write_text(fw, encoding="utf-8")
    ref = build_simple_area(6, "Reference & Downloads", "reference",
                            "Supporting materials (glossary, RACI, regulatory mappings, role "
                            "catalog, license requirements). Downloads are role-based Excel "
                            "checklists under docs/downloads/ (described in docs/downloads/index.md).")
    ref += "\n\n" + section("Downloads (docs/downloads/index.md)") + flatten_links(
        read(DOCS / "downloads" / "index.md"))
    areas["reference-downloads"].write_text(ref, encoding="utf-8")

    (pkg / "MANIFEST.json").write_text(build_manifest(areas), encoding="utf-8")
    copy_briefs(pkg / "briefs")

    if args.site or args.pdf:
        site_dir = pkg / "_rendered-site"
        render_site(site_dir)
        if args.pdf:
            render_pdf(site_dir, pkg / "_pdf")

    if args.zip:
        print("  zipping (full — includes rendered site)...")
        shutil.make_archive(str(OUTPUT / "FSI-AgentGov-Review-Package"), "zip",
                            root_dir=pkg.parent, base_dir=pkg.name)
        # Lite zip for agents with tight upload limits: everything EXCEPT the
        # heavy _rendered-site/ (per-area .md + briefs + PDFs + manifest).
        lite = OUTPUT / "FSI-AgentGov-Review-Package-lite.zip"
        with zipfile.ZipFile(lite, "w", zipfile.ZIP_DEFLATED) as z:
            for f in pkg.rglob("*"):
                if f.is_file() and "_rendered-site" not in f.parts:
                    z.write(f, f.relative_to(pkg.parent))
        print(f"  zips: FSI-AgentGov-Review-Package.zip + {lite.name}")

    print("\nDone. Package files:")
    for p in sorted(pkg.iterdir()):
        size = p.stat().st_size if p.is_file() else sum(
            f.stat().st_size for f in p.rglob('*') if f.is_file())
        print(f"  {p.name}  ({size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
