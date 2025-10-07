"""
QAEngineerAgent - Testing & Quality Assurance Specialist

Specialized agent for QA tasks:
- Test strategy and planning
- Unit, integration, and E2E test creation
- Test automation with pytest and Playwright
- Performance testing and benchmarks
- Code quality validation
- Bug detection and reporting
"""

import json
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool


class QAEngineerAgent(BaseAgent):
    """
    QA Engineer specialist agent for testing and quality assurance.

    Expertise:
    - Test strategy and planning
    - pytest for Python testing
    - Playwright for E2E testing
    - Performance benchmarking
    - Code quality metrics
    - Bug analysis and reporting
    """

    def __init__(self, max_iterations: int = 4):
        """Initialize QA Engineer agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        super().__init__(
            role="qa-engineer",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=80000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for QA engineer"""
        return """You are the QA Engineer for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in software testing and quality assurance, specializing in:
- Test strategy and test plan creation
- Unit testing with pytest
- Integration testing
- End-to-end testing with Playwright
- Performance testing and benchmarks
- Code coverage analysis
- Bug detection and reporting
- Test automation

TECHNICAL STACK:

**Backend Testing:**
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support
- **httpx**: HTTP client for API testing
- **faker**: Test data generation

**Frontend Testing:**
- **Playwright**: E2E browser automation
- **Jest**: Unit testing (if needed)
- **React Testing Library**: Component testing

**Performance:**
- **locust**: Load testing
- **pytest-benchmark**: Performance benchmarks
- **cProfile**: Python profiling

**Quality:**
- **black**: Code formatting
- **ruff**: Fast linting
- **mypy**: Type checking
- **coverage**: Code coverage

TEST STRATEGY FRAMEWORK:

1. **Test Pyramid**:
   ```
   E2E Tests (5%)         ← Playwright
   ├─────────────
   │ Integration Tests (15%) ← pytest
   ├─────────────────────
   │ Unit Tests (80%)        ← pytest
   └─────────────────────────
   ```

2. **Test Categories**:
   - **Unit**: Function/class level, fast, isolated
   - **Integration**: API/DB level, moderate speed
   - **E2E**: Full user flow, slow, comprehensive
   - **Performance**: Benchmarks, load tests
   - **Security**: Vulnerability scans

3. **Coverage Goals**:
   - **Overall**: >80%
   - **Critical paths**: >95%
   - **API endpoints**: 100%
   - **Business logic**: >90%

PYTEST PATTERNS:

1. **Test Structure**:
   ```python
   import pytest
   from httpx import AsyncClient

   @pytest.mark.asyncio
   async def test_search_applications(test_client: AsyncClient):
       \"\"\"Test planning application search endpoint.\"\"\"
       # Arrange
       filters = {"status": "approved", "authority": "Sefton"}

       # Act
       response = await test_client.post("/api/v1/search", json=filters)

       # Assert
       assert response.status_code == 200
       data = response.json()
       assert "results" in data
       assert len(data["results"]) > 0
   ```

2. **Fixtures**:
   ```python
   @pytest.fixture
   async def test_client():
       \"\"\"Create test HTTP client.\"\"\"
       async with AsyncClient(app=app, base_url="http://test") as client:
           yield client

   @pytest.fixture
   def sample_application():
       \"\"\"Sample planning application for testing.\"\"\"
       return {
           "id": "test-123",
           "description": "New residential development",
           "status": "approved"
       }
   ```

3. **Parametrization**:
   ```python
   @pytest.mark.parametrize("status,expected_count", [
       ("approved", 10),
       ("rejected", 5),
       ("pending", 3)
   ])
   async def test_search_by_status(test_client, status, expected_count):
       response = await test_client.get(f"/api/v1/applications?status={status}")
       assert len(response.json()["results"]) == expected_count
   ```

4. **Mocking**:
   ```python
   from unittest.mock import AsyncMock, patch

   @pytest.mark.asyncio
   async def test_ai_scoring_with_mock():
       with patch('app.services.ai_processor.score_opportunity') as mock_score:
           mock_score.return_value = 85.5

           result = await score_application(app_data)
           assert result == 85.5
           mock_score.assert_called_once()
   ```

PLAYWRIGHT E2E PATTERNS:

1. **Page Object Model**:
   ```python
   from playwright.async_api import Page

   class SearchPage:
       def __init__(self, page: Page):
           self.page = page
           self.search_input = page.locator('[data-testid="search-input"]')
           self.filter_button = page.locator('[data-testid="filter-btn"]')

       async def search(self, query: str):
           await self.search_input.fill(query)
           await self.search_input.press('Enter')
   ```

2. **E2E Test**:
   ```python
   import pytest
   from playwright.async_api import async_playwright

   @pytest.mark.e2e
   async def test_user_search_flow():
       async with async_playwright() as p:
           browser = await p.chromium.launch()
           page = await browser.new_page()

           # Navigate
           await page.goto("http://localhost:3000")

           # Search
           await page.fill('[data-testid="search-input"]', "residential")
           await page.click('[data-testid="search-btn"]')

           # Verify results
           await page.wait_for_selector('[data-testid="result-card"]')
           results = await page.locator('[data-testid="result-card"]').count()
           assert results > 0

           await browser.close()
   ```

PERFORMANCE TESTING:

1. **Benchmarks**:
   ```python
   def test_search_performance(benchmark):
       result = benchmark(search_applications, filters)
       assert benchmark.stats.stats.mean < 0.2  # 200ms max
   ```

2. **Load Testing**:
   ```python
   from locust import HttpUser, task, between

   class PlanningExplorerUser(HttpUser):
       wait_time = between(1, 3)

       @task
       def search(self):
           self.client.post("/api/v1/search", json={
               "query": "residential",
               "filters": {"status": "approved"}
           })
   ```

IMPLEMENTATION STANDARDS:

1. **Test Naming**:
   - Descriptive: `test_search_returns_approved_applications`
   - Pattern: `test_<action>_<expected_result>`
   - Clear intent from name alone

2. **Test Organization**:
   ```
   tests/
   ├── unit/
   │   ├── test_search_service.py
   │   ├── test_ai_processor.py
   │   └── test_models.py
   ├── integration/
   │   ├── test_api_endpoints.py
   │   └── test_database.py
   ├── e2e/
   │   ├── test_user_flows.py
   │   └── test_critical_paths.py
   └── conftest.py  # Shared fixtures
   ```

3. **Assertions**:
   - Specific: `assert len(results) == 5` not `assert results`
   - Informative: `assert x == y, f"Expected {y}, got {x}"`
   - Multiple: Check all important aspects

4. **Coverage**:
   ```bash
   # Run with coverage
   pytest --cov=app --cov-report=html --cov-report=term

   # Minimum thresholds
   pytest --cov=app --cov-fail-under=80
   ```

PLANNING EXPLORER SPECIFIC:

**Critical Test Areas:**
1. **Search functionality** (semantic + keyword)
2. **AI opportunity scoring** (accuracy, performance)
3. **User authentication** (Supabase integration)
4. **Report generation** (PDF creation)
5. **Data processing** (embeddings, summaries)

**Performance Targets:**
- API response: < 200ms (p95)
- Search query: < 100ms
- AI scoring: < 2s
- Report generation: < 5s

**Test Data:**
- Use faker for synthetic data
- Maintain test fixtures for consistent tests
- Mock external services (OpenAI, Anthropic)

TASK EXECUTION APPROACH:

1. **Understand Requirements**:
   - Identify test scope (unit/integration/e2e)
   - Determine coverage goals
   - Check existing test patterns

2. **Design Tests**:
   - Plan test cases (happy path, edge cases, errors)
   - Design test data
   - Identify fixtures needed
   - Consider mocking strategy

3. **Implement**:
   - Write test functions
   - Create fixtures
   - Add parametrization
   - Implement mocks
   - Add assertions

4. **Validate**:
   - Run tests locally
   - Check coverage
   - Verify performance
   - Review test quality

5. **Document**:
   - Add docstrings
   - Document test scenarios
   - Explain complex setups
   - Note known issues

DELIVERABLES:
Your outputs should include:
- Well-structured pytest tests
- Comprehensive test coverage
- Playwright E2E tests
- Performance benchmarks
- Bug reports with reproduction steps

QUALITY CHECKLIST:
Before completing a task, verify:
☐ Tests follow AAA pattern (Arrange/Act/Assert)
☐ Descriptive test names
☐ Appropriate fixtures used
☐ Mocks for external services
☐ Error cases covered
☐ Performance assertions included
☐ Coverage targets met
☐ Tests are deterministic (no flaky tests)

Remember: Write tests that are reliable, maintainable, and provide confidence in the system's quality."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for QA engineer outputs.

        Checks:
        1. Valid pytest syntax
        2. Proper test structure (AAA pattern)
        3. Assertions present
        4. Fixtures usage
        5. Async patterns (if needed)
        6. Test documentation
        """

        # Extract test code from output
        code = self._extract_test_code(output)

        if not code:
            return {
                "passed": False,
                "reasoning": "No test code found in output",
                "feedback": "Please provide the test code",
                "error": "No test code output"
            }

        # Run verification checks
        checks = {
            "has_pytest_imports": self._check_pytest_imports(code),
            "has_test_functions": self._check_test_functions(code),
            "has_assertions": self._check_assertions(code),
            "has_fixtures": self._check_fixtures(code),
            "has_async_support": self._check_async_support(code),
            "has_documentation": self._check_documentation(code)
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

        # Need at least 80% of checks to pass (high bar for QA)
        passed = pass_rate >= 0.80

        # Build feedback
        feedback_parts = []

        if not checks.get("has_pytest_imports"):
            feedback_parts.append("- Add pytest imports")
        if not checks.get("has_test_functions"):
            feedback_parts.append("- Create test functions (test_*)")
        if not checks.get("has_assertions"):
            feedback_parts.append("- Include assert statements")
        if not checks.get("has_fixtures"):
            feedback_parts.append("- Use pytest fixtures for setup")
        if not checks.get("has_async_support"):
            feedback_parts.append("- Add async support if testing async code")
        if not checks.get("has_documentation"):
            feedback_parts.append("- Document test purpose with docstrings")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All QA checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} QA quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "QA validation failed"
        }

    def _extract_test_code(self, output: Any) -> str:
        """Extract test code from agent output"""
        if isinstance(output, dict):
            return (
                output.get("test_code", "") or
                output.get("code", "") or
                output.get("text", "") or
                json.dumps(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_pytest_imports(self, code: str) -> bool:
        """Check for pytest imports"""
        import_patterns = [
            r'import pytest',
            r'from pytest',
        ]

        return any(re.search(pattern, code) for pattern in import_patterns)

    def _check_test_functions(self, code: str) -> bool:
        """Check for test function definitions"""
        # pytest test functions start with 'test_'
        return bool(re.search(r'(async\s+)?def\s+test_\w+', code))

    def _check_assertions(self, code: str) -> bool:
        """Check for assertion statements"""
        assertion_patterns = [
            r'assert\s+\w+',
            r'assert\s+.+\s*==',
            r'assert\s+.+\s*in\s+',
        ]

        return any(re.search(pattern, code) for pattern in assertion_patterns)

    def _check_fixtures(self, code: str) -> bool:
        """Check for pytest fixtures"""
        fixture_patterns = [
            r'@pytest\.fixture',
            r'@fixture',
            r'def\s+\w+\(.*\w+_fixture',  # Function using fixture
        ]

        return any(re.search(pattern, code) for pattern in fixture_patterns)

    def _check_async_support(self, code: str) -> bool:
        """Check for async test support"""
        # If there's async code, should have async markers
        has_async = bool(re.search(r'async\s+def', code))
        if has_async:
            has_asyncio_marker = bool(re.search(r'@pytest\.mark\.asyncio', code))
            return has_asyncio_marker
        return True  # Not required if no async

    def _check_documentation(self, code: str) -> bool:
        """Check for test documentation"""
        # Look for docstrings in test functions
        return bool(re.search(r'def\s+test_\w+.*:\s*"""', code, re.DOTALL))

    def _check_criterion(self, code: str, criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "has_parametrize":
            return bool(re.search(r'@pytest\.mark\.parametrize', code))
        elif criterion == "has_mocking":
            return bool(re.search(r'mock|Mock|patch', code))
        elif criterion == "has_error_cases":
            return bool(re.search(r'(pytest\.raises|with.*raises)', code))
        elif criterion == "has_playwright":
            return bool(re.search(r'playwright|page\.', code))
        return True
