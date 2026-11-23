# AI SRE Guardrails & Governance

## Overview
This repository contains labs and code for Week 6 of the AI SRE Practitioner Program: **Guardrails, Governance, and Compliance**.

Governance is the set of policies, standards, protocols, and procedures that keep your organization's SRE practices well-defined and scalable. This week focuses on building automated guardrails to enforce SLO compliance, agent governance, and audit trails.

## Key Concepts
- **Policy Engine**: Centralized rule-based enforcement for AWS, Kubernetes, and SLO policies.
- **AgentOps**: Orchestration and governance of AI-driven agents for SRE tasks.
- **Compliance**: Automated audit trails and reporting for regulatory and internal control.
- **Governance Dashboard**: Unified view of SLO status, policy violations, and agent activity.
- **Shadow Duel**: Week 6 signature exercise comparing human vs AI governance capabilities.

## Lab Exercises
1. **6.1 - Policy Engine**: Building configurable policy rules for system governance.
2. **6.2 - AWS Guardrails**: Setting up IAM, networking, and resource policies.
3. **6.3 - Kubernetes Policies**: Enforcing lineage, vulnerability, and rotation policies.
4. **6.4 - AgentOps Integration**: Orchestration and control of AI SRE agents.
5. **6.5 - Comply & Audit**: Generating audit trails and compliance reports.
6. **6.6 - Shadow Duel**: Live comparison of human vs AI governance.

## Quick Start
1. **Deploy Guardrails**: Configure via guardrails/policy-engine.yaml.
2. **Configure Policies**: Edit policies in `policies/` directory.
3. **Agent Governance**: Set up agent config in `agent-ops/`.
4. **Audit Trails**: Run audit scripts to generate compliance reports.
5. **Dashboard**: Visualize in governance dashboard.

## Prerequisites
- AWS account with IAM and KMS configured.
- Kubernetes cluster (EKS) with Argocd for GitOps.
- OpenTelemetry and Prometheus (from Weeks 2-3).

## Documentation
- `docs/trainer-guide.md`: 6-phase trainer session breakdown.
- `docs/learner-lab-guide.md`: Step-by-step hands-on instructions.