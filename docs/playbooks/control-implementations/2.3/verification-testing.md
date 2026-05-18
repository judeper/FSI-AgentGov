# Control 2.3: Change Management and Release Planning — Verification & Testing

> Verification and testing guidance for [Control 2.3: Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
>
> **Audience:** Power Platform Admins, AI Governance Lead, Compliance Officer, internal audit.

---

## Verification Checklist

| # | Step | Expected Result | Evidence |
|---|------|-----------------|----------|
| 1 | Pipelines exist for every Zone 2 / Zone 3 agent | Pipeline list in PPAC > Deployment > Pipelines includes the agent's solution | Screenshot or `pac admin pipeline list` export |
| 2 | Approval gates configured per zone | Power Automate flow on `OnApprovalStarted` (Zone 3) or native publish approval (Zone 2) is **On** | Flow definition export, JSON of approval action |
| 3 | Delegated deployment configured on Zone 3 Prod | Stage shows "Delegated deployment: On" with service principal identity distinct from any maker | PPAC stage screenshot |
| 4 | All recent changes documented | Each pipeline run in the last 90 days has a matching change record with approver, timestamp, and justification | Change-record export joined to deployment run IDs |
| 5 | Rollback procedure tested | At least one rollback drill completed in the last 90 days for Zone 3 | Drill report (see "Rollback Drills" below) |
| 6 | Audit trail complete and immutable | Pipeline deployment history retained per zone (1y / 6y); WORM or equivalent for Zone 3 | Storage policy + sample retrieval |
| 7 | Configuration snapshots present | Every Zone 2 / Zone 3 agent has a snapshot dated within the last change cycle | Source-control listing with hashes |
| 8 | Message Center monitoring active | Last delta query within 24 hours; relevant messages routed to change intake | Delta state file timestamp; intake-queue records |
| 9 | Out-of-solution components inventoried | Parallel inventory of external knowledge sources, hosted files, tenant-level connector configs | Inventory document |

---

## Rollback Drills

Rollback is the most often-failed step under examination. Drill at least once per quarter for Zone 3 agents.

### Drill scenario template

| Field | Example |
|-------|---------|
| **Drill ID** | DRILL-2026Q2-001 |
| **Agent** | `fsi_customer_support_agent` |
| **Trigger scenario** | Customer-impacting incorrect response after deployment of v2.4.0.0 |
| **Decision authority** | AI Governance Lead |
| **Target rollback version** | v2.3.5.12 (last known-good managed solution) |
| **RTO target** | 60 minutes (per Control 2.4) |
| **Actual RTO** | _to be filled_ |
| **Outcome** | _Pass / Fail with notes_ |

### Drill steps

1. Announce the drill to participants (do not include real customers).
2. Identify the last known-good managed solution version and confirm the artifact is retrievable from your storage location.
3. Verify the SHA-256 hash of the retrieved artifact against the evidence sidecar produced at export time.
4. Run the import to a non-production target first; confirm the prior version is restored.
5. Run the import to production through the pipeline using the documented rollback procedure.
6. Validate functional behavior matches the prior version.
7. Record actual elapsed time, any deviations from the runbook, and any gaps in evidence retention.
8. Open remediation items for any failed step.

---

## Rollback Triggers (Decision Reference)

| Trigger | Decision Authority | Action | Timeline |
|---------|--------------------|--------|----------|
| Critical functional failure | AI Governance Lead | Immediate rollback | < 1 hour |
| Performance degradation | Power Platform Admin | Assess, then decide | < 4 hours |
| User-reported issues (non-critical) | Agent Owner | Investigate, then decide | < 24 hours |
| Compliance concern | Compliance Officer | Hold, assess, decide | Immediate hold |
| Security vulnerability | Entra Security Admin | Immediate rollback | < 1 hour |
| Regulatory mandate | Compliance Officer / CCO | Coordinated rollback | Per regulator's window |

### Agent Rollback Decision Matrix

| Scenario | Decision Authority | Max Rollback Time | Approval Required |
|----------|--------------------|-------------------|-------------------|
| **Security vulnerability** | Entra Security Admin | 1 hour | Post-rollback notification to CISO |
| **Regulatory violation** | Compliance Officer | 4 hours | CCO notification |
| **Customer-impacting error** | AI Governance Lead | 2 hours | Post-rollback documentation |
| **Performance degradation** | Power Platform Admin | 4 hours | Manager approval |
| **Incorrect responses** | Designated Supervisor (FINRA 3110) | 24 hours | AI Governance Lead approval |
| **User complaints (non-critical)** | Agent Owner | 48 hours | Standard change process |

---

## Immediate Rollback Procedure (< 4 hours)

For critical issues requiring an immediate response. Authorized for the roles listed in the matrix above.

### 1. Suspend the Agent

- [ ] Open Microsoft Copilot Studio and select the affected agent
- [ ] Settings > Publish: set status to **Draft** (unpublishes from production channels)
- [ ] Confirm the suspension is reflected in the agent registry (Control 3.1)
- [ ] Record: time _____, operator _____

### 2. Notify Stakeholders

- [ ] Send notification to: Agent Owner, business stakeholders, IT Operations, Compliance (if scope warrants)
- [ ] Template: *"Agent [Name] has been suspended due to [brief reason]. Investigation in progress. ETA for next update: [time]."*
- [ ] Record: time _____, operator _____

### 3. Restore the Previous Version

**Path A — Solution rollback (preferred when the change was solution-deployed):**

- [ ] Retrieve the previous managed solution from artifact storage
- [ ] Verify SHA-256 hash against the evidence sidecar
- [ ] Import to production using the documented rollback pipeline (delegated deployment still applies)
- [ ] Republish the agent

**Path B — Configuration restore (when the change was in-place / non-solution):**

- [ ] Retrieve the previous configuration snapshot from source control
- [ ] Restore configuration components manually (system prompt, topics, connectors, settings)
- [ ] Validate in a non-production environment first
- [ ] Republish to the production channel

### 4. Validate the Rollback

- [ ] Test agent behavior matches the prior version's expected behavior
- [ ] Confirm no new issues introduced by the rollback itself
- [ ] Record: time _____, operator _____

### 5. Document and Notify

- [ ] Update the agent registry with the rollback event and version
- [ ] Send stakeholder notification: *"Agent [Name] restored to version [X.Y.Z]. Root cause analysis in progress."*
- [ ] Open an incident record (link to Control 2.4)
- [ ] Schedule a post-incident review within 5 business days

---

## Planned Rollback (> 4 hours)

For non-urgent rollbacks that follow the standard change process:

1. Open a rollback change request
2. Identify the target version from snapshot history
3. Test the rollback in a non-production environment
4. Schedule the rollback during an approved change window
5. Execute through the standard pipeline (with approvals)
6. Validate using standard test procedures
7. Document with root cause and lessons learned

---

## Solution Backup Strategy

| Zone | Backup Frequency | Retention | Storage |
|------|------------------|-----------|---------|
| Zone 1 | On change | 30 days | Maker OneDrive or team SharePoint |
| Zone 2 | Before deployment | 90 days | SharePoint with versioning + Git |
| Zone 3 | Before deployment + daily | 6 years (per SEC 17a-4) | Immutable storage (WORM-compliant blob, M365 Backup, or equivalent) |

---

## Agent Version History Requirements

Maintain version history for regulatory examination and incident investigation.

| Zone | History Retention | Detail Level | Storage Location |
|------|-------------------|--------------|------------------|
| Zone 1 | 90 days | Summary | Agent registry |
| Zone 2 | 1 year | Standard | SharePoint + Git |
| Zone 3 | 6 years (SEC 17a-4) | Comprehensive | Immutable storage |

### Version History Record Schema

| Field | Description | Required |
|-------|-------------|----------|
| Version Number | 4-part semantic version (`Major.Minor.Build.Revision`) | Yes |
| Effective Date | When the version went live in the target environment | Yes |
| Change Summary | Brief description of what changed | Yes |
| Change Category | Prompt / Topic / Knowledge / Connector / Action / Setting | Yes |
| Change Request ID | Link to change record | Zone 2-3 |
| Approved By | Approver name and timestamp | Zone 2-3 |
| Snapshot Reference | Link to configuration snapshot with hash | Zone 2-3 |
| Test Results | Link to test evidence (Control 2.5) | Zone 2-3 |
| Pipeline Run ID | PPAC deployment run identifier | Zone 2-3 |
| Rollback Status | Never / Rolled back on [date] with reason | Yes |

---

## Pre / During / Post Change Checklists

### Before any change

- [ ] Current version documented in agent registry
- [ ] Configuration snapshot captured and committed to source control with hash
- [ ] Rollback plan documented (target version, runbook reference)
- [ ] Change request approved per zone matrix
- [ ] Solution Checker run (Zone 2-3); critical and high findings addressed

### During the change

- [ ] Changes made in the development environment only
- [ ] Testing completed per zone (Control 2.5)
- [ ] New version number assigned per the convention
- [ ] Pipeline run initiated; approval gates satisfied
- [ ] Delegated-deployment identity used on Zone 3 Prod

### After the change

- [ ] Production deployment verified (functional smoke test)
- [ ] Version history updated
- [ ] Stakeholders notified
- [ ] Monitoring in place (24-hour heightened observation for Zone 3)
- [ ] Post-deployment validation completed (24-48 hours)
- [ ] Change record closed

### Rollback readiness (continuous)

- [ ] Previous snapshot accessible
- [ ] Rollback procedure current (reviewed quarterly)
- [ ] Rollback authority contacts current
- [ ] Communication templates current

---

## A/B Testing for Zone 3 Agent Updates

For Zone 3 agents or significant changes, A/B testing reduces blast radius. Where the platform supports traffic splitting, configure metrics that correspond to FSI risk indicators (regulator-relevant errors, supervisor-flagged responses, escalation rates).

```yaml
# A/B test configuration template
ab_testing:
  enabled: true
  test_duration_days: 7
  traffic_split:
    control: 80%    # Current production version
    treatment: 20%  # New version
  success_metrics:
    - metric: resolution_rate
      maximum_degradation_percent: 5
    - metric: csat_score
      maximum_degradation_points: 0.2
    - metric: error_rate
      maximum_degradation_percent: 2
    - metric: supervisor_flagged_rate
      maximum_degradation_percent: 0   # No tolerance for increase
  auto_rollback_triggers:
    - condition: "error_rate > control_error_rate + 5%"
      action: immediate_rollback
    - condition: "supervisor_flagged_rate > control + 0%"
      action: pause_and_review
  graduation_criteria:
    - All success metrics met
    - No critical errors
    - Stakeholder sign-off
    - Compliance Officer review of supervisor-flagged sample
```

> **FSI note:** For agents in regulated workflows (broker-dealer supervision, lending decisioning, AML triage), confirm with Compliance that A/B testing on production traffic is permissible under your supervisory framework. Some firms require a synthetic-traffic shadow deployment instead.

---

## Documentation Requirements

### Change Record Contents

| Field | Description | Required |
|-------|-------------|----------|
| Change ID | Unique identifier (ties to ticketing system) | Yes |
| Description | What is being changed | Yes |
| Justification | Why the change is needed | Yes |
| Risk assessment | Potential impact (model risk if applicable) | Zone 2-3 |
| Test results | Validation evidence (Control 2.5) | Zone 2-3 |
| Approvals | Who approved with timestamps | Yes |
| Pipeline run ID | PPAC deployment run identifier | Zone 2-3 |
| Deployment date | When deployed | Yes |
| Validation | Post-deployment confirmation outcome | Yes |
| Rollback status | Whether rolled back, when, and why | Yes |

### Audit Trail

Maintain records for:

- Change requests and approvals
- Pipeline deployment runs (PPAC export)
- Power Automate approval flow runs (export from Power Automate run history)
- Delegated-deployment service-principal sign-in events (Entra audit logs)
- Test results (Control 2.5)
- Rollback events
- Post-deployment validation
- Message Center events that drove changes

---

## Evidence Package for Audit

When audit or examination requests evidence of Control 2.3 effectiveness, prepare:

1. **Pipeline configuration export** — list of pipelines, stages, target environments, delegated-deployment identities
2. **Approval flow definition** — JSON export of the Power Automate flow on `OnApprovalStarted`
3. **Sample of deployment runs** (typically 25 random runs from the audit period) with linked change records, approvals, and post-deployment validation
4. **Rollback drill reports** — at least the most recent quarter's drill
5. **Configuration snapshots** for sampled agents with SHA-256 hashes
6. **Audit log extracts** showing service-principal identity executing Prod deployments
7. **Message Center triage log** showing platform-change events routed into change intake
8. **Retention policy documentation** for change records

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — PPAC and Copilot Studio configuration
- [PowerShell Setup](powershell-setup.md) — Automation scripts
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
