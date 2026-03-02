# Control 1.24: Defender AI Security Posture Management (AI-SPM)

## Expected Screenshots

### Screenshot 1: AI-SPM Plan Enablement
**Portal Path:** Azure Portal → Microsoft Defender for Cloud → Environment settings → [Subscription] → Defender plans
**What to capture:**
- AI-SPM plan enabled on Azure subscription
- Plan status (On/Off)
- Pricing tier and coverage scope

### Screenshot 2: AI Workload Discovery and Inventory
**Portal Path:** Azure Portal → Microsoft Defender for Cloud → Inventory → Filter: Resource type = AI
**What to capture:**
- Discovered AI agents across Microsoft Foundry and Copilot Studio
- AI Bill of Materials (AI BOM) for inventoried components
- Agent count and resource details

### Screenshot 3: Attack Path Analysis for AI Workloads
**Portal Path:** Azure Portal → Microsoft Defender for Cloud → Attack path analysis
**What to capture:**
- AI-specific attack path scenarios identified
- Attack path targeting AI workloads and sensitive data
- Risk factors including indirect prompt injection and data exfiltration

### Screenshot 4: Security Recommendations for AI
**Portal Path:** Azure Portal → Microsoft Defender for Cloud → Recommendations → Filter: Category = AI/ML
**What to capture:**
- Prioritized security recommendations for AI workloads
- Recommendation severity and remediation guidance
- Compliance status per recommendation

### Screenshot 5: Multi-Cloud Connector Configuration
**Portal Path:** Azure Portal → Microsoft Defender for Cloud → Environment settings → Add environment
**What to capture:**
- Multi-cloud connector setup for AWS Bedrock or GCP Vertex AI (if applicable)
- Connector status and discovery scope
- Cross-cloud AI workload visibility

### Screenshot 6: AI-SPM Dashboard Overview
**Portal Path:** Azure Portal → Microsoft Defender for Cloud → Overview → AI security posture
**What to capture:**
- AI security posture summary dashboard
- Risk factor distribution across AI workloads
- Trend indicators for posture improvements or regressions

---

## Verification Focus
- Capture from pre-production environment when possible
- Ensure subscription and resource names are representative but not sensitive
- Include timestamps to demonstrate currency
- Verify UI matches documentation after Microsoft portal updates
- Note: Multi-cloud screenshots only applicable if AWS/GCP AI services are in scope

---

## Screenshot Organization

Organize screenshots in this directory as:
- `1.24-01-ai-spm-plan.png` — AI-SPM plan enablement
- `1.24-02-ai-workload-inventory.png` — AI workload discovery and inventory
- `1.24-03-attack-path-analysis.png` — AI attack path analysis
- `1.24-04-security-recommendations.png` — AI security recommendations
- `1.24-05-multi-cloud-connector.png` — Multi-cloud connector configuration
- `1.24-06-ai-spm-dashboard.png` — AI-SPM dashboard overview
