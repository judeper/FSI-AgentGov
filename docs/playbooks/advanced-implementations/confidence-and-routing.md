# Spec: Confidence / Uncertainty Capture and Routing

**Purpose:** Ensure agent outputs are handled according to risk by capturing **confidence/uncertainty** and enforcing routing rules (review, escalation, block) based on zone, action type, and confidence.  
**Applies to:** Zone 3 (required), Zone 2 (recommended), Zone 1 (baseline banding recommended).  
**Regulatory driver:** FINRA highlights that AI agents may perform multi-step reasoning that reduces transparency/explainability and may act autonomously beyond authority, reinforcing the need for governance, oversight, and guardrails. [web:87]  
**Evidence driver:** Microsoft Purview Copilot audit records include structured interaction metadata and can include message-level flags like `JailbreakDetected` (prompt jailbreak attempt) and resource-level `XPIADetected` (cross prompt injection attack detection) that are useful “uncertainty/risk signals” for routing. [web:118]

---

## 1) Definitions

- **Confidence:** A measure of how likely the agent’s output is correct/appropriate for the request (not “model probability” unless the model provides it).
- **Uncertainty:** Evidence that the agent may be wrong, missing required information, or operating outside its designed capability.
- **Routing:** The process that determines whether the output is (a) allowed to proceed, (b) requires human review, (c) is escalated, or (d) is blocked.

---

## 2) Confidence representation (choose one)

### Option A (recommended): 3-band confidence
- **High / Medium / Low**
- Works across different agent implementations and avoids false precision.

### Option B: Numeric score
- `confidence_score` in [0.0, 1.0]
- Only if consistently derivable and calibrated.

> For regulated governance, consistency and auditability matter more than “perfect” confidence math.

---

## 3) Inputs to compute confidence (minimum viable)

Confidence should be computed from a **policy-driven heuristic** (even if the model doesn’t provide a score), using signals like:

### C1) Source support
- Number of distinct sources used
- Presence of authoritative internal sources vs “no source”
- Conflicts between sources

### C2) Policy and boundary signals
- Any DLP/policy blocks (PolicyDetails present)
- Any restricted label encountered in `AccessedResources.SensitivityLabelId` [web:118]

### C3) Attack/abuse signals (risk, not “confidence”)
- Any prompt message flagged `JailbreakDetected == true` [web:118]
- Any resource flagged `XPIADetected == true` [web:118]

### C4) Task type + criticality
- Informational vs recommendation vs execute
- Customer-facing vs internal
- Consequential decision context

---

## 4) Routing policy (required)

### 4.1 Routing matrix

| Zone | Decision type | Confidence | Default route | Notes |
|---|---|---|---|---|
| Zone 1 | Inform | High/Med/Low | Allow | Log band + key metadata |
| Zone 1 | Recommend/Execute | Any | Block or review | Zone 1 should not execute |
| Zone 2 | Inform/Recommend | High | Allow | With monitoring |
| Zone 2 | Inform/Recommend | Medium | Review optional | Reviewer sampling recommended |
| Zone 2 | Inform/Recommend | Low | Mandatory review | Create ticket/case |
| Zone 2 | Execute | Any | Mandatory review | Execute requires approval |
| Zone 3 | Inform/Recommend | High | Allow | Monitor + log |
| Zone 3 | Inform/Recommend | Medium | Review required | Default to review in regulated |
| Zone 3 | Inform/Recommend | Low | Escalate | Block auto actions |
| Zone 3 | Execute | High only | Allow only if AAM allows | Must still pass hard limits |
| Zone 3 | Execute | Medium/Low | Block + escalate | No auto-exec |

### 4.2 Mandatory escalation triggers (override confidence)
Regardless of confidence band, escalate/block if:
- Prohibited action attempted (AAM violation)
- Restricted label boundary crossed
- `JailbreakDetected == true` for prompt message [web:118]
- `XPIADetected == true` for accessed resource [web:118]
- Scope drift detected (connector/site drift)
- Missing required sources for a regulated recommendation (“unsupported claim”)

---

## 5) Logging requirements (tie to Gap 2 decision logs)

For each material interaction:
- `confidence_band` (required)
- `confidence_factors` (optional list, recommended)
- `routing_outcome` (allow/review/escalate/block)
- `routing_reason_codes` (required if not “allow”)
- `review_required` boolean + reviewer outcome if applicable

Also log whether:
- jailbreak signal observed [web:118]
- XPIA signal observed [web:118]

---

## 6) Human review requirements

### Review checklist (minimum)
- Is the output supported by sources?
- Does it comply with communications/disclosure rules if customer-facing?
- Does it contain any sensitive data that should be masked?
- Is the action within authorized scope?

### Reviewer actions
- Approve as-is
- Modify output
- Reject output
- Escalate to compliance/security

---

## 7) Calibration and QA (monthly/quarterly)

- Sample Low/Medium/High outputs and measure:
  - approval rate
  - correction rate
  - false-negative rate (High confidence but wrong)
- Adjust confidence heuristics and thresholds
- Record changes via change management

FINRA underscores governance/testing/monitoring expectations for GenAI use and the need for supervisory processes under FINRA Rule 3110. [web:86]

---

## 8) “Done” criteria

- Confidence bands recorded for Zone 2/3 agents in decision logs.
- Routing matrix enforced (no bypass without logged override).
- Mandatory escalation triggers implemented and tested.
- Monthly calibration report exists and is reviewed by governance stakeholders.

---

*FSI Agent Governance Framework v1.2 - January 2026*