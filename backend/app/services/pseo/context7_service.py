"""
Context7 Service for Industry-Specific Planning Context
FREE tier: 50 queries/day, no API key needed
"""

from typing import Dict, List, Optional
import requests
import os
from datetime import datetime


class Context7Service:
    """
    Get industry-specific planning context using Context7 API.
    FREE tier provides 50 queries/day without API key.
    Optional API key for higher limits and private repos.
    """

    def __init__(self):
        self.api_key = os.getenv('CONTEXT7_API_KEY')  # Optional
        self.base_url = "https://api.context7.com/v1"

        # Free tier: No auth needed for public docs
        self.headers = {}
        if self.api_key:
            self.headers = {"Authorization": f"Bearer {self.api_key}"}

        self.cache = {}  # Simple in-memory cache

    async def get_planning_policy_context(self, authority_name: str, topic: str) -> Dict:
        """
        Get planning policy context for specific topics.

        Args:
            authority_name: Name of the authority
            topic: Topic to get context for (e.g., 'affordable housing', 'design policy')

        Returns:
            Dict with context, definitions, and relevant information
        """

        cache_key = f"{authority_name}_{topic}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        query = f"{authority_name} planning {topic}"

        try:
            # Context7 provides up-to-date planning documentation context
            response = requests.post(
                f"{self.base_url}/context",
                headers=self.headers,
                json={
                    "query": query,
                    "domain": "uk_planning",  # Specify UK planning domain
                    "include_sources": True,
                    "max_results": 5
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                result = {
                    "topic": topic,
                    "context": data.get('context', ''),
                    "definitions": data.get('definitions', []),
                    "sources": data.get('sources', []),
                    "retrieved_at": datetime.now().isoformat()
                }

                self.cache[cache_key] = result
                return result

            else:
                # Fallback to generic context
                return self._get_generic_planning_context(topic)

        except Exception as e:
            print(f"Context7 error for {query}: {e}")
            return self._get_generic_planning_context(topic)

    async def get_local_plan_context(self, authority_name: str) -> Dict:
        """Get context about local plan requirements and structure"""

        topics = [
            "local plan requirements",
            "housing allocation policy",
            "development management policies"
        ]

        contexts = []
        for topic in topics:
            context = await self.get_planning_policy_context(authority_name, topic)
            if context.get('context'):
                contexts.append(context)

        return {
            "authority": authority_name,
            "local_plan_contexts": contexts,
            "summary": self._summarize_contexts(contexts)
        }

    async def get_application_type_context(self, app_type: str) -> Dict:
        """Get context about specific application types"""

        query = f"UK planning {app_type} application requirements"

        try:
            response = requests.post(
                f"{self.base_url}/context",
                headers=self.headers,
                json={
                    "query": query,
                    "domain": "uk_planning",
                    "format": "structured"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "application_type": app_type,
                    "requirements": data.get('requirements', []),
                    "typical_conditions": data.get('conditions', []),
                    "common_refusal_reasons": data.get('refusal_reasons', []),
                    "context": data.get('context', '')
                }

        except Exception as e:
            print(f"Context7 error for {app_type}: {e}")

        return self._get_generic_app_type_context(app_type)

    async def get_policy_explanation(self, policy_name: str) -> Dict:
        """Get explanation of specific planning policies"""

        query = f"UK planning policy {policy_name} explanation"

        try:
            response = requests.post(
                f"{self.base_url}/explain",
                headers=self.headers,
                json={
                    "topic": policy_name,
                    "domain": "uk_planning_law",
                    "detail_level": "comprehensive"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "policy": policy_name,
                    "explanation": data.get('explanation', ''),
                    "key_points": data.get('key_points', []),
                    "related_policies": data.get('related', [])
                }

        except Exception as e:
            print(f"Context7 error for policy {policy_name}: {e}")

        return {
            "policy": policy_name,
            "explanation": f"Planning policy {policy_name}",
            "key_points": [],
            "related_policies": []
        }

    async def enrich_authority_data(self, authority: Dict, scraped_data: Dict) -> Dict:
        """
        Enrich authority data with Context7 industry context.

        Args:
            authority: Authority metadata
            scraped_data: Data scraped from authority website

        Returns:
            Dict with enriched context
        """

        enriched = {
            "authority": authority['name'],
            "contexts": {}
        }

        # Get context for local plan
        if scraped_data.get('local_plan'):
            enriched['contexts']['local_plan'] = await self.get_local_plan_context(
                authority['name']
            )

        # Get context for policies
        if scraped_data.get('policies', {}).get('policy_areas'):
            policy_contexts = []
            for policy in scraped_data['policies']['policy_areas'][:5]:  # Top 5 policies
                context = await self.get_policy_explanation(policy['name'])
                policy_contexts.append(context)

            enriched['contexts']['policies'] = policy_contexts

        # Add general planning context
        enriched['contexts']['general'] = await self.get_planning_policy_context(
            authority['name'],
            "planning application process"
        )

        return enriched

    def _get_generic_planning_context(self, topic: str) -> Dict:
        """Fallback generic context when API unavailable"""

        generic_contexts = {
            "affordable housing": {
                "context": "Affordable housing policies typically require a percentage of new developments to provide affordable units. Thresholds vary by authority but commonly apply to developments of 10+ dwellings.",
                "key_points": [
                    "Percentage requirement (typically 20-40%)",
                    "Threshold triggers (often 10+ dwellings)",
                    "Tenure split requirements",
                    "Viability assessment provisions"
                ]
            },
            "design policy": {
                "context": "Design policies ensure developments are of high quality and appropriate to their context. They typically cover layout, scale, massing, materials, and relationship to surroundings.",
                "key_points": [
                    "Character and appearance",
                    "Scale and massing",
                    "Materials and detailing",
                    "Landscaping and public realm"
                ]
            },
            "heritage": {
                "context": "Heritage policies protect listed buildings, conservation areas, and archaeological sites. Development affecting heritage assets requires special consideration.",
                "key_points": [
                    "Listed building consent requirements",
                    "Conservation area considerations",
                    "Heritage impact assessment",
                    "Preservation vs. enabling development"
                ]
            }
        }

        return generic_contexts.get(topic, {
            "context": f"Planning context for {topic}",
            "key_points": []
        })

    def _get_generic_app_type_context(self, app_type: str) -> Dict:
        """Fallback context for application types"""

        contexts = {
            "Householder": {
                "requirements": ["Site plan", "Elevations", "Floor plans"],
                "typical_conditions": ["Materials to match existing", "Permitted development rights removal"],
                "common_refusal_reasons": ["Overdevelopment", "Impact on amenity", "Design quality"]
            },
            "Full Planning": {
                "requirements": ["Full plans and elevations", "Supporting statements", "Technical assessments"],
                "typical_conditions": ["Construction management plan", "Landscaping scheme", "Materials approval"],
                "common_refusal_reasons": ["Policy conflict", "Highway safety", "Residential amenity"]
            },
            "Outline": {
                "requirements": ["Site location plan", "Parameters", "Access details"],
                "typical_conditions": ["Reserved matters approval", "Phasing plan", "S106 agreement"],
                "common_refusal_reasons": ["Premature development", "Sustainability", "Infrastructure capacity"]
            }
        }

        return contexts.get(app_type, {
            "requirements": [],
            "typical_conditions": [],
            "common_refusal_reasons": []
        })

    def _summarize_contexts(self, contexts: List[Dict]) -> str:
        """Create summary from multiple contexts"""

        if not contexts:
            return ""

        summary_parts = []
        for ctx in contexts:
            if ctx.get('context'):
                summary_parts.append(ctx['context'][:200])

        return " ".join(summary_parts)

    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""

        return {
            "cached_queries": len(self.cache),
            "api_key_configured": bool(self.api_key),
            "tier": "Premium" if self.api_key else "Free (50/day)"
        }


# Utility function for testing
async def test_context7_service():
    """Test Context7 service"""

    service = Context7Service()

    print(f"Context7 Status: {service.get_usage_stats()}\n")

    # Test policy context
    print("Testing affordable housing context...")
    context = await service.get_planning_policy_context(
        "Birmingham City Council",
        "affordable housing"
    )
    print(f"Context: {context.get('context', 'N/A')[:200]}...\n")

    # Test application type context
    print("Testing householder application context...")
    app_context = await service.get_application_type_context("Householder")
    print(f"Requirements: {app_context.get('requirements', [])}\n")

    # Test enrichment
    test_authority = {
        "name": "Test Council"
    }

    test_scraped = {
        "local_plan": {"summary": "Test plan"},
        "policies": {
            "policy_areas": [
                {"name": "Housing Policy"},
                {"name": "Design Standards"}
            ]
        }
    }

    print("Testing data enrichment...")
    enriched = await service.enrich_authority_data(test_authority, test_scraped)
    print(f"Enriched contexts: {list(enriched.get('contexts', {}).keys())}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_context7_service())
