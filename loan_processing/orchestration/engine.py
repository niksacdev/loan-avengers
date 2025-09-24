"""
Orchestration engine for executing multi-agent loan processing workflows.

This module implements the configuration-driven orchestration architecture
from ADR-005, supporting dynamic pattern execution without hardcoded handoffs.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel

from loan_processing.agents.registry import get_global_registry
from loan_processing.models.application import LoanApplication
from loan_processing.models.assessment import ComprehensiveAssessment
from loan_processing.models.decision import LoanDecision, LoanDecisionStatus

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """Supported orchestration pattern types."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    COLLABORATIVE = "collaborative"  # Future implementation


class AgentExecutionStatus(str, Enum):
    """Status of agent execution within a pattern."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class OrchestrationContext(BaseModel):
    """
    Shared context that evolves through the workflow execution.

    This context accumulates results as agents complete their assessments,
    providing a comprehensive view for subsequent agents and final decision making.
    """
    application: LoanApplication
    pattern_name: str
    started_at: datetime
    current_agent: Optional[str] = None

    # Agent execution results
    agent_results: Dict[str, Dict[str, Any]] = {}
    agent_statuses: Dict[str, AgentExecutionStatus] = {}

    # Comprehensive assessment state
    comprehensive_assessment: Optional[ComprehensiveAssessment] = None

    # Processing metadata
    audit_trail: List[str] = []
    processing_errors: List[str] = []
    total_processing_time: float = 0.0
    agents_involved: List[str] = []

    def add_agent_result(self, agent_name: str, result: Dict[str, Any]) -> None:
        """Add result from an agent execution."""
        self.agent_results[agent_name] = result
        self.agent_statuses[agent_name] = AgentExecutionStatus.COMPLETED
        if agent_name not in self.agents_involved:
            self.agents_involved.append(agent_name)

        audit_message = f"Agent {agent_name} completed assessment"
        self.audit_trail.append(audit_message)
        logger.info(audit_message)

    def mark_agent_failed(self, agent_name: str, error: str) -> None:
        """Mark an agent execution as failed."""
        self.agent_statuses[agent_name] = AgentExecutionStatus.FAILED
        error_message = f"Agent {agent_name} failed: {error}"
        self.processing_errors.append(error_message)
        self.audit_trail.append(error_message)
        logger.error(error_message)

    def get_context_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get relevant context for a specific agent."""
        return {
            "application": self.application.dict(),
            "previous_results": self.agent_results,
            "pattern": self.pattern_name,
            "current_agent": agent_name,
            "audit_trail": self.audit_trail[-5:]  # Last 5 entries for context
        }


class WorkflowPattern(BaseModel):
    """Configuration for a specific orchestration pattern."""
    name: str
    pattern_type: PatternType
    description: Optional[str] = None
    timeout_seconds: int = 600

    # Pattern-specific configuration
    agents: List[Dict[str, Any]] = []
    handoff_rules: List[Dict[str, Any]] = []
    parallel_branches: List[Dict[str, Any]] = []
    success_conditions: List[str] = []
    failure_conditions: List[str] = []


class OrchestrationEngine:
    """
    Dynamic orchestration engine supporting multiple workflow patterns.

    Implements the configuration-driven approach from ADR-005, allowing
    dynamic execution of different patterns without code changes.
    """

    def __init__(self):
        """Initialize the orchestration engine."""
        self._patterns: Dict[str, WorkflowPattern] = {}
        self._pattern_cache: Dict[str, WorkflowPattern] = {}

    async def load_patterns_from_directory(self, patterns_dir: str) -> None:
        """
        Load workflow patterns from YAML files in a directory.

        Args:
            patterns_dir: Directory containing pattern YAML files
        """
        import os
        from pathlib import Path

        pattern_dir = Path(patterns_dir)
        if not pattern_dir.exists():
            logger.warning(f"Pattern directory does not exist: {patterns_dir}")
            return

        for pattern_file in pattern_dir.glob("*.yaml"):
            if pattern_file.name == "agents.yaml":  # Skip agent config
                continue

            try:
                with open(pattern_file, 'r') as f:
                    pattern_data = yaml.safe_load(f)

                pattern = WorkflowPattern(**pattern_data)
                self._patterns[pattern.name] = pattern

                logger.info(f"Loaded pattern: {pattern.name} ({pattern.pattern_type})")

            except Exception as e:
                logger.error(f"Failed to load pattern from {pattern_file}: {e}")

    def get_available_patterns(self) -> List[str]:
        """Get list of available pattern names."""
        return list(self._patterns.keys())

    def get_pattern_info(self, pattern_name: str) -> Dict[str, Any]:
        """Get information about a specific pattern."""
        if pattern_name not in self._patterns:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        pattern = self._patterns[pattern_name]
        return {
            "name": pattern.name,
            "type": pattern.pattern_type,
            "description": pattern.description,
            "agents": [agent.get("type") for agent in pattern.agents],
            "timeout_seconds": pattern.timeout_seconds
        }

    async def execute_pattern(
        self,
        pattern_name: str,
        application: LoanApplication,
        context: Optional[Dict[str, Any]] = None
    ) -> LoanDecision:
        """
        Execute a specific orchestration pattern.

        Args:
            pattern_name: Name of the pattern to execute
            application: Loan application to process
            context: Optional additional context

        Returns:
            LoanDecision: Final loan decision

        Raises:
            ValueError: If pattern is not found
            RuntimeError: If pattern execution fails
        """
        if pattern_name not in self._patterns:
            raise ValueError(f"Unknown pattern: {pattern_name}")

        pattern = self._patterns[pattern_name]

        # Create orchestration context
        orchestration_context = OrchestrationContext(
            application=application,
            pattern_name=pattern_name,
            started_at=datetime.utcnow()
        )

        logger.info(f"Starting pattern execution: {pattern_name} for application {application.application_id}")

        try:
            # Execute pattern based on type
            if pattern.pattern_type == PatternType.SEQUENTIAL:
                await self._execute_sequential_pattern(pattern, orchestration_context)
            elif pattern.pattern_type == PatternType.PARALLEL:
                await self._execute_parallel_pattern(pattern, orchestration_context)
            elif pattern.pattern_type == PatternType.COLLABORATIVE:
                await self._execute_collaborative_pattern(pattern, orchestration_context)
            else:
                raise RuntimeError(f"Unsupported pattern type: {pattern.pattern_type}")

            # Generate final decision
            decision = await self._generate_final_decision(orchestration_context)

            logger.info(f"Pattern {pattern_name} completed successfully")
            return decision

        except Exception as e:
            logger.error(f"Pattern execution failed: {e}")
            orchestration_context.mark_agent_failed("orchestrator", str(e))

            # Generate failure decision
            return await self._generate_failure_decision(orchestration_context, str(e))

    async def _execute_sequential_pattern(
        self,
        pattern: WorkflowPattern,
        context: OrchestrationContext
    ) -> None:
        """Execute agents in sequential order with handoff conditions."""
        registry = get_global_registry()

        for agent_config in pattern.agents:
            agent_type = agent_config["type"]
            context.current_agent = agent_type
            context.agent_statuses[agent_type] = AgentExecutionStatus.RUNNING

            try:
                # Create agent instance
                agent = await registry.create_agent_with_tools(agent_type)

                # Execute agent assessment
                agent_context = context.get_context_for_agent(agent_type)
                result = await agent.assess_application(context.application, agent_context)

                # Store result
                context.add_agent_result(agent_type, result.dict())

                # Check handoff conditions
                if not await self._evaluate_handoff_conditions(pattern, agent_type, context):
                    logger.info(f"Handoff conditions not met, stopping at {agent_type}")
                    break

            except Exception as e:
                context.mark_agent_failed(agent_type, str(e))
                # Continue with remaining agents depending on error handling strategy
                continue

    async def _execute_parallel_pattern(
        self,
        pattern: WorkflowPattern,
        context: OrchestrationContext
    ) -> None:
        """Execute agents in parallel branches."""
        registry = get_global_registry()
        tasks = []

        for branch in pattern.parallel_branches:
            branch_agents = branch.get("agents", [])
            for agent_config in branch_agents:
                task = self._execute_agent_async(agent_config, context, registry)
                tasks.append(task)

        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Parallel agent execution failed: {result}")

    async def _execute_collaborative_pattern(
        self,
        pattern: WorkflowPattern,
        context: OrchestrationContext
    ) -> None:
        """Execute agents with collaborative communication (future implementation)."""
        # Placeholder for future collaborative pattern implementation
        logger.warning("Collaborative pattern not yet implemented, falling back to sequential")
        await self._execute_sequential_pattern(pattern, context)

    async def _execute_agent_async(
        self,
        agent_config: Dict[str, Any],
        context: OrchestrationContext,
        registry
    ) -> None:
        """Execute a single agent asynchronously."""
        agent_type = agent_config["type"]
        context.agent_statuses[agent_type] = AgentExecutionStatus.RUNNING

        try:
            agent = await registry.create_agent_with_tools(agent_type)
            agent_context = context.get_context_for_agent(agent_type)
            result = await agent.assess_application(context.application, agent_context)
            context.add_agent_result(agent_type, result.dict())

        except Exception as e:
            context.mark_agent_failed(agent_type, str(e))

    async def _evaluate_handoff_conditions(
        self,
        pattern: WorkflowPattern,
        current_agent: str,
        context: OrchestrationContext
    ) -> bool:
        """Evaluate whether handoff conditions are met to continue to next agent."""
        # Find handoff rules for current agent
        for rule in pattern.handoff_rules:
            if rule.get("from") == current_agent:
                conditions = rule.get("conditions", [])

                # Evaluate each condition
                for condition in conditions:
                    if not await self._evaluate_condition(condition, context):
                        return False

        return True

    async def _evaluate_condition(self, condition: str, context: OrchestrationContext) -> bool:
        """Evaluate a single condition expression."""
        # Simple condition evaluation - can be enhanced with more sophisticated logic
        try:
            # Get current agent result
            current_agent = context.current_agent
            if current_agent not in context.agent_results:
                return False

            result = context.agent_results[current_agent]

            # Basic condition parsing and evaluation
            # This is a simplified implementation - production would use a proper expression evaluator
            if "validation_status" in condition and "validation_status" in result:
                if "== 'PASSED'" in condition:
                    return result["validation_status"] == "PASSED"
                elif "in ['PASSED', 'REQUIRES_REVIEW']" in condition:
                    return result["validation_status"] in ["PASSED", "REQUIRES_REVIEW"]

            return True  # Default to true if condition can't be evaluated

        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    async def _generate_final_decision(self, context: OrchestrationContext) -> LoanDecision:
        """Generate final loan decision from orchestration context."""
        # Calculate processing time
        processing_time = (datetime.utcnow() - context.started_at).total_seconds()

        # Determine decision based on agent results
        decision_status = LoanDecisionStatus.APPROVED
        decision_reason = "All assessments completed successfully"
        confidence = 0.85

        # Check for any failed agents
        failed_agents = [agent for agent, status in context.agent_statuses.items()
                        if status == AgentExecutionStatus.FAILED]

        if failed_agents:
            decision_status = LoanDecisionStatus.MANUAL_REVIEW
            decision_reason = f"Manual review required due to agent failures: {failed_agents}"
            confidence = 0.3

        # Extract risk factors and conditions from agent results
        risk_factors = []
        conditions = []

        for agent_name, result in context.agent_results.items():
            if "risk_factors" in result:
                risk_factors.extend(result["risk_factors"])
            if "conditions" in result:
                conditions.extend(result["conditions"])

        return LoanDecision(
            application_id=context.application.application_id,
            decision=decision_status,
            decision_reason=decision_reason,
            confidence_score=confidence,
            decision_maker="orchestration_engine",
            processing_duration_seconds=processing_time,
            agents_consulted=context.agents_involved,
            orchestration_pattern=context.pattern_name,
            reasoning=f"Processed through {context.pattern_name} pattern with {len(context.agents_involved)} agents",
            risk_factors=risk_factors,
            conditions=conditions
        )

    async def _generate_failure_decision(
        self,
        context: OrchestrationContext,
        error: str
    ) -> LoanDecision:
        """Generate decision for failed pattern execution."""
        processing_time = (datetime.utcnow() - context.started_at).total_seconds()

        return LoanDecision(
            application_id=context.application.application_id,
            decision=LoanDecisionStatus.MANUAL_REVIEW,
            decision_reason=f"Processing error: {error}",
            confidence_score=0.0,
            decision_maker="orchestration_engine",
            processing_duration_seconds=processing_time,
            agents_consulted=context.agents_involved,
            orchestration_pattern=context.pattern_name,
            reasoning=f"Pattern execution failed: {error}",
            review_required=True,
            review_priority="urgent"
        )


__all__ = [
    "OrchestrationEngine",
    "OrchestrationContext",
    "WorkflowPattern",
    "PatternType",
    "AgentExecutionStatus"
]