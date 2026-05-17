# Frontier Readiness Assessment Coverage Matrix

This page is **generated** by `scripts/generate_coverage_matrix.py --type frontier` from `assessment/manifest/frontier-readiness.json`. Do not edit by hand.

It is the honest answer to *what does the Frontier Readiness assessment actually automate today?* In the current manifest, 6 of 25 questions (24.0%) are telemetry-backed, 19 remain facilitator-answered by design, and 0 still declare automation that is not yet wired.

## Evaluator states

| State | Icon | Meaning |
|-------|------|---------|
| `auto_evaluable` | ✅ | Evaluator is registered AND `auto_evaluable: true` in the manifest. Score derived from telemetry. |
| `unimplemented_evaluator` | ⚠️ | Manifest declares a `pass_condition` but the question is marked `auto_evaluable: false` and no evaluator function exists. (Most common state in v1.) |
| `manual_only` | 📝 | Question is manual by design (`collection_methods: ["Manual"]` and `auto_evaluable: false`). Facilitator-answered only. |

## Summary

### By question

| State | Count | Share |
|-------|-------|-------|
| ✅ Auto | 6 | 24.0% |
| 📝 Manual | 19 | 76.0% |
| ⚠️ Unimplemented | 0 | 0.0% |
| **Total** | 25 | 100% |

### Per-driver breakdown

| Driver | Total Questions | Auto | Manual | Unimplemented |
|---|---|---|---|---|
| AI Strategy & Experience | 5 | 2 | 3 | 0 |
| Business Strategy | 5 | 0 | 5 | 0 |
| AI Governance & Security | 5 | 1 | 4 | 0 |
| Technology & Data | 5 | 3 | 2 | 0 |
| Organization & Culture | 5 | 0 | 5 | 0 |

## Per-question detail

### AI Strategy & Experience

| Q ID | Level | Question | State | Pass Condition | Notes |
|---|---|---|---|---|---|
| Q01 | 100 | Has the organization identified at least one named individual responsible for... | ✅ Auto | `ai_initiative_owner_identified` |  |
| Q02 | 200 | Within at least one business unit, do AI agent investments follow recurring, ... | 📝 Manual | `bu_level_repeatable_intake_pattern` | Facilitator-answered. |
| Q03 | 300 | Has the organization published an enterprise AI strategy reviewed by a Govern... | ✅ Auto | `enterprise_ai_strategy_published_with_portfolio` | Auto-evaluator capped at 'partial' — site naming heuristic detects strategy publication, but governance review + portfolio scope are facilitator-only. |
| Q04 | 400 | Is the AI strategy refreshed on a documented cadence aligned to the firm's go... | 📝 Manual | `strategy_refresh_cadence_with_board_reporting` | Facilitator-answered. |
| Q05 | 500 | Do named executive sponsors provide quarterly outcome attestation for each pa... | 📝 Manual | `quarterly_sponsor_attestation_with_sunset_criteria` | Facilitator-answered. |

### Business Strategy

| Q ID | Level | Question | State | Pass Condition | Notes |
|---|---|---|---|---|---|
| Q06 | 100 | Have any deployed AI agents been assigned a business owner accountable for th... | 📝 Manual | `any_agent_has_business_owner` | Facilitator-answered. |
| Q07 | 200 | Within a single business line, are agent use cases tied to informal but ident... | 📝 Manual | `bu_level_outcome_targets_tracked` | Facilitator-answered. |
| Q08 | 300 | Are formal process redesign artifacts maintained for production agents, with ... | 📝 Manual | `documented_process_redesign_with_kpi_dashboards` | Facilitator-answered. |
| Q09 | 400 | Are end-to-end agent-supported services governed by documented decision bound... | 📝 Manual | `e2e_service_with_slas_and_exec_review` | Facilitator-answered. |
| Q10 | 500 | Do agents in core business processes (KYC, claims, financial close, regulator... | 📝 Manual | `core_processes_under_versioned_decision_rules_with_supervisors` | Facilitator-answered. |

### AI Governance & Security

| Q ID | Level | Question | State | Pass Condition | Notes |
|---|---|---|---|---|---|
| Q11 | 100 | Does the organization have any informal guardrails (acceptable use guidance, ... | 📝 Manual | `informal_guardrails_in_place` | Facilitator-answered. |
| Q12 | 200 | In some business units, are platform controls (DLP, audit logging) applied to... | 📝 Manual | `bu_level_platform_controls_and_written_policy` | Facilitator-answered. |
| Q13 | 300 | Are agents classified into Zone-tiered Managed Environments with comprehensiv... | ✅ Auto | `zone_classification_with_audit_supervision_and_model_risk` | Auto-evaluator caps suggested answer at 'partial' because model-risk overlay (the third L300 signal) is not telemetry-verifiable. Facilitator must confirm model risk separately to upgrade to 'yes'. |
| Q14 | 400 | Do risk metrics flow into a risk committee on a documented cadence, supported... | 📝 Manual | `risk_metrics_to_committee_with_tested_runbooks` | Facilitator-answered. |
| Q15 | 500 | Does the organization operate continuous control monitoring with risk-tier-ba... | 📝 Manual | `continuous_monitoring_with_release_gates_and_examiner_drills` | Facilitator-answered. |

### Technology & Data

| Q ID | Level | Question | State | Pass Condition | Notes |
|---|---|---|---|---|---|
| Q16 | 100 | Is there any visibility into which Power Platform environments host AI agents... | ✅ Auto | `any_environment_visibility_for_agents` |  |
| Q17 | 200 | Are some environments tagged or grouped for agent workloads, with basic telem... | ✅ Auto | `tagged_environments_with_basic_telemetry` |  |
| Q18 | 300 | Are Environment Groups with tier classification operational, with automated a... | ✅ Auto | `env_groups_with_inventory_siem_rag_and_lineage` | Auto-evaluator capped at 'partial' — 3/5 signals are telemetry-verifiable (env groups, SIEM, SP scan), but agent inventory is not collected and RAG-integrity + lineage are facilitator-only. |
| Q19 | 400 | Does the platform provide integrated telemetry across Sentinel, the Agent 365... | 📝 Manual | `integrated_telemetry_with_curated_templates_and_agent_id` | Facilitator-answered. |
| Q20 | 500 | Is the platform continuously monitored and version-controlled, with multi-age... | 📝 Manual | `continuous_platform_with_orchestration_limits_and_validated_grounding` | Facilitator-answered. |

### Organization & Culture

| Q ID | Level | Question | State | Pass Condition | Notes |
|---|---|---|---|---|---|
| Q21 | 100 | Has any baseline AI awareness communication (e.g., acceptable use email, intr... | 📝 Manual | `baseline_awareness_communication_issued` | Facilitator-answered. |
| Q22 | 200 | Does a general AI training module exist that staff in pilot business units ha... | 📝 Manual | `general_training_completed_in_pilot_with_maker_channels` | Facilitator-answered. |
| Q23 | 300 | Is a role-based training and awareness program operational covering superviso... | 📝 Manual | `role_based_training_with_disclosure_and_comm_compliance` | Facilitator-answered. |
| Q24 | 400 | Is there a curated maker community with documented contribution paths and KPI... | 📝 Manual | `curated_maker_community_with_external_governance_and_evidenced_training` | Facilitator-answered. |
| Q25 | 500 | Can the organization demonstrate to an examiner that the supervisor — not the... | 📝 Manual | `supervisor_accountability_with_per_decision_review_under_change_control` | Facilitator-answered. |

## Future evaluator candidates

The remaining manual questions already carry `pass_condition` strings in the manifest, so the per-question table above is the live backlog for future evaluator work. Add an explicit shortlist here when a specific implementation wave is planned.

No separate future-evaluator shortlist is maintained yet.

## How to wire up an evaluator (future)

1. Add a `_eval_<name>(collected, source_key)` function to a new `assessment/engine/score_frontier.py` evaluators block, returning `(passed: bool | None, evidence: str)`.
2. Update the question entry in `frontier-readiness.json`: set `auto_evaluable: true`, change `collection_methods` to include the API source (`Graph_API`, `SharePoint_PnP`, etc.).
3. Re-run `python scripts/generate_coverage_matrix.py --type frontier` and commit the regenerated `docs/reference/frontier-assessment-coverage.md`.

<!-- This page is generated by scripts/generate_coverage_matrix.py --type frontier. Do not edit by hand. -->
