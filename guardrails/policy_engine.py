#!/usr/bin/env python3
"""
Policy Engine

Centralized rule-based enforcement for AWS, Kubernetes, and SLO policies.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class PolicyCategory(Enum):
    """Categories of governance policies."""
    AWS = "aws"
    KUBERNETES = "kubernetes"
    SLO = "slo"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    FINANCE = "finance"


class EnforcementAction(Enum):
    """Actions to take when a policy is violated."""
    DENY = "deny"
    WARN = "warn"
    AUDIT = "audit"
    BLOCK_DEPLOY = "block_deployment"


@dataclass
class PolicyRule:
    """A single policy rule."""
    name: str
    category: PolicyCategory
    resource_type: str
    condition: str  # Expression or condition string
    enforcement_action: EnforcementAction
    severity: str  # "low", "medium", "high", "critical"
    description: str
    enabled: bool = True


@dataclass
class PolicyContext:
    """The context in which a policy is evaluated."""
    resource: Dict[str, Any]
    region: str
    account_id: str
    effective_org_units: List[str]


class PolicyEngine:
    """
    Centralized policy enforcement engine.

    Supports:
    - AWS resource policies (IAM, VPC, EKS)
    - Kubernetes resource policies (lineage, vulnerability, rotation)
    - SLO-based governance
    - Compliance and security policies
    """

    def __init__(self):
        self.policies: Dict[str, PolicyRule] = {}
        self.violations: List[Dict[str, Any]] = []
        self.audit_trail: List[Dict[str, Any]] = []

    def register_policy(self, policy: PolicyRule):
        """Register a new policy."""
        self.policies[policy.name] = policy
        print(f"Policy registered: {policy.name} ({policy.category.value})")

    def register_policy_from_yaml(self, yaml_path: str):
        """Register policy from YAML file."""
        # Would parse YAML here
        policy = PolicyRule(
            name="example-policy",
            category=PolicyCategory.AWS,
            resource_type="s3_bucket",
            condition="acls.public_access.enabled == true",
            enforcement_action=EnforcementAction.BLOCK_DEPLOY,
            severity="high",
            description="Block S3 buckets with public access",
        )
        self.register_policy(policy)

    def evaluate_policy(
        self,
        policy_name: str,
        context: PolicyContext,
    ) -> bool:
        """
        Evaluate a single policy.

        Returns True if policy passes, False if violated.
        """
        policy = self.policies.get(policy_name)
        if not policy or not policy.enabled:
            return True

        # Would parse and evaluate condition expression here
        # For demo, we'll use a simple mock evaluation
        success = self._evaluate_condition(policy.condition, context.resource)

        if not success:
            self._log_violation(policy, context, EnforcementAction.DENY)

        return success

    def evaluate_all_policies(
        self,
        context: PolicyContext,
    ) -> Dict[str, bool]:
        """
        Evaluate all policies against a context.

        Returns dict mapping policy names to pass/fail results.
        """
        results = {}
        for policy_name, policy in self.policies.items():
            if not policy.enabled:
                results[policy_name] = True
                continue

            success = self._evaluate_condition(policy.condition, context.resource)
            results[policy_name] = success

            if not success:
                self._log_violation(policy, context, policy.enforcement_action)

        return results

    def check_commit_policy(
        self,
        context: PolicyContext,
    ) -> tuple[bool, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Check policies before committing code changes.

        Returns:
            (allowed, filtered_contexts, details)
        """
        results = self.evaluate_all_policies(context)
        violations = [
            {"policy": name, **result}
            for name, result in results.items()
            if not result["passed"]
        ]

        if violations:
            return False, [], {"violations": violations}

        return True, [], {"message": "All policies passed"}

    def _evaluate_condition(self, condition: str, resource: Dict[str, Any]) -> bool:
        """
        Evaluate a policy condition against a resource.

        For demo, simulates evaluation truth table.
        """
        condition_upper = condition.upper()

        # Mock evaluation based on condition keywords
        if "PUBLIC" in condition_upper:
            return not resource.get("public_access", True)
        elif "ANY_ROLE" in condition_upper:
            return not resource.get("default_bucket_policy", False)
        elif "ERROR_RATE" in condition_upper:
            return resource.get("error_rate", 0.0) < 0.05
        elif "LATENCY" in condition_upper:
            return resource.get("latency_ms", 0.0) < 500.0
        elif "HIGH_RISK_LABEL" in condition_upper:
            return resource.get("risk_level", "low") != "high"
        else:
            # Default: assume condition passes
            return True

    def _log_violation(
        self,
        policy: PolicyRule,
        context: PolicyContext,
        action: EnforcementAction,
    ):
        """Log a policy violation."""
        violation = {
            "timestamp": datetime.utcnow().isoformat(),
            "policy": policy.name,
            "category": policy.category.value,
            "resource": context.resource.get("name", "unknown"),
            "resource_type": resource.resource_type,
            "condition": policy.condition,
            "enforcement_action": action.value,
            "severity": policy.severity,
            "account_id": context.account_id,
            "region": context.region,
        }

        self.violations.append(violation)
        self.audit_trail.append(violation)

        print(f"⚠️  Violation: {policy.name} - {policy.severity} severity")

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all recorded violations."""
        return self.violations

    def reset_violations(self):
        """Clear violation log."""
        self.violations = []
        print("Violation log cleared")

    def generate_audit_report(self, output_path: str) -> bool:
        """
        Generate an audit report of violations.

        Returns:
            bool: True if successful, False otherwise
        """
        import json
        from pathlib import Path

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_violations": len(self.violations),
            "violations": self.violations,
            "summary": self._generate_violation_summary(),
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            output_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
            print(f"✓ Audit report generated: {output_path}")
            return True

        except Exception as e:
            print(f"Error generating audit report: {e}")
            return False

    def _generate_violation_summary(self) -> Dict[str, Any]:
        """Generate summary statistics of violations."""
        severity_counts = {}
        category_counts = {}

        for v in self.violations:
            severity = v["severity"]
            category = v["category"]

            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "by_severity": severity_counts,
            "by_category": category_counts,
            "total_violations": len(self.violations),
            "allowed_resources": len(self.violations) * 10,  # Mock: verify against 10 resources
        }


async def main():
    """Demo: Run policy engine sample."""
    from datetime import datetime

    engine = PolicyEngine()

    # Register sample policies
    policies = [
        PolicyRule(
            name="s3-no-public",
            category=PolicyCategory.AWS,
            resource_type="s3_bucket",
            condition="acls.public_access.enabled == true",
            enforcement_action=EnforcementAction.BLOCK_DEPLOY,
            severity="critical",
            description="Block S3 buckets with public access",
        ),
        PolicyRule(
            name="eks-no-admin-role",
            category=PolicyCategory.AWS,
            resource_type="iam_role",
            condition="role.assume_role_policy.allow_any_account == true",
            enforcement_action=EnforcementAction.WARN,
            severity="high",
            description="Warn on IAM roles that allow any account",
        ),
        PolicyRule(
            name="slo-error-rate",
            category=PolicyCategory.SLO,
            resource_type="service",
            condition="slo_error_rate > 0.1",
            enforcement_action=EnforcementAction.AUDIT,
            severity="high",
            description="Audit high error rate services",
        ),
        PolicyRule(
            name="k8s-no-root",
            category=PolicyCategory.KUBERNETES,
            resource_type="pod",
            condition="container.run_as_root == true",
            enforcement_action=EnforcementAction.BLOCK_DEPLOY,
            severity="critical",
            description="Block pods running as root",
        ),
    ]

    for policy in policies:
        engine.register_policy(policy)

    # Evaluate against sample contexts
    print("\n=== Evaluating Context 1 (PASSing bucket) ===")
    context1 = PolicyContext(
        resource={
            "name": "secure-bucket",
            "public_access": False,
            "versioning": True,
            "encryption": True,
        },
        region="us-east-1",
        account_id="123456789012",
        effective_org_units=["finance"],
    )
    results = engine.evaluate_all_policies(context1)
    print(f"Results: {results}")

    print("\n=== Evaluating Context 2 (FAILing bucket) ===")
    context2 = PolicyContext(
        resource={
            "name": "public-bucket",
            "public_access": True,
            "versioning": False,
            "encryption": False,
        },
        region="us-east-1",
        account_id="123456789012",
        effective_org_units=["finance"],
    )
    results = engine.evaluate_all_policies(context2)
    print(f"Results: {results}")

    # Generate audit report
    engine.generate_audit_report("policy-audit-report.json")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())