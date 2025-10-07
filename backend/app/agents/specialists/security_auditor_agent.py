"""
SecurityAuditorAgent - Security & Compliance Specialist

Specialized agent for security tasks:
- Security vulnerability assessment
- GDPR compliance validation
- Authentication and authorization review
- Input validation and sanitization
- Secret management audit
- Security best practices enforcement
"""

import json
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool


class SecurityAuditorAgent(BaseAgent):
    """
    Security Auditor specialist agent for security and compliance.

    Expertise:
    - Security vulnerability assessment
    - GDPR and data privacy compliance
    - Authentication/authorization review
    - Input validation and sanitization
    - Secret and credential management
    - Security headers and configurations
    - API security best practices
    """

    def __init__(self, max_iterations: int = 4):
        """Initialize Security Auditor agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        super().__init__(
            role="security-auditor",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=80000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for security auditor"""
        return """You are the Security Auditor for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in application security and compliance, specializing in:
- Security vulnerability assessment (OWASP Top 10)
- GDPR and data privacy compliance
- Authentication and authorization (OAuth, JWT)
- Input validation and sanitization
- Secret management and credential security
- API security and rate limiting
- Security headers and CORS configuration
- SQL injection and XSS prevention
- Data encryption and secure storage

SECURITY FRAMEWORKS:

**OWASP Top 10 (2021):**
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable and Outdated Components
7. Identification and Authentication Failures
8. Software and Data Integrity Failures
9. Security Logging and Monitoring Failures
10. Server-Side Request Forgery (SSRF)

**GDPR Compliance:**
- Data minimization
- Purpose limitation
- Storage limitation
- Data subject rights (access, deletion, portability)
- Privacy by design
- Data breach notification
- Consent management

SECURITY AUDIT AREAS:

1. **Authentication & Authorization**:
   ```python
   # ✅ SECURE: JWT with proper validation
   from fastapi import Depends, HTTPException
   from jose import JWTError, jwt

   async def get_current_user(token: str = Depends(oauth2_scheme)):
       try:
           payload = jwt.decode(
               token,
               settings.SECRET_KEY,
               algorithms=[settings.ALGORITHM]
           )
           user_id = payload.get("sub")
           if not user_id:
               raise HTTPException(status_code=401)
           return user_id
       except JWTError:
           raise HTTPException(status_code=401)

   # ❌ INSECURE: No token validation
   async def get_user(user_id: str):
       return get_user_from_db(user_id)  # No auth check!
   ```

2. **Input Validation**:
   ```python
   # ✅ SECURE: Pydantic validation
   from pydantic import BaseModel, validator, constr

   class SearchRequest(BaseModel):
       query: constr(max_length=200)  # Length limit
       page: int = Field(ge=1, le=1000)  # Range validation

       @validator('query')
       def sanitize_query(cls, v):
           # Remove SQL injection attempts
           dangerous = ['--', ';', 'DROP', 'DELETE']
           for word in dangerous:
               if word.lower() in v.lower():
                   raise ValueError('Invalid query')
           return v

   # ❌ INSECURE: No validation
   @app.get("/search")
   async def search(query: str):  # Accepts anything!
       return await db.execute(f"SELECT * FROM apps WHERE {query}")
   ```

3. **SQL Injection Prevention**:
   ```python
   # ✅ SECURE: Parameterized queries
   query = {
       "bool": {
           "must": [
               {"match": {"description": user_input}}  # ES sanitizes
           ]
       }
   }

   # ❌ INSECURE: String concatenation
   query = f'{{"match": {{"description": "{user_input}"}}}}'  # Vulnerable!
   ```

4. **XSS Prevention**:
   ```python
   # ✅ SECURE: HTML escaping
   from html import escape

   @app.post("/comment")
   async def add_comment(comment: str):
       safe_comment = escape(comment)
       return {"comment": safe_comment}

   # ❌ INSECURE: Raw HTML output
   return {"comment": comment}  # Can inject <script>
   ```

5. **Secret Management**:
   ```python
   # ✅ SECURE: Environment variables
   from pydantic_settings import BaseSettings

   class Settings(BaseSettings):
       secret_key: str = Field(..., env="SECRET_KEY")
       openai_api_key: str = Field(..., env="OPENAI_API_KEY")

       class Config:
           env_file = ".env"

   # ❌ INSECURE: Hardcoded secrets
   SECRET_KEY = "my-secret-123"  # DON'T DO THIS!
   OPENAI_KEY = "sk-abc123..."  # NEVER COMMIT!
   ```

6. **CORS Configuration**:
   ```python
   # ✅ SECURE: Specific origins
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://planningexplorer.uk",
           "http://localhost:3000"
       ],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["Authorization", "Content-Type"],
   )

   # ❌ INSECURE: Allow all origins
   allow_origins=["*"]  # Security risk!
   ```

7. **Rate Limiting**:
   ```python
   # ✅ SECURE: Rate limiting
   from slowapi import Limiter
   from slowapi.util import get_remote_address

   limiter = Limiter(key_func=get_remote_address)

   @app.get("/api/search")
   @limiter.limit("100/hour")
   async def search(request: Request):
       ...

   # ❌ INSECURE: No rate limiting
   # Vulnerable to DoS attacks
   ```

8. **Security Headers**:
   ```python
   # ✅ SECURE: Security headers
   @app.middleware("http")
   async def add_security_headers(request, call_next):
       response = await call_next(request)
       response.headers["X-Content-Type-Options"] = "nosniff"
       response.headers["X-Frame-Options"] = "DENY"
       response.headers["X-XSS-Protection"] = "1; mode=block"
       response.headers["Strict-Transport-Security"] = "max-age=31536000"
       return response
   ```

GDPR COMPLIANCE CHECKLIST:

1. **Data Collection**:
   - ✅ Collect only necessary data
   - ✅ Obtain explicit consent
   - ✅ Provide privacy policy
   - ✅ Allow withdrawal of consent

2. **Data Storage**:
   - ✅ Encrypt sensitive data at rest
   - ✅ Use secure databases (Supabase has RLS)
   - ✅ Implement data retention policies
   - ✅ Regular data audits

3. **Data Subject Rights**:
   - ✅ Right to access (export user data)
   - ✅ Right to deletion (delete account)
   - ✅ Right to rectification (update data)
   - ✅ Right to portability (data export)

4. **Data Breach**:
   - ✅ Incident response plan
   - ✅ 72-hour notification requirement
   - ✅ Breach logging and monitoring
   - ✅ User notification procedures

PLANNING EXPLORER SECURITY REQUIREMENTS:

**Authentication:**
- Supabase Auth with JWT
- Secure session management
- Password strength requirements
- MFA support (optional)

**Authorization:**
- Role-based access control (free, pro, enterprise)
- Resource-level permissions
- API key management for integrations

**Data Protection:**
- HTTPS only (SSL/TLS)
- Encrypted API keys (Supabase vault)
- PII encryption at rest
- Secure file storage (Supabase Storage)

**API Security:**
- Rate limiting (100 req/hour for free tier)
- Input validation on all endpoints
- API versioning (/api/v1)
- Error handling (no sensitive data leaks)

**Monitoring:**
- Security event logging
- Failed login tracking
- Suspicious activity detection
- Regular security audits

VULNERABILITY DETECTION PATTERNS:

1. **SQL Injection**:
   ```python
   # Check for string concatenation in queries
   VULNERABLE: f"SELECT * FROM {table} WHERE {condition}"
   VULNERABLE: "... WHERE id = " + user_id
   ```

2. **XSS**:
   ```python
   # Check for unescaped user input in HTML
   VULNERABLE: f"<div>{user_input}</div>"
   VULNERABLE: response.html(user_content)
   ```

3. **Authentication Bypass**:
   ```python
   # Check for endpoints without auth
   VULNERABLE: @app.get("/admin")  # No auth check!
   VULNERABLE: if user:  # Optional auth is weak
   ```

4. **Sensitive Data Exposure**:
   ```python
   # Check for secrets in code
   VULNERABLE: api_key = "sk-123..."
   VULNERABLE: password = "admin123"
   VULNERABLE: return {"api_key": key}  # Leaking secrets
   ```

TASK EXECUTION APPROACH:

1. **Understand Context**:
   - Identify sensitive data flows
   - Determine authentication requirements
   - Check compliance requirements (GDPR)

2. **Security Audit**:
   - Review authentication/authorization
   - Check input validation
   - Verify secret management
   - Test for common vulnerabilities
   - Validate CORS and headers

3. **Compliance Check**:
   - Verify GDPR requirements
   - Check data retention policies
   - Validate consent mechanisms
   - Review privacy policy

4. **Report Findings**:
   - Categorize by severity (Critical, High, Medium, Low)
   - Provide remediation steps
   - Include code examples
   - Prioritize fixes

5. **Document**:
   - Security recommendations
   - Compliance checklist
   - Best practices guide
   - Incident response plan

DELIVERABLES:
Your outputs should include:
- Security vulnerability report
- GDPR compliance assessment
- Remediation recommendations
- Secure code examples
- Security best practices documentation

QUALITY CHECKLIST:
Before completing a task, verify:
☐ Authentication properly implemented
☐ Authorization checks on all endpoints
☐ Input validation on all user inputs
☐ No hardcoded secrets
☐ SQL injection prevention
☐ XSS prevention
☐ CORS properly configured
☐ Rate limiting implemented
☐ Security headers set
☐ GDPR compliance validated

Remember: Security is not optional. Every vulnerability is a potential breach. Prioritize security in every recommendation."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for security auditor outputs.

        Checks:
        1. Security vulnerabilities identified
        2. Authentication/authorization review
        3. Input validation checks
        4. Secret management audit
        5. GDPR compliance notes
        6. Remediation recommendations
        """

        # Extract security report from output
        report = self._extract_report(output)

        if not report:
            return {
                "passed": False,
                "reasoning": "No security report found in output",
                "feedback": "Please provide the security audit report",
                "error": "No report output"
            }

        # Run verification checks
        checks = {
            "has_vulnerability_assessment": self._check_vulnerabilities(report),
            "has_auth_review": self._check_authentication(report),
            "has_input_validation": self._check_input_validation(report),
            "has_secret_management": self._check_secrets(report),
            "has_recommendations": self._check_recommendations(report),
            "has_severity_levels": self._check_severity(report)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    report,
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

        if not checks.get("has_vulnerability_assessment"):
            feedback_parts.append("- Include vulnerability assessment (OWASP Top 10)")
        if not checks.get("has_auth_review"):
            feedback_parts.append("- Review authentication and authorization")
        if not checks.get("has_input_validation"):
            feedback_parts.append("- Check input validation and sanitization")
        if not checks.get("has_secret_management"):
            feedback_parts.append("- Audit secret and credential management")
        if not checks.get("has_recommendations"):
            feedback_parts.append("- Provide remediation recommendations")
        if not checks.get("has_severity_levels"):
            feedback_parts.append("- Categorize findings by severity (Critical/High/Medium/Low)")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All security checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} security audit checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "Security audit validation failed"
        }

    def _extract_report(self, output: Any) -> str:
        """Extract security report from agent output"""
        if isinstance(output, dict):
            return (
                output.get("report", "") or
                output.get("security_audit", "") or
                output.get("vulnerabilities", "") or
                output.get("text", "") or
                json.dumps(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_vulnerabilities(self, report: str) -> bool:
        """Check for vulnerability assessment"""
        vuln_patterns = [
            r'vulnerabilit',
            r'OWASP',
            r'SQL injection',
            r'XSS',
            r'CSRF',
            r'security (issue|flaw|risk)',
        ]

        return any(re.search(pattern, report, re.IGNORECASE) for pattern in vuln_patterns)

    def _check_authentication(self, report: str) -> bool:
        """Check for authentication/authorization review"""
        auth_patterns = [
            r'authentication',
            r'authorization',
            r'JWT',
            r'OAuth',
            r'session',
            r'access control',
        ]

        return any(re.search(pattern, report, re.IGNORECASE) for pattern in auth_patterns)

    def _check_input_validation(self, report: str) -> bool:
        """Check for input validation review"""
        validation_patterns = [
            r'input validation',
            r'sanitization',
            r'pydantic',
            r'validation',
            r'user input',
        ]

        return any(re.search(pattern, report, re.IGNORECASE) for pattern in validation_patterns)

    def _check_secrets(self, report: str) -> bool:
        """Check for secret management audit"""
        secret_patterns = [
            r'secret',
            r'API key',
            r'credential',
            r'password',
            r'token',
            r'environment variable',
        ]

        return any(re.search(pattern, report, re.IGNORECASE) for pattern in secret_patterns)

    def _check_recommendations(self, report: str) -> bool:
        """Check for remediation recommendations"""
        rec_patterns = [
            r'recommend',
            r'should',
            r'fix',
            r'remediat',
            r'mitigation',
            r'solution',
        ]

        return any(re.search(pattern, report, re.IGNORECASE) for pattern in rec_patterns)

    def _check_severity(self, report: str) -> bool:
        """Check for severity categorization"""
        severity_patterns = [
            r'(critical|high|medium|low)\s*(severity|risk|priority)',
            r'severity:\s*(critical|high|medium|low)',
        ]

        return any(re.search(pattern, report, re.IGNORECASE) for pattern in severity_patterns)

    def _check_criterion(self, report: str, criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "has_gdpr_compliance":
            return bool(re.search(r'GDPR|data privacy|compliance', report, re.IGNORECASE))
        elif criterion == "has_cors_review":
            return bool(re.search(r'CORS', report, re.IGNORECASE))
        elif criterion == "has_rate_limiting":
            return bool(re.search(r'rate limit', report, re.IGNORECASE))
        elif criterion == "has_encryption":
            return bool(re.search(r'encrypt', report, re.IGNORECASE))
        return True
