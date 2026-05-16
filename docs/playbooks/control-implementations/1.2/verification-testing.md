# Control 1.2 — Verification & Testing Playbook (Registration Plane Integrity)

**Control:** 1.2 — Agent Registry and Integrated Apps Management
**Pillar:** 1 — Security
**Audience:** Agent Sponsor, Agent Owner, Compliance Officer, AI Governance Lead, Entra Global Admin (PIM-activated only), Entra Identity Governance Admin, Entra Application Admin, AI Administrator, Power Platform Admin, Purview Compliance Admin, Internal Audit, Model Risk Manager
**Sovereign-cloud scope:** Microsoft 365 Commercial, GCC, GCC High, DoD. 21Vianet is **out of scope** for this playbook (see PRE-06 / SOV-03).
**Last UI verified:** April 2026

---

## Regulatory hedging notice

This playbook helps support FSI organizations in meeting expectations from FINRA Rule 4511 (books and records), FINRA Rule 3110 (supervision), FINRA Regulatory Notice 25-07 (generative-AI supervision), SEC Rule 17a-4(b)(4) and 17a-4(g) (records retention and third-party custody), SOX §§302/404 (internal control over financial reporting), GLBA 501(b) Safeguards Rule, FTC Safeguards Rule 16 CFR §314.4(c) (asset inventory and access controls), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) / Federal Reserve SR 26-2 (formerly SR 11-7) (model risk management — inventory and accountable ownership), CFTC Regulation 1.31, NYDFS 23 NYCRR Part 500.07 / 500.16 / 500.17 (privileged access, incident response, asset inventory), NIST AI RMF 1.0 GOVERN 1.4 and GOVERN 1.6 (accountable AI inventory and roles), and ISO/IEC 42001:2023 where applicable.

A clean run of this playbook **does not guarantee legal or regulatory compliance**, does not replace independent supervisory review, does not substitute for the firm's written supervisory procedures, and does not by itself prove the absence of unknown agents in surfaces this playbook did not enumerate. Implementation requires organization-specific risk assessment, legal review, and integration with the firm's broader compliance program. Organizations should verify current Microsoft Learn documentation, sovereign-cloud feature parity, tenant-specific entitlements, and Entra / Microsoft 365 / Power Platform admin-surface availability at each cycle. Numeric thresholds, SLA windows, sample sizes, and rotation cadences in this playbook are **calibrated to the tenant baseline captured in PRE-04**; they are not portable between tenants without recalibration.

This playbook is **registration-plane verification**: its purpose is to verify that every AI agent and integrated application deployed in the tenant is **completely registered, authorized, properly governed, owned by a named accountable person, scoped to least privilege, credentialed in a hygienic manner, sponsored under a current attestation, and reconciled to the declared sovereign-cloud boundary**. Control 1.2 is the foundation control for the **agent identity and registration plane**; it is the upstream sister to Control 3.1 (Agent Inventory and Metadata Management). If a registration is incomplete, every downstream control that assumes a governed identity anchor — Conditional Access (Control 1.4 / 1.5), audit logging (Control 1.7), eDiscovery (Control 1.19), step-up auth (Control 1.23), Defender posture management (Control 1.24), managed environments (Control 2.1), QA (Control 2.5), and inventory reporting (Controls 3.1 / 3.6 / 3.11) — has nothing to bind to.

---

## Why this playbook is foundational

The registration plane is where an AI agent acquires a tenant identity (Entra App Registration, service principal, or Entra Agent ID), accepts permission grants, accumulates credentials, declares an owner and sponsor, and chooses a sovereign-cloud anchor. Every other security and governance control assumes those facts are correct. Three categories of failure propagate silently from this plane:

1. **Identity-anchor gaps.** An agent runs on an unregistered identity, an undocumented service principal, or a permanent client secret with no owner of record. Conditional Access cannot target it; audit logs cannot attribute its actions; incident response cannot disable it cleanly.
2. **Authorization drift.** A registration acquires an additional Graph permission, a new credential, a re-consented OAuth scope, or a new owner without re-attestation. The cycle was clean last quarter; the registration is now over-scoped, but no surface flags the change unless this playbook looks for it.
3. **Sponsorship and accountability decay.** The named Agent Sponsor or Agent Owner leaves the firm; the registration persists; the backup is stale; quarterly attestation lapses. The agent is still callable, but no human can defensibly answer the FINRA / OCC examiner question "who approved this and who is supervising it today."

The playbook treats all three failure categories as first-class conditions. **Silent registration incompleteness** (an agent that exists in PPAC but has no Entra identity anchor — a "shadow agent" in Microsoft's official terminology) is treated as more severe than visible misconfiguration, because it cannot be detected by any control downstream of registration.

---

## Audience and how to use this playbook

| Role | What you do here |
|---|---|
| **Agent Sponsor** | Owns business accountability for the agent's purpose, zone, and continued justification. Signs as **Sponsor** in the three-signature attestation chain. Confirms quarterly that the agent is still business-justified. |
| **Agent Owner** | Owns operational accountability for the agent's identity, credentials, permissions, and lifecycle. Executes the cycle's REG / PERM / CRED / CONSENT tests. Signs as **Owner** in the three-signature chain. |
| **Compliance Officer** | Reviews the cycle evidence pack from a supervisory and regulatory-readiness perspective. Validates sponsor-attestation completeness and consent-workflow integrity. Signs as **Compliance**. |
| **AI Governance Lead** | Reviews the cycle outputs against governance policy, validates the reconciliation deltas across the registration surfaces, and arbitrates failure escalations. Owns the per-cycle exception register. |
| **Entra Application Admin** | Executes Graph-based enumeration of `/applications`, `/servicePrincipals`, `/oauth2PermissionGrants`, `/appRoleAssignments`, owners, and credentials. |
| **Entra Identity Governance Admin** | Confirms access reviews / Lifecycle Workflows for application owners; attests the ownerless-app remediation queue. |
| **Power Platform Admin** | Confirms PPAC and Copilot Studio agent enumeration is complete, the publisher tenant ID is recorded, and connection / connector references map cleanly to registered service principals. |
| **AI Administrator** | Confirms Microsoft 365 admin center → Copilot → Agents and Integrated Apps inventory is enumerated; reconciles declarative agents and partner-built agents to their underlying Entra app objects. |
| **Purview Compliance Admin** | Pulls UAL events for `Add application`, `Add app role assignment grant to user`, `Consent to application`, `Update application — Certificates and secrets management`, `Add owner to application`, etc.; verifies records are immutable. |
| **Entra Global Admin** | Activated through Entra PIM, time-bound, never standing. Used only where a non-elevated role cannot complete the action. |
| **Internal Audit** | Uses the evidence pack and three-signature chain as the testable artifact for SOX-style and FINRA-supervision walkthroughs and runs the quarterly examiner-style audit (Section 10). |
| **Model Risk Manager** | Reviews REG / OWN / SPONSOR evidence under Fed SR 26-2 (formerly SR 11-7) / OCC Bulletin 2026-13 (formerly OCC 2011-12) inventory and accountable-ownership expectations for higher-risk agents. |

Run order each cycle: **Section 5 PRE gates → Section 7 §REG → §OWN → §PERM → §CRED → §CONSENT → §CA → §SPONSOR → §SOV → Section 8 evidence pack assembly → Section 9 attestation chain**. Any PRE-* failure or any REG-* FAIL halts the cycle.

---

## Cross-links

This playbook depends on, and is depended on by, the following framework controls and playbooks. Operators should open these alongside this document during a cycle:

- [Control 1.2 — Agent Registry and Integrated Apps Management (control specification)](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)
- [Control 1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- [Control 1.19 — eDiscovery for Agent Interactions (verification playbook)](../1.19/verification-testing.md)
- [Control 1.21 — Adversarial Input Logging (verification playbook)](../1.21/verification-testing.md)
- [Control 1.23 — Step-Up Authentication for Agent Operations](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)
- [Control 1.24 — Defender AI Security Posture Management](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md)
- [Control 2.1 — Managed Environments (verification playbook)](../2.1/verification-testing.md)
- [Control 2.5 — Testing, Validation, and QA (verification playbook)](../2.5/verification-testing.md)
- [Control 3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- [Control 3.11 — Centralized Agent Inventory Enforcement](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md)
- [Sponsorship Lifecycle Workflows (companion playbook)](./sponsorship-lifecycle-workflows.md)
- [AI Incident Response Playbook](../../incident-and-risk/ai-incident-response-playbook.md)

---

## What this playbook catches

This playbook is designed to detect defects in the **registration program**, not in the runtime behavior of any one agent. It is built to surface:

1. **Shadow agents** — agents discovered in PPAC, Copilot Studio, or the Agent 365 surface that have no Entra App Registration / service principal / Agent ID anchor.
2. **Half-registered agents** — an Entra App Registration with no service principal in the home tenant; a service principal with no application object; an Entra Agent ID with no owning app object; a Copilot Studio agent with no provisioned identity.
3. **Owner-of-record decay** — applications with zero owners, with a sole owner who has departed, or with a backup owner who is also stale.
4. **Permission-grant drift** — application or delegated permissions added since the last attestation; high-privilege scopes (`Mail.ReadWrite.All`, `Files.ReadWrite.All`, `Directory.ReadWrite.All`, `Sites.FullControl.All`, etc.) granted without admin-consent record; tenant-wide application grants where a scoped grant was approved.
5. **Orphaned consent grants** — `oauth2PermissionGrants` referencing deleted users, deleted apps, or service principals that no longer exist.
6. **Credential hygiene failures** — expired-but-not-removed client secrets; secrets rotated past the firm's policy threshold; long-lived secrets where certificate-based authentication or federated credentials were required by zone policy.
7. **Consent-workflow degradation** — admin consent workflow disabled, reviewer queue backlog beyond SLA, user consent not restricted to verified publishers and low-risk scopes per the firm's policy.
8. **Conditional Access for workload identities gap** — Zone 3 service principals not covered by an SP-targeted Conditional Access policy; sign-in risk policy for workload identities disabled or misscoped.
9. **Sponsorship lapses** — Zone 2 / Zone 3 agents with no active Sponsor + Backup; sponsor approval audit trail missing; quarterly sponsor attestation overdue.
10. **Sovereign-cloud assumption leakage** — registration entries with no cloud designation, cross-cloud service principals (multi-tenant home cloud mismatch) unflagged, per-cloud feature parity gaps undocumented.
11. **Publisher-verification gaps** — partner-built agents and Integrated Apps published by unverified publishers without a documented compensating review.
12. **Hash-chain breaks across cycles** — a previous cycle's manifest hash that does not match the current cycle's `previousManifestHash` field, indicating tampering or evidence loss.

---

## What this playbook does NOT claim

This playbook **does not** prove the absence of unknown agents in surfaces it did not enumerate, **does not** validate the runtime behavior of any agent, **does not** independently verify the publisher claims of partner-built agents beyond what Microsoft's publisher-verification program records, **does not** guarantee that least-privilege grants are operationally minimal (only that they conform to the documented Graph permissions matrix at the cycle start), **does not** substitute for the firm's third-party / vendor-risk-management program for partner-built agents, **does not** replace the AI Incident Response Playbook for live identity-compromise events, and **does not** assume universal sovereign-cloud feature parity. A clean cycle is a defensible attestation that the registration plane is governed against the policy in force on the cycle start date; it is not a statement about the firm's complete identity-security posture.

---

## Section 1 — The 3-Signature Attestation Chain

Every registration verification cycle terminates in a **three-signature attestation chain** with cryptographic integrity. This is the cycle's primary deliverable and the artifact handed to internal audit and external examiners.

### 1.1 Signature roles

| Signature | Role (canonical) | What this signature attests |
|---|---|---|
| **Sponsor** | Agent Sponsor | "I confirm that the agents in scope for this cycle remain business-justified; that the zone classification and regulatory tagging on each one match my current understanding of how the agent is used; that I am the named accountable sponsor for each Zone 2 / Zone 3 agent in scope, or have an active Backup Sponsor of record; and that I have re-attested any agent whose connectors, grounding sources, permission set, or business purpose materially changed during the cycle window." |
| **Owner** | Agent Owner | "I executed the REG, OWN, PERM, CRED, CONSENT, CA, SPONSOR, and SOV tests as documented; I assembled the evidence pack listed in the manifest; the SHA-256 hashes in the manifest match the artifacts in the evidence store; I have not altered any source export after capture; every remediation action recorded in the cycle was completed by a named operator under documented change control." |
| **Compliance** | Compliance Officer | "I reviewed the evidence pack from a supervisory and regulatory-readiness perspective; the residual gaps documented in this cycle are acceptable for the firm's current risk posture or are tracked to a dated remediation plan; the consent-workflow, publisher-verification, and sovereign-cloud designation evidence is suitable for inclusion in the firm's books-and-records repository under the applicable retention period." |

The three signatures **must** be three distinct natural persons. Role collision (the same person signing two roles) is a cycle-stopping FAIL recorded in PRE-02. A documented temporary exception for a Zone 1-only scope is allowed only with a co-signed expiry and a return-to-three-person review on the next cycle.

### 1.2 Hash chain across snapshots

Each cycle's evidence pack contains a `manifest.sha256` file listing one SHA-256 per artifact. The cycle attestation file (`attestation.json`) records:

- `cycleId` — stable identifier for this cycle (e.g., `1.2-2026-04-Z3-COMM`)
- `previousCycleId` — the immediately preceding cycle for the same scope and cloud
- `previousManifestHash` — SHA-256 of the previous cycle's `manifest.sha256`
- `manifestHash` — SHA-256 of the current cycle's `manifest.sha256`
- `chainHash` — SHA-256 of the concatenation `previousManifestHash || manifestHash || cycleId`
- `signatures[]` — three signature objects (Sponsor, Owner, Compliance) each with role, identity (UPN), timestamp (UTC ISO-8601), signature method (e.g., Entra-bound device-bound key, S/MIME certificate, hardware token), and the signed digest

The `previousManifestHash` field creates a tamper-evident hash chain across the cycle history. A break in the chain (a `previousManifestHash` value in the current cycle that does not match the `manifestHash` of the prior cycle) is itself an audit finding and triggers the failure path described in Section 11 — Failure escalation matrix.

Example `attestation.json` skeleton:

```json
{
  "cycleId": "1.2-2026-04-Z3-COMM",
  "previousCycleId": "1.2-2026-03-Z3-COMM",
  "previousManifestHash": "9c0f...e1a7",
  "manifestHash": "1ad4...77b2",
  "chainHash": "8b22...904c",
  "scope": { "zone": "Z3", "cloud": "Commercial", "agentCount": 184 },
  "signatures": [
    { "role": "Sponsor", "upn": "sponsor@contoso.com", "tsUtc": "2026-04-15T14:02:11Z", "method": "Entra-bound key", "digest": "..." },
    { "role": "Owner", "upn": "owner@contoso.com", "tsUtc": "2026-04-15T14:09:48Z", "method": "Entra-bound key", "digest": "..." },
    { "role": "Compliance", "upn": "compliance@contoso.com", "tsUtc": "2026-04-15T15:31:02Z", "method": "S/MIME", "digest": "..." }
  ]
}
```

### 1.3 Attestation note language

The Owner attestation should include the literal language: *"This cycle was executed against the registration surfaces and tenant entitlements available as of the cycle start date in the declared sovereign cloud. A clean cycle does not by itself guarantee regulatory compliance, model-risk completeness, or freedom from shadow registrations in surfaces this cycle did not enumerate."* Sponsor and Compliance signatures should each include a reference to the policy document identifier and effective date that they are attesting against, plus the specific Graph permissions matrix version used to evaluate PERM-* tests.

### 1.4 Signature method requirements

| Zone | Minimum signature method | Stronger-method recommendation |
|---|---|---|
| Zone 1 | Entra Verified ID-attested signature or equivalent | Entra-bound device-bound key |
| Zone 2 | Entra-bound device-bound key on a managed device | Hardware-token-protected key |
| Zone 3 | Hardware-token-protected key (FIPS 140-2 or 140-3 validated) | HSM-resident signing key with dual-control activation |

The signature method is recorded in the `method` field; verification at audit replay time confirms the method satisfied the zone minimum at the cycle start.

---

## Section 2 — Sovereign Cloud parity matrix per surface

The registration surfaces this playbook depends on do **not** have uniform feature parity across Microsoft 365 sovereign clouds as of April 2026. The matrix below is the operative parity reference for the cycle. Any cell marked *Verify* should be re-checked against the tenant Message Center and Microsoft Learn at cycle start; the cycle should record what was observed, not what was assumed.

| Registration surface / capability | Commercial | GCC | GCC High | DoD | Cycle implication if unavailable |
|---|---|---|---|---|---|
| Microsoft Entra App Registration (`/applications`) | GA | GA | GA | GA | Required everywhere; absence is a hard blocker |
| Microsoft Entra service principal (`/servicePrincipals`) | GA | GA | GA | GA | Required everywhere; absence is a hard blocker |
| Microsoft Entra Agent ID directory | Preview / rolling | Limited preview / verify | Verify | Verify | Use Entra app + SP as identity anchor; record SOV-03 compensating control |
| Integrated Apps (M365 admin center) | GA | GA / verify rollout | Verify | Verify | Fall back to Entra-only enumeration; record SOV-03 |
| App consent workflow | GA | GA | GA / verify UX parity | GA / verify UX parity | Required for CONSENT-01; verify UX parity at cycle start |
| User consent restriction settings | GA | GA | GA | GA | Required everywhere |
| Conditional Access for workload identities | GA | GA | Verify rollout | Verify rollout | If unavailable, document compensating control via tenant restrictions and IP allow-listing |
| Workload identity sign-in risk policies (Identity Protection) | GA (P2) | GA (P2) | Verify | Verify | Compensating control via Defender for Cloud Apps anomaly policies if unavailable |
| Microsoft Graph `/oauth2PermissionGrants`, `/appRoleAssignments` | GA | GA | GA | GA | Required everywhere |
| Microsoft Graph application credential enumeration | GA | GA | GA | GA | Required for CRED-* tests |
| Federated identity credentials (workload identity federation) | GA | GA | Verify rollout | Verify rollout | Where unavailable, document the compensating credential-rotation cadence |
| Service principal sign-in audit | GA | GA | GA | GA | Required for CONSENT-04, CRED-04 |
| Power Platform Copilot Studio registration | GA | GA / verify feature scope | Verify | Verify | Fall back to Dataverse-side enumeration; record SOV-03 |
| Defender for Cloud Apps (app governance) | GA | Rolling / verify | Limited / verify | Verify | PERM-04 enrichment skipped; record SOV-03 |
| Microsoft Agent 365 admin center | Preview / rolling | Limited / verify | Verify | Verify | Treat as additive only; do not rely on as system of record |
| Purview Audit (UAL) — application lifecycle events | GA | GA | GA | GA | Required everywhere; absence is a hard blocker |
| Purview eDiscovery for app-related artifacts | GA | GA | GA | GA | Required for evidence-pack retention |
| WORM / immutable retention for evidence | GA | GA | GA | GA | Required everywhere |

**Parity rule.** Any surface marked *Verify*, *Limited*, or *Preview* should be paired with a documented compensating control in the cycle's SOV-03 evidence. Treat any parity gap as a **compensating-control conversation**, not an assumption of feature equivalence across clouds. 21Vianet is out of scope for this playbook; tenants in 21Vianet should run a separate cloud-specific cycle.

---

## Section 3 — License and permissions prerequisites

Re-verify SKU and preview availability at cycle start against current Microsoft Learn licensing guidance and the tenant Message Center.

### 3.1 Required licenses and entitlements

| Capability | License / entitlement | Used by |
|---|---|---|
| Microsoft Entra ID base directory and app registration | Entra ID Free (minimum) | REG-*, OWN-*, PERM-* |
| Conditional Access policy authoring (incl. workload identities) | Entra ID P1 (workload identity CA in P1; some signal sources require P2) | CA-01, CA-02 |
| Identity Protection (workload identity risk) | Entra ID P2 | CA-02 |
| Entra Workload ID Premium (richer SP governance) | Entra Workload ID Premium SKU | CA-01, CA-02, CRED-04 |
| Entra Identity Governance (access reviews, Lifecycle Workflows) | Entra ID Governance / P2 | OWN-03, OWN-04, SPONSOR-03 |
| Microsoft Entra PIM (time-bound activation of elevated roles) | Entra ID P2 | PRE-02 |
| Microsoft 365 Copilot agent surfaces | Microsoft 365 Copilot | REG-01, REG-02 |
| Power Platform Copilot Studio admin surface | Power Platform Admin entitlement | REG-01, REG-02 |
| Purview Audit (UAL) — high-bandwidth retention | E5 Compliance / Purview Audit Premium | CONSENT-04, CRED-03, PERM-02, OWN-03 |
| Defender for Cloud Apps — App Governance | MDA + App Governance entitlement | PERM-04, CONSENT-02 (enrichment) |
| Microsoft Agent 365 (where available) | Agent 365 entitlement (rollout-dependent) | REG-01 (additive only) |
| Verified Publisher status (for publishing internally-developed agents) | Microsoft Partner / Verified Publisher enrollment | REG-04 |
| Federated identity credentials (workload identity federation) | Entra (no extra SKU) | CRED-04 |
| Microsoft Information Protection sensitivity labels (for Sponsor signature on labeled records) | E5 Compliance | Section 1 (Sponsor signature) |

### 3.2 Required role assignments (canonical names)

| Role | Why needed |
|---|---|
| Agent Sponsor | Cycle scoping; Sponsor signature |
| Agent Owner | Cycle execution; Owner signature |
| Compliance Officer | Cycle review; Compliance signature |
| AI Governance Lead | Cycle validation and exception arbitration |
| Entra Application Admin | `/applications`, `/servicePrincipals`, `/oauth2PermissionGrants` enumeration |
| Entra Identity Governance Admin | Access-review and Lifecycle Workflows attestation; OWN-04 ownerless-app remediation queue |
| Entra Cloud Application Admin (where the broader Application Admin is too privileged) | Lower-privilege execution of OWN-* tasks |
| Power Platform Admin | PPAC + Copilot Studio enumeration |
| AI Administrator | M365 admin center → Copilot → Agents and Integrated Apps enumeration |
| Purview Compliance Admin | UAL searches; consent-workflow audit |
| Entra Global Reader | Read-only attestation review |
| Entra Global Admin | Tenant-wide irreversible operations only; activated through Entra PIM, time-bound, never standing |
| Conditional Access Admin | CA policy authoring and review for SP-targeted policies |

Role separation is enforced by PRE-02. Standing privileged role overlap with the Sponsor / Owner / Compliance signatures is a cycle-stopping FAIL.

### 3.3 Minimum Graph permissions for cycle automation

Where the cycle is executed by an automation principal (recommended for Zone 3), the principal should hold the minimum Graph permissions below — and **only** these — recorded in the firm's Graph permissions matrix:

| Graph permission | Why needed | Type |
|---|---|---|
| `Application.Read.All` | Enumerate `/applications` and credentials | Application |
| `Directory.Read.All` | Resolve owner UPNs, manager links, group memberships | Application |
| `AuditLog.Read.All` | Pull SP sign-in logs and directory audit logs | Application |
| `Policy.Read.All` | Read Conditional Access policy targeting | Application |
| `Policy.Read.ConditionalAccess` | Detailed CA policy read for CA-01 evaluation | Application |
| `IdentityRiskyServicePrincipal.Read.All` | Workload identity risk read for CA-02 | Application |
| `RoleManagement.Read.Directory` | Read directory role assignments for PRE-02 | Application |
| `DelegatedPermissionGrant.Read.All` | Read `/oauth2PermissionGrants` for PERM-02, CONSENT-04 | Application |
| `AppRoleAssignment.ReadWrite.All` (read-only modes only) | Enumerate app role assignments | Application (read-only) |

Write permissions are **never** held by the cycle-execution principal. Remediation actions are always performed by a named operator under separate change control.

---

## Section 4 — Required namespace × zone cadence matrix

| Namespace | What the family verifies | Zone 1 | Zone 2 | Zone 3 | Owner | Reviewer |
|---|---|---|---|---|---|---|
| **REG** | Registration completeness (every deployed agent has an Entra App Registration / SP / Agent ID; no shadow agents) | Quarterly | Monthly | Weekly | Agent Owner | AI Governance Lead |
| **OWN** | Ownership integrity (every app ≥ 1 active owner + Backup; departed-owner reassignment within zone SLA) | Quarterly | Monthly | Monthly | Agent Owner | Entra Identity Governance Admin |
| **PERM** | Permission grant minimization (no over-scoped grants; no orphaned consent grants; admin-consent-required for sensitive scopes) | Quarterly | Monthly | Monthly | Agent Owner | AI Governance Lead |
| **CRED** | Credential hygiene (no expired secrets in active use; cert / federated-credential preference in Z3; rotation cadence met) | Quarterly | Monthly | Weekly | Agent Owner | Entra Application Admin |
| **CONSENT** | Consent governance integrity (admin consent workflow active; reviewer queue SLA met; user consent restrictions enforced) | Quarterly | Monthly | Monthly | Compliance Officer | AI Governance Lead |
| **CA** | Conditional Access for workload identities (Z3 SPs covered by SP-targeted CA policy; sign-in risk policies active) | Annual | Quarterly | Monthly | Conditional Access Admin | AI Governance Lead |
| **SPONSOR** | Sponsorship integrity (Z2 / Z3 agents have active Sponsor + Backup; sponsor approval audit trail; quarterly attestation) | Annual | Quarterly | Quarterly | Agent Sponsor | Compliance Officer |
| **SOV** | Sovereign cloud boundary (every registration entry has cloud designation; cross-cloud SPs flagged; per-cloud parity gaps documented) | Annual | Semi-annual | Quarterly | AI Governance Lead | Compliance Officer |

**Cadence rule.** Monthly cycles have a 35-day grace window, quarterly cycles have a 100-day grace window, semi-annual cycles have a 200-day grace window, annual cycles have a 400-day grace window. A namespace that fails in two consecutive cycles automatically escalates one tier (Zone 1 → Zone 2 cadence, Zone 2 → Zone 3 cadence) until two clean cycles are observed. The escalation is recorded in the AI Governance Lead's exception register and is itself an artifact in the next cycle's evidence pack.

---

## Section 5 — Pre-flight gates (PRE-01 through PRE-07)

All PRE gates should pass before any §7 test runs. A PRE failure halts the cycle and returns validator exit code **2**.

### PRE-01 — Registration governance charter and Graph permissions matrix in force

- **Objective.** Confirm the organization has a current, signed registration-governance charter that defines the canonical metadata schema (App ID, SP Object ID, Entra Agent ID where applicable, Sponsor, Owner, Backup Owner, Zone, Permission Set, Credential Type, Sovereign Cloud, Publisher Verification State, etc.) and the Graph permissions matrix that PERM-* tests evaluate against.
- **How to verify.** Pull the charter document and Graph permissions matrix from the policy repository; confirm signatures from AI Governance Lead and Compliance Officer; confirm effective date is current and review date has not lapsed; confirm the matrix version is referenced in the cycle manifest.
- **Evidence.** `pre-01-registration-charter.json` referencing policy ID, effective date, review date, owner, sign-off roster, Graph matrix version.
- **Pass criteria.** Charter exists, is signed, has not lapsed its review date, and the metadata schema and Graph matrix in force match the schema and matrix this cycle is enforcing.
- **Failure remediation.** If lapsed, halt the cycle and re-charter with AI Governance Lead and Compliance Officer signatures; if mismatched, reconcile the matrix difference and re-baseline before resuming.
- **Audit assertion.** "The cycle was executed against a current, signed registration-governance policy and against the canonical Graph permissions matrix referenced therein."

### PRE-02 — Role separation and reviewer independence

- **Objective.** Confirm the same natural person does not occupy the attestation roles of Sponsor (Agent Sponsor), Owner (Agent Owner), and Compliance (Compliance Officer); confirm any elevated admin used during the cycle is time-bound through Entra PIM and that no PIM-eligible Global Admin standing assignment exists.
- **How to verify.** Query Entra role assignments and the cycle approver roster; verify PIM activation history for any privileged role used; confirm co-signer requirements for any exception.
- **Evidence.** `pre-02-role-separation.json`
- **Pass criteria.** Three roles are distinct natural persons, no standing privileged overlap exists, any exception is explicit and time-limited (≤ 30 days) with co-signature.
- **Failure remediation.** Reassign one of the colliding roles to a different person; if no second person is available in the responsible group, treat as a structural finding and escalate to AI Governance Committee for risk acceptance.
- **Audit assertion.** "The verification cycle was run under segregated duties consistent with supervisory and internal-control expectations."

### PRE-03 — License and entitlement floor

- **Objective.** Confirm the tenant has the entitlements required for every registration surface and source-of-truth system the cycle relies on (Entra ID P1 / P2, Workload ID Premium, Identity Governance, Microsoft 365 Copilot, Power Platform admin, Purview Audit, optional MDA / Agent 365).
- **How to verify.** Capture tenant SKU report, Entra ID tier, Workload ID Premium activation state, Identity Governance state, and entitlement availability for each surface; if a surface is absent in the declared sovereign cloud, record the compensating manual path.
- **Evidence.** `pre-03-licensing-and-env.json`
- **Pass criteria.** All exercised surfaces are entitled and reachable, or a compensating control is documented and tied to the relevant SOV-* test.
- **Failure remediation.** Acquire the missing entitlement or formally narrow the cycle scope (e.g., drop CA-02 if Identity Protection P2 is unavailable) with AI Governance Lead sign-off.
- **Audit assertion.** "The cycle relied only on features the tenant is entitled to use in the declared cloud."

### PRE-04 — Tenant baseline capture

- **Objective.** Establish the tenant-specific baseline for total app / SP count, surface-level counts, expected reconciliation tolerance, secret-rotation drift band, consent-queue SLA observed, and CA-policy coverage rate before the cycle's pass conditions are evaluated. The baseline is the source of all numeric thresholds in the cycle; thresholds are not portable from another tenant.
- **How to verify.** Pull trailing 90-day cycle history; calculate trend, mean, p50, p95 for the count metrics; write a baseline file with a stable `baselineId` that every test references.
- **Evidence.** `pre-04-baseline.json`
- **Pass criteria.** A current baseline exists, references at least three trailing cycles where available, and is the sole source for the numeric thresholds cited later.
- **Failure remediation.** If trailing cycles are unavailable (new program), use the bootstrap baseline procedure in the AI Governance Lead's playbook and mark the cycle as `baseline=bootstrap`. Bootstrap baselines must be recalibrated in the next cycle.
- **Audit assertion.** "All numerical assertions in this cycle trace back to a documented tenant baseline rather than copied values from another tenant or an older cycle."

### PRE-05 — Snapshot freeze and refresh-window alignment

- **Objective.** Confirm the registration snapshot used for this cycle was taken **after** the most recent platform refresh window and is frozen for the duration of the cycle. PPAC inventory has a ~15-minute refresh cadence; UAL ingestion can lag up to 24 hours; snapshots taken inside refresh windows can silently truncate.
- **How to verify.** Record snapshot timestamps for each surface; confirm each timestamp is at least 20 minutes after the prior write activity recorded in UAL; freeze the snapshot directory by computing SHA-256 over its contents at cycle start and again at cycle end.
- **Evidence.** `pre-05-snapshot-freeze.json`
- **Pass criteria.** Snapshot start and end SHA-256 values match (the snapshot did not mutate during the cycle), and each surface snapshot is outside the documented refresh window.
- **Failure remediation.** Re-take the snapshot outside the refresh window and restart the cycle.
- **Audit assertion.** "The cycle's evidence corresponds to a stable snapshot taken outside the platform refresh window and unchanged for the cycle duration."

### PRE-06 — Cloud guard and sovereign parity pre-check

- **Objective.** Confirm the tenant cloud is correctly classified (Commercial, GCC, GCC High, DoD) and refuse to run if the cloud is unsupported or ambiguous.
- **How to verify.** Query organization metadata, connection endpoints, and cloud instance; compare to declared cloud in the cycle manifest; verify the Section 2 parity matrix matches what is observable in the tenant Message Center.
- **Evidence.** `pre-06-cloud-guard.json`
- **Pass criteria.** Declared cloud and observed cloud match exactly; unsupported clouds (21Vianet) halt.
- **Failure remediation.** Reset the cycle scope to match the actual cloud, or split into per-cloud cycles for multi-cloud tenants.
- **Audit assertion.** "No cross-cloud assumptions were made silently, and the cycle executed in the environment it claims to describe."

### PRE-07 — Evidence store reachability and write-protection

- **Objective.** Confirm the evidence store (SharePoint with Purview retention label and locked policy, Azure Blob with WORM, or equivalent) is reachable, that the cycle has write access for new artifacts, and that write-protection / version-history is active so that mid-cycle edits cannot mask reconciliation deltas.
- **How to verify.** Query the evidence-store schema; confirm Purview retention label is `Locked`; capture a read-only smoke-test write and re-read with timestamp.
- **Evidence.** `pre-07-evidence-store.json`
- **Pass criteria.** The store is reachable, write succeeds, version history / immutable retention is enabled, and the smoke-test artifact is hashed.
- **Failure remediation.** Restore evidence-store access via Purview Compliance Admin; if WORM is not enabled, halt and remediate at Control 1.7 before resuming.
- **Audit assertion.** "The evidence store is the immutable target for the cycle, with retention policy sufficient to support audit replay."

---

## Section 6 — Documented processing windows

This playbook does **not invent SLAs**. Where Microsoft documentation is qualitative or eventual-consistency based, the playbook says so plainly and uses the tenant-specific PRE-04 baseline as the operative threshold.

| Signal or operation | Documentation-safe statement | Used by |
|---|---|---|
| Entra App Registration directory propagation | Eventually consistent per Entra documentation; use tenant baseline | REG-01, OWN-01 |
| Service principal sign-in audit propagation | Microsoft documents up to a few minutes typical latency in Commercial; use tenant baseline | CONSENT-04, CRED-04 |
| Microsoft Graph `/oauth2PermissionGrants` read consistency | Near-real-time read; record observed | PERM-02, CONSENT-04 |
| Microsoft Graph application credential listing | Near-real-time read; record observed | CRED-01, CRED-02, CRED-03 |
| Conditional Access policy evaluation lag (workload identity) | Eventual; documented as up to one hour for newly-provisioned SPs in Commercial; use tenant baseline | CA-01, CA-02 |
| Workload identity sign-in risk detection | Tenant-dependent; record observed in baseline | CA-02 |
| Admin consent request submission to reviewer queue | Documented as near-real-time; queue SLA is firm policy, not Microsoft policy | CONSENT-02 |
| Purview Audit (UAL) ingestion of application lifecycle events | Eventual; Microsoft documents up to 24 hours typical latency in Commercial; use tenant baseline | PERM-04, CONSENT-04, CRED-03, OWN-03 |
| PPAC inventory refresh | ~15 minutes per Microsoft Learn; lower bound | REG-01, REG-02 |
| Defender for Cloud Apps app-governance enrichment | Tenant-dependent ingestion lag; record observed | PERM-04 |
| Sponsor attestation propagation to evidence store | Tenant-store dependent; record observed | SPONSOR-03 |

---

## Section 7 — Test catalog (28 tests across 8 namespaces)

Each test has a stable ID, one clear objective, specific preconditions, operator-runnable steps, deterministic expected behavior and pass criteria, named evidence artifacts, the failure remediation path, the cycle cadence, the named owning role, and zone applicability. The order is fixed: **REG → OWN → PERM → CRED → CONSENT → CA → SPONSOR → SOV**. A REG-* FAIL halts the cycle.

### Namespace expansion

- **REG** — Registration completeness across surfaces; shadow-agent detection; cross-surface join integrity; publisher verification
- **OWN** — Ownership integrity; departed-owner reassignment; ownerless-app remediation queue
- **PERM** — Permission-grant minimization; orphaned consent grants; admin-consent-required scopes; permission drift
- **CRED** — Credential hygiene; certificate / federated-credential preference; rotation cadence
- **CONSENT** — Consent governance integrity (workflow active, queue SLA, user-consent restrictions, audit trail)
- **CA** — Conditional Access for workload identities; sign-in risk policies
- **SPONSOR** — Sponsorship integrity; approval audit trail; quarterly attestation; departure handling
- **SOV** — Sovereign cloud boundary attestation; cross-cloud detection; parity-gap compensating-control register

---

### 7.REG — Registration completeness across surfaces

This family verifies that no agent is silently missing from the registration plane. The cycle treats the **union** of Entra app objects, service principals, Entra Agent IDs, Integrated Apps, M365 admin center Copilot agents, Copilot Studio agents, MCP servers, and Agent 365 (where available) as the authoritative superset; the registration governance store should reconcile to that superset, not the other way around. A single missing registration in this family halts the cycle.

#### 1.2-REG-01 — Registration surface enumeration completeness

- **Objective.** Confirm that the cycle enumerated every registration surface that can host or anchor an AI agent identity in the declared sovereign cloud.
- **Pre-conditions.** PRE-01, PRE-03, PRE-05, PRE-06, PRE-07 PASS.
- **Steps.**
  1. Enumerate Entra App Registrations via Microsoft Graph: `GET /applications?$select=id,appId,displayName,publisherDomain,verifiedPublisher,signInAudience,createdDateTime,tags`. Save as `surface-entra-apps.json`.
  2. Enumerate Entra Service Principals: `GET /servicePrincipals?$select=id,appId,displayName,servicePrincipalType,accountEnabled,appOwnerOrganizationId,tags,signInAudience`. Save as `surface-entra-sps.json`.
  3. Enumerate Entra Agent IDs (where preview / GA in the declared cloud): pull the Agent ID directory listing; save as `surface-entra-agentids.json`. If unavailable, record the absence in SOV-03 and fall back to the App + SP join as the identity anchor.
  4. Export Integrated Apps from **Microsoft 365 admin center → Settings → Integrated apps**: save as `surface-integrated-apps.csv` with capture timestamp.
  5. Export Microsoft 365 admin center → Copilot → Agents inventory: save as `surface-m365-copilot-agents.csv`.
  6. Export Power Platform Copilot Studio agents (per environment, across all environments) using `Get-AdminPowerApp` / `Get-AdminBot` (verify current cmdlet) or PPAC export: save as `surface-copilot-studio-agents.csv`. If the tenant exceeds the PPAC display ceiling, fall back to Azure Resource Graph and record the fallback.
  7. Enumerate MCP server registrations (Entra App Registrations tagged as MCP per the firm's tagging convention, or via the firm's MCP registration register): save as `surface-mcp-servers.csv`.
  8. Where available in the declared cloud, export the Microsoft Agent 365 admin-center surface as `surface-agent365.csv`. Treat as **additive** only; absence in GCC High / DoD does not FAIL this test but should be recorded in SOV-03.
  9. Pull a Purview Audit (UAL) export of `Add application`, `Add service principal`, `Update application`, `Update service principal`, `Add owner to application`, `Remove owner from application`, `Add app role assignment grant to user`, `Consent to application`, and `Update application — Certificates and secrets management` events for the trailing reconciliation window. Save as `surface-ual-app-events.csv`.
  10. Compute SHA-256 for each surface export and write into `manifest.sha256`.
- **Expected result.** Eight to nine surface exports (or seven plus a documented additive-skip for Agent 365 and Entra Agent ID) exist with timestamps and hashes. Each enumeration completed without truncation warnings.
- **Pass criteria.** All required surface exports exist, are non-empty (or empty for a documented reason such as no agents in scope), are hashed, and the PPAC export shows a row count ≥ the count visible in PPAC at snapshot time (or used the documented Resource Graph fallback). Truncation, missing surfaces, or unfilled fallbacks are FAIL.
- **Failure remediation.** Identify the missing surface, restore access via Power Platform Admin / Entra Application Admin / AI Administrator as appropriate, re-take the snapshot outside the next refresh window, and re-run the test. Do not proceed to REG-02 with a partial surface set.
- **Evidence.** `surface-entra-apps.json`, `surface-entra-sps.json`, `surface-entra-agentids.json` (or skip note), `surface-integrated-apps.csv`, `surface-m365-copilot-agents.csv`, `surface-copilot-studio-agents.csv`, `surface-mcp-servers.csv`, `surface-agent365.csv` (or skip note), `surface-ual-app-events.csv`, `manifest.sha256`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones; Zone 3 weekly is the binding cadence for any tenant with regulated agents.

#### 1.2-REG-02 — Shadow agent detection (no Entra identity anchor)

- **Objective.** Confirm that every agent visible in PPAC, Copilot Studio, M365 admin center Copilot Agents, Integrated Apps, or Agent 365 has a corresponding Entra App Registration / service principal / Agent ID anchor — i.e., no shadow agents (Microsoft's official terminology for unregistered agents lacking an Entra Agent ID anchor).
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. Build the **agent superset** by unioning the agent identifiers from `surface-m365-copilot-agents.csv`, `surface-copilot-studio-agents.csv`, `surface-integrated-apps.csv`, `surface-mcp-servers.csv`, and `surface-agent365.csv` (where available).
  2. Build the **identity-anchor set** by unioning `appId` values from `surface-entra-apps.json` and `surface-entra-sps.json`, plus the Entra Agent ID set where available.
  3. For each agent in the superset, attempt to resolve to an identity anchor using:
     - The agent's `appId` field (Copilot Studio agents created via "Create agent in Copilot Studio with Entra-backed identity")
     - The agent's `publisherAppId` (partner-built agents in Integrated Apps)
     - The agent's `connectionReferences[].appId` (where the agent has no own identity but references a connector SP)
     - The agent's Entra Agent ID linkage (where Agent ID preview is exposed)
  4. Classify the result for each agent: `ANCHORED`, `ANCHORED-VIA-CONNECTOR-ONLY` (the agent itself has no identity but its connectors do), `SHADOW` (no anchor by any path).
  5. Output `reg-02-shadow-classification.csv` with one row per agent and the classification.
  6. For every `SHADOW` classification, also pull the Agent 365 admin-center "shadow agent" indicator where available and confirm Microsoft's discovery aligns with the cycle's classification.
- **Expected result.** A complete classification table; ideally zero `SHADOW` rows; any `SHADOW` rows are explicitly enumerated and ticketed.
- **Pass criteria.** Classification table is complete (every superset agent classified); `SHADOW` count is 0 OR every shadow row has an open remediation ticket assigned to the Agent Owner with a due date inside the zone reconciliation cadence AND a quarantine action (per the Agent 365 shadow-agent registry actions: Quarantine / Investigate / Register) recorded.
- **Failure remediation.** For each shadow row: (a) classify intent — was it intended to have an identity? (b) if yes, initiate Entra App Registration provisioning per the firm's registration workflow; (c) if no, decommission the agent under Control 3.6 (Orphaned Agent Detection); (d) if uncertain, place into Quarantine via the Agent 365 registry action while sponsor adjudication runs.
- **Evidence.** `reg-02-shadow-classification.csv`, `reg-02-quarantine-actions.csv`, `reg-02-tickets.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones. Any Zone 3 shadow agent is automatically a High-severity finding in Section 11.

#### 1.2-REG-03 — Cross-registration join integrity (App ↔ SP ↔ Agent ID)

- **Objective.** Confirm that for every Entra App Registration in the home tenant, a corresponding service principal exists; that for every service principal of type `Application` in the home tenant, an `Application` object exists; and that where Entra Agent ID is in use, the Agent ID resolves to a known App + SP pair.
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. Build the join key `appId` across `surface-entra-apps.json` and `surface-entra-sps.json`. Filter SPs to `servicePrincipalType eq 'Application'` AND `appOwnerOrganizationId eq <home tenant ID>`.
  2. Compute the symmetric difference: `apps-without-sp.csv` (apps in home tenant with no SP) and `sps-without-app.csv` (home-tenant SPs with no application object).
  3. For Entra Agent ID entries, resolve each Agent ID to its underlying App + SP via the documented Agent ID → App linkage; output `agentid-without-app.csv` for any unresolved.
  4. Compute `reg-03-join-summary.json` with counts and exception list.
- **Expected result.** All three delta files exist (even if empty); zero rows in each delta file or every row is exception-tracked.
- **Pass criteria.** `apps-without-sp.csv` row count is 0 OR every row has a documented reason (e.g., "newly created within the last refresh window — re-test after PPAC ~15 min refresh"); `sps-without-app.csv` row count is 0 OR rows are exception-tracked; `agentid-without-app.csv` row count is 0 OR exception-tracked.
- **Failure remediation.** For an `Application` with no SP in the home tenant, instantiate the SP via `New-MgServicePrincipal -AppId <appId>` (or equivalent); for an SP with no application object, investigate whether the SP is for a deleted app and decommission via Control 3.6; for an Agent ID with no App, escalate to Microsoft support and document as a SOV-03 compensating-control note.
- **Evidence.** `apps-without-sp.csv`, `sps-without-app.csv`, `agentid-without-app.csv`, `reg-03-join-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Entra Application Admin.
- **Zone applicability.** All zones.

#### 1.2-REG-04 — Publisher verification or compensating documentation

- **Objective.** Confirm that every partner-built agent / Integrated App in scope is published by an Entra Verified Publisher OR has a documented compensating publisher review on file. Confirm that every internally-developed agent surfaced in the Microsoft 365 Agent Store is published under the firm's own Verified Publisher status.
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. From `surface-entra-apps.json`, extract the `verifiedPublisher` block for each multi-tenant or partner-built app referenced in `surface-integrated-apps.csv`.
  2. Classify each app as `VERIFIED_PUBLISHER`, `INTERNAL_VERIFIED_PUBLISHER` (the firm's own Verified Publisher MPN), `UNVERIFIED_WITH_COMPENSATING_REVIEW`, or `UNVERIFIED_NO_REVIEW`.
  3. Cross-reference `UNVERIFIED_WITH_COMPENSATING_REVIEW` rows with the firm's third-party / vendor-risk-management register to confirm a current review exists.
  4. Output `reg-04-publisher-verification.csv` with classification per app and the supporting evidence reference.
- **Expected result.** Every partner-built / Integrated App is one of `VERIFIED_PUBLISHER` or `UNVERIFIED_WITH_COMPENSATING_REVIEW`; zero `UNVERIFIED_NO_REVIEW` rows. Every internally-published store agent is `INTERNAL_VERIFIED_PUBLISHER`.
- **Pass criteria.** `UNVERIFIED_NO_REVIEW` count is 0 OR every such row is in active remediation with a due date inside the zone cadence and is removed from any Zone 2 / Zone 3 user assignment until cleared.
- **Failure remediation.** For each unverified-without-review app: initiate vendor-risk review through the firm's TPRM intake; until the review completes, restrict the app's user assignment to a sandbox group and record the restriction action in evidence.
- **Evidence.** `reg-04-publisher-verification.csv`, `reg-04-tprm-references.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones; Zone 3 monthly is binding for any tenant with partner-built agents in production.

---

### 7.OWN — Ownership integrity

This family verifies that every Entra App Registration in scope has a current, resolvable owner of record; that Zone 2 / Zone 3 apps have a Backup Owner; that departed-owner reassignment runs within the zone SLA; and that the ownerless-app remediation queue is being worked.

#### 1.2-OWN-01 — Active owner present on every Application and Service Principal

- **Objective.** Confirm that every Entra App Registration and home-tenant service principal in scope has at least one owner of record whose UPN resolves to an active, non-disabled Entra user, and that the owner is not a service principal itself unless explicitly approved (workload-managed apps).
- **Pre-conditions.** REG-01 PASS, REG-03 PASS.
- **Steps.**
  1. For each application in `surface-entra-apps.json`, query owners: `GET /applications/{id}/owners`.
  2. For each home-tenant service principal in `surface-entra-sps.json`, query owners: `GET /servicePrincipals/{id}/owners`.
  3. For each owner, resolve the owner principal via `GET /users/{id}` or `GET /servicePrincipals/{id}` and capture `accountEnabled`, `userType`, `assignedLicenses`, and last sign-in.
  4. Classify each app / SP as `OWNED_ACTIVE_USER`, `OWNED_ACTIVE_SP_APPROVED`, `OWNED_DISABLED_USER`, `OWNED_DEPARTED` (where the owner has a `userType eq 'Member'` but `accountEnabled eq false` and a Lifecycle Workflow leaver event), `OWNERLESS`.
  5. Output `own-01-ownership.csv` with one row per app / SP and classification.
- **Expected result.** Zero `OWNERLESS` rows; zero `OWNED_DISABLED_USER` rows in Zone 2 / Zone 3; zero `OWNED_DEPARTED` rows beyond the OWN-03 reassignment SLA window.
- **Pass criteria.** `OWNERLESS` count is 0 (any orphan halts the cycle and escalates to Control 3.6); `OWNED_DISABLED_USER` and `OWNED_DEPARTED` counts in Zone 2 / Zone 3 are 0 OR every row is in active remediation with an open OWN-03 ticket within SLA.
- **Failure remediation.** For each ownerless app: search UAL `Remove owner from application` events for the trailing 90 days to identify the prior owner; engage the AI Governance Lead to assign a new owner from the agent's sponsoring business unit; record the assignment in UAL via `Add owner to application`. For Zone 3 ownerless apps, treat as Critical per Section 11.
- **Evidence.** `own-01-ownership.csv`, `own-01-summary.json`, UAL `Add owner` event references for any remediations.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones.

#### 1.2-OWN-02 — Backup Owner present on Zone 2 / Zone 3 registrations

- **Objective.** Confirm that every Zone 2 and Zone 3 application has a designated Backup Owner whose UPN resolves to an active Entra user and who is distinct from the primary owner.
- **Pre-conditions.** OWN-01 PASS.
- **Steps.**
  1. Join `own-01-ownership.csv` to the registration-governance store's Backup Owner field (SharePoint list, Dataverse, or equivalent).
  2. For each Zone 2 / Zone 3 row, confirm: (a) Backup Owner field is populated; (b) Backup Owner UPN resolves to an active Entra user; (c) Backup Owner is distinct from primary owner; (d) Backup Owner is also listed as an owner on the underlying Entra app object (not just the governance store).
  3. Output `own-02-backup-owner.csv` with classification: `BACKUP_RESOLVED_AND_ENTRA_OWNER`, `BACKUP_RESOLVED_BUT_NOT_ENTRA_OWNER`, `BACKUP_DEPARTED`, `BACKUP_MISSING`.
- **Expected result.** Every Zone 2 / Zone 3 row resolves to `BACKUP_RESOLVED_AND_ENTRA_OWNER`.
- **Pass criteria.** `BACKUP_MISSING` and `BACKUP_DEPARTED` counts are 0 in Zone 2 / Zone 3; `BACKUP_RESOLVED_BUT_NOT_ENTRA_OWNER` is treated as a Medium finding requiring remediation within 14 days (Backup Owner should also be a directory-resolvable owner so they can act in an emergency).
- **Failure remediation.** For each missing Backup Owner: engage the agent's Sponsor to nominate a Backup; add the Backup as an owner on the Entra app via `POST /applications/{id}/owners/$ref`; update the governance store; record both actions in evidence.
- **Evidence.** `own-02-backup-owner.csv`, `own-02-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Agent Owner.
- **Zone applicability.** Zone 2 and Zone 3 only.

#### 1.2-OWN-03 — Departed-owner reassignment within zone SLA

- **Objective.** Confirm that when an owner of record departs the firm (Lifecycle Workflows leaver event, account disablement, or Entra user deletion), the application is reassigned to a new owner within the zone SLA: Zone 1 ≤ 30 days, Zone 2 ≤ 14 days, Zone 3 ≤ 5 business days.
- **Pre-conditions.** OWN-01 PASS, OWN-02 PASS.
- **Steps.**
  1. Pull Lifecycle Workflows leaver events and Entra user disablement events for the trailing 12 months from UAL.
  2. Cross-reference to `own-01-ownership.csv` to identify any current owner who appears in the leaver-event set.
  3. For each historical leaver who was an owner, find the UAL `Add owner to application` event that replaced them; compute time-to-reassignment.
  4. Compare time-to-reassignment to the zone SLA.
  5. Output `own-03-reassignment-sla.csv` with one row per departed-owner-app pair and the SLA result.
- **Expected result.** Every reassignment completed within the zone SLA; current state has no app where the departed owner is still the sole owner.
- **Pass criteria.** Zone 3 reassignments p95 ≤ 5 business days; Zone 2 p95 ≤ 14 days; Zone 1 p95 ≤ 30 days. Zero current-state apps with a departed sole owner.
- **Failure remediation.** For each over-SLA case, open a remediation ticket; perform the reassignment immediately; update OWN-03 with the corrective action and root cause (e.g., "Leaver event was not piped to Lifecycle Workflows; reassignment workflow did not trigger"). Repeat over-SLA failures escalate the namespace cadence per Section 4.
- **Evidence.** `own-03-reassignment-sla.csv`, `own-03-rca.md` for any over-SLA case.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Entra Identity Governance Admin.
- **Zone applicability.** All zones.

#### 1.2-OWN-04 — Ownerless-app remediation queue health

- **Objective.** Confirm that the ownerless-app remediation queue (per Control 3.6) is being actively worked, that no item is stuck beyond the queue SLA, and that escalation paths from this cycle to Control 3.6 are intact.
- **Pre-conditions.** OWN-01 PASS.
- **Steps.**
  1. Pull the ownerless-app queue from the firm's ITSM / governance store.
  2. For each item, capture intake date, current state, age, assigned remediator, and last activity.
  3. Compute queue-aging stats (count by age bucket: 0–7 days, 8–30 days, 31–60 days, > 60 days).
  4. Cross-reference to OWN-01 outputs from this cycle and the trailing two cycles to confirm no `OWNERLESS` row from a prior cycle has aged out without resolution.
- **Expected result.** Zero items aged > 60 days in any queue; trend is stable or declining.
- **Pass criteria.** No item aged > 60 days OR every aged item has documented sponsor adjudication notes and a forced-decommission action scheduled. Items aged 31–60 days are flagged Medium per Section 11.
- **Failure remediation.** For each aged item, escalate to AI Governance Lead for forced reassignment or decommission; if neither is possible (e.g., the agent is in active production but no business unit will claim it), invoke the AI Incident Response Playbook for cross-functional adjudication.
- **Evidence.** `own-04-queue-aging.csv`, `own-04-summary.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Entra Identity Governance Admin.
- **Zone applicability.** All zones.

---

### 7.PERM — Permission grant minimization

This family verifies that no application holds a Graph or connector permission outside its approved scope, that no orphaned consent grants linger, that sensitive scopes require admin consent, and that permission drift since the last attestation is detected.

#### 1.2-PERM-01 — No over-scoped grants vs. Graph permissions matrix

- **Objective.** Confirm that for every application in scope, the union of its delegated permissions (`/oauth2PermissionGrants`) and application permissions (`/appRoleAssignments` for the Microsoft Graph SP) is a subset of what the Graph permissions matrix authorizes for that application's zone and business purpose.
- **Pre-conditions.** REG-01 PASS, PRE-01 PASS (matrix is current).
- **Steps.**
  1. For each application in `surface-entra-apps.json`, query its service principal: `GET /servicePrincipals(appId='{appId}')`.
  2. Query delegated grants: `GET /oauth2PermissionGrants?$filter=clientId eq '{spId}'`.
  3. Query app role assignments: `GET /servicePrincipals/{spId}/appRoleAssignments`.
  4. Resolve each scope / app-role to its human-readable name (e.g., `Mail.Read`, `Files.ReadWrite.All`).
  5. Look up the application in the Graph permissions matrix; compute `granted - approved` for both delegated and application sets.
  6. Output `perm-01-overscoped.csv` with one row per app / over-scope finding.
- **Expected result.** `perm-01-overscoped.csv` row count is 0.
- **Pass criteria.** Row count 0 OR every row is exception-tracked with a documented business justification and a due-date for either matrix update or scope reduction. Any row with a high-privilege scope (`*.ReadWrite.All`, `Directory.ReadWrite.All`, `Sites.FullControl.All`, `RoleManagement.ReadWrite.Directory`, `User.Read.All` for Zone 3 finance agents, or any scope marked High in the firm's matrix) is treated as Critical and halts the cycle.
- **Failure remediation.** For each over-scope finding: (a) confirm the grant is current (re-query Graph); (b) revoke the grant via `DELETE /oauth2PermissionGrants/{id}` or `DELETE /servicePrincipals/{spId}/appRoleAssignments/{id}` after sponsor sign-off; (c) record the revocation in UAL; (d) re-test PERM-01.
- **Evidence.** `perm-01-overscoped.csv`, `perm-01-revocations.json`, UAL revocation event references.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones.

#### 1.2-PERM-02 — No orphaned consent grants

- **Objective.** Confirm that every `oauth2PermissionGrant` in the tenant references a current `clientId` (existing service principal), `principalId` (existing user, if delegated), and `resourceId` (existing service principal). Orphaned grants — grants whose referent has been deleted — are leftover authorization noise that complicates audit and that can be revived by SP recreation under the same `appId`.
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. Pull all `/oauth2PermissionGrants` in the tenant.
  2. For each grant, attempt to resolve `clientId`, `principalId` (if not null), and `resourceId` to a current directory object.
  3. Classify each grant: `RESOLVED`, `ORPHAN_CLIENT_DELETED`, `ORPHAN_PRINCIPAL_DELETED`, `ORPHAN_RESOURCE_DELETED`.
  4. Output `perm-02-orphan-grants.csv`.
- **Expected result.** Zero orphan grants.
- **Pass criteria.** Orphan count 0 OR every orphan has a documented remediation action scheduled within 14 days. Any orphan referencing a previously-deleted high-privilege scope is treated as Critical (revival risk).
- **Failure remediation.** Revoke orphan grants via `DELETE /oauth2PermissionGrants/{id}` after Compliance Officer sign-off; record the revocation in UAL.
- **Evidence.** `perm-02-orphan-grants.csv`, `perm-02-revocations.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Entra Application Admin.
- **Zone applicability.** All zones.

#### 1.2-PERM-03 — Admin-consent required for sensitive scopes

- **Objective.** Confirm that the tenant's user-consent setting requires admin consent for any sensitive scope (per the firm's matrix), and that no non-admin grants exist for sensitive scopes.
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. Read the tenant's authorization policy: `GET /policies/authorizationPolicy`.
  2. Confirm `defaultUserRolePermissions.permissionGrantPoliciesAssigned` is the firm's policy ID for "low-risk delegated permissions only" (or equivalent restrictive policy).
  3. Read the permission grant policy: `GET /policies/permissionGrantPolicies/{id}`.
  4. Cross-reference the policy's allowed scope set against the firm's "non-sensitive" scope list; any scope in the policy that is on the firm's "sensitive" list is a finding.
  5. Pull `/oauth2PermissionGrants` where `consentType eq 'Principal'` (user consent, not admin consent) and inspect the granted scopes for any sensitive scope.
  6. Output `perm-03-sensitive-consent.csv`.
- **Expected result.** Authorization policy restricts user consent to non-sensitive scopes only; zero user-consent grants exist for sensitive scopes.
- **Pass criteria.** Authorization policy is correctly configured AND user-consent grants for sensitive scopes count is 0.
- **Failure remediation.** Update `authorizationPolicy.defaultUserRolePermissions` to assign the restrictive permission grant policy; revoke any non-conforming user-consent grants; trigger an admin consent request from the affected user via the admin consent workflow.
- **Evidence.** `perm-03-auth-policy.json`, `perm-03-sensitive-consent.csv`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Entra Application Admin.
- **Zone applicability.** All zones.

#### 1.2-PERM-04 — Permission drift since last attestation

- **Objective.** Confirm that no application's permission set changed since the last cycle's attestation without a re-attestation event. This is the registration-plane equivalent of a "configuration drift" check.
- **Pre-conditions.** PERM-01 PASS; previous cycle's `perm-01-overscoped.csv` and `perm-snapshot.json` exist in the evidence store.
- **Steps.**
  1. Construct the current cycle's `perm-snapshot.json`: for each app in scope, the set of granted scopes (delegated + app-role) with grant ID and grant timestamp.
  2. Diff against the previous cycle's `perm-snapshot.json`.
  3. For each diff entry (added scope, removed scope, modified consent type), check whether a corresponding re-attestation record exists in the registration-governance store.
  4. Output `perm-04-drift.csv` with one row per drift event and the re-attestation status.
- **Expected result.** Every drift event has a corresponding re-attestation record; ideally drift count is small.
- **Pass criteria.** Drift events without re-attestation count 0 OR every such event is in active remediation. Where Defender for Cloud Apps (App Governance) is available, cross-reference its drift detections to confirm the cycle did not miss any.
- **Failure remediation.** For each unattested drift: (a) identify the actor from UAL `Add app role assignment grant to user` / `Consent to application` events; (b) confirm the change was authorized; (c) if authorized, create the missing re-attestation record; (d) if unauthorized, revoke the grant and trigger the AI Incident Response Playbook.
- **Evidence.** `perm-snapshot.json`, `perm-04-drift.csv`, `perm-04-rca.md` for unauthorized drifts.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones; Zone 3 monthly is the binding cadence.

---

### 7.CRED — Credential hygiene

This family verifies that no application authenticates with an expired or unmanaged secret, that Zone 3 applications prefer certificate-based or federated credential authentication, and that the rotation cadence required by zone policy is being met.

#### 1.2-CRED-01 — No expired client secrets in active use

- **Objective.** Confirm that no application service principal has signed in within the trailing 30 days using a client secret that is now expired (per `passwordCredentials.endDateTime`) or that was already expired at the time of sign-in.
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. For each application in scope, enumerate `passwordCredentials` and `keyCredentials` via `GET /applications/{id}` and capture `keyId`, `startDateTime`, `endDateTime`, `displayName`.
  2. Pull SP sign-in logs for the trailing 30 days from Entra Sign-in Logs / `/auditLogs/signIns?$filter=signInEventTypes/any(t:t eq 'servicePrincipal')`.
  3. For each sign-in event, capture the `appId`, `servicePrincipalId`, `authenticationDetails`, and the `keyId` used (where exposed).
  4. Cross-reference: any sign-in whose `keyId` corresponds to a credential whose `endDateTime` is in the past (relative to the sign-in time or the cycle date) is a finding.
  5. Output `cred-01-expired-in-use.csv`.
- **Expected result.** Zero rows.
- **Pass criteria.** Expired-in-use count is 0. Any nonzero result is treated as Critical (the platform is allowing post-expiry authentication or the operator has rotated `endDateTime` to mask the lapse).
- **Failure remediation.** Immediately rotate the affected credential to a new secret or, preferably, a certificate; revoke the expired secret; record both actions in evidence and in UAL.
- **Evidence.** `cred-01-expired-in-use.csv`, `cred-01-rotation-actions.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones.

#### 1.2-CRED-02 — Certificate-based or federated authentication preference in Zone 3

- **Objective.** Confirm that at least the firm's policy floor (typically ≥ 80% per the AI Governance charter — verify against PRE-04 baseline) of Zone 3 applications authenticate via certificate-based credentials (`keyCredentials`) or federated identity credentials (workload identity federation), and that any Zone 3 application still using a long-lived client secret has a documented exception with an expiry date.
- **Pre-conditions.** REG-01 PASS, CRED-01 PASS.
- **Steps.**
  1. For each Zone 3 application, classify the active credential type: `CERTIFICATE`, `FEDERATED`, `MANAGED_IDENTITY` (where the workload runs on Azure compute with a managed identity instead of an app-registration credential), `CLIENT_SECRET`.
  2. Output `cred-02-z3-credential-type.csv`.
  3. Compute the Z3 certificate-or-federated coverage rate.
- **Expected result.** Coverage rate ≥ firm's policy floor (typically ≥ 80% per PRE-04 baseline); every `CLIENT_SECRET` row has a documented exception.
- **Pass criteria.** Coverage rate ≥ policy floor AND every `CLIENT_SECRET` row in Zone 3 has a documented, dated exception with an expiry date in force.
- **Failure remediation.** For each Zone 3 application using a client secret without exception: schedule migration to certificate or federated credential; record the migration plan with target date; if migration is not feasible (legacy connector, third-party requirement), file a formal exception with AI Governance Lead and Compliance Officer co-signature.
- **Evidence.** `cred-02-z3-credential-type.csv`, `cred-02-exceptions.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Agent Owner.
- **Zone applicability.** Zone 3 binding; Zone 2 advisory; Zone 1 informational only.

#### 1.2-CRED-03 — Rotation cadence per zone policy

- **Objective.** Confirm that every active credential's age (from `startDateTime` to cycle date) is within the zone's rotation policy: Zone 1 ≤ 24 months, Zone 2 ≤ 12 months, Zone 3 ≤ 90 days for client secrets and ≤ 12 months for certificates (or stricter per firm policy in PRE-04).
- **Pre-conditions.** REG-01 PASS.
- **Steps.**
  1. For each application, compute the age of every active (non-expired) credential.
  2. Compare to zone policy.
  3. Output `cred-03-rotation.csv` with rows for any over-cadence credential.
- **Expected result.** Zero over-cadence credentials.
- **Pass criteria.** Over-cadence count 0 OR every over-cadence row has an active rotation ticket within 14 days. Any Zone 3 client secret over 90 days old is treated as High.
- **Failure remediation.** Initiate rotation; new credential is provisioned and validated in production; old credential is removed from `passwordCredentials` / `keyCredentials`; rotation event is captured in UAL `Update application — Certificates and secrets management`.
- **Evidence.** `cred-03-rotation.csv`, `cred-03-rotation-actions.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 weekly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones.

#### 1.2-CRED-04 — Federated / managed identity preference where the workload supports it

- **Objective.** Confirm that for any application whose workload runs on Azure compute that supports managed identities (App Service, Functions, AKS, VM, Container Apps) or whose workload runs on a federation-capable platform (GitHub Actions, Azure DevOps, external IdP), the credential is a managed identity or federated identity credential rather than a client secret, unless an exception is recorded.
- **Pre-conditions.** REG-01 PASS, CRED-02 PASS.
- **Steps.**
  1. Cross-reference each application's hosting environment (recorded in the registration-governance store) against the platform-capability table for managed-identity / federated-credential support.
  2. For each application whose hosting platform supports managed identity / federation but the active credential is a client secret, record as a finding.
  3. Output `cred-04-federation-gap.csv`.
- **Expected result.** Zero gap rows or every gap row has a documented exception.
- **Pass criteria.** Gap count 0 OR every row has a remediation plan within 90 days.
- **Failure remediation.** Migrate the workload to managed identity or federated credential; once the workload is using the new credential, remove the client secret.
- **Evidence.** `cred-04-federation-gap.csv`, `cred-04-migration-plan.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Agent Owner.
- **Zone applicability.** All zones; Zone 3 binding.

---

### 7.CONSENT — Consent governance integrity

This family verifies that the admin consent workflow is active, that the reviewer queue is being worked within the firm's SLA, that user consent restrictions are enforced, and that every consent grant has an audit trail.

#### 1.2-CONSENT-01 — Admin consent workflow active

- **Objective.** Confirm that the admin consent request workflow is enabled in the tenant, that reviewers are configured, that the request expiry is set per firm policy, and that reviewer notifications are flowing.
- **Pre-conditions.** PRE-03 PASS.
- **Steps.**
  1. Read the admin consent request policy: `GET /policies/adminConsentRequestPolicy`.
  2. Confirm `isEnabled eq true`, `notifyReviewers eq true`, `remindersEnabled eq true`, `requestDurationInDays` matches firm policy.
  3. Confirm `reviewers` collection is non-empty and references active users / groups, not departed accounts.
  4. Send a smoke-test admin consent request from a non-admin test account for a low-impact scope and confirm the reviewer queue receives it.
- **Expected result.** Workflow is enabled, reviewers are active, smoke test succeeds.
- **Pass criteria.** All policy fields conform AND the smoke test reaches the reviewer queue within the documented latency.
- **Failure remediation.** Enable the workflow; populate reviewer roster from the AI Governance group; re-run smoke test.
- **Evidence.** `consent-01-policy.json`, `consent-01-smoke-test.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones.

#### 1.2-CONSENT-02 — Reviewer queue SLA

- **Objective.** Confirm that the admin consent request queue is being worked within the firm's reviewer SLA (typically 5 business days for non-sensitive scopes, 2 business days for sensitive scopes — verify PRE-04 baseline).
- **Pre-conditions.** CONSENT-01 PASS.
- **Steps.**
  1. Pull all admin consent requests for the trailing 90 days: `GET /identityGovernance/appConsent/appConsentRequests`.
  2. For each request, capture `createdDateTime`, `reviewedDateTime`, `decision`, `reviewerId`, scope set.
  3. Compute time-to-decision per request.
  4. Compare to SLA by scope sensitivity.
  5. Output `consent-02-queue-sla.csv`.
- **Expected result.** All decisions within SLA; ideally backlog of pending requests is small.
- **Pass criteria.** Pending requests aged > SLA count is 0; trailing-90-day p95 time-to-decision ≤ SLA. Where Defender for Cloud Apps app-governance is available, cross-reference its risky-app review queue to confirm the cycle did not miss off-platform consent flows.
- **Failure remediation.** For each over-SLA request, escalate to AI Governance Lead for immediate decision; root-cause why the queue aged out (reviewer absence, notification failure); remediate.
- **Evidence.** `consent-02-queue-sla.csv`, `consent-02-rca.md` for over-SLA cases.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Compliance Officer.
- **Zone applicability.** All zones.

#### 1.2-CONSENT-03 — User consent restriction enforced

- **Objective.** Confirm that the tenant's user consent setting is configured to allow user consent only for applications from verified publishers and only for low-risk delegated scopes (or the firm's stricter equivalent).
- **Pre-conditions.** PRE-03 PASS, PERM-03 PASS.
- **Steps.**
  1. Read `authorizationPolicy.defaultUserRolePermissions.permissionGrantPoliciesAssigned`.
  2. Confirm the assigned policy is `microsoft-user-default-low` (verified-publisher + low-risk delegated only) OR a tenant-defined stricter policy.
  3. Read the assigned policy detail and capture the includes/excludes scope set.
  4. Output `consent-03-user-consent-policy.json`.
- **Expected result.** Restrictive policy is assigned; the policy's scope set matches firm policy.
- **Pass criteria.** Assigned policy ID matches the firm's documented value AND scope set conforms.
- **Failure remediation.** Update the authorization policy; verify with a test user account that user consent for a sensitive scope is blocked.
- **Evidence.** `consent-03-user-consent-policy.json`, `consent-03-test-block.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Entra Application Admin.
- **Zone applicability.** All zones.

#### 1.2-CONSENT-04 — Consent grant audit trail completeness

- **Objective.** Confirm that for every `oauth2PermissionGrant` and `appRoleAssignment` created in the trailing 90 days, a corresponding UAL event (`Consent to application`, `Add app role assignment grant to user`, or `Add delegated permission grant`) exists, with actor, scope, and target resolvable.
- **Pre-conditions.** REG-01 PASS, PERM-02 PASS.
- **Steps.**
  1. From `surface-ual-app-events.csv`, filter to consent / grant events in the trailing 90 days.
  2. From the current `/oauth2PermissionGrants` and `/appRoleAssignments`, identify grants whose `createdDateTime` is in the trailing 90 days.
  3. Join: every recent grant should have a corresponding UAL event; every UAL grant event should map to a current grant (or a documented revocation).
  4. Output `consent-04-trail-gaps.csv`.
- **Expected result.** Zero gaps in either direction.
- **Pass criteria.** Gap count 0 OR every gap is exception-tracked. Any gap involving a Zone 3 sensitive scope is treated as Critical (potential evidence-trail tampering or UAL ingestion failure).
- **Failure remediation.** For UAL-missing grants, open a Microsoft support case to investigate UAL ingestion gaps; for orphan UAL events with no current grant, confirm the grant was revoked and record the revocation reference.
- **Evidence.** `consent-04-trail-gaps.csv`, `consent-04-msft-cases.json`.
- **Cadence.** Zone 1 quarterly · Zone 2 monthly · Zone 3 monthly.
- **Owner.** Purview Compliance Admin.
- **Zone applicability.** All zones.

---

### 7.CA — Conditional Access for workload identities

This family verifies that Zone 3 service principals are covered by an SP-targeted Conditional Access policy, that workload identity sign-in risk policies are active where licensed, and that the CA policy exclusion list is reviewed.

#### 1.2-CA-01 — Zone 3 service principals covered by SP-targeted CA policy

- **Objective.** Confirm that every Zone 3 service principal is covered by at least one Conditional Access policy whose `conditions.clientApplications.includeServicePrincipals` either explicitly includes the SP or includes a group / tag the SP belongs to, and whose grant control imposes at least the firm's minimum (typically: location restriction to allowed IP ranges, device compliance where applicable, block on risky sign-in).
- **Pre-conditions.** REG-01 PASS, PRE-03 PASS (P1 floor confirmed).
- **Steps.**
  1. Pull all CA policies: `GET /identity/conditionalAccess/policies`.
  2. Filter to policies that target service principals (workload identity CA).
  3. For each Zone 3 SP in scope, evaluate whether at least one such policy applies.
  4. Output `ca-01-coverage.csv` with `appId`, `spId`, `coveringPolicyIds`, `gapType`.
- **Expected result.** Every Zone 3 SP is covered by at least one SP-targeted CA policy.
- **Pass criteria.** Zone 3 coverage rate is 100% OR every uncovered SP has a documented exception with a compensating control (e.g., tenant-level IP restriction, sign-in event monitoring).
- **Failure remediation.** Add the missing SPs to the existing SP-targeted CA policy or create a new policy targeting the firm's "Zone 3 workload identities" group; verify with a sign-in test from outside the allowed location.
- **Evidence.** `ca-01-coverage.csv`, `ca-01-policies.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Conditional Access Admin.
- **Zone applicability.** Zone 3 binding; Zone 2 advisory.

#### 1.2-CA-02 — Workload identity sign-in risk policy active

- **Objective.** Confirm that, where Entra ID P2 / Identity Protection workload identity risk is licensed and available in the cloud, a sign-in risk policy is active that blocks or requires step-up for high-risk SP sign-ins.
- **Pre-conditions.** PRE-03 PASS (P2 confirmed), PRE-06 PASS (cloud parity for Identity Protection).
- **Steps.**
  1. Read the workload identity risk policy from Identity Protection.
  2. Confirm policy is enabled, scoped to all SPs (or at minimum all Zone 2 / Zone 3 SPs), and grant control blocks high risk.
  3. Pull `riskyServicePrincipals` for the trailing 90 days; confirm each high-risk SP has a recorded action (blocked, dismissed with reason, remediated).
  4. Output `ca-02-risk-policy.json`, `ca-02-risky-sps.csv`.
- **Expected result.** Policy is active and scoped correctly; risky SPs are being triaged.
- **Pass criteria.** Policy active AND no risky SP aged > 14 days without action.
- **Failure remediation.** Enable the policy; triage existing risky SPs; for each, document action and rationale.
- **Evidence.** `ca-02-risk-policy.json`, `ca-02-risky-sps.csv`, `ca-02-triage-notes.md`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 monthly.
- **Owner.** Conditional Access Admin.
- **Zone applicability.** Zone 2 and Zone 3; Zone 1 advisory.

#### 1.2-CA-03 — CA policy exclusion list reviewed

- **Objective.** Confirm that any user, group, or service principal excluded from a SP-targeting CA policy is on a documented exclusion list with a stated rationale and an expiry date, and that no Zone 3 SP is silently excluded.
- **Pre-conditions.** CA-01 PASS.
- **Steps.**
  1. For each CA policy targeting workload identities, capture the exclusion set (`conditions.clientApplications.excludeServicePrincipals`, `conditions.users.excludeGroups`, `conditions.users.excludeUsers`).
  2. Cross-reference exclusions to the firm's exclusion register.
  3. Identify any Zone 3 SP in any exclusion list.
  4. Output `ca-03-exclusions.csv`.
- **Expected result.** Every exclusion is justified, dated, and within its review window; zero Zone 3 SPs in exclusions.
- **Pass criteria.** Unjustified exclusions count 0; Zone 3 exclusions count 0 OR explicit exception with co-signature.
- **Failure remediation.** Remove unjustified exclusions; for justified-but-undocumented exclusions, file a formal exception; for Zone 3 SP exclusions, escalate to AI Governance Lead for immediate review.
- **Evidence.** `ca-03-exclusions.csv`, `ca-03-register-references.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Conditional Access Admin.
- **Zone applicability.** All zones.

---

### 7.SPONSOR — Sponsorship integrity

This family verifies that every Zone 2 / Zone 3 agent has an active Sponsor and Backup Sponsor, that sponsor approvals have an audit trail, that quarterly sponsor attestations are completed, and that sponsor departures are handled within SLA.

#### 1.2-SPONSOR-01 — Active Sponsor and Backup Sponsor on every Zone 2 / Zone 3 agent

- **Objective.** Confirm that every Zone 2 / Zone 3 agent has a recorded Agent Sponsor whose UPN resolves to an active Entra user, plus a Backup Sponsor distinct from the primary.
- **Pre-conditions.** REG-01 PASS, OWN-01 PASS.
- **Steps.**
  1. Join the registration-governance store's Sponsor / Backup Sponsor fields to the in-scope agent set.
  2. Resolve each Sponsor UPN against Entra; confirm `accountEnabled eq true`, `userType` is appropriate.
  3. Output `sponsor-01-coverage.csv` with classifications: `SPONSOR_AND_BACKUP_ACTIVE`, `SPONSOR_ACTIVE_NO_BACKUP`, `SPONSOR_DEPARTED`, `SPONSOR_MISSING`.
- **Expected result.** All Zone 2 / Zone 3 rows are `SPONSOR_AND_BACKUP_ACTIVE`.
- **Pass criteria.** `SPONSOR_DEPARTED` and `SPONSOR_MISSING` counts 0 in Z2 / Z3; `SPONSOR_ACTIVE_NO_BACKUP` count 0 in Z3.
- **Failure remediation.** Engage business unit leadership to designate Sponsor / Backup; record assignment in the governance store with co-signature; update Section 1 attestation roster.
- **Evidence.** `sponsor-01-coverage.csv`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Agent Sponsor.
- **Zone applicability.** Zone 2 and Zone 3.

#### 1.2-SPONSOR-02 — Sponsor approval audit trail per registration

- **Objective.** Confirm that the original Sponsor approval that authorized each agent's registration exists in the governance store and is linked to the registration record by registration ID.
- **Pre-conditions.** SPONSOR-01 PASS.
- **Steps.**
  1. For each agent, retrieve the original sponsor approval record (registration intake form, signed approval, or workflow output).
  2. Confirm the approval references the agent's current `appId`, current zone, and current business purpose. If any of those have changed since approval, a re-approval should exist.
  3. Output `sponsor-02-approvals.csv` with classification: `APPROVAL_CURRENT`, `APPROVAL_STALE_NEEDS_REAPPROVAL`, `APPROVAL_MISSING`.
- **Expected result.** All `APPROVAL_CURRENT`.
- **Pass criteria.** `APPROVAL_MISSING` count 0; `APPROVAL_STALE_NEEDS_REAPPROVAL` count 0 in Z3 OR every stale row has a re-approval ticket within 30 days.
- **Failure remediation.** Retrieve missing approvals from prior systems of record; if unrecoverable, treat the agent as un-sponsored and trigger SPONSOR-01 remediation; update the registration record with the approval reference.
- **Evidence.** `sponsor-02-approvals.csv`, `sponsor-02-approval-references.json`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Compliance Officer.
- **Zone applicability.** Zone 2 and Zone 3.

#### 1.2-SPONSOR-03 — Quarterly sponsor attestation completed

- **Objective.** Confirm that the Agent Sponsor for each Zone 2 / Zone 3 agent has completed the quarterly attestation that the agent is still business-justified, still scoped correctly, and still operating within the approved zone.
- **Pre-conditions.** SPONSOR-01 PASS, SPONSOR-02 PASS.
- **Steps.**
  1. Pull the trailing-quarter Sponsor attestation submissions from the governance store.
  2. Cross-reference to in-scope Z2 / Z3 agents.
  3. For each agent, confirm an attestation submission exists in the trailing-quarter window, signed by the active Sponsor, with a structured response (justification statement, zone confirmation, change disclosure).
  4. Output `sponsor-03-attestation.csv` with classification: `ATTESTED`, `OVERDUE`, `MISSING`, `SUBMITTED_BY_NON_SPONSOR`.
- **Expected result.** All `ATTESTED`.
- **Pass criteria.** `MISSING` and `SUBMITTED_BY_NON_SPONSOR` counts 0 in Z2 / Z3; `OVERDUE` count 0 OR every overdue row has an open ticket within 14 days. See [Sponsorship Lifecycle Workflows](./sponsorship-lifecycle-workflows.md) for the attestation ceremony.
- **Failure remediation.** Notify Sponsor with escalation copy to Backup Sponsor and AI Governance Lead; if Sponsor is unreachable for > 30 days, trigger Backup activation via SPONSOR-04.
- **Evidence.** `sponsor-03-attestation.csv`, attestation submission references.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Agent Sponsor.
- **Zone applicability.** Zone 2 and Zone 3.

#### 1.2-SPONSOR-04 — Sponsor departure handling SLA

- **Objective.** Confirm that when a Sponsor departs the firm (Lifecycle Workflows leaver event), the agents they sponsor are reassigned to a new Sponsor (or the Backup is activated) within zone SLA: Z2 ≤ 30 days, Z3 ≤ 14 days.
- **Pre-conditions.** SPONSOR-01 PASS.
- **Steps.**
  1. Pull leaver events for the trailing 12 months from Lifecycle Workflows / UAL.
  2. Cross-reference to historical Sponsor assignments.
  3. For each departed Sponsor, find the reassignment record in the governance store; compute time-to-reassignment.
  4. Compare to zone SLA.
  5. Output `sponsor-04-reassignment.csv`.
- **Expected result.** All reassignments within SLA.
- **Pass criteria.** Z3 p95 ≤ 14 days; Z2 p95 ≤ 30 days; zero current-state agents with a departed sole Sponsor.
- **Failure remediation.** For each over-SLA case, perform reassignment immediately; root-cause the delay; if Lifecycle Workflows did not pipe the leaver event into the sponsorship reassignment workflow, remediate the workflow.
- **Evidence.** `sponsor-04-reassignment.csv`, `sponsor-04-rca.md`.
- **Cadence.** Zone 1 annual · Zone 2 quarterly · Zone 3 quarterly.
- **Owner.** Agent Sponsor.
- **Zone applicability.** Zone 2 and Zone 3.

---

### 7.SOV — Sovereign cloud boundary attestation

This family verifies that every registration entry has a sovereign-cloud designation, that cross-cloud service principals are detected and flagged, and that per-cloud feature parity gaps are documented as compensating-control conversations.

#### 1.2-SOV-01 — Cloud designation present on every registration

- **Objective.** Confirm that every registration entry in the governance store has an explicit sovereign-cloud designation field (Commercial, GCC, GCC High, DoD), and that the designation matches the cloud the cycle is executing against.
- **Pre-conditions.** PRE-06 PASS.
- **Steps.**
  1. Pull the cloud designation field from the registration governance store for every in-scope agent.
  2. Cross-reference to the cycle's declared cloud.
  3. Output `sov-01-cloud-designation.csv` with classification: `DESIGNATED_MATCHES`, `DESIGNATED_MISMATCH`, `MISSING`.
- **Expected result.** All `DESIGNATED_MATCHES`.
- **Pass criteria.** `MISSING` and `DESIGNATED_MISMATCH` counts 0.
- **Failure remediation.** Populate missing designations from the tenant cloud at PRE-06; for mismatches, investigate and correct the governance record.
- **Evidence.** `sov-01-cloud-designation.csv`.
- **Cadence.** Zone 1 annual · Zone 2 semi-annual · Zone 3 quarterly.
- **Owner.** AI Governance Lead.
- **Zone applicability.** All zones.

#### 1.2-SOV-02 — Cross-cloud service principal detection

- **Objective.** Confirm that no service principal in the home tenant has a `appOwnerOrganizationId` that resolves to a tenant in a different sovereign cloud than the one declared, except for explicitly approved cross-cloud integrations.
- **Pre-conditions.** REG-01 PASS, PRE-06 PASS.
- **Steps.**
  1. For each home-tenant service principal, resolve `appOwnerOrganizationId` to its home tenant's cloud (where determinable from public metadata or the firm's cross-tenant collaboration register).
  2. Identify any SP whose home cloud does not match the declared cloud and is not on the approved cross-cloud list.
  3. Output `sov-02-cross-cloud.csv`.
- **Expected result.** Zero unapproved cross-cloud SPs.
- **Pass criteria.** Unapproved cross-cloud count 0 OR every row is in active TPRM review with restriction in place.
- **Failure remediation.** Restrict the SP via Conditional Access or remove the consent; engage TPRM for cross-cloud risk review; update the cross-cloud approved list if accepted.
- **Evidence.** `sov-02-cross-cloud.csv`, `sov-02-tprm-references.json`.
- **Cadence.** Zone 1 annual · Zone 2 semi-annual · Zone 3 quarterly.
- **Owner.** AI Governance Lead.
- **Zone applicability.** All zones; binding for tenants operating in GCC High or DoD.

#### 1.2-SOV-03 — Per-cloud parity gaps documented as compensating-control register

- **Objective.** Confirm that every Section 2 cell that the cycle observed as `Verify`, `Limited`, or `Preview` is paired with a documented compensating control in the cycle's evidence pack, and that the compensating control register is current.
- **Pre-conditions.** PRE-06 PASS, Section 2 reviewed at cycle start.
- **Steps.**
  1. Cross-reference Section 2 against the tenant Message Center observations.
  2. For each `Verify` / `Limited` / `Preview` cell that applies to a surface this cycle exercised, write a register entry containing: surface name, observed state, compensating control description, owning role, expiry date.
  3. Output `sov-03-compensating-controls.csv`.
- **Expected result.** Every applicable cell is paired with a current compensating control entry.
- **Pass criteria.** Coverage of applicable cells is 100%; no entry expired without renewal.
- **Failure remediation.** Author the missing entries with AI Governance Lead and Compliance Officer co-signature; renew expired entries.
- **Evidence.** `sov-03-compensating-controls.csv`.
- **Cadence.** Zone 1 annual · Zone 2 semi-annual · Zone 3 quarterly.
- **Owner.** AI Governance Lead.
- **Zone applicability.** All zones.

---

## Section 8 — Reconciliation evidence pack

Every cycle produces a single immutable evidence pack named `1.2-{cycleId}.zip` written to the WORM-protected evidence store referenced in PRE-07. The pack contains the artifacts named in each test, plus the cycle-level files below. The pack is the artifact handed to internal audit and external examiners; nothing referenced in Section 9 / Section 10 lives outside this pack.

### 8.1 Cycle-level files (always present)

| File | Purpose |
|---|---|
| `attestation.json` | Three-signature attestation chain (Section 1) including hash-chain fields |
| `manifest.sha256` | SHA-256 of every artifact in the pack |
| `cycle-summary.md` | Human-readable cycle summary: scope, cloud, namespace results, exception count, sign-off roster |
| `pre-01-registration-charter.json` ... `pre-07-evidence-store.json` | Pre-flight gate evidence |
| `baseline.json` | Copy of the baseline file in force (PRE-04) |
| `graph-permissions-matrix.json` | Copy of the matrix version evaluated against (PRE-01) |
| `surface-*.{json,csv}` | All registration-surface exports from REG-01 |
| `<test-id>-*` | Per-test artifacts as named in §7 |
| `exceptions-register.csv` | All exceptions in force during this cycle, with expiry dates |
| `remediation-actions.json` | All remediation actions taken during the cycle, with operator UPN, timestamp, and UAL reference |
| `cycle-log.txt` | Full chronological log of cycle execution including operator commands, timing, and any platform errors |

### 8.2 Pack assembly procedure

1. Author closes all per-test artifacts and computes SHA-256 for each; writes `manifest.sha256`.
2. Author authors `cycle-summary.md` from a template that names every test, its result (PASS / FAIL / EXCEPTION), and the relevant artifact file.
3. Author writes `attestation.json` with `manifestHash` populated; obtains Owner signature.
4. Sponsor reviews `cycle-summary.md`, the SPONSOR-* outputs, and the exceptions register; signs.
5. Compliance Officer reviews the entire pack including audit trail completeness in CONSENT-04 and consent-workflow integrity in CONSENT-01 / CONSENT-02; signs.
6. Once all three signatures are present, the pack is sealed by writing `chainHash` and applying the WORM retention label.
7. Pack is written to the immutable evidence store; an entry is appended to the cycle index.

### 8.3 Retention

The evidence pack is retained per the firm's records-retention schedule; for FSI organizations subject to SEC Rule 17a-4 / FINRA Rule 4511, the minimum is six years in WORM storage with a non-rewriteable, non-erasable format and an indexed retrieval capability. Compliance Officer is responsible for confirming the Purview retention label applied to the pack matches the firm's adopted retention schedule.

### 8.4 Pack integrity verification at audit time

When an internal auditor or external examiner retrieves a pack, the verification procedure is:
1. Recompute SHA-256 over each artifact in the pack and compare to `manifest.sha256`.
2. Recompute the SHA-256 of `manifest.sha256` and compare to `manifestHash` in `attestation.json`.
3. Recompute `chainHash` and compare to the recorded value.
4. Retrieve the prior cycle's pack and confirm `previousManifestHash` matches that pack's `manifestHash`.
5. Validate each signature's signing key against its issuance record at the cycle date; confirm the signing method satisfied the zone minimum at the cycle start.

A failure at any of steps 1–5 triggers the failure escalation matrix in Section 11.

---

## Section 9 — Quarterly examiner-style audit (randomized seeded sample)

In addition to the regular cycle cadence, AI Governance Lead and Internal Audit jointly execute a **quarterly examiner-style audit** designed to mirror the kind of sampling-based review that a FINRA, OCC, or SEC examiner would conduct. The sampling is reproducible: every cycle uses a documented seed so the same sample can be re-derived from the cycle ID and the in-scope agent set.

### 9.1 Sampling procedure

1. Determine the in-scope agent population for the quarter (typically all Zone 2 + Zone 3 agents in the declared cloud).
2. Compute the seed: `seed = SHA-256(cycleId || "quarterly-audit-sample" || tenantId)`.
3. Use the seed to drive a deterministic shuffle (e.g., Fisher–Yates with a SHA-256 PRNG); select the first **N** rows where N is the larger of 25 or 10% of the population (capped at 60 to keep the audit feasible).
4. For each sampled agent, perform a full registration trace from REG-01 through SOV-03, capturing source-of-truth evidence rather than relying on the cycle's pre-computed CSVs.
5. Independently re-derive the agent's owner, sponsor, permission set, credential type, CA coverage, and cloud designation from primary sources (Microsoft Graph, PPAC, Purview UAL).

### 9.2 Re-attestation expectation

For each sampled agent, the auditor re-issues a single-line attestation: "On {date}, I, {auditor UPN}, independently verified that agent {appId / displayName} has registration anchor {App ID + SP ID + Agent ID}, owner {UPN}, sponsor {UPN}, zone {Z}, cloud {C}, permission set hash {SHA-256 of normalized scope set}, credential type {type}, CA coverage {policy ID(s)}, and conforms to the firm's registration governance policy in force on the cycle date. Discrepancies, if any, are recorded in `quarterly-audit-{cycleId}-discrepancies.csv`."

### 9.3 Discrepancy handling

| Discrepancy class | Definition | Action |
|---|---|---|
| **Class A — Material registration gap** | Sampled agent is shadow, ownerless, has expired credential in use, or has unattested high-privilege scope grant | Cycle is reopened; affected control fails retroactively; a corrective cycle runs immediately; AI Governance Committee notified |
| **Class B — Documentation drift** | Governance store and primary source disagree on a metadata field (zone, sponsor, owner, cloud) but no security exposure | Governance store is reconciled; cycle is amended with corrected evidence and re-signed |
| **Class C — Stylistic / formatting** | Field-format inconsistency (e.g., UPN casing, ID-format) | Captured in continuous-improvement register (Section 12); no cycle reopen |

### 9.4 Quarterly audit evidence pack

The audit produces a self-contained pack `1.2-quarterly-audit-{cycleId}.zip` containing the sample list, the re-derivation outputs, the attestations, the discrepancy register, and a summary signed by AI Governance Lead and Internal Audit. The pack is stored in the same WORM evidence store as the cycle pack.

---

## Section 10 — Annual external attestation pack

Once per year, AI Governance Lead, Compliance Officer, and Internal Audit jointly assemble an **annual external attestation pack** intended to satisfy external supervisory or examiner requests under FINRA, SEC, OCC, Federal Reserve, or NYDFS supervisory programs. The pack is structured to be readable by an external party who has no prior context on the firm's tenant.

### 10.1 Pack contents

| Section | Contents |
|---|---|
| **Cover memo** | Scope, cloud(s), tenant identifier, attestation period, signatories, and a plain-language explanation of what the pack represents (and what it does not — see hedging notice) |
| **Policy basis** | The registration-governance charter (PRE-01) effective during the period, the Graph permissions matrix versions in force, the zone classification policy, and the records-retention policy |
| **Cycle index** | A table listing every cycle executed during the period, with cycleId, date, scope, cloud, sign-off roster, and PASS / FAIL summary |
| **Hash chain trace** | A computed verification of the hash chain across all cycles in the period, demonstrating no chain breaks |
| **Sampled cycle artifacts** | A representative sample of cycle packs (typically: first cycle of each quarter, plus any cycle that had a Critical or High finding) attached in full |
| **Quarterly audit packs** | All four quarterly audit packs from §9 |
| **Exception register** | Every exception in force during the period, with rationale, sign-off, expiry, and resolution status |
| **Incident references** | Cross-references to any AI Incident Response invocations during the period that touched the registration plane |
| **Regulatory mapping** | Per-regulation crosswalk: FINRA Rule 4511 / Notice 25-07, SEC 17a-4, SOX §§302/404, GLBA / FTC Safeguards 16 CFR §314.4(c), OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7), NYDFS 23 NYCRR Part 500.07 / 500.16, NIST AI RMF GOVERN 1.4 / 1.6, ISO/IEC 42001:2023 — for each, name the controls and tests in this playbook that support the requirement, with the explicit caveat that "supports" is not "guarantees" |
| **Attestation statement** | Three-signature statement from AI Governance Lead, Compliance Officer, and Internal Audit affirming the period's coverage, completeness, and limitations |
| **Limitations and exclusions** | A frank inventory of what the pack does NOT cover (surfaces not enumerated, controls outside scope, regulatory frameworks not mapped, sovereign clouds not exercised) |

### 10.2 External-readability requirements

The pack should be readable by a reviewer with: knowledge of US FSI supervisory frameworks; general knowledge of Microsoft 365 and Microsoft Entra; **no** prior knowledge of the firm's tenant, internal naming, or undocumented conventions. Every internal acronym is expanded on first use; every internal role is mapped to a canonical Microsoft role (or labeled as a firm-specific role with a one-line description).

### 10.3 Retention and availability

The annual pack is retained for the longer of (a) the records-retention period of the underlying evidence packs and (b) seven years; it is held in the WORM evidence store with an indexed retrieval capability suitable for examiner production within standard supervisory timelines.

---

## Section 11 — Failure escalation matrix

Every test in §7 has a declared severity floor. When a test FAILs, the escalation path below is invoked.

| Severity | Examples | Initial response | Escalation | Containment SLA | Cycle impact |
|---|---|---|---|---|---|
| **Critical** | REG-02 Z3 shadow agent; PERM-01 high-privilege over-scope; CRED-01 expired-secret-in-use; CONSENT-04 missing UAL trail for Z3 sensitive scope | Page on-call AI Governance Lead and Entra Application Admin; immediately quarantine the affected agent (block via CA, disable SP, or revoke credential as appropriate) | AI Governance Committee notified within 4 hours; AI Incident Response Playbook invoked if compromise suspected | Containment ≤ 4 hours; full remediation ≤ 5 business days | Cycle FAILs; corrective cycle runs immediately; current cycle is sealed with FAIL and a parallel remediation cycle is opened |
| **High** | OWN-01 ownerless app in Z2/Z3; PERM-02 orphan grant for previously-deleted sensitive scope; SPONSOR-04 over-SLA reassignment in Z3; CA-01 uncovered Z3 SP; SOV-02 unapproved cross-cloud SP | Notify Agent Owner, Agent Sponsor, AI Governance Lead within 1 business day | Compliance Officer review within 5 business days | Remediation ≤ 14 days | Cycle records FAIL on the test; cycle PASSes overall only if remediation is completed and re-tested within the cycle window |
| **Medium** | OWN-02 missing Backup Owner; CRED-03 over-cadence credential not yet at hard expiry; CONSENT-02 over-SLA queue item; CA-03 undocumented exclusion (non-Z3); SOV-03 missing compensating-control entry | Notify Agent Owner; create remediation ticket | AI Governance Lead at the cycle close | Remediation ≤ 30 days | Recorded as a finding; does not FAIL the cycle if remediation is on track |
| **Low** | Stylistic discrepancies; documentation drift class C; informational reconciliation deltas | Note in cycle log | Continuous-improvement review (Section 12) | None | No cycle impact |

Cross-references for invocation paths:
- AI Incident Response Playbook: [`../../incident-and-risk/ai-incident-response-playbook.md`](../../incident-and-risk/ai-incident-response-playbook.md)
- Control 3.6 Orphaned Agent Detection (forced decommission): [`../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- Control 1.7 Audit Logging (evidence-trail integrity): [`../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- Sponsorship Lifecycle Workflows (sponsor reassignment ceremony): [`./sponsorship-lifecycle-workflows.md`](./sponsorship-lifecycle-workflows.md)

---

## Section 12 — Continuous improvement

Each cycle contributes lessons-learned that feed the next cycle. The continuous-improvement loop is itself an evidence artifact.

### 12.1 Per-cycle retrospective

Within five business days of cycle close, AI Governance Lead facilitates a 30-minute retrospective with Sponsor, Owner, and Compliance Officer covering: what worked, what was harder than expected, what evidence proved insufficient at audit, what numerical thresholds need recalibration in PRE-04, what additional surfaces or namespaces should be added, and what test steps can be automated further. The retrospective output is `retro-{cycleId}.md` filed alongside the cycle pack.

### 12.2 Threshold and policy recalibration

Numerical thresholds (rotation windows, queue SLAs, coverage rates, sample sizes) are reviewed every two cycles against the trailing performance trend. A threshold change requires AI Governance Lead and Compliance Officer co-signature, is recorded in the policy register with effective date, and propagates to the next cycle's PRE-04 baseline.

### 12.3 Surface coverage review

Microsoft's agent surfaces are evolving. Once per quarter, AI Administrator and AI Governance Lead review the Microsoft Learn roadmap, the tenant Message Center, and the firm's third-party / partner-built agent intake to identify any new surface that should be added to REG-01. Adding a surface mid-period is allowed but requires re-baselining PRE-04 and noting the change in the next cycle's `cycle-summary.md`.

### 12.4 Automation maturity

This playbook is written to be operator-runnable end-to-end, but mature implementations automate large portions: Graph enumeration, hash-chain computation, manifest assembly, evidence-store writes, exception-register reconciliation, drift detection. Automation should never replace the three-signature attestation chain, the pre-flight gates, or the discrepancy adjudication; automation reduces fatigue but should not absorb judgment. Every automation change is itself controlled by the firm's change management and is recorded in the cycle log.

### 12.5 External feedback integration

Findings from internal audit walkthroughs, examiner observations, and peer-firm benchmarking that touch the registration plane are routed to AI Governance Lead for inclusion in the next cycle's playbook revision. Material revisions trigger a playbook version bump and are recorded in the change log at the bottom of this document.

---

## Section 13 — References

### 13.1 Microsoft Learn (verify currency at each cycle — content drifts; April 2026 was the verification baseline for this revision)

- Microsoft Entra application and service principal objects — overview and lifecycle
- Microsoft Entra App Registrations — `applications`, `servicePrincipals`, `oauth2PermissionGrants`, `appRoleAssignments` Graph reference
- Microsoft Entra Verified Publisher program
- Microsoft Entra Workload Identities — Conditional Access for workload identities, Identity Protection workload identity risk
- Microsoft Entra ID Governance — Lifecycle Workflows, access reviews
- Microsoft Entra Privileged Identity Management (PIM) — eligible vs. active assignment
- Microsoft Entra Agent ID — directory anchor for AI agents (preview / rollout state varies by cloud)
- Microsoft Entra federated identity credentials — workload identity federation
- Microsoft 365 admin center — Integrated apps overview, Copilot agents inventory, Agent Store governance
- Microsoft Copilot Studio — agent registration, identity model, and tenant administration
- Microsoft Power Platform admin center — agent enumeration, environment governance
- Microsoft Agent 365 admin center — unified agent registry, shadow-agent registry actions (Quarantine / Investigate / Register)
- Microsoft Purview Audit (UAL) — application lifecycle event schema
- Microsoft Purview retention — Locked retention labels and WORM behavior
- Microsoft Defender for Cloud Apps — App Governance for OAuth applications
- Microsoft Graph permissions reference — full scope catalog
- Microsoft sovereign-cloud documentation — Commercial, GCC, GCC High, DoD parity matrices and Message Center

### 13.2 Regulatory and supervisory references

- **FINRA Rule 4511** — Books and records general requirements
- **FINRA Rule 3110** — Supervision
- **FINRA Regulatory Notice 25-07** — Supervision of generative-AI applications
- **SEC Rule 17a-4(b)(4) and 17a-4(g)** — Records preservation; third-party recordkeeper requirements; non-rewriteable / non-erasable storage
- **SEC Rule 17a-3** — Records to be made by certain exchange members, brokers, and dealers
- **SOX §§302 and 404** — Internal control over financial reporting
- **GLBA Title V — 15 USC §§6801–6809** — Financial-institution safeguards
- **FTC Safeguards Rule** — 16 CFR §314.4(c) — written information security program; access controls; asset inventory
- **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** — Sound practices for model risk management
- **Federal Reserve Supervisory Letter Fed SR 26-2 (formerly SR 11-7)** — Guidance on model risk management (joint with OCC Bulletin 2026-13 (formerly OCC 2011-12))
- **CFTC Regulation 1.31** — Books and records
- **NYDFS 23 NYCRR Part 500** — Cybersecurity requirements for financial services companies (notably 500.07 access privileges, 500.16 incident response, 500.17 reporting)

### 13.3 Voluntary frameworks and standards

- **NIST AI RMF 1.0** — particularly **GOVERN 1.4** (governance and accountability roles) and **GOVERN 1.6** (inventory of AI systems)
- **NIST SP 800-53 Rev. 5** — IA-5 (authenticator management), AC-2 (account management), AC-6 (least privilege), AU-2 (event logging)
- **ISO/IEC 42001:2023** — AI management system requirements
- **ISO/IEC 27001:2022** — Information security management

### 13.4 Companion artifacts in this repository

- Control specification: [`../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- Sponsorship lifecycle workflows: [`./sponsorship-lifecycle-workflows.md`](./sponsorship-lifecycle-workflows.md)
- Portal walkthrough: [`./portal-walkthrough.md`](./portal-walkthrough.md)
- PowerShell setup: [`./powershell-setup.md`](./powershell-setup.md)
- Troubleshooting: [`./troubleshooting.md`](./troubleshooting.md)
- AI Incident Response Playbook: [`../../incident-and-risk/ai-incident-response-playbook.md`](../../incident-and-risk/ai-incident-response-playbook.md)

### 13.5 Validation commands

After modifying this playbook, run from the repository root:

```powershell
mkdocs build --strict
python scripts/verify_controls.py
```

A clean `mkdocs build --strict` confirms the cross-links resolve and the navigation is intact; a clean `verify_controls.py` confirms the control-side metadata still aligns. Both should be re-run after any cycle that adds or removes a cross-referenced playbook.

---

*Updated: April 2026 | Version: v1.6.2 | Maintained by: AI Governance Team*


---
