"""
Workflow Evaluator - Quality Assessment for Multi-Agent Workflows

Provides comprehensive evaluation of workflow execution:
- Task success rates
- Agent performance metrics
- Handoff quality
- Overall workflow quality
- Regression detection
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.agents.orchestrator_agent import (
    WorkflowResult,
    TaskResult,
    AgentRole
)


logger = logging.getLogger(__name__)


class QualityGrade(Enum):
    """Quality assessment grades"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"  # 75-89%
    FAIR = "fair"  # 60-74%
    POOR = "poor"  # <60%


@dataclass
class TaskEvaluation:
    """Evaluation of single task execution"""
    task_id: str
    agent_role: AgentRole
    success: bool
    execution_time: float
    quality_score: float  # 0-100
    metrics: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


@dataclass
class WorkflowEvaluation:
    """Comprehensive workflow evaluation"""
    workflow_id: str
    overall_success: bool
    quality_grade: QualityGrade
    overall_score: float  # 0-100
    task_evaluations: List[TaskEvaluation]
    performance_metrics: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class WorkflowEvaluator:
    """
    Evaluates multi-agent workflow execution quality.

    Assessment criteria:
    - Task success rate
    - Execution efficiency
    - Agent performance
    - Handoff quality
    - Error recovery
    - Overall completeness
    """

    def __init__(self):
        # Historical data for baseline comparison
        self.workflow_history: List[WorkflowEvaluation] = []

        # Quality thresholds
        self.thresholds = {
            "task_success_rate": 0.80,  # 80% minimum
            "execution_time_factor": 2.0,  # 2x baseline max
            "quality_score": 75.0,  # 75/100 minimum
            "handoff_success": 0.90  # 90% handoff success
        }

    async def evaluate_workflow(
        self,
        workflow_result: WorkflowResult
    ) -> WorkflowEvaluation:
        """
        Comprehensive workflow evaluation.

        Args:
            workflow_result: Result to evaluate

        Returns:
            WorkflowEvaluation with detailed assessment
        """
        logger.info(f"Evaluating workflow {workflow_result.workflow_id}")

        # Evaluate individual tasks
        task_evaluations = []

        for task_result in workflow_result.task_results:
            task_eval = await self._evaluate_task(task_result)
            task_evaluations.append(task_eval)

        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(
            workflow_result,
            task_evaluations
        )

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(
            workflow_result,
            task_evaluations
        )

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            performance_metrics,
            quality_metrics
        )

        # Determine grade
        quality_grade = self._determine_grade(overall_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            workflow_result,
            task_evaluations,
            performance_metrics,
            quality_metrics
        )

        # Create evaluation
        evaluation = WorkflowEvaluation(
            workflow_id=workflow_result.workflow_id,
            overall_success=workflow_result.success,
            quality_grade=quality_grade,
            overall_score=overall_score,
            task_evaluations=task_evaluations,
            performance_metrics=performance_metrics,
            quality_metrics=quality_metrics,
            recommendations=recommendations
        )

        # Store in history
        self.workflow_history.append(evaluation)

        logger.info(
            f"Workflow {workflow_result.workflow_id} evaluation complete: "
            f"{quality_grade.value} ({overall_score:.1f}/100)"
        )

        return evaluation

    async def _evaluate_task(
        self,
        task_result: TaskResult
    ) -> TaskEvaluation:
        """Evaluate individual task execution"""
        # Calculate quality score based on multiple factors
        quality_score = 0.0

        # Success factor (40%)
        if task_result.success:
            quality_score += 40.0

        # Execution time factor (20%)
        # Lower is better, baseline is 30s
        baseline_time = 30.0
        time_score = max(0, 20.0 * (1 - task_result.execution_time / baseline_time))
        quality_score += min(20.0, time_score)

        # Error handling factor (20%)
        if not task_result.errors:
            quality_score += 20.0
        elif len(task_result.errors) == 1:
            quality_score += 10.0

        # Output completeness factor (20%)
        if task_result.output:
            output_score = min(20.0, len(task_result.output) / 5 * 20.0)
            quality_score += output_score

        # Identify issues
        issues = []

        if not task_result.success:
            issues.append("Task failed to complete successfully")

        if task_result.errors:
            issues.append(f"{len(task_result.errors)} error(s) occurred")

        if task_result.execution_time > 60.0:
            issues.append(f"Slow execution: {task_result.execution_time:.1f}s")

        # Identify strengths
        strengths = []

        if task_result.success and task_result.execution_time < 10.0:
            strengths.append("Fast execution")

        if not task_result.errors and not task_result.warnings:
            strengths.append("Error-free execution")

        if task_result.output:
            strengths.append("Complete output generated")

        # Collect metrics
        metrics = {
            "execution_time": task_result.execution_time,
            "error_count": len(task_result.errors),
            "warning_count": len(task_result.warnings),
            "output_size": len(task_result.output) if task_result.output else 0
        }

        return TaskEvaluation(
            task_id=task_result.task_id,
            agent_role=task_result.agent_role,
            success=task_result.success,
            execution_time=task_result.execution_time,
            quality_score=quality_score,
            metrics=metrics,
            issues=issues,
            strengths=strengths
        )

    def _calculate_performance_metrics(
        self,
        workflow_result: WorkflowResult,
        task_evaluations: List[TaskEvaluation]
    ) -> Dict[str, Any]:
        """Calculate performance metrics"""
        total_tasks = len(task_evaluations)
        successful_tasks = sum(1 for t in task_evaluations if t.success)

        return {
            "total_execution_time": workflow_result.total_execution_time,
            "task_count": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": total_tasks - successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "average_task_time": (
                sum(t.execution_time for t in task_evaluations) / total_tasks
                if total_tasks > 0 else 0
            ),
            "max_task_time": (
                max(t.execution_time for t in task_evaluations)
                if task_evaluations else 0
            ),
            "min_task_time": (
                min(t.execution_time for t in task_evaluations)
                if task_evaluations else 0
            )
        }

    def _calculate_quality_metrics(
        self,
        workflow_result: WorkflowResult,
        task_evaluations: List[TaskEvaluation]
    ) -> Dict[str, Any]:
        """Calculate quality metrics"""
        total_tasks = len(task_evaluations)

        return {
            "average_quality_score": (
                sum(t.quality_score for t in task_evaluations) / total_tasks
                if total_tasks > 0 else 0
            ),
            "tasks_with_issues": sum(1 for t in task_evaluations if t.issues),
            "total_issues": sum(len(t.issues) for t in task_evaluations),
            "total_strengths": sum(len(t.strengths) for t in task_evaluations),
            "error_free_rate": (
                sum(1 for t in task_evaluations if not t.metrics.get("error_count", 1))
                / total_tasks
                if total_tasks > 0 else 0
            )
        }

    def _calculate_overall_score(
        self,
        performance_metrics: Dict[str, Any],
        quality_metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall workflow quality score"""
        # Weighted scoring
        scores = []

        # Success rate (30%)
        success_score = performance_metrics["success_rate"] * 100 * 0.30
        scores.append(success_score)

        # Average quality (40%)
        quality_score = quality_metrics["average_quality_score"] * 0.40
        scores.append(quality_score)

        # Error-free rate (20%)
        error_free_score = quality_metrics["error_free_rate"] * 100 * 0.20
        scores.append(error_free_score)

        # Execution efficiency (10%)
        # Penalize if average task time > 30s
        avg_time = performance_metrics["average_task_time"]
        efficiency_score = max(0, 10.0 * (1 - avg_time / 30.0))
        scores.append(efficiency_score)

        return sum(scores)

    def _determine_grade(self, overall_score: float) -> QualityGrade:
        """Determine quality grade from score"""
        if overall_score >= 90:
            return QualityGrade.EXCELLENT
        elif overall_score >= 75:
            return QualityGrade.GOOD
        elif overall_score >= 60:
            return QualityGrade.FAIR
        else:
            return QualityGrade.POOR

    def _generate_recommendations(
        self,
        workflow_result: WorkflowResult,
        task_evaluations: List[TaskEvaluation],
        performance_metrics: Dict[str, Any],
        quality_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        # Check success rate
        if performance_metrics["success_rate"] < self.thresholds["task_success_rate"]:
            recommendations.append(
                f"Task success rate ({performance_metrics['success_rate']*100:.1f}%) "
                f"is below threshold ({self.thresholds['task_success_rate']*100}%). "
                "Review failed tasks and implement better error handling."
            )

        # Check execution time
        if performance_metrics["average_task_time"] > 30.0:
            recommendations.append(
                f"Average task time ({performance_metrics['average_task_time']:.1f}s) "
                "is high. Consider optimizing slow agents or adding caching."
            )

        # Check quality score
        if quality_metrics["average_quality_score"] < self.thresholds["quality_score"]:
            recommendations.append(
                f"Average quality score ({quality_metrics['average_quality_score']:.1f}) "
                f"is below threshold ({self.thresholds['quality_score']}). "
                "Focus on improving agent output quality."
            )

        # Check for tasks with issues
        if quality_metrics["tasks_with_issues"] > 0:
            recommendations.append(
                f"{quality_metrics['tasks_with_issues']} task(s) had issues. "
                "Review task evaluations for specific problems."
            )

        # Agent-specific recommendations
        agent_performance = self._analyze_agent_performance(task_evaluations)

        for agent_role, perf in agent_performance.items():
            if perf["success_rate"] < 0.80:
                recommendations.append(
                    f"{agent_role.value} agent has low success rate "
                    f"({perf['success_rate']*100:.1f}%). "
                    "Review and improve agent implementation."
                )

        if not recommendations:
            recommendations.append("Workflow execution meets all quality standards.")

        return recommendations

    def _analyze_agent_performance(
        self,
        task_evaluations: List[TaskEvaluation]
    ) -> Dict[AgentRole, Dict[str, Any]]:
        """Analyze performance by agent"""
        agent_stats = {}

        for eval in task_evaluations:
            if eval.agent_role not in agent_stats:
                agent_stats[eval.agent_role] = {
                    "total": 0,
                    "successful": 0,
                    "total_time": 0.0,
                    "quality_scores": []
                }

            stats = agent_stats[eval.agent_role]
            stats["total"] += 1

            if eval.success:
                stats["successful"] += 1

            stats["total_time"] += eval.execution_time
            stats["quality_scores"].append(eval.quality_score)

        # Calculate metrics
        result = {}

        for agent_role, stats in agent_stats.items():
            result[agent_role] = {
                "total_tasks": stats["total"],
                "success_rate": stats["successful"] / stats["total"],
                "average_time": stats["total_time"] / stats["total"],
                "average_quality": (
                    sum(stats["quality_scores"]) / len(stats["quality_scores"])
                )
            }

        return result

    def get_evaluation_summary(
        self,
        workflow_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get evaluation summary for workflow"""
        evaluation = next(
            (e for e in self.workflow_history if e.workflow_id == workflow_id),
            None
        )

        if not evaluation:
            return None

        return {
            "workflow_id": evaluation.workflow_id,
            "grade": evaluation.quality_grade.value,
            "score": evaluation.overall_score,
            "success": evaluation.overall_success,
            "task_count": len(evaluation.task_evaluations),
            "performance": evaluation.performance_metrics,
            "quality": evaluation.quality_metrics,
            "recommendations": evaluation.recommendations,
            "timestamp": evaluation.timestamp.isoformat()
        }

    def detect_regression(
        self,
        current_evaluation: WorkflowEvaluation,
        baseline_count: int = 5
    ) -> Dict[str, Any]:
        """
        Detect performance regression.

        Args:
            current_evaluation: Current evaluation
            baseline_count: Number of previous runs for baseline

        Returns:
            Regression analysis
        """
        # Get recent evaluations (excluding current)
        recent_evals = [
            e for e in self.workflow_history[-baseline_count-1:-1]
            if e.workflow_id != current_evaluation.workflow_id
        ]

        if not recent_evals:
            return {
                "regression_detected": False,
                "reason": "No baseline data available"
            }

        # Calculate baseline metrics
        baseline_score = sum(e.overall_score for e in recent_evals) / len(recent_evals)
        baseline_success_rate = sum(
            e.performance_metrics["success_rate"] for e in recent_evals
        ) / len(recent_evals)

        # Compare current to baseline
        score_diff = current_evaluation.overall_score - baseline_score
        success_diff = (
            current_evaluation.performance_metrics["success_rate"] - baseline_success_rate
        )

        regression_detected = False
        regression_details = []

        # Check for score regression (>10% drop)
        if score_diff < -10.0:
            regression_detected = True
            regression_details.append(
                f"Quality score dropped by {abs(score_diff):.1f} points"
            )

        # Check for success rate regression (>10% drop)
        if success_diff < -0.10:
            regression_detected = True
            regression_details.append(
                f"Success rate dropped by {abs(success_diff)*100:.1f}%"
            )

        return {
            "regression_detected": regression_detected,
            "current_score": current_evaluation.overall_score,
            "baseline_score": baseline_score,
            "score_difference": score_diff,
            "current_success_rate": current_evaluation.performance_metrics["success_rate"],
            "baseline_success_rate": baseline_success_rate,
            "success_rate_difference": success_diff,
            "details": regression_details if regression_detected else []
        }
