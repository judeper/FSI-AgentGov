# Documentation Quality Findings

**Method:** Structural scan of all 71 controls + deep review of 33 sampled controls, 12 framework docs, 21 reference docs. Cross-reference integrity validated against mkdocs.yml and filesystem.

## Summary

| Finding Type | Count |
|-------------|-------|
| Incorrect (wrong names, stale data, factual errors) | 17 |
| Missing (absent fields, unmapped controls, no citations) | 7 |
| Ambiguity (conflicting info, unclear scope, inconsistency) | 6 |
| Gap (missing content, structural issues) | 5 |
| Language (prohibited overclaims) | 1 |
| **Total** | **36** |

## Cross-Reference Integrity ✅

| Check | Scope | Result |
|-------|-------|--------|
| mkdocs.yml nav → file existence | 474 entries | ✅ PASS — all entries resolve |
| Control → Playbook links | 71 controls × 4 playbooks | ✅ PASS — all 284 playbooks exist |
| Control → Solution cross-refs | 25 solutions in solutions-index.md | ✅ PASS — all match Solutions repo |
| CONTROL-INDEX.md completeness | 71 controls | ✅ PASS — exact match with filesystem |

---

## Findings by Category

### Incorrect (17)

#### Role Naming (12 findings)

| # | Control | Issue | File Path |
|---|---------|-------|-----------|
| 1 | 1.5 | "Entra AI Admin" → should be "AI Administrator" | pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md |
| 2 | 1.8 | "Power Platform Administrator" → "Power Platform Admin" | pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md |
| 3 | 1.11 | "Copilot Studio Environment Admin" → "Environment Admin" | pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md |
| 4 | 1.19 | "Purview eDiscovery Admin" → "Purview eDiscovery Roles" | pillar-1-security/1.19-ediscovery-for-agent-interactions.md |
| 5 | 3.4 | "Platform Admin" → "Power Platform Admin" | pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md |
| 6 | 3.8 | "M365 Administrator" not in role catalog | pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md |
| 7 | 3.9 | "Platform Admin" → "Power Platform Admin" | pillar-3-reporting/3.9-microsoft-sentinel-integration.md |
| 8 | 4.2 | "Site Collection Admin" → "SharePoint Site Collection Admin" | pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md |
| 9 | 4.3 | "Records Management" → "Purview Records Manager" | pillar-4-sharepoint/4.3-site-and-document-retention-management.md |
| 10 | 4.4 | "Security Admin" → "Entra Security Admin" | pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md |
| 11 | 4.7 | "Microsoft 365 Admin" not in role catalog | pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md |
| 12 | 4.7 | Related Controls table uses external Learn URL instead of internal cross-reference | pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md |

#### Data Accuracy (5 findings)

| # | File | Issue | Path |
|---|------|-------|------|
| 13 | executive-summary.md | Pillar breakdown claims 64 total controls; actual is 71 | docs/framework/executive-summary.md |
| 14 | governance-fundamentals.md | Header says "71 controls" but table shows 25+22+10+7=64 | docs/framework/governance-fundamentals.md |
| 15 | glossary.md | FINRA 4512 labeled "Continuing Education"; actually "Customer Account Information" (CE is Rule 1240) | docs/reference/glossary.md |
| 16 | solutions-index.md | Compliance Dashboard claims "62 controls"; framework has 71 | docs/reference/solutions-index.md |
| 17 | license-requirements.md | Uses "Copilot for Enterprise" — official name is "Microsoft 365 Copilot" | docs/reference/license-requirements.md |

### Missing (7)

| # | File | Issue | Path |
|---|------|-------|------|
| 1 | 1.5 | Role "Purview Data Security AI Admin" not in role catalog | pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md |
| 2 | 1.11 | Role "Authentication Administrator" not in role catalog | pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md |
| 3 | 1.19 | Role "Microsoft Purview Admin" not in role catalog | pillar-1-security/1.19-ediscovery-for-agent-interactions.md |
| 4 | 3.11 | Missing "Last Verified" header field (present in all other Pillar 3 controls) | pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md |
| 5 | 3.12 | Missing "Last Verified" header field (present in all other Pillar 3 controls) | pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md |
| 6 | license-requirements.md | Controls 1.25–1.28, 2.22–2.24, 3.11–3.12 (7 controls) have no license mapping | docs/reference/license-requirements.md |
| 7 | executive-summary.md | Retention periods (7yr, 10yr) cited without regulatory source references | docs/framework/executive-summary.md |

### Ambiguity (6)

| # | File | Issue | Path |
|---|------|-------|------|
| 1 | Instructions | Section 8 called "Implementation Guides" in instructions but "Implementation Playbooks" in template and all controls | .github/copilot-instructions.md |
| 2 | Multiple controls | Operational roles (SOC Analyst, Cloud Security Architect, Model Risk Manager, Copilot Studio Agent Author) used across controls but not in role catalog | Multiple |
| 3 | solutions-index.md | Warns to act "before February 2026" but doc dated February 2026 — stale deadline | docs/reference/solutions-index.md |
| 4 | Multiple files | Footer versions inconsistent: some say v1.2 Jan 2026, others v1.2.41 Feb 2026 | docs/framework/*.md, docs/reference/*.md |
| 5 | executive-summary.md | Zone 3 agent approval has two Accountable (A) parties in RACI — best practice is one | docs/framework/executive-summary.md |
| 6 | quick-start.md | Claims "Compliance: None" for Zone 1; zones-and-tiers.md properly hedges | docs/getting-started/quick-start.md |

### Gap (5)

| # | File | Issue | Path |
|---|------|-------|------|
| 1 | 1.11 | Missing `---` separator before Implementation Playbooks | pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md |
| 2 | 3.8 | Missing `---` separator before Implementation Playbooks | pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md |
| 3 | 3.11 | Missing `---` separator before Implementation Playbooks | pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md |
| 4 | 3.12 | Missing `---` separator before Implementation Playbooks | pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md |
| 5 | regulatory-framework.md | CFTC Rule 1.31 in project scope but no dedicated section | docs/framework/regulatory-framework.md |

### Language (1)

| # | File | Issue | Path |
|---|------|-------|------|
| 1 | solutions-index.md | "Ensures consistent zone classification" — prohibited overclaim | docs/reference/solutions-index.md |
