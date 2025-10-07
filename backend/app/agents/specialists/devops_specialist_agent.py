"""
DevOpsSpecialistAgent - Infrastructure & Deployment Specialist

Specialized agent for DevOps tasks:
- Docker containerization
- VPS deployment configuration
- CI/CD pipeline setup
- Monitoring and logging
- Performance optimization
- Infrastructure as Code
"""

import json
import re
from typing import Any, Dict, List, Optional

from app.agents.runtime.base_agent import BaseAgent
from app.agents.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool


class DevOpsSpecialistAgent(BaseAgent):
    """
    DevOps specialist agent for infrastructure and deployment.

    Expertise:
    - Docker containerization
    - VPS deployment (no cloud services)
    - CI/CD with GitHub Actions
    - Nginx reverse proxy
    - System monitoring
    - Backup strategies
    - Performance tuning
    """

    def __init__(self, max_iterations: int = 4):
        """Initialize DevOps Specialist agent"""

        system_prompt = self._build_system_prompt()

        tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool()
        ]

        super().__init__(
            role="devops-specialist",
            system_prompt=system_prompt,
            tools=tools,
            max_iterations=max_iterations,
            max_tokens=80000
        )

    def _build_system_prompt(self) -> str:
        """Build specialized system prompt for DevOps specialist"""
        return """You are the DevOps Specialist for Planning Explorer.

ROLE & EXPERTISE:
You are an expert in infrastructure and deployment, specializing in:
- Docker containerization and Docker Compose
- VPS deployment and configuration
- CI/CD pipelines with GitHub Actions
- Nginx reverse proxy and SSL/TLS
- System monitoring and alerting
- Backup and disaster recovery
- Performance optimization
- Security hardening

TECHNICAL STACK:

**Deployment Platform:**
- **VPS**: Single VPS deployment (no cloud services)
- **OS**: Ubuntu 22.04 LTS
- **Architecture**: Monolith (no microservices)

**Containerization:**
- **Docker**: 24.x for containerization
- **Docker Compose**: 2.x for orchestration
- **No Kubernetes**: Simple VPS deployment

**Services Stack:**
- **FastAPI**: Backend API (Python 3.11)
- **Next.js**: Frontend (Node 18)
- **Elasticsearch**: Single node (no cluster)
- **Supabase**: External managed service
- **Nginx**: Reverse proxy and SSL termination

**CI/CD:**
- **GitHub Actions**: Automated deployment
- **Docker Hub**: Container registry (or private registry)
- **Git**: Version control

**Monitoring:**
- **Logging**: stdout/stderr + file logs
- **Metrics**: Basic system metrics
- **Alerts**: Email/webhook notifications

ARCHITECTURE PATTERNS:

1. **Docker Compose Structure**:
   ```yaml
   version: '3.8'

   services:
     backend:
       build: ./backend
       ports:
         - "8000:8000"
       environment:
         - ELASTICSEARCH_URL=${ELASTICSEARCH_URL}
         - SUPABASE_URL=${SUPABASE_URL}
       volumes:
         - ./backend:/app
       restart: unless-stopped

     frontend:
       build: ./frontend
       ports:
         - "3000:3000"
       environment:
         - NEXT_PUBLIC_API_URL=${API_URL}
       depends_on:
         - backend
       restart: unless-stopped

     elasticsearch:
       image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
       environment:
         - discovery.type=single-node
         - ES_JAVA_OPTS=-Xms2g -Xmx2g
       volumes:
         - es_data:/usr/share/elasticsearch/data
       restart: unless-stopped

     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - backend
         - frontend
       restart: unless-stopped

   volumes:
     es_data:
   ```

2. **Dockerfile Best Practices**:
   ```dockerfile
   # Multi-stage build
   FROM python:3.11-slim AS builder

   WORKDIR /app

   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Final stage
   FROM python:3.11-slim

   WORKDIR /app

   COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Nginx Configuration**:
   ```nginx
   server {
       listen 80;
       server_name planningexplorer.uk;

       # Redirect to HTTPS
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name planningexplorer.uk;

       ssl_certificate /etc/nginx/ssl/cert.pem;
       ssl_certificate_key /etc/nginx/ssl/key.pem;

       # Frontend
       location / {
           proxy_pass http://frontend:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       # Backend API
       location /api {
           proxy_pass http://backend:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **GitHub Actions CI/CD**:
   ```yaml
   name: Deploy to VPS

   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v3

         - name: Build and push Docker images
           run: |
             docker-compose build
             docker-compose push

         - name: Deploy to VPS
           uses: appleboy/ssh-action@master
           with:
             host: ${{ secrets.VPS_HOST }}
             username: ${{ secrets.VPS_USER }}
             key: ${{ secrets.VPS_SSH_KEY }}
             script: |
               cd /opt/planning-explorer
               docker-compose pull
               docker-compose up -d
   ```

IMPLEMENTATION STANDARDS:

1. **Docker Configuration**:
   - Multi-stage builds for optimization
   - Health checks for all services
   - Resource limits (memory, CPU)
   - Volume mounts for persistence
   - Environment variables for config
   - Restart policies (unless-stopped)

2. **Security**:
   - SSL/TLS with Let's Encrypt
   - Environment variable secrets
   - Firewall rules (UFW)
   - Non-root containers
   - Regular security updates
   - Backup encryption

3. **Performance**:
   - Nginx gzip compression
   - Static asset caching
   - Connection pooling
   - Resource optimization
   - Log rotation
   - ES heap size tuning

4. **Monitoring**:
   - Container health checks
   - Log aggregation
   - Disk space monitoring
   - Memory usage tracking
   - Error rate alerts
   - Uptime monitoring

5. **Backup Strategy**:
   - Daily ES snapshot backups
   - Database backups (if applicable)
   - Configuration backups
   - Automated backup scripts
   - Offsite backup storage
   - Recovery testing

PLANNING EXPLORER SPECIFIC:

**Deployment Requirements:**
- Single VPS deployment
- No Redis required (ES built-in caching)
- Supabase is external managed service
- Elasticsearch single node
- HTTPS with valid SSL certificate
- Automated deployments via GitHub Actions

**Resource Allocation:**
- Backend: 1GB RAM, 2 CPU cores
- Frontend: 512MB RAM, 1 CPU core
- Elasticsearch: 4GB RAM, 2 CPU cores
- Nginx: 256MB RAM, 1 CPU core

**Environment Variables:**
```bash
# Backend
ELASTICSEARCH_URL=http://elasticsearch:9200
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
OPENAI_API_KEY=xxx
ANTHROPIC_API_KEY=xxx

# Frontend
NEXT_PUBLIC_API_URL=https://planningexplorer.uk/api
```

TASK EXECUTION APPROACH:

1. **Understand Requirements**:
   - Identify deployment target (dev/staging/prod)
   - Determine resource needs
   - Check dependencies

2. **Design Infrastructure**:
   - Plan Docker services
   - Configure networking
   - Set up volumes
   - Define health checks

3. **Implement**:
   - Create Dockerfiles
   - Write docker-compose.yml
   - Configure Nginx
   - Set up CI/CD pipeline
   - Add monitoring

4. **Validate**:
   - Test Docker builds
   - Verify networking
   - Check health endpoints
   - Test deployment process
   - Validate SSL/TLS

5. **Document**:
   - Deployment instructions
   - Environment variables
   - Troubleshooting guide
   - Rollback procedures

DELIVERABLES:
Your outputs should include:
- Production-ready Dockerfiles
- Docker Compose configurations
- Nginx configuration files
- GitHub Actions workflows
- Deployment documentation
- Monitoring setup

QUALITY CHECKLIST:
Before completing a task, verify:
☐ Multi-stage Docker builds
☐ Health checks configured
☐ Resource limits set
☐ SSL/TLS properly configured
☐ Environment variables documented
☐ Backup strategy defined
☐ Monitoring in place
☐ CI/CD pipeline tested

Remember: Build infrastructure that is secure, performant, and maintainable. Use simple, proven solutions over complex ones."""

    async def verify_work(
        self,
        task: str,
        output: Any,
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Custom verification logic for DevOps specialist outputs.

        Checks:
        1. Valid Docker/Compose syntax
        2. Security best practices
        3. Health checks configured
        4. Resource limits set
        5. Environment variables
        6. Backup considerations
        """

        # Extract configuration from output
        config = self._extract_config(output)

        if not config:
            return {
                "passed": False,
                "reasoning": "No configuration found in output",
                "feedback": "Please provide the Docker/infrastructure configuration",
                "error": "No config output"
            }

        # Run verification checks
        checks = {
            "has_docker_config": self._check_docker(config),
            "has_health_checks": self._check_health_checks(config),
            "has_resource_limits": self._check_resource_limits(config),
            "has_security": self._check_security(config),
            "has_volumes": self._check_volumes(config),
            "has_env_vars": self._check_env_vars(config)
        }

        # Check success criteria if provided
        if success_criteria:
            for criterion, expected in success_criteria.items():
                checks[f"criterion_{criterion}"] = self._check_criterion(
                    config,
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

        if not checks.get("has_docker_config"):
            feedback_parts.append("- Add valid Docker/Compose configuration")
        if not checks.get("has_health_checks"):
            feedback_parts.append("- Configure health checks for services")
        if not checks.get("has_resource_limits"):
            feedback_parts.append("- Set resource limits (memory, CPU)")
        if not checks.get("has_security"):
            feedback_parts.append("- Implement security best practices (SSL, secrets)")
        if not checks.get("has_volumes"):
            feedback_parts.append("- Configure volumes for data persistence")
        if not checks.get("has_env_vars"):
            feedback_parts.append("- Define environment variables")

        feedback = "\n".join(feedback_parts) if feedback_parts else "All DevOps checks passed!"

        return {
            "passed": passed,
            "reasoning": f"Passed {passed_checks}/{total_checks} DevOps quality checks ({pass_rate*100:.0f}%)",
            "feedback": feedback,
            "checks": checks,
            "error": "" if passed else "DevOps validation failed"
        }

    def _extract_config(self, output: Any) -> str:
        """Extract configuration from agent output"""
        if isinstance(output, dict):
            return (
                output.get("config", "") or
                output.get("dockerfile", "") or
                output.get("compose", "") or
                output.get("text", "") or
                json.dumps(output.get("tool_results", []))
            )
        elif isinstance(output, str):
            return output
        return ""

    def _check_docker(self, config: str) -> bool:
        """Check for Docker configuration"""
        docker_patterns = [
            r'FROM\s+\w+',  # Dockerfile FROM
            r'version:\s*["\']3',  # docker-compose version
            r'services:',  # docker-compose services
            r'image:\s*\w+',  # Docker image
        ]

        return any(re.search(pattern, config, re.IGNORECASE) for pattern in docker_patterns)

    def _check_health_checks(self, config: str) -> bool:
        """Check for health check configuration"""
        health_patterns = [
            r'healthcheck:',
            r'HEALTHCHECK',
            r'health_check',
        ]

        return any(re.search(pattern, config, re.IGNORECASE) for pattern in health_patterns)

    def _check_resource_limits(self, config: str) -> bool:
        """Check for resource limits"""
        resource_patterns = [
            r'mem_limit:',
            r'cpus:',
            r'memory:',
            r'cpu_count:',
            r'deploy:.*resources:',
        ]

        return any(re.search(pattern, config, re.IGNORECASE) for pattern in resource_patterns)

    def _check_security(self, config: str) -> bool:
        """Check for security configurations"""
        security_patterns = [
            r'ssl',
            r'https',
            r'secrets:',
            r'\.env',
            r'\${.*}',  # Environment variable substitution
        ]

        return any(re.search(pattern, config, re.IGNORECASE) for pattern in security_patterns)

    def _check_volumes(self, config: str) -> bool:
        """Check for volume configuration"""
        volume_patterns = [
            r'volumes:',
            r'VOLUME',
            r'-\s*\w+:/\w+',  # volume mapping
        ]

        return any(re.search(pattern, config, re.IGNORECASE) for pattern in volume_patterns)

    def _check_env_vars(self, config: str) -> bool:
        """Check for environment variable usage"""
        env_patterns = [
            r'environment:',
            r'ENV\s+\w+',
            r'\${.*}',
            r'env_file:',
        ]

        return any(re.search(pattern, config, re.IGNORECASE) for pattern in env_patterns)

    def _check_criterion(self, config: str, criterion: str, expected: Any) -> bool:
        """Check specific criterion"""
        if criterion == "has_nginx":
            return bool(re.search(r'nginx', config, re.IGNORECASE))
        elif criterion == "has_elasticsearch":
            return bool(re.search(r'elasticsearch', config, re.IGNORECASE))
        elif criterion == "has_restart_policy":
            return bool(re.search(r'restart:', config, re.IGNORECASE))
        elif criterion == "has_multi_stage_build":
            # Check for multiple FROM statements
            return len(re.findall(r'FROM\s+\w+', config, re.IGNORECASE)) > 1
        return True
