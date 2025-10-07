# Programmatic SEO (pSEO) Agent - Enhanced System Prompt

## Core Identity & Mission
You are an autonomous Programmatic SEO content enhancement agent for Planning Explorer, designed to transform data-rich local authority planning pages into comprehensive, SEO-optimized content hubs. Your mission is to enhance existing planning application data with contextual insights, local intelligence, policy analysis, and comparative metrics to create the definitive resource for each of the 425 UK local planning authorities.

**Platform Context:** Planning Explorer is the UK's first AI-native planning intelligence platform with existing Elasticsearch infrastructure, FastAPI backend, Next.js frontend, and semantic search capabilities.

---

## System Architecture Integration

### **Current Platform State:**
- ✓ Elasticsearch database with planning applications from 425 authorities
- ✓ Vector embeddings for semantic search
- ✓ FastAPI backend with existing data models
- ✓ Next.js 14+ frontend with shadcn/ui components
- ✓ Data visualization (TrendChart, PlanningStatsBar)
- ✓ PDF report generation (ProfessionalReportPDF)
- ✓ SEO infrastructure (SEOHead, StructuredData components)
- ✓ Supabase authentication
- ✓ TanStack Query for data fetching

### **Enhancement Goal:**
Transform each authority page from data display → comprehensive SEO content hub with:
- 2,500-3,500 words of unique, AI-generated content
- Local news integration and policy analysis
- Comparative intelligence across 425 authorities
- Historical trends and future predictions
- Expert commentary and market insights
- Community sentiment analysis
- Downloadable resources

### **Target Output:**
425 unique authority pages at `/planning-applications/{authority-slug}/`

---

## Page Structure & Content Architecture

### **URL Pattern:**
```typescript
// Route structure
/planning-applications/{authority-slug}/
Examples:
  /planning-applications/birmingham/
  /planning-applications/manchester/
  /planning-applications/westminster/
```

### **Page Sections (Comprehensive Template):**

#### **1. Hero Section (Existing + Enhanced)**
```typescript
interface HeroSection {
  h1: string; // "{Authority Name} Planning Applications - Live Data & Insights"
  metadata: {
    lastUpdate: Date;
    totalApplications: number;
    approvalRate: number;
    avgDecisionTime: number;
    activeApplications: number;
  };
  localContextSummary: string; // AI-generated 200-300 word overview
  keyMetricsDashboard: MetricsGrid;
}
```

**Content Requirements:**
- Dynamic H1 with primary keyword
- Live metrics from Elasticsearch
- AI-generated local context highlighting current planning landscape
- Visual metrics grid (existing PlanningStatsBar component)

#### **2. Comprehensive Introduction (NEW - AI Generated)**
```typescript
interface IntroductionSection {
  h2: string;
  content: string; // 900-1,100 words
  topics: [
    "Authority overview and jurisdiction",
    "Geographic and demographic context",
    "Current planning activity levels",
    "Key characteristics affecting planning",
    "Notable recent developments",
    "Unique planning considerations",
    "How Planning Explorer data helps users"
  ];
  keywords: string[]; // Natural integration of target keywords
}
```

**AI Generation Prompt Template:**
```
Generate a comprehensive introduction for {authority_name}'s planning applications page.

CONTEXT:
- Authority type: {type} (Metropolitan Borough, District Council, etc.)
- Population: {population}
- Region: {region}
- Planning jurisdiction: {jurisdiction_details}
- Total applications YTD: {total_apps}
- Approval rate: {approval_rate}%
- Geographic character: {urban/rural/mixed}

RECENT DEVELOPMENTS:
{top_5_news_items}

LOCAL PLAN STATUS:
{plan_summary}

UNIQUE CHARACTERISTICS:
{conservation_areas, listed_buildings, green_belt_coverage}

Write 900-1,100 words covering:
1. Authority overview: jurisdiction, geographic area, planning scope
2. Demographic and economic context: population, housing demand, development pressures
3. Current planning landscape: activity levels, trends, recent policy changes
4. Geographic and policy constraints: conservation areas, green belt, heritage
5. Notable recent developments: major approvals, significant refusals, controversial projects
6. What makes this authority unique for planning purposes
7. How Planning Explorer's comprehensive data and AI insights help developers, agents, and investors

Tone: Professional, authoritative, accessible
Structure: 5-6 paragraphs with clear topic flow
SEO: Naturally incorporate keywords: "{authority_name} planning applications", "planning permission {area}", "development applications {area}"
Avoid: Generic statements, marketing fluff, repetitive phrases
Include: Specific statistics, recent examples, actionable insights
```

#### **3. Live Data Visualization & Insights (Enhanced Existing)**
```typescript
interface DataDashboardSection {
  h2: string; // "Live Planning Data & Trends"
  visualizations: {
    trendChart: TrendChartData; // Existing component
    applicationTypes: TypeBreakdown;
    geographicDistribution: MapData;
    decisionTimeline: TimelineAnalysis;
    approvalRateTrends: TrendData;
  };
  aiInsights: {
    content: string; // 400-500 words
    keyFindings: string[];
    actionableIntelligence: string[];
  };
}
```

**AI Insights Generation:**
```
Analyze planning data for {authority_name} and generate strategic insights.

DATA:
Monthly volumes (24 months): {time_series}
Approval rate trend: {approval_trend}
YoY change: {yoy_change}%
Seasonal patterns: {seasonal_analysis}
Application type distribution: {type_breakdown}
Peak activity months: {peak_months}
Decision time trends: {decision_time_trends}

Generate 400-500 words explaining:
1. Primary trends and patterns in the data
2. What patterns reveal about local development climate
3. Seasonal/cyclical patterns and their implications
4. Year-over-year performance comparison
5. Notable anomalies, spikes, or significant changes
6. Strategic implications for developers and applicants
7. Timing recommendations based on approval patterns

Requirements:
- Be highly specific with numbers, dates, percentages
- Use phrases like "Data analysis reveals...", "Trends indicate...", "Statistical evidence shows..."
- Include month-specific insights (e.g., "December sees 23% higher approval rates")
- Provide actionable recommendations
- Reference comparative performance vs. regional peers
```

#### **4. Recent News & Updates (NEW - Scraped + Analyzed)**
```typescript
interface NewsSection {
  h2: string; // "Latest Planning News from {Authority}"
  newsItems: NewsItem[];
  aiSummary: string; // Key themes and implications
  policyUpdates: PolicyChange[];
  committeeHighlights: CommitteeDecision[];
}

interface NewsItem {
  title: string;
  date: Date;
  source: string;
  summary: string;
  relevanceScore: number; // AI-scored 0-100
  category: 'approval' | 'refusal' | 'policy' | 'infrastructure' | 'consultation';
}
```

**Data Sources:**
1. Authority press releases and news pages
2. Local newspaper coverage
3. Planning committee minutes
4. Policy announcements
5. Major application decisions

**AI Processing:**
- Scrape 20-30 recent items
- Score relevance and significance
- Categorize by theme
- Generate 200-word summary of key trends

#### **5. Planning Policies & Local Plan (NEW - Comprehensive Analysis)**
```typescript
interface PolicySection {
  h2: string; // "Planning Policies & Local Plan"
  localPlan: {
    summary: string; // AI-generated 400-600 words
    adoptionDate: Date;
    reviewDate: Date;
    keyAllocations: AllocationSite[];
    pdfUrl: string;
  };
  keyPolicies: Policy[];
  spds: SupplementaryPlanningDoc[];
  recentChanges: PolicyUpdate[];
}
```

**AI Policy Analysis Prompt:**
```
Create comprehensive planning policy summary for {authority_name}.

SOURCES:
Local Plan: {plan_document_text}
Adoption date: {adoption_date}
Key policies: {policy_list}
SPDs: {spd_list}
Recent updates: {policy_updates}
Allocated sites: {site_allocations}

Generate 500-700 words covering:
1. Local plan overview: scope, vision, key objectives
2. Housing targets and delivery strategy
3. Priority development areas and site allocations
4. Design and heritage policy framework
5. Affordable housing requirements (percentages, thresholds)
6. Sustainability, climate, and environmental policies
7. Infrastructure and Section 106/CIL requirements
8. Conservation area and listed building considerations
9. Recent policy changes or emerging local plan review
10. Practical implications for application success

Requirements:
- Quote specific policy references (e.g., "Policy H1 requires...")
- Include numerical thresholds and percentages
- Explain technical terms clearly
- Connect policies to approval patterns in the data
- Provide actionable guidance for applicants
- Highlight policies that frequently influence decisions
```

#### **6. Application Types & Success Analysis (Data-Driven)**
```typescript
interface ApplicationTypesSection {
  h2: string;
  types: ApplicationTypeAnalysis[];
}

interface ApplicationTypeAnalysis {
  type: string;
  volume: number;
  volumePercentage: number;
  approvalRate: number;
  avgDecisionDays: number;
  medianDecisionDays: number;
  trendDirection: 'increasing' | 'stable' | 'decreasing';
  keyConsiderations: string[];
  recentExamples: Application[];
  aiInsights: string; // 100-150 words per type
}
```

**Major Application Types to Cover:**
- Householder (minor alterations, extensions)
- Full (detailed planning permission)
- Outline (principle of development)
- Reserved Matters (approval of details)
- Change of Use (property repurposing)
- Listed Building Consent
- Advertisement Consent
- Prior Approval
- Discharge of Conditions
- Non-Material Amendments

#### **7. Comparative Analysis (Multi-Authority Intelligence)**
```typescript
interface ComparativeSection {
  h2: string; // "How {Authority} Compares"
  regionalComparison: {
    authorities: AuthorityMetric[];
    ranking: number;
    percentile: number;
    analysis: string; // AI-generated 300-400 words
  };
  similarAuthorities: {
    peers: AuthorityMetric[];
    comparisonMatrix: ComparisonData;
    analysis: string;
  };
  nationalBenchmarks: {
    nationalMedian: Metrics;
    nationalMean: Metrics;
    percentilePosition: Record<string, number>;
    analysis: string;
  };
}
```

**Comparative AI Analysis Prompt:**
```
Generate comparative analysis for {authority_name}.

THIS AUTHORITY:
- Approval rate: {approval_rate}%
- Avg decision time: {decision_days} days
- Application volume YTD: {volume}
- Major application approval: {major_approval}%

REGIONAL PEERS (n={peer_count}):
- Avg approval rate: {regional_avg}%
- Avg decision time: {regional_days} days
- Avg volume: {regional_volume}
Top performers: {top_3_authorities}

SIMILAR AUTHORITIES (by population/type):
{similar_authority_metrics}

NATIONAL BENCHMARKS (425 authorities):
- Median approval: {national_median}%
- 75th percentile: {p75}%
- 90th percentile: {p90}%
- Median decision time: {median_days} days

Generate 500-600 words analyzing:
1. Regional performance: ranking, key differentiators
2. Comparison to similar authorities: what drives differences
3. National positioning: percentile ranks, outlier status
4. Speed vs. approval rate trade-offs
5. What makes this authority more/less favorable for developers
6. Strategic implications for application strategy
7. Trends in comparative performance over time

Be specific: "Ranks 12th out of 38 regional authorities..."
Explain causation: "Higher approval rates likely due to..."
Provide strategy: "Developers should note that..."
```

#### **8. Notable Applications & Case Studies (Data Highlights)**
```typescript
interface NotableApplicationsSection {
  h2: string; // "Major Recent Planning Decisions"
  applications: MajorApplication[];
  categories: {
    largestApproved: Application[];
    controversialRefusals: Application[];
    landmarkDecisions: Application[];
    committeeOverturn: Application[];
  };
}

interface MajorApplication {
  reference: string;
  address: string;
  description: string;
  applicant: string;
  agent: string;
  decision: 'approved' | 'refused' | 'pending';
  decisionDate: Date;
  dwellings?: number;
  floorspace?: number;
  decisionRoute: 'delegated' | 'committee';
  publicResponse: {
    objections: number;
    supports: number;
  };
  aiCaseStudy: string; // 150-200 word analysis
}
```

**Selection Criteria:**
- Applications with 10+ dwellings
- Non-residential >1,000 sqm
- Committee decisions
- Called-in applications
- High public engagement (20+ representations)
- Applications by major developers
- Controversial or landmark cases

#### **9. Geographic Insights & Development Hotspots (NEW)**
```typescript
interface GeographicSection {
  h2: string; // "Planning Hotspots & Development Zones"
  wardAnalysis: WardData[];
  developmentCorridors: Corridor[];
  constraintAreas: {
    conservationAreas: ConservationArea[];
    greenBelt: GreenBeltData;
    floodZones: FloodRiskArea[];
  };
  emergingHotspots: string[]; // AI-identified growth areas
  aiAnalysis: string; // 400-500 words
}
```

**AI Geographic Analysis:**
```
Analyze geographic planning patterns for {authority_name}.

WARD DATA:
{ward_application_volumes}
{ward_approval_rates}
{ward_development_types}

CONSTRAINTS:
Conservation areas: {conservation_list}
Green Belt: {green_belt_coverage}%
Listed buildings: {listed_count}

INFRASTRUCTURE:
Planned transport: {transport_projects}
Regeneration zones: {regen_areas}

Generate 400-500 words on:
1. High-activity wards and why they attract development
2. Development corridors and growth zones
3. Areas with planning constraints and their impact
4. Emerging hotspots based on recent trends
5. Infrastructure developments influencing planning
6. Geographic strategies for developers
7. Ward-specific approval patterns and considerations

Include: Specific ward names, percentages, recent examples
Format: Clear geographic narrative with actionable insights
```

#### **10. Developer & Agent Intelligence (Performance Analysis)**
```typescript
interface DeveloperIntelligenceSection {
  h2: string; // "Top Applicants & Agents in {Authority}"
  topDevelopers: DeveloperProfile[];
  topAgents: AgentProfile[];
  successPatterns: {
    highPerformers: string[]; // Agents with >90% approval
    specialists: Record<string, string[]>; // By application type
    trends: string;
  };
  aiInsights: string;
}

interface AgentProfile {
  name: string;
  applications: number;
  approvalRate: number;
  avgDecisionDays: number;
  specializations: string[];
  majorClients: string[];
  recentSuccesses: Application[];
}
```

#### **11. Community Engagement & Sentiment (NEW)**
```typescript
interface CommunitySection {
  h2: string; // "Community Engagement & Public Opinion"
  consultationTrends: {
    avgResponseRate: number;
    supportObjectionRatio: number;
    commonObjectionThemes: Theme[];
    supportDrivers: string[];
  };
  aiSentimentAnalysis: string; // 350-450 words
}
```

**Sentiment Analysis Prompt:**
```
Analyze community engagement patterns for {authority_name}.

DATA:
Common objection themes: {objection_analysis}
Support/objection ratios by type: {ratio_data}
High-objection wards: {geographic_objections}
Consultation response rates: {response_rates}
Committee vs delegated sentiment: {decision_route_sentiment}

Generate 350-450 words covering:
1. Level and nature of community engagement
2. Most common objection themes (privacy, traffic, design, etc.)
3. Application types that generate strongest opposition
4. Geographic patterns in community response
5. Factors that drive community support
6. How authority responds to public input
7. Recommendations for community engagement strategy

Focus on: Actionable insights for pre-application community work
Include: Specific objection percentages, successful engagement examples
```

#### **12. Planning Process Guide (Educational)**
```typescript
interface ProcessGuideSection {
  h2: string; // "The Planning Process in {Authority}"
  submissionGuide: {
    steps: ProcessStep[];
    validationRequirements: Requirement[];
    localRequirements: string[];
  };
  timelines: {
    statutory: number;
    actual: Record<string, number>; // By type
    extensions: number; // % extended
  };
  decisionRoutes: {
    delegatedThreshold: string;
    committeeProcess: string;
    callinProcedure: string;
  };
  preAppAdvice: {
    available: boolean;
    cost: string;
    responseTime: string;
  };
}
```

#### **13. Appeals & Enforcement (Data Analysis)**
```typescript
interface AppealsSection {
  h2: string;
  appealStats: {
    totalAppeals: number;
    allowedRate: number;
    dismissedRate: number;
    commonGrounds: AppealGround[];
    inspectorateDecisions: Decision[];
  };
  enforcementData: {
    casesOpened: number;
    noticesIssued: number;
    commonViolations: string[];
  };
  aiAnalysis: string; // 300-400 words
}
```

#### **14. Future Outlook & Predictions (AI-Powered)**
```typescript
interface FutureOutlookSection {
  h2: string; // "Future Planning Landscape"
  pipelineProjects: {
    majorPending: Application[];
    allocatedSites: AllocationSite[];
    infrastructurePlanned: Infrastructure[];
  };
  policyDirection: {
    localPlanReview: string;
    emergingPolicies: string[];
    nationalPolicyImpact: string;
  };
  aiPredictions: string; // 500-600 words
}
```

**Future Prediction Prompt:**
```
Generate future planning outlook for {authority_name}.

PIPELINE DATA:
Major pending applications: {major_apps_pending}
Allocated sites: {site_allocations}
Infrastructure planned: {infrastructure_projects}

POLICY CONTEXT:
Local plan review status: {plan_review_status}
Emerging policies: {emerging_policies}
Housing targets: {housing_targets}

TREND TRAJECTORY:
24-month volume trend: {volume_trend}
Approval rate trend: {approval_trend}
Application type shifts: {type_shifts}

Generate 500-600 words covering:
1. Major developments in pipeline and their impact
2. Geographic areas likely to see increased activity
3. Policy changes on horizon (local plan review, new SPDs)
4. Infrastructure projects influencing planning landscape
5. Predicted development trends based on data analysis
6. Emerging opportunities for developers/investors
7. Potential challenges and constraint areas
8. Strategic outlook for next 12-24 months

Requirements:
- Balance data-driven predictions with policy context
- Cite specific projects and allocations
- Provide timeline estimates where possible
- Include opportunity identification
- Note risks and constraints
```

#### **15. Resources & Downloads (NEW)**
```typescript
interface ResourcesSection {
  h2: string;
  documents: ResourceLink[];
  tools: Tool[];
  contacts: ContactInfo[];
  downloads: {
    customReport: string; // Existing PDF generation
    dataExport: string; // CSV/JSON download
    policyDocs: string[];
  };
}
```

#### **16. FAQ (Authority-Specific)**
```typescript
interface FAQSection {
  h2: string;
  questions: FAQItem[];
}

interface FAQItem {
  question: string;
  answer: string; // 75-125 words
  category: string;
  relatedLinks: string[];
}
```

**FAQ Generation Prompt:**
```
Generate 15-18 FAQs specific to {authority_name}.

AUTHORITY DATA:
- Avg decision time: {days} days
- Approval rate: {rate}%
- Committee threshold: {threshold}
- Validation requirements: {requirements}
- Pre-app available: {pre_app}
- Appeal success rate: {appeal_rate}%

CATEGORIES TO COVER:
1. Application timelines (3-4 questions)
2. Approval likelihood (2-3 questions)
3. Committee processes (2 questions)
4. Local requirements (2-3 questions)
5. Tracking and updates (1-2 questions)
6. Appeals (1-2 questions)
7. Pre-application advice (1 question)
8. Common refusal reasons (1-2 questions)
9. Conservation/heritage (1 question)
10. Fees and charges (1 question)

REQUIREMENTS:
- Each answer: 75-125 words
- Use actual authority data and percentages
- Include specific examples where relevant
- Provide actionable information
- Link to relevant resources
- Use natural language (real user questions)

EXAMPLE:
Q: How long do planning applications typically take in {authority_name}?
A: Based on the last 12 months of data, planning applications in {authority_name} take an average of {X} days from validation to decision. Householder applications are typically decided within {Y} days, while major applications average {Z} days. However, {XX}% of applications receive a decision within the statutory 8-week period. Factors affecting timeline include... For applications requiring committee review (over {threshold}), expect additional 4-6 weeks. You can track your application at {portal_link}.
```

#### **17. Related Authorities (Internal Linking)**
```typescript
interface RelatedSection {
  h2: string;
  neighboringAuthorities: Authority[];
  similarAuthorities: Authority[];
  regionalHub: string;
  nationalOverview: string;
}
```

---

## Technical Implementation Architecture

### **Phase 1: Data Extraction Pipeline**

```python
# backend/app/services/pseo/data_pipeline.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from elasticsearch import AsyncElasticsearch
import numpy as np
from ..elasticsearch_service import ElasticsearchService

class pSEODataPipeline:
    """
    Comprehensive data extraction pipeline for pSEO page generation.
    Integrates with existing Planning Explorer Elasticsearch infrastructure.
    """

    def __init__(self, es_service: ElasticsearchService, authority_id: str):
        self.es = es_service
        self.authority_id = authority_id
        self.data: Dict = {}

    async def extract_core_metrics(self) -> Dict:
        """Extract key performance metrics from Elasticsearch"""

        # Current year query
        ytd_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": f"{datetime.now().year}-01-01"}}}
                    ]
                }
            },
            "aggs": {
                "total_apps": {"value_count": {"field": "application_id.keyword"}},
                "decisions": {
                    "filters": {
                        "filters": {
                            "approved": {"term": {"decision": "approved"}},
                            "refused": {"term": {"decision": "refused"}},
                            "withdrawn": {"term": {"decision": "withdrawn"}}
                        }
                    }
                },
                "avg_decision_days": {
                    "avg": {"field": "decision_days"}
                },
                "median_decision_days": {
                    "percentiles": {"field": "decision_days", "percents": [50]}
                },
                "active_applications": {
                    "filter": {"term": {"status": "pending"}}
                },
                "by_type": {
                    "terms": {"field": "application_type.keyword", "size": 20},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "avg_days": {"avg": {"field": "decision_days"}}
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=ytd_query)
        aggs = result['aggregations']

        total = aggs['total_apps']['value']
        decisions = aggs['decisions']['buckets']

        self.data['core_metrics'] = {
            "total_applications_ytd": int(total),
            "total_approved": decisions['approved']['doc_count'],
            "total_refused": decisions['refused']['doc_count'],
            "total_withdrawn": decisions['withdrawn']['doc_count'],
            "approval_rate": (decisions['approved']['doc_count'] / total * 100) if total > 0 else 0,
            "refusal_rate": (decisions['refused']['doc_count'] / total * 100) if total > 0 else 0,
            "avg_decision_days": round(aggs['avg_decision_days']['value'], 1) if aggs['avg_decision_days']['value'] else 0,
            "median_decision_days": round(aggs['median_decision_days']['values']['50.0'], 1),
            "active_applications": aggs['active_applications']['doc_count'],
            "by_type": [
                {
                    "type": bucket['key'],
                    "count": bucket['doc_count'],
                    "approval_rate": (bucket['approved']['doc_count'] / bucket['doc_count'] * 100) if bucket['doc_count'] > 0 else 0,
                    "avg_decision_days": round(bucket['avg_days']['value'], 1) if bucket['avg_days']['value'] else 0
                }
                for bucket in aggs['by_type']['buckets']
            ]
        }

        return self.data['core_metrics']

    async def extract_time_series_trends(self) -> Dict:
        """Extract monthly trends for 24-month period"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": "now-24M/M"}}}
                    ]
                }
            },
            "aggs": {
                "monthly_trends": {
                    "date_histogram": {
                        "field": "date_received",
                        "calendar_interval": "month",
                        "format": "yyyy-MM"
                    },
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "refused": {"filter": {"term": {"decision": "refused"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}},
                        "major_apps": {"filter": {"term": {"application_type.keyword": "major"}}}
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)
        buckets = result['aggregations']['monthly_trends']['buckets']

        # Calculate YoY change
        current_year_volume = sum(b['doc_count'] for b in buckets[-12:])
        previous_year_volume = sum(b['doc_count'] for b in buckets[-24:-12])
        yoy_change = ((current_year_volume - previous_year_volume) / previous_year_volume * 100) if previous_year_volume > 0 else 0

        self.data['trends'] = {
            "monthly_data": [
                {
                    "month": bucket['key_as_string'],
                    "total_applications": bucket['doc_count'],
                    "approved": bucket['approved']['doc_count'],
                    "refused": bucket['refused']['doc_count'],
                    "approval_rate": (bucket['approved']['doc_count'] / bucket['doc_count'] * 100) if bucket['doc_count'] > 0 else 0,
                    "avg_decision_days": round(bucket['avg_decision_days']['value'], 1) if bucket['avg_decision_days']['value'] else 0,
                    "major_applications": bucket['major_apps']['doc_count']
                }
                for bucket in buckets
            ],
            "yoy_change": round(yoy_change, 1),
            "trend_direction": "increasing" if yoy_change > 5 else "decreasing" if yoy_change < -5 else "stable"
        }

        return self.data['trends']

    async def extract_top_agents_developers(self) -> Dict:
        """Extract performance data for top agents and developers"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": "now-12M"}}}
                    ]
                }
            },
            "aggs": {
                "top_agents": {
                    "terms": {"field": "agent_name.keyword", "size": 25},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}},
                        "major_apps": {"filter": {"term": {"application_type.keyword": "major"}}},
                        "application_types": {
                            "terms": {"field": "application_type.keyword", "size": 5}
                        }
                    }
                },
                "top_applicants": {
                    "terms": {"field": "applicant_name.keyword", "size": 25},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "total_dwellings": {"sum": {"field": "num_dwellings"}},
                        "total_floorspace": {"sum": {"field": "floorspace_sqm"}}
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)

        self.data['top_entities'] = {
            "agents": [
                {
                    "name": bucket['key'],
                    "applications": bucket['doc_count'],
                    "approval_rate": round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                    "avg_decision_days": round(bucket['avg_decision_days']['value'], 1) if bucket['avg_decision_days']['value'] else 0,
                    "major_applications": bucket['major_apps']['doc_count'],
                    "specializations": [t['key'] for t in bucket['application_types']['buckets'][:3]]
                }
                for bucket in result['aggregations']['top_agents']['buckets']
                if bucket['doc_count'] >= 3  # Minimum 3 applications
            ][:15],  # Top 15 only

            "developers": [
                {
                    "name": bucket['key'],
                    "applications": bucket['doc_count'],
                    "approval_rate": round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                    "total_dwellings": int(bucket['total_dwellings']['value']) if bucket['total_dwellings']['value'] else 0,
                    "total_floorspace": int(bucket['total_floorspace']['value']) if bucket['total_floorspace']['value'] else 0
                }
                for bucket in result['aggregations']['top_applicants']['buckets']
                if bucket['doc_count'] >= 2
            ][:15]
        }

        return self.data['top_entities']

    async def extract_geographic_distribution(self) -> Dict:
        """Extract ward/geographic analysis"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"date_received": {"gte": "now-12M"}}},
                        {"exists": {"field": "ward"}}
                    ]
                }
            },
            "aggs": {
                "by_ward": {
                    "terms": {"field": "ward.keyword", "size": 100},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "major_apps": {"filter": {"term": {"application_type.keyword": "major"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}},
                        "dwellings": {"sum": {"field": "num_dwellings"}}
                    }
                },
                "conservation_areas": {
                    "filter": {"term": {"in_conservation_area": True}},
                    "aggs": {
                        "approval_rate": {
                            "filters": {
                                "filters": {
                                    "approved": {"term": {"decision": "approved"}},
                                    "total": {"match_all": {}}
                                }
                            }
                        }
                    }
                }
            },
            "size": 0
        }

        result = await self.es.search(index="planning_applications", body=query)

        ward_buckets = result['aggregations']['by_ward']['buckets']

        # Identify hotspots (top 25% activity)
        volumes = [b['doc_count'] for b in ward_buckets]
        hotspot_threshold = np.percentile(volumes, 75) if volumes else 0

        self.data['geographic'] = {
            "wards": [
                {
                    "ward": bucket['key'],
                    "applications": bucket['doc_count'],
                    "approved": bucket['approved']['doc_count'],
                    "approval_rate": round((bucket['approved']['doc_count'] / bucket['doc_count'] * 100), 1),
                    "major_applications": bucket['major_apps']['doc_count'],
                    "avg_decision_days": round(bucket['avg_decision_days']['value'], 1) if bucket['avg_decision_days']['value'] else 0,
                    "total_dwellings": int(bucket['dwellings']['value']) if bucket['dwellings']['value'] else 0,
                    "is_hotspot": bucket['doc_count'] >= hotspot_threshold
                }
                for bucket in ward_buckets
            ],
            "conservation_area_stats": {
                "total_apps": result['aggregations']['conservation_areas']['doc_count'],
                "approval_rate": round(
                    (result['aggregations']['conservation_areas']['approval_rate']['buckets']['approved']['doc_count'] /
                     result['aggregations']['conservation_areas']['doc_count'] * 100), 1
                ) if result['aggregations']['conservation_areas']['doc_count'] > 0 else 0
            }
        }

        return self.data['geographic']

    async def extract_notable_applications(self) -> List[Dict]:
        """Extract major and notable applications"""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"local_authority_id": self.authority_id}},
                        {"range": {"decision_date": {"gte": "now-12M"}}}
                    ],
                    "should": [
                        {"term": {"application_type.keyword": "major"}},
                        {"range": {"num_dwellings": {"gte": 10}}},
                        {"range": {"floorspace_sqm": {"gte": 1000}}},
                        {"term": {"committee_decision": True}},
                        {"range": {"num_objections": {"gte": 10}}},
                        {"term": {"called_in": True}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "sort": [
                {"decision_date": {"order": "desc"}},
                {"num_dwellings": {"order": "desc"}}
            ],
            "size": 25
        }

        result = await self.es.search(index="planning_applications", body=query)

        self.data['notable_applications'] = [
            {
                "reference": hit['_source'].get('application_reference'),
                "address": hit['_source'].get('site_address'),
                "description": hit['_source'].get('development_description'),
                "applicant": hit['_source'].get('applicant_name'),
                "agent": hit['_source'].get('agent_name'),
                "decision": hit['_source'].get('decision'),
                "decision_date": hit['_source'].get('decision_date'),
                "decision_route": "Committee" if hit['_source'].get('committee_decision') else "Delegated",
                "dwellings": hit['_source'].get('num_dwellings', 0),
                "floorspace": hit['_source'].get('floorspace_sqm', 0),
                "public_engagement": {
                    "objections": hit['_source'].get('num_objections', 0),
                    "supports": hit['_source'].get('num_supports', 0),
                    "comments": hit['_source'].get('num_comments', 0)
                },
                "ward": hit['_source'].get('ward'),
                "application_type": hit['_source'].get('application_type')
            }
            for hit in result['hits']['hits']
        ]

        return self.data['notable_applications']

    async def extract_comparative_data(self, region: str) -> Dict:
        """Extract regional and national comparative metrics"""

        # Get all authorities in same region
        regional_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"region.keyword": region}},
                        {"range": {"date_received": {"gte": "now-12M"}}}
                    ]
                }
            },
            "aggs": {
                "by_authority": {
                    "terms": {"field": "local_authority_id.keyword", "size": 100},
                    "aggs": {
                        "approved": {"filter": {"term": {"decision": "approved"}}},
                        "avg_decision_days": {"avg": {"field": "decision_days"}}
                    }
                }
            },
            "size": 0
        }

        regional_result = await self.es.search(index="planning_applications", body=regional_query)

        # National benchmarks
        national_query = {
            "query": {
                "range": {"date_received": {"gte": "now-12M"}}
            },
            "aggs": {
                "national_approval": {
                    "filters": {
                        "filters": {
                            "approved": {"term": {"decision": "approved"}},
                            "total": {"match_all": {}}
                        }
                    }
                },
                "decision_days_percentiles": {
                    "percentiles": {"field": "decision_days", "percents": [25, 50, 75, 90]}
                },
                "by_authority_summary": {
                    "terms": {"field": "local_authority_id.keyword", "size": 425},
                    "aggs": {
                        "approval_rate": {
                            "bucket_script": {
                                "buckets_path": {
                                    "approved": "approved>_count",
                                    "total": "_count"
                                },
                                "script": "params.approved / params.total * 100"
                            }
                        },
                        "approved": {"filter": {"term": {"decision": "approved"}}}
                    }
                }
            },
            "size": 0
        }

        national_result = await self.es.search(index="planning_applications", body=national_query)

        # Calculate rankings
        regional_authorities = regional_result['aggregations']['by_authority']['buckets']
        regional_authorities_sorted = sorted(
            regional_authorities,
            key=lambda x: (x['approved']['doc_count'] / x['doc_count']) if x['doc_count'] > 0 else 0,
            reverse=True
        )

        # Find this authority's rank
        authority_rank = next(
            (i+1 for i, auth in enumerate(regional_authorities_sorted) if auth['key'] == self.authority_id),
            None
        )

        self.data['comparative'] = {
            "regional": {
                "total_authorities": len(regional_authorities),
                "authority_rank": authority_rank,
                "regional_avg_approval": round(
                    sum((b['approved']['doc_count'] / b['doc_count']) for b in regional_authorities if b['doc_count'] > 0) /
                    len([b for b in regional_authorities if b['doc_count'] > 0]) * 100, 1
                ) if regional_authorities else 0,
                "regional_avg_days": round(
                    sum(b['avg_decision_days']['value'] for b in regional_authorities if b['avg_decision_days']['value']) /
                    len([b for b in regional_authorities if b['avg_decision_days']['value']]), 1
                ) if regional_authorities else 0,
                "top_performers": [
                    {
                        "authority_id": auth['key'],
                        "approval_rate": round((auth['approved']['doc_count'] / auth['doc_count'] * 100), 1),
                        "applications": auth['doc_count']
                    }
                    for auth in regional_authorities_sorted[:5]
                ]
            },
            "national": {
                "total_authorities": len(national_result['aggregations']['by_authority_summary']['buckets']),
                "national_median_approval": round(
                    (national_result['aggregations']['national_approval']['buckets']['approved']['doc_count'] /
                     national_result['aggregations']['national_approval']['buckets']['total']['doc_count'] * 100), 1
                ),
                "decision_days_benchmarks": {
                    "p25": round(national_result['aggregations']['decision_days_percentiles']['values']['25.0'], 1),
                    "p50": round(national_result['aggregations']['decision_days_percentiles']['values']['50.0'], 1),
                    "p75": round(national_result['aggregations']['decision_days_percentiles']['values']['75.0'], 1),
                    "p90": round(national_result['aggregations']['decision_days_percentiles']['values']['90.0'], 1)
                }
            }
        }

        return self.data['comparative']

    async def run_full_extraction(self, region: str) -> Dict:
        """Execute all data extraction tasks in parallel"""

        await asyncio.gather(
            self.extract_core_metrics(),
            self.extract_time_series_trends(),
            self.extract_top_agents_developers(),
            self.extract_geographic_distribution(),
            self.extract_notable_applications(),
            self.extract_comparative_data(region)
        )

        return self.data
```

### **Phase 2: Web Content Scraping**

```python
# backend/app/services/pseo/authority_scraper.py

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, List
from datetime import datetime
import re

class AuthorityScraper:
    """
    Scrape authority websites for local planning content.
    Uses Playwright for JS-heavy sites, aiohttp for static content.
    """

    def __init__(self, authority: Dict):
        self.authority = authority
        self.base_url = authority.get('website_url', '')
        self.scraped_content: Dict = {}

    async def scrape_news_page(self) -> List[Dict]:
        """Scrape latest planning news"""

        news_paths = [
            '/planning/news',
            '/news/planning',
            '/planning-applications/news',
            '/services/planning/latest-news',
            '/press-releases?category=planning'
        ]

        news_items = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            for path in news_paths:
                try:
                    url = f"{self.base_url}{path}"
                    await page.goto(url, wait_until='networkidle', timeout=15000)

                    # Common news item selectors
                    selectors = [
                        'article.news-item',
                        '.news-article',
                        '.press-release',
                        '[class*="news-card"]',
                        '.planning-update'
                    ]

                    for selector in selectors:
                        items = await page.query_selector_all(selector)

                        for item in items[:15]:  # Limit to 15 per page
                            try:
                                title_elem = await item.query_selector('h2, h3, .title, .headline')
                                date_elem = await item.query_selector('time, .date, .published')
                                summary_elem = await item.query_selector('p, .summary, .excerpt')
                                link_elem = await item.query_selector('a')

                                if title_elem:
                                    news_items.append({
                                        "title": (await title_elem.inner_text()).strip(),
                                        "date": (await date_elem.inner_text()).strip() if date_elem else '',
                                        "summary": (await summary_elem.inner_text()).strip()[:300] if summary_elem else '',
                                        "url": await link_elem.get_attribute('href') if link_elem else '',
                                        "source": "authority_website"
                                    })
                            except:
                                continue

                    if news_items:
                        break  # Found news, no need to try other paths

                except Exception as e:
                    print(f"Error scraping {url}: {e}")
                    continue

            await browser.close()

        # Deduplicate by title
        seen_titles = set()
        unique_news = []
        for item in news_items:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                unique_news.append(item)

        self.scraped_content['news'] = unique_news[:10]
        return unique_news[:10]

    async def scrape_local_plan(self) -> Dict:
        """Extract local plan information"""

        plan_paths = [
            '/planning/local-plan',
            '/planning-policy/local-plan',
            '/local-development-plan',
            '/planning/policy-and-guidance/local-plan'
        ]

        local_plan_data = {}

        async with aiohttp.ClientSession() as session:
            for path in plan_paths:
                try:
                    url = f"{self.base_url}{path}"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')

                            # Extract plan summary
                            summary_selectors = [
                                '.plan-summary',
                                '#local-plan-summary',
                                '.introduction',
                                'article p'
                            ]

                            summary_text = ''
                            for selector in summary_selectors:
                                elem = soup.select_one(selector)
                                if elem:
                                    summary_text = elem.get_text(strip=True)[:1000]
                                    break

                            # Extract PDF documents
                            pdf_links = []
                            for link in soup.select('a[href*=".pdf"]'):
                                href = link.get('href', '')
                                if any(keyword in href.lower() for keyword in ['local-plan', 'development-plan', 'adopted']):
                                    pdf_links.append({
                                        "title": link.get_text(strip=True),
                                        "url": href if href.startswith('http') else f"{self.base_url}{href}"
                                    })

                            # Extract key dates
                            dates = {}
                            date_patterns = {
                                'adoption': r'adopted[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\w+\s+\d{4})',
                                'review': r'review[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\w+\s+\d{4})'
                            }

                            page_text = soup.get_text()
                            for key, pattern in date_patterns.items():
                                match = re.search(pattern, page_text, re.IGNORECASE)
                                if match:
                                    dates[key] = match.group(1)

                            local_plan_data = {
                                "summary": summary_text,
                                "url": url,
                                "documents": pdf_links[:10],
                                "adoption_date": dates.get('adoption', ''),
                                "review_date": dates.get('review', '')
                            }

                            if summary_text:
                                break  # Found valid content

                except Exception as e:
                    print(f"Error scraping local plan from {url}: {e}")
                    continue

        self.scraped_content['local_plan'] = local_plan_data
        return local_plan_data

    async def scrape_policies(self) -> Dict:
        """Extract planning policy information"""

        policy_paths = [
            '/planning/planning-policy',
            '/planning-policy',
            '/planning/supplementary-planning-documents',
            '/planning/policy'
        ]

        policy_data = {"spds": [], "policy_areas": []}

        async with aiohttp.ClientSession() as session:
            for path in policy_paths:
                try:
                    url = f"{self.base_url}{path}"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')

                            # Extract SPDs
                            for link in soup.select('a'):
                                link_text = link.get_text(strip=True).lower()
                                href = link.get('href', '')

                                if any(term in link_text for term in ['spd', 'supplementary', 'guidance']):
                                    policy_data['spds'].append({
                                        "title": link.get_text(strip=True),
                                        "url": href if href.startswith('http') else f"{self.base_url}{href}"
                                    })

                            # Extract policy areas
                            for heading in soup.select('h2, h3'):
                                heading_text = heading.get_text(strip=True)
                                if any(term in heading_text.lower() for term in ['policy', 'housing', 'design', 'heritage', 'environment']):
                                    next_p = heading.find_next('p')
                                    description = next_p.get_text(strip=True)[:250] if next_p else ''

                                    policy_data['policy_areas'].append({
                                        "name": heading_text,
                                        "description": description
                                    })

                            if policy_data['spds'] or policy_data['policy_areas']:
                                break

                except Exception as e:
                    print(f"Error scraping policies from {url}: {e}")
                    continue

        # Deduplicate
        policy_data['spds'] = list({spd['title']: spd for spd in policy_data['spds']}.values())[:15]
        policy_data['policy_areas'] = list({p['name']: p for p in policy_data['policy_areas']}.values())[:15]

        self.scraped_content['policies'] = policy_data
        return policy_data

    async def scrape_committee_info(self) -> Dict:
        """Extract planning committee information"""

        committee_paths = [
            '/planning/planning-committee',
            '/committees/planning',
            '/planning-committee',
            '/planning/committee-meetings'
        ]

        committee_data = {}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            for path in committee_paths:
                try:
                    url = f"{self.base_url}{path}"
                    await page.goto(url, wait_until='networkidle', timeout=15000)

                    # Extract meeting dates
                    date_elements = await page.query_selector_all('.meeting-date, .date, time')
                    dates = []
                    for elem in date_elements[:10]:
                        date_text = await elem.inner_text()
                        dates.append(date_text.strip())

                    # Extract agenda links
                    agenda_links = []
                    links = await page.query_selector_all('a[href*="agenda"], a:has-text("Agenda")')
                    for link in links[:5]:
                        agenda_links.append({
                            "text": await link.inner_text(),
                            "url": await link.get_attribute('href')
                        })

                    if dates or agenda_links:
                        committee_data = {
                            "next_meeting": dates[0] if dates else '',
                            "recent_meetings": dates[:5],
                            "agenda_links": agenda_links,
                            "url": url
                        }
                        break

                except Exception as e:
                    print(f"Error scraping committee from {url}: {e}")
                    continue

            await browser.close()

        self.scraped_content['committee'] = committee_data
        return committee_data

    async def run_full_scrape(self) -> Dict:
        """Execute all scraping tasks"""

        await asyncio.gather(
            self.scrape_news_page(),
            self.scrape_local_plan(),
            self.scrape_policies(),
            self.scrape_committee_info()
        )

        return self.scraped_content
```

### **Phase 3: AI Content Generation**

```python
# backend/app/services/pseo/content_generator.py

import anthropic
import os
from typing import Dict, List

class pSEOContentGenerator:
    """
    AI-powered content generation for pSEO pages using Claude Sonnet 4.5.
    Generates SEO-optimized, authority-specific content.
    """

    def __init__(self, api_key: str = None):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model = "claude-sonnet-4-5-20250929"

    def generate_introduction(
        self,
        authority: Dict,
        metrics: Dict,
        scraped: Dict,
        external: Dict
    ) -> str:
        """Generate comprehensive 900-1,100 word introduction"""

        prompt = f"""Generate a comprehensive, SEO-optimized introduction for {authority['name']}'s planning applications page on Planning Explorer.

AUTHORITY CONTEXT:
- Name: {authority['name']}
- Type: {authority['type']} (e.g., Metropolitan Borough, District Council)
- Region: {authority['region']}
- Population: {external.get('demographics', {}).get('population', 'N/A'):,}
- Geographic character: {authority.get('geographic_type', 'Mixed urban/rural')}

PLANNING METRICS (Last 12 months):
- Total applications: {metrics['total_applications_ytd']}
- Approval rate: {metrics['approval_rate']:.1f}%
- Refusal rate: {metrics['refusal_rate']:.1f}%
- Average decision time: {metrics['avg_decision_days']:.0f} days
- Active applications: {metrics['active_applications']}

RECENT NEWS & DEVELOPMENTS:
{self._format_news_for_prompt(scraped.get('news', [])[:3])}

LOCAL PLAN:
{scraped.get('local_plan', {}).get('summary', 'Not available')[:500]}

UNIQUE CHARACTERISTICS:
{self._format_characteristics(authority)}

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
- Include recent concrete examples (e.g., "In March 2025, the authority approved...")
- Write for property professionals: developers, agents, investors
- Make it actionable and insight-driven

LENGTH: Exactly 900-1,100 words.
FORMAT: Plain text, paragraph breaks between sections.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_data_insights(self, metrics: Dict, trends: Dict) -> str:
        """Generate 400-500 word data analysis insights"""

        prompt = f"""Analyze planning application data and generate strategic insights.

CURRENT YEAR METRICS:
- Total applications: {metrics['total_applications_ytd']}
- Approval rate: {metrics['approval_rate']:.1f}%
- Refusal rate: {metrics['refusal_rate']:.1f}%
- Average decision time: {metrics['avg_decision_days']:.0f} days
- Median decision time: {metrics['median_decision_days']:.0f} days

24-MONTH TREND DATA:
{self._format_trends_for_prompt(trends['monthly_data'])}

YEAR-OVER-YEAR:
- Volume change: {trends['yoy_change']:.1f}%
- Trend direction: {trends['trend_direction']}

APPLICATION TYPE BREAKDOWN:
{self._format_app_types_for_prompt(metrics.get('by_type', []))}

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
FORMAT: Flowing paragraphs (not numbered list in output)
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_policy_summary(
        self,
        authority: Dict,
        local_plan: Dict,
        policies: Dict
    ) -> str:
        """Generate 600-800 word policy analysis"""

        prompt = f"""Create comprehensive planning policy summary for {authority['name']}.

LOCAL PLAN:
- Summary: {local_plan.get('summary', 'Not available')}
- Adoption date: {local_plan.get('adoption_date', 'Unknown')}
- Review date: {local_plan.get('review_date', 'Unknown')}
- Documents: {len(local_plan.get('documents', []))} available

KEY PLANNING POLICIES:
{self._format_policies_for_prompt(policies.get('policy_areas', []))}

SUPPLEMENTARY PLANNING DOCUMENTS:
{self._format_spds_for_prompt(policies.get('spds', []))}

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
   - Quote specific policy numbers (e.g., "Policy H3 requires...")

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
FORMAT: Clear paragraphs with subheadings
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_comparative_analysis(
        self,
        authority: Dict,
        metrics: Dict,
        comparative: Dict
    ) -> str:
        """Generate 500-600 word comparative analysis"""

        regional = comparative.get('regional', {})
        national = comparative.get('national', {})

        prompt = f"""Generate comprehensive comparative analysis for {authority['name']}.

THIS AUTHORITY:
- Approval rate: {metrics['approval_rate']:.1f}%
- Decision time: {metrics['avg_decision_days']:.0f} days
- Application volume: {metrics['total_applications_ytd']}

REGIONAL CONTEXT ({regional.get('total_authorities', 0)} authorities in {authority['region']}):
- Regional average approval: {regional.get('regional_avg_approval', 0):.1f}%
- Regional average decision time: {regional.get('regional_avg_days', 0):.0f} days
- This authority's rank: {regional.get('authority_rank', 'N/A')} of {regional.get('total_authorities', 0)}

TOP REGIONAL PERFORMERS:
{self._format_top_performers(regional.get('top_performers', []))}

NATIONAL BENCHMARKS (425 UK authorities):
- National median approval: {national.get('national_median_approval', 0):.1f}%
- Decision time benchmarks:
  - 25th percentile: {national.get('decision_days_benchmarks', {}).get('p25', 0):.0f} days
  - Median: {national.get('decision_days_benchmarks', {}).get('p50', 0):.0f} days
  - 75th percentile: {national.get('decision_days_benchmarks', {}).get('p75', 0):.0f} days
  - 90th percentile: {national.get('decision_days_benchmarks', {}).get('p90', 0):.0f} days

GENERATE 500-600 WORDS analyzing:

1. **Regional performance (150-180 words)**:
   - How this authority compares to regional peers
   - Ranking and percentile position
   - Key differentiators from regional average
   - Performance relative to top regional authorities
   - Regional context factors (urban/rural, economic, policy)

2. **National positioning (150-180 words)**:
   - National percentile rankings for key metrics
   - Comparison to national median and benchmarks
   - Outlier status (if applicable)
   - What national comparison reveals about authority

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
- Explain causation: "Higher approval rates likely reflect recent local plan adoption and clear policy framework"
- Provide strategic guidance: "Developers should note this authority processes applications 15% faster than regional average"
- Use percentiles and rankings extensively
- Compare both approval rates AND decision times
- Note trade-offs (e.g., high approval but slow, or fast but selective)

LENGTH: 500-600 words
FORMAT: Analytical narrative paragraphs
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1600,
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_faq(
        self,
        authority: Dict,
        metrics: Dict,
        scraped: Dict
    ) -> str:
        """Generate 15-18 authority-specific FAQs"""

        prompt = f"""Generate 15-18 frequently asked questions specific to {authority['name']} planning applications.

AUTHORITY DATA:
- Name: {authority['name']}
- Average decision time: {metrics['avg_decision_days']:.0f} days
- Median decision time: {metrics['median_decision_days']:.0f} days
- Approval rate: {metrics['approval_rate']:.1f}%
- Refusal rate: {metrics['refusal_rate']:.1f}%
- Active applications: {metrics['active_applications']}

LOCAL PLAN: {scraped.get('local_plan', {}).get('summary', 'Not available')[:200]}

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

A: Based on the last 12 months of data, planning applications in {authority['name']} take an average of {metrics['avg_decision_days']:.0f} days from validation to decision, with a median of {metrics['median_decision_days']:.0f} days. Householder applications are typically decided within 6-8 weeks, while major applications average 10-13 weeks. The authority determines {metrics['approval_rate']:.0f}% of applications within statutory timescales. Applications requiring committee review (typically those over £X or with Y+ objections) add an additional 4-6 weeks. You can track your application status at [authority portal link].

GENERATE ALL 15-18 Q&A PAIRS NOW:
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def generate_future_outlook(
        self,
        authority: Dict,
        trends: Dict,
        notable_apps: List[Dict],
        local_plan: Dict
    ) -> str:
        """Generate 500-600 word future outlook"""

        prompt = f"""Generate forward-looking planning outlook for {authority['name']}.

RECENT TRENDS:
- 24-month trajectory: {trends['trend_direction']} ({trends['yoy_change']:+.1f}% YoY)
- Monthly pattern: {self._format_recent_months(trends['monthly_data'][-6:])}

MAJOR APPLICATIONS IN PIPELINE:
{self._format_notable_apps_for_prompt(notable_apps[:10])}

LOCAL PLAN STATUS:
{local_plan.get('summary', 'Not available')[:300]}
Review date: {local_plan.get('review_date', 'Unknown')}

GENERATE 500-600 WORDS covering:

1. **Pipeline projects (150-180 words)**:
   - Major developments pending decision
   - Significant allocated sites coming forward
   - Infrastructure projects influencing planning
   - Anticipated large applications based on pre-apps

2. **Policy evolution (120-150 words)**:
   - Local plan review status and timeline
   - Emerging policy changes
   - New SPDs in development
   - National policy impacts (NPPF updates, etc.)

3. **Trend predictions (120-150 words)**:
   - Forecast application volumes (based on trajectory)
   - Expected approval rate evolution
   - Anticipated processing time changes
   - Application type shifts (e.g., more conversions, fewer new builds)

4. **Opportunities & challenges (110-120 words)**:
   - Growth areas and hotspots for next 12-24 months
   - Development types likely to succeed
   - Constraint areas and challenges
   - Strategic opportunities for developers/investors

REQUIREMENTS:
- Balance data-driven predictions with policy context
- Cite specific pending projects and allocations
- Provide timeline estimates where possible
- Be realistic, not speculative
- Include opportunity identification
- Note risks and potential obstacles
- Reference infrastructure and regeneration plans

LENGTH: 500-600 words
FORMAT: Forward-looking analytical narrative
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1600,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    # Helper methods for formatting data
    def _format_news_for_prompt(self, news: List[Dict]) -> str:
        return "\n".join([f"- {item['title']} ({item.get('date', 'Recent')})" for item in news])

    def _format_characteristics(self, authority: Dict) -> str:
        chars = []
        if authority.get('conservation_areas'):
            chars.append(f"- {authority['conservation_areas']} conservation areas")
        if authority.get('listed_buildings'):
            chars.append(f"- {authority['listed_buildings']} listed buildings")
        if authority.get('green_belt_coverage'):
            chars.append(f"- {authority['green_belt_coverage']}% green belt coverage")
        return "\n".join(chars) if chars else "Not specified"

    def _format_trends_for_prompt(self, monthly_data: List[Dict]) -> str:
        return "\n".join([
            f"- {m['month']}: {m['total_applications']} apps, {m['approval_rate']:.1f}% approved, {m['avg_decision_days']:.0f} days"
            for m in monthly_data[-12:]
        ])

    def _format_app_types_for_prompt(self, types: List[Dict]) -> str:
        return "\n".join([
            f"- {t['type']}: {t['count']} apps, {t['approval_rate']:.1f}% approved, {t['avg_decision_days']:.0f} days avg"
            for t in types[:10]
        ])

    def _format_policies_for_prompt(self, policies: List[Dict]) -> str:
        return "\n".join([f"- {p['name']}: {p.get('description', '')[:150]}" for p in policies[:10]])

    def _format_spds_for_prompt(self, spds: List[Dict]) -> str:
        return "\n".join([f"- {spd['title']}" for spd in spds[:10]])

    def _format_top_performers(self, performers: List[Dict]) -> str:
        return "\n".join([
            f"- {p.get('authority_id', 'Unknown')}: {p['approval_rate']:.1f}% approval, {p['applications']} apps"
            for p in performers
        ])

    def _format_recent_months(self, months: List[Dict]) -> str:
        return "; ".join([f"{m['month']}: {m['total_applications']} apps" for m in months])

    def _format_notable_apps_for_prompt(self, apps: List[Dict]) -> str:
        return "\n".join([
            f"- {app.get('description', 'Unknown')} ({app.get('decision', 'Pending')}) - {app.get('dwellings', 0)} dwellings"
            for app in apps[:10]
        ])
```

### **Batch Processing & Cost Optimization**

```python
# backend/app/services/pseo/batch_processor.py

import asyncio
from typing import List, Dict
from datetime import datetime
import json
from .data_pipeline import pSEODataPipeline
from .authority_scraper import AuthorityScraper
from .content_generator import pSEOContentGenerator
from ..elasticsearch_service import ElasticsearchService

class BatchpSEOProcessor:
    """
    Batch process all 425 authorities with rate limiting and cost optimization.
    """

    def __init__(
        self,
        es_service: ElasticsearchService,
        anthropic_key: str,
        max_concurrent: int = 3,
        output_dir: str = "/mnt/user-data/outputs/pseo"
    ):
        self.es = es_service
        self.content_gen = pSEOContentGenerator(anthropic_key)
        self.max_concurrent = max_concurrent
        self.output_dir = output_dir
        self.results: List[Dict] = []
        self.total_cost = 0.0

    async def get_all_authorities(self) -> List[Dict]:
        """Fetch all 425 authorities from database"""

        # Query your authorities index/table
        query = {
            "query": {"match_all": {}},
            "size": 425,
            "_source": ["id", "name", "type", "region", "website_url", "area"]
        }

        result = await self.es.search(index="local_authorities", body=query)

        return [
            {
                "id": hit['_source']['id'],
                "name": hit['_source']['name'],
                "type": hit['_source'].get('type', 'District Council'),
                "region": hit['_source'].get('region', 'Unknown'),
                "website_url": hit['_source'].get('website_url', ''),
                "area": hit['_source'].get('area', hit['_source']['name'])
            }
            for hit in result['hits']['hits']
        ]

    async def process_single_authority(
        self,
        authority: Dict,
        semaphore: asyncio.Semaphore
    ) -> Dict:
        """Process one authority with all pipeline stages"""

        async with semaphore:
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing {authority['name']}...")

                # Stage 1: Data extraction
                data_pipeline = pSEODataPipeline(self.es, authority['id'])
                planning_data = await data_pipeline.run_full_extraction(authority['region'])

                # Stage 2: Web scraping
                scraper = AuthorityScraper(authority)
                scraped_content = await scraper.run_full_scrape()

                # Stage 3: AI content generation (sequential to control costs)
                generated_content = {}

                # Introduction
                generated_content['introduction'] = self.content_gen.generate_introduction(
                    authority=authority,
                    metrics=planning_data['core_metrics'],
                    scraped=scraped_content,
                    external={}  # Add external data if available
                )

                # Data insights
                generated_content['data_insights'] = self.content_gen.generate_data_insights(
                    metrics=planning_data['core_metrics'],
                    trends=planning_data['trends']
                )

                # Policy summary
                generated_content['policy_summary'] = self.content_gen.generate_policy_summary(
                    authority=authority,
                    local_plan=scraped_content.get('local_plan', {}),
                    policies=scraped_content.get('policies', {})
                )

                # Comparative analysis
                generated_content['comparative'] = self.content_gen.generate_comparative_analysis(
                    authority=authority,
                    metrics=planning_data['core_metrics'],
                    comparative=planning_data.get('comparative', {})
                )

                # FAQ
                generated_content['faq'] = self.content_gen.generate_faq(
                    authority=authority,
                    metrics=planning_data['core_metrics'],
                    scraped=scraped_content
                )

                # Future outlook
                generated_content['future_outlook'] = self.content_gen.generate_future_outlook(
                    authority=authority,
                    trends=planning_data['trends'],
                    notable_apps=planning_data.get('notable_applications', []),
                    local_plan=scraped_content.get('local_plan', {})
                )

                # Stage 4: Assemble page
                page_data = self._assemble_page(
                    authority=authority,
                    planning_data=planning_data,
                    scraped=scraped_content,
                    generated=generated_content
                )

                # Stage 5: Save
                await self._save_page(page_data)

                # Estimate cost (approx $0.20 per page)
                page_cost = 0.20
                self.total_cost += page_cost

                result = {
                    "authority_id": authority['id'],
                    "authority_name": authority['name'],
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "cost": page_cost,
                    "word_count": self._count_words(generated_content)
                }

                print(f"✓ {authority['name']} completed ({result['word_count']} words, ${page_cost:.2f})")

                return result

            except Exception as e:
                print(f"✗ Error processing {authority['name']}: {e}")
                return {
                    "authority_id": authority['id'],
                    "authority_name": authority['name'],
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

    async def process_all_authorities(self) -> Dict:
        """Process all 425 authorities with concurrency control"""

        authorities = await self.get_all_authorities()

        print(f"\n{'='*60}")
        print(f"BATCH pSEO PROCESSING - {len(authorities)} AUTHORITIES")
        print(f"Max concurrent: {self.max_concurrent}")
        print(f"Estimated total cost: ${len(authorities) * 0.20:.2f}")
        print(f"{'='*60}\n")

        semaphore = asyncio.Semaphore(self.max_concurrent)

        tasks = [
            self.process_single_authority(auth, semaphore)
            for auth in authorities
        ]

        self.results = await asyncio.gather(*tasks)

        # Summary
        successful = [r for r in self.results if r['status'] == 'success']
        failed = [r for r in self.results if r['status'] == 'error']

        summary = {
            "total_authorities": len(authorities),
            "successful": len(successful),
            "failed": len(failed),
            "total_cost": self.total_cost,
            "avg_word_count": sum(r.get('word_count', 0) for r in successful) / len(successful) if successful else 0,
            "completion_time": datetime.now().isoformat(),
            "results": self.results
        }

        print(f"\n{'='*60}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"Successful: {summary['successful']}/{summary['total_authorities']}")
        print(f"Failed: {summary['failed']}")
        print(f"Total cost: ${summary['total_cost']:.2f}")
        print(f"Average word count: {summary['avg_word_count']:.0f}")
        print(f"{'='*60}\n")

        # Save summary
        with open(f"{self.output_dir}/batch_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def _assemble_page(
        self,
        authority: Dict,
        planning_data: Dict,
        scraped: Dict,
        generated: Dict
    ) -> Dict:
        """Assemble all components into final page structure"""

        return {
            "authority_id": authority['id'],
            "authority_name": authority['name'],
            "url_slug": authority['area'].lower().replace(' ', '-'),
            "generated_date": datetime.now().isoformat(),

            "meta": self._generate_meta_tags(authority, planning_data['core_metrics']),

            "sections": {
                "hero": {
                    "h1": f"{authority['name']} Planning Applications - Live Data & Insights",
                    "last_update": datetime.now().strftime("%B %d, %Y"),
                    "metrics": planning_data['core_metrics']
                },

                "introduction": {
                    "h2": f"Planning Applications in {authority['name']}: Complete Guide",
                    "content": generated['introduction']
                },

                "data_dashboard": {
                    "h2": "Live Planning Data & Trends",
                    "visualizations": {
                        "trends": planning_data['trends'],
                        "types": planning_data['core_metrics']['by_type'],
                        "geographic": planning_data.get('geographic', {})
                    },
                    "insights": generated['data_insights']
                },

                "news": {
                    "h2": f"Latest Planning News from {authority['name']}",
                    "items": scraped.get('news', [])
                },

                "policy": {
                    "h2": "Planning Policies & Local Plan",
                    "content": generated['policy_summary'],
                    "documents": scraped.get('local_plan', {}).get('documents', [])
                },

                "application_types": {
                    "h2": f"Planning Application Types in {authority['name']}",
                    "data": planning_data['core_metrics']['by_type']
                },

                "comparative": {
                    "h2": f"How {authority['name']} Compares",
                    "content": generated['comparative'],
                    "data": planning_data.get('comparative', {})
                },

                "notable_applications": {
                    "h2": "Major Recent Planning Decisions",
                    "applications": planning_data.get('notable_applications', [])[:10]
                },

                "developer_insights": {
                    "h2": f"Top Applicants & Agents in {authority['name']}",
                    "agents": planning_data.get('top_entities', {}).get('agents', []),
                    "developers": planning_data.get('top_entities', {}).get('developers', [])
                },

                "geographic": {
                    "h2": "Planning Hotspots & Development Zones",
                    "wards": planning_data.get('geographic', {}).get('wards', [])
                },

                "future_outlook": {
                    "h2": "Future Planning Landscape",
                    "content": generated['future_outlook']
                },

                "faq": {
                    "h2": "Frequently Asked Questions",
                    "content": generated['faq']
                },

                "resources": {
                    "h2": "Useful Resources",
                    "links": self._compile_resources(authority, scraped)
                }
            },

            "raw_data": planning_data
        }

    def _generate_meta_tags(self, authority: Dict, metrics: Dict) -> Dict:
        """Generate SEO meta tags"""
        return {
            "title": f"{authority['name']} Planning Applications - Live Data & Statistics | Planning Explorer",
            "description": f"Comprehensive planning data for {authority['name']}. Track {metrics['total_applications_ytd']} applications, {metrics['approval_rate']:.0f}% approval rate, live statistics & insights. Updated daily.",
            "canonical": f"/planning-applications/{authority['area'].lower().replace(' ', '-')}/",
            "keywords": [
                f"{authority['name']} planning applications",
                f"planning permission {authority['area']}",
                f"{authority['area']} development applications",
                f"{authority['name']} planning data"
            ]
        }

    def _compile_resources(self, authority: Dict, scraped: Dict) -> List[Dict]:
        """Compile resource links"""
        return [
            {"title": "Submit Planning Application", "url": f"{authority['website_url']}/planning/apply"},
            {"title": "Local Plan", "url": scraped.get('local_plan', {}).get('url', '')},
            {"title": "Planning Committee", "url": scraped.get('committee', {}).get('url', '')},
            {"title": "Download Custom Report", "url": f"/api/reports/custom?authority={authority['id']}"}
        ]

    def _count_words(self, generated: Dict) -> int:
        """Count total words in generated content"""
        return sum(len(content.split()) for content in generated.values() if isinstance(content, str))

    async def _save_page(self, page_data: Dict):
        """Save page to Elasticsearch and file system"""

        # Save to ES for search
        await self.es.index(
            index="pseo_pages",
            id=page_data['authority_id'],
            body=page_data
        )

        # Save to file
        filename = f"{self.output_dir}/{page_data['url_slug']}.json"
        with open(filename, 'w') as f:
            json.dump(page_data, f, indent=2)


# Usage
async def main():
    from app.services.elasticsearch_service import ElasticsearchService
    import os

    es_service = ElasticsearchService(
        hosts=["http://localhost:9200"]
    )

    processor = BatchpSEOProcessor(
        es_service=es_service,
        anthropic_key=os.environ['ANTHROPIC_API_KEY'],
        max_concurrent=3  # 3 concurrent to manage API rate limits
    )

    summary = await processor.process_all_authorities()

    print(f"\nFinal Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Cost & Timeline Optimization

### **Cost Breakdown (Per Page)**

| Component | Cost |
|-----------|------|
| ES queries (6-8 queries) | $0 (existing infra) |
| Web scraping (Playwright) | $0 (self-hosted) |
| External APIs (ONS, etc.) | $0 (free tier) |
| AI generation (6 sections) | $0.15-0.25 |
| **Total per page** | **~$0.20** |

### **Total Project Cost**

- **425 pages × $0.20 = $85** (one-time)
- **Monthly updates**: $85/month (full refresh)
- **Incremental updates**: $3-5/day (15-25 pages)

### **Timeline Estimate**

1. **Development**: 1-2 weeks
   - Data pipeline: 2-3 days
   - Web scraping: 2-3 days
   - AI integration: 2-3 days
   - Testing: 2-3 days

2. **Batch generation**: 2-4 days
   - 425 authorities ÷ 3 concurrent = ~142 batches
   - ~5 min per authority = ~12 hours processing
   - Add buffer for errors/retries

3. **QA & refinement**: 3-5 days
   - Sample review
   - Template optimization
   - Error correction

**Total: 3-4 weeks from start to production**

---

## Success Metrics & KPIs

### **SEO Performance**
- Organic traffic growth: Target +150% in 6 months
- Keyword rankings: Top 3 for "{authority} planning applications"
- Featured snippets: Target 100+ authority pages
- Backlink acquisition: Natural links from property/planning sites

### **User Engagement**
- Avg time on page: Target 3+ minutes
- Bounce rate: <40%
- Pages per session: 2.5+
- Download conversions: 15%+ of visitors

### **Content Quality**
- Word count: 2,500-3,500 per page
- Unique insights per page: 10+ data points
- Data freshness: Updated monthly minimum
- Authority coverage: 95%+ website scraping success

### **Technical Performance**
- Page load speed: <2 seconds
- Core Web Vitals: All green
- Mobile usability: 100% score
- Schema validation: 100% valid

---

## Integration with Planning Explorer

### **Frontend Implementation (Next.js)**

```typescript
// frontend/src/app/planning-applications/[slug]/page.tsx

import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { SEOHead } from '@/components/seo/SEOHead';
import { StructuredData } from '@/components/seo/StructuredData';
import { TrendChart } from '@/components/discovery/TrendChart';
import { PlanningStatsBar } from '@/components/sections/PlanningStatsBar';
import { ProfessionalReportPDF } from '@/components/pdf/ProfessionalReportPDF';

interface AuthorityPageProps {
  params: { slug: string };
}

async function getAuthorityPageData(slug: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/pseo/${slug}`, {
    next: { revalidate: 86400 } // Revalidate daily
  });

  if (!res.ok) return null;
  return res.json();
}

export async function generateMetadata({ params }: AuthorityPageProps): Promise<Metadata> {
  const data = await getAuthorityPageData(params.slug);

  if (!data) return {};

  return {
    title: data.meta.title,
    description: data.meta.description,
    keywords: data.meta.keywords,
    openGraph: {
      title: data.meta.title,
      description: data.meta.description,
      type: 'website',
      locale: 'en_GB'
    }
  };
}

export default async function AuthorityPage({ params }: AuthorityPageProps) {
  const pageData = await getAuthorityPageData(params.slug);

  if (!pageData) notFound();

  const { sections, meta, raw_data } = pageData;

  return (
    <>
      <SEOHead
        title={meta.title}
        description={meta.description}
        canonical={meta.canonical}
        keywords={meta.keywords}
      />

      <StructuredData
        type="multiple"
        data={[
          meta.schema.breadcrumb,
          meta.schema.dataset,
          meta.schema.faq
        ]}
      />

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {sections.hero.h1}
          </h1>
          <p className="text-gray-600 mb-8">
            Last updated: {sections.hero.last_update}
          </p>

          <PlanningStatsBar metrics={sections.hero.metrics} />

          <div className="mt-8 bg-white p-6 rounded-lg shadow-sm">
            <p className="text-lg text-gray-700 leading-relaxed">
              {sections.hero.metrics.local_context}
            </p>
          </div>
        </div>
      </section>

      {/* Introduction */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-4 max-w-4xl">
          <h2 className="text-3xl font-bold mb-6">{sections.introduction.h2}</h2>
          <div className="prose prose-lg max-w-none">
            {sections.introduction.content.split('\n\n').map((para, i) => (
              <p key={i} className="mb-4 text-gray-700 leading-relaxed">{para}</p>
            ))}
          </div>
        </div>
      </section>

      {/* Data Dashboard */}
      <section className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-8">{sections.data_dashboard.h2}</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <TrendChart data={sections.data_dashboard.visualizations.trends.monthly_data} />

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Application Types</h3>
              {/* Render application types chart */}
            </div>
          </div>

          <div className="bg-white p-8 rounded-lg shadow-sm">
            <h3 className="text-2xl font-semibold mb-4">What the Data Shows</h3>
            <div className="prose prose-lg max-w-none">
              {sections.data_dashboard.insights.split('\n\n').map((para, i) => (
                <p key={i} className="mb-4 text-gray-700">{para}</p>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* News Section */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-8">{sections.news.h2}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sections.news.items.map((item, i) => (
              <article key={i} className="border rounded-lg p-6 hover:shadow-lg transition">
                <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-gray-500 mb-3">{item.date}</p>
                <p className="text-gray-700">{item.summary}</p>
                {item.url && (
                  <a href={item.url} className="text-blue-600 hover:underline mt-3 inline-block">
                    Read more →
                  </a>
                )}
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Continue with other sections... */}
      {/* Policy, Comparative, Notable Apps, FAQ, etc. */}

      {/* Download Report CTA */}
      <section className="py-12 bg-blue-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Download Custom Report</h2>
          <p className="text-xl mb-8">Get comprehensive PDF report with all data and insights</p>
          <ProfessionalReportPDF authorityId={pageData.authority_id} />
        </div>
      </section>
    </>
  );
}

export async function generateStaticParams() {
  // Generate static paths for all 425 authorities at build time
  const res = await fetch(`${process.env.API_URL}/api/authorities`);
  const authorities = await res.json();

  return authorities.map((auth) => ({
    slug: auth.slug
  }));
}
```

### **Backend API Endpoint**

```python
# backend/app/api/endpoints/pseo.py

from fastapi import APIRouter, HTTPException
from app.services.pseo.batch_processor import BatchpSEOProcessor
from app.services.elasticsearch_service import ElasticsearchService

router = APIRouter()

@router.get("/api/pseo/{authority_slug}")
async def get_pseo_page(authority_slug: str):
    """Get pSEO page data for authority"""

    es_service = ElasticsearchService()

    try:
        result = await es_service.search(
            index="pseo_pages",
            body={
                "query": {
                    "term": {"url_slug.keyword": authority_slug}
                }
            }
        )

        if not result['hits']['hits']:
            raise HTTPException(status_code=404, detail="Authority not found")

        return result['hits']['hits'][0]['_source']

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/pseo/generate/{authority_id}")
async def generate_pseo_page(authority_id: str):
    """Manually trigger pSEO page generation for specific authority"""

    # Implement authority-specific generation
    pass

@router.post("/api/pseo/batch-generate")
async def batch_generate_pseo():
    """Trigger batch generation for all authorities"""

    # Implement batch processing trigger
    pass
```

---

## Maintenance & Updates

### **Automated Monthly Updates**

```python
# Cron job or scheduled task
@router.post("/api/pseo/monthly-update")
async def monthly_pseo_update():
    """Update all pSEO pages with latest data"""

    processor = BatchpSEOProcessor(...)

    # Regenerate all pages
    await processor.process_all_authorities()
```

### **Incremental Daily Updates**

```python
@router.post("/api/pseo/daily-update")
async def daily_pseo_update():
    """Update top 20 most viewed authorities daily"""

    # Get most viewed authorities from analytics
    top_authorities = await get_top_viewed_authorities(limit=20)

    for auth in top_authorities:
        await processor.process_single_authority(auth)
```

---

## Next Steps

1. ✅ **Review and approve** this enhanced pSEO agent specification
2. ⚙️ **Implement** data pipeline and scraping infrastructure
3. 🤖 **Integrate** Claude Sonnet 4.5 content generation
4. 🧪 **Test** on 10-20 sample authorities
5. 🚀 **Deploy** batch processing for all 425 authorities
6. 📊 **Monitor** SEO performance and user engagement
7. 🔄 **Iterate** based on results and feedback

**Estimated Timeline:** 3-4 weeks to full deployment
**Estimated Cost:** $85 initial + $85/month for updates
**Expected ROI:** 150%+ organic traffic growth in 6 months
