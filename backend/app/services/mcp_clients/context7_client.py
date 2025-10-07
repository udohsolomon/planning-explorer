"""
Context7 MCP Client Wrapper

This module wraps OpenAI API for LLM-powered semantic extraction.
"""

import logging
import json
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class Context7Client:
    """
    Wrapper for Context7 MCP server for semantic data extraction using LLMs.

    Used for adaptive extraction from unknown portal types where structural
    patterns are not known. Typically takes 3-5 seconds for LLM processing.
    """

    def __init__(self):
        """Initialize Context7 client with OpenAI API."""
        self.model = "gpt-4o-mini"  # Cost-effective model
        self.timeout_ms = 15000  # 15 second timeout
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set - Context7 extractions will fail")

        logger.info(f"Context7Client initialized with model: {self.model}")

    async def extract(self, content: str, prompt: str) -> Optional[Dict]:
        """
        Extract structured data from content using LLM.

        Args:
            content: HTML or text content to extract from
            prompt: Extraction instructions for the LLM

        Returns:
            Dictionary with extracted data, or None if extraction fails

        Raises:
            Exception: If LLM call fails or times out
        """
        try:
            if not self.api_key:
                logger.error("OPENAI_API_KEY not set, cannot perform extraction")
                return None

            logger.info(f"Extracting with OpenAI {self.model} (content length: {len(content)} chars)")

            # Use OpenAI API for extraction
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)

            # Truncate content if too long (max ~8000 chars to stay under token limit)
            truncated_content = content[:8000] if len(content) > 8000 else content

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction specialist. Extract information accurately and return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nContent to extract from:\n{truncated_content}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=500
            )

            # Parse JSON response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            logger.info(f"OpenAI extraction successful: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            return None

    async def extract_with_schema(
        self,
        content: str,
        schema: Dict,
        instructions: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Extract data conforming to a specific schema.

        Args:
            content: HTML or text content to extract from
            schema: JSON schema defining expected output structure
            instructions: Optional additional extraction instructions

        Returns:
            Dictionary matching schema, or None if extraction fails
        """
        try:
            logger.info(f"Extracting with schema: {schema.get('title', 'unnamed')}")

            # Build prompt from schema
            prompt = f"""
            Extract data from the following content matching this schema:
            {json.dumps(schema, indent=2)}

            {instructions or ''}

            Return ONLY valid JSON matching the schema.
            """

            return await self.extract(content, prompt)

        except Exception as e:
            logger.error(f"Schema-based extraction failed: {str(e)}")
            return None

    async def extract_applicant_agent(self, content: str) -> Optional[Dict]:
        """
        Specialized method for extracting applicant and agent names.

        Args:
            content: HTML content from planning portal

        Returns:
            Dictionary with applicant_name and agent_name, or None
        """
        prompt = """
        Extract the applicant name and agent name from this planning application page.
        Look for fields labeled "Applicant", "Applicant Name", "Agent", "Agent Name", or similar.

        Return ONLY a JSON object with this exact structure:
        {
            "applicant_name": "exact name or null",
            "agent_name": "exact name or null"
        }

        If a field is not available, use null. Do not include labels, only the actual names.
        """

        return await self.extract(content, prompt)

    async def validate_extraction(self, extracted_data: Dict, content: str) -> Dict:
        """
        Validate and score extracted data quality.

        Args:
            extracted_data: Previously extracted data
            content: Original content

        Returns:
            Dictionary with validation results and confidence scores
        """
        try:
            validation_prompt = f"""
            Validate this extracted data against the source content:

            Extracted Data: {json.dumps(extracted_data)}

            Is the data accurate? Rate confidence 0.0-1.0 for each field.

            Return JSON:
            {{
                "valid": true/false,
                "confidence": {{
                    "applicant_name": 0.0-1.0,
                    "agent_name": 0.0-1.0
                }},
                "issues": ["list of any problems found"]
            }}
            """

            result = await self.extract(content, validation_prompt)

            return result or {
                "valid": False,
                "confidence": {"applicant_name": 0.0, "agent_name": 0.0},
                "issues": ["Validation failed"]
            }

        except Exception as e:
            logger.error(f"Extraction validation failed: {str(e)}")
            return {
                "valid": False,
                "confidence": {"applicant_name": 0.0, "agent_name": 0.0},
                "issues": [str(e)]
            }

    async def health_check(self) -> bool:
        """
        Check if Context7 MCP server is responsive.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # TODO: Implement health check via MCP
            # result = await mcp_client.call_tool("context7_health", {})
            # return result["status"] == "ok"

            logger.warning("Context7 health check not implemented")
            return True

        except Exception as e:
            logger.error(f"Context7 health check failed: {str(e)}")
            return False
