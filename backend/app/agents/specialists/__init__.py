"""
Specialist Agents Module

Autonomous specialist agents converted from .claude/specialists/*.md roles:

- BackendEngineerAgent: FastAPI development, Supabase integration ✅
- ElasticsearchArchitectAgent: Schema design, indexing strategies ✅
- AIEngineerAgent: LLM integration, opportunity scoring ✅
- FrontendSpecialistAgent: Next.js, React, UI components ✅
- DevOpsSpecialistAgent: Docker, deployment, infrastructure ✅
- QAEngineerAgent: Testing, validation, performance benchmarks ✅
- SecurityAuditorAgent: Security review, GDPR compliance ✅
- DocsWriterAgent: Documentation, API specs ✅
"""

from .backend_engineer_agent import BackendEngineerAgent
from .elasticsearch_architect_agent import ElasticsearchArchitectAgent
from .ai_engineer_agent import AIEngineerAgent
from .frontend_specialist_agent import FrontendSpecialistAgent
from .devops_specialist_agent import DevOpsSpecialistAgent
from .qa_engineer_agent import QAEngineerAgent
from .security_auditor_agent import SecurityAuditorAgent
from .docs_writer_agent import DocsWriterAgent

__all__ = [
    "BackendEngineerAgent",
    "ElasticsearchArchitectAgent",
    "AIEngineerAgent",
    "FrontendSpecialistAgent",
    "DevOpsSpecialistAgent",
    "QAEngineerAgent",
    "SecurityAuditorAgent",
    "DocsWriterAgent",
]
