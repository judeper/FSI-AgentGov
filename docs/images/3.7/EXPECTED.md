# Control 3.7: PPAC Security Posture Assessment - Screenshot Specifications

## Required Screenshots

| Filename | Portal | Navigation Path | What to Capture |
|----------|--------|-----------------|-----------------|
| `01-ppac-security-home.png` | PPAC | Security | Security dashboard home |
| `02-ppac-security-score.png` | PPAC | Security → Score | Security posture score |
| `03-ppac-security-recommendations.png` | PPAC | Security → Recommendations | Improvement recommendations |
| `04-ppac-security-details.png` | PPAC | Recommendation → Details | Recommendation details |
| `05-ppac-security-history.png` | PPAC | Security → History | Score history/trends |
| `06-entra-verify-admin.png` | Entra | User → Roles | Admin role verification |
| `07-purview-audit-check.png` | Purview | Audit | Audit logging enabled |
| `08-env-blocked-attachments.png` | PPAC | Environments → [env] → Settings → Privacy + Security | Blocked attachment extensions list |
| `09-env-blocked-mimetypes.png` | PPAC | Environments → [env] → Settings → Privacy + Security | Blocked MIME types list |
| `10-env-inactivity-timeout.png` | PPAC | Environments → [env] → Settings → Privacy + Security | Inactivity timeout setting (≤ 120 min) |
| `11-env-session-expiration.png` | PPAC | Environments → [env] → Settings → Privacy + Security | Session expiration setting (≤ 1440 min) |
| `12-env-csp-enforcement.png` | PPAC | Environments → [env] → Settings → Privacy + Security | Content Security Policy enforcement toggle |

## Notes for Verification

- Security score is visible
- Recommendations are actionable
- History shows improvement trend
- Admin access is confirmed
- Environment security settings match hardening baseline items #28-32
- Blocked attachments include all 43 critical extensions
- Timeout values are within organizational policy thresholds

---

[Back to Control 3.7](../../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md)
