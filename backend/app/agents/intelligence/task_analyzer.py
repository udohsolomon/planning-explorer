"""
Task Analyzer - Intelligent Task Decomposition using LLMs

Uses Claude/GPT to analyze complex tasks and create optimal workflows:
- Understand task complexity and requirements
- Select appropriate specialist agents
- Identify dependencies between subtasks
- Determine optimal execution mode
- Generate detailed workflow plans
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.llm.prompt_library import PromptLibrary, PromptType
from app.agents.orchestrator_agent import (
    WorkflowDefinition,
    AgentTask,
    AgentRole,
    TaskPriority,
)


logger = logging.getLogger(__name__)


@dataclass
class TaskAnalysis:
    """Analysis of a development task"""
    task_id: str
    complexity_score: float  # 0-100
    estimated_duration_hours: float
    required_agents: List[AgentRole]
    risk_factors: List[str]
    success_criteria: Dict[str, Any]
    recommended_approach: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowPlan:
    """Generated workflow plan"""
    workflow_definition: WorkflowDefinition
    analysis: TaskAnalysis
    rationale: str
    confidence_score: float  # 0-1
    alternative_approaches: List[str] = field(default_factory=list)


class TaskAnalyzer:
    """
    Intelligent task analyzer using LLMs.

    Capabilities:
    - Analyze task complexity and requirements
    - Select optimal specialist agents
    - Identify task dependencies
    - Generate workflow plans
    - Assess risks and success criteria
    """

    def __init__(
        self,
        llm_client: LLMClient,
        model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize task analyzer.

        Args:
            llm_client: LLM client for intelligence
            model: LLM model to use
        """
        self.llm_client = llm_client
        self.model = model

        # Analysis history for learning
        self.analysis_history: List[TaskAnalysis] = []

    async def analyze_task(
        self,
        task_description: str,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> TaskAnalysis:
        """
        Analyze task complexity and requirements.

        Args:
            task_description: High-level task description
            requirements: Task requirements
            context: Optional project context

        Returns:
            TaskAnalysis with complexity assessment
        """
        logger.info(f"Analyzing task: {task_description}")

        context = context or {}

        # Build analysis prompt
        prompt = f"""Analyze this development task in detail:

Task: {task_description}

Requirements:
{json.dumps(requirements, indent=2)}

Project Context:
{json.dumps(context, indent=2)}

Provide a comprehensive analysis in JSON format:
{{
  "complexity_score": <0-100>,
  "estimated_duration_hours": <hours>,
  "required_agents": ["backend_engineer", "elasticsearch_architect", ...],
  "risk_factors": ["risk1", "risk2", ...],
  "success_criteria": {{"criterion1": "description", ...}},
  "recommended_approach": "detailed approach description"
}}

Consider:
- Technical complexity
- Integration points
- Testing requirements
- Documentation needs
- Potential risks
- Required expertise"""

        # Get LLM analysis
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert software architect analyzing development tasks.",
            model=self.model,
            temperature=0.3  # Lower temperature for consistent analysis
        )

        # Parse response
        try:
            analysis_data = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            logger.warning("Failed to parse LLM response as JSON, using defaults")
            analysis_data = {
                "complexity_score": 50.0,
                "estimated_duration_hours": 4.0,
                "required_agents": ["backend_engineer"],
                "risk_factors": ["Unknown complexity"],
                "success_criteria": {"implemented": "Feature works as specified"},
                "recommended_approach": "Standard implementation approach"
            }

        # Convert agent names to AgentRole enums
        required_agents = []
        for agent_name in analysis_data.get("required_agents", []):
            try:
                role = AgentRole[agent_name.upper()]
                required_agents.append(role)
            except (KeyError, AttributeError):
                logger.warning(f"Unknown agent role: {agent_name}")

        # Create analysis
        task_analysis = TaskAnalysis(
            task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            complexity_score=float(analysis_data.get("complexity_score", 50.0)),
            estimated_duration_hours=float(analysis_data.get("estimated_duration_hours", 4.0)),
            required_agents=required_agents,
            risk_factors=analysis_data.get("risk_factors", []),
            success_criteria=analysis_data.get("success_criteria", {}),
            recommended_approach=analysis_data.get("recommended_approach", ""),
            metadata={
                "llm_model": self.model.value,
                "llm_cost": response.cost_usd,
                "analyzed_at": datetime.now().isoformat()
            }
        )

        # Store in history
        self.analysis_history.append(task_analysis)

        logger.info(
            f"Task analysis complete: complexity={task_analysis.complexity_score}, "
            f"duration={task_analysis.estimated_duration_hours}h, "
            f"agents={len(task_analysis.required_agents)}"
        )

        return task_analysis

    async def generate_workflow(
        self,
        task_description: str,
        requirements: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        analysis: Optional[TaskAnalysis] = None
    ) -> WorkflowPlan:
        """
        Generate complete workflow plan using LLM.

        Args:
            task_description: Task description
            requirements: Task requirements
            context: Optional context
            analysis: Optional pre-computed analysis

        Returns:
            WorkflowPlan with workflow definition
        """
        logger.info(f"Generating workflow for: {task_description}")

        # Analyze task if not provided
        if not analysis:
            analysis = await self.analyze_task(task_description, requirements, context)

        # Get task decomposition prompt
        decomposition_prompt = PromptLibrary.get_prompt(PromptType.TASK_DECOMPOSITION)

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            decomposition_prompt,
            task_description=task_description,
            requirements=json.dumps(requirements, indent=2),
            context=json.dumps(context or {}, indent=2)
        )

        # Get workflow from LLM
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.model,
            temperature=0.5  # Moderate temperature for creativity
        )

        # Parse workflow
        try:
            workflow_data = json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse workflow JSON")
            # Create fallback workflow
            workflow_data = {
                "workflow_name": task_description,
                "execution_mode": "sequential",
                "tasks": [],
                "success_criteria": requirements
            }

        # Convert to WorkflowDefinition
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        tasks = []
        for i, task_data in enumerate(workflow_data.get("tasks", [])):
            # Map agent role
            agent_name = task_data.get("agent_role", "backend_engineer")
            try:
                agent_role = AgentRole[agent_name.upper()]
            except (KeyError, AttributeError):
                logger.warning(f"Unknown agent: {agent_name}, using BACKEND")
                agent_role = AgentRole.BACKEND

            # Map priority
            priority_map = {
                "critical": TaskPriority.CRITICAL,
                "high": TaskPriority.HIGH,
                "normal": TaskPriority.MEDIUM,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW,
            }
            priority_str = task_data.get("priority", "normal").lower()
            priority = priority_map.get(priority_str, TaskPriority.MEDIUM)

            task = AgentTask(
                task_id=task_data.get("task_id", f"task_{i+1}"),
                agent_role=agent_role,
                description=task_data.get("description", ""),
                requirements=task_data.get("requirements", {}),
                dependencies=task_data.get("dependencies", []),
                priority=priority
            )

            tasks.append(task)

        workflow_definition = WorkflowDefinition(
            workflow_id=workflow_id,
            name=workflow_data.get("workflow_name", task_description),
            description=f"LLM-generated workflow for: {task_description}",
            tasks=tasks,
            execution_mode=workflow_data.get("execution_mode", "sequential"),
            success_criteria=workflow_data.get("success_criteria", {})
        )

        # Calculate confidence
        confidence_score = self._calculate_confidence(
            workflow_definition,
            analysis,
            response
        )

        workflow_plan = WorkflowPlan(
            workflow_definition=workflow_definition,
            analysis=analysis,
            rationale=analysis.recommended_approach,
            confidence_score=confidence_score,
            alternative_approaches=[]  # Could be enhanced
        )

        logger.info(
            f"Workflow generated: {len(tasks)} tasks, "
            f"mode={workflow_definition.execution_mode}, "
            f"confidence={confidence_score:.2f}"
        )

        return workflow_plan

    async def select_agent(
        self,
        task_description: str,
        requirements: Dict[str, Any]
    ) -> tuple[AgentRole, float]:
        """
        Select optimal agent for a task using LLM.

        Args:
            task_description: Task description
            requirements: Task requirements

        Returns:
            (selected_agent, confidence_score)
        """
        # Get agent selection prompt
        selection_prompt = PromptLibrary.get_prompt(PromptType.AGENT_SELECTION)

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            selection_prompt,
            task_description=task_description,
            requirements=json.dumps(requirements, indent=2)
        )

        # Get LLM selection
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.model,
            temperature=0.3
        )

        # Parse selection
        try:
            selection_data = json.loads(response.content)
            agent_name = selection_data.get("primary_agent", "backend_engineer")
            confidence = float(selection_data.get("confidence", 0.7))

            try:
                agent_role = AgentRole[agent_name.upper()]
            except (KeyError, AttributeError):
                logger.warning(f"Unknown agent: {agent_name}")
                agent_role = AgentRole.BACKEND
                confidence = 0.5

            return agent_role, confidence

        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning("Failed to parse agent selection, using default")
            return AgentRole.BACKEND, 0.5

    async def identify_dependencies(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Identify dependencies between tasks using LLM.

        Args:
            tasks: List of task descriptions

        Returns:
            Dict mapping task_id to list of dependency task_ids
        """
        prompt = f"""Analyze these tasks and identify dependencies:

Tasks:
{json.dumps(tasks, indent=2)}

For each task, identify which other tasks must be completed first.

Return JSON:
{{
  "task1": ["prerequisite_task1", "prerequisite_task2"],
  "task2": [],
  ...
}}"""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert at analyzing task dependencies in software development.",
            model=self.model,
            temperature=0.3
        )

        try:
            dependencies = json.loads(response.content)
            return dependencies
        except json.JSONDecodeError:
            logger.warning("Failed to parse dependencies")
            return {task["task_id"]: [] for task in tasks}

    def _calculate_confidence(
        self,
        workflow: WorkflowDefinition,
        analysis: TaskAnalysis,
        llm_response: Any
    ) -> float:
        """Calculate confidence score for workflow"""
        confidence = 0.7  # Base confidence

        # Increase confidence if workflow has good structure
        if len(workflow.tasks) > 0:
            confidence += 0.1

        # Increase if dependencies are specified
        has_dependencies = any(task.dependencies for task in workflow.tasks)
        if has_dependencies:
            confidence += 0.1

        # Decrease for high complexity
        if analysis.complexity_score > 80:
            confidence -= 0.1

        # Decrease if many agents required
        if len(analysis.required_agents) > 5:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics from analysis history"""
        if not self.analysis_history:
            return {"total_analyses": 0}

        return {
            "total_analyses": len(self.analysis_history),
            "average_complexity": sum(
                a.complexity_score for a in self.analysis_history
            ) / len(self.analysis_history),
            "average_duration": sum(
                a.estimated_duration_hours for a in self.analysis_history
            ) / len(self.analysis_history),
            "most_common_agents": self._get_most_common_agents(),
            "total_llm_cost": sum(
                a.metadata.get("llm_cost", 0.0) for a in self.analysis_history
            )
        }

    def _get_most_common_agents(self) -> List[str]:
        """Get most commonly required agents"""
        agent_counts = {}

        for analysis in self.analysis_history:
            for agent in analysis.required_agents:
                agent_counts[agent.value] = agent_counts.get(agent.value, 0) + 1

        sorted_agents = sorted(
            agent_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [agent for agent, _ in sorted_agents[:5]]
