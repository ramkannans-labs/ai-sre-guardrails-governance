# Learner Lab Guide: Week 6 - Guardrails & Governance

## Lab 6.1: Policy Engine Basics
1. Explore `guardrails/policies/` directory structure.
2. Define a custom policy for error rate thresholds.
3. Validate policies in `policies/validator.py`.

## Lab 6.2: AWS Guardrails Configuration
1. Create IAM policies in `guardrails/aws/iam-policies/`.
2. Configure VPC boundary in `guardrails/aws/network-policies/`.
3. Test policy enforcement via `scripts/test_aws_guardrails.sh`.

## Lab 6.3: Kubernetes Policies
1. Set up KPolicyEngine in `guardrails/kubernetes/policy-config.yaml`.
2. Configure lineage tracking in `k8s-resource-tracker/`.
3. Define vulnerability and rotation checks.

## Lab 6.4: AgentOps Integration
1. Configure agent lifecycle in `agent-ops/agent_config.yaml`.
2. Set up control plane for AI agents in `agent-ops/control_plane.py`.
3. Verify agent governance via `scripts/audit_agents.sh`.

## Lab 6.5: Compliance & Auditing
1. Run audit collectors in `scripts/run_audit.sh`.
2. Generate compliance report in `compliance/report.py`.
3. Review governance dashboard.

## Lab 6.6: Shadow Duel
1. Set up human governance baseline in `shadow-duel/human_governance_baseline.py`.
2. Configure AI governance in `shadow-duel/ai_governance.py`.
3. Run comparative analysis and document findings.