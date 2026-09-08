"""
Agent Registry — Central catalog of all agents in the system.

Each agent has a unique ID, defined capabilities, resource requirements,
and performance SLAs. The orchestrator consults this registry when routing
messages and assigning tasks.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentCapability:
    """A single capability of an agent."""
    name: str
    description: str
    input_types: List[str] = field(default_factory=list)
    output_types: List[str] = field(default_factory=list)
    latency_ms: Optional[float] = None


@dataclass
class AgentResourceRequirements:
    """Resource requirements for an agent."""
    cpu_cores: float = 1.0
    memory_mb: float = 512.0
    max_concurrent_tasks: int = 10
    network_bandwidth_mbps: float = 100.0


@dataclass
class AgentSLA:
    """Service level agreement for an agent."""
    throughput_per_second: float = 10.0
    max_latency_ms: float = 1000.0
    availability_percent: float = 99.9
    max_error_rate: float = 0.01


@dataclass
class AgentDefinition:
    """Complete definition of an agent in the system."""
    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    resources: AgentResourceRequirements = field(default_factory=AgentResourceRequirements)
    sla: AgentSLA = field(default_factory=AgentSLA)
    constraints: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent Registry
# ---------------------------------------------------------------------------

class AgentRegistry:
    """Central registry of all agents in the compliance monitoring system."""

    def __init__(self):
        self._agents: Dict[str, AgentDefinition] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """Register the 4 primary agents + orchestrator."""

        self.register(AgentDefinition(
            agent_id="ORCH-001",
            name="Orchestrator",
            description="Central coordinator managing multi-agent workflows, routing, and consensus resolution.",
            capabilities=[
                AgentCapability("workflow_orchestration", "Manage multi-agent compliance workflows"),
                AgentCapability("message_routing", "Route messages between agents"),
                AgentCapability("conflict_resolution", "Resolve inter-agent conflicts"),
                AgentCapability("escalation_management", "Manage human-in-the-loop escalation"),
            ],
            resources=AgentResourceRequirements(cpu_cores=2.0, memory_mb=1024.0, max_concurrent_tasks=50),
        ))

        self.register(AgentDefinition(
            agent_id="TM-001",
            name="Transaction Monitor",
            description="Continuous surveillance of trading and financial transaction activity for compliance violations.",
            capabilities=[
                AgentCapability("pattern_detection", "Identify statistical anomalies in transaction data",
                               input_types=["transaction_batch"], output_types=["detection_event"]),
                AgentCapability("threshold_monitoring", "Monitor regulatory thresholds (position limits, SAR triggers)",
                               input_types=["transaction_batch"], output_types=["threshold_alert"]),
                AgentCapability("temporal_analysis", "Detect patterns across multiple time windows",
                               input_types=["transaction_history"], output_types=["temporal_pattern"]),
                AgentCapability("counterparty_analysis", "Identify unusual counterparty concentrations",
                               input_types=["transaction_batch", "counterparty_db"], output_types=["counterparty_alert"]),
                AgentCapability("cross_market_surveillance", "Detect correlated patterns across multiple markets",
                               input_types=["multi_venue_data"], output_types=["cross_market_alert"]),
            ],
            resources=AgentResourceRequirements(cpu_cores=4.0, memory_mb=2048.0, max_concurrent_tasks=20),
            sla=AgentSLA(throughput_per_second=1000.0, max_latency_ms=500.0, availability_percent=99.95),
            constraints=[
                "Cannot access raw customer communications (must rely on CS agent)",
                "Detection confidence scores must be calibrated against historical false positive rates",
                "Cannot issue trading halts autonomously",
                "Must maintain sub-second latency for real-time monitoring",
            ],
            dependencies=["CS-001"],
        ))

        self.register(AgentDefinition(
            agent_id="CS-001",
            name="Communication Scanner",
            description="Monitors all business communications for compliance violations across multiple channels and languages.",
            capabilities=[
                AgentCapability("keyword_detection", "Identify compliance-relevant keywords and code words",
                               input_types=["communication_batch"], output_types=["keyword_alert"]),
                AgentCapability("sentiment_intent_analysis", "Detect coercive language, misleading statements",
                               input_types=["communication_batch"], output_types=["sentiment_alert"]),
                AgentCapability("information_barrier_monitoring", "Detect Chinese wall breaches",
                               input_types=["cross_department_comms"], output_types=["barrier_alert"]),
                AgentCapability("record_keeping_compliance", "Verify regulated communications are captured",
                               input_types=["communication_metadata"], output_types=["recordKeeping_alert"]),
                AgentCapability("privilege_detection", "Identify potentially privileged communications",
                               input_types=["communication_batch"], output_types=["privilege_alert"]),
            ],
            resources=AgentResourceRequirements(cpu_cores=4.0, memory_mb=2048.0, max_concurrent_tasks=20),
            sla=AgentSLA(throughput_per_second=500.0, max_latency_ms=2000.0, availability_percent=99.9),
            constraints=[
                "Cannot decrypt end-to-end encrypted communications",
                "Voice analysis limited to transcribed text",
                "Must respect data retention boundaries",
                "Cannot independently determine legal privilege",
                "Privacy-preserving analysis for personal communications",
            ],
            dependencies=["RU-001"],
        ))

        self.register(AgentDefinition(
            agent_id="RU-001",
            name="Regulatory Update Tracker",
            description="Continuous monitoring of regulatory landscape across all operating jurisdictions.",
            capabilities=[
                AgentCapability("regulatory_feed_monitoring", "Monitor regulatory body publications",
                               input_types=["regulatory_feed"], output_types=["regulatory_update"]),
                AgentCapability("impact_assessment", "Assess impact of regulatory changes on existing policies",
                               input_types=["regulatory_update", "policy_db"], output_types=["impact_report"]),
                AgentCapability("timeline_extraction", "Extract implementation deadlines from regulations",
                               input_types=["regulatory_text"], output_types=["deadline_schedule"]),
                AgentCapability("cross_regulation_conflict", "Identify conflicts between jurisdictions",
                               input_types=["multiple_regulations"], output_types=["conflict_alert"]),
                AgentCapability("precedent_analysis", "Analyze enforcement actions to calibrate thresholds",
                               input_types=["enforcement_db"], output_types=["threshold_recommendation"]),
            ],
            resources=AgentResourceRequirements(cpu_cores=2.0, memory_mb=1024.0, max_concurrent_tasks=10),
            sla=AgentSLA(throughput_per_second=50.0, max_latency_ms=5000.0, availability_percent=99.5),
            constraints=[
                "Cannot provide legal interpretations of ambiguous regulatory language",
                "Impact assessments are preliminary and require human validation",
                "Cannot independently modify compliance rules",
                "Coverage limited to official sources",
            ],
            dependencies=[],
        ))

        self.register(AgentDefinition(
            agent_id="RG-001",
            name="Report Generator",
            description="Compiles, formats, and distributes compliance reports for multiple stakeholders.",
            capabilities=[
                AgentCapability("scheduled_reports", "Automated daily/weekly/monthly/quarterly/annual reports",
                               input_types=["compliance_data"], output_types=["formatted_report"]),
                AgentCapability("event_triggered_reporting", "Immediate report for critical events (SAR/STR)",
                               input_types=["detection_event", "escalation_decision"], output_types=["sareport"]),
                AgentCapability("multi_audience_adaptation", "Adjust detail and format per target audience",
                               input_types=["report_content", "audience_profile"], output_types=["adapted_report"]),
                AgentCapability("evidence_compilation", "Compile supporting evidence with source attribution",
                               input_types=["evidence_list"], output_types=["evidence_package"]),
                AgentCapability("regulatory_filing_preparation", "Generate filing drafts (XBRL, XML, PDF)",
                               input_types=["filing_data", "filing_template"], output_types=["filing_draft"]),
            ],
            resources=AgentResourceRequirements(cpu_cores=2.0, memory_mb=1024.0, max_concurrent_tasks=10),
            sla=AgentSLA(throughput_per_second=10.0, max_latency_ms=10000.0, availability_percent=99.5),
            constraints=[
                "Cannot file regulatory reports without human authorisation (dual sign-off required)",
                "Report templates must be version-controlled",
                "Cannot include privileged materials without legal clearance",
                "Distribution lists are controlled",
            ],
            dependencies=["TM-001", "CS-001", "RU-001"],
        ))

    def register(self, agent: AgentDefinition):
        """Register an agent."""
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> Optional[AgentDefinition]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[AgentDefinition]:
        """List all registered agents."""
        return list(self._agents.values())

    def get_capabilities_matrix(self) -> Dict[str, List[str]]:
        """Get a capability matrix: agent_id → list of capability names."""
        return {
            agent_id: [c.name for c in agent.capabilities]
            for agent_id, agent in self._agents.items()
        }

    def get_agent_pairs(self) -> List[Dict[str, Any]]:
        """Get all agent pairs with their shared boundaries."""
        agents = self.list_agents()
        pairs = []
        for i, a1 in enumerate(agents):
            for a2 in agents[i + 1:]:
                shared_inputs = set()
                for c1 in a1.capabilities:
                    for c2 in a2.capabilities:
                        overlap = set(c1.output_types) & set(c2.input_types)
                        shared_inputs.update(overlap)
                pairs.append({
                    "agent_pair": [a1.agent_id, a2.agent_id],
                    "shared_data_types": list(shared_inputs),
                    "a1_can_reach_a2": a2.agent_id in a1.dependencies,
                    "a2_can_reach_a1": a1.agent_id in a2.dependencies,
                })
        return pairs

    def to_markdown(self) -> str:
        """Generate a markdown representation of the registry."""
        lines = ["# Agent Registry\n"]
        for agent in self.list_agents():
            lines.append(f"## {agent.name} ({agent.agent_id})\n")
            lines.append(f"**Description:** {agent.description}\n")
            lines.append("**Capabilities:**\n")
            for cap in agent.capabilities:
                lines.append(f"- **{cap.name}:** {cap.description}")
            lines.append(f"\n**Constraints:**\n")
            for constraint in agent.constraints:
                lines.append(f"- {constraint}")
            lines.append(f"\n**SLA:** {agent.sla.throughput_per_second}/s, "
                        f"max {agent.sla.max_latency_ms}ms latency, "
                        f"{agent.sla.availability_percent}% availability\n")
            lines.append("---\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
