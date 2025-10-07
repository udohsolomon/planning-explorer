"""
Agent API - Production REST API for Autonomous Agents

Exposes agent capabilities via FastAPI endpoints:
- Conversational workflow control
- Task analysis and workflow generation
- Code generation and review
- Performance monitoring
- Real-time progress streaming
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.llm import LLMClient, LLMModel
from app.agents.intelligence import (
    TaskAnalyzer,
    CodeGenerator,
    ConversationalOrchestrator,
    PerformanceAnalyzer,
    CodeContext,
    IntentType,
)
from app.agents.orchestrator_agent import (
    OrchestratorAgent,
    WorkflowDefinition,
    AgentRole,
    AgentTask,
    TaskPriority,
)


logger = logging.getLogger(__name__)


# ==================== REQUEST/RESPONSE MODELS ====================


class ChatRequest(BaseModel):
    """Chat with conversational orchestrator"""
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    project_context: Optional[Dict[str, Any]] = Field(None, description="Project context")
    auto_execute: bool = Field(False, description="Automatically execute workflow")


class ChatResponse(BaseModel):
    """Chat response"""
    message: str
    conversation_id: str
    intent_type: str
    confidence: float
    workflow_id: Optional[str] = None
    workflow_status: Optional[str] = None


class TaskAnalysisRequest(BaseModel):
    """Request task analysis"""
    task_description: str = Field(..., description="Task to analyze")
    requirements: Dict[str, Any] = Field(..., description="Task requirements")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")


class TaskAnalysisResponse(BaseModel):
    """Task analysis result"""
    task_id: str
    complexity_score: float
    estimated_duration_hours: float
    required_agents: List[str]
    risk_factors: List[str]
    success_criteria: Dict[str, Any]
    recommended_approach: str


class WorkflowGenerationRequest(BaseModel):
    """Request workflow generation"""
    task_description: str = Field(..., description="Task description")
    requirements: Dict[str, Any] = Field(..., description="Requirements")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")


class WorkflowGenerationResponse(BaseModel):
    """Generated workflow"""
    workflow_id: str
    workflow_name: str
    task_count: int
    execution_mode: str
    confidence_score: float
    estimated_duration_hours: float


class CodeGenerationRequest(BaseModel):
    """Request code generation"""
    specifications: str = Field(..., description="Code specifications")
    language: str = Field(..., description="Programming language (python/typescript)")
    project_type: str = Field(..., description="Project type (backend/frontend/fullstack)")
    existing_code: Optional[Dict[str, str]] = Field(None, description="Existing code files")
    include_tests: bool = Field(True, description="Generate tests")
    include_docs: bool = Field(True, description="Generate documentation")


class CodeGenerationResponse(BaseModel):
    """Generated code result"""
    code: str
    language: str
    explanation: str
    tests: Optional[str] = None
    documentation: Optional[str] = None
    confidence_score: float
    cost_usd: float
    tokens_used: int


class CodeReviewRequest(BaseModel):
    """Request code review"""
    code: str = Field(..., description="Code to review")
    language: str = Field(..., description="Programming language")
    requirements: Dict[str, Any] = Field(..., description="Requirements to check")


class CodeReviewResponse(BaseModel):
    """Code review result"""
    assessment: str  # APPROVE, REQUEST_CHANGES, REJECT
    issues: List[Dict[str, Any]]
    strengths: List[str]
    overall_feedback: str
    confidence_score: float


class PerformanceStatsResponse(BaseModel):
    """Performance statistics"""
    total_executions: int
    total_time_seconds: float
    total_cost_usd: float
    success_rate: float
    average_quality: float
    by_agent: Dict[str, Any]


class OptimizationRecommendationsResponse(BaseModel):
    """Optimization recommendations"""
    recommendations: List[Dict[str, Any]]
    total_count: int


class WorkflowExecutionRequest(BaseModel):
    """Execute workflow"""
    workflow_id: Optional[str] = Field(None, description="Workflow ID if already created")
    task_description: Optional[str] = Field(None, description="Create workflow from description")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Requirements")


class WorkflowStatusResponse(BaseModel):
    """Workflow execution status"""
    workflow_id: str
    status: str
    progress: float  # 0-100
    current_task: Optional[str] = None
    completed_tasks: int
    total_tasks: int
    metadata: Dict[str, Any]


# ==================== API DEPENDENCIES ====================


async def get_llm_client() -> LLMClient:
    """Get LLM client dependency"""
    import os

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not anthropic_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY not configured"
        )

    return LLMClient(
        anthropic_api_key=anthropic_key,
        openai_api_key=openai_key
    )


async def get_task_analyzer(
    llm_client: LLMClient = Depends(get_llm_client)
) -> TaskAnalyzer:
    """Get task analyzer dependency"""
    return TaskAnalyzer(llm_client=llm_client)


async def get_code_generator(
    llm_client: LLMClient = Depends(get_llm_client)
) -> CodeGenerator:
    """Get code generator dependency"""
    return CodeGenerator(llm_client=llm_client)


async def get_orchestrator() -> OrchestratorAgent:
    """Get orchestrator dependency"""
    return OrchestratorAgent()


async def get_conversational(
    llm_client: LLMClient = Depends(get_llm_client),
    task_analyzer: TaskAnalyzer = Depends(get_task_analyzer),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
) -> ConversationalOrchestrator:
    """Get conversational orchestrator dependency"""
    return ConversationalOrchestrator(
        llm_client=llm_client,
        task_analyzer=task_analyzer,
        orchestrator=orchestrator
    )


async def get_performance_analyzer(
    llm_client: LLMClient = Depends(get_llm_client)
) -> PerformanceAnalyzer:
    """Get performance analyzer dependency"""
    return PerformanceAnalyzer(llm_client=llm_client)


# ==================== API ROUTER ====================


router = APIRouter(prefix="/api/v1/agents", tags=["Autonomous Agents"])


# ==================== ENDPOINTS ====================


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    conversational: ConversationalOrchestrator = Depends(get_conversational)
):
    """
    Chat with conversational agent for natural language workflow control.

    Example:
    ```json
    {
      "message": "Build a feature to analyze planning applications with AI",
      "auto_execute": false
    }
    ```
    """
    try:
        response, workflow_result = await conversational.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            project_context=request.project_context,
            auto_execute=request.auto_execute
        )

        # Get conversation turns to extract intent
        conversation = conversational.conversations.get(
            request.conversation_id or list(conversational.conversations.keys())[-1]
        )

        latest_turn = conversation.turns[-1]

        return ChatResponse(
            message=response,
            conversation_id=conversation.conversation_id,
            intent_type=latest_turn.intent.intent_type.value,
            confidence=latest_turn.intent.confidence,
            workflow_id=workflow_result.workflow_id if workflow_result else None,
            workflow_status=workflow_result.status if workflow_result else None
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-task", response_model=TaskAnalysisResponse)
async def analyze_task(
    request: TaskAnalysisRequest,
    task_analyzer: TaskAnalyzer = Depends(get_task_analyzer)
):
    """
    Analyze task complexity and requirements using AI.

    Returns:
    - Complexity score (0-100)
    - Estimated duration
    - Required agents
    - Risk factors
    - Success criteria
    """
    try:
        analysis = await task_analyzer.analyze_task(
            task_description=request.task_description,
            requirements=request.requirements,
            context=request.context
        )

        return TaskAnalysisResponse(
            task_id=analysis.task_id,
            complexity_score=analysis.complexity_score,
            estimated_duration_hours=analysis.estimated_duration_hours,
            required_agents=[a.value for a in analysis.required_agents],
            risk_factors=analysis.risk_factors,
            success_criteria=analysis.success_criteria,
            recommended_approach=analysis.recommended_approach
        )

    except Exception as e:
        logger.error(f"Task analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-workflow", response_model=WorkflowGenerationResponse)
async def generate_workflow(
    request: WorkflowGenerationRequest,
    task_analyzer: TaskAnalyzer = Depends(get_task_analyzer)
):
    """
    Generate intelligent workflow plan from task description.

    Uses AI to:
    - Break down task into specialist assignments
    - Identify dependencies
    - Determine execution mode
    - Estimate duration and complexity
    """
    try:
        workflow_plan = await task_analyzer.generate_workflow(
            task_description=request.task_description,
            requirements=request.requirements,
            context=request.context
        )

        return WorkflowGenerationResponse(
            workflow_id=workflow_plan.workflow_definition.workflow_id,
            workflow_name=workflow_plan.workflow_definition.name,
            task_count=len(workflow_plan.workflow_definition.tasks),
            execution_mode=workflow_plan.workflow_definition.execution_mode,
            confidence_score=workflow_plan.confidence_score,
            estimated_duration_hours=workflow_plan.analysis.estimated_duration_hours
        )

    except Exception as e:
        logger.error(f"Workflow generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-code", response_model=CodeGenerationResponse)
async def generate_code(
    request: CodeGenerationRequest,
    code_generator: CodeGenerator = Depends(get_code_generator)
):
    """
    Generate production-quality code using AI.

    Supports:
    - Backend (Python/FastAPI)
    - Frontend (TypeScript/React)
    - Automatic test generation
    - API documentation
    """
    try:
        context = CodeContext(
            project_type=request.project_type,
            existing_code=request.existing_code or {}
        )

        if request.language == "python" or request.project_type == "backend":
            generated = await code_generator.generate_backend_code(
                specifications=request.specifications,
                context=context,
                include_tests=request.include_tests,
                include_docs=request.include_docs
            )
        else:
            generated = await code_generator.generate_frontend_code(
                specifications=request.specifications,
                context=context,
                include_tests=request.include_tests
            )

        return CodeGenerationResponse(
            code=generated.code,
            language=generated.language,
            explanation=generated.explanation,
            tests=generated.tests,
            documentation=generated.documentation,
            confidence_score=generated.confidence_score,
            cost_usd=generated.metadata.get("cost", 0.0),
            tokens_used=generated.metadata.get("tokens", 0)
        )

    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review-code", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest,
    code_generator: CodeGenerator = Depends(get_code_generator)
):
    """
    AI-powered code review.

    Reviews for:
    - Correctness
    - Best practices
    - Performance
    - Security
    - Maintainability
    """
    try:
        review = await code_generator.review_code(
            code=request.code,
            language=request.language,
            requirements=request.requirements
        )

        return CodeReviewResponse(
            assessment=review.assessment,
            issues=review.issues,
            strengths=review.strengths,
            overall_feedback=review.overall_feedback,
            confidence_score=review.confidence_score
        )

    except Exception as e:
        logger.error(f"Code review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-workflow", response_model=WorkflowStatusResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator),
    task_analyzer: TaskAnalyzer = Depends(get_task_analyzer)
):
    """
    Execute workflow (async background task).

    Either provide workflow_id or task_description to generate workflow first.
    """
    try:
        workflow_id = request.workflow_id

        if not workflow_id:
            # Generate workflow from description
            if not request.task_description:
                raise HTTPException(
                    status_code=400,
                    detail="Either workflow_id or task_description required"
                )

            workflow_plan = await task_analyzer.generate_workflow(
                task_description=request.task_description,
                requirements=request.requirements or {}
            )

            workflow_id = workflow_plan.workflow_definition.workflow_id

            # Queue execution in background
            background_tasks.add_task(
                orchestrator.execute_workflow,
                workflow_plan.workflow_definition
            )

        # Return initial status
        status = orchestrator.get_workflow_status(workflow_id)

        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")

        total_tasks = len(status["tasks"])
        completed = sum(1 for t in status["tasks"].values() if t["status"] == "completed")

        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            status=status["status"],
            progress=(completed / total_tasks * 100) if total_tasks > 0 else 0,
            current_task=status.get("current_task"),
            completed_tasks=completed,
            total_tasks=total_tasks,
            metadata=status.get("metadata", {})
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """Get workflow execution status"""
    status = orchestrator.get_workflow_status(workflow_id)

    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")

    total_tasks = len(status["tasks"])
    completed = sum(1 for t in status["tasks"].values() if t["status"] == "completed")

    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status=status["status"],
        progress=(completed / total_tasks * 100) if total_tasks > 0 else 0,
        current_task=status.get("current_task"),
        completed_tasks=completed,
        total_tasks=total_tasks,
        metadata=status.get("metadata", {})
    )


@router.get("/performance/stats", response_model=PerformanceStatsResponse)
async def get_performance_stats(
    performance: PerformanceAnalyzer = Depends(get_performance_analyzer)
):
    """Get agent performance statistics"""
    stats = performance.get_performance_summary()

    return PerformanceStatsResponse(
        total_executions=stats.get("total_executions", 0),
        total_time_seconds=stats.get("total_time_seconds", 0.0),
        total_cost_usd=stats.get("total_cost_usd", 0.0),
        success_rate=stats.get("success_rate", 0.0),
        average_quality=stats.get("average_quality", 0.0),
        by_agent=stats.get("by_agent", {})
    )


@router.get("/performance/recommendations", response_model=OptimizationRecommendationsResponse)
async def get_optimization_recommendations(
    focus_areas: Optional[List[str]] = Query(None, description="Focus areas (cost, speed, quality)"),
    performance: PerformanceAnalyzer = Depends(get_performance_analyzer)
):
    """Get AI-powered optimization recommendations"""
    try:
        recommendations = await performance.get_optimization_recommendations(
            focus_areas=focus_areas
        )

        return OptimizationRecommendationsResponse(
            recommendations=[
                {
                    "category": r.category,
                    "priority": r.priority,
                    "title": r.title,
                    "current_state": r.current_state,
                    "proposed_change": r.proposed_change,
                    "expected_improvement": r.expected_improvement,
                    "implementation_effort": r.implementation_effort,
                    "estimated_savings": r.estimated_savings
                }
                for r in recommendations
            ],
            total_count=len(recommendations)
        )

    except Exception as e:
        logger.error(f"Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Agent API health check"""
    return {
        "status": "healthy",
        "service": "Autonomous Agent API",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0"
    }
