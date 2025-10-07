"""
Anthropic Claude Content Generator for pSEO
Generates SEO-optimized, authority-specific planning content
Cost: ~$0.20 per page (6 AI-generated sections)
"""

from typing import Dict, List, Optional
import anthropic
import os
from datetime import datetime
import json


class ContentGenerator:
    """
    AI-powered content generation using Claude Sonnet 4.5.
    Generates comprehensive, SEO-optimized content for each authority.
    """

    def __init__(self):
        # Check for z.ai proxy or direct Anthropic
        self.base_url = os.getenv('ANTHROPIC_BASE_URL')
        self.auth_token = os.getenv('ANTHROPIC_AUTH_TOKEN')
        self.api_key = os.getenv('ANTHROPIC_API_KEY')

        # Use z.ai proxy if configured, otherwise direct Anthropic
        if self.base_url and self.auth_token:
            # z.ai proxy
            self.client = anthropic.Anthropic(
                api_key=self.auth_token,
                base_url=self.base_url
            )
        elif self.api_key:
            # Direct Anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError("Either ANTHROPIC_API_KEY or (ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN) must be set")

        self.model = "claude-sonnet-4-5-20250929"

        # Token limits and costs
        self.max_tokens_per_section = {
            'introduction': 2500,
            'data_insights': 1500,
            'policy_summary': 2000,
            'comparative_analysis': 1600,
            'faq': 4000,
            'future_outlook': 1600
        }

        # Track costs
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    async def generate_all_sections(
        self,
        authority: Dict,
        metrics: Dict,
        trends: Dict,
        scraped: Dict,
        external: Dict = None,
        comparative: Dict = None
    ) -> Dict:
        """
        Generate all AI content sections for an authority page.

        Returns:
            Dict with all generated content sections
        """

        generated = {}

        # Generate each section
        generated['introduction'] = await self.generate_introduction(
            authority, metrics, scraped, external or {}
        )

        generated['data_insights'] = await self.generate_data_insights(
            metrics, trends
        )

        # Ensure local_plan and policies are dicts before passing
        local_plan = scraped.get('local_plan', {})
        local_plan = local_plan if isinstance(local_plan, dict) else {}
        policies = scraped.get('policies', {})
        policies = policies if isinstance(policies, dict) else {}

        generated['policy_summary'] = await self.generate_policy_summary(
            authority, local_plan, policies
        )

        if comparative:
            generated['comparative_analysis'] = await self.generate_comparative_analysis(
                authority, metrics, comparative
            )

        generated['faq'] = await self.generate_faq(
            authority, metrics, scraped
        )

        generated['future_outlook'] = await self.generate_future_outlook(
            authority, trends, scraped
        )

        # Calculate total cost for this page
        page_cost = self._calculate_page_cost()
        generated['_metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'total_words': self._count_total_words(generated),
            'cost': page_cost,
            'model': self.model
        }

        return generated

    async def generate_introduction(
        self,
        authority: Dict,
        metrics: Dict,
        scraped: Dict,
        external: Dict
    ) -> str:
        """Generate comprehensive 900-1,100 word introduction"""

        news_summary = self._format_news_for_prompt(scraped.get('news', [])[:3])

        # Handle local_plan safely - might be dict, list, or None
        local_plan = scraped.get('local_plan', {})
        if isinstance(local_plan, dict):
            local_plan_summary = local_plan.get('summary', 'Not available')[:500]
        else:
            local_plan_summary = 'Not available'

        prompt = f"""Generate a comprehensive, SEO-optimized introduction for {authority['name']}'s planning applications page on Planning Explorer.

AUTHORITY CONTEXT:
- Name: {authority['name']}
- Type: {authority.get('type', 'Local Authority')}
- Region: {authority.get('region', 'UK')}
- Population: {external.get('demographics', {}).get('population', 'N/A')}
- Geographic character: {authority.get('geographic_type', 'Mixed urban/rural')}

PLANNING METRICS (Last 12 months):
- Total applications: {metrics.get('total_applications_ytd', 0)}
- Approval rate: {metrics.get('approval_rate', 0):.1f}%
- Refusal rate: {metrics.get('refusal_rate', 0):.1f}%
- Average decision time: {metrics.get('avg_decision_days', 0):.0f} days
- Active applications: {metrics.get('active_applications', 0)}

RECENT NEWS & DEVELOPMENTS:
{news_summary}

LOCAL PLAN STATUS:
{local_plan_summary}

WRITE 900-1,100 WORDS covering these topics in this order:

1. **Opening paragraph (150-200 words)**:
   - Introduce Planning Explorer as the UK's leading AI-powered planning intelligence platform
   - Position this page as the definitive resource for {authority['name']} planning data
   - Highlight what makes this authority unique (geography, demographics, planning pressures)
   - Include primary keyword naturally: "{authority['name']} planning applications"

2. **Planning jurisdiction & activity (200-250 words)**:
   - Describe the authority's geographic coverage and planning scope
   - Detail current planning activity levels with specific metrics
   - Explain recent trends (increasing/decreasing/stable) with data
   - Compare to regional peers briefly

3. **Local planning landscape (200-250 words)**:
   - Summarize local plan status and key policies
   - Highlight priority development areas or constraints
   - Mention conservation areas, green belt, or heritage considerations
   - Reference major recent developments or controversies

4. **Current development climate (200-250 words)**:
   - Analyze approval rates and what they indicate
   - Discuss decision timelines and efficiency
   - Highlight any seasonal or cyclical patterns
   - Note types of development that perform well/poorly

5. **How Planning Explorer helps (150-200 words)**:
   - Explain how our platform provides comprehensive intelligence
   - Highlight AI-powered insights, semantic search, comparative data
   - Mention downloadable reports and real-time tracking
   - Position as essential tool for developers, consultants, investors

REQUIREMENTS:
- Professional, authoritative tone
- Highly specific with numbers, dates, percentages
- Natural keyword integration: "{authority['name']} planning applications", "planning permission {authority.get('area', authority['name'])}", "development applications"
- Avoid marketing fluff and generic statements
- Use clear paragraph structure with topic sentences
- Include recent concrete examples where possible
- Write for property professionals: developers, agents, investors
- Make it actionable and insight-driven

LENGTH: Exactly 900-1,100 words.
FORMAT: Plain text with paragraph breaks between sections."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens_per_section['introduction'],
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        self._track_usage(response.usage)
        return response.content[0].text

    async def generate_data_insights(self, metrics: Dict, trends: Dict) -> str:
        """Generate 400-500 word data analysis insights"""

        monthly_summary = self._format_trends_for_prompt(trends.get('monthly_data', []))
        app_types_summary = self._format_app_types_for_prompt(metrics.get('by_type', []))

        prompt = f"""Analyze planning application data and generate strategic insights.

CURRENT YEAR METRICS:
- Total applications: {metrics.get('total_applications_ytd', 0)}
- Approval rate: {metrics.get('approval_rate', 0):.1f}%
- Refusal rate: {metrics.get('refusal_rate', 0):.1f}%
- Average decision time: {metrics.get('avg_decision_days', 0):.0f} days
- Median decision time: {metrics.get('median_decision_days', 0):.0f} days

24-MONTH TREND DATA:
{monthly_summary}

YEAR-OVER-YEAR:
- Volume change: {trends.get('yoy_change', 0):.1f}%
- Trend direction: {trends.get('trend_direction', 'stable')}

APPLICATION TYPE BREAKDOWN:
{app_types_summary}

GENERATE 400-500 WORDS analyzing:

1. **Primary trends (100-120 words)**:
   - Overall trajectory (increasing/declining/stable)
   - Key patterns in the 24-month data
   - Significant month-to-month variations
   - Year-over-year performance

2. **Application type insights (100-120 words)**:
   - Which types are most/least successful
   - Approval rate variations by type
   - Decision time differences by type
   - Volume distribution analysis

3. **Seasonal patterns (80-100 words)**:
   - Identify peak and low activity months
   - Explain approval rate seasonality
   - Decision time seasonal variations
   - Strategic timing recommendations

4. **Notable anomalies (80-100 words)**:
   - Unusual spikes or drops
   - Policy changes reflected in data
   - Significant outlier months
   - Potential external factors

5. **Actionable intelligence (80-100 words)**:
   - Best times to submit applications
   - Application types with highest success
   - Decision timeline expectations
   - Strategic recommendations for developers

REQUIREMENTS:
- Use highly specific numbers: "March 2025 saw 127 applications, 15% above monthly average"
- Data-driven language: "Analysis reveals...", "Trends indicate...", "Statistical evidence shows..."
- Connect patterns to real-world factors (policy changes, economic conditions)
- Provide actionable takeaways
- Reference percentiles and comparative benchmarks
- Be authoritative but accessible

LENGTH: 400-500 words
FORMAT: Flowing paragraphs with clear topic transitions"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens_per_section['data_insights'],
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        self._track_usage(response.usage)
        return response.content[0].text

    async def generate_policy_summary(
        self,
        authority: Dict,
        local_plan: Dict,
        policies: Dict
    ) -> str:
        """Generate 600-800 word policy analysis"""

        # Handle local_plan and policies safely
        if not isinstance(local_plan, dict):
            local_plan = {}
        if not isinstance(policies, dict):
            policies = {}

        policy_areas = self._format_policies_for_prompt(policies.get('policy_areas', []))
        spds = self._format_spds_for_prompt(policies.get('spds', []))

        prompt = f"""Create comprehensive planning policy summary for {authority['name']}.

LOCAL PLAN:
- Summary: {local_plan.get('summary', 'Not available')}
- Adoption date: {local_plan.get('adoption_date', 'Unknown')}
- Review date: {local_plan.get('review_date', 'Unknown')}
- Documents: {len(local_plan.get('documents', []))} available

KEY PLANNING POLICIES:
{policy_areas}

SUPPLEMENTARY PLANNING DOCUMENTS:
{spds}

GENERATE 600-800 WORDS covering:

1. **Local plan overview (150-180 words)**:
   - Plan status (adopted/emerging/under review)
   - Core strategy and vision
   - Plan period and coverage
   - Housing targets and delivery strategy
   - Key site allocations

2. **Core planning policies (180-220 words)**:
   - Housing policy framework
   - Design and character requirements
   - Heritage and conservation approach
   - Environmental and sustainability policies
   - Infrastructure and S106/CIL requirements
   - Quote specific policy numbers where possible (e.g., "Policy H3 requires...")

3. **Development requirements (150-180 words)**:
   - Affordable housing thresholds and percentages
   - Parking standards
   - Open space requirements
   - Design quality expectations
   - Sustainability standards (BREEAM, energy)

4. **SPDs and guidance (120-150 words)**:
   - Key supplementary documents
   - Topic-specific guidance
   - Design codes and area frameworks
   - When SPDs apply

5. **Policy implications for applicants (100-120 words)**:
   - How policies influence approval decisions
   - Common policy-based refusal reasons
   - Pre-application advice importance
   - Strategies for policy compliance

REQUIREMENTS:
- Quote specific policy references where possible
- Include numerical thresholds (e.g., "30% affordable housing on sites of 10+ dwellings")
- Explain technical terms clearly
- Connect policies to actual approval patterns
- Provide actionable guidance for applicants
- Highlight recent policy changes or updates
- Be authoritative and precise

LENGTH: 600-800 words
FORMAT: Clear paragraphs with logical flow"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens_per_section['policy_summary'],
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        self._track_usage(response.usage)
        return response.content[0].text

    async def generate_comparative_analysis(
        self,
        authority: Dict,
        metrics: Dict,
        comparative: Dict
    ) -> str:
        """Generate 500-600 word comparative analysis"""

        # Ensure regional and national are dicts, not lists
        regional = comparative.get('regional', {})
        regional = regional if isinstance(regional, dict) else {}
        national = comparative.get('national', {})
        national = national if isinstance(national, dict) else {}

        prompt = f"""Generate comprehensive comparative analysis for {authority['name']}.

THIS AUTHORITY:
- Approval rate: {metrics.get('approval_rate', 0):.1f}%
- Decision time: {metrics.get('avg_decision_days', 0):.0f} days
- Application volume: {metrics.get('total_applications_ytd', 0)}

REGIONAL CONTEXT ({regional.get('total_authorities', 0)} authorities in {authority.get('region', 'UK')}):
- Regional average approval: {regional.get('regional_avg_approval', 0):.1f}%
- Regional average decision time: {regional.get('regional_avg_days', 0):.0f} days
- This authority's rank: {regional.get('authority_rank', 'N/A')} of {regional.get('total_authorities', 0)}

NATIONAL BENCHMARKS (425 UK authorities):
- National median approval: {national.get('national_median_approval', 0):.1f}%
- Decision time benchmarks:
  - 25th percentile: {national.get('decision_days_benchmarks', {}).get('p25', 0):.0f} days
  - Median: {national.get('decision_days_benchmarks', {}).get('p50', 0):.0f} days
  - 75th percentile: {national.get('decision_days_benchmarks', {}).get('p75', 0):.0f} days

GENERATE 500-600 WORDS analyzing:

1. **Regional performance (150-180 words)**:
   - How this authority compares to regional peers
   - Ranking and percentile position
   - Key differentiators from regional average
   - Performance relative to top regional authorities
   - Regional context factors

2. **National positioning (150-180 words)**:
   - National percentile rankings for key metrics
   - Comparison to national median and benchmarks
   - Outlier status (if applicable)
   - What national comparison reveals

3. **Performance drivers (100-130 words)**:
   - Factors explaining higher/lower approval rates
   - Reasons for faster/slower decision times
   - Policy, resourcing, or process differences
   - Local plan status impact

4. **Strategic implications (100-130 words)**:
   - What comparison means for developers/applicants
   - When this authority is favorable/unfavorable
   - Application strategy considerations
   - Realistic expectations vs. benchmarks

REQUIREMENTS:
- Be highly specific: "Ranks 12th out of 38 regional authorities with 87.3% approval rate"
- Explain causation: "Higher approval rates likely reflect recent local plan adoption"
- Provide strategic guidance
- Use percentiles and rankings extensively
- Compare both approval rates AND decision times
- Note trade-offs (e.g., high approval but slow)

LENGTH: 500-600 words"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens_per_section['comparative_analysis'],
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        self._track_usage(response.usage)
        return response.content[0].text

    async def generate_faq(
        self,
        authority: Dict,
        metrics: Dict,
        scraped: Dict
    ) -> str:
        """Generate 15-18 authority-specific FAQs"""

        prompt = f"""Generate 15-18 frequently asked questions specific to {authority['name']} planning applications.

AUTHORITY DATA:
- Name: {authority['name']}
- Average decision time: {metrics.get('avg_decision_days', 0):.0f} days
- Median decision time: {metrics.get('median_decision_days', 0):.0f} days
- Approval rate: {metrics.get('approval_rate', 0):.1f}%
- Refusal rate: {metrics.get('refusal_rate', 0):.1f}%
- Active applications: {metrics.get('active_applications', 0)}

GENERATE 15-18 Q&A PAIRS covering:

TOPICS (minimum questions per topic):
1. Application timelines (3 questions)
2. Approval likelihood by type (2 questions)
3. Committee processes (2 questions)
4. Local requirements (2-3 questions)
5. Application tracking (1-2 questions)
6. Appeals process (1-2 questions)
7. Pre-application advice (1 question)
8. Common refusal reasons (1-2 questions)
9. Conservation/heritage (1 question)
10. Fees and charges (1 question)

REQUIREMENTS FOR EACH Q&A:
- Question: Natural language (how real users ask)
- Answer: 75-125 words
- Use actual authority data and percentages
- Include specific examples
- Provide actionable information
- Link to resources where relevant
- Be authority-specific (not generic)

FORMAT:
**Q: [Question]**

A: [Answer with specific data, examples, and actionable guidance. 75-125 words.]

EXAMPLE:
**Q: How long do planning applications typically take in {authority['name']}?**

A: Based on the last 12 months of data, planning applications in {authority['name']} take an average of {metrics.get('avg_decision_days', 0):.0f} days from validation to decision, with a median of {metrics.get('median_decision_days', 0):.0f} days. Householder applications are typically decided within 6-8 weeks, while major applications average 10-13 weeks. The authority determines {metrics.get('approval_rate', 0):.0f}% of applications within statutory timescales. Applications requiring committee review add an additional 4-6 weeks. You can track your application status at the authority's planning portal.

GENERATE ALL 15-18 Q&A PAIRS NOW:"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens_per_section['faq'],
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        self._track_usage(response.usage)
        return response.content[0].text

    async def generate_future_outlook(
        self,
        authority: Dict,
        trends: Dict,
        scraped: Dict
    ) -> str:
        """Generate 500-600 word future outlook"""

        recent_months = self._format_recent_months(trends.get('monthly_data', [])[-6:])

        # Handle local_plan safely
        local_plan = scraped.get('local_plan', {})
        if not isinstance(local_plan, dict):
            local_plan = {}

        prompt = f"""Generate forward-looking planning outlook for {authority['name']}.

RECENT TRENDS:
- 24-month trajectory: {trends.get('trend_direction', 'stable')} ({trends.get('yoy_change', 0):+.1f}% YoY)
- Monthly pattern: {recent_months}

LOCAL PLAN STATUS:
{local_plan.get('summary', 'Not available')[:300]}
Review date: {local_plan.get('review_date', 'Unknown')}

GENERATE 500-600 WORDS covering:

1. **Pipeline projects (150-180 words)**:
   - Major developments pending decision
   - Significant allocated sites coming forward
   - Infrastructure projects influencing planning
   - Anticipated large applications

2. **Policy evolution (120-150 words)**:
   - Local plan review status and timeline
   - Emerging policy changes
   - New SPDs in development
   - National policy impacts (NPPF updates, etc.)

3. **Trend predictions (120-150 words)**:
   - Forecast application volumes (based on trajectory)
   - Expected approval rate evolution
   - Anticipated processing time changes
   - Application type shifts

4. **Opportunities & challenges (110-120 words)**:
   - Growth areas and hotspots for next 12-24 months
   - Development types likely to succeed
   - Constraint areas and challenges
   - Strategic opportunities for developers/investors

REQUIREMENTS:
- Balance data-driven predictions with policy context
- Cite specific pending projects and allocations where possible
- Provide timeline estimates where possible
- Be realistic, not speculative
- Include opportunity identification
- Note risks and potential obstacles

LENGTH: 500-600 words
FORMAT: Forward-looking analytical narrative"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens_per_section['future_outlook'],
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        self._track_usage(response.usage)
        return response.content[0].text

    # Helper methods for formatting data

    def _format_news_for_prompt(self, news: List[Dict]) -> str:
        """Format news items for prompt"""
        if not news:
            return "No recent news available"
        return "\n".join([f"- {item.get('title', 'Untitled')} ({item.get('date', 'Recent')})" for item in news[:3]])

    def _format_trends_for_prompt(self, monthly_data: List[Dict]) -> str:
        """Format monthly trends for prompt"""
        if not monthly_data:
            return "No trend data available"
        return "\n".join([
            f"- {m.get('month', 'Unknown')}: {m.get('total_applications', 0)} apps, "
            f"{m.get('approval_rate', 0):.1f}% approved, {m.get('avg_decision_days', 0):.0f} days"
            for m in monthly_data[-12:]
        ])

    def _format_app_types_for_prompt(self, types: List[Dict]) -> str:
        """Format application types for prompt"""
        if not types:
            return "No application type data available"
        return "\n".join([
            f"- {t.get('type', 'Unknown')}: {t.get('count', 0)} apps, "
            f"{t.get('approval_rate', 0):.1f}% approved, {t.get('avg_decision_days', 0):.0f} days avg"
            for t in types[:10]
        ])

    def _format_policies_for_prompt(self, policies: List[Dict]) -> str:
        """Format policies for prompt"""
        if not policies:
            return "No policy data available"
        return "\n".join([
            f"- {p.get('name', 'Unnamed')}: {p.get('description', '')[:150]}"
            for p in policies[:10]
        ])

    def _format_spds_for_prompt(self, spds: List[Dict]) -> str:
        """Format SPDs for prompt"""
        if not spds:
            return "No SPD data available"
        return "\n".join([f"- {spd.get('title', 'Untitled')}" for spd in spds[:10]])

    def _format_recent_months(self, months: List[Dict]) -> str:
        """Format recent months for prompt"""
        if not months:
            return "No recent data"
        return "; ".join([f"{m.get('month', 'Unknown')}: {m.get('total_applications', 0)} apps" for m in months])

    def _track_usage(self, usage):
        """Track API usage and costs"""
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens

        # Claude Sonnet 4.5 pricing (per million tokens)
        input_cost_per_million = 3.00
        output_cost_per_million = 15.00

        input_cost = (usage.input_tokens / 1_000_000) * input_cost_per_million
        output_cost = (usage.output_tokens / 1_000_000) * output_cost_per_million

        self.total_cost += (input_cost + output_cost)

    def _calculate_page_cost(self) -> float:
        """Calculate total cost for current page"""
        return self.total_cost

    def _count_total_words(self, content: Dict) -> int:
        """Count total words in generated content"""
        total = 0
        for key, value in content.items():
            if isinstance(value, str) and not key.startswith('_'):
                total += len(value.split())
        return total

    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
            "avg_cost_per_page": round(self.total_cost, 4) if self.total_cost > 0 else 0
        }

    def reset_usage(self):
        """Reset usage tracking"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0


# Utility function for testing
async def test_content_generator():
    """Test content generator"""

    generator = ContentGenerator()

    test_authority = {
        'name': 'Birmingham City Council',
        'type': 'Metropolitan Borough',
        'region': 'West Midlands',
        'area': 'Birmingham'
    }

    test_metrics = {
        'total_applications_ytd': 1247,
        'approval_rate': 87.3,
        'refusal_rate': 9.2,
        'avg_decision_days': 67,
        'median_decision_days': 58,
        'active_applications': 234,
        'by_type': [
            {'type': 'Householder', 'count': 456, 'approval_rate': 92.1, 'avg_decision_days': 42},
            {'type': 'Full Planning', 'count': 387, 'approval_rate': 84.5, 'avg_decision_days': 78}
        ]
    }

    test_trends = {
        'yoy_change': 12.5,
        'trend_direction': 'increasing',
        'monthly_data': [
            {'month': 'Jan', 'total_applications': 98, 'approval_rate': 85.2, 'avg_decision_days': 65},
            {'month': 'Feb', 'total_applications': 102, 'approval_rate': 88.1, 'avg_decision_days': 62},
        ]
    }

    test_scraped = {
        'news': [
            {'title': 'Major development approved', 'date': '2025-09-15'},
            {'title': 'New local plan consultation', 'date': '2025-09-10'}
        ],
        'local_plan': {'summary': 'Birmingham Development Plan 2031 sets out the vision...'},
        'policies': {
            'policy_areas': [
                {'name': 'Housing Policy', 'description': 'Requires 35% affordable housing...'}
            ],
            'spds': [{'title': 'Affordable Housing SPD'}]
        }
    }

    print("Generating introduction...")
    intro = await generator.generate_introduction(test_authority, test_metrics, test_scraped, {})
    print(f"✓ Introduction: {len(intro.split())} words\n")

    print("Generating data insights...")
    insights = await generator.generate_data_insights(test_metrics, test_trends)
    print(f"✓ Data Insights: {len(insights.split())} words\n")

    print("Generating FAQ...")
    faq = await generator.generate_faq(test_authority, test_metrics, test_scraped)
    print(f"✓ FAQ: {len(faq.split())} words\n")

    stats = generator.get_usage_stats()
    print(f"Total cost: ${stats['total_cost']:.4f}")
    print(f"Input tokens: {stats['total_input_tokens']:,}")
    print(f"Output tokens: {stats['total_output_tokens']:,}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_content_generator())
