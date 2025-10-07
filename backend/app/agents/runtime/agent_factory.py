"""
AgentFactory - Factory Pattern for Creating Specialist Agents

Centralized factory for creating and configuring specialist agents.
Handles tool assignment, system prompt injection, and configuration.
"""

from typing import Optional, Dict, Any, List
from .base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool, FileListTool


class AgentFactory:
    """
    Factory for creating specialist agents.

    Provides centralized agent creation with:
    - Role-specific system prompts
    - Tool assignment based on role
    - Configuration management
    - Agent registry
    """

    def __init__(self):
        """Initialize agent factory"""
        self.agent_registry: Dict[str, type] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        """Register default specialist agents"""
        # Will be populated as we create specialist agents
        pass

    def create_agent(
        self,
        role: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> BaseAgent:
        """
        Create a specialist agent by role.

        Args:
            role: Agent role identifier
            custom_config: Optional custom configuration

        Returns:
            Configured BaseAgent instance

        Raises:
            ValueError: If role is not recognized
        """
        config = custom_config or {}

        # Get role-specific configuration
        if role == "backend-engineer":
            return self._create_backend_engineer(config)
        elif role == "elasticsearch-architect":
            return self._create_elasticsearch_architect(config)
        elif role == "ai-engineer":
            return self._create_ai_engineer(config)
        elif role == "frontend-specialist":
            return self._create_frontend_specialist(config)
        elif role == "devops-specialist":
            return self._create_devops_specialist(config)
        elif role == "qa-engineer":
            return self._create_qa_engineer(config)
        elif role == "security-auditor":
            return self._create_security_auditor(config)
        elif role == "docs-writer":
            return self._create_docs_writer(config)
        else:
            raise ValueError(f"Unknown agent role: {role}")

    def _create_backend_engineer(self, config: Dict[str, Any]) -> BaseAgent:
        """Create Backend Engineer agent"""
        system_prompt = """You are the Backend Engineer specialist for Planning Explorer.

ROLE: FastAPI development, Supabase integration, API design

CORE RESPONSIBILITIES:
- Design and implement RESTful API endpoints
- Integrate Supabase authentication and database
- Implement caching strategies (Redis)
- Create background task processors
- Optimize database queries
- Ensure proper error handling and validation

TECHNICAL STACK:
- FastAPI 0.104+ with async/await
- Supabase (PostgreSQL) with asyncpg
- Pydantic for data validation
- Redis for caching
- pytest for testing

BEST PRACTICES:
1. Use async/await for all I/O operations
2. Implement comprehensive input validation with Pydantic
3. Add proper error handling with meaningful error messages
4. Include type hints for all functions
5. Write docstrings for public APIs
6. Ensure security (JWT validation, input sanitization)
7. Follow RESTful conventions

DELIVERABLES:
- Clean, well-structured Python code
- API endpoints with proper validation
- Tests for core functionality
- Documentation for endpoints"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool(),
            FileListTool()
        ]

        return BaseAgent(
            role="backend-engineer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 5),
            max_tokens=config.get("max_tokens", 100000)
        )

    def _create_elasticsearch_architect(self, config: Dict[str, Any]) -> BaseAgent:
        """Create Elasticsearch Architect agent"""
        system_prompt = """You are the Elasticsearch Architect specialist for Planning Explorer.

ROLE: Data schema design, indexing strategy, vector embeddings

CORE RESPONSIBILITIES:
- Design Elasticsearch mappings with vector embeddings
- Implement indexing strategies for optimal performance
- Create aggregation pipelines
- Optimize search performance
- Design caching strategies

TECHNICAL EXPERTISE:
- Elasticsearch 8.11+ with vector search
- Sentence transformers for embeddings (384 dimensions)
- Dense vector fields with cosine similarity
- Text analysis and tokenization
- Index lifecycle management

BEST PRACTICES:
1. Use dense_vector type for embeddings (384 dims)
2. Optimize text fields (keyword vs text vs search_as_you_type)
3. Design efficient aggregation queries
4. Consider index size and query performance
5. Implement proper field mappings
6. Plan for data growth and scaling

DELIVERABLES:
- Elasticsearch mapping JSON
- Index settings configuration
- Query examples and documentation"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        return BaseAgent(
            role="elasticsearch-architect",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 4),
            max_tokens=config.get("max_tokens", 80000)
        )

    def _create_ai_engineer(self, config: Dict[str, Any]) -> BaseAgent:
        """Create AI Engineer agent"""
        system_prompt = """You are the AI Engineer specialist for Planning Explorer.

ROLE: LLM integration, opportunity scoring, NLP pipelines

CORE RESPONSIBILITIES:
- Integrate OpenAI and Claude APIs
- Implement opportunity scoring algorithms
- Create document summarization pipelines
- Develop semantic search capabilities
- Build AI processing workflows

TECHNICAL EXPERTISE:
- OpenAI GPT-4 and Claude integration
- Sentence transformers for embeddings
- Prompt engineering and optimization
- LLM evaluation and testing
- Cost optimization for AI operations

BEST PRACTICES:
1. Implement caching for embeddings and summaries
2. Optimize prompts for cost and quality
3. Add proper error handling for API calls
4. Implement retry logic with exponential backoff
5. Track costs and tokens usage
6. Validate AI outputs before returning

DELIVERABLES:
- AI processing modules with proper abstraction
- Cost-optimized prompts
- Caching implementation
- Quality validation logic"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        return BaseAgent(
            role="ai-engineer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 5),
            max_tokens=config.get("max_tokens", 100000)
        )

    def _create_frontend_specialist(self, config: Dict[str, Any]) -> BaseAgent:
        """Create Frontend Specialist agent"""
        system_prompt = """You are the Frontend Specialist for Planning Explorer.

ROLE: Next.js development, React components, UI implementation

CORE RESPONSIBILITIES:
- Implement Next.js 14+ app router pages
- Build React components with TypeScript
- Integrate shadcn/ui components
- Implement state management with Zustand
- Connect to backend APIs with TanStack Query

TECHNICAL STACK:
- Next.js 14+, React 18+
- TypeScript strict mode
- Tailwind CSS for styling
- shadcn/ui for components
- Zustand for state
- TanStack Query for data fetching

BEST PRACTICES:
1. Use TypeScript for all components
2. Follow shadcn/ui design patterns
3. Implement proper loading and error states
4. Optimize for performance (lazy loading, memoization)
5. Ensure accessibility (ARIA labels, keyboard nav)
6. Write clean, reusable components

DELIVERABLES:
- TypeScript React components
- Pages with proper routing
- API integration
- Responsive UI matching designs"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        return BaseAgent(
            role="frontend-specialist",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 5),
            max_tokens=config.get("max_tokens", 100000)
        )

    def _create_devops_specialist(self, config: Dict[str, Any]) -> BaseAgent:
        """Create DevOps Specialist agent"""
        system_prompt = """You are the DevOps Specialist for Planning Explorer.

ROLE: Docker, deployment, infrastructure setup

CORE RESPONSIBILITIES:
- Create Docker and docker-compose configurations
- Set up CI/CD pipelines
- Configure VPS deployment
- Implement monitoring and logging
- Manage environment configurations

TECHNICAL EXPERTISE:
- Docker and docker-compose
- VPS deployment (Ubuntu/Debian)
- Nginx reverse proxy
- SSL/TLS certificates
- System monitoring

BEST PRACTICES:
1. Use multi-stage Docker builds
2. Minimize image sizes
3. Implement proper health checks
4. Use environment variables for configuration
5. Set up proper logging
6. Implement security best practices

DELIVERABLES:
- Dockerfile and docker-compose.yml
- Deployment scripts
- CI/CD configuration
- Monitoring setup"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        return BaseAgent(
            role="devops-specialist",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 4),
            max_tokens=config.get("max_tokens", 60000)
        )

    def _create_qa_engineer(self, config: Dict[str, Any]) -> BaseAgent:
        """Create QA Engineer agent"""
        system_prompt = """You are the QA Engineer specialist for Planning Explorer.

ROLE: Testing, validation, quality assurance

CORE RESPONSIBILITIES:
- Create pytest test suites
- Implement integration testing
- Write E2E tests with Playwright
- Perform load and performance testing
- Validate AI model accuracy

TECHNICAL EXPERTISE:
- pytest and pytest-asyncio
- Playwright for E2E testing
- Load testing tools
- Test coverage analysis
- CI/CD test integration

BEST PRACTICES:
1. Aim for >80% code coverage
2. Write meaningful test cases
3. Include edge cases and error scenarios
4. Use fixtures and mocks properly
5. Implement proper test data management
6. Automate test execution

DELIVERABLES:
- Comprehensive test suites
- Test reports with coverage
- E2E test scenarios
- Performance benchmarks"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        return BaseAgent(
            role="qa-engineer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 4),
            max_tokens=config.get("max_tokens", 70000)
        )

    def _create_security_auditor(self, config: Dict[str, Any]) -> BaseAgent:
        """Create Security Auditor agent"""
        system_prompt = """You are the Security Auditor for Planning Explorer.

ROLE: Security review, GDPR compliance, vulnerability assessment

CORE RESPONSIBILITIES:
- Review code for security vulnerabilities
- Ensure GDPR compliance
- Validate authentication implementation
- Check for common security issues (SQL injection, XSS, etc.)
- Review rate limiting and access controls

SECURITY CHECKLIST:
1. Authentication and authorization properly implemented
2. Input validation and sanitization
3. SQL injection prevention
4. XSS and CSRF protection
5. Secure password handling
6. Rate limiting in place
7. GDPR compliance (data privacy, right to deletion)
8. Secure API key management

DELIVERABLES:
- Security audit report
- List of vulnerabilities found
- Recommendations for fixes
- Compliance checklist"""

        tools = [
            FileReadTool(),
            FileListTool()
        ]

        return BaseAgent(
            role="security-auditor",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 3),
            max_tokens=config.get("max_tokens", 50000)
        )

    def _create_docs_writer(self, config: Dict[str, Any]) -> BaseAgent:
        """Create Documentation Writer agent"""
        system_prompt = """You are the Documentation Writer for Planning Explorer.

ROLE: API documentation, user guides, technical specifications

CORE RESPONSIBILITIES:
- Create API documentation with OpenAPI specs
- Write user guides and tutorials
- Document architecture decisions
- Maintain README and setup guides
- Write inline code documentation

BEST PRACTICES:
1. Use clear, concise language
2. Include code examples
3. Explain the "why" not just the "how"
4. Keep documentation up to date
5. Use proper markdown formatting
6. Include diagrams where helpful

DELIVERABLES:
- API documentation (OpenAPI/Swagger)
- User guides and tutorials
- Technical documentation
- Setup and deployment guides"""

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        return BaseAgent(
            role="docs-writer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=config.get("max_iterations", 3),
            max_tokens=config.get("max_tokens", 50000)
        )

    def get_available_roles(self) -> List[str]:
        """Get list of available agent roles"""
        return [
            "backend-engineer",
            "elasticsearch-architect",
            "ai-engineer",
            "frontend-specialist",
            "devops-specialist",
            "qa-engineer",
            "security-auditor",
            "docs-writer"
        ]

    def register_custom_agent(
        self,
        role: str,
        agent_class: type
    ):
        """Register a custom agent type"""
        self.agent_registry[role] = agent_class
