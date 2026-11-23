#!/usr/bin/env python3
"""
AgentOps Control Plane

Governance layer for AI agents, enabling oversight, approval flows, and activity logging.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """State of an agent."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CONFIG_PENDING = "config_pending"


class AgentCapability(Enum):
    """What an agent can do."""
    OBSERVABILITY = "observability"
    RCA = "rca"
    INCIDENT_RESPONSE = "incident_response"
    AUTOMATION = "automation"
    GOVERNANCE = "governance"


@dataclass
class AgentConfig:
    """Agent configuration and governance settings."""
    agent_id: str
    name: str
    capability: AgentCapability
    allowed_actions: List[str]
    approvals_required: List[str]
    monitoring_level: str  # none, basic, full, audit
    activity_logging_level: str  # none, standard, detailed
    alerts_enabled: bool
    permissions: List[str]
    constraints: Dict[str, Any]
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None


@dataclass
class AgentExecution:
    """A single agent execution instance."""
    execution_id: str
    agent_id: str
    command: str
    parameters: Dict[str, Any]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    output: Optional[str] = None
    cost_estimated: float = 0.0
    tokens_consumed: int = 0
    error: Optional[str] = None


@dataclass
class AgentActivityLog:
    """Audit log for agent activity."""
    timestamp: datetime
    agent_id: str
    agent_name: str
    action: str
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]]
    cost: float
    tokens: int
    user: Optional[str]
    ip_address: Optional[str]


class AgentOpsControlPlane:
    """
    Centralized governance for AI SRE agents.

    Features:
    - Agent registration and configuration
    - Approval workflow enforcement
    - Monitoring and rate limiting
    - Activity auditing and compliance
    """

    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self.executions: List[AgentExecution] = []
        self.activity_logs: List[AgentActivityLog] = []
        self.approval_queue: List[Dict[str, Any]] = []

    async def register_agent(self, config: AgentConfig) -> bool:
        """Register a new agent with governance config."""
        if config.agent_id in self.agents:
            print(f"⚠️  Agent {config.agent_id} already registered")
            return False

        self.agents[config.agent_id] = config
        logger.info(f"Agent registered: {config.name} ({config.agent_id})")
        return True

    async def check_approval_requirements(
        self,
        agent_id: str,
        action: str,
        parameters: Dict[str, Any],
        user: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if an action requires approval.

        Returns:
            (allowed, optional reason)
        """
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        if action in agent.approvals_required:
            approval_key = f"{agent_id}:{action}:{datetime.utcnow().isoformat()}"
            self.approval_queue.append({
                "request_id": approval_key,
                "agent_id": agent_id,
                "action": action,
                "parameters": parameters,
                "requested_by": user,
                "timestamp": datetime.utcnow().isoformat(),
            })
            print(f"⏳ Action {action} requires approval")
            print(f"   Request ID: {approval_key}")
            return False, f"Requires approval for: {action}"

        return True, None

    async def execute_agent(
        self,
        agent_id: str,
        command: str,
        parameters: Dict[str, Any] = None,
        user: str = "system",
    ) -> AgentExecution:
        """
        Execute an agent command with governance checks.

        Returns:
            AgentExecution object with result
        """
        parameters = parameters or {}
        execution_id = f"auto-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{len(self.executions)}"

        execution = AgentExecution(
            execution_id=execution_id,
            agent_id=agent_id,
            command=command,
            parameters=parameters,
        )

        logger.info(f"Executing agent {agent_id}: {command}")

        # Check approval requirements
        approved, reason = await self.check_approval_requirements(
            agent_id, command, parameters, user
        )

        if not approved:
            execution.status = "rejected"
            execution.error = reason
            return execution

        execution.started_at = datetime.utcnow()
        execution.status = "running"

        # Simulate execution
        await asyncio.sleep(2)  # Simulate work

        # Generate mock output
        remaining_tokens = 4000 - len(str(parameters)) * 2
        execution.tokens_consumed = max(100, remaining_tokens)
        execution.cost_estimated = execution.tokens_consumed * 0.00001

        # Annotate with monitoring details
        if self.agents.get(agent_id).monitoring_level == "full":
            execution.output = f"Full monitoring output for {command}"

        execution.completed_at = datetime.utcnow()
        execution.status = "completed"

        # Log activity
        self._log_activity(
            agent_id,
            command,
            parameters,
            execution.output,
            execution.cost_estimated,
            execution.tokens_consumed,
            user,
        )

        return execution

    async def get_agent_status(self, agent_id: str) -> AgentConfig:
        """Get agent configuration."""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        return agent

    async def get_activitiy_log(
        self,
        agent_id: str = None,
        action: str = None,
        limit: int = 100,
    ) -> List[AgentActivityLog]:
        """
        Get agent activity log with filtering.

        Args:
            agent_id: Filter by agent ID
            action: Filter by action
            limit: Maximum number of entries

        Returns:
            List of activity log entries
        """
        logs = self.activity_logs

        if agent_id:
            logs = [l for l in logs if l.agent_id == agent_id]

        if action:
            logs = [l for l in logs if l.action == action]

        return logs[-limit:]

    def get_stats(self, agent_id: str = None) -> Dict[str, Any]:
        """
        Get governance statistics.

        Args:
            agent_id: Optional, filter by agent

        Returns:
            Statistics dict
        """
        if agent_id:
            agent_logs = [l for l in self.activity_logs if l.agent_id == agent_id]
        else:
            agent_logs = self.activity_logs

        total_executions = len(
            [e for e in self.executions if e.agent_id == (agent_id or "all")]
        )
        total_cost = sum(e.cost_estimated for e in self.executions)
        total_tokens = sum(e.tokens_consumed for e in self.executions)

        return {
            "total_executions": total_executions,
            "total_cost_estimate": total_cost,
            "total_tokens": total_tokens,
            "apglance_time_range": (
                min((l.timestamp for l in agent_logs), default=None),
                max((l.timestamp for l in agent_logs), default=None),
            ) if agent_logs else (None, None),
        }

    def _log_activity(
        self,
        agent_id: str,
        action: str,
        input_params: Dict[str, Any],
        output: Optional[str],
        cost: float,
        tokens: int,
        user: str,
    ):
        """Log an agent activity for auditing."""
        agent = self.agents.get(agent_id, {"name": "unknown"})

        log_entry = AgentActivityLog(
            timestamp=datetime.utcnow(),
            agent_id=agent_id,
            agent_name=agent.get("name", "unknown"),
            action=action,
            input=input_params,
            output={"summary": output} if output else None,
            cost=cost,
            tokens=tokens,
            user=user,
            ip_address=None,
        )

        self.activity_logs.append(log_entry)

        print(
            f"🤖 Agent Activity: [{user}] {agent.get('name')} executed {action} "
            f"({tokens} tokens, ${cost:.6f})"
        )

    def export_audit_report(self, output_path: str) -> bool:
        """Export activity log to file."""
        # Would be async in production
        import json
        from pathlib import Path
        from datetime import datetime

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_activities": len(self.activity_logs),
            "activities": [
                {
                    "timestamp": l.timestamp.isoformat(),
                    "agent_id": l.agent_id,
                    "agent_name": l.agent_name,
                    "action": l.action,
                    "input_summary": str(l.input)[:500],
                    "output_summary": str(l.output)[:500] if l.output else None,
                    "cost": l.cost,
                    "tokens": l.tokens,
                    "user": l.user,
                }
                for l in self.activity_logs
            ],
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            output_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Error exporting audit report: {e}")
            return False


async def main():
    """Demo: Run AgentOps control plane."""
    control_plane = AgentOpsControlPlane()

    # Register sample agents
    agents_to_register = [
        AgentConfig(
            agent_id="rca-agent-alpha",
            name="Symptom-to-Cause Analyzer",
            capability=AgentCapability.RCA,
            allowed_actions=["analyze", "aggregate", "rank_hypotheses"],
            approvals_required=["analyze", "aggregate"],
            monitoring_level="full",
            activity_logging_level="detailed",
            alerts_enabled=True,
            permissions=["k8s:read", "logs:read", "metrics:read"],
            constraints={
                "max_hypotheses": 5,
                "confidence_threshold": 0.6,
            },
        ),
        AgentConfig(
            agent_id="observability-agent-beta",
            name="Observability Scout",
            capability=AgentCapability.OBSERVABILITY,
            allowed_actions=["scan", "denoise", "aggregate"],
            approvals_required=[],
            monitoring_level="basic",
            activity_logging_level="standard",
            alerts_enabled=False,
            permissions=["logs:read", "metrics:write"],
            constraints={
                "operation_timeout": 300,
            },
        ),
    ]

    for agent_config in agents_to_register:
        await control_plane.register_agent(agent_config)

    # Execute agents with/approvals
    print("\n=== Testing Approved Agent (observability-agent-beta) ===")
    execution1 = await control_plane.execute_agent(
        agent_id="observability-agent-beta",
        command="scan_services",
        parameters={"namespace": "production"},
        user="demo-user",
    )
    print(f"Execution {execution1.execution_id} status: {execution1.status}")

    print("\n=== Testing Requires Approval Agent (rca-agent-alpha) ===")
    execution2 = await control_plane.execute_agent(
        agent_id="rca-agent-alpha",
        command="analyze_incident_x-12345",
        parameters={"incident_id": "x-12345"},
        user="demo-user",
    )
    print(f"Execution {execution2.execution_id} status: {execution2.status}")

    # Get stats
    print("\n=== Governance Statistics ===")
    stats = control_plane.get_stats()
    print(f"Total executions: {stats['total_executions']}")
    print(f"Estimated cost: ${stats['total_cost_estimate']:.6f}")
    print(f"Total tokens: {stats['total_tokens']}")

    # Export audit report
    control_plane.export_audit_report("agentops-audit-report.json")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())