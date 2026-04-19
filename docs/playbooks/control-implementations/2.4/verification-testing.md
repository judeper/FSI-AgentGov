# Control 2.4: Business Continuity and Disaster Recovery — Verification & Testing

> Verification, exercise scenarios, and evidence collection for [Control 2.4: Business Continuity and Disaster Recovery](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Audience

M365 administrators, AI Governance Leads, and Compliance Officers in US financial services who need to evidence that customer-side BC/DR controls for Copilot Studio agents operate effectively. Evidence produced by these tests supports FFIEC BCM examination, FINRA Rule 4370 review, SEC 17a-4 reconstruction obligations, SOX 404 ITGC testing, and OCC Heightened Standards (Appendix D) independent assurance.

---

## Pre-Verification Prerequisites

| Item | Source |
|------|--------|
| Approved BIA listing every in-scope agent with tier, RTO, RPO, dependencies | AI Governance Lead |
| DR runbook (current version, Compliance-approved) | [Portal Walkthrough §7](portal-walkthrough.md#part-7-author-the-dr-runbook) |
| Provisioned secondary-region environment with parity policies | [Portal Walkthrough §2](portal-walkthrough.md#part-2-provision-and-harden-the-secondary-region-environment) |
| Customer-managed solution exports landing in immutable storage | [PowerShell Setup §4](powershell-setup.md#4-customer-managed-solution-export-to-immutable-storage) |
| Service Health alerts routed to DR distribution list | [Portal Walkthrough §6](portal-walkthrough.md#part-6-subscribe-to-service-health-and-message-center-alerts) |
| Independent observer assigned (Compliance or Internal Audit) for Zone 3 exercises | OCC Appendix D requires independent assurance |

---

## Verification Checklist

### Backup verification

- [ ] PPAC shows continuous Dataverse system backups for the past 28 days (production) or 7 days (sandbox) per environment
- [ ] At least one manual backup created in the past change window with a labeled, traceable change ID
- [ ] Customer-managed solution export job has run within the cadence required by the highest-tier agent's RPO
- [ ] Solution exports are landing in immutable Azure Blob (or equivalent WORM-capable) storage with a time-based retention policy that meets SEC 17a-4
- [ ] SHA-256 hash sidecars exist alongside every export for independent integrity verification

### DR environment verification

- [ ] Secondary-region environment exists for every Zone 3 production environment, in a different Azure region within the same regulatory geography
- [ ] DR environment is enabled as a Managed Environment with parity DLP policies
- [ ] Latest managed solution(s) imported in DR; version matches the most recent production release
- [ ] Application users present in DR for every Entra Agent ID / service principal used by in-scope agents
- [ ] Conditional Access targeting DR environment URLs is documented and tested
- [ ] Connection references can be re-bound; reference inventory documented

### Identity continuity verification

- [ ] App registrations and Entra Agent IDs used by in-scope agents have federated credentials present and not expiring within 30 days
- [ ] Client secrets (where used) are stored in a region-paired Key Vault with rotation owner documented
- [ ] Smoke test (`WhoAmI`) succeeds against DR environment using production-equivalent identity

### Runbook verification

- [ ] Runbook is published, version-controlled, and approved by Compliance within the past 12 months
- [ ] Declaration authority list and contact details are current (no departed personnel)
- [ ] Failover and failback sequences include explicit time targets aligned to BIA RTO
- [ ] Communication templates exist for stakeholder, regulator, and customer notifications

### Exercise verification

- [ ] Most recent Zone 3 exercise occurred within the past 90 days; Zone 2 within the past 12 months
- [ ] Exercise documentation includes scenario, scope, participants, observer, and timestamps for each phase
- [ ] Measured RTO and RPO recorded against targets
- [ ] Gaps tracked to closure with owner and date
- [ ] Compliance Officer sign-off recorded
- [ ] Exercise evidence is retained for ≥ 6 years in the firm's regulatory recordkeeping system

---

## Zone-Specific BC/DR Targets

These are starting framework targets; firms ratify the actual numbers in the BIA against board-approved disruption tolerances.

| Configuration | Zone 1 | Zone 2 | Zone 3 |
|---------------|--------|--------|--------|
| **RTO target (indicative)** | ≤ 72 hours | ≤ 4 hours | ≤ 1 hour |
| **RPO target (indicative)** | ≤ 24 hours | ≤ 1 hour | ≤ 15 minutes |
| **Customer-managed export cadence** | None required | Daily (minimum) | Aligned to RPO (typically continuous via Synapse Link) |
| **Long-term immutable retention** | Not required | ≥ 90 days | ≥ 6 years (SEC 17a-4) |
| **Secondary-region environment** | Not required | Warm standby recommended | Hot or warm standby required |
| **Documented exercise cadence** | Not required | Annual | Quarterly (mix of tabletop and live) |
| **Independent assurance** | Not required | Internal review | Annual independent review (OCC Appendix D) |

---

## Backup Retention Layers

| Layer | Retention | Purpose |
|-------|-----------|---------|
| Microsoft system backups (Dataverse production) | 28 days | In-region operational recovery |
| Microsoft system backups (Dataverse sandbox) | 7 days | In-region operational recovery |
| Customer manual backups (Power Platform) | Per published Power Platform policy — verify before relying on a window | Pre-change rollback |
| Local staging exports | ≤ 14 days | Short-term staging only — not regulatory evidence |
| Immutable Azure Blob exports | ≥ 6 years (or longest applicable retention) | SEC 17a-4 reconstruction; FINRA 4511 books and records |

---

## DR Exercise Scenarios

Each scenario should be run at least once per Zone 3 quarterly cycle. Mix tabletop and live execution; Microsoft does not need to be notified for a customer-side exercise that does not impersonate a Microsoft outage to other tenants.

### Scenario 1 — Regional outage simulation (live failover)

**Objective:** Validate ability to fail Tier 1 agents over to the DR environment within RTO.

**Pre-conditions:**

- DR environment refreshed within the past 24 hours
- Identity continuity check passed within the past 7 days (see [PowerShell Setup §5](powershell-setup.md#5-validate-agent-identity-continuity-in-the-dr-environment))
- Business stakeholders notified
- Independent observer present

**Procedure:**

| Phase | Activity | Target | Owner |
|-------|----------|--------|-------|
| 1 | Declare exercise; primary "marked unavailable" in change-control terms | 5 min | On-call manager |
| 2 | Validate DR environment health (smoke test) | 10 min | Power Platform Admin |
| 3 | Re-bind connection references and refresh OAuth tokens in DR | 15 min | Environment Admin |
| 4 | Cut traffic / channel publish to DR endpoint | 10 min | Power Platform Admin |
| 5 | Functional smoke test on Tier 1 agent | 15 min | Business owner |
| 6 | Notify stakeholders, log declaration time | 5 min | AI Governance Lead |
| **Total** | **Failover complete** | **≤ 60 min** | |

**Pass criteria:**

- All Tier 1 agents respond in DR within RTO
- No data loss exceeding documented RPO
- All runbook steps executed without undocumented deviation
- Identity, DLP, and Conditional Access enforced in DR

### Scenario 2 — Single-agent restore from backup (live)

**Objective:** Validate ability to restore a single agent from a customer-managed solution export.

**Procedure:**

1. Select a non-production agent
2. Export current state as baseline (managed solution + Dataverse data)
3. Make a destructive change (delete solution components)
4. Restore from the most recent managed solution export
5. Re-bind connection references
6. Verify functional parity against baseline

**Pass criteria:**

- Agent restored within 30 minutes
- All exportable components recovered
- Components excluded from solution export (knowledge sources, etc.) recovered via documented secondary procedure
- Test conversation produces expected response

### Scenario 3 — Tenant-wide auth failure (tabletop)

**Objective:** Validate runbook coverage for an Entra outage affecting credential acquisition.

**Procedure:**

1. Walk through declaration criteria for an identity-plane outage
2. Confirm break-glass identities and out-of-band communication channels
3. Identify which agents become unrecoverable until identity is restored
4. Document escalation and customer-notification thresholds

**Pass criteria:** Runbook explicitly addresses identity-plane scenarios; participants can locate break-glass procedures within 5 minutes.

### Scenario 4 — Malicious deletion of agent (live, sandbox-only)

**Objective:** Validate ability to recover from accidental or malicious deletion of an agent solution.

**Procedure:**

1. In a sandbox environment, delete a non-production agent's solution
2. Restore from immutable Azure Blob using the latest export and SHA-256 verification
3. Validate component coverage and conduct functional test

**Pass criteria:** Recovery completes within tier RTO; integrity hash matches export sidecar.

### Scenario 5 — Failback to primary

**Objective:** Validate clean return to the primary environment after the simulated outage.

**Procedure:**

1. Operate in DR for the documented exercise window (minimum 2 hours)
2. Inventory configuration and data changes made in DR
3. Export and import changes back to primary; reconcile conflicts
4. Cut traffic back to primary; place DR back into warm-standby state
5. Verify primary functionality

**Pass criteria:** No data loss during failback; no unresolved conflicts; users experience no functional regression.

---

## DR Exercise Documentation Template

Use this template for every exercise; retain ≥ 6 years.

### Exercise summary

| Field | Value |
|-------|-------|
| Exercise date | |
| Exercise type | Tabletop / Partial / Full |
| Scenario | (e.g., Scenario 1 — Regional outage simulation) |
| Scope (agents, environments) | |
| Participants | |
| Independent observer | |
| Runbook version exercised | |

### Measured outcomes

| Metric | Target | Actual | Result |
|--------|--------|--------|--------|
| Tier 1 RTO | ≤ 1 hr | | Pass / Fail |
| Tier 2 RTO | ≤ 4 hr | | Pass / Fail |
| RPO (data loss measured) | ≤ 15 min | | Pass / Fail |
| Component coverage (% of solution restored) | 100% | | Pass / Fail |
| Identity continuity (WhoAmI in DR) | Pass | | Pass / Fail |
| Runbook executed without deviation | Yes | | Pass / Fail |

### Issues and corrective actions

| Issue | Severity | Root cause | Corrective action | Owner | Target close date | Status |
|-------|----------|------------|-------------------|-------|-------------------|--------|
| | High / Med / Low | | | | | |

### Lessons learned

(narrative)

### Sign-off

| Role | Name | Date |
|------|------|------|
| AI Governance Lead | | |
| Power Platform Admin | | |
| Compliance Officer | | |
| Independent observer | | |

---

## FSI Use Case — Trading-Floor Surveillance Agent

A surveillance agent that supports supervisory review under FINRA Rule 3110 is typically Tier 1 or Tier 2. Treatment:

- **Recordkeeping:** Conversation transcripts and supervisory dispositions are books and records; export to immutable storage with SEC 17a-4 retention
- **Architecture:** Primary in East US, warm standby in West US; daily Synapse Link replication of supervisory tables to ADLS Gen2
- **RTO / RPO:** ≤ 1 hr / ≤ 15 min, ratified by the BCP committee
- **Exercise cadence:** Quarterly live failover (one full, three tabletop), with Internal Audit observation for the annual full exercise
- **Examiner artifacts:** BIA entry, runbook, last four exercise reports with measured outcomes, immutability policy on the export Blob, agent identity rotation log

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — Step-by-step portal configuration
- [PowerShell Setup](powershell-setup.md) — Automation scripts
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: April 2026 | Version: v1.4.0*
