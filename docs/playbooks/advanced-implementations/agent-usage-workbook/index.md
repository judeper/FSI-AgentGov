# Agent Usage & Performance Workbook

**Status:** In Development — February 2026
**Related Controls:** 3.1, 3.2, 3.3, 3.7, 3.8

---

## Overview

The Agent Usage & Performance Workbook is an Azure Monitor Workbook that provides unified visibility into Copilot Studio agent activity across an FSI organization. Built on Application Insights telemetry, the workbook consolidates usage metrics, performance indicators, and governance signals into a single operational dashboard.

The workbook is designed for M365 administrators, compliance officers, and AI governance leads who need to monitor agent adoption, identify performance issues, and support regulatory reporting requirements.

### Workbook Tabs

| Tab | Purpose | Key Metrics |
|-----|---------|-------------|
| **Usage Overview** | Agent adoption and conversation volume | Active users, conversations per agent, channel distribution, usage trends |
| **Performance & Errors** | Agent health and reliability | Error rates, exception patterns, dependency failures, response latency estimates |
| **Governance & Compliance** | Regulatory monitoring signals | Escalation rates, topic coverage, session patterns, generative AI usage |

---

## Available Documentation

| Document | Description | Status |
|----------|-------------|--------|
| [Telemetry Schema Reference](telemetry-schema.md) | Application Insights telemetry schema for Copilot Studio — event types, customDimensions properties, channel identifiers, session tracking, and prerequisites | Available |
| KQL Query Library | Complete query library powering all workbook visualizations | Planned (Phase 1) |
| Deployment Guide | Step-by-step workbook deployment and configuration | Planned (Phase 3) |
| Customization Guide | Adapting the workbook for organization-specific requirements | Planned (Phase 3) |

---

## Prerequisites

- Azure Application Insights resource connected to Copilot Studio agents
- Appropriate Azure RBAC permissions (Reader or higher on the Application Insights resource)
- Copilot Studio "Log activities" setting enabled per agent

See the [Telemetry Schema Reference](telemetry-schema.md) for detailed prerequisite configuration.

---

!!! info "Development Status"
    This solution is in development. The telemetry schema reference is available; the KQL query library, deployment guide, and customization guide will follow in subsequent phases.

---

*Updated: February 2026 | Version: v1.3 | Framework: FSI Agent Governance*
