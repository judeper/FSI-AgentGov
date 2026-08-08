# Vendor Library Manifest

Libraries vendored for the Governance Readiness Assessment tool and the
documentation site.

Lazy-load scope:

- `lib/chart.min.js`, `lib/xlsx.full.min.js` — loaded by the assessment
  SPA only. Chart.js is loaded by `docs/javascripts/assessment-loader.js`;
  SheetJS is lazy-loaded by the XLSX export path in
  `docs/javascripts/assessment-app.js`. SRI literals are CI-verified by
  `scripts/verify-sheetjs-sri.mjs`, and the shipped SheetJS version/source/hash
  are fail-closed by `scripts/verify-vendored-runtime.mjs`.
- `vendor/mermaid.min.js` — loaded site-wide on any page that contains
  a Mermaid block. Material 9.7.6's bundle dynamically appends a
  `<script>` tag pointing at `https://unpkg.com/mermaid@11/...`; we
  intercept that appendChild call in `overrides/main.html` and rewrite
  the URL to the local vendored copy with SRI pinned.

| Library  | Version | File                  | SHA-256 (hex) | SRI Hash (base64) | Source |
|----------|---------|-----------------------|---------------|-------------------|--------|
| Chart.js | 4.4.7   | lib/chart.min.js      | `206b6e8b...5d0e` | `sha256-IGtui7APx7uix+6AykHbPp4FunvgqjWr66nP1TV/XQ4=` | https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js |
| SheetJS  | 0.20.3  | lib/xlsx.full.min.js  | `cc015130aa8521e7f088f88898eba949ccdcbfb38df0bd129b44b7273c3a6f41` | `sha256-zAFRMKqFIefwiPiImOupSczcv7ON8L0Sm0S3Jzw6b0E=` | https://cdn.sheetjs.com/xlsx-0.20.3/xlsx-0.20.3.tgz (dist/xlsx.full.min.js) |
| Mermaid  | 11.15.0 | vendor/mermaid.min.js | `70137e77bb273bb2ef972b86e8b0400cca8be53cb25bfc45911a186dc98665de` | `sha256-cBN+d7snO7LvlyuG6LBADMqL5TyyW/xFkRoYbcmGZd4=` | https://unpkg.com/mermaid@11/dist/mermaid.min.js |

## Update Instructions

1. Resolve the official package from the locked URL in `package-lock.json`;
   do not substitute an unpinned mirror or public CDN.
2. Extract the browser artifact from the package (`dist/xlsx.full.min.js`) and
   verify its SHA-256 hash: `sha256sum docs/javascripts/<lib|vendor>/<filename>`
3. Update this manifest with the reviewed version, full hash, SRI, and source.
4. Update the SRI literal in:
   - `docs/javascripts/assessment-loader.js` (for `lib/*` SPA libs), or
   - `docs/javascripts/assessment-app.js` (for the SheetJS export path), or
   - `overrides/main.html` (for `vendor/mermaid.min.js`)
5. Update `scripts/verify-vendored-runtime.mjs` only after security review of
   the replacement version and artifact.
6. Test: assessment page loads + exports work; any Mermaid-bearing
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

The deployed SPA uses the official SheetJS `xlsx@0.20.3` browser artifact
from the locked `cdn.sheetjs.com` package tarball. The older 0.18.x runtime is
within known high-severity advisory ranges and is explicitly rejected by the
vendored-runtime policy; usage patterns do not waive a shipped dependency
vulnerability. The package-lock integrity, on-disk SHA-256, SRI literal, and
manifest source/version must agree before the runtime is accepted.

## Mermaid Note

Mermaid v11.15.0 matches the major version Material 9.7.6 requests at
runtime (`https://unpkg.com/mermaid@11/dist/mermaid.min.js` resolves
to `mermaid@11.15.0` as of the vendoring date). Material's bundle
auto-detects `.mermaid` elements and lazy-loads the script — our
intercept rewrites the URL while preserving Material's theme/palette
init flow. To rotate to a newer 11.x release, refresh the file and
update the SRI literal in both this manifest and `overrides/main.html`.
