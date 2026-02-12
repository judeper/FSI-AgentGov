# MIME Type Exception Request

**Template Version:** 1.0
**Control Reference:** [1.25 — MIME Type Restrictions](../controls/pillar-1-security/1.25-mime-type-restrictions.md)
**Last Updated:** February 2026

---

> **Purpose:** Use this form to request an exception to the MIME type restrictions defined for your governance zone. All exceptions require documented business justification, risk assessment, and approval before MIME types can be added to an environment's allowlist. Approved exceptions are tracked in the exception register and subject to periodic review.

---

## 1. Requestor Information

| Field | Value |
|-------|-------|
| **Name** | _[Full name]_ |
| **Email** | _[Email address]_ |
| **Department** | _[Department / business unit]_ |
| **Request Date** | _[YYYY-MM-DD]_ |

---

## 2. Exception Details

| Field | Value |
|-------|-------|
| **MIME Type(s)** | _[e.g., application/zip, application/x-zip-compressed]_ |
| **File Extension(s)** | _[e.g., .zip]_ |
| **Governance Zone** | _[Zone 1 / Zone 2 / Zone 3]_ |
| **Environment ID** | _[Dataverse environment identifier]_ |
| **Environment Name** | _[Human-readable environment name]_ |

---

## 3. Business Justification

### Purpose and Workflow

_Describe the business process or workflow that requires this file type. Include specific use cases and the teams or roles involved._

> _[Your response here]_

### Volume and Frequency

| Field | Value |
|-------|-------|
| **Estimated file volume** | _[e.g., 50 files per month]_ |
| **Frequency** | _[e.g., Daily / Weekly / Monthly / Quarterly]_ |
| **Peak periods** | _[e.g., End of quarter regulatory filings]_ |

### Duration

- [ ] **Permanent** — Ongoing business requirement with no anticipated end date
- [ ] **Temporary** — Required until: _[YYYY-MM-DD]_

_If temporary, describe what conditions would remove the need for this exception:_

> _[Your response here]_

---

## 4. Alternatives Considered

_List alternative approaches that were evaluated before requesting this exception. For each alternative, explain why it was insufficient._

| Alternative Approach | Reason Insufficient |
|---------------------|---------------------|
| _[e.g., Individual file upload without compression]_ | _[e.g., Volume exceeds practical limits for manual upload]_ |
| _[e.g., Managed file transfer service]_ | _[e.g., Not yet approved by procurement; timeline exceeds business need]_ |
| _[e.g., Alternative file format]_ | _[e.g., External counterparty mandates .zip format]_ |

---

## 5. Risk Assessment

### Threat Scenarios

_Identify potential threats associated with allowing this file type in the environment._

- [ ] Malware delivery via file type
- [ ] Data exfiltration using file type as container
- [ ] Obfuscated executable content within archive
- [ ] Social engineering using familiar file type
- [ ] Other: _[Describe]_

### Data Sensitivity Classification

- [ ] Public
- [ ] Internal
- [ ] Confidential
- [ ] Highly Confidential / Regulated

### Risk Rating

| Dimension | Rating |
|-----------|--------|
| **Likelihood** | _[Low / Medium / High]_ |
| **Impact** | _[Low / Medium / High]_ |
| **Overall Risk** | _[Low / Medium / High / Critical]_ |

_Provide additional context for the risk rating:_

> _[Your response here]_

---

## 6. Mitigating Controls

_Describe the controls that will be in place to reduce risk from this exception. Check all that apply and provide details._

- [ ] **DLP Policy Coverage**
  - Policy name: _[Policy name]_
  - Inspection scope: _[e.g., Content inspection of archive contents]_

- [ ] **Microsoft Sentinel Monitoring**
  - Analytic rule: _[Rule name or description]_
  - Alert severity: _[Informational / Low / Medium / High]_

- [ ] **Additional Scanning**
  - Tool: _[e.g., Defender for Cloud Apps, Defender for Endpoint sandbox]_
  - Scope: _[e.g., All files matching MIME type undergo detonation analysis]_

- [ ] **Access Restrictions**
  - Security group: _[Group name limiting who can upload/download this file type]_
  - Conditional access policy: _[Policy name, if applicable]_

- [ ] **Other Mitigating Controls**
  - _[Describe any additional safeguards]_

---

## 7. Approval

> **Note:** Exceptions for Zone 2 environments require approval from the Power Platform Admin or designated governance lead. Zone 3 exceptions require approval from both the Power Platform Admin and the Compliance Officer.

| Field | Value |
|-------|-------|
| **Approver Name** | _[Full name]_ |
| **Approver Email** | _[Email address]_ |
| **Approver Role** | _[e.g., Power Platform Admin, Compliance Officer]_ |
| **Approval Date** | _[YYYY-MM-DD]_ |
| **Conditions / Restrictions** | _[Any conditions placed on this exception]_ |

### Approval Decision

- [ ] **Approved** — Exception granted as requested
- [ ] **Approved with Conditions** — Exception granted with modifications noted above
- [ ] **Denied** — Justification: _[Reason for denial]_

---

## 8. Review Schedule

| Field | Value |
|-------|-------|
| **Next Review Date** | _[YYYY-MM-DD — default is 90 days from approval]_ |
| **Review Cadence** | _[Quarterly / Semi-Annual / Annual]_ |
| **Responsible Reviewer** | _[Name and role of person responsible for periodic review]_ |

### Review Criteria

At each review, the reviewer should verify:

- [ ] The business justification remains valid
- [ ] Mitigating controls are still in place and functioning
- [ ] No security incidents have been linked to this exception
- [ ] The exception scope (MIME types, environment) remains appropriate
- [ ] The risk assessment has not materially changed

---

## Submission Instructions

1. Complete all sections of this form
2. Submit the completed form to your **Power Platform Admin** or **Governance Lead** via your organization's approved request channel
3. The approver will review the request against Control 1.25 zone requirements
4. Upon approval, the exception will be recorded in the MIME type exception register (`scripts/governance/mime-type-exceptions.csv`)
5. The approved MIME type will be added to the environment configuration using the `FsiMimeControl` module
6. The exception will be validated during subsequent runs of `validate-exceptions.ps1`

> **Important:** Exceptions do not remove the requirement for ongoing monitoring. All excepted MIME types remain subject to DLP inspection, Sentinel monitoring, and periodic review per the schedule above.

---

*Template Version: 1.0 | Control Reference: 1.25 | Last Updated: February 2026*
