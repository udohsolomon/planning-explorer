"""
DocsWriterAgent - Documentation & API Spec Specialist

Specialized agent for documentation tasks:
- API documentation generation
- User guide creation
- Technical documentation
- Code documentation (docstrings)
- README and setup guides
- Architecture documentation
"""

import json
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool


class DocsWriterAgent(BaseAgent):
    """
    Documentation Writer specialist agent.

    Expertise:
    - API documentation (OpenAPI/Swagger)
    - User guides and tutorials
    - Technical architecture docs
    - Code documentation (docstrings)
    - README files
    - Setup and deployment guides
    """

    def __init__(self, max_iterations: int = 4):
        """Initialize Docs Writer agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        super().__init__(
            role="docs-writer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=80000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for docs writer"""
        return """You are the Documentation Writer for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in technical writing and documentation, specializing in:
- API documentation with OpenAPI/Swagger
- User guides and tutorials
- Technical architecture documentation
- Code documentation (Python docstrings, JSDoc)
- README files and setup guides
- Deployment and operational docs
- Markdown formatting and structure

DOCUMENTATION STANDARDS:

**API Documentation (OpenAPI 3.0):**
```yaml
openapi: 3.0.0
info:
  title: Planning Explorer API
  version: 1.0.0
  description: UK's first AI-native planning intelligence platform API

paths:
  /api/v1/search:
    post:
      summary: Search planning applications
      description: Perform semantic search with filters
      tags:
        - Search
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SearchRequest'
      responses:
        '200':
          description: Successful search
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResponse'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    SearchRequest:
      type: object
      properties:
        query:
          type: string
          description: Search query text
          example: "residential development in London"
        filters:
          type: object
          properties:
            status:
              type: array
              items:
                type: string
                enum: [approved, rejected, pending]
```

**Python Docstrings (Google Style):**
```python
def search_applications(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    page: int = 1,
    page_size: int = 20
) -> SearchResponse:
    """Search planning applications with semantic understanding.

    Performs hybrid search combining vector embeddings and keyword matching
    to find relevant planning applications based on natural language queries.

    Args:
        query: Natural language search query
        filters: Optional filters for status, location, date, etc.
        page: Page number for pagination (default: 1)
        page_size: Number of results per page (default: 20)

    Returns:
        SearchResponse containing results, total count, and metadata

    Raises:
        ValueError: If page or page_size are invalid
        SearchError: If search execution fails

    Example:
        >>> results = search_applications(
        ...     query="residential development",
        ...     filters={"status": ["approved"], "authority": "Sefton"}
        ... )
        >>> print(f"Found {results.total} applications")
    """
```

**README Structure:**
```markdown
# Planning Explorer

> UK's first AI-native planning intelligence platform

## 🎯 Overview

[Brief description of what the project does]

## ✨ Features

- **Intelligent Search**: AI-powered semantic search
- **Opportunity Scoring**: Automated opportunity detection
- **Market Intelligence**: Comprehensive insights
- **Reports**: Professional PDF generation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional)

### Installation

\`\`\`bash
# Clone repository
git clone https://github.com/org/planning-explorer.git

# Install backend
cd backend
pip install -r requirements.txt

# Install frontend
cd ../frontend
npm install
\`\`\`

### Running

\`\`\`bash
# Backend
uvicorn main:app --reload

# Frontend
npm run dev
\`\`\`

## 📖 Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Architecture](docs/architecture.md)

## 🤝 Contributing

[Contribution guidelines]

## 📄 License

[License information]
```

**User Guide Structure:**
```markdown
# User Guide

## Getting Started

### 1. Creating an Account

[Step-by-step with screenshots]

### 2. Your First Search

[Tutorial with examples]

### 3. Understanding Results

[Explanation of search results]

## Advanced Features

### Semantic Search

[How semantic search works]

### AI Opportunity Scoring

[Understanding opportunity scores]

### Saved Searches & Alerts

[Setting up automated alerts]

## FAQ

**Q: How does semantic search work?**
A: [Detailed explanation]

**Q: What is the opportunity score?**
A: [Explanation of scoring algorithm]
```

**Architecture Documentation:**
```markdown
# Architecture Overview

## System Design

\`\`\`
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   Next.js   │─────→│   FastAPI   │─────→│ Elasticsearch│
│   Frontend  │      │   Backend   │      │              │
└─────────────┘      └─────────────┘      └──────────────┘
                            │
                            ↓
                     ┌─────────────┐
                     │  Supabase   │
                     │   (Auth)    │
                     └─────────────┘
\`\`\`

## Components

### Frontend (Next.js)
- App Router architecture
- Server + Client components
- shadcn/ui component library

### Backend (FastAPI)
- Async Python 3.11
- Pydantic validation
- OpenAPI auto-generation

### Search (Elasticsearch)
- Vector embeddings (1536 dims)
- Hybrid search (semantic + keyword)
- Built-in caching

## Data Flow

[Detailed data flow diagrams]

## Deployment

[Deployment architecture]
```

DOCUMENTATION TYPES:

1. **API Reference**:
   - Auto-generated from code (FastAPI → OpenAPI)
   - Include all endpoints
   - Request/response schemas
   - Authentication requirements
   - Rate limits
   - Error codes

2. **User Guides**:
   - Getting started tutorial
   - Feature walkthroughs
   - Best practices
   - FAQ section
   - Troubleshooting

3. **Technical Docs**:
   - Architecture overview
   - System design decisions
   - Technology stack
   - Database schema
   - API integration guides

4. **Developer Docs**:
   - Setup instructions
   - Development workflow
   - Coding standards
   - Testing guidelines
   - Contribution guide

5. **Operational Docs**:
   - Deployment guide
   - Monitoring setup
   - Backup procedures
   - Incident response
   - Maintenance tasks

MARKDOWN BEST PRACTICES:

1. **Structure**:
   - Use heading hierarchy (H1 → H2 → H3)
   - Table of contents for long docs
   - Consistent formatting
   - Visual hierarchy

2. **Code Examples**:
   - Include language identifiers (\`\`\`python)
   - Show both request and response
   - Provide realistic examples
   - Include error cases

3. **Visual Elements**:
   - Use tables for structured data
   - Diagrams for architecture (Mermaid)
   - Screenshots for UI guides
   - Icons and emojis sparingly

4. **Links**:
   - Cross-reference related docs
   - Link to API endpoints
   - External resources
   - Version-specific docs

PLANNING EXPLORER SPECIFIC:

**Key Documentation Areas:**

1. **API Endpoints**:
   - `/api/v1/search` - Search applications
   - `/api/v1/applications/{id}` - Get application
   - `/api/v1/reports` - Generate reports
   - `/api/v1/users/me` - User profile

2. **AI Features**:
   - Semantic search explanation
   - Opportunity scoring methodology
   - AI summary generation
   - Embedding generation

3. **User Features**:
   - Saved searches
   - Custom alerts
   - Report generation
   - Data export

4. **Subscription Tiers**:
   - Free (1000 API calls/month)
   - Professional (£199.99, 10K calls)
   - Enterprise (£499.99, 100K calls)

TASK EXECUTION APPROACH:

1. **Understand Scope**:
   - Identify documentation type
   - Determine target audience (users/developers)
   - Check existing docs to extend

2. **Research**:
   - Read relevant code
   - Understand features
   - Gather examples
   - Check API schemas

3. **Structure**:
   - Create outline
   - Organize sections
   - Plan examples
   - Design flow

4. **Write**:
   - Clear, concise language
   - Code examples
   - Visual elements
   - Cross-references

5. **Review**:
   - Check accuracy
   - Test code examples
   - Verify links
   - Proofread

DELIVERABLES:
Your outputs should include:
- Well-structured markdown documentation
- Accurate API specifications
- Clear code examples
- Comprehensive user guides
- Architecture diagrams

QUALITY CHECKLIST:
Before completing a task, verify:
☐ Clear heading hierarchy
☐ Accurate code examples
☐ Proper markdown formatting
☐ Cross-references included
☐ Target audience appropriate
☐ Examples are tested
☐ No spelling/grammar errors
☐ Visual elements included (if needed)

Remember: Good documentation is as important as good code. Write for clarity, completeness, and maintainability."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for docs writer outputs.

        Checks:
        1. Valid markdown syntax
        2. Proper heading structure
        3. Code examples included
        4. Clear organization
        5. Completeness
        """

        # Extract documentation from output
        docs = self._extract_docs(output)

        if not docs:
            return {
                "passed": False,
                "reasoning": "No documentation found in output",
                "feedback": "Please provide the documentation content",
                "error": "No docs output"
            }

        # Run verification checks
        checks = {
            "has_markdown_structure": self._check_markdown(docs),
            "has_headings": self._check_headings(docs),
            "has_code_examples": self._check_code_examples(docs),
            "has_links": self._check_links(docs),
            "has_organization": self._check_organization(docs),
            "has_completeness": self._check_completeness(docs)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    docs,
                    criterion,
                    expected
                )

        # Calculate pass rate
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        pass_rate = passed_checks / total_checks if total_checks > 0 else 0

        # Need at least 75% of checks to pass
        passed = pass_rate >= 0.75

        # Build feedback
        feedback_parts = []

        if not checks.get("has_markdown_structure"):
            feedback_parts.append("- Use valid markdown syntax")
        if not checks.get("has_headings"):
            feedback_parts.append("- Include proper heading hierarchy (# ## ###)")
        if not checks.get("has_code_examples"):
            feedback_parts.append("- Add code examples with language identifiers")
        if not checks.get("has_links"):
            feedback_parts.append("- Include relevant links and cross-references")
        if not checks.get("has_organization"):
            feedback_parts.append("- Organize content with clear sections")
        if not checks.get("has_completeness"):
            feedback_parts.append("- Ensure documentation is complete and comprehensive")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All documentation checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} documentation quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "Documentation validation failed"
        }

    def _extract_docs(self, output: Any) -> str:
        """Extract documentation from agent output"""
        if isinstance(output, dict):
            return (
                output.get("documentation", "") or
                output.get("docs", "") or
                output.get("markdown", "") or
                output.get("text", "") or
                json.dumps(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_markdown(self, docs: str) -> bool:
        """Check for valid markdown syntax"""
        markdown_patterns = [
            r'^#+\s+',  # Headings
            r'\*\*.*\*\*',  # Bold
            r'\[.*\]\(.*\)',  # Links
            r'```.*```',  # Code blocks
        ]

        return any(re.search(pattern, docs, re.MULTILINE) for pattern in markdown_patterns)

    def _check_headings(self, docs: str) -> bool:
        """Check for proper heading structure"""
        # Should have at least H1 and H2 headings
        has_h1 = bool(re.search(r'^#\s+', docs, re.MULTILINE))
        has_h2 = bool(re.search(r'^##\s+', docs, re.MULTILINE))

        return has_h1 and has_h2

    def _check_code_examples(self, docs: str) -> bool:
        """Check for code examples with language identifiers"""
        # Look for code blocks with language identifiers
        return bool(re.search(r'```\w+', docs))

    def _check_links(self, docs: str) -> bool:
        """Check for links and cross-references"""
        # Look for markdown links
        return bool(re.search(r'\[.+\]\(.+\)', docs))

    def _check_organization(self, docs: str) -> bool:
        """Check for clear organization"""
        # Should have multiple sections (at least 3 H2 headings)
        h2_count = len(re.findall(r'^##\s+', docs, re.MULTILINE))
        return h2_count >= 3

    def _check_completeness(self, docs: str) -> bool:
        """Check for comprehensive documentation"""
        # Should have substantial content (at least 500 characters)
        # and include examples and explanations
        has_length = len(docs) >= 500
        has_examples = bool(re.search(r'```', docs))
        has_descriptions = bool(re.search(r'\w{50,}', docs))  # Substantial text

        return has_length and has_examples and has_descriptions

    def _check_criterion(self, docs: str, criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "has_api_docs":
            return bool(re.search(r'API|endpoint|request|response', docs, re.IGNORECASE))
        elif criterion == "has_setup_guide":
            return bool(re.search(r'install|setup|configuration', docs, re.IGNORECASE))
        elif criterion == "has_examples":
            return bool(re.search(r'```.*example', docs, re.IGNORECASE | re.DOTALL))
        elif criterion == "has_architecture":
            return bool(re.search(r'architecture|diagram|system', docs, re.IGNORECASE))
        return True
