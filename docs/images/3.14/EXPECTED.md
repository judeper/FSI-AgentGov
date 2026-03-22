# Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry - Screenshot Specifications

## Required Screenshots

### Screenshot 1: SDK configuration in code or environment
**Portal Path:** Code editor or deployment settings
**What to capture:**
- Observability SDK package reference
- Exporter environment variable
- Token resolver or credential configuration

### Screenshot 2: Entra agent sign-in logs
**Portal Path:** Microsoft Entra admin center -> Monitoring & health -> Sign-in logs
**What to capture:**
- Filter Is Agent = Yes
- Agent sign-in record
- Agent-specific fields visible

### Screenshot 3: Diagnostic settings for MicrosoftServicePrincipalSignInLogs
**Portal Path:** Microsoft Entra admin center -> Monitoring & health -> Diagnostic settings
**What to capture:**
- MicrosoftServicePrincipalSignInLogs selected
- Destinations configured
- Save/update action visible

### Screenshot 4: Purview or Defender telemetry confirmation
**Portal Path:** Purview Audit or Microsoft Defender
**What to capture:**
- Agent session or exception telemetry record
- Timestamp and agent context
- Evidence of ingestion success

---

## Notes for Verification
- Capture from a pre-production or demo tenant when possible
- Include timestamps to demonstrate currency
- Redact tenant-specific sensitive values before retaining screenshots
- Re-verify after major Microsoft portal changes

---

## Screenshot Naming Convention

Save screenshots with the following naming format:
```
3.14_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Store screenshots in the `docs/images/3.14/` directory for local maintainer verification.

---

[Back to Control 3.14](../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md)
