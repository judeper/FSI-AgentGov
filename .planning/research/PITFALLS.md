# Pitfalls Research: FSI Agent Governance

**Domain:** Financial services AI agent governance (Microsoft 365 Copilot Studio/Power Platform)
**Researched:** February 2, 2026
**Confidence:** HIGH (regulatory sources), MEDIUM (platform issues from docs/community)

## Summary

Research identifies 5 critical regulatory pitfalls and 8 major technical pitfalls in FSI agent governance for 2025-2026:

- **Retention period misclassification** - Agent logs as communications (3 years) vs financial records (6 years)
- **February 2026 pipeline deadline** - Automatic Managed Environment enforcement requires premium licensing
- **PAYG licensing misconception** - Pay-as-you-go does NOT satisfy Managed Environment requirements for active users
- **Service Principal security group bypass** - SPs access ANY environment regardless of Security Groups
- **Recordkeeping completeness gap** - Audit logs provide metadata only; full content requires eDiscovery/DSPM

---

## Regulatory Pitfalls

### CRITICAL: Retention Period Misclassification

**What goes wrong:** Organizations apply 6-year retention to ALL agent records based on SEC 17a-4(a), when most agent conversation logs qualify as "communications" under 17a-4(b)(4) requiring only 3 years.

**Why it happens:**
- Broker-dealers default to longest retention period to be "safe"
- Confusion between communications vs. financial/accounting records
- Documentation doesn't distinguish record types

**Consequences:**
- Unnecessary storage costs (3x storage for 3 extra years)
- Incorrect retention policy configuration
- Potential compliance gaps if policies don't match actual requirements

**Prevention:**
- Implement retention period matrix from framework (v1.2.30 update)
- Classify agent logs as communications (SEC 17a-4(b)(4)) unless they generate/modify financial records
- Use separate retention labels: `FSI-Communications-3Y` vs `FSI-Financial-6Y`

**Detection:**
- Review retention policy names in Purview
- Check CopilotInteraction audit log retention settings
- Verify storage tier costs align with record type classifications

**Which controls address this:** 1.7, 1.9, 2.13, 4.3

**Phase recommendation:** Phase 1 (Foundation) - Must establish retention classification before agents go live

---

### CRITICAL: FINRA Supervision Gaps for Autonomous Agents

**What goes wrong:** Firms deploy autonomous AI agents without establishing written supervisory procedures (WSPs), human-in-the-loop (HITL) triggers, or annual testing protocols required under FINRA Rules 3110 and 3120.

**Why it happens:**
- FINRA Notice 24-09 (June 2024) provided general guidance but many firms missed application to agentic AI
- FINRA 2026 Annual Regulatory Oversight Report (December 2025) clarified autonomous agent supervision requirements AFTER many deployments
- Firms treat AI agents as "technology tools" rather than systems requiring supervision

**Consequences:**
- FINRA examination findings and enforcement actions
- Agent autonomy without documented oversight creates regulatory exposure
- Inability to demonstrate supervisory procedures during examinations

**Prevention:**
- Document WSPs specifically for AI agent supervision per Rule 3110
- Implement HITL triggers for Zone 2/3 agents (see HITL triggers playbook)
- Establish annual testing program per Rule 3120 (WSP adherence, HITL functionality, escalation procedures)
- Classify agents by autonomy level (Assisted, Augmented, Automated, Autonomous) with corresponding supervision intensity

**Detection:**
- Check if WSPs mention "AI agents," "Copilot Studio," or "autonomous systems"
- Verify HITL trigger configuration exists in production agents
- Confirm Rule 3120 testing was performed in last 12 months

**Which controls address this:** 2.12, 2.5, 3.3

**Phase recommendation:** Phase 2 (Management) - Required before Zone 3 agents launch

**Sources:**
- [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/sites/default/files/2025-12/2026-annual-regulatory-oversight-report.pdf)
- [FINRA Regulatory Notice 24-09](https://www.finra.org/rules-guidance/notices/24-09)

---

### CRITICAL: Recordkeeping Completeness Gap

**What goes wrong:** Organizations rely solely on Purview CopilotInteraction audit logs, believing they capture full prompt/response content for SEC 17a-4/FINRA 4511 compliance. Purview audit logs capture **metadata only** (timestamps, model info, detection flags) - NOT full conversational content.

**Why it happens:**
- Microsoft's audit schema naming suggests comprehensive coverage
- Organizations don't read schema field documentation carefully
- Assumption that "audit log" = "complete record"

**Consequences:**
- Recordkeeping violation during SEC/FINRA examination when full conversation reconstruction is requested
- Inability to demonstrate what agent said to customer
- Gap between believed compliance posture and actual capability

**Prevention:**
- Implement eDiscovery, DSPM for AI, or Communication Compliance for FULL content capture
- Document distinction: Purview audit = evidence trail; eDiscovery = content
- Test content retrieval BEFORE production deployment

**Detection:**
- Export CopilotInteraction schema and verify field contents
- Attempt to reconstruct full conversation from audit log alone
- Check if eDiscovery/DSPM configured for Copilot Studio workloads

**Which controls address this:** 1.7, 1.19, 1.6

**Phase recommendation:** Phase 1 (Foundation) - Must configure before Zone 3 agents interact with customers

**Sources:**
- Framework v1.2.32 - Control 1.7 CopilotInteraction schema clarification
- [SEC 2026 Examination Priorities](https://www.sec.gov/files/2026-exam-priorities.pdf)

---

### HIGH: AI Explainability Requirement

**What goes wrong:** AI systems flag communications as high-risk or make recommendations, but compliance teams cannot explain HOW the AI reached that decision when SEC examiners ask.

**Why it happens:**
- Organizations deploy black-box AI models without decision transparency
- Focus on outputs rather than reasoning process
- Model risk management doesn't include explainability testing

**Consequences:**
- SEC examination findings for inadequate supervisory controls
- Inability to demonstrate reasonableness of agent recommendations
- Potential enforcement if decision-making process cannot be demonstrated

**Prevention:**
- Require decision reasoning documentation in agent design (Agent Card)
- Test explainability BEFORE production (can you explain why agent made recommendation X?)
- Log decision factors alongside outputs
- Implement HITL review for non-explainable decisions

**Detection:**
- Ask "Why did the agent recommend X?" and verify answer exists
- Check if audit logs include decision reasoning fields
- Test reconstruction of agent decision logic from logs

**Which controls address this:** 2.6, 2.13, 3.2

**Phase recommendation:** Phase 2 (Management) - Required for Zone 3 agents making recommendations

**Sources:**
- [SEC 2026 Examination Priorities](https://www.wealthmanagement.com/regulation-compliance/sec-2026-examination-priorities-what-financial-services-firms-need-to-know)
- [Skadden AI Recordkeeping Analysis](https://www.skadden.com/insights/publications/2024/09/how-and-when-sec-recordkeeping-rules-may-apply)

---

### HIGH: OCC 2011-12 / SR 11-7 Model Classification Confusion

**What goes wrong:** Banks fail to apply Model Risk Management (MRM) guidance consistently to AI agents, either over-applying (9-month delays) or under-applying (missing governance).

**Why it happens:**
- Examiners lack consistent framework for classifying AI tools as "models"
- MRM processes designed for traditional statistical models don't fit AI agents well
- Excessive documentation requirements delay AI adoption

**Consequences:**
- OCC/Fed examination findings for inadequate model governance
- Delayed AI agent deployments (up to 9 months reported)
- Inconsistent risk management across agent portfolio

**Prevention:**
- Establish clear model classification criteria (use SR 11-7 definition: quantitative tool with outputs based on statistical/ML algorithms)
- Apply proportional MRM based on risk (Zone 1 = minimal, Zone 2 = basic, Zone 3 = comprehensive)
- Document model classification decisions with rationale
- Engage with examiners early for alignment on classification approach

**Detection:**
- Check if model inventory includes/excludes Copilot Studio agents
- Verify MRM documentation exists for Zone 3 agents
- Confirm independent validation performed for high-risk agents

**Which controls address this:** 2.6, 2.11, 2.5

**Phase recommendation:** Phase 2 (Management) - Required before deploying agents making financial decisions

**Sources:**
- [BPI OSTP AI RFI Response (October 2025)](https://bpi.com/wp-content/uploads/2025/10/BPI-OSTP-AI-RFI-Response-10.27.25.pdf)
- [OCC Model Risk Management Guidance](https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/model-risk-management/index-model-risk-management.html)

---

### MODERATE: Notice 25-07 Misinterpretation

**What goes wrong:** Organizations cite FINRA Notice 25-07 as requiring specific AI governance controls, when it actually addresses workplace modernization rules (not AI).

**Why it happens:**
- Notice 25-07 released April 2025 with "AI" mentioned in limited recordkeeping context
- Title suggests broader AI applicability than content delivers
- Organizations don't read full RFI vs. interpreting title

**Consequences:**
- Misdirected compliance effort
- Confusion about actual AI supervision requirements
- Missing actual guidance (Notice 24-09, 2026 Report)

**Prevention:**
- Reference FINRA Notice 24-09 (June 2024) for Gen AI guidance
- Use FINRA 2026 Annual Regulatory Oversight Report for AI agent supervision requirements
- Clarify Notice 25-07 is Request for Comment (RFI) on workplace modernization

**Detection:**
- Review compliance documentation citing Notice 25-07
- Check if referenced for AI governance vs. recordkeeping

**Which controls address this:** Framework regulatory references

**Phase recommendation:** Documentation accuracy check during Phase 1

---

## Technical Pitfalls

### CRITICAL: February 2026 Pipeline Deadline - Licensing Trap

**What goes wrong:** Organizations miss Microsoft's automatic Managed Environment enablement for pipeline targets starting February 2026, triggering premium licensing requirements for ALL users in those environments.

**Why it happens:**
- Notification via Microsoft 365 Message Center (MC) easily missed
- Organizations use pipelines without realizing Managed Environment implications
- Assumption that existing licensing covers new requirements

**Consequences:**
- Sudden premium license requirement for all active users in pipeline target environments
- Budget impact (Power Apps Premium $20/user/month or Power Automate Premium $15/user/month)
- Potential service interruption if licenses not procured

**Prevention:**
- Enable Managed Environments manually NOW for all pipeline targets
- Audit active users in pipeline target environments
- Procure premium licenses proactively (Power Apps Premium, Power Automate Premium, Copilot Studio, or Dynamics 365)
- Configure automatic Managed Environment setting for new pipelines

**Detection:**
- Query environments: `Get-AdminPowerAppEnvironment | Where-Object {$_.Internal.properties.states.management.id -eq "ManagedEnvironment"}`
- Check Message Center for MC notifications about pipeline enforcement
- Review pipeline configuration for target environments

**Which controls address this:** 2.1, 2.2

**Phase recommendation:** IMMEDIATE action required - deadline February 2026

**Sources:**
- Framework v1.2.25 - Control 2.1 critical warning
- [Power Platform Pipelines Documentation](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)

---

### CRITICAL: Pay-As-You-Go (PAYG) Licensing Misconception

**What goes wrong:** Organizations enable Pay-As-You-Go for Managed Environments, believing it satisfies licensing requirements. PAYG does NOT satisfy Managed Environment licensing for active users without standalone licenses.

**Why it happens:**
- PAYG name suggests comprehensive licensing coverage
- Microsoft documentation distinction between capacity licensing vs. user licensing is subtle
- Organizations see PAYG as easier than individual license procurement

**Consequences:**
- Non-compliant Managed Environment configuration
- Licensing violation risk
- Potential service disruption during audit

**Prevention:**
- Procure per-user premium licenses (Power Apps Premium, Power Automate Premium, etc.) for Managed Environment users
- Use PAYG for capacity overages, NOT as primary licensing strategy
- Document licensing approach and validate with Microsoft licensing specialist

**Detection:**
- Check if Managed Environment relies solely on PAYG without user licenses
- Query active users and cross-reference with premium license assignments
- Review billing to see if costs align with expected user count

**Which controls address this:** 2.1

**Phase recommendation:** Phase 1 (Foundation) - Validate before enabling Managed Environments

**Sources:**
- Framework v1.2.32 - Control 2.1 PAYG limitation warning
- [Managed Environment Licensing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing)

---

### CRITICAL: Service Principal Security Group Bypass

**What goes wrong:** Organizations configure environment-level Security Groups to restrict access, but Service Principals bypass these controls entirely and can access ANY environment.

**Why it happens:**
- Microsoft documentation doesn't prominently highlight SP bypass behavior
- Assumption that Security Groups apply universally
- Service Principals created for automation without security review

**Consequences:**
- Unexpected privileged access to sensitive environments
- Compliance violation if separation of duties required
- Audit findings for inadequate access controls

**Prevention:**
- Implement defense-in-depth: row-level security (RLS), column-level security, Dataverse audit logging
- Quarterly audit of Service Principal permissions
- Rotate credentials regularly (90 days recommended)
- Minimize Service Principal privilege (least privilege principle)

**Detection:**
- Enumerate Service Principals with environment access
- Review RLS/column security configuration
- Check audit logs for Service Principal activity in restricted environments

**Which controls address this:** 2.8, 1.18

**Phase recommendation:** Phase 2 (Management) - Critical for Environment Lifecycle Management implementation

**Sources:**
- Framework v1.2.32 - ELM architecture.md critical warning
- Zenity research on Power Platform SP permissions (June 2025)

---

### HIGH: DLP Enforcement Mode Confusion

**What goes wrong:** Organizations deploy agents believing DLP is enforced, but agents are in "Soft-Enabled" mode where existing agents keep running without DLP adherence (only updates blocked).

**Why it happens:**
- Microsoft phased DLP enforcement rollout (January-March 2025)
- Mode changed from Soft-Enabled to Enabled without proactive notification
- Organizations don't verify enforcement mode after deployment

**Consequences:**
- Agents accessing restricted data despite DLP policies
- Compliance violation (GLBA 501(b), SEC Reg S-P)
- False sense of security

**Prevention:**
- Verify DLP enforcement mode is "Enabled" (not "Soft-Enabled")
- Test DLP policy blocking BEFORE production deployment
- Review MC973179 for phased rollout timeline (completed March 2025)
- Configure 11 virtual governance connectors for AI capabilities

**Detection:**
- Check Power Platform Admin Center > Data Policies > Enforcement Mode
- Test agent with restricted data connector
- Review CloudAppEvents for blocked DLP actions

**Which controls address this:** 1.5, 1.4

**Phase recommendation:** Phase 1 (Foundation) - Verify before any agent deployment

**Sources:**
- Framework v1.2.32 - Control 1.5 phased timeline
- [Microsoft Copilot Studio DLP Best Practices](https://ragnarheil.de/from-chaos-to-control-governance-best-practices-for-microsoft-copilot-studio-with-dlp-capacity-security-controls/)

---

### HIGH: Connector Governance Blind Spot

**What goes wrong:** Organizations focus on agent logic security but ignore connector governance, creating massive hidden risk surface for data exfiltration.

**Why it happens:**
- Copilot Studio includes ALL premium connectors by default
- Organizations don't realize agent can invoke any allowed connector
- Connector catalog is vast (hundreds) and complex

**Consequences:**
- Agent uses unapproved third-party connector
- Data exfiltration to unvetted SaaS application
- GLBA/SEC Reg S-P violation

**Prevention:**
- Implement Advanced Connector Policies (ACP) for granular control
- Allowlist approach: block by default, allow specific connectors
- Regular connector policy refresh as new connectors released
- Vendor risk assessment for third-party connectors

**Detection:**
- Review DLP policies for connector classifications
- Audit agent connections to identify connector usage
- Check CloudAppEvents for connector activity

**Which controls address this:** 1.4, 2.7

**Phase recommendation:** Phase 1 (Foundation) - Must configure before agent deployment

**Sources:**
- [Copilot Studio Governance Guide](https://holgerimbery.blog/copilot-studio-governance)
- [DLP and Governance Tips](https://ragnarheil.de/mastering-microsoft-copilot-studio-data-loss-prevention-and-governance-tips/)

---

### HIGH: Microsoft Defender Integration Confusion

**What goes wrong:** Organizations believe runtime protection is automatic, but native Defender integration requires explicit two-portal configuration (Defender Portal + Power Platform Admin Center).

**Why it happens:**
- Defender for Cloud Apps licensing doesn't auto-enable Copilot Studio protection
- Two-portal configuration requirement not obvious
- Organizations assume M365 E5 includes everything

**Consequences:**
- Prompt injection attacks succeed without blocking
- No AI agent inventory in Defender
- Missing XDR alerting for agent threats
- Compliance gap (Control 1.8)

**Prevention:**
- Configure native Defender integration via both portals (Step 5 in portal-walkthrough)
- Enable "Copilot Studio AI Agents" in Defender for Cloud Apps > M365 App Connector
- Enable Defender toggle in Power Platform Admin Center > Environment > AI Agents
- Verify AI agent inventory appears in Defender XDR

**Detection:**
- Check if AI agent inventory visible in Microsoft Defender XDR
- Query CloudAppEvents for CopilotInteraction events
- Test if Defender blocks known prompt injection pattern

**Which controls address this:** 1.8

**Phase recommendation:** Phase 1 (Foundation) - Required for Zone 2/3 agents

**Sources:**
- Framework v1.2.37 - Control 1.8 comprehensive documentation
- [Protect Copilot Studio AI Agents with Defender](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection)

---

### MODERATE: Information Barriers - Channel Agent Limitation

**What goes wrong:** Organizations assume Information Barriers (IB) work for all Copilot Studio deployment types, but Channel Agents do NOT support IB.

**Why it happens:**
- Microsoft documentation doesn't prominently call out limitation
- Assumption that IB applies universally across M365
- Organizations deploy Channel Agents for scalability without verifying IB support

**Consequences:**
- Agent shares information across IB segments
- FINRA Rule 2241 (research/investment banking wall) violation
- Chinese Wall breach for M&A teams

**Prevention:**
- Use Copilot Studio agents deployed in Teams (supports IB), NOT Channel Agents
- Test IB enforcement before production deployment
- Document IB applicability in agent architecture decisions

**Detection:**
- Identify agent deployment type (Teams vs. Channel)
- Test agent access across IB segments
- Review IB policy logs for agent user

**Which controls address this:** 1.22

**Phase recommendation:** Phase 2 (Management) - Critical for organizations with IB requirements

**Sources:**
- Framework v1.2.32 - Control 1.22 clarification

---

### MODERATE: x-api-key Deprecation (March 31, 2026)

**What goes wrong:** Organizations use Application Insights x-api-key authentication for RAI telemetry export, unaware of March 31, 2026 deprecation. Scripts fail after deadline.

**Why it happens:**
- Legacy authentication method still works (for now)
- Microsoft deprecation notice not widely visible
- Organizations copy older implementation patterns

**Consequences:**
- RAI telemetry export scripts fail after March 31, 2026
- Loss of hallucination/UPIA/XPIA tracking
- Compliance gap (Control 3.10)

**Prevention:**
- Migrate to Entra ID authentication (service principals or managed identities)
- Update Export-RaiTelemetry.ps1 to use Entra auth
- Reference FSI-AgentGov-Solutions DEC v1.1.0 for updated scripts

**Detection:**
- Search scripts for "-ApiKey" parameter
- Check if authentication uses x-api-key header
- Verify script execution after March 2026

**Which controls address this:** 1.8, 3.10

**Phase recommendation:** Phase 3 (Reporting) - Migrate before March 31, 2026

**Sources:**
- Framework v1.2.33 - DEC playbook deprecation warning
- [Azure Monitor API Retirement Notice](https://azure.microsoft.com/en-us/updates/)

---

## Documentation Accuracy Pitfalls

### Critical Documentation Mistakes

Based on framework's 36 versions with 189 corrections/clarifications (v1.2.1 - v1.2.37), common documentation accuracy pitfalls:

1. **Regulatory Citation Precision**
   - **Pitfall:** Citing wrong regulation section or misattributing requirements
   - **Examples:** FINRA 4511 retention (5 files corrected v1.2.17), SEC 17a-4 retention period (5 files v1.2.19), CFTC WORM misattribution (v1.2.29)
   - **Prevention:** Verify citations against official regulator sources, include CFR section numbers, link to source

2. **Feature Naming History**
   - **Pitfall:** Using outdated product/feature names
   - **Examples:** "AI Hub DSPM" → "DSPM for AI" (v1.2.35), Sentinel Azure portal deprecation
   - **Prevention:** Check Microsoft Learn for current naming, note rebranding dates

3. **Licensing Scope Creep**
   - **Pitfall:** Overstating what's included in base licenses
   - **Examples:** E5 vs E5 Compliance vs E5 Security distinctions, Copilot Studio premium connectors
   - **Prevention:** Reference official Microsoft licensing guide, specify SKU exactly

4. **Technical Capability Overclaims**
   - **Pitfall:** Stating features exist that require additional configuration or don't exist
   - **Examples:** CopilotInteraction full content (metadata only), UPIA/XPIA detection locations
   - **Prevention:** Test feature, read schema documentation, verify with Microsoft Learn

5. **Deprecation Date Accuracy**
   - **Pitfall:** Wrong retirement/deprecation dates
   - **Examples:** Exchange Basic Auth (corrected v1.2.32), x-api-key (March 31, 2026), Azure Key Vault API (February 27, 2027)
   - **Prevention:** Check Message Center, Azure Updates, verify MC number

---

## Prevention Strategies

### Organizational Level

1. **Establish Research Validation Protocol**
   - Verify regulatory claims with official sources (finra.org, sec.gov, federalreserve.gov)
   - Cross-reference Microsoft Learn for technical capabilities
   - Date all documentation with "verified as of [date]"
   - Flag LOW confidence claims requiring validation

2. **Implement Technical Verification**
   - Test feature claims in lab environment before documenting
   - Export schemas and verify field contents
   - Screenshot portal configurations with dates
   - Maintain "Last Verified" metadata per control

3. **Monitor Regulatory Updates**
   - Subscribe to FINRA Regulatory Notices, SEC examination priorities
   - Track Microsoft 365 Message Center for deprecations
   - Quarterly review of framework controls for accuracy
   - Annual regulatory mapping validation

4. **Licensing Clarity**
   - Reference official Microsoft Licensing Guide (month/year version)
   - Specify exact SKU names (not generic "E5")
   - Validate with Microsoft licensing specialist before documenting requirements
   - Track PAYG vs. per-user license distinctions

### Phase-Specific Prevention

| Phase | Primary Pitfall Risks | Mitigation |
|-------|----------------------|------------|
| Phase 1 (Foundation) | Retention classification, DLP enforcement mode, Defender integration | Validate retention matrix, test DLP blocking, verify Defender inventory |
| Phase 2 (Management) | FINRA supervision gaps, MRM classification, Service Principal bypass | Document WSPs, classify agents as models per SR 11-7, implement RLS |
| Phase 3 (Reporting) | Recordkeeping completeness, x-api-key deprecation | Configure eDiscovery, migrate to Entra auth |
| Phase 4 (Maturity) | February 2026 deadline, PAYG misconception | Enable Managed Environments, procure premium licenses |

---

## Sources

### Regulatory Sources (HIGH Confidence)

- [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/sites/default/files/2025-12/2026-annual-regulatory-oversight-report.pdf)
- [FINRA Regulatory Notice 24-09 - Gen AI Guidance](https://www.finra.org/rules-guidance/notices/24-09)
- [SEC 2026 Examination Priorities](https://www.sec.gov/files/2026-exam-priorities.pdf)
- [OCC Model Risk Management Guidance](https://www.occ.gov/publications-and-resources/publications/comptrollers-handbook/files/model-risk-management/index-model-risk-management.html)
- [Federal Reserve SR 11-7](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm)

### Microsoft Official Sources (HIGH Confidence)

- [Power Platform Pipelines Documentation](https://learn.microsoft.com/en-us/power-platform/alm/pipelines)
- [Managed Environment Licensing](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-licensing)
- [Protect Copilot Studio AI Agents - Defender](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection)
- [SEC 17a-4 Compliance - Microsoft](https://learn.microsoft.com/en-us/compliance/regulatory/offering-sec-docs)

### Industry Analysis (MEDIUM Confidence)

- [Skadden - SEC Recordkeeping Rules for AI](https://www.skadden.com/insights/publications/2024/09/how-and-when-sec-recordkeeping-rules-may-apply)
- [McGuireWoods - FINRA 2026 Report Analysis](https://www.mcguirewoods.com/client-resources/alerts/2025/12/finras-2026-annual-regulatory-oversight-report-same-priorities-new-focus-on-ai-and-cybersecurity/)
- [Directions on Microsoft - Defender for Cloud Apps](https://www.directionsonmicrosoft.com/reports/defender-for-cloud-apps-helps-protect-copilot-studio-agents/)

### Community Best Practices (MEDIUM Confidence)

- [Holger Imbery - Copilot Studio Governance](https://holgerimbery.blog/copilot-studio-governance)
- [Ragnar Heil - DLP Best Practices](https://ragnarheil.de/from-chaos-to-control-governance-best-practices-for-microsoft-copilot-studio-with-dlp-capacity-security-controls/)

### Framework Internal Sources (HIGH Confidence)

- FSI-AgentGov CHANGELOG.md (v1.2.1 - v1.2.37) - 189 corrections across 36 versions
- Framework documentation accuracy remediation phases (v1.2.17 - v1.2.37)

---

**Research Complete:** February 2, 2026
**Next Steps:** Use findings to inform roadmap phase structure and identify controls requiring deeper implementation guidance
