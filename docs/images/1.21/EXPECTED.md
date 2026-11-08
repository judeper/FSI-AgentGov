# Control 1.21: Adversarial Input Logging

**Specification reviewed:** 2026-11-06 (documentation alignment only; no tenant UI or screenshots verified)

These are text-only evidence requirements, not proof of deployed configuration. Apply the supported workload boundaries in the [portal walkthrough](../../playbooks/control-implementations/1.21/portal-walkthrough.md) and [verification playbook](../../playbooks/control-implementations/1.21/verification-testing.md). Record missing/unsupported evidence explicitly rather than marking it verified.

## Expected Screenshots

### Screenshot 1: Agent 365 Licensing, Settings, and Onboarding
**Portal Path:** Microsoft Defender portal → Settings → Security for AI (current applicable experience)
**What to capture:**
- Agent 365 eligibility, consolidated Security for AI Agents setting, and Copilot Studio / Foundry agent registry-observability coverage
- Current schema-validated `AgentsInfo` inventory and the tested agent's available identifiers; no legacy Power Platform handshake is assumed sufficient
- Separate Azure OpenAI / Foundry Models protection evidence where applicable; a model-plan toggle is not the agent entitlement
- Applicable agent threat-detection alert or real-time protection `BehaviorInfo` route, per the [Microsoft transition guidance](https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/transition-agent-security-to-agent-365)

### Screenshot 2: Sentinel Analytics Rule Configuration
**Portal Path:** Microsoft Sentinel → Analytics → Create → Scheduled query rule
**What to capture:**
- Rule creation wizard
- KQL query pane with adversarial detection query
- Alert settings (frequency, threshold)
- MITRE ATT&CK mapping visible

### Screenshot 3: Applicable Alert or Behavior Evidence
**Portal Path:** Microsoft Defender → Hunting → Advanced hunting; Microsoft Sentinel → Incidents where an incident route is configured
**What to capture:**
- Actual supported threat-detection alert or Agent 365 real-time protection behavior with raw identifiers and event/ingestion timestamps
- Available agent/workload identifiers, correlation confidence and configured incident linkage, where applicable
- Explicit unsupported, pending-ingestion, collection-error or missing-supported-signal reasons; not every probe generates a legacy alert or incident

### Screenshot 4: Audit Log Search for Adversarial Patterns
**Portal Path:** Microsoft Purview portal → Audit → Search
**What to capture:**
- Search parameters for the tested workload's actual operation/record category; native `CopilotInteraction` is not universal for every Copilot Studio thread
- Raw `Operation`, `RecordType`, `Workload`, `AppIdentity` and available agent/message/resource identifiers, with documented correlation confidence
- Audit metadata paired with separate detection/response evidence; neither a universal ConversationId join nor prompt-body pattern matching in audit metadata is assumed
- Export option visible
- The [Microsoft audit schema](https://learn.microsoft.com/en-us/purview/audit-copilot) used to validate the actual workload/field mapping

### Screenshot 5: Zone 3 Blocking Configuration (Optional)
**Portal Path:** Agent 365 real-time protection: Microsoft Defender → Settings → Security for AI → Policies & rules → Real-time protection; separate supported experiences where applicable
**What to capture:**
- Actual assigned policy and supported test surface, with representative blocking outcomes where required
- Redefined Agent 365 Block rules in the current policy experience and applicable `BehaviorInfo` evidence; configuration alone does not prove runtime blocking
- Distinguish Copilot Studio real-time protection through Defender for Cloud Apps, which the transition guidance describes as unchanged; do not assume a generic session policy covers all agents

---

## Verification Focus
- All screenshots should be captured from a production or pre-production environment
- Sensitive data (user identities, actual attack content) should be redacted
- Include timestamps in screenshots for audit trail
- Verify UI matches documentation after Microsoft portal updates

---

## Screenshot Organization

Use these filenames under the local-only `maintainers-local\tenant-evidence\` location; do not commit screenshots:
- `1.21-01-defender-policy-creation.png` — Current Agent 365 licensing/settings/registry-observability evidence
- `1.21-02-sentinel-analytics-rule.png` — Sentinel scheduled query rule
- `1.21-03-sentinel-incident-alert.png` — Applicable raw alert/behavior and configured incident evidence
- `1.21-04-audit-log-adversarial.png` — Purview audit log search results
- `1.21-05-zone3-blocking-config.png` — Applicable assigned Zone 3 blocking policy and observed outcomes
