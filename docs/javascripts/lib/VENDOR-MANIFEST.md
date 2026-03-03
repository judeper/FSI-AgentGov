# Vendor Library Manifest

Libraries vendored for the Governance Readiness Assessment tool.
Lazy-loaded only on the assessment page.

| Library | Version | File | SHA-256 (hex) | SRI Hash (base64) | Source |
|---------|---------|------|---------------|-------------------|--------|
| Chart.js | 4.4.7 | chart.min.js | `206b6e8b...5d0e` | `sha256-IGtui7APx7uix+6AykHbPp4FunvgqjWr66nP1TV/XQ4=` | https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js |
| SheetJS | 0.18.5 | xlsx.full.min.js | `c9506197...3c99` | `sha256-yVBhl8r4CaB1tt7h2g02+xnacVj/6KiOewyWxdhiPJk=` | https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js |

## Update Instructions

1. Download new version from the CDN URL above
2. Verify the SHA-256 hash: `sha256sum docs/javascripts/lib/<filename>`
3. Update this manifest with new version and hash
4. Test: assessment page loads and exports work correctly

## Verification

```bash
# Verify vendored files match recorded hex hashes
sha256sum docs/javascripts/lib/chart.min.js docs/javascripts/lib/xlsx.full.min.js

# Generate SRI-compatible base64 hashes (for integrity attributes)
openssl dgst -sha256 -binary docs/javascripts/lib/chart.min.js | openssl base64 -A
openssl dgst -sha256 -binary docs/javascripts/lib/xlsx.full.min.js | openssl base64 -A
```

## SheetJS Note

SheetJS v0.18.5 is the latest version available on jsdelivr CDN. The library
moved to a commercial model after v0.18.x; newer versions (0.19+, 0.20+) are
not available on public CDNs. For this project's use case (basic XLSX export),
v0.18.5 is functionally sufficient. No known security vulnerabilities affect
the read-only/write-only usage patterns in the assessment tool.
