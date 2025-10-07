"""
Code Generator - Autonomous Code Generation using LLMs

Generates production-quality code with:
- Context-aware code generation
- Multi-file project understanding
- Best practices enforcement
- Automated testing
- Code review
- Documentation generation
"""

import logging
import json
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from app.agents.llm import LLMClient, LLMMessage, LLMModel
from app.agents.llm.prompt_library import PromptLibrary, PromptType


logger = logging.getLogger(__name__)


@dataclass
class CodeContext:
    """Context for code generation"""
    project_type: Literal["backend", "frontend", "fullstack"]
    existing_code: Dict[str, str] = field(default_factory=dict)  # filepath -> content
    dependencies: List[str] = field(default_factory=list)
    design_patterns: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedCode:
    """Generated code with metadata"""
    code: str
    language: str
    file_path: Optional[str] = None
    explanation: str = ""
    dependencies: List[str] = field(default_factory=list)
    tests: Optional[str] = None
    documentation: Optional[str] = None
    confidence_score: float = 0.8
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeReview:
    """Code review result"""
    assessment: Literal["APPROVE", "REQUEST_CHANGES", "REJECT"]
    issues: List[Dict[str, Any]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    overall_feedback: str = ""
    confidence_score: float = 0.8


class CodeGenerator:
    """
    Autonomous code generator using LLMs.

    Capabilities:
    - Generate production-quality code
    - Context-aware generation
    - Multi-language support
    - Automated testing
    - Code review
    - Documentation generation
    """

    def __init__(
        self,
        llm_client: LLMClient,
        code_model: LLMModel = LLMModel.GPT_4_TURBO,
        review_model: LLMModel = LLMModel.CLAUDE_3_5_SONNET
    ):
        """
        Initialize code generator.

        Args:
            llm_client: LLM client
            code_model: Model for code generation (GPT-4 Turbo recommended)
            review_model: Model for code review (Claude recommended)
        """
        self.llm_client = llm_client
        self.code_model = code_model
        self.review_model = review_model

        # Generation history
        self.generation_history: List[GeneratedCode] = []

    async def generate_backend_code(
        self,
        specifications: str,
        context: CodeContext,
        include_tests: bool = True,
        include_docs: bool = True
    ) -> GeneratedCode:
        """
        Generate FastAPI backend code.

        Args:
            specifications: Code specifications
            context: Code context
            include_tests: Generate tests
            include_docs: Generate documentation

        Returns:
            GeneratedCode with backend implementation
        """
        logger.info("Generating backend code")

        # Get backend code generation prompt
        prompt = PromptLibrary.CODE_GENERATION_BACKEND

        # Format existing code context
        existing_code_str = "\n\n".join([
            f"# {filepath}\n```python\n{code}\n```"
            for filepath, code in context.existing_code.items()
        ])

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            prompt,
            specifications=specifications,
            context=json.dumps({
                "project_type": context.project_type,
                "dependencies": context.dependencies,
                "constraints": context.constraints
            }, indent=2),
            existing_code=existing_code_str or "No existing code"
        )

        # Generate code
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.code_model,
            temperature=0.4,  # Lower for code consistency
            max_tokens=4096
        )

        # Extract code from response
        code = self._extract_code_block(response.content, "python")

        # Generate tests if requested
        tests = None
        if include_tests:
            tests = await self.generate_tests(code, "python", context)

        # Generate docs if requested
        documentation = None
        if include_docs:
            documentation = await self.generate_documentation(
                code,
                "python",
                specifications
            )

        generated = GeneratedCode(
            code=code,
            language="python",
            explanation=self._extract_explanation(response.content),
            tests=tests,
            documentation=documentation,
            confidence_score=0.85,
            metadata={
                "model": self.code_model.value,
                "cost": response.cost_usd,
                "tokens": response.tokens_used,
                "generated_at": datetime.now().isoformat()
            }
        )

        self.generation_history.append(generated)

        logger.info(f"Backend code generated: {len(code)} chars")

        return generated

    async def generate_frontend_code(
        self,
        specifications: str,
        context: CodeContext,
        design_system: Optional[Dict[str, Any]] = None,
        include_tests: bool = True
    ) -> GeneratedCode:
        """
        Generate Next.js/React frontend code.

        Args:
            specifications: Component specifications
            context: Code context
            design_system: Design system specs
            include_tests: Generate tests

        Returns:
            GeneratedCode with React component
        """
        logger.info("Generating frontend code")

        # Get frontend prompt
        prompt = PromptLibrary.CODE_GENERATION_FRONTEND

        # Format existing components
        existing_components = "\n\n".join([
            f"// {filepath}\n```typescript\n{code}\n```"
            for filepath, code in context.existing_code.items()
        ])

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            prompt,
            specifications=specifications,
            design_system=json.dumps(design_system or {}, indent=2),
            existing_components=existing_components or "No existing components"
        )

        # Generate code
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.code_model,
            temperature=0.4,
            max_tokens=4096
        )

        # Extract code
        code = self._extract_code_block(response.content, "typescript")

        # Generate tests if requested
        tests = None
        if include_tests:
            tests = await self.generate_tests(code, "typescript", context)

        generated = GeneratedCode(
            code=code,
            language="typescript",
            explanation=self._extract_explanation(response.content),
            tests=tests,
            confidence_score=0.85,
            metadata={
                "model": self.code_model.value,
                "cost": response.cost_usd,
                "generated_at": datetime.now().isoformat()
            }
        )

        self.generation_history.append(generated)

        logger.info(f"Frontend code generated: {len(code)} chars")

        return generated

    async def review_code(
        self,
        code: str,
        language: str,
        requirements: Dict[str, Any],
        context: Optional[CodeContext] = None
    ) -> CodeReview:
        """
        Automated code review using LLM.

        Args:
            code: Code to review
            language: Programming language
            requirements: Requirements to check against
            context: Optional code context

        Returns:
            CodeReview with assessment
        """
        logger.info(f"Reviewing {language} code")

        # Get code review prompt
        prompt = PromptLibrary.CODE_REVIEW

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            prompt,
            language=language,
            code=code,
            context=json.dumps(context.__dict__ if context else {}, indent=2),
            requirements=json.dumps(requirements, indent=2)
        )

        # Get review
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.review_model,
            temperature=0.3,
            max_tokens=2048
        )

        # Parse review
        try:
            review_data = json.loads(response.content)

            review = CodeReview(
                assessment=review_data.get("assessment", "REQUEST_CHANGES"),
                issues=review_data.get("issues", []),
                strengths=review_data.get("strengths", []),
                overall_feedback=review_data.get("overall_feedback", ""),
                confidence_score=0.8
            )

            logger.info(f"Code review: {review.assessment}, {len(review.issues)} issues")

            return review

        except json.JSONDecodeError:
            logger.warning("Failed to parse review JSON")
            return CodeReview(
                assessment="REQUEST_CHANGES",
                overall_feedback="Review parsing failed",
                confidence_score=0.3
            )

    async def generate_tests(
        self,
        code: str,
        language: str,
        context: CodeContext,
        coverage_target: int = 80
    ) -> str:
        """
        Generate tests for code.

        Args:
            code: Code to test
            language: Programming language
            context: Code context
            coverage_target: Target coverage percentage

        Returns:
            Generated test code
        """
        logger.info(f"Generating tests for {language} code")

        # Get test generation prompt
        prompt = PromptLibrary.TEST_GENERATION

        test_types = ["unit", "integration"]
        if context.project_type == "backend":
            test_types.append("e2e")

        dependencies_to_mock = context.dependencies

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            prompt,
            code=code,
            coverage_target=str(coverage_target),
            test_types=", ".join(test_types),
            dependencies_to_mock=", ".join(dependencies_to_mock)
        )

        # Generate tests
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.code_model,
            temperature=0.4,
            max_tokens=3072
        )

        # Extract test code
        test_code = self._extract_code_block(response.content, language)

        logger.info(f"Tests generated: {len(test_code)} chars")

        return test_code

    async def generate_documentation(
        self,
        code: str,
        language: str,
        specifications: str,
        audience: str = "developers"
    ) -> str:
        """
        Generate documentation for code.

        Args:
            code: Code to document
            language: Programming language
            specifications: Original specifications
            audience: Target audience

        Returns:
            Generated documentation (Markdown)
        """
        logger.info("Generating documentation")

        # Build API spec from code
        api_spec = f"""
Code:
```{language}
{code}
```

Original Specifications:
{specifications}
"""

        prompt = PromptLibrary.DOCUMENTATION_API

        system_prompt, user_prompt = PromptLibrary.format_prompt(
            prompt,
            api_spec=api_spec,
            audience=audience,
            languages="Python, JavaScript, cURL"
        )

        # Generate docs
        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=user_prompt)],
            system_prompt=system_prompt,
            model=self.code_model,
            temperature=0.5,
            max_tokens=2048
        )

        logger.info(f"Documentation generated: {len(response.content)} chars")

        return response.content

    async def refactor_code(
        self,
        code: str,
        language: str,
        refactoring_goal: str,
        context: Optional[CodeContext] = None
    ) -> GeneratedCode:
        """
        Refactor code for improvement.

        Args:
            code: Code to refactor
            language: Programming language
            refactoring_goal: What to improve
            context: Optional context

        Returns:
            GeneratedCode with refactored version
        """
        logger.info(f"Refactoring {language} code: {refactoring_goal}")

        prompt = f"""Refactor this {language} code:

```{language}
{code}
```

Refactoring Goal: {refactoring_goal}

Context:
{json.dumps(context.__dict__ if context else {}, indent=2)}

Provide:
1. Refactored code
2. Explanation of changes
3. Benefits of refactoring

Return in format:
REFACTORED CODE:
```{language}
<refactored code here>
```

EXPLANATION:
<explanation here>

BENEFITS:
- <benefit 1>
- <benefit 2>
..."""

        response = await self.llm_client.complete(
            messages=[LLMMessage(role="user", content=prompt)],
            system_prompt="You are an expert code refactoring specialist.",
            model=self.code_model,
            temperature=0.4
        )

        # Extract refactored code
        refactored = self._extract_code_block(response.content, language)
        explanation = self._extract_explanation(response.content)

        return GeneratedCode(
            code=refactored,
            language=language,
            explanation=explanation,
            confidence_score=0.8,
            metadata={
                "refactoring_goal": refactoring_goal,
                "model": self.code_model.value,
                "cost": response.cost_usd
            }
        )

    def _extract_code_block(self, content: str, language: str) -> str:
        """Extract code from markdown code block"""
        # Look for code block with language
        start_marker = f"```{language}"
        if start_marker not in content:
            # Try generic code block
            start_marker = "```"

        if start_marker in content:
            parts = content.split(start_marker)
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()

        # No code block found, return as-is
        return content.strip()

    def _extract_explanation(self, content: str) -> str:
        """Extract explanation from response"""
        # Look for explanation markers
        markers = ["EXPLANATION:", "Explanation:", "## Explanation"]

        for marker in markers:
            if marker in content:
                parts = content.split(marker)
                if len(parts) > 1:
                    # Take text after marker up to next section
                    explanation = parts[1].split("```")[0]
                    explanation = explanation.split("##")[0]
                    return explanation.strip()

        # No explicit explanation, return first paragraph
        paragraphs = content.split("\n\n")
        if paragraphs:
            return paragraphs[0].strip()

        return ""

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get code generation statistics"""
        if not self.generation_history:
            return {"total_generations": 0}

        return {
            "total_generations": len(self.generation_history),
            "by_language": self._count_by_language(),
            "average_confidence": sum(
                g.confidence_score for g in self.generation_history
            ) / len(self.generation_history),
            "total_cost": sum(
                g.metadata.get("cost", 0.0) for g in self.generation_history
            ),
            "with_tests": sum(
                1 for g in self.generation_history if g.tests
            ),
            "with_docs": sum(
                1 for g in self.generation_history if g.documentation
            )
        }

    def _count_by_language(self) -> Dict[str, int]:
        """Count generations by language"""
        counts = {}
        for gen in self.generation_history:
            counts[gen.language] = counts.get(gen.language, 0) + 1
        return counts
