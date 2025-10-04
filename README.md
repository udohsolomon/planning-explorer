# 🏗️ Planning Explorer - AI-First Planning Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.11+-orange.svg)](https://www.elastic.co/elasticsearch/)

> **The UK's first AI-native planning intelligence platform that transforms weeks of manual research into minutes of AI-powered insights.**

Planning Explorer revolutionises property intelligence by combining comprehensive UK planning data with advanced AI to deliver instant opportunity scoring, predictive analytics, intelligent alerts, and personalised insights for property professionals.

## 🌟 Key Features

### 🧠 AI-Powered Intelligence
- **Semantic Search**: Natural language queries across all planning data
- **Opportunity Scoring**: AI-generated 0-100 opportunity scores with detailed rationale
- **Predictive Analytics**: ML models predicting approval likelihood and timelines
- **Smart Summaries**: AI-generated application summaries tailored to user personas
- **Market Intelligence**: Real-time insights and trend analysis

### 🔍 Advanced Search & Discovery
- **Hybrid Search Engine**: Combines keyword matching with semantic similarity
- **Interactive Mapping**: Geographic visualization with clustering and heatmaps
- **Advanced Filtering**: Location, date, status, and AI-suggested combinations
- **Saved Searches**: Personalised search libraries with AI naming
- **Real-time Alerts**: Smart notifications for relevant opportunities

### 📊 Comprehensive Data Coverage
- **Complete UK Coverage**: Every planning application from all councils
- **Real-time Updates**: Continuous data ingestion and processing
- **Document Intelligence**: PDF parsing and information extraction
- **Historical Analysis**: Trend tracking and comparative analysis
- **Export Capabilities**: PDF reports, CSV exports, and API access

### 🎯 Persona-Specific Insights
- **Developer View**: ROI potential, constraints, and competition analysis
- **Supplier View**: Contract opportunities and project scale assessment
- **Consultant View**: Client relevance and regulatory compliance
- **Agent View**: Market impact and investment potential analysis

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** and **npm/yarn**
- **Python 3.11+**
- **Docker** (optional, for containerized deployment)
- **Elasticsearch cluster** (credentials required)
- **Supabase project** (for user management)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/udohsolomon/planning-explorer.git
   cd planning-explorer
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local with your API endpoints
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python start.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

5. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

### Tech Stack

#### Backend
- **FastAPI 0.104+**: Modern Python web framework with automatic API documentation
- **Elasticsearch 8.11+**: Search engine with vector search capabilities
- **Supabase**: PostgreSQL + Authentication + Storage for user management
- **OpenAI/Anthropic**: AI models for summarization and analysis
- **Pydantic**: Data validation and serialization
- **Uvicorn**: High-performance ASGI server

#### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript 5+**: Type-safe development
- **Tailwind CSS 4**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **React Leaflet**: Interactive mapping
- **Zustand**: Lightweight state management
- **React Hook Form**: Form handling and validation

#### AI & ML
- **OpenAI GPT-4/Claude 3.5**: Advanced language models
- **Sentence Transformers**: Local embedding generation
- **Vector Search**: Semantic similarity matching
- **ML Models**: Predictive analytics and scoring

### Project Structure

```
planning-explorer/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/               # API endpoints and routing
│   │   ├── ai/                # AI processing modules
│   │   ├── core/              # Configuration and startup
│   │   ├── db/                # Database clients (ES, Supabase)
│   │   ├── middleware/        # CORS, auth, logging, rate limiting
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utility functions
│   ├── scripts/               # Data migration and setup scripts
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Container configuration
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   ├── components/       # React components
│   │   │   ├── ai/          # AI-powered components
│   │   │   ├── search/      # Search interface components
│   │   │   ├── ui/          # Reusable UI components
│   │   │   └── user/        # User management components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── stores/          # Zustand state management
│   │   └── types/           # TypeScript type definitions
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── next.config.ts       # Next.js configuration
├── docs/                     # Project documentation
├── .github/                  # GitHub workflows and templates
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Elasticsearch Configuration
ELASTICSEARCH_NODE=https://your-elasticsearch-cluster:9200
ELASTICSEARCH_USERNAME=your-username
ELASTICSEARCH_PASSWORD=your-password

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Application Configuration
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO

# Performance Settings
CACHE_TTL=300
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

#### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Feature Flags
NEXT_PUBLIC_AI_FEATURES_ENABLED=true
NEXT_PUBLIC_MAP_FEATURES_ENABLED=true
```

## 📚 API Documentation

### Core Endpoints

#### Search & Applications
- `GET /api/v1/applications` - List planning applications with filters
- `GET /api/v1/applications/{id}` - Get detailed application information
- `POST /api/v1/search` - Advanced search with multiple criteria
- `POST /api/v1/search/semantic` - AI-powered semantic search
- `GET /api/v1/aggregations` - Market intelligence and statistics

#### AI Features
- `POST /api/v1/ai/opportunity-score` - Calculate AI opportunity scores
- `POST /api/v1/ai/summarize` - Generate AI summaries
- `GET /api/v1/ai/insights` - Get market insights and trends
- `POST /api/v1/ai/semantic-search` - Natural language search

#### User Management
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/auth/user` - Get current user profile
- `POST /api/v1/user/searches` - Save search queries
- `GET /api/v1/user/alerts` - Get user alert subscriptions

### Example API Usage

```python
import requests

# Search for planning applications
response = requests.post('http://localhost:8000/api/v1/search', json={
    "query": "residential development Manchester",
    "filters": {
        "authority": "Manchester City Council",
        "status": "approved",
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        }
    }
})

# Get AI opportunity score
response = requests.post('http://localhost:8000/api/v1/ai/opportunity-score', json={
    "application_id": "12345",
    "user_type": "developer"
})
```

## 🎨 Frontend Components

### Key Components

#### Search Interface
- **AISearchAnimation**: Animated search experience with real-time feedback
- **SearchWithAnimation**: Main search component with AI integration
- **SemanticSearchBar**: Natural language search input
- **SearchSuggestions**: AI-powered search suggestions

#### AI Features
- **OpportunityScoreCard**: Visual opportunity scoring display
- **AIInsightsSummary**: AI-generated insights and recommendations
- **MarketIntelligencePanel**: Market trends and analysis
- **SimilarApplications**: AI-suggested similar applications

#### Data Visualization
- **PlanningMap**: Interactive mapping with clustering
- **TrendChart**: Time-series data visualization
- **VolumeChart**: Application volume analysis
- **TimelineChart**: Project timeline visualization

### Component Usage Example

```tsx
import { AISearchAnimation } from '@/components/search/animation'
import { OpportunityScoreCard } from '@/components/ai/OpportunityScoreCard'

export default function SearchPage() {
  return (
    <div>
      <AISearchAnimation 
        onSearch={handleSearch}
        placeholder="Search planning applications..."
      />
      <OpportunityScoreCard 
        score={85}
        breakdown={{
          approval_probability: 0.8,
          market_potential: 0.9,
          project_viability: 0.7,
          strategic_fit: 0.9
        }}
      />
    </div>
  )
}
```

## 🚀 Deployment

### Docker Deployment (Recommended)

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Production deployment**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

### Manual Deployment

#### Backend
```bash
cd backend
pip install -r requirements-production.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

### Environment Setup

1. **Elasticsearch**: Configure cluster with planning data index
2. **Supabase**: Set up database tables and authentication
3. **AI Services**: Configure OpenAI/Anthropic API keys
4. **Reverse Proxy**: Set up nginx for production
5. **SSL**: Configure HTTPS certificates

## 📊 Performance & Monitoring

### Performance Features
- **Response Caching**: In-memory and Elasticsearch native caching
- **Query Optimization**: Optimized search queries and aggregations
- **Rate Limiting**: Per-user and per-endpoint rate limits
- **Compression**: Gzip compression for API responses
- **Connection Pooling**: Optimized database connections

### Monitoring Endpoints
- `GET /health` - Overall system health
- `GET /api/status` - Detailed performance metrics
- `GET /api/info` - API capabilities and version info

### Performance Metrics
- **Search Response Time**: < 200ms for cached queries
- **AI Processing Time**: < 2s for opportunity scoring
- **Cache Hit Rate**: > 80% for frequently accessed data
- **API Availability**: > 99.9% uptime target

## 🔐 Security

### Authentication & Authorization
- **JWT Tokens**: Supabase-managed authentication
- **Role-Based Access**: Different permissions per subscription tier
- **API Key Validation**: Secure API access control
- **Rate Limiting**: Protection against abuse

### Data Protection
- **Input Validation**: Pydantic models for data validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content Security Policy headers
- **CORS Configuration**: Controlled cross-origin access

### Privacy & Compliance
- **GDPR Compliance**: User data protection and deletion
- **Data Encryption**: TLS encryption for data in transit
- **Audit Logging**: Complete audit trail of user actions
- **Secure Storage**: Encrypted storage of sensitive data

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:e2e
```

### Test Coverage
- **Backend**: > 85% code coverage
- **Frontend**: > 80% component coverage
- **E2E Tests**: Critical user journey coverage

## 📈 Subscription Tiers

### 🆓 Starter Plan - FREE
- 20 AI-enhanced searches per month
- 5 full application profiles with AI insights
- Basic opportunity scores
- Email support

### 🔹 Professional Plan - £199.99/month
- Unlimited AI-enhanced searches
- Full AI application intelligence
- Advanced filtering and semantic search
- Email alerts and saved searches
- PDF report generation
- Priority support

### 🔹 Enterprise Plan - £499.99/month
- Up to 5 team members
- Full API access
- Custom AI model fine-tuning
- White-label options
- Advanced analytics
- Dedicated account manager

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use ESLint and Prettier
- **Commits**: Use conventional commit format
- **Documentation**: Update README and API docs

## 📞 Support

### Documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API reference
- [Component Library](frontend/CODE_EXAMPLES.md) - Frontend component examples
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions

### Getting Help
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Email Support**: Available for Professional and Enterprise users

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Planning Insights**: Design inspiration and UX reference
- **OpenAI**: AI capabilities and language models
- **Elasticsearch**: Search and analytics platform
- **Supabase**: Backend-as-a-Service infrastructure
- **Next.js & FastAPI**: Modern web frameworks

---

**Planning Explorer** - Transforming UK planning intelligence with AI-native technology. Built with ❤️ for property professionals who need smarter, faster insights.

[🚀 Get Started](#quick-start) | [📚 Documentation](#api-documentation) | [🤝 Contributing](#contributing) | [💬 Support](#support)
