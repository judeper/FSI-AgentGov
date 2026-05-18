import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / 'assessment' / 'manifest' / 'controls.json'
CONTROL_INDEX_PATH = REPO_ROOT / 'docs' / 'controls' / 'CONTROL-INDEX.md'
SCAN_ROOTS = [
    REPO_ROOT / 'docs' / 'controls',
    REPO_ROOT / 'docs' / 'playbooks',
    REPO_ROOT / 'docs' / 'framework',
    REPO_ROOT / 'docs' / 'reference',
]
EXPECTED_CONTROL_COUNT = 78
CONTROL_ID_PATTERN = r'[1-4]\.(?:[1-9]|1\d|2\d)'
CONTROL_ID_RE = re.compile(rf'\b({CONTROL_ID_PATTERN})\b')
CONTROL_INDEX_ROW_RE = re.compile(
    rf'^\|\s*(?P<id>{CONTROL_ID_PATTERN})\s*\|\s*\[(?P<name>[^\]]+)\]\(',
    re.MULTILINE,
)
BRACKETED_CONTROL_RE = re.compile(
    rf'\[Control\s+(?P<id>{CONTROL_ID_PATTERN})(?:\s*\((?P<paren_label>[^)]+)\))?\]',
    re.IGNORECASE,
)
CONTROL_PAREN_RE = re.compile(
    rf'\bControl\s+(?P<id>{CONTROL_ID_PATTERN})\s*\((?P<label>[^)]+)\)',
    re.IGNORECASE,
)
BARE_PAREN_RE = re.compile(rf'(?<![\w.])(?P<id>{CONTROL_ID_PATTERN})\s*\((?P<label>[^)]+)\)')
CONTROL_LIST_RE = re.compile(
    rf'\bControls?\s+(?P<body>{CONTROL_ID_PATTERN}(?:\s*(?:,\s*|,?\s+(?:and|or)\s+|&\s*){CONTROL_ID_PATTERN})+)',
    re.IGNORECASE,
)
SIMPLE_CONTROL_RE = re.compile(rf'\bControl\s+(?P<id>{CONTROL_ID_PATTERN})\b', re.IGNORECASE)
CODE_FENCE_RE = re.compile(r'^\s*(```|~~~)')
URL_RE = re.compile(r'https?://\S+')
ANCHOR_LINK_RE = re.compile(r'\[[^\]]+\]\(#.*?\)')
INLINE_CODE_RE = re.compile(r'`[^`]*`')


@dataclass
class Reference:
    control_id: str
    found_text: str
    label: str | None
    start: int
    end: int


@dataclass
class Finding:
    file: str
    line: int
    severity: str
    found_text: str
    control_id: str
    expected: str


def load_manifest_controls() -> dict[str, str]:
    data = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    return {str(item['id']).strip(): str(item['name']).strip() for item in data if item.get('id') and item.get('name')}


def load_control_index() -> dict[str, str]:
    content = CONTROL_INDEX_PATH.read_text(encoding='utf-8')
    return {match.group('id'): match.group('name').strip() for match in CONTROL_INDEX_ROW_RE.finditer(content)}


def build_canonical_map() -> dict[str, str]:
    manifest_controls = load_manifest_controls()
    index_controls = load_control_index()
    canonical: dict[str, str] = {}

    for control_id in sorted(set(manifest_controls) | set(index_controls), key=sort_control_id):
        canonical[control_id] = index_controls.get(control_id) or manifest_controls.get(control_id, '')

    if len(canonical) != EXPECTED_CONTROL_COUNT:
        print(
            f'ERROR: expected {EXPECTED_CONTROL_COUNT} canonical controls but found {len(canonical)}',
            file=sys.stderr,
        )
        raise SystemExit(1)

    return canonical


def sort_control_id(control_id: str) -> tuple[int, int]:
    pillar, number = control_id.split('.')
    return int(pillar), int(number)


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        files.extend(path for path in root.rglob('*.md') if path.name != 'CONTROL-INDEX.md')
    return sorted(files)


def normalize_text(value: str) -> str:
    value = value.casefold().replace('&', ' and ')
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return ' '.join(value.split())


GENERIC_LABEL_TOKENS = {
    'a',
    'an',
    'and',
    'by',
    'control',
    'controls',
    'detection',
    'for',
    'governance',
    'management',
    'monitoring',
    'only',
    'operation',
    'operations',
    'or',
    'plane',
    'policies',
    'policy',
    'premium',
    'program',
    'reporting',
    'review',
    'reviews',
    'setup',
    'testing',
    'the',
    'to',
    'troubleshooting',
    'under',
    'update',
    'verification',
    'walkthrough',
    'with',
}


def meaningful_tokens(value: str) -> set[str]:
    tokens = normalize_text(value).split()
    expanded_tokens: set[str] = set()
    for token in tokens:
        if token in GENERIC_LABEL_TOKENS:
            continue
        expanded_tokens.add(token)
        if token.endswith('s') and len(token) <= 5:
            expanded_tokens.add(token[:-1])
    return {token for token in expanded_tokens if len(token) > 1}



def matching_token_count(label: str, canonical_name: str) -> int:
    label_tokens = meaningful_tokens(label)
    canonical_tokens = meaningful_tokens(canonical_name)
    matches = 0
    for label_token in label_tokens:
        if any(
            label_token == canonical_token
            or label_token.startswith(canonical_token)
            or canonical_token.startswith(label_token)
            for canonical_token in canonical_tokens
        ):
            matches += 1
    return matches



def label_matches_canonical(label: str, canonical_name: str) -> bool:
    label_normalized = normalize_text(label)
    canonical_normalized = normalize_text(canonical_name)
    if not label_normalized:
        return False
    if label_normalized in canonical_normalized or canonical_normalized in label_normalized:
        return True

    label_tokens = meaningful_tokens(label)
    canonical_tokens = meaningful_tokens(canonical_name)
    if not label_tokens or not canonical_tokens:
        return False
    if label_tokens.issubset(canonical_tokens) or canonical_tokens.issubset(label_tokens):
        return True
    return matching_token_count(label, canonical_name) >= 1



def best_canonical_label_match(label: str, canonical: dict[str, str], referenced_control_id: str) -> str | None:
    best_control_id: str | None = None
    best_score = 0
    tied = False
    label_normalized = normalize_text(label)

    for control_id, control_name in canonical.items():
        if control_id == referenced_control_id:
            continue

        canonical_normalized = normalize_text(control_name)
        if label_normalized and (label_normalized in canonical_normalized or canonical_normalized in label_normalized):
            score = 100
        else:
            score = matching_token_count(label, control_name)

        if score > best_score:
            best_control_id = control_id
            best_score = score
            tied = False
        elif score and score == best_score:
            tied = True

    if tied:
        return None
    if best_score >= 2 or best_score == 100:
        return best_control_id
    return None



def should_validate_label(label: str | None) -> bool:
    if not label:
        return False

    stripped = label.strip()
    if not stripped or not stripped[0].isalpha():
        return False

    starts_like_title = stripped[0].isupper() or (len(stripped) > 1 and stripped[0].islower() and stripped[1].isupper())
    return starts_like_title and len(meaningful_tokens(stripped)) >= 2


EXCLUDED_BARE_PREFIX_WORDS = (
    'section',
    'figure',
    'table',
    'item',
    'step',
    'rule',
    'iso',
    'iso/iec',
)


def is_excluded_bare_reference(line: str, match_start: int) -> bool:
    prefix = line[max(0, match_start - 16):match_start].lower()
    if prefix.endswith('v'):
        return True
    rstripped = prefix.rstrip()
    if rstripped.endswith('§'):
        return True
    for word in EXCLUDED_BARE_PREFIX_WORDS:
        if prefix.endswith(word + ' '):
            return True
    return False


def overlaps(existing_spans: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(start < existing_end and end > existing_start for existing_start, existing_end in existing_spans)


def cleaned_line(line: str) -> str:
    without_urls = URL_RE.sub('', line)
    without_anchors = ANCHOR_LINK_RE.sub('', without_urls)
    return INLINE_CODE_RE.sub('', without_anchors)


def collect_references(line: str) -> list[Reference]:
    references: list[Reference] = []
    occupied_spans: list[tuple[int, int]] = []
    filtered_line = cleaned_line(line)

    def register_reference(control_id: str, found_text: str, label: str | None, start: int, end: int) -> None:
        if overlaps(occupied_spans, start, end):
            return
        occupied_spans.append((start, end))
        references.append(Reference(control_id=control_id, found_text=found_text, label=label, start=start, end=end))

    for pattern in (BRACKETED_CONTROL_RE, CONTROL_PAREN_RE, BARE_PAREN_RE):
        for match in pattern.finditer(filtered_line):
            if pattern is BARE_PAREN_RE and is_excluded_bare_reference(filtered_line, match.start()):
                continue
            label = match.groupdict().get('paren_label') or match.groupdict().get('label')
            register_reference(match.group('id'), match.group(0), label, match.start(), match.end())

    for match in CONTROL_LIST_RE.finditer(filtered_line):
        body = match.group('body')
        for id_match in CONTROL_ID_RE.finditer(body):
            start = match.start('body') + id_match.start(1)
            end = match.start('body') + id_match.end(1)
            register_reference(id_match.group(1), id_match.group(1), None, start, end)

    for match in SIMPLE_CONTROL_RE.finditer(filtered_line):
        register_reference(match.group('id'), match.group(0), None, match.start(), match.end())

    return references


def scan_files(canonical: dict[str, str]) -> tuple[int, int, list[Finding], list[Finding]]:
    files_scanned = 0
    refs_found = 0
    broken_id: list[Finding] = []
    mislabeled: list[Finding] = []

    for path in iter_markdown_files():
        if 'maintainers-local' in path.parts:
            continue

        files_scanned += 1
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        lines = path.read_text(encoding='utf-8').splitlines()
        in_code_fence = False

        for line_number, line in enumerate(lines, start=1):
            if CODE_FENCE_RE.match(line):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            for reference in collect_references(line):
                refs_found += 1
                canonical_name = canonical.get(reference.control_id)
                if not canonical_name:
                    broken_id.append(
                        Finding(
                            file=relative_path,
                            line=line_number,
                            severity='BROKEN-ID',
                            found_text=reference.found_text,
                            control_id=reference.control_id,
                            expected='<existing canonical control>',
                        )
                    )
                    continue

                has_explicit_control_prefix = 'control' in reference.found_text.casefold()
                if has_explicit_control_prefix and should_validate_label(reference.label):
                    label = reference.label or ''
                    if not label_matches_canonical(label, canonical_name):
                        likely_control_id = best_canonical_label_match(label, canonical, reference.control_id)
                        expected_text = canonical_name
                        if likely_control_id and likely_control_id in canonical:
                            expected_text = (
                                f'{canonical_name} '
                                f'(label appears to match Control {likely_control_id}: {canonical[likely_control_id]})'
                            )
                        mislabeled.append(
                            Finding(
                                file=relative_path,
                                line=line_number,
                                severity='MISLABELED',
                                found_text=reference.found_text,
                                control_id=reference.control_id,
                                expected=expected_text,
                            )
                        )

    return files_scanned, refs_found, broken_id, mislabeled


def main() -> int:
    canonical = build_canonical_map()
    files_scanned, refs_found, broken_id, mislabeled = scan_files(canonical)

    for finding in broken_id + mislabeled:
        print(
            f'{finding.file}:{finding.line}: {finding.severity}: {finding.found_text} — expected {finding.expected}',
            file=sys.stderr,
        )

    summary = {
        'files_scanned': files_scanned,
        'refs_found': refs_found,
        'broken_id': [asdict(finding) for finding in broken_id],
        'mislabeled': [asdict(finding) for finding in mislabeled],
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if broken_id or mislabeled else 0


if __name__ == '__main__':
    raise SystemExit(main())
