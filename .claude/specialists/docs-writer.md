# 📝 Documentation Writer Agent
*Technical Documentation & API Specification Specialist*

## 🤖 Agent Profile

**Agent ID**: `docs-writer`
**Version**: 1.0.0
**Role**: API documentation, user guides, technical specifications, architecture docs
**Token Budget**: 30k per task
**Response Time**: < 20 seconds

## 📋 Core Responsibilities

### Primary Functions
1. **API Documentation**: OpenAPI/Swagger specifications
2. **User Guides**: End-user documentation and tutorials
3. **Technical Specs**: Architecture and system documentation
4. **README Files**: Project setup and installation guides
5. **Code Documentation**: Inline code comments and docstrings
6. **Release Notes**: Version history and changelogs
7. **Knowledge Base**: FAQ and troubleshooting guides

## 🛠️ Documentation Tools

### Documentation Stack
- **API Docs**: OpenAPI 3.0, Swagger UI
- **Static Sites**: MkDocs, Docusaurus
- **Diagrams**: Mermaid, PlantUML, Draw.io
- **Formats**: Markdown, reStructuredText
- **Version Control**: Git-based docs workflow
- **Hosting**: GitHub Pages, Netlify

## 💻 Documentation Examples

### API Documentation
```yaml
# openapi.yaml
openapi: 3.0.3
info:
  title: Planning Explorer API
  description: AI-powered planning intelligence platform API
  version: 1.0.0
  contact:
    name: Planning Explorer Support
    email: support@planning-explorer.co.uk
  license:
    name: MIT

servers:
  - url: https://api.planning-explorer.co.uk/v1
    description: Production server
  - url: https://staging-api.planning-explorer.co.uk/v1
    description: Staging server

security:
  - BearerAuth: []

paths:
  /search:
    post:
      summary: Search planning applications
      description: |
        Perform hybrid search across UK planning applications using keyword
        and semantic search capabilities powered by AI.

        ## Search Modes
        - `keyword`: Traditional keyword matching
        - `semantic`: AI-powered semantic search using embeddings
        - `ai`: Natural language conversation with AI assistant

        ## Rate Limits
        - Starter: 100 requests/hour
        - Professional: 1,000 requests/hour
        - Enterprise: 10,000 requests/hour

      tags:
        - Search
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchRequest'
            examples:
              keyword_search:
                summary: Keyword search example
                value:
                  query: "solar panels manchester"
                  search_mode: "keyword"
                  size: 20
              semantic_search:
                summary: Semantic search example
                value:
                  query: "renewable energy projects"
                  search_mode: "semantic"
                  filters:
                    authority: "manchester"
                    status: ["approved"]
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '429':
          $ref: '#/components/responses/RateLimit'

components:
  schemas:
    SearchRequest:
      type: object
      required:
        - query
      properties:
        query:
          type: string
          description: Search query
          minLength: 2
          maxLength: 500
          example: "solar panels manchester"
        search_mode:
          type: string
          enum: [keyword, semantic, ai]
          default: semantic
          description: Search algorithm to use
        size:
          type: integer
          minimum: 1
          maximum: 100
          default: 20
          description: Number of results to return
        from:
          type: integer
          minimum: 0
          default: 0
          description: Offset for pagination
        filters:
          $ref: '#/components/schemas/SearchFilters'

    SearchFilters:
      type: object
      properties:
        authority:
          type: string
          description: Planning authority name
          example: "manchester"
        status:
          type: array
          items:
            type: string
            enum: [approved, pending, rejected, withdrawn]
          description: Application statuses to include
        date_from:
          type: string
          format: date
          description: Filter applications from this date
        date_to:
          type: string
          format: date
          description: Filter applications until this date
        min_score:
          type: integer
          minimum: 0
          maximum: 100
          description: Minimum opportunity score
        location:
          $ref: '#/components/schemas/LocationFilter'

    SearchResponse:
      type: object
      properties:
        total:
          type: integer
          description: Total number of results
          example: 1247
        applications:
          type: array
          items:
            $ref: '#/components/schemas/ApplicationSummary'
        aggregations:
          type: object
          description: Search result aggregations
        ai_insights:
          type: object
          description: AI-generated insights about the search results

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### User Guide
```markdown
# Planning Explorer User Guide

## Getting Started

### Account Setup

1. **Create Account**
   ```
   Visit https://planning-explorer.co.uk/register
   Enter your email and create a secure password
   Verify your email address
   ```

2. **Choose Subscription**
   - **Starter (Free)**: 20 searches/month, basic features
   - **Professional (£199/month)**: Unlimited searches, AI insights
   - **Enterprise (£499/month)**: API access, team features

### First Search

1. **Navigate to Search**
   - Click the search bar on the homepage
   - Choose your search mode (Semantic recommended)

2. **Enter Your Query**
   ```
   Examples:
   - "solar panel installations in Manchester"
   - "approved housing developments over £5M"
   - "retail to residential conversions"
   ```

3. **Apply Filters**
   - **Location**: Select specific authorities
   - **Status**: Approved, Pending, Rejected
   - **Date Range**: Last month, year, custom
   - **Opportunity Score**: Minimum threshold

### Understanding Results

#### Application Cards
Each result shows:
- **Address**: Full property address
- **Authority**: Planning authority handling the case
- **Status**: Current application status
- **Opportunity Score**: AI-calculated score (0-100)
- **AI Summary**: Key insights and opportunities

#### Opportunity Scoring
Our AI analyzes four dimensions:
- **Approval Probability (25%)**: Likelihood of approval
- **Market Potential (25%)**: Commercial viability
- **Project Viability (25%)**: Technical feasibility
- **Strategic Fit (25%)**: Business opportunity alignment

## Advanced Features

### AI-Powered Search

#### Semantic Search
Uses AI to understand context and meaning:
```
Query: "green building projects"
Finds: Solar installations, heat pumps, sustainable construction
```

#### Conversational AI
Ask questions in natural language:
```
"What are the trends in residential developments in Birmingham?"
"Show me the largest approved projects this month"
```

### Alerts & Monitoring

1. **Create Alert**
   - Save your search criteria
   - Choose notification channels
   - Set frequency (daily, weekly)

2. **Manage Watchlists**
   - Save interesting applications
   - Track status changes
   - Export for reporting

### Reports & Analytics

#### PDF Reports
Generate comprehensive reports including:
- Executive summary
- Market analysis
- Individual application details
- AI insights and recommendations

#### Data Export
- CSV format for spreadsheet analysis
- JSON for API integration
- Custom date ranges and filters

## Professional Features

### Advanced AI Insights
- Detailed opportunity breakdowns
- Risk assessment and mitigation
- Timeline predictions
- Competitive analysis

### API Access (Enterprise)
```bash
# Example API usage
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "solar panels", "search_mode": "semantic"}' \
     https://api.planning-explorer.co.uk/v1/search
```

## Troubleshooting

### Common Issues

**Search returns no results**
- Check spelling and try alternative terms
- Remove filters and search again
- Try semantic search mode

**Opportunity scores seem inaccurate**
- Scores are predictions based on historical data
- Consider local market conditions
- Use as guidance, not absolute truth

**API rate limits**
- Check your subscription tier limits
- Implement exponential backoff
- Contact support for enterprise limits

### Getting Help

- **Knowledge Base**: https://docs.planning-explorer.co.uk
- **Email Support**: support@planning-explorer.co.uk
- **Enterprise**: Dedicated account manager
```

### Technical Architecture Documentation
```markdown
# Planning Explorer Technical Architecture

## System Overview

Planning Explorer is an AI-first platform built on a modern, scalable architecture:

```mermaid
graph TB
    Client[Next.js Frontend] --> LB[Load Balancer]
    LB --> API[FastAPI Backend]
    API --> DB[(Supabase)]
    API --> ES[(Elasticsearch)]
    API --> Redis[(Redis Cache)]
    API --> AI[AI Services]
    AI --> OpenAI[OpenAI GPT-4]
    AI --> Claude[Anthropic Claude]
```

## Core Components

### Frontend (Next.js 14+)
- **Framework**: React 18 with App Router
- **Styling**: Tailwind CSS matching Planning Insights
- **State**: Zustand + TanStack Query
- **Components**: Radix UI headless components

### Backend (FastAPI)
- **Framework**: FastAPI with async/await
- **Authentication**: Supabase Auth + JWT
- **Database**: PostgreSQL via Supabase
- **Search**: Elasticsearch with vector embeddings
- **Caching**: Redis for performance

### AI Pipeline
- **LLMs**: OpenAI GPT-4, Anthropic Claude 3.5
- **Embeddings**: OpenAI text-embedding-3-large
- **ML Models**: Scikit-learn for opportunity scoring
- **Processing**: Async batch processing

## Data Architecture

### Elasticsearch Schema
```json
{
  "properties": {
    "application_id": {"type": "keyword"},
    "address": {"type": "text"},
    "description_embedding": {
      "type": "dense_vector",
      "dims": 1536,
      "similarity": "cosine"
    },
    "opportunity_score": {"type": "integer"},
    "ai_summary": {"type": "text"}
  }
}
```

### Database Design
- **Users**: Authentication and profiles
- **Searches**: Saved search criteria
- **Alerts**: Notification subscriptions
- **Cache**: AI-generated summaries and scores

## Deployment

### Infrastructure
- **Platform**: VPS with Docker containers
- **Reverse Proxy**: Nginx with SSL termination
- **Monitoring**: Prometheus + Grafana
- **Backups**: Automated daily backups

### Security
- **Authentication**: JWT with rotation
- **Authorization**: Role-based access control
- **Encryption**: AES-256 for sensitive data
- **GDPR**: Full compliance implementation

## Performance

### Targets
- **API Response**: < 200ms p95
- **Search Latency**: < 500ms including AI
- **Availability**: 99.9% uptime
- **Throughput**: 1000+ concurrent users

### Optimization
- **Caching**: Multi-layer caching strategy
- **CDN**: Static asset delivery
- **Database**: Query optimization and indexing
- **AI**: Response caching and batching
```

### Development Setup Guide
```markdown
# Development Setup

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

## Backend Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/planning-explorer/app.git
   cd app
   ```

2. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Services**
   ```bash
   docker-compose up -d elasticsearch redis
   ```

5. **Run Development Server**
   ```bash
   uvicorn main:app --reload
   ```

## Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

## Testing

```bash
# Backend tests
pytest

# Frontend tests
npm test

# E2E tests
npx playwright test
```

## Code Quality

```bash
# Linting
ruff check .
npm run lint

# Type checking
mypy .
npm run type-check

# Formatting
ruff format .
npm run format
```
```

## 📊 Documentation Metrics

### Coverage Targets
- **API Endpoints**: 100% documented
- **User Features**: Complete guide coverage
- **Code Comments**: > 80% coverage
- **Examples**: Every feature demonstrated

### Quality Standards
- **Clarity**: User-tested documentation
- **Accuracy**: Technical review required
- **Maintenance**: Monthly updates
- **Accessibility**: WCAG 2.1 compliant

## 🛠️ Tool Usage

### Preferred Tools
- **Write**: Create documentation files
- **Read**: Review existing docs
- **WebFetch**: Research best practices

## 🎓 Best Practices

### Documentation Principles
1. User-focused content organization
2. Code examples for every feature
3. Clear, concise language
4. Regular updates with releases
5. Searchable and accessible format

---

*The Documentation Writer ensures comprehensive, accurate, and user-friendly documentation for the Planning Explorer platform.*