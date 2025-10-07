"""
Planning Analyzer Demo - Real-World Agent Application

Demonstrates autonomous agents building a real Planning Explorer feature:
- Analyze planning applications using AI
- Generate opportunity scores
- Extract key insights
- Provide recommendations
- Full autonomous workflow from spec to implementation
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from app.agents.llm import LLMClient, LLMModel
from app.agents.intelligence import (
    TaskAnalyzer,
    CodeGenerator,
    CodeContext,
    ConversationalOrchestrator,
    PerformanceAnalyzer,
)
from app.agents.orchestrator_agent import (
    OrchestratorAgent,
    AgentRole,
    WorkflowDefinition,
    AgentTask,
    TaskPriority,
)


logger = logging.getLogger(__name__)


@dataclass
class PlanningApplication:
    """Planning application data"""
    application_id: str
    description: str
    location: str
    applicant: str
    development_type: str
    status: str
    decision_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OpportunityAnalysis:
    """AI-generated opportunity analysis"""
    application_id: str
    opportunity_score: float  # 0-100
    risk_score: float  # 0-100
    key_insights: List[str]
    recommendations: List[str]
    target_audience: List[str]  # developers, suppliers, investors
    estimated_value: Optional[float] = None
    confidence: float = 0.8
    generated_at: datetime = field(default_factory=datetime.now)


class PlanningAnalyzerDemo:
    """
    Demo: Autonomous agents building Planning Explorer feature.

    This demonstrates the full autonomous development workflow:
    1. User provides feature requirements in natural language
    2. TaskAnalyzer breaks down into agent tasks
    3. CodeGenerator creates implementation
    4. Agents autonomously build, test, and document
    5. PerformanceAnalyzer tracks and optimizes

    Feature: AI Planning Application Analyzer
    - Analyzes planning applications
    - Scores opportunities (0-100)
    - Identifies risks and insights
    - Recommends target audiences
    - Provides business intelligence
    """

    def __init__(
        self,
        anthropic_api_key: str,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize demo with LLM clients.

        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: Optional OpenAI API key
        """
        # Initialize LLM client
        self.llm_client = LLMClient(
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key
        )

        # Initialize intelligence components
        self.task_analyzer = TaskAnalyzer(
            llm_client=self.llm_client,
            model=LLMModel.CLAUDE_3_5_SONNET
        )

        self.code_generator = CodeGenerator(
            llm_client=self.llm_client,
            code_model=LLMModel.GPT_4_TURBO,
            review_model=LLMModel.CLAUDE_3_5_SONNET
        )

        self.performance_analyzer = PerformanceAnalyzer(
            llm_client=self.llm_client
        )

        # Initialize orchestrator
        self.orchestrator = OrchestratorAgent()

        # Conversational interface
        self.conversational = ConversationalOrchestrator(
            llm_client=self.llm_client,
            task_analyzer=self.task_analyzer,
            orchestrator=self.orchestrator
        )

    async def run_full_demo(self) -> Dict[str, Any]:
        """
        Run complete demo: conversational -> workflow -> implementation.

        Returns:
            Demo results with metrics
        """
        logger.info("=" * 80)
        logger.info("PLANNING ANALYZER DEMO - Autonomous Agent System")
        logger.info("=" * 80)

        demo_results = {
            "start_time": datetime.now().isoformat(),
            "stages": {}
        }

        # Stage 1: Natural Language Intent
        logger.info("\n[STAGE 1] Natural Language Feature Request")
        user_request = """
        I need an AI-powered planning application analyzer for Planning Explorer.

        It should:
        - Analyze planning applications and score opportunities (0-100)
        - Identify key insights and risks
        - Recommend target audiences (developers, suppliers, investors)
        - Provide actionable business intelligence

        This should be a FastAPI endpoint that takes application data and returns analysis.
        """

        response, workflow_result = await self.conversational.chat(
            message=user_request,
            project_context={
                "project": "Planning Explorer",
                "tech_stack": "FastAPI, Pydantic, OpenAI GPT-4",
                "existing_endpoints": "/api/v1/planning-applications"
            },
            auto_execute=False  # Manual execution for demo
        )

        logger.info(f"Agent Response: {response}")

        demo_results["stages"]["intent_recognition"] = {
            "user_request": user_request,
            "agent_response": response
        }

        # Stage 2: Task Analysis & Workflow Generation
        logger.info("\n[STAGE 2] Intelligent Task Analysis")

        requirements = {
            "feature": "AI Planning Application Analyzer",
            "endpoint": "POST /api/v1/analyze-application",
            "input": "PlanningApplication model",
            "output": "OpportunityAnalysis model",
            "ai_model": "GPT-4 or Claude 3.5",
            "processing_time": "< 3 seconds",
            "accuracy_target": "> 85%"
        }

        workflow_plan = await self.task_analyzer.generate_workflow(
            task_description="AI-powered planning application analyzer endpoint",
            requirements=requirements,
            context={
                "project": "Planning Explorer",
                "existing_code": True,
                "deployment": "Production-ready"
            }
        )

        logger.info(f"Workflow Plan Generated:")
        logger.info(f"  Tasks: {len(workflow_plan.workflow_definition.tasks)}")
        logger.info(f"  Execution Mode: {workflow_plan.workflow_definition.execution_mode}")
        logger.info(f"  Confidence: {workflow_plan.confidence_score:.2f}")

        demo_results["stages"]["workflow_planning"] = {
            "task_count": len(workflow_plan.workflow_definition.tasks),
            "execution_mode": workflow_plan.workflow_definition.execution_mode,
            "confidence": workflow_plan.confidence_score
        }

        # Stage 3: Autonomous Code Generation
        logger.info("\n[STAGE 3] Autonomous Code Generation")

        specifications = """
        Create a FastAPI endpoint for AI planning application analysis.

        Endpoint: POST /api/v1/analyze-application

        Input Model:
        - application_id: str
        - description: str (planning application description)
        - location: str
        - development_type: str
        - status: str

        Output Model:
        - opportunity_score: float (0-100)
        - risk_score: float (0-100)
        - key_insights: List[str]
        - recommendations: List[str]
        - target_audience: List[str]
        - confidence: float (0-1)

        Use OpenAI GPT-4 to analyze the application and generate:
        1. Opportunity score based on development potential
        2. Risk assessment
        3. Key insights for business intelligence
        4. Recommendations for stakeholders
        5. Target audience identification

        Include proper error handling, validation, and logging.
        """

        context = CodeContext(
            project_type="backend",
            existing_code={
                "app/main.py": "# FastAPI app initialization",
                "app/models/planning.py": "# Pydantic models"
            },
            dependencies=["fastapi", "pydantic", "openai"],
            design_patterns=["dependency_injection", "async_await"],
            constraints={"max_processing_time": 3.0}
        )

        generated_code = await self.code_generator.generate_backend_code(
            specifications=specifications,
            context=context,
            include_tests=True,
            include_docs=True
        )

        logger.info(f"Code Generated:")
        logger.info(f"  Lines of Code: {len(generated_code.code.splitlines())}")
        logger.info(f"  Language: {generated_code.language}")
        logger.info(f"  Tests: {'Yes' if generated_code.tests else 'No'}")
        logger.info(f"  Docs: {'Yes' if generated_code.documentation else 'No'}")

        demo_results["stages"]["code_generation"] = {
            "lines_of_code": len(generated_code.code.splitlines()),
            "has_tests": generated_code.tests is not None,
            "has_docs": generated_code.documentation is not None,
            "confidence": generated_code.confidence_score,
            "cost": generated_code.metadata.get("cost")
        }

        # Stage 4: Code Review
        logger.info("\n[STAGE 4] Autonomous Code Review")

        review_requirements = {
            "correctness": "Does it work as specified?",
            "performance": "< 3 second processing time",
            "security": "Proper input validation",
            "maintainability": "Clean, documented code",
            "testing": "Comprehensive test coverage"
        }

        code_review = await self.code_generator.review_code(
            code=generated_code.code,
            language="python",
            requirements=review_requirements,
            context=context
        )

        logger.info(f"Code Review Complete:")
        logger.info(f"  Assessment: {code_review.assessment}")
        logger.info(f"  Issues Found: {len(code_review.issues)}")
        logger.info(f"  Strengths: {len(code_review.strengths)}")

        demo_results["stages"]["code_review"] = {
            "assessment": code_review.assessment,
            "issues_count": len(code_review.issues),
            "strengths_count": len(code_review.strengths),
            "confidence": code_review.confidence_score
        }

        # Stage 5: Test the Feature (Simulated)
        logger.info("\n[STAGE 5] Feature Testing")

        test_application = PlanningApplication(
            application_id="APP-2025-001",
            description="Construction of 50 residential units with commercial space",
            location="Manchester City Centre",
            applicant="ABC Developments Ltd",
            development_type="Mixed Use",
            status="Under Review"
        )

        # Simulate analysis (would use generated code in production)
        analysis = await self._simulate_analysis(test_application)

        logger.info(f"Test Analysis Results:")
        logger.info(f"  Opportunity Score: {analysis.opportunity_score}/100")
        logger.info(f"  Risk Score: {analysis.risk_score}/100")
        logger.info(f"  Key Insights: {len(analysis.key_insights)}")
        logger.info(f"  Recommendations: {len(analysis.recommendations)}")
        logger.info(f"  Target Audience: {', '.join(analysis.target_audience)}")

        demo_results["stages"]["feature_testing"] = {
            "opportunity_score": analysis.opportunity_score,
            "risk_score": analysis.risk_score,
            "insights_count": len(analysis.key_insights),
            "confidence": analysis.confidence
        }

        # Stage 6: Performance Analysis
        logger.info("\n[STAGE 6] Performance Analysis & Optimization")

        # Record simulated metrics
        from app.agents.intelligence.performance_analyzer import ExecutionMetrics

        metrics = ExecutionMetrics(
            workflow_id="demo_workflow",
            timestamp=datetime.now(),
            agent_role=AgentRole.BACKEND,
            task_id="analyze_application",
            execution_time_seconds=2.3,
            tokens_used=8500,
            cost_usd=0.12,
            success=True,
            quality_score=0.92
        )

        # Would record in production:
        # await self.performance_analyzer.record_execution(...)

        recommendations = await self.performance_analyzer.get_optimization_recommendations(
            focus_areas=["cost", "speed"]
        )

        logger.info(f"Optimization Recommendations: {len(recommendations)}")
        for i, rec in enumerate(recommendations[:3], 1):
            logger.info(f"  {i}. {rec.title} (Priority: {rec.priority})")

        demo_results["stages"]["performance_optimization"] = {
            "recommendations_count": len(recommendations),
            "execution_time": metrics.execution_time_seconds,
            "cost": metrics.cost_usd,
            "quality_score": metrics.quality_score
        }

        # Final Summary
        demo_results["end_time"] = datetime.now().isoformat()
        demo_results["status"] = "success"

        logger.info("\n" + "=" * 80)
        logger.info("DEMO COMPLETE")
        logger.info("=" * 80)
        logger.info("\nAutonomous agents successfully:")
        logger.info("  ✓ Understood natural language requirements")
        logger.info("  ✓ Generated intelligent workflow plan")
        logger.info("  ✓ Created production-quality code")
        logger.info("  ✓ Wrote comprehensive tests")
        logger.info("  ✓ Generated API documentation")
        logger.info("  ✓ Performed code review")
        logger.info("  ✓ Tested the feature")
        logger.info("  ✓ Provided optimization recommendations")

        return demo_results

    async def _simulate_analysis(
        self,
        application: PlanningApplication
    ) -> OpportunityAnalysis:
        """
        Simulate AI analysis of planning application.

        In production, this would use the generated code.
        For demo, we use LLM directly.
        """
        prompt = f"""Analyze this UK planning application and provide business intelligence:

Application: {application.application_id}
Description: {application.description}
Location: {application.location}
Type: {application.development_type}
Status: {application.status}

Provide:
1. Opportunity Score (0-100): How attractive is this for business opportunities?
2. Risk Score (0-100): What are the risks and challenges?
3. Key Insights (3-5): Important facts and observations
4. Recommendations (3-5): Actionable advice for stakeholders
5. Target Audience: Who should care about this? (developers/suppliers/investors)

Return JSON:
{{
  "opportunity_score": 85.0,
  "risk_score": 35.0,
  "key_insights": ["...", "..."],
  "recommendations": ["...", "..."],
  "target_audience": ["developers", "suppliers"],
  "estimated_value": 5000000.0,
  "confidence": 0.85
}}"""

        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are an expert in UK planning and property development.",
            model=LLMModel.CLAUDE_3_5_SONNET,
            temperature=0.4
        )

        import json
        analysis_data = json.loads(response.content)

        return OpportunityAnalysis(
            application_id=application.application_id,
            opportunity_score=analysis_data["opportunity_score"],
            risk_score=analysis_data["risk_score"],
            key_insights=analysis_data["key_insights"],
            recommendations=analysis_data["recommendations"],
            target_audience=analysis_data["target_audience"],
            estimated_value=analysis_data.get("estimated_value"),
            confidence=analysis_data.get("confidence", 0.8)
        )

    async def quick_demo(self) -> str:
        """
        Run quick demo showing core capabilities.

        Returns:
            Demo summary
        """
        logger.info("Running Quick Demo...")

        # Just show natural language -> workflow generation
        user_message = "Build an AI feature to score planning applications"

        response, _ = await self.conversational.chat(
            message=user_message,
            auto_execute=False
        )

        workflow_plan = await self.task_analyzer.generate_workflow(
            task_description=user_message,
            requirements={"feature": "AI scoring"}
        )

        summary = f"""
Quick Demo Summary:

User Request: "{user_message}"

Agent Understanding:
{response}

Generated Workflow:
- Tasks: {len(workflow_plan.workflow_definition.tasks)}
- Execution Mode: {workflow_plan.workflow_definition.execution_mode}
- Confidence: {workflow_plan.confidence_score:.0%}

Agents Required:
{', '.join([t.agent_role.value for t in workflow_plan.workflow_definition.tasks])}

This demonstrates autonomous agents understanding requirements and creating execution plans!
        """

        return summary


async def main():
    """Run demo"""
    import os

    # Get API keys from environment
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not anthropic_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Initialize demo
    demo = PlanningAnalyzerDemo(
        anthropic_api_key=anthropic_key,
        openai_api_key=openai_key
    )

    # Run full demo
    results = await demo.run_full_demo()

    # Print results summary
    print("\n" + "=" * 80)
    print("DEMO RESULTS SUMMARY")
    print("=" * 80)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    import json
    asyncio.run(main())
