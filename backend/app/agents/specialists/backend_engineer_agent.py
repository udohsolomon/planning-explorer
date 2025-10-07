"""
BackendEngineerAgent - FastAPI Development Specialist

Specialized agent for backend development tasks:
- FastAPI endpoint creation
- Supabase integration
- API design and implementation
- Data validation with Pydantic
- Background task processing
"""

import ast
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool, FileListTool
from app.agents.tools.supabase_tools import SupabaseCRUDTool, SupabaseAuthTool


class BackendEngineerAgent(BaseAgent):
    """
    Backend Engineer specialist agent.

    Expertise:
    - FastAPI application development
    - RESTful API design
    - Supabase authentication and database integration
    - Async/await patterns
    - Pydantic data validation
    - Background task processing
    - Error handling and logging
    """

    def __init__(self, max_iterations: int = 5):
        """Initialize Backend Engineer agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool(),
            FileListTool(),
            SupabaseCRUDTool(),
            SupabaseAuthTool()
        ]

        super().__init__(
            role="backend-engineer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=100000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for backend engineer"""
        return """You are the Backend Engineer specialist for Planning Explorer.

ROLE & EXPERTISE:
You are an expert FastAPI developer specializing in:
- RESTful API design and implementation
- Supabase authentication with JWT
- PostgreSQL database integration
- Async/await patterns for high performance
- Pydantic models for data validation
- Background task processing
- Comprehensive error handling
- API documentation (OpenAPI/Swagger)

TECHNICAL STACK:
- **Framework**: FastAPI 0.104+ with async/await
- **Database**: Supabase (PostgreSQL) via asyncpg
- **Auth**: Supabase Auth with JWT tokens
- **Validation**: Pydantic v2 for request/response models
- **Caching**: Redis for performance optimization
- **Testing**: pytest with async support

IMPLEMENTATION STANDARDS:

1. **Code Quality**:
   - Use async/await for all I/O operations
   - Type hints on all functions and parameters
   - Comprehensive docstrings (Google style)
   - Clean, readable, maintainable code
   - Follow PEP 8 style guidelines

2. **API Design**:
   - RESTful conventions (GET, POST, PUT, DELETE, PATCH)
   - Consistent response format: {"success": bool, "data": ..., "error": ...}
   - Proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
   - Pagination for list endpoints (limit/offset or cursor)
   - Filtering and sorting capabilities

3. **Security**:
   - JWT validation on protected routes
   - Input sanitization to prevent injection
   - Rate limiting per user tier
   - CORS configuration for frontend
   - Proper error messages (no sensitive data leakage)

4. **Error Handling**:
   - Try/except blocks for external calls
   - Custom exception classes for domain errors
   - Structured error responses
   - Proper logging (structlog/loguru)
   - Graceful degradation

5. **Data Validation**:
   - Pydantic models for request bodies
   - Query/Path parameter validation
   - Email, UUID, datetime validators
   - Custom validators for business logic
   - Clear validation error messages

6. **Performance**:
   - Database connection pooling
   - Query optimization (select only needed fields)
   - Caching for frequently accessed data
   - Background tasks for heavy processing
   - Async I/O throughout

7. **Testing**:
   - Unit tests for business logic
   - Integration tests for endpoints
   - Mock external dependencies
   - Test edge cases and error conditions

TASK EXECUTION APPROACH:

1. **Understand Requirements**:
   - Read task description carefully
   - Identify endpoints, models, and dependencies
   - Clarify success criteria

2. **Design API**:
   - Define Pydantic models (request/response)
   - Design endpoint structure (/api/v1/resource)
   - Plan database schema if needed
   - Consider authentication requirements

3. **Implement**:
   - Create Pydantic models first
   - Implement endpoint with proper decorators
   - Add validation and error handling
   - Integrate with Supabase if needed
   - Add comprehensive docstrings

4. **Validate**:
   - Check code quality (async, type hints, docs)
   - Verify error handling
   - Ensure security best practices
   - Test with example requests (mentally or with tests)

5. **Document**:
   - Clear endpoint documentation
   - Example requests/responses
   - Error codes and meanings

DELIVERABLES:
Your outputs should include:
- Well-structured Python code
- Pydantic models for validation
- FastAPI endpoints with proper decorators
- Error handling and logging
- Inline documentation
- Usage examples in docstrings

QUALITY CHECKLIST:
Before completing a task, verify:
☐ All functions use async/await
☐ Type hints on all parameters
☐ Pydantic models for data validation
☐ Try/except blocks for error handling
☐ Proper HTTP status codes
☐ Security (JWT validation if needed)
☐ Docstrings on all public functions
☐ Clean, readable code

Remember: Write production-ready code that is secure, performant, and maintainable."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for backend engineer outputs.

        Checks:
        1. Code quality (async, type hints, docstrings)
        2. FastAPI patterns (decorators, Pydantic models)
        3. Error handling
        4. Security considerations
        5. Success criteria met
        """

        # Extract code from output
        code = self._extract_code(output)

        if not code:
            return {
                "passed": False,
                "reasoning": "No code found in output",
                "feedback": "Please provide the implementation code",
                "error": "No code output"
            }

        # Run verification checks
        checks = {
            "has_async": self._check_async(code),
            "has_type_hints": self._check_type_hints(code),
            "has_error_handling": self._check_error_handling(code),
            "has_pydantic": self._check_pydantic_models(code),
            "has_fastapi_decorator": self._check_fastapi_decorator(code),
            "has_docstrings": self._check_docstrings(code)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    code,
                    criterion,
                    expected
                )

        # Calculate pass rate
        passed_checks = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        pass_rate = passed_checks / total_checks if total_checks > 0 else 0

        # Determine if passed (need at least 80% of checks)
        passed = pass_rate >= 0.8

        # Build feedback
        failed_checks = [k for k, v in checks.items() if not v]
        feedback_parts = []

        if not checks.get("has_async"):
            feedback_parts.append("- Use async/await for I/O operations")
        if not checks.get("has_type_hints"):
            feedback_parts.append("- Add type hints to function parameters")
        if not checks.get("has_error_handling"):
            feedback_parts.append("- Add try/except blocks for error handling")
        if not checks.get("has_pydantic"):
            feedback_parts.append("- Use Pydantic models for data validation")
        if not checks.get("has_fastapi_decorator"):
            feedback_parts.append("- Add FastAPI router decorators (@router.get, etc.)")
        if not checks.get("has_docstrings"):
            feedback_parts.append("- Add docstrings to functions and classes")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else f"Failed checks: {', '.join(failed_checks)}"
        }

    def _extract_code(self, output: Any) -> str:
        """Extract code from agent output"""
        if isinstance(output, dict):
            # Check for code in various fields
            return (
                output.get("code", "") or
                output.get("text", "") or
                str(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_async(self, code: str) -> bool:
        """Check if code uses async/await"""
        return "async def" in code or "await " in code

    def _check_type_hints(self, code: str) -> bool:
        """Check if code has type hints"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for type hints in parameters or return
                    if node.returns is not None:
                        return True
                    for arg in node.args.args:
                        if arg.annotation is not None:
                            return True
            return False
        except (SyntaxError, ValueError):
            return False

    def _check_error_handling(self, code: str) -> bool:
        """Check if code has error handling"""
        return "try:" in code and "except" in code

    def _check_pydantic_models(self, code: str) -> bool:
        """Check if code uses Pydantic models"""
        return "BaseModel" in code or "from pydantic" in code

    def _check_fastapi_decorator(self, code: str) -> bool:
        """Check if code has FastAPI decorators"""
        patterns = [
            r"@router\.(get|post|put|delete|patch)",
            r"@app\.(get|post|put|delete|patch)"
        ]
        return any(re.search(pattern, code) for pattern in patterns)

    def _check_docstrings(self, code: str) -> bool:
        """Check if code has docstrings"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        return True
            return False
        except (SyntaxError, ValueError):
            return False

    def _check_criterion(self, code: str, criterion: str, expected: Any) -> bool:
        """Check if code meets specific criterion"""
        # Custom criterion checking based on task requirements
        if criterion == "endpoint_exists":
            return self._check_fastapi_decorator(code)
        elif criterion == "has_validation":
            return "Query(" in code or "Path(" in code or "Body(" in code
        elif criterion == "has_auth":
            return "Depends(" in code or "get_current_user" in code
        return True  # Default to true for unknown criteria
