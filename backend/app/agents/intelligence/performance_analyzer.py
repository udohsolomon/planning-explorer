"""
Performance Analyzer - Learning and Optimization System

Analyzes agent performance and learns from past executions:
- Track execution metrics
- Identify optimization opportunities
- Learn from successes and failures
- Recommend improvements
- Predict task duration and complexity
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.orchestrator_agent import WorkflowResult, AgentRole


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    EXECUTION_TIME = "execution_time"
    TOKEN_USAGE = "token_usage"
    COST = "cost"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    QUALITY_SCORE = "quality_score"


@dataclass
class ExecutionMetrics:
    """Metrics from a single execution"""
    workflow_id: str
    timestamp: datetime
    agent_role: AgentRole
    task_id: str
    execution_time_seconds: float
    tokens_used: int = 0
    cost_usd: float = 0.0
    success: bool = True
    quality_score: float = 0.8
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceInsight:
    """Insight from performance analysis"""
    insight_type: str
    severity: str  # "info", "warning", "critical"
    title: str
    description: str
    recommendation: str
    affected_agents: List[AgentRole] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    category: str
    priority: str  # "high", "medium", "low"
    title: str
    current_state: str
    proposed_change: str
    expected_improvement: str
    implementation_effort: str
    estimated_savings: Dict[str, float] = field(default_factory=dict)


class PerformanceAnalyzer:
    """
    Learning and optimization system for autonomous agents.

    Capabilities:
    - Track execution metrics
    - Identify performance patterns
    - Learn from past executions
    - Recommend optimizations
    - Predict task complexity
    - Estimate costs and duration
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize performance analyzer.

        Args:
            llm_client: LLM client for analysis
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

        # Metrics storage
        self.execution_history: List[ExecutionMetrics] = []

        # Insights cache
        self.insights: List[PerformanceInsight] = []

        # Agent performance tracking
        self.agent_stats: Dict[AgentRole, Dict[str, Any]] = defaultdict(
            lambda: {
                "total_executions": 0,
                "total_time": 0.0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "successes": 0,
                "failures": 0,
                "average_quality": 0.0,
            }
        )

    async def record_execution(
        self,
        workflow_result: WorkflowResult,
        detailed_metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record execution metrics from workflow result.

        Args:
            workflow_result: Result from workflow execution
            detailed_metrics: Optional detailed metrics
        """
        logger.info(f"Recording execution metrics for workflow: {workflow_result.workflow_id}")

        # Extract metrics from each task result
        for task_id, task_result in workflow_result.task_results.items():
            agent_role_str = task_result.get("agent", "backend")

            try:
                agent_role = AgentRole[agent_role_str.upper()]
            except (KeyError, AttributeError):
                agent_role = AgentRole.BACKEND

            # Extract execution time
            exec_time = task_result.get("execution_time", 0.0)
            if isinstance(exec_time, str):
                try:
                    exec_time = float(exec_time)
                except ValueError:
                    exec_time = 0.0

            # Create execution metrics
            metrics = ExecutionMetrics(
                workflow_id=workflow_result.workflow_id,
                timestamp=datetime.now(),
                agent_role=agent_role,
                task_id=task_id,
                execution_time_seconds=exec_time,
                tokens_used=task_result.get("tokens_used", 0),
                cost_usd=task_result.get("cost", 0.0),
                success=task_result.get("status") == "completed",
                quality_score=task_result.get("quality_score", 0.8),
                error_message=task_result.get("error"),
                metadata=detailed_metrics or {}
            )

            self.execution_history.append(metrics)

            # Update agent stats
            stats = self.agent_stats[agent_role]
            stats["total_executions"] += 1
            stats["total_time"] += metrics.execution_time_seconds
            stats["total_cost"] += metrics.cost_usd
            stats["total_tokens"] += metrics.tokens_used

            if metrics.success:
                stats["successes"] += 1
            else:
                stats["failures"] += 1

            # Update average quality
            prev_avg = stats["average_quality"]
            n = stats["total_executions"]
            stats["average_quality"] = (prev_avg * (n - 1) + metrics.quality_score) / n

        logger.info(f"Recorded {len(workflow_result.task_results)} execution metrics")

    async def analyze_performance(
        self,
        time_window_hours: int = 24
    ) -> List[PerformanceInsight]:
        """
        Analyze performance and generate insights.

        Args:
            time_window_hours: Time window for analysis

        Returns:
            List of performance insights
        """
        logger.info(f"Analyzing performance over last {time_window_hours} hours")

        # Filter metrics to time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        recent_metrics = [
            m for m in self.execution_history
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            logger.info("No recent metrics to analyze")
            return []

        # Analyze with LLM
        metrics_summary = self._summarize_metrics(recent_metrics)

        prompt = f"""Analyze these agent performance metrics and provide insights:

{json.dumps(metrics_summary, indent=2)}

Identify:
1. Performance bottlenecks
2. Cost optimization opportunities
3. Quality issues
4. Unusual patterns or anomalies
5. Best performing agents/patterns

For each insight, provide:
- Type (bottleneck, cost, quality, anomaly, best_practice)
- Severity (info, warning, critical)
- Clear title and description
- Actionable recommendation
- Affected agents
- Relevant metrics

Return JSON array of insights:
[
  {{
    "insight_type": "...",
    "severity": "warning",
    "title": "...",
    "description": "...",
    "recommendation": "...",
    "affected_agents": ["backend_engineer"],
    "metrics": {{"average_time": 45.2, "cost": 0.15}}
  }}
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at analyzing software system performance.",
            model=self.model,
            temperature=0.3
        )

        # Parse insights
        try:
            insights_data = json.loads(response.content)

            insights = []
            for insight_data in insights_data:
                # Convert agent names to roles
                affected_agents = []
                for agent_name in insight_data.get("affected_agents", []):
                    try:
                        role = AgentRole[agent_name.upper()]
                        affected_agents.append(role)
                    except (KeyError, AttributeError):
                        pass

                insight = PerformanceInsight(
                    insight_type=insight_data.get("insight_type", "general"),
                    severity=insight_data.get("severity", "info"),
                    title=insight_data.get("title", ""),
                    description=insight_data.get("description", ""),
                    recommendation=insight_data.get("recommendation", ""),
                    affected_agents=affected_agents,
                    metrics=insight_data.get("metrics", {})
                )

                insights.append(insight)

            # Cache insights
            self.insights = insights

            logger.info(f"Generated {len(insights)} performance insights")

            return insights

        except json.JSONDecodeError:
            logger.warning("Failed to parse insights JSON")
            return []

    async def get_optimization_recommendations(
        self,
        focus_areas: Optional[List[str]] = None
    ) -> List[OptimizationRecommendation]:
        """
        Get optimization recommendations based on performance data.

        Args:
            focus_areas: Optional focus areas (cost, speed, quality)

        Returns:
            List of optimization recommendations
        """
        logger.info("Generating optimization recommendations")

        focus_areas = focus_areas or ["cost", "speed", "quality"]

        # Get current performance summary
        summary = self.get_performance_summary()

        prompt = f"""Based on this agent system performance data, provide optimization recommendations:

Current Performance:
{json.dumps(summary, indent=2)}

Focus areas: {", ".join(focus_areas)}

For each recommendation, provide:
- Category (prompt_optimization, caching, model_selection, architecture, workflow_design)
- Priority (high, medium, low)
- Title
- Current state description
- Proposed change
- Expected improvement
- Implementation effort (low, medium, high)
- Estimated savings (cost_usd, time_seconds, tokens)

Return JSON array of recommendations:
[
  {{
    "category": "caching",
    "priority": "high",
    "title": "Implement prompt caching",
    "current_state": "No caching enabled",
    "proposed_change": "Enable prompt caching for repeated prompts",
    "expected_improvement": "50% reduction in input tokens",
    "implementation_effort": "low",
    "estimated_savings": {{"cost_usd": 0.50, "tokens": 50000}}
  }}
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at optimizing AI agent systems for cost and performance.",
            model=self.model,
            temperature=0.4
        )

        # Parse recommendations
        try:
            recs_data = json.loads(response.content)

            recommendations = []
            for rec_data in recs_data:
                rec = OptimizationRecommendation(
                    category=rec_data.get("category", "general"),
                    priority=rec_data.get("priority", "medium"),
                    title=rec_data.get("title", ""),
                    current_state=rec_data.get("current_state", ""),
                    proposed_change=rec_data.get("proposed_change", ""),
                    expected_improvement=rec_data.get("expected_improvement", ""),
                    implementation_effort=rec_data.get("implementation_effort", "medium"),
                    estimated_savings=rec_data.get("estimated_savings", {})
                )

                recommendations.append(rec)

            logger.info(f"Generated {len(recommendations)} optimization recommendations")

            return recommendations

        except json.JSONDecodeError:
            logger.warning("Failed to parse recommendations JSON")
            return []

    async def predict_task_metrics(
        self,
        task_description: str,
        agent_role: AgentRole,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        Predict execution metrics for a task.

        Args:
            task_description: Task description
            agent_role: Agent role
            context: Optional task context

        Returns:
            Predicted metrics (duration, cost, tokens, quality)
        """
        logger.info(f"Predicting metrics for {agent_role.value} task")

        # Get historical data for this agent
        agent_history = [
            m for m in self.execution_history
            if m.agent_role == agent_role
        ]

        if not agent_history:
            # No history, return defaults
            return {
                "duration_seconds": 30.0,
                "cost_usd": 0.05,
                "tokens": 5000,
                "quality_score": 0.8,
                "confidence": 0.3
            }

        # Calculate historical averages
        avg_time = sum(m.execution_time_seconds for m in agent_history) / len(agent_history)
        avg_cost = sum(m.cost_usd for m in agent_history) / len(agent_history)
        avg_tokens = sum(m.tokens_used for m in agent_history) / len(agent_history)
        avg_quality = sum(m.quality_score for m in agent_history) / len(agent_history)

        # Use LLM to refine prediction based on task
        prompt = f"""Predict execution metrics for this task:

Task: {task_description}
Agent: {agent_role.value}
Context: {json.dumps(context or {}, indent=2)}

Historical averages for this agent:
- Average duration: {avg_time:.1f} seconds
- Average cost: ${avg_cost:.4f}
- Average tokens: {avg_tokens:.0f}
- Average quality: {avg_quality:.2f}

Based on task complexity and historical data, predict:
- duration_seconds: How long will this take?
- cost_usd: How much will it cost?
- tokens: How many tokens will be used?
- quality_score: Expected quality (0-1)
- confidence: Prediction confidence (0-1)

Return JSON:
{{
  "duration_seconds": 45.0,
  "cost_usd": 0.08,
  "tokens": 8000,
  "quality_score": 0.85,
  "confidence": 0.75
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at predicting software task metrics.",
            model=self.model,
            temperature=0.3
        )

        try:
            predictions = json.loads(response.content)
            return predictions

        except json.JSONDecodeError:
            # Fallback to historical averages
            return {
                "duration_seconds": avg_time,
                "cost_usd": avg_cost,
                "tokens": avg_tokens,
                "quality_score": avg_quality,
                "confidence": 0.6
            }

    async def identify_patterns(
        self,
        pattern_type: str = "success"
    ) -> List[Dict[str, Any]]:
        """
        Identify patterns in execution history.

        Args:
            pattern_type: Type of pattern (success, failure, cost, speed)

        Returns:
            List of identified patterns
        """
        logger.info(f"Identifying {pattern_type} patterns")

        if not self.execution_history:
            return []

        # Prepare data summary
        metrics_by_agent = defaultdict(list)
        for metric in self.execution_history:
            metrics_by_agent[metric.agent_role.value].append({
                "task_id": metric.task_id,
                "execution_time": metric.execution_time_seconds,
                "cost": metric.cost_usd,
                "tokens": metric.tokens_used,
                "success": metric.success,
                "quality": metric.quality_score
            })

        prompt = f"""Identify {pattern_type} patterns in this execution data:

{json.dumps(dict(metrics_by_agent), indent=2)}

Look for:
- Common characteristics of {pattern_type} executions
- Conditions that lead to {pattern_type}
- Agent combinations that work well
- Task types that perform best/worst
- Time-of-day or sequencing effects

Return JSON array of patterns:
[
  {{
    "pattern": "description of pattern",
    "frequency": "how often it occurs",
    "impact": "what effect it has",
    "recommendation": "how to leverage/avoid"
  }}
]"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at pattern recognition in software systems.",
            model=self.model,
            temperature=0.4
        )

        try:
            patterns = json.loads(response.content)
            logger.info(f"Identified {len(patterns)} patterns")
            return patterns

        except json.JSONDecodeError:
            logger.warning("Failed to parse patterns JSON")
            return []

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        if not self.execution_history:
            return {"total_executions": 0}

        total_executions = len(self.execution_history)
        total_time = sum(m.execution_time_seconds for m in self.execution_history)
        total_cost = sum(m.cost_usd for m in self.execution_history)
        total_tokens = sum(m.tokens_used for m in self.execution_history)

        successes = sum(1 for m in self.execution_history if m.success)
        success_rate = successes / total_executions if total_executions > 0 else 0

        avg_quality = sum(m.quality_score for m in self.execution_history) / total_executions

        # By-agent stats
        agent_summary = {}
        for agent_role, stats in self.agent_stats.items():
            agent_summary[agent_role.value] = {
                "executions": stats["total_executions"],
                "avg_time": stats["total_time"] / stats["total_executions"] if stats["total_executions"] > 0 else 0,
                "total_cost": stats["total_cost"],
                "success_rate": stats["successes"] / stats["total_executions"] if stats["total_executions"] > 0 else 0,
                "avg_quality": stats["average_quality"]
            }

        return {
            "total_executions": total_executions,
            "total_time_seconds": total_time,
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "success_rate": success_rate,
            "average_quality": avg_quality,
            "average_time_per_execution": total_time / total_executions,
            "average_cost_per_execution": total_cost / total_executions,
            "by_agent": agent_summary
        }

    def get_agent_leaderboard(
        self,
        metric: MetricType = MetricType.SUCCESS_RATE
    ) -> List[Tuple[AgentRole, float]]:
        """
        Get agent leaderboard by metric.

        Args:
            metric: Metric to rank by

        Returns:
            List of (agent_role, score) tuples, sorted
        """
        scores = []

        for agent_role, stats in self.agent_stats.items():
            if stats["total_executions"] == 0:
                continue

            if metric == MetricType.SUCCESS_RATE:
                score = stats["successes"] / stats["total_executions"]
            elif metric == MetricType.EXECUTION_TIME:
                score = stats["total_time"] / stats["total_executions"]
            elif metric == MetricType.COST:
                score = stats["total_cost"] / stats["total_executions"]
            elif metric == MetricType.QUALITY_SCORE:
                score = stats["average_quality"]
            else:
                score = 0.0

            scores.append((agent_role, score))

        # Sort by score (descending for success_rate/quality, ascending for time/cost)
        reverse = metric in [MetricType.SUCCESS_RATE, MetricType.QUALITY_SCORE]
        scores.sort(key=lambda x: x[1], reverse=reverse)

        return scores

    def _summarize_metrics(
        self,
        metrics: List[ExecutionMetrics]
    ) -> Dict[str, Any]:
        """Summarize metrics for LLM analysis"""
        if not metrics:
            return {}

        by_agent = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "successes": 0,
            "failures": 0,
            "quality_scores": []
        })

        for metric in metrics:
            agent = metric.agent_role.value
            data = by_agent[agent]

            data["count"] += 1
            data["total_time"] += metric.execution_time_seconds
            data["total_cost"] += metric.cost_usd
            data["total_tokens"] += metric.tokens_used
            data["quality_scores"].append(metric.quality_score)

            if metric.success:
                data["successes"] += 1
            else:
                data["failures"] += 1

        # Calculate averages
        summary = {}
        for agent, data in by_agent.items():
            summary[agent] = {
                "total_executions": data["count"],
                "avg_time_seconds": data["total_time"] / data["count"],
                "total_cost_usd": data["total_cost"],
                "avg_cost_usd": data["total_cost"] / data["count"],
                "total_tokens": data["total_tokens"],
                "success_rate": data["successes"] / data["count"],
                "avg_quality": sum(data["quality_scores"]) / len(data["quality_scores"]) if data["quality_scores"] else 0
            }

        return summary

    def clear_history(self, older_than_hours: Optional[int] = None) -> int:
        """
        Clear execution history.

        Args:
            older_than_hours: Only clear records older than this

        Returns:
            Number of records cleared
        """
        if older_than_hours is None:
            count = len(self.execution_history)
            self.execution_history.clear()
            self.agent_stats.clear()
            self.insights.clear()
            logger.info(f"Cleared all {count} execution records")
            return count

        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)

        original_count = len(self.execution_history)
        self.execution_history = [
            m for m in self.execution_history
            if m.timestamp >= cutoff_time
        ]
        cleared = original_count - len(self.execution_history)

        logger.info(f"Cleared {cleared} execution records older than {older_than_hours}h")

        return cleared
