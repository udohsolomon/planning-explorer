# Planning Explorer - AI Coding Subagents Framework
*Last Updated: September 2025*

## 🎯 Project Overview
**Planning Explorer revolutionises property intelligence by transforming weeks of manual research into minutes of AI-powered insights.**

Planning Explorer is the UK's first AI-native planning intelligence platform that empowers property developers, consultants, suppliers, and investors to make faster, smarter decisions with unprecedented confidence. This project uses an advanced AI subagent framework to accelerate development through specialized agents working in coordination.

**Mission**: Democratise planning intelligence by making comprehensive UK planning data accessible, actionable, and intelligent for every property professional.

**Project PRD**: `Planning_explorer_prd.md`
**Framework Location**: `.claude/` directory
**Current Phase**: Development Setup

## 🤖 AI Subagents Framework Explained

### Framework Architecture
**This is a CUSTOM role-switching framework**, NOT the built-in Claude Code Task tool. The agents are instruction files that Claude loads into context and executes directly.

**How it works:**
1. **Specialist files** (`.claude/specialists/*.md`) contain detailed instructions for specific roles
2. **Claude loads** these instructions and adopts that specialist persona
3. **Session tracking** via `.claude/sessions/current-session.md` maintains state
4. **TodoWrite** tracks progress natively (NO Task tool needed)
5. **Master Orchestrator** coordinates multi-specialist workflows

**Key Distinction:**
- ❌ **NOT**: Using `@agent-general-purpose` with Task tool
- ✅ **YES**: Direct context loading and role adoption

### Master Orchestrator Invocation
To start a comprehensive development session with the master orchestrator:
```
Load and follow the instructions from @.claude/orchestrator/master-orchestrator.md
Analyze the PRD and coordinate the Planning Explorer build.
```

### Direct Specialist Invocation
For specific tasks, invoke specialists by directly loading their instructions:
```
Load and follow the instructions from @.claude/specialists/elasticsearch-architect.md
Design the enhanced ES schema for Planning Explorer with vector embeddings.

Load and follow the instructions from @.claude/specialists/frontend-specialist.md
Implement the Planning Insights UI design with shadcn/ui components.

Load and follow the instructions from @.claude/specialists/ai-engineer.md
Integrate the opportunity scoring system.
```

### Sequential Workflow Execution
For coordinated multi-specialist workflows:
```
1. Load @.claude/orchestrator/master-orchestrator.md
2. Create a development plan for [feature]
3. When ready, switch to @.claude/specialists/elasticsearch-architect.md
4. After schema is complete, switch to @.claude/specialists/backend-engineer.md
5. Update @.claude/sessions/current-session.md after each phase
```

### How Specialists Coordinate
**Session State Management:**
- Each specialist updates `.claude/sessions/current-session.md` with progress
- Next specialist reads session state to understand context
- Master Orchestrator reviews session and decides next specialist

**Native TodoWrite Integration:**
- Specialists use TodoWrite (not Task tool) for task tracking
- Todo items persist across specialist switches
- Master Orchestrator reviews todos to coordinate work

## 📋 Project Context

### Tech Stack
- **Backend**: FastAPI (Python 3.11+), Single monolith architecture
- **Data & Search**: Elasticsearch (Single node + embeddings index)
  - Planning applications data with AI enhancements
  - Vector embeddings for semantic search
  - Built-in caching and performance optimisation
- **Authentication**: Supabase Authentication
  - User authentication and authorization
  - JWT session management
  - User profile management
  - Role-based access control
- **User Management**: Supabase + PostgreSQL
  - User profiles, preferences, and settings
  - Role-based access control and permissions
  - Usage tracking and analytics
  - Subscription and billing management
- **Frontend**: Next.js 14+, React 18+, Tailwind CSS, shadcn/ui, Zustand, TanStack Query
- **UI Components**: shadcn/ui (Radix UI + CVA), React Hook Form + Zod validation
- **Testing**: Playwright MCP Server (E2E automation), Jest, React Testing Library
- **Tooling**: Shadcn UI MCP Server (component generation), TypeScript
- **AI/ML**: OpenAI GPT-4, Claude 3.5, Sentence Transformers
- **Deployment**: Docker, VPS, No Redis dependency

### Key Features to Build
1. **Intelligent Opportunity Detection**: AI automatically identifies and scores opportunities
2. **Instant Market Intelligence**: Comprehensive insights in seconds, not weeks
3. **Personalised Business Intelligence**: AI learns preferences and highlights relevant opportunities
4. **Predictive Analytics**: Approval likelihood and timeline predictions
5. **Smart Alerts & Notifications**: Never miss relevant opportunities
6. **Planning Insights UI**: Exact design match with enhanced AI features
7. **Freemium Model**: Starter (free), Professional (£199.99), Enterprise (£499.99)

### Development Priorities
1. **Elasticsearch Schema**: Enhanced schema with vector embeddings and AI fields
2. **Supabase Setup**: User authentication and profile management
3. **FastAPI Backend**: Monolith architecture with ES and Supabase integration
4. **AI Processing Pipeline**: Opportunity scoring, summarisation, and embeddings generation
5. **Next.js Frontend**: shadcn/ui components matching Planning Insights design exactly
6. **Semantic Search**: Vector similarity search with hybrid filtering
7. **User Features**: Saved searches, reports, alerts, and notifications with Supabase
8. **Organization Features**: Multi-tenant organization management and team collaboration
9. **Security & Compliance**: Advanced audit logging, rate limiting, and security monitoring
10. **Automated Testing**: Playwright MCP Server for E2E validation
11. **Docker Deployment**: Single VPS deployment without Redis dependency

## 🔧 Agent Framework Structure

### Available Agents
- **master-orchestrator**: Strategic planning and coordination
- **elasticsearch-architect**: Data schema and indexing
- **backend-engineer**: FastAPI and Supabase implementation
- **frontend-specialist**: Next.js and UI development
- **ai-engineer**: LLM integration and AI features
- **devops-specialist**: Docker and deployment
- **qa-engineer**: Testing and validation
- **security-auditor**: Security and compliance
- **docs-writer**: Documentation generation

### Agent Communication Protocol
Agents share context through:
- `.claude/agents.md` - Central configuration
- `.claude/sessions/current-session.md` - Active state
- TodoWrite integration for task tracking
- Structured result passing between agents

## 🚀 Common Workflows

### Full Stack Development
```
1. Invoke master-orchestrator for strategic planning
2. Execute elasticsearch-architect for schema design
3. Parallel execution:
   - backend-engineer for API development
   - frontend-specialist for shadcn/ui component implementation
4. ai-engineer for AI integration
5. qa-engineer for testing with Playwright MCP Server automation
6. master-orchestrator for final integration review
```

### AI Feature Implementation
```
1. ai-engineer analyzes requirements
2. elasticsearch-architect updates schema
3. backend-engineer creates endpoints
4. frontend-specialist adds shadcn/ui components with AI integration
5. qa-engineer validates AI accuracy with automated testing
```

### Deployment Setup
```
1. devops-specialist creates Docker configuration
2. security-auditor reviews security settings
3. docs-writer generates deployment guide
4. devops-specialist finalizes VPS setup
```

## 📊 Success Metrics

### Development KPIs
- Code coverage > 80%
- API response time < 200ms
- AI processing < 2 seconds
- Opportunity score accuracy > 85%
- UI matches Planning Insights 100%
- Semantic search relevance > 90%
- ES vector search performance < 100ms
- User feature adoption > 70%

### Agent Performance
- Task completion rate > 95%
- Token efficiency < 100k per agent
- Parallel execution success > 90%
- Context retention accuracy > 95%

## 🛠️ Tool Preferences

### By Agent Type
- **elasticsearch-architect**: Glob, Grep, Read, Edit
- **backend-engineer**: Write, Edit, Bash, Read
- **frontend-specialist**: Write, Edit, WebFetch
- **ai-engineer**: WebFetch, Read, Write, Edit
- **devops-specialist**: Bash, Write, Edit
- **qa-engineer**: Bash, Read, Grep
- **security-auditor**: Grep, Read, Bash
- **docs-writer**: Write, Read, WebFetch

### Optimization Rules
- Use specialist role-switching for complex multi-step operations
- Batch Read operations for efficiency
- Prefer Edit tool for file modifications
- Use parallel Bash for independent commands
- Update session state after each major milestone

## 💡 Best Practices

### Agent Invocation
1. Always provide clear context and objectives
2. Reference the PRD for requirements
3. Use TodoWrite for task tracking
4. Request parallel execution when possible
5. Ask for progress updates between phases

### Code Quality
- Follow existing code patterns
- Match Planning Insights UI exactly
- Implement comprehensive error handling
- Add type hints and validation
- Optimize for performance

### Token Optimization
- Share context through agents.md
- Use focused prompts for specialists
- Batch similar operations
- Clear session data after completion

## 🔄 Session Management

### Current Session
Track active development in: `.claude/sessions/current-session.md`

### Session Commands
- Start new session: `Create new session in .claude/sessions/`
- Review progress: `Show current session status`
- Archive session: `Move current-session.md to session-history/`

## 📚 Quick References

### File Locations
- **PRD**: `Planning_explorer_prd.md`
- **Agents Config**: `.claude/agents.md`
- **Master Orchestrator**: `.claude/orchestrator/master-orchestrator.md`
- **Specialists**: `.claude/specialists/`
- **Templates**: `.claude/templates/`
- **Workflows**: `.claude/workflows/`

### Common Commands
```bash
# Check project structure
ls -la .claude/

# View agent configuration
cat .claude/agents.md

# Check current session
cat .claude/sessions/current-session.md

# Run tests
pytest tests/

# Start development server
uvicorn main:app --reload

# Build Docker image
docker-compose up --build
```

## 🆘 Troubleshooting

### Agent Issues
- If agent doesn't respond: Check agents.md configuration
- If context lost: Review current-session.md
- If parallel execution fails: Run agents sequentially
- If token limit reached: Clear session and restart

### Development Issues
- Import errors: Check requirements.txt
- UI mismatch: Reference Planning Insights design system exactly
- AI timeout: Use ES native caching, not external cache
- ES errors: Verify enhanced schema with vector embeddings
- Supabase auth issues: Check Supabase configuration and connection
- Authentication errors: Verify JWT configuration and session management
- No Redis: All caching handled by ES built-in mechanisms

## 🎯 Next Steps

1. **Initialize Framework**: Create all agent configurations
2. **Setup Development**: Install dependencies and tools
3. **Start Building**: Invoke master-orchestrator
4. **Iterate**: Use specialists for specific features
5. **Deploy**: Use devops-specialist for production setup

---

*Remember: This framework is designed for rapid, high-quality development. Use agents strategically, track progress with TodoWrite, and maintain clear communication between specialists.*