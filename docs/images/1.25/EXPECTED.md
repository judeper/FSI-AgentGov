# Control 1.25: MIME Type Restrictions for File Uploads

## Expected Screenshots

### Screenshot 1: PPAC Blocked Extensions Field
**Portal Path:** Power Platform Admin Center → Environments → [Environment] → Settings → Privacy + Security
**What to capture:**
- Blocked file extensions configuration list
- The semicolon-separated extension values populated in the field
- Environment name visible in the header

### Screenshot 2: PPAC Blocked MIME Types Field
**Portal Path:** Power Platform Admin Center → Environments → [Environment] → Settings → Privacy + Security
**What to capture:**
- Blocked MIME types configuration field
- MIME type values populated (e.g., application/x-msdownload)
- Setting label and input area

### Screenshot 3: PPAC Allowed MIME Types Field
**Portal Path:** Power Platform Admin Center → Environments → [Environment] → Settings → Privacy + Security
**What to capture:**
- Allowed MIME types configuration field
- Allowlist values populated with approved document and image types
- Setting label and input area

### Screenshot 4: Compliance Test Output
**What to capture:**
- Terminal output from `Test-FsiMimeCompliance` showing pass/fail per zone
- Environment name, zone classification, and individual check results
- Overall compliance status (COMPLIANT or NON-COMPLIANT)

---

## Verification Focus
- Capture from pre-production environment when possible
- Ensure environment names are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- All three settings fields (blocked extensions, blocked MIME types, allowed MIME types) are on the same Privacy + Security settings page
