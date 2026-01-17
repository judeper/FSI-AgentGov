# Control 1.21: Adversarial Input Logging - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Defender for Cloud Apps Policy Creation
**Portal Path:** Microsoft Defender Portal → Cloud Apps → Policies → Policy Management → Create policy
**What to capture:**
- Activity policy creation screen
- Policy name field showing "FSI-Adversarial-Input-Detection"
- App filter configured for Microsoft 365 Copilot/Copilot Studio
- Severity set to High

### Screenshot 2: Sentinel Analytics Rule Configuration
**Portal Path:** Microsoft Sentinel → Analytics → Create → Scheduled query rule
**What to capture:**
- Rule creation wizard
- KQL query pane with adversarial detection query
- Alert settings (frequency, threshold)
- MITRE ATT&CK mapping visible

### Screenshot 3: Detection Alert in Sentinel Incidents
**Portal Path:** Microsoft Sentinel → Incidents
**What to capture:**
- Incident list showing adversarial detection alert
- Incident severity (High/Critical)
- Alert details pane showing matched pattern

### Screenshot 4: Audit Log Search for Adversarial Patterns
**Portal Path:** Microsoft Purview → Audit → Search
**What to capture:**
- Search parameters configured for CopilotInteraction
- Search results showing detected adversarial input
- Export option visible

### Screenshot 5: Zone 3 Blocking Configuration (Optional)
**Portal Path:** Defender for Cloud Apps → Policies → Session policy
**What to capture:**
- Session policy configured for blocking
- App filter for Zone 3 agents
- Block action configured

---

## Notes for Verification
- All screenshots should be captured from a production or pre-production environment
- Sensitive data (user identities, actual attack content) should be redacted
- Include timestamps in screenshots for audit trail
- Verify UI matches documentation after Microsoft portal updates
