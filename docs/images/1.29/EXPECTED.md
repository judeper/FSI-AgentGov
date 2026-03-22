# Control 1.29: Global Secure Access: Network Controls for Copilot Studio Agents - Screenshot Specifications

## Required Screenshots

### Screenshot 1: Power Platform environment forwarding toggle
**Portal Path:** Power Platform admin center -> Environments -> [Environment] -> Settings -> Global Secure Access
**What to capture:**
- GSA forwarding enabled for the target environment
- Environment name and zone context
- Save/apply action visible

### Screenshot 2: Global Secure Access baseline profile
**Portal Path:** Microsoft Entra admin center -> Global Secure Access -> Security profiles -> Baseline profile
**What to capture:**
- Web content filtering policy
- Threat intelligence filtering settings
- File filtering settings

### Screenshot 3: Blocked request log evidence
**Portal Path:** Microsoft Entra admin center -> Global Secure Access -> Traffic logs
**What to capture:**
- Blocked outbound request tied to agent traffic
- Destination, policy match, and action
- Timestamp and tenant context

### Screenshot 4: Sentinel or Log Analytics query
**Portal Path:** Microsoft Sentinel or Log Analytics -> Query window
**What to capture:**
- Query showing agent outbound traffic events
- Allowed vs blocked actions
- Export or save capability

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
1.29_Screenshot-[Number]_[Description]_[YYYYMMDD].png
```

Store screenshots in the `docs/images/1.29/` directory for local maintainer verification.

---

[Back to Control 1.29](../../controls/pillar-1-security/1.29-global-secure-access-network-controls.md)
