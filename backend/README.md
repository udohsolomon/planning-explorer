# Planning Explorer Backend API

The UK's first AI-native planning intelligence platform backend, built with FastAPI, Elasticsearch, and Supabase.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Access to Elasticsearch cluster (credentials in .env)
- Supabase project (for user management)

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd "Planning Explorer/backend"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

5. **Start the API**
   ```bash
   python start.py
   ```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗️ Architecture

### Tech Stack
- **FastAPI**: Modern Python web framework
- **Elasticsearch**: Search engine with existing planning data
- **Supabase**: PostgreSQL + Auth + Storage for user management
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

### Project Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   └── api.py              # API router configuration
│   │   └── endpoints/
│   │       ├── search.py           # Search endpoints
│   │       ├── applications.py     # Planning application endpoints
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── user.py            # User management endpoints
│   │       └── ai.py              # AI feature endpoints
│   ├── core/
│   │   ├── config.py              # Application settings
│   │   └── database.py            # Database lifecycle management
│   ├── db/
│   │   ├── elasticsearch.py       # Elasticsearch client
│   │   └── supabase.py           # Supabase client
│   ├── middleware/
│   │   ├── auth.py               # Authentication middleware
│   │   ├── cors.py               # CORS configuration
│   │   ├── error_handler.py      # Error handling
│   │   ├── logging.py            # Request/response logging
│   │   ├── rate_limit.py         # Rate limiting
│   │   └── performance.py        # Caching, compression, security
│   ├── models/
│   │   ├── planning.py           # Planning application models
│   │   └── user.py               # User models
│   ├── services/
│   │   └── search.py             # Search business logic
│   └── main.py                   # FastAPI application
├── requirements.txt              # Python dependencies
├── .env.example                 # Environment variables template
├── start.py                     # Startup script
└── README.md                    # This file
```

## 🔌 API Endpoints

### Search & Planning Data
- `GET /api/v1/applications` - List planning applications with filters
- `GET /api/v1/applications/{id}` - Get application details
- `POST /api/v1/search` - Advanced search with filters
- `POST /api/v1/search/semantic` - AI-powered semantic search
- `GET /api/v1/aggregations` - Market intelligence aggregations

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/user` - Get current user
- `POST /api/v1/auth/logout` - User logout

### User Features
- `GET /api/v1/user/searches` - Get saved searches
- `POST /api/v1/user/searches` - Save search
- `GET /api/v1/user/alerts` - Get user alerts
- `POST /api/v1/user/alerts` - Create alert
- `GET /api/v1/user/reports` - Get user reports

### AI Features
- `POST /api/v1/ai/opportunity-score` - Calculate opportunity scores
- `POST /api/v1/ai/summarize` - Generate AI summaries
- `GET /api/v1/ai/insights` - Get market insights

## 🔧 Configuration

### Environment Variables

Required variables in `.env`:

```bash
# Elasticsearch (existing data)
ELASTICSEARCH_NODE=https://95.217.117.251:9200/
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=d41=*sDuOnhQqXonYz2U

# Supabase (user management)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# API Configuration
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO

# Performance
CACHE_TTL=300
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Supabase Setup

The application requires these Supabase tables:

```sql
-- User profiles
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT NOT NULL,
    full_name TEXT,
    company TEXT,
    role TEXT DEFAULT 'free',
    api_calls_this_month INTEGER DEFAULT 0,
    max_api_calls_per_month INTEGER DEFAULT 1000,
    max_saved_searches INTEGER DEFAULT 10,
    max_alerts INTEGER DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Saved searches
CREATE TABLE saved_searches (
    search_id TEXT PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id),
    name TEXT NOT NULL,
    description TEXT,
    query TEXT,
    filters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User alerts
CREATE TABLE user_alerts (
    alert_id TEXT PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id),
    name TEXT NOT NULL,
    query TEXT,
    filters JSONB,
    frequency TEXT DEFAULT 'daily',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User reports
CREATE TABLE user_reports (
    report_id TEXT PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id),
    name TEXT NOT NULL,
    report_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    content JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage tracking
CREATE TABLE api_usage (
    usage_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id),
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔍 Data Integration

### Elasticsearch Integration
- Connects to existing planning applications index
- Uses comprehensive schema with AI enhancements
- Built-in caching for performance
- Vector search capabilities for AI features

### Planning Application Schema
The API works with planning applications containing:
- Core application data (reference, authority, address, status)
- Development details (type, description, project value)
- Geographic information (location, postcode, ward)
- AI enhancements (opportunity scores, market insights)
- Documents and consultation responses

## 🚀 Performance Features

### Caching
- In-memory response caching
- Elasticsearch native caching
- Configurable TTL per endpoint type

### Rate Limiting
- IP-based limits for anonymous users
- User-based limits for authenticated users
- Different limits per endpoint type

### Optimization
- Response compression (gzip)
- Request size limits
- Query optimization
- Connection pooling

## 🔐 Security

### Authentication
- Supabase JWT authentication
- Role-based access control
- API key validation

### Security Headers
- CORS protection
- XSS protection
- Content type validation
- Frame options

### Data Protection
- Input validation with Pydantic
- SQL injection prevention
- Rate limiting
- Error message sanitization

## 🧪 Development

### Running in Development
```bash
python start.py
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Health Checks
- `/health` - Overall system health
- `/api/status` - Detailed API status
- `/api/info` - API information and features

### Logging
Structured logging with:
- Request/response tracking
- Performance monitoring
- Error tracking
- Database connection status

## 📊 Monitoring

### Health Endpoints
- **GET /health** - Service health status
- **GET /api/status** - Performance metrics
- **GET /api/info** - API capabilities

### Performance Metrics
- Response times
- Cache hit rates
- Error rates
- Database connection status

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
1. Set production environment variables
2. Configure Supabase tables
3. Verify Elasticsearch connectivity
4. Set up reverse proxy (nginx)
5. Configure SSL certificates

## 📞 Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review health status at `/health`
3. Check logs for error details
4. Verify environment configuration

## 🔄 Integration with Frontend

The backend is designed to work with the Planning Explorer frontend:
- CORS configured for localhost:3000 (development)
- Authentication tokens compatible with Supabase
- Response formats optimized for React components
- Real-time features ready for WebSocket integration

## 📈 Subscription Tiers

The API supports three subscription tiers:

### Free Tier
- 1,000 API calls/month
- 10 saved searches
- 5 alerts
- Basic search and application details

### Professional Tier
- 10,000 API calls/month
- 100 saved searches
- 50 alerts
- Full AI features
- Report generation
- Market insights

### Enterprise Tier
- Unlimited API calls
- Unlimited saved searches/alerts
- All features
- Custom integrations
- Dedicated support

---

**Planning Explorer Backend** - Revolutionizing UK planning intelligence with AI-native technology.