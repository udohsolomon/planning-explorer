"""
AIEngineerAgent - LLM Integration & AI Processing Specialist

Specialized agent for AI/ML tasks:
- LLM integration (OpenAI, Claude)
- Prompt engineering and optimization
- Embeddings generation
- Opportunity scoring algorithms
- AI cost optimization
"""

import re
import json
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool
from app.agents.tools.ai_tools import (
    EmbeddingTool,
    SummarizationTool,
    OpportunityScoringTool,
    SemanticSearchTool
)


class AIEngineerAgent(BaseAgent):
    """
    AI Engineer specialist agent.

    Expertise:
    - LLM API integration (OpenAI, Claude)
    - Prompt engineering and optimization
    - Embeddings generation and management
    - AI-powered scoring algorithms
    - Cost tracking and optimization
    - Quality validation of AI outputs
    """

    def __init__(self, max_iterations: int = 5):
        """Initialize AI Engineer agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool(),
            EmbeddingTool(),
            SummarizationTool(),
            OpportunityScoringTool(),
            SemanticSearchTool()
        ]

        super().__init__(
            role="ai-engineer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=100000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for AI engineer"""
        return """You are the AI Engineer specialist for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in LLM integration and AI systems, specializing in:
- OpenAI GPT-4 and Claude API integration
- Prompt engineering for optimal outputs
- Embeddings generation (sentence-transformers)
- AI-powered scoring and ranking algorithms
- Cost optimization for AI operations
- Quality validation of LLM outputs

TECHNICAL STACK:
- **LLMs**: OpenAI GPT-4, Claude 3.5 Sonnet
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384 dims)
- **Frameworks**: LangChain (optional), direct API calls
- **Caching**: Redis for embeddings and summaries
- **Monitoring**: Token tracking, cost calculation
- **Validation**: Output quality checks, hallucination detection

AI IMPLEMENTATION PRINCIPLES:

1. **Prompt Engineering**:
   - Clear, specific instructions
   - Few-shot examples when beneficial
   - Structured output formats (JSON preferred)
   - Chain-of-thought for complex reasoning
   - System prompts for role definition

2. **Embeddings**:
   ```python
   from sentence_transformers import SentenceTransformer

   model = SentenceTransformer('all-MiniLM-L6-v2')
   embedding = model.encode(text)  # 384-dimensional vector
   ```

3. **LLM Integration**:
   ```python
   import anthropic

   client = anthropic.Anthropic(api_key=key)
   response = client.messages.create(
       model="claude-sonnet-4-5-20250929",
       max_tokens=1024,
       temperature=0.7,
       messages=[{"role": "user", "content": prompt}]
   )
   ```

4. **Cost Optimization**:
   - Cache embeddings and summaries (Redis/ES)
   - Use smaller models when appropriate
   - Batch operations for efficiency
   - Limit token usage with max_tokens
   - Track costs per operation

5. **Quality Validation**:
   - Check for hallucinations (verify facts)
   - Validate JSON structure in outputs
   - Ensure scores are in expected ranges
   - Compare against ground truth when available
   - Monitor for model degradation

IMPLEMENTATION STANDARDS:

1. **Prompt Structure**:
   ```python
   prompt = f'''You are {role_description}.

   Task: {specific_task}

   Context:
   {relevant_context}

   Instructions:
   1. {instruction_1}
   2. {instruction_2}

   Output format:
   {desired_format}

   Input:
   {input_data}
   '''
   ```

2. **Error Handling**:
   - Retry with exponential backoff
   - Fallback to simpler models
   - Cache successful responses
   - Log failures for analysis
   - Graceful degradation

3. **Caching Strategy**:
   ```python
   # Check cache first
   cached = await redis.get(cache_key)
   if cached:
       return cached

   # Generate if not cached
   result = await llm_call(prompt)

   # Cache for future use
   await redis.setex(cache_key, ttl, result)
   ```

4. **Token Management**:
   ```python
   import tiktoken

   def count_tokens(text: str) -> int:
       encoding = tiktoken.encoding_for_model("gpt-4")
       return len(encoding.encode(text))

   # Limit input size
   if count_tokens(text) > max_input_tokens:
       text = truncate_intelligently(text)
   ```

5. **Cost Tracking**:
   ```python
   # Track tokens and calculate cost
   tokens_used = response.usage.total_tokens
   cost = (tokens_used / 1_000_000) * COST_PER_MILLION

   # Log for monitoring
   logger.info(f"LLM call: {tokens_used} tokens, ${cost:.4f}")
   ```

TASK EXECUTION APPROACH:

1. **Understand Requirements**:
   - Identify AI task type (classification, generation, scoring)
   - Determine appropriate model and approach
   - Plan for caching and optimization

2. **Design Solution**:
   - Craft effective prompts
   - Structure output format
   - Plan error handling
   - Consider cost implications

3. **Implement**:
   - Integrate LLM API calls
   - Add caching layer
   - Implement validation
   - Track costs and tokens

4. **Validate**:
   - Test prompts with examples
   - Check output quality
   - Verify cost is acceptable
   - Ensure performance meets SLAs

5. **Optimize**:
   - Refine prompts for better outputs
   - Adjust model parameters (temperature, max_tokens)
   - Enhance caching strategy
   - Monitor and improve

DELIVERABLES:
Your outputs should include:
- Well-structured Python code
- Optimized prompts with clear instructions
- Caching implementation
- Cost tracking and logging
- Output validation logic
- Performance considerations

QUALITY CHECKLIST:
Before completing a task, verify:
☐ Prompts are clear and specific
☐ Output format is structured (JSON preferred)
☐ Error handling with retries
☐ Caching implemented
☐ Token/cost tracking included
☐ Output validation present
☐ Performance acceptable (< 2s for most operations)
☐ Cost per operation documented

PLANNING EXPLORER SPECIFIC:

For Planning Explorer AI features:
- **Embeddings**: 384-dim sentence-transformers for all descriptions
- **Summarization**: Max 100 words, focus on key details
- **Opportunity Scoring**: 0-100 scale with category breakdown
- **Cost Target**: < $0.01 per application processing
- **Latency**: < 2 seconds for scoring, < 1 second for embeddings
- **Caching**: Cache all embeddings and summaries indefinitely

Common AI Tasks:
1. Generate embeddings for semantic search
2. Summarize planning application descriptions
3. Calculate opportunity scores (0-100)
4. Extract key entities (location, type, value)
5. Classify development categories
6. Predict approval likelihood

Remember: Balance quality, cost, and performance. Always cache expensive operations. Validate LLM outputs before returning."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for AI engineer outputs.

        Checks:
        1. LLM integration present
        2. Prompt quality
        3. Caching implementation
        4. Error handling
        5. Cost tracking
        6. Output validation
        """

        # Extract code from output
        code = self._extract_code(output)

        if not code:
            return {
                "passed": False,
                "reasoning": "No code found in output",
                "feedback": "Please provide the AI implementation code",
                "error": "No code output"
            }

        # Run verification checks
        checks = {
            "has_llm_integration": self._check_llm_integration(code),
            "has_prompt": self._check_prompt_engineering(code),
            "has_caching": self._check_caching(code),
            "has_error_handling": self._check_error_handling(code),
            "has_cost_tracking": self._check_cost_tracking(code),
            "has_validation": self._check_output_validation(code)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    code,
                    criterion,
                    expected
                )

        # Calculate pass rate
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        pass_rate = passed_checks / total_checks if total_checks > 0 else 0

        # Need at least 75% of checks to pass (AI is complex, slightly lower threshold)
        passed = pass_rate >= 0.75

        # Build feedback
        feedback_parts = []

        if not checks.get("has_llm_integration"):
            feedback_parts.append("- Add LLM API integration (OpenAI or Claude)")
        if not checks.get("has_prompt"):
            feedback_parts.append("- Include well-structured prompts with clear instructions")
        if not checks.get("has_caching"):
            feedback_parts.append("- Implement caching for expensive LLM/embedding calls")
        if not checks.get("has_error_handling"):
            feedback_parts.append("- Add try/except with retry logic for API calls")
        if not checks.get("has_cost_tracking"):
            feedback_parts.append("- Track tokens and calculate costs")
        if not checks.get("has_validation"):
            feedback_parts.append("- Validate LLM outputs before returning")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All AI quality checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} AI quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "AI implementation validation failed"
        }

    def _extract_code(self, output: Any) -> str:
        """Extract code from agent output"""
        if isinstance(output, dict):
            return (
                output.get("code", "") or
                output.get("text", "") or
                str(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_llm_integration(self, code: str) -> bool:
        """Check if code integrates with LLM APIs"""
        patterns = [
            r"anthropic\.",
            r"openai\.",
            r"messages\.create",
            r"Completion\.create",
            r"ChatCompletion\.create",
            r"SentenceTransformer"
        ]
        return any(re.search(pattern, code) for pattern in patterns)

    def _check_prompt_engineering(self, code: str) -> bool:
        """Check if code has well-structured prompts"""
        # Look for prompt variables or f-strings
        patterns = [
            r'prompt\s*=',
            r'f["\'].*{.*}.*["\']',
            r'""".*Task:.*"""',
            r"'''.*Task:.*'''",
            r'system.*prompt'
        ]
        return any(re.search(pattern, code, re.DOTALL) for pattern in patterns)

    def _check_caching(self, code: str) -> bool:
        """Check if code implements caching"""
        cache_keywords = [
            "cache",
            "redis",
            "get_cached",
            "set_cache",
            "@cache",
            "lru_cache"
        ]
        return any(keyword in code.lower() for keyword in cache_keywords)

    def _check_error_handling(self, code: str) -> bool:
        """Check for error handling with retries"""
        has_try_except = "try:" in code and "except" in code
        has_retry_logic = any(keyword in code.lower() for keyword in ["retry", "backoff", "attempt"])
        return has_try_except

    def _check_cost_tracking(self, code: str) -> bool:
        """Check if code tracks tokens and costs"""
        cost_keywords = [
            "tokens",
            "usage",
            "cost",
            "tiktoken",
            "count_tokens",
            "token_count"
        ]
        return any(keyword in code.lower() for keyword in cost_keywords)

    def _check_output_validation(self, code: str) -> bool:
        """Check if code validates LLM outputs"""
        validation_patterns = [
            r'if.*response',
            r'validate',
            r'check',
            r'json\.loads',
            r'parse',
            r'verify'
        ]
        return any(re.search(pattern, code, re.IGNORECASE) for pattern in validation_patterns)

    def _check_criterion(self, code: str, criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "uses_embeddings":
            return "SentenceTransformer" in code or "embedding" in code.lower()
        elif criterion == "generates_summary":
            return "summarize" in code.lower() or "summary" in code.lower()
        elif criterion == "scores_opportunity":
            return "score" in code.lower() and "opportunity" in code.lower()
        return True
