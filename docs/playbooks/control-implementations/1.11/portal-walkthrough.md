# Control 1.11: Conditional Access and Phishing-Resistant MFA - Portal Walkthrough

> This playbook provides portal configuration guidance for [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md).

---

## Prerequisites

- Microsoft Entra ID P1/P2 licenses assigned
- Emergency access (break-glass) accounts configured and excluded from CA
- Named locations defined for office networks
- Authentication methods configured
- Agent inventory available for policy targeting

---

## Step 1: Access Conditional Access

**Portal Path:** Microsoft Entra admin center > Conditional Access

1. Open [Microsoft Entra admin center](https://entra.microsoft.com)
2. Navigate to **Entra ID** > **Conditional Access**
3. Review the Overview dashboard

### Dashboard Review

| Card | Action |
|------|--------|
| Agent Identities | Monitor agent coverage |
| Policy Snapshot | Track policy state (Enabled/Report-only/Off) |
| Users | Address coverage gaps |
| Applications | Ensure agent apps are protected |

---

## Step 2: Configure Named Locations

**Portal Path:** Conditional Access > Manage > Named locations

1. Click **+ New location**
2. Configure corporate office locations:
   - **Name:** Corporate Offices
   - **IP ranges:** Add office IP ranges
   - **Mark as trusted location:** Yes
3. Click **Create**

---

## Step 3: Configure Authentication Methods

**Portal Path:** Entra ID > Authentication methods > Policies

### FSI Recommended Settings

| Method | Tier 1 | Tier 2 | Tier 3 |
|--------|--------|--------|--------|
| Passkey (FIDO2) | Enable | Enable | **Required** |
| Microsoft Authenticator | Enable | Enable | Limited |
| SMS | Disable | Disable | Block |
| Certificate-based auth | Enable | Enable | **Required** |

1. Navigate to **Authentication methods** > **Policies**
2. Enable FIDO2/Passkey for enterprise users
3. Disable SMS and Voice for Tier 2-3 users
4. Enable Certificate-based authentication for enterprise

---

## Step 4: Configure Authentication Strengths

**Portal Path:** Conditional Access > Manage > Authentication strengths

1. Click **+ New authentication strength**
2. Create FSI-specific strength:
   - **Name:** FSI-Phishing-Resistant
   - **Methods:** FIDO2 security key, Certificate-based
3. Click **Create**

---

## Step 5: Create Conditional Access Policies

**Portal Path:** Conditional Access > Policies > + New policy

### Policy 1: Baseline MFA for All Users

1. Click **+ New policy**
2. Configure:
   - **Name:** FSI-Baseline-All-Users-MFA
   - **Users:** All users (exclude break-glass accounts)
   - **Cloud apps:** All cloud apps
   - **Grant:** Require MFA
   - **State:** Enabled
3. Click **Create**

### Policy 2: Agent Creators - Phishing-Resistant MFA

1. Click **+ New policy**
2. Configure:
   - **Name:** FSI-Enterprise-Agent-Creators-PhishingResistantMFA
   - **Users:** sg-enterprise-agent-creators (exclude break-glass)
   - **Cloud apps:** Power Platform, Copilot Studio
   - **Grant:** Require authentication strength (FSI-Phishing-Resistant)
   - **State:** Report-only (test first)
3. Click **Create**

### Policy 3: High-Risk Sign-In Response

1. Click **+ New policy**
2. Configure:
   - **Name:** FSI-HighRisk-SignIn-Response
   - **Users:** All users (exclude break-glass)
   - **Conditions:** Sign-in risk = High
   - **Grant:** Require MFA + Require password change
   - **State:** Enabled
3. Click **Create**

---

## Step 6: Validate Break-Glass Exclusions

**Portal Path:** Conditional Access > Policies > What if

1. Navigate to **What if**
2. Select break-glass account
3. Select all cloud apps
4. Click **What if**
5. **Expected:** No CA policies apply (or only intended controls)

---

## Step 7: Configure Agent ID (Preview)

**Portal Path:** Entra ID > Agent ID (Preview)

### Review Agent Overview

1. Navigate to **Agent ID** > **Overview**
2. Review agent metrics:
   - Total agents
   - Recently created
   - Unmanaged (assign sponsors)
   - Active agents

### Configure Agent Collections

1. Navigate to **Agent collections**
2. Review predefined collections:
   - **Global:** Visible to all identities
   - **Quarantined:** Hidden from all (use for review)
3. Create custom collections as needed

### Assign Agent Sponsors

1. Navigate to **All agent identities**
2. For each Zone 2/3 agent:
   - Select agent
   - Assign human sponsor
   - Document sponsorship

---

## Step 8: Monitor Agent Sign-Ins

**Portal Path:** Agent ID > Sign-in logs

1. Navigate to **Sign-in logs**
2. Filter: **Is Agent** = Yes
3. Review:
   - Service principal sign-ins
   - Non-interactive user sign-ins
4. Configure alerts for anomalies

---

*Updated: January 2026 | Version: v1.1*
