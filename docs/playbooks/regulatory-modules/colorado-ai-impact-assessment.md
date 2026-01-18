# Template: Colorado AI Act (SB24-205) Impact Assessment — Deployer

**Purpose:** Provide a repeatable “impact assessment” document for any AI system that is or may be a **high-risk artificial intelligence system** under Colorado law.  
**Who uses this:** The **deployer** (a person doing business in Colorado that deploys a high-risk AI system). [page:11]  
**Effective trigger date:** Colorado’s bill summary states deployer obligations apply “on and after **February 1, 2026**,” including completing an impact assessment and annual review. [page:11]  
**FSI relevance:** The statute defines “consequential decision” to include decisions affecting “a financial or lending service,” and defines “high-risk AI system” as one that makes or is a substantial factor in making a consequential decision. [page:12]

> Important: This is a governance template, not legal advice. Legal counsel should confirm applicability to your specific footprint and use case.

---

## 1) System identification

- **System name:**
- **System ID / version:**
- **Owner (business):**
- **Owner (technical):**
- **Deployer entity:** (legal entity doing business in Colorado)
- **Vendor/developer (if third-party):**
- **Deployment date:**
- **Last assessment date:**
- **Next assessment date:** (at least annually) [page:11]

---

## 2) Applicability determination (is this “high-risk” under SB24-205?)

### 2.1 Is it an “AI system” under the statute?
Colorado defines an “artificial intelligence system” broadly as a machine-based system that infers how to generate outputs (content/decisions/predictions/recommendations) that can influence environments. [page:12]

- **Yes / No / Uncertain**
- **Rationale:**

### 2.2 Does it make or substantially factor into a “consequential decision”?
Colorado defines “consequential decision” as having a material legal or similarly significant effect on provision/denial/cost/terms of categories including “a financial or lending service.” [page:12]

- **Yes / No / Uncertain**
- **Decision type(s):** (credit underwriting, pricing, fraud blocking, account closure, etc.)
- **Rationale:**

### 2.3 High-risk conclusion
Colorado defines a “high-risk AI system” as one that, when deployed, makes or is a substantial factor in making a consequential decision. [page:12]

- **High-risk: Yes / No / Uncertain**
- **If “uncertain,” escalation:** route to Legal/Compliance for determination.

---

## 3) Purpose, intended use cases, and deployment context

Colorado requires the impact assessment to include a statement disclosing purpose, intended use cases, deployment context, and benefits. [page:11]

- **Purpose (plain language):**
- **Intended use cases:**
- **Deployment context:** (channel, product line, customer segment, geography)
- **Benefits:** (risk reduction, speed, accuracy, consumer benefit)

---

## 4) Data categories and outputs

Colorado requires describing categories of data processed as inputs and outputs produced. [page:11]

### 4.1 Inputs (data categories)
- Personal data categories:
- Non-personal data categories:
- Sensitive data categories:
- Data sources (internal/external):
- Data quality caveats:

### 4.2 Outputs
- Output types: content / score / recommendation / decision / prediction [page:12]
- How outputs are used:
- Is output used directly or as “substantial factor” in a human decision? [page:12]

---

## 5) Known/foreseeable risks of algorithmic discrimination + mitigations

Colorado requires analysis of known or reasonably foreseeable risks of algorithmic discrimination and steps taken to mitigate. [page:11]  
Colorado defines “algorithmic discrimination” as unlawful differential treatment or impact disadvantaging a protected class under state/federal law. [page:12]

### 5.1 Risk inventory
- Potential disparate impact vectors:
- Protected class considerations:
- Proxy variables risks:
- Accessibility/limited English proficiency risks (if applicable):

### 5.2 Mitigations (pre-deployment)
- Data governance measures:
- Feature review / proxy checks:
- Bias testing approach and results summary:
- Human oversight controls:
- Threshold tuning / guardrails:
- Red-team/adversarial testing summary:

### 5.3 Mitigations (post-deployment monitoring)
- Drift monitoring:
- Outcome monitoring:
- Complaint feedback loop:
- Escalation and incident response:

---

## 6) Performance metrics and known limitations

Colorado requires listing metrics used to evaluate performance and known limitations. [page:11]

- **Primary metrics:** (accuracy, FPR/FNR, calibration, etc.)
- **Fairness metrics:** (selection rate ratios, error rate parity, etc.)
- **Known limitations:** (data sparsity, model scope, false positive patterns)
- **Operational constraints:** (time windows, required human review)

---

## 7) Transparency measures and consumer notice readiness

Colorado requires describing transparency measures, including measures to disclose when the high-risk AI system is in use. [page:11]  
The statute requires notice to the consumer that a high-risk AI system is used to make or be a substantial factor in making a consequential decision, and includes requirements for disclosures and adverse decision information. [page:11]

- **Disclosure approach:** (where/how consumer is notified)
- **Plain-language description:** (one paragraph)
- **Contact information for deployer:** (support channel)
- **Adverse decision explanation readiness:** principal reasons, degree/manner AI contributed, type and sources of data (prepare process). [page:11]

---

## 8) Post-deployment monitoring and user safeguards

Colorado requires describing post-deployment monitoring and safeguards, including oversight and learning process established by deployer. [page:11]

- Monitoring owners:
- Monitoring cadence:
- Guardrails (e.g., no-auto-execute, review thresholds):
- Human review workflow:
- Corrective action (CAPA) workflow:

---

## 9) Annual review requirement

The bill summary states deployers must annually review each deployed high-risk system to ensure it is not causing algorithmic discrimination. [page:11]

- **Annual review plan:** (date, sampling, metrics, sign-off)
- **Evidence artifacts to retain:** (report, approvals, remediation tickets)

---

## 10) Recordkeeping

Colorado requires maintaining the most recent impact assessment and related records and prior assessments for at least 3 years following final deployment (per statutory text). [page:12]

- **Retention period:** (>= 3 years after final deployment)
- **Storage location:** (GRC repository / SharePoint restricted site)
- **Access controls:** (who can access)
- **Legal privilege handling:** (if applicable)

---

## 11) Exceptions / exemptions check (FSI note)

The statutory text includes a “full compliance” concept for certain regulated banks/credit unions subject to prudential regulator examination under qualifying guidance/regulations. [page:12]  
Even if relying on that concept, keep this impact assessment as evidence of “reasonable care” and alignment to a recognized AI RMF.

- **Prudential regulator exam framework relied upon:** (if any)
- **Rationale and legal sign-off:**

---

## 12) Approvals

- **Prepared by:**
- **Reviewed by (Data Science):**
- **Reviewed by (Compliance/Risk):**
- **Reviewed by (Legal):**
- **Approved by (Executive owner):**
- **Approval date:**
- **Version:**