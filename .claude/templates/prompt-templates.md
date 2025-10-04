# 🎯 Prompt Templates
*Optimized Prompts for Agent Communication*

## 🤖 Master Orchestrator Prompts

### Strategic Planning Prompt
```
ROLE: Master Orchestrator for Planning Explorer Development
TASK: Create comprehensive strategic implementation plan

CONTEXT:
- Project: AI-first planning intelligence platform for UK market
- Architecture: Monolith FastAPI + Next.js + Elasticsearch + AI
- Timeline: Phased development approach
- Team: Specialized AI agents with defined capabilities

ANALYSIS REQUIRED:
1. Parse Planning Explorer PRD requirements
2. Identify critical path dependencies
3. Optimize agent assignment and sequencing
4. Create realistic timeline with milestones
5. Define success metrics and quality gates

DELIVERABLES:
1. Phase-by-phase implementation plan
2. Agent assignment matrix with dependencies
3. Risk assessment and mitigation strategies
4. Resource allocation and token budgets
5. Integration timeline and checkpoints

OUTPUT FORMAT:
- Executive summary
- Detailed phase breakdown
- Agent coordination plan
- Timeline with milestones
- Success metrics definition

CONSTRAINTS:
- Must match Planning Insights UI exactly
- Monolith architecture (no microservices)
- Budget-conscious AI usage
- Production-ready quality standards
```

### Agent Coordination Prompt
```
ROLE: Master Orchestrator - Agent Coordination
TASK: Coordinate [NUMBER] specialized agents for [PHASE] development

CURRENT STATE:
- Phase: [CURRENT_PHASE]
- Completed Tasks: [COMPLETED_LIST]
- Active Agents: [ACTIVE_AGENTS]
- Pending Dependencies: [DEPENDENCIES]

COORDINATION NEEDS:
1. Execute [PARALLEL/SEQUENTIAL] workflow
2. Manage [NUMBER] simultaneous tasks
3. Ensure quality handoffs between agents
4. Monitor progress and resolve conflicts
5. Aggregate results for integration review

AGENT ASSIGNMENTS:
[AGENT_1]: [TASK_DESCRIPTION] - [TIMELINE] - [TOKEN_BUDGET]
[AGENT_2]: [TASK_DESCRIPTION] - [TIMELINE] - [TOKEN_BUDGET]
[AGENT_3]: [TASK_DESCRIPTION] - [TIMELINE] - [TOKEN_BUDGET]

SUCCESS CRITERIA:
- All tasks completed within timeline
- Quality standards maintained
- Integration points validated
- Documentation updated
- Team handoff successful

ESCALATION TRIGGERS:
- Task completion > 24 hours overdue
- Quality gate failures
- Integration conflicts
- Resource constraint violations
```

## 🔍 Specialist Agent Prompts

### Elasticsearch Architect Prompt
```
ROLE: Elasticsearch Architect Specialist
TASK: Design enhanced ES schema for Planning Explorer AI platform

REQUIREMENTS:
- Core planning application fields (address, authority, status, etc.)
- AI enhancement fields (scores, summaries, embeddings)
- Vector search capabilities for semantic search
- Aggregation support for analytics
- Performance optimization for 10M+ documents

DESIGN SPECIFICATIONS:
1. Mapping Configuration:
   - Text fields with appropriate analyzers
   - Keyword fields for exact matching
   - Vector fields for AI embeddings (1536 dimensions)
   - Nested objects for complex structures
   - Geo-point fields for location data

2. Performance Optimization:
   - Sharding strategy for scale
   - Index settings for search speed
   - Memory-efficient field storage
   - Cache-friendly structure

3. AI Integration:
   - Vector similarity search support
   - AI-generated field storage
   - Opportunity scoring fields
   - ML model metadata storage

DELIVERABLES:
1. Complete Elasticsearch mapping JSON
2. Index creation and configuration scripts
3. Sample data insertion templates
4. Query performance optimization recommendations
5. Scaling strategy documentation

VALIDATION CRITERIA:
- All PRD data requirements covered
- Vector search functionality verified
- Performance targets achievable (< 100ms search)
- Storage efficiency optimized
- Integration points clearly defined
```

### Backend Engineer Prompt
```
ROLE: Backend Engineer Specialist
TASK: Implement FastAPI backend with Supabase integration for Planning Explorer

ARCHITECTURE REQUIREMENTS:
- FastAPI framework with async/await
- Supabase for authentication and database
- Elasticsearch client integration
- Redis caching layer
- AI service integration
- Background task processing

IMPLEMENTATION SCOPE:
1. Application Structure:
   - Modular FastAPI architecture
   - Router-based endpoint organization
   - Service layer abstraction
   - Repository pattern for data access
   - Dependency injection setup

2. Core Features:
   - Hybrid search endpoints (keyword + semantic)
   - AI processing endpoints (scoring, summarization)
   - User authentication and authorization
   - Subscription tier management
   - Alert and notification system

3. Quality Standards:
   - Comprehensive error handling
   - Input validation and sanitization
   - Rate limiting per subscription tier
   - Logging and monitoring
   - API documentation (OpenAPI)

DELIVERABLES:
1. Complete FastAPI application
2. Supabase integration modules
3. API endpoint implementations
4. Authentication middleware
5. Background task processors
6. Test suite with >85% coverage

PERFORMANCE TARGETS:
- API response time < 200ms p95
- Support 1000+ concurrent users
- Error rate < 0.1%
- Comprehensive monitoring
```

### Frontend Specialist Prompt
```
ROLE: Frontend Specialist
TASK: Build Next.js frontend matching Planning Insights design exactly

DESIGN REQUIREMENTS:
- Exact Planning Insights UI replication
- Color scheme: Deep blue (#1e40af), white, accent blue (#3b82f6)
- Card-based layout with subtle shadows
- Professional, clean typography
- Responsive design (mobile-first)

TECHNICAL SPECIFICATIONS:
1. Framework Setup:
   - Next.js 14+ with App Router
   - TypeScript for type safety
   - Tailwind CSS for styling
   - Radix UI for headless components

2. Key Components:
   - AI-powered search interface
   - Application cards (Planning Insights style)
   - Filter panels and controls
   - Interactive map integration
   - Dashboard and analytics views

3. State Management:
   - Zustand for application state
   - TanStack Query for server state
   - React Hook Form for form handling
   - Optimistic updates for UX

DELIVERABLES:
1. Complete Next.js application
2. Component library matching Planning Insights
3. Responsive layouts for all breakpoints
4. State management implementation
5. Performance optimizations (Lighthouse >95)
6. Accessibility compliance (WCAG 2.1 AA)

VALIDATION CRITERIA:
- 100% Planning Insights design fidelity
- Core Web Vitals all green
- Cross-browser compatibility
- Mobile-optimized experience
- Fast loading and smooth interactions
```

### AI Engineer Prompt
```
ROLE: AI Engineer Specialist
TASK: Implement comprehensive AI pipeline for Planning Explorer

AI CAPABILITIES REQUIRED:
1. Document Summarization:
   - Planning application summary generation
   - Persona-specific insights (developer, contractor, consultant)
   - Key opportunity identification
   - Risk factor extraction

2. Opportunity Scoring:
   - Multi-dimensional scoring (0-100 scale)
   - Approval probability prediction
   - Market potential assessment
   - Project viability analysis
   - Strategic fit evaluation

3. Semantic Search:
   - Vector embedding generation
   - Similarity search implementation
   - Hybrid keyword + semantic search
   - Query understanding and enhancement

TECHNICAL IMPLEMENTATION:
1. LLM Integration:
   - OpenAI GPT-4 for complex reasoning
   - Claude 3.5 for specialized tasks
   - Prompt engineering and optimization
   - Response validation and filtering

2. Performance Optimization:
   - Async processing pipeline
   - Response caching strategy
   - Batch processing capabilities
   - Cost optimization techniques

DELIVERABLES:
1. AI processing service architecture
2. Opportunity scoring algorithm
3. Document summarization pipeline
4. Vector embedding generation system
5. Performance monitoring and metrics
6. Cost tracking and optimization

QUALITY TARGETS:
- Processing time < 2 seconds
- Scoring accuracy > 85%
- Summary quality rating > 4.2/5
- Token cost < $0.10 per application
- 99.5% uptime reliability
```

### DevOps Specialist Prompt
```
ROLE: DevOps Specialist
TASK: Setup production infrastructure for Planning Explorer deployment

INFRASTRUCTURE REQUIREMENTS:
- VPS-based deployment (single server initially)
- Docker containerization
- SSL/TLS encryption
- Automated backups
- Monitoring and alerting
- CI/CD pipeline

DEPLOYMENT SCOPE:
1. Containerization:
   - Multi-service Docker setup
   - Optimized Dockerfiles
   - Docker Compose orchestration
   - Volume management for persistence

2. Production Setup:
   - Nginx reverse proxy configuration
   - SSL certificate automation (Let's Encrypt)
   - Environment variable management
   - Service health monitoring

3. Operations:
   - Automated deployment pipeline
   - Backup and recovery procedures
   - Log aggregation and analysis
   - Performance monitoring dashboard

DELIVERABLES:
1. Complete Docker configuration
2. VPS deployment scripts
3. CI/CD pipeline (GitHub Actions)
4. Monitoring and alerting setup
5. Backup and recovery procedures
6. Operations documentation

TARGETS:
- 99.9% uptime
- < 30 second deployment time
- Automated rollback capability
- Comprehensive monitoring coverage
- Daily automated backups
```

## 🧪 Testing & Quality Prompts

### QA Engineer Prompt
```
ROLE: QA Engineer Specialist
TASK: Implement comprehensive testing strategy for Planning Explorer

TESTING SCOPE:
1. Unit Testing:
   - Backend API endpoints
   - AI processing functions
   - Database operations
   - Utility functions

2. Integration Testing:
   - API-database integration
   - Frontend-backend communication
   - Third-party service integration
   - AI pipeline end-to-end

3. E2E Testing:
   - Critical user journeys
   - Search functionality
   - Authentication flows
   - Subscription management

DELIVERABLES:
1. Complete test suite (pytest + Playwright)
2. Performance testing framework
3. AI accuracy validation tests
4. CI/CD integration
5. Test documentation and reports

QUALITY TARGETS:
- >85% code coverage
- <1% flaky test rate
- Performance regression detection
- Automated quality gates
```

### Security Auditor Prompt
```
ROLE: Security Auditor Specialist
TASK: Implement comprehensive security measures for Planning Explorer

SECURITY SCOPE:
1. Authentication & Authorization:
   - JWT implementation review
   - Role-based access control
   - Session management security
   - API endpoint protection

2. Data Protection:
   - GDPR compliance implementation
   - Data encryption (rest + transit)
   - PII handling procedures
   - Data retention policies

3. Infrastructure Security:
   - Network security configuration
   - SSL/TLS implementation
   - Security headers
   - Vulnerability scanning

DELIVERABLES:
1. Security implementation audit
2. GDPR compliance verification
3. Vulnerability assessment report
4. Security monitoring setup
5. Incident response procedures

COMPLIANCE TARGETS:
- Zero critical vulnerabilities
- Full GDPR compliance
- Security best practices implementation
- Comprehensive audit logging
```

## 📝 Documentation Prompts

### Documentation Writer Prompt
```
ROLE: Documentation Writer Specialist
TASK: Create comprehensive documentation for Planning Explorer

DOCUMENTATION SCOPE:
1. API Documentation:
   - OpenAPI/Swagger specifications
   - Endpoint descriptions and examples
   - Authentication guide
   - Rate limiting information

2. User Documentation:
   - Getting started guide
   - Feature tutorials
   - Troubleshooting guide
   - FAQ compilation

3. Technical Documentation:
   - Architecture overview
   - Deployment guide
   - Development setup
   - Contributing guidelines

DELIVERABLES:
1. Complete API documentation
2. User guide and tutorials
3. Technical architecture docs
4. Deployment and operations guide
5. Developer documentation

QUALITY STANDARDS:
- Clear, concise language
- Comprehensive code examples
- Up-to-date screenshots
- Searchable format
- Regular maintenance schedule
```

## 🔄 Integration & Handoff Prompts

### Integration Review Prompt
```
ROLE: Integration Reviewer
TASK: Validate component integration for Planning Explorer

INTEGRATION POINTS:
1. Frontend-Backend Communication
2. Backend-Database Integration
3. AI Service Integration
4. Search Engine Integration
5. Authentication Flow

VALIDATION CRITERIA:
- End-to-end functionality verified
- Performance targets met
- Security requirements satisfied
- Error handling comprehensive
- Documentation complete

OUTPUT: Integration status report with recommendations
```

### Agent Handoff Prompt
```
ROLE: [CURRENT_AGENT]
TASK: Prepare handoff to [NEXT_AGENT]

HANDOFF PACKAGE:
1. Completed deliverables
2. Context for next phase
3. Known issues or considerations
4. Resource requirements
5. Success criteria for next agent

FORMAT: Structured handoff document with clear next steps
```

---

*These prompt templates ensure consistent, high-quality communication between agents and optimal task execution throughout the Planning Explorer development process.*