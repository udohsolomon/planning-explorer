"""
AI-Powered Document Summarization Pipeline for Planning Applications

This module provides intelligent summarization capabilities using OpenAI GPT-4
and Claude 3.5, extracting key insights, risks, and opportunities from planning
documents and applications.
"""

import asyncio
import logging
import time
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import openai
import anthropic
from datetime import datetime

from app.core.ai_config import ai_config, AIModel, AIProvider
from app.models.planning import PlanningApplication

logger = logging.getLogger(__name__)


class SummaryType(str, Enum):
    """Types of summaries that can be generated"""
    GENERAL = "general"
    OPPORTUNITIES = "opportunities"
    RISKS = "risks"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    STAKEHOLDER = "stakeholder"


class SummaryLength(str, Enum):
    """Summary length options"""
    SHORT = "short"      # 1-2 sentences
    MEDIUM = "medium"    # 1 paragraph
    LONG = "long"        # Multi-paragraph detailed analysis
    EXECUTIVE = "executive"  # Executive summary format


@dataclass
class SummaryResult:
    """Result of document summarization"""
    summary: str
    key_points: List[str]
    sentiment: str
    complexity_score: float
    processing_time_ms: int
    confidence_score: float
    extracted_entities: Dict[str, List[str]]
    recommendations: List[str]
    model_used: str
    token_count: int


@dataclass
class DocumentContext:
    """Context information for document summarization"""
    document_type: str
    source: str
    creation_date: Optional[datetime]
    authority: Optional[str]
    related_applications: List[str]
    user_focus: Optional[str]


class DocumentSummarizer:
    """
    AI-powered document summarization service using multiple models
    for comprehensive planning document analysis.
    """

    def __init__(self):
        self.config = ai_config
        self._initialize_clients()
        self._load_prompt_templates()

    def _initialize_clients(self) -> None:
        """Initialize AI service clients"""
        self.openai_client = None
        self.anthropic_client = None

        # Initialize OpenAI client
        if self.config.settings.openai_api_key:
            openai.api_key = self.config.settings.openai_api_key
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.settings.openai_api_key)
            logger.info("OpenAI client initialized for summarization")

        # Initialize Anthropic client
        if self.config.settings.anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=self.config.settings.anthropic_api_key
            )
            logger.info("Anthropic client initialized for summarization")

        if not self.openai_client and not self.anthropic_client:
            logger.warning("No AI providers available for summarization")

    def _load_prompt_templates(self) -> None:
        """Load prompt templates for different summary types"""
        self.prompts = {
            SummaryType.GENERAL: {
                "system": """You are an expert planning consultant analyzing UK planning applications.
                Provide clear, professional summaries that highlight the most important aspects for property developers and investors.""",

                "user": """Analyze this planning application and provide a {length} summary focusing on:
                - Development proposal overview
                - Key planning considerations
                - Approval likelihood indicators
                - Timeline expectations

                Application: {content}

                Format your response as a professional planning summary."""
            },

            SummaryType.OPPORTUNITIES: {
                "system": """You are a business development specialist focusing on identifying commercial opportunities in planning applications.""",

                "user": """Analyze this planning application to identify business opportunities:
                - Investment potential
                - Market timing advantages
                - Strategic partnerships possibilities
                - Value creation opportunities

                Application: {content}

                Provide a {length} summary focused on commercial opportunities."""
            },

            SummaryType.RISKS: {
                "system": """You are a risk assessment specialist for planning and development projects.""",

                "user": """Analyze this planning application to identify risks and challenges:
                - Planning policy conflicts
                - Technical challenges
                - Community opposition factors
                - Regulatory compliance risks
                - Timeline and cost overrun risks

                Application: {content}

                Provide a {length} risk-focused summary."""
            },

            SummaryType.TECHNICAL: {
                "system": """You are a technical planning expert specializing in the technical aspects of development proposals.""",

                "user": """Analyze the technical aspects of this planning application:
                - Design and architectural considerations
                - Engineering requirements
                - Environmental impact factors
                - Infrastructure needs
                - Technical compliance requirements

                Application: {content}

                Provide a {length} technical summary."""
            },

            SummaryType.COMPLIANCE: {
                "system": """You are a planning policy and compliance specialist familiar with UK planning regulations.""",

                "user": """Analyze this planning application for policy compliance:
                - Local planning policy alignment
                - National planning framework compliance
                - Statutory requirements fulfillment
                - Consultation and procedure adherence
                - Conditions and obligations

                Application: {content}

                Provide a {length} compliance-focused summary."""
            },

            SummaryType.STAKEHOLDER: {
                "system": """You are a stakeholder engagement specialist analyzing community and stakeholder perspectives.""",

                "user": """Analyze stakeholder aspects of this planning application:
                - Community impact assessment
                - Public consultation outcomes
                - Stakeholder concerns and support
                - Local authority perspectives
                - Engagement recommendations

                Application: {content}

                Provide a {length} stakeholder-focused summary."""
            }
        }

    async def summarize_application(
        self,
        application: PlanningApplication,
        summary_type: SummaryType = SummaryType.GENERAL,
        length: SummaryLength = SummaryLength.MEDIUM,
        context: Optional[DocumentContext] = None
    ) -> SummaryResult:
        """
        Generate AI summary of a planning application.

        Args:
            application: Planning application to summarize
            summary_type: Type of summary to generate
            length: Desired summary length
            context: Additional context for summarization

        Returns:
            SummaryResult with comprehensive analysis
        """
        start_time = time.time()

        try:
            # Prepare content for summarization
            content = self._prepare_application_content(application)

            # Choose best available model
            model_choice = self._select_model(summary_type, len(content))

            # Generate summary using selected model
            if model_choice["provider"] == AIProvider.ANTHROPIC and self.anthropic_client:
                result = await self._summarize_with_claude(
                    content, summary_type, length, model_choice["model"], context
                )
            elif model_choice["provider"] == AIProvider.OPENAI and self.openai_client:
                result = await self._summarize_with_openai(
                    content, summary_type, length, model_choice["model"], context
                )
            else:
                # Fallback to rule-based summarization
                result = self._generate_fallback_summary(application, summary_type, length)

            # Post-process and enhance result
            enhanced_result = await self._enhance_summary_result(result, application, context)

            processing_time_ms = int((time.time() - start_time) * 1000)
            enhanced_result.processing_time_ms = processing_time_ms

            logger.info(f"Summarization completed in {processing_time_ms}ms for application {application.application_id}")
            return enhanced_result

        except Exception as e:
            logger.error(f"Error summarizing application {application.application_id}: {str(e)}")
            return self._generate_fallback_summary(application, summary_type, length)

    def _prepare_application_content(self, application: PlanningApplication) -> str:
        """Prepare application content for summarization"""
        content_parts = []

        # Basic information
        content_parts.append(f"Application ID: {application.application_id}")
        content_parts.append(f"Development Type: {application.development_type}")
        content_parts.append(f"Location: {application.address}")
        content_parts.append(f"Authority: {application.authority}")
        content_parts.append(f"Status: {application.status}")

        # Dates
        if application.date_received:
            content_parts.append(f"Received: {application.date_received.strftime('%Y-%m-%d')}")
        if application.decision_date:
            content_parts.append(f"Decision: {application.decision_date.strftime('%Y-%m-%d')}")

        # Main description
        if application.description:
            content_parts.append(f"\\nDescription: {application.description}")

        # Proposal details
        if application.proposal:
            content_parts.append(f"\\nProposal: {application.proposal}")

        # Additional fields
        for field in ['ward', 'parish', 'case_officer', 'agent', 'applicant']:
            value = getattr(application, field, None)
            if value:
                content_parts.append(f"{field.title()}: {value}")

        return "\\n".join(content_parts)

    def _select_model(self, summary_type: SummaryType, content_length: int) -> Dict[str, Any]:
        """Select the best model for the summarization task"""

        # Claude 3.5 Sonnet for detailed analysis and complex reasoning
        if summary_type in [SummaryType.OPPORTUNITIES, SummaryType.RISKS, SummaryType.COMPLIANCE]:
            if self.anthropic_client:
                return {"provider": AIProvider.ANTHROPIC, "model": AIModel.CLAUDE_3_5_SONNET}

        # GPT-4 for general summaries and technical analysis
        if summary_type in [SummaryType.GENERAL, SummaryType.TECHNICAL]:
            if self.openai_client:
                return {"provider": AIProvider.OPENAI, "model": AIModel.GPT_4}

        # Fallback to available provider
        if self.anthropic_client:
            return {"provider": AIProvider.ANTHROPIC, "model": AIModel.CLAUDE_3_5_SONNET}
        elif self.openai_client:
            return {"provider": AIProvider.OPENAI, "model": AIModel.GPT_4}

        # No providers available
        return {"provider": None, "model": None}

    async def _summarize_with_claude(
        self,
        content: str,
        summary_type: SummaryType,
        length: SummaryLength,
        model: AIModel,
        context: Optional[DocumentContext]
    ) -> SummaryResult:
        """Generate summary using Claude (Anthropic)"""
        try:
            prompt_template = self.prompts[summary_type]

            user_prompt = prompt_template["user"].format(
                content=content,
                length=length.value
            )

            response = await self.anthropic_client.messages.create(
                model=model.value,
                max_tokens=self._get_max_tokens_for_length(length),
                temperature=self.config.settings.temperature,
                system=prompt_template["system"],
                messages=[{"role": "user", "content": user_prompt}]
            )

            summary_text = response.content[0].text

            # Extract structured information
            key_points = self._extract_key_points(summary_text)
            sentiment = self._analyze_sentiment(summary_text)
            complexity_score = self._calculate_complexity_score(content)
            confidence_score = self._calculate_confidence_score(summary_text, content)
            entities = self._extract_entities(content)
            recommendations = self._extract_recommendations(summary_text)

            return SummaryResult(
                summary=summary_text.strip(),
                key_points=key_points,
                sentiment=sentiment,
                complexity_score=complexity_score,
                processing_time_ms=0,  # Will be set by caller
                confidence_score=confidence_score,
                extracted_entities=entities,
                recommendations=recommendations,
                model_used=f"Claude-{model.value}",
                token_count=response.usage.input_tokens + response.usage.output_tokens
            )

        except Exception as e:
            logger.error(f"Error with Claude summarization: {str(e)}")
            raise

    async def _summarize_with_openai(
        self,
        content: str,
        summary_type: SummaryType,
        length: SummaryLength,
        model: AIModel,
        context: Optional[DocumentContext]
    ) -> SummaryResult:
        """Generate summary using OpenAI GPT"""
        try:
            prompt_template = self.prompts[summary_type]

            user_prompt = prompt_template["user"].format(
                content=content,
                length=length.value
            )

            response = await self.openai_client.chat.completions.create(
                model=model.value,
                messages=[
                    {"role": "system", "content": prompt_template["system"]},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self._get_max_tokens_for_length(length),
                temperature=self.config.settings.temperature,
                top_p=self.config.settings.top_p
            )

            summary_text = response.choices[0].message.content

            # Extract structured information
            key_points = self._extract_key_points(summary_text)
            sentiment = self._analyze_sentiment(summary_text)
            complexity_score = self._calculate_complexity_score(content)
            confidence_score = self._calculate_confidence_score(summary_text, content)
            entities = self._extract_entities(content)
            recommendations = self._extract_recommendations(summary_text)

            return SummaryResult(
                summary=summary_text.strip(),
                key_points=key_points,
                sentiment=sentiment,
                complexity_score=complexity_score,
                processing_time_ms=0,  # Will be set by caller
                confidence_score=confidence_score,
                extracted_entities=entities,
                recommendations=recommendations,
                model_used=f"OpenAI-{model.value}",
                token_count=response.usage.prompt_tokens + response.usage.completion_tokens
            )

        except Exception as e:
            logger.error(f"Error with OpenAI summarization: {str(e)}")
            raise

    def _get_max_tokens_for_length(self, length: SummaryLength) -> int:
        """Get appropriate max tokens for summary length"""
        token_limits = {
            SummaryLength.SHORT: 150,
            SummaryLength.MEDIUM: 500,
            SummaryLength.LONG: 1200,
            SummaryLength.EXECUTIVE: 800
        }
        return token_limits.get(length, 500)

    def _extract_key_points(self, summary_text: str) -> List[str]:
        """Extract key points from summary text"""
        # Look for bullet points, numbered lists, or structured content
        key_points = []

        # Try to find bullet points
        bullet_points = re.findall(r'[•-]\s*(.+)', summary_text)
        if bullet_points:
            key_points.extend(bullet_points[:5])

        # Try to find numbered lists
        numbered_points = re.findall(r'\\d+\\.\\s*(.+)', summary_text)
        if numbered_points:
            key_points.extend(numbered_points[:5])

        # If no structured points found, extract sentences
        if not key_points:
            sentences = re.split(r'[.!?]+', summary_text)
            key_points = [s.strip() for s in sentences[:3] if len(s.strip()) > 20]

        return key_points[:5]  # Limit to 5 key points

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of the summary"""
        positive_words = [
            'approved', 'positive', 'favorable', 'strong', 'excellent', 'good',
            'beneficial', 'opportunity', 'advantage', 'success', 'support'
        ]
        negative_words = [
            'refused', 'rejected', 'negative', 'poor', 'weak', 'challenging',
            'risk', 'problem', 'concern', 'opposition', 'difficulty', 'unfavorable'
        ]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate complexity score based on content characteristics"""
        score = 0.0

        # Length factor
        if len(content) > 2000:
            score += 0.3
        elif len(content) > 1000:
            score += 0.2
        else:
            score += 0.1

        # Technical terms
        technical_terms = [
            'environmental', 'heritage', 'listed', 'conservation',
            'infrastructure', 'transport', 'drainage', 'flooding',
            'ecology', 'archaeology', 'contamination'
        ]
        content_lower = content.lower()
        technical_count = sum(1 for term in technical_terms if term in content_lower)
        score += min(0.4, technical_count * 0.05)

        # Major development indicators
        major_indicators = ['major', 'large', 'significant', 'substantial']
        if any(indicator in content_lower for indicator in major_indicators):
            score += 0.2

        return min(1.0, score)

    def _calculate_confidence_score(self, summary: str, original_content: str) -> float:
        """Calculate confidence in the summary quality"""
        confidence = 0.6  # Base confidence

        # Length appropriateness
        summary_length = len(summary)
        content_length = len(original_content)

        if 100 <= summary_length <= content_length * 0.3:
            confidence += 0.2

        # Content coverage (simple heuristic)
        important_words = ['development', 'planning', 'application', 'proposal']
        covered_words = sum(1 for word in important_words if word.lower() in summary.lower())
        confidence += (covered_words / len(important_words)) * 0.2

        return min(1.0, confidence)

    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities from content using pattern matching"""
        entities = {
            "locations": [],
            "people": [],
            "organizations": [],
            "dates": []
        }

        # Extract postcodes
        postcodes = re.findall(r'\\b[A-Z]{1,2}\\d[A-Z\\d]?\\s*\\d[A-Z]{2}\\b', content)
        entities["locations"].extend(postcodes)

        # Extract dates
        dates = re.findall(r'\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b', content)
        entities["dates"].extend(dates)

        # Extract potential person names (simple pattern)
        names = re.findall(r'\\b[A-Z][a-z]+\\s+[A-Z][a-z]+\\b', content)
        entities["people"].extend(names[:3])  # Limit to first 3

        return entities

    def _extract_recommendations(self, summary_text: str) -> List[str]:
        """Extract recommendations from summary text"""
        recommendations = []

        # Look for recommendation indicators
        rec_patterns = [
            r'(?:recommend|suggest|advise|should)\\s+(.+?)(?:\\.|$)',
            r'(?:it is|would be)\\s+(?:advisable|recommended)\\s+to\\s+(.+?)(?:\\.|$)'
        ]

        for pattern in rec_patterns:
            matches = re.findall(pattern, summary_text, re.IGNORECASE)
            recommendations.extend(matches)

        return recommendations[:3]  # Limit to top 3

    async def _enhance_summary_result(
        self,
        result: SummaryResult,
        application: PlanningApplication,
        context: Optional[DocumentContext]
    ) -> SummaryResult:
        """Enhance summary result with additional analysis"""

        # Add application-specific insights
        if not result.recommendations:
            result.recommendations = self._generate_default_recommendations(application)

        return result

    def _generate_default_recommendations(self, application: PlanningApplication) -> List[str]:
        """Generate default recommendations based on application characteristics"""
        recommendations = []

        if application.status == "submitted":
            recommendations.append("Monitor application progress through planning committee")

        if application.development_type == "residential":
            recommendations.append("Consider affordable housing requirements and local housing need")

        recommendations.append("Engage with planning authority early in the process")
        recommendations.append("Ensure all supporting documentation is comprehensive")

        return recommendations

    def _generate_fallback_summary(
        self,
        application: PlanningApplication,
        summary_type: SummaryType,
        length: SummaryLength
    ) -> SummaryResult:
        """Generate fallback summary when AI models are unavailable"""
        logger.warning(f"Using fallback summarization for application {application.application_id}")

        # Basic rule-based summary
        if length == SummaryLength.SHORT:
            summary = f"{application.development_type} development at {application.address}, status: {application.status}."
        elif length == SummaryLength.LONG:
            summary = f"""This planning application proposes {application.development_type} development at {application.address}.

            The application is currently {application.status} with {application.authority}.

            {application.description[:200] + '...' if application.description and len(application.description) > 200 else application.description or 'No detailed description available.'}

            Further analysis requires AI model availability for comprehensive insights."""
        else:  # MEDIUM
            summary = f"{application.development_type} development at {application.address}. Status: {application.status}. {application.description[:150] + '...' if application.description and len(application.description) > 150 else application.description or ''}"

        return SummaryResult(
            summary=summary,
            key_points=[
                f"Development type: {application.development_type}",
                f"Location: {application.address}",
                f"Status: {application.status}"
            ],
            sentiment="neutral",
            complexity_score=0.5,
            processing_time_ms=50,
            confidence_score=0.3,
            extracted_entities={"locations": [application.address], "people": [], "organizations": [application.authority], "dates": []},
            recommendations=["Consider detailed AI analysis when models are available"],
            model_used="fallback-rules",
            token_count=0
        )

    async def batch_summarize(
        self,
        applications: List[PlanningApplication],
        summary_type: SummaryType = SummaryType.GENERAL,
        length: SummaryLength = SummaryLength.MEDIUM,
        max_concurrent: int = 5
    ) -> List[SummaryResult]:
        """Batch summarize multiple applications"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def summarize_with_semaphore(app):
            async with semaphore:
                return await self.summarize_application(app, summary_type, length)

        tasks = [summarize_with_semaphore(app) for app in applications]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error summarizing application {applications[i].id}: {result}")
                processed_results.append(
                    self._generate_fallback_summary(applications[i], summary_type, length)
                )
            else:
                processed_results.append(result)

        return processed_results