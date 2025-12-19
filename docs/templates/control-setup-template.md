# Control [X.X]: [Control Name]

## Overview

**Control ID:** [X.X]  
**Control Name:** [Control Name]  
**Regulatory Reference:** [Regulations]  
**Setup Time:** [Time estimate]  

---

## Prerequisites

- **License Required:** [Specific Microsoft license] - [Learn more](https://learn.microsoft.com/en-us/...)
- **Primary Owner Admin Role:** [Use canonical role name from `reference/role-catalog.md`]
- **Dependencies:** [List any controls that must be configured first]
- **Additional Requirements:** [e.g., Managed Environments, specific features]

---

## Governance Levels

### Baseline (Level 1)

[Description of baseline implementation - minimal requirements]

### Recommended (Level 2-3)

[Description of recommended implementation - best practices for Zone 2+]

### Regulated/High-Risk (Level 4)

[Description of strictest implementation - comprehensive controls for Zone 3]

---

## Setup & Configuration

### Portal-Based Configuration (Primary Method)

**Step 1: [First Major Configuration Step]**

1. Sign in to the **[Admin Center Name]** ([https://admin.portal.com](https://admin.portal.com))
2. Navigate to **[Menu]** > **[Submenu]** > **[Option]**
3. Select **[Button/Toggle]**
4. Configure the following settings:
   - **[Setting 1]**: [Value/recommendation]
   - **[Setting 2]**: [Value/recommendation]
5. Select **Save** or **Apply**

[Screenshot needed: Description of what screenshot should show]

**Step 2: [Second Major Configuration Step]**

1. [Step details...]
2. [Step details...]

[Screenshot needed: Description]

<a id="configuration-matrix"></a>

**Configuration Matrix by Governance Level:**

| Setting | Baseline | Recommended | Regulated |
|---------|----------|-------------|-----------|
| [Setting 1] | [Value] | [Value] | [Value] |
| [Setting 2] | [Value] | [Value] | [Value] |
| [Setting 3] | [Value] | [Value] | [Value] |

### PowerShell/CLI Configuration (Alternative Method)

```powershell
# Prerequisites: [Required modules]
# Install-Module -Name [ModuleName] -Scope CurrentUser

# Connect to service
Connect-[ServiceName]

# [Description of what the script does]
[PowerShell commands with comments]

# Validation command
[Command to verify the configuration]
```

---

## Financial Sector Considerations

### Regulatory Alignment

| Regulation | Requirement | How This Control Helps |
|------------|-------------|------------------------|
| **FINRA [Rule]** | [Requirement description] | [How control addresses it] |
| **SEC [Rule]** | [Requirement description] | [How control addresses it] |
| **SOX [Section]** | [Requirement description] | [How control addresses it] |
| **GLBA [Section]** | [Requirement description] | [How control addresses it] |

### Zone-Specific Configuration

**Zone 1 (Personal Productivity):**
- [Configuration guidance or "Not required for Zone 1"]
- Rationale: [Why this configuration for Zone 1]

**Zone 2 (Team Collaboration):**
- [Specific configuration settings]
- Rationale: [Why this configuration for Zone 2]

**Zone 3 (Enterprise Managed):**
- [Strict configuration settings]
- Rationale: [Why this configuration for Zone 3]

### FSI Implementation Example

**Scenario:** [Concrete example - e.g., "Regional bank deploying customer service agents"]

**Configuration:**
- Allow: [List of approved items]
- Block: [List of restricted items]
- Audit level: [Recommended setting]
- Retention period: [Recommended period]

**Documentation Requirements:**
- [What to document for compliance]
- [Evidence to collect]

---

## Verification & Testing

1. [Verification step 1]
2. [Verification step 2]
3. [Verification step 3]
4. [Verification step 4]

**EXPECTED:** [Description of expected successful state]

---

## Troubleshooting & Validation

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| [Issue 1 description] | [Root cause] | [Solution steps] |
| [Issue 2 description] | [Root cause] | [Solution steps] |
| [Issue 3 description] | [Root cause] | [Solution steps] |

### How to Confirm Configuration is Active

1. **Via Portal:**
   - Navigate to [location]
   - Confirm [what to look for]

2. **Via PowerShell:**
   ```powershell
   [Validation command]
   ```

3. **Via User Testing:**
   - [Test scenario description]
   - Expected result: [What should happen]

---

## Additional Resources

- [Microsoft Learn: Primary documentation](https://learn.microsoft.com/en-us/...)
- [Microsoft Learn: Related feature](https://learn.microsoft.com/en-us/...)
- [Microsoft Learn: Best practices](https://learn.microsoft.com/en-us/...)
- [Admin portal direct link](https://admin.portal.com/...)

---

## Related Controls

| Control | Relationship |
|---------|--------------|
| [X.X - Control Name](link) | [Depends on / Required for / Related to] |
| [X.X - Control Name](link) | [Relationship description] |

---

## Support & Questions

For implementation support or questions about this control, contact:
- **AI Governance Lead** (governance direction)
- **Compliance Officer** (regulatory requirements)
- **Technical Implementation Team** (platform setup)

---

**Updated:** Dec 2025  
**Version:** v1.0 Beta (Dec 2025)  
**UI Verification Status:** ✅ Current / ⚠️ Partially verified / ❌ Needs verification
