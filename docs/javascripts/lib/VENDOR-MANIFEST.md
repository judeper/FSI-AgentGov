# Vendor Library Manifest

Libraries vendored for the Governance Readiness Assessment tool and the
documentation site.

Lazy-load scope:

- `lib/chart.min.js`, `lib/xlsx.full.min.js` — loaded by the assessment
  SPA only (`docs/javascripts/assessment-loader.js`). SRI literals live
  in the loader's `SRI_HASHES` dict and are CI-verified by
  `scripts/verify-sheetjs-sri.mjs`.
- `vendor/mermaid.min.js` — loaded site-wide on any page that contains
  a Mermaid block. Material 9.7.6's bundle dynamically appends a
  `<script>` tag pointing at `https://unpkg.com/mermaid@11/...`; we
  intercept that appendChild call in `overrides/main.html` and rewrite
  the URL to the local vendored copy with SRI pinned.

| Library  | Version | File                  | SHA-256 (hex) | SRI Hash (base64) | Source |
|----------|---------|-----------------------|---------------|-------------------|--------|
| Chart.js | 4.4.7   | lib/chart.min.js      | `206b6e8b...5d0e` | `sha256-IGtui7APx7uix+6AykHbPp4FunvgqjWr66nP1TV/XQ4=` | https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js |
| SheetJS  | 0.18.5  | lib/xlsx.full.min.js  | `c9506197...3c99` | `sha256-yVBhl8r4CaB1tt7h2g02+xnacVj/6KiOewyWxdhiPJk=` | https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js |
| Mermaid  | 11.15.0 | vendor/mermaid.min.js | `70137e77bb273bb2ef972b86e8b0400cca8be53cb25bfc45911a186dc98665de` | `sha256-cBN+d7snO7LvlyuG6LBADMqL5TyyW/xFkRoYbcmGZd4=` | https://unpkg.com/mermaid@11/dist/mermaid.min.js |

## Update Instructions

1. Download new version from the CDN URL above
2. Verify the SHA-256 hash: `sha256sum docs/javascripts/<lib|vendor>/<filename>`
3. Update this manifest with new version and hash
4. Update the SRI literal in:
   - `docs/javascripts/assessment-loader.js` (for `lib/*` SPA libs), or
   - `overrides/main.html` (for `vendor/mermaid.min.js`)
5. Test: assessment page loads + exports work; any Mermaid-bearing
   docs page renders SVGs (zero `pre.mermaid` survivors, zero CSP
   violations)

## Verification

```bash
# Verify vendored files match recorded hex hashes
sha256sum docs/javascripts/lib/chart.min.js docs/javascripts/lib/xlsx.full.min.js docs/javascripts/vendor/mermaid.min.js

# Generate SRI-compatible base64 hashes (for integrity attributes)
openssl dgst -sha256 -binary docs/javascripts/lib/chart.min.js      | openssl base64 -A
openssl dgst -sha256 -binary docs/javascripts/lib/xlsx.full.min.js  | openssl base64 -A
openssl dgst -sha256 -binary docs/javascripts/vendor/mermaid.min.js | openssl base64 -A
```

## SheetJS Note

SheetJS v0.18.5 is the latest version available on jsdelivr CDN. The library
moved to a commercial model after v0.18.x; newer versions (0.19+, 0.20+) are
not available on public CDNs. For this project's use case (basic XLSX export),
v0.18.5 is functionally sufficient. No known security vulnerabilities affect
the read-only/write-only usage patterns in the assessment tool.

## Mermaid Note

Mermaid v11.15.0 matches the major version Material 9.7.6 requests at
runtime (`https://unpkg.com/mermaid@11/dist/mermaid.min.js` resolves
to `mermaid@11.15.0` as of the vendoring date). Material's bundle
auto-detects `.mermaid` elements and lazy-loads the script — our
intercept rewrites the URL while preserving Material's theme/palette
init flow. To rotate to a newer 11.x release, refresh the file and
update the SRI literal in both this manifest and `overrides/main.html`.
