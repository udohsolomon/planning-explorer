"""
AI Processing Tools

Tools for AI operations: embeddings, summarization, opportunity scoring.
Enables agents to leverage AI capabilities for Planning Explorer.
"""

from typing import Any, List, Dict, Optional
import openai
import anthropic

from .base_tool import BaseTool, ToolParameter
from app.core.config import settings


class EmbeddingTool(BaseTool):
    """Generate embeddings for text"""

    def __init__(self):
        super().__init__()
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def get_name(self) -> str:
        return "generate_embeddings"

    def get_description(self) -> str:
        return """Generate vector embeddings for text using OpenAI text-embedding-3-small.

Creates 1536-dimensional dense vectors for semantic search.
Optimized for Planning Explorer application descriptions."""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="text",
                type="string",
                description="Text to generate embeddings for",
                required=True
            ),
            ToolParameter(
                name="model",
                type="string",
                description="OpenAI model to use (default: text-embedding-3-small)",
                required=False,
                default="text-embedding-3-small"
            )
        ]

    async def execute(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> Any:
        """Generate embeddings using OpenAI"""
        self.validate_parameters(text=text)

        try:
            # Generate embedding via OpenAI API
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )

            embedding = response.data[0].embedding

            return {
                "success": True,
                "text_length": len(text),
                "embedding_dims": len(embedding),
                "embedding": embedding,
                "model": model,
                "tokens_used": response.usage.total_tokens
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Embedding generation failed: {str(e)}",
                "text_length": len(text)
            }


class SummarizationTool(BaseTool):
    """Summarize text using Claude"""

    def __init__(self):
        super().__init__()
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def get_name(self) -> str:
        return "summarize_text"

    def get_description(self) -> str:
        return """Summarize text using Claude AI.

Generates concise summaries optimized for planning applications.
Includes key details: location, development type, status, decision."""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="text",
                type="string",
                description="Text to summarize",
                required=True
            ),
            ToolParameter(
                name="max_length",
                type="number",
                description="Maximum summary length in words (default: 100)",
                required=False,
                default=100
            ),
            ToolParameter(
                name="focus",
                type="string",
                description="Focus area: general, technical, business",
                required=False,
                enum=["general", "technical", "business"],
                default="general"
            )
        ]

    async def execute(
        self,
        text: str,
        max_length: int = 100,
        focus: str = "general"
    ) -> Any:
        """Generate summary"""
        self.validate_parameters(text=text)

        try:
            # Build prompt based on focus
            focus_prompts = {
                "general": "Provide a concise summary highlighting the key points.",
                "technical": "Summarize focusing on technical details and specifications.",
                "business": "Summarize from a business perspective, highlighting commercial implications."
            }

            prompt = f"""{focus_prompts.get(focus, focus_prompts['general'])}

Text to summarize:
{text}

Provide a summary in approximately {max_length} words."""

            # Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.content[0].text

            return {
                "success": True,
                "original_length": len(text.split()),
                "summary_length": len(summary.split()),
                "summary": summary,
                "focus": focus,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Summarization failed: {str(e)}"
            }


class OpportunityScoringTool(BaseTool):
    """Calculate opportunity score for planning applications"""

    def __init__(self):
        super().__init__()
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def get_name(self) -> str:
        return "score_opportunity"

    def get_description(self) -> str:
        return """Calculate AI-powered opportunity score for planning applications.

Analyzes application details and returns:
- Overall score (0-100)
- Category scores (commercial, residential, infrastructure, etc.)
- Key factors influencing score
- Reasoning for score"""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="application_data",
                type="object",
                description="Planning application data (JSON object)",
                required=True
            ),
            ToolParameter(
                name="user_preferences",
                type="object",
                description="User preferences for scoring (optional)",
                required=False
            )
        ]

    async def execute(
        self,
        application_data: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Calculate opportunity score"""
        self.validate_parameters(application_data=application_data)

        try:
            # Build scoring prompt
            prompt = f"""Analyze this planning application and provide an opportunity score.

Application Details:
{self._format_application(application_data)}

{self._format_preferences(user_preferences) if user_preferences else ""}

Provide a JSON response with:
{{
    "overall_score": score_0_to_100,
    "category_scores": {{
        "commercial_potential": score,
        "approval_likelihood": score,
        "timeline_favorability": score,
        "market_demand": score
    }},
    "key_factors": ["factor 1", "factor 2", ...],
    "reasoning": "explanation of score",
    "risk_level": "low|medium|high"
}}"""

            # Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            import json
            result_text = response.content[0].text

            # Extract JSON from response
            try:
                # Try to find JSON in response
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    result_json = json.loads(result_text[start_idx:end_idx])
                else:
                    result_json = {"overall_score": 50, "reasoning": result_text}
            except json.JSONDecodeError:
                result_json = {"overall_score": 50, "reasoning": result_text}

            return {
                "success": True,
                "application_id": application_data.get("id"),
                "score": result_json.get("overall_score"),
                "category_scores": result_json.get("category_scores", {}),
                "key_factors": result_json.get("key_factors", []),
                "reasoning": result_json.get("reasoning", ""),
                "risk_level": result_json.get("risk_level", "medium"),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Opportunity scoring failed: {str(e)}",
                "application_id": application_data.get("id")
            }

    def _format_application(self, data: Dict[str, Any]) -> str:
        """Format application data for prompt"""
        return f"""
- ID: {data.get('id')}
- Location: {data.get('location', {}).get('address', 'N/A')}
- Development Type: {data.get('development_type', 'N/A')}
- Description: {data.get('description', 'N/A')[:500]}
- Status: {data.get('status', 'N/A')}
- Decision Date: {data.get('decision_date', 'N/A')}
- Authority: {data.get('authority', 'N/A')}
"""

    def _format_preferences(self, prefs: Dict[str, Any]) -> str:
        """Format user preferences"""
        return f"""
User Preferences:
- Preferred sectors: {prefs.get('sectors', [])}
- Preferred locations: {prefs.get('locations', [])}
- Risk tolerance: {prefs.get('risk_tolerance', 'medium')}
"""


class SemanticSearchTool(BaseTool):
    """Perform semantic search using embeddings"""

    def __init__(self):
        super().__init__()
        self.embedding_tool = EmbeddingTool()

    def get_name(self) -> str:
        return "semantic_search"

    def get_description(self) -> str:
        return """Perform semantic search by combining keyword and vector similarity.

Returns results ranked by semantic relevance to query."""

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True
            ),
            ToolParameter(
                name="filters",
                type="object",
                description="Additional filters (optional)",
                required=False
            ),
            ToolParameter(
                name="size",
                type="number",
                description="Number of results (default: 10)",
                required=False,
                default=10
            )
        ]

    async def execute(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 10
    ) -> Any:
        """Execute semantic search"""
        self.validate_parameters(query=query)

        try:
            # Generate query embedding
            embedding_result = await self.embedding_tool.execute(query)

            if not embedding_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to generate query embedding"
                }

            query_embedding = embedding_result["embedding"]

            # Build ES query with kNN search
            es_query = {
                "knn": {
                    "field": "description_embedding",
                    "query_vector": query_embedding,
                    "k": size,
                    "num_candidates": size * 10
                }
            }

            # Add filters if provided
            if filters:
                es_query["filter"] = [
                    {"term": {key: value}}
                    for key, value in filters.items()
                ]

            return {
                "success": True,
                "query": query,
                "query_type": "semantic",
                "es_query": es_query,
                "filters": filters,
                "size": size
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Semantic search failed: {str(e)}"
            }
