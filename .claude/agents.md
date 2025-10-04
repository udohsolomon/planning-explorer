# 🧠 Planning Explorer AI Agents - Central Configuration
*Version: 1.0.0 | September 2025*

## 🎯 Agent Registry
*Color-coded for visual tracking and identification*

### Master Orchestrator
**ID**: `master-orchestrator` 🟣
**Color**: `#8B5CF6` (Purple - Strategic Leadership)
**Role**: Strategic planning, task decomposition, agent coordination
**Location**: `.claude/orchestrator/master-orchestrator.md`
**Capabilities**:
- Analyzes PRD and creates strategic implementation plans
- Decomposes complex tasks into specialist assignments
- Manages sequential and parallel execution flows
- Aggregates results from multiple specialists
- Performs integration reviews and quality checks
**Preferred Tools**: `Task`, `TodoWrite`, `Read`, `Grep`
**Token Budget**: 100k per session
**Success Metrics**:
- Task completion rate > 95%
- Agent coordination efficiency > 90%
- Integration success rate > 95%

### Development Specialists

#### Elasticsearch Architect
**ID**: `elasticsearch-architect` 🔵
**Color**: `#3B82F6` (Blue - Data Architecture)
**Role**: Data schema design, indexing strategy, vector embeddings
**Location**: `.claude/specialists/elasticsearch-architect.md`
**Capabilities**:
- Designs enhanced ES mappings with AI fields
- Implements vector embedding strategies
- Optimizes search performance and indexing
- Creates aggregation pipelines
**Preferred Tools**: `Write`, `MultiEdit`, `Read`, `Grep`
**Token Budget**: 50k per task
**Output Format**: JSON schemas, mapping configurations

#### Backend Engineer
**ID**: `backend-engineer` 🟠
**Color**: `#F59E0B` (Orange - Core Infrastructure)
**Role**: FastAPI development, Supabase integration, API design
**Location**: `.claude/specialists/backend-engineer.md`
**Capabilities**:
- Implements FastAPI endpoints and routers
- Integrates Supabase authentication with security features
- Implements role-based access and user management
- Creates background task processors
- Manages session and token validation
**Preferred Tools**: `Write`, `MultiEdit`, `Bash`, `Read`
**Token Budget**: 75k per task
**Output Format**: Python code, API specifications, auth configurations

#### Frontend Specialist
**ID**: `frontend-specialist` 🟢
**Color**: `#10B981` (Green - User Interface)
**Role**: Next.js development, UI implementation, Planning Insights matching
**Location**: `.claude/specialists/frontend-specialist.md`
**Capabilities**:
- Implements React components with TypeScript
- Matches Planning Insights design exactly
- Integrates with backend APIs
- Implements state management with Zustand
**Preferred Tools**: `Write`, `MultiEdit`, `WebFetch`, `Read`
**Token Budget**: 75k per task
**Output Format**: TypeScript/JSX components, CSS modules

#### AI Engineer
**ID**: `ai-engineer` 🔵
**Color**: `#06B6D4` (Cyan - AI & Intelligence)
**Role**: LLM integration, opportunity scoring, NLP pipeline
**Location**: `.claude/specialists/ai-engineer.md`
**Capabilities**:
- Integrates OpenAI and Claude APIs
- Implements opportunity scoring algorithms
- Creates document summarization pipelines
- Develops semantic search capabilities
**Preferred Tools**: `Task`, `Write`, `WebFetch`, `Read`
**Token Budget**: 80k per task
**Output Format**: Python AI modules, prompt templates

### Support Specialists

#### DevOps Specialist
**ID**: `devops-specialist` ⚫
**Color**: `#6B7280` (Gray - Infrastructure)
**Role**: Docker configuration, deployment scripts, infrastructure
**Location**: `.claude/specialists/devops-specialist.md`
**Capabilities**:
- Creates Docker and docker-compose configurations
- Implements CI/CD pipelines
- Sets up VPS deployment scripts
- Configures monitoring and logging
**Preferred Tools**: `Bash`, `Write`, `Edit`, `Read`
**Token Budget**: 40k per task
**Output Format**: Dockerfiles, shell scripts, YAML configs

#### QA Engineer
**ID**: `qa-engineer` 🟣
**Color**: `#8B5CF6` (Purple - Quality Assurance)
**Role**: Test implementation, validation, performance testing
**Location**: `.claude/specialists/qa-engineer.md`
**Capabilities**:
- Creates pytest test suites
- Implements integration testing
- Performs load and performance testing
- Validates AI model accuracy
**Preferred Tools**: `Bash`, `Write`, `Read`, `Grep`
**Token Budget**: 50k per task
**Output Format**: Test files, test reports

#### Security Auditor
**ID**: `security-auditor` 🔴
**Color**: `#EF4444` (Red - Security & Protection)
**Role**: Security review, GDPR compliance, vulnerability assessment
**Location**: `.claude/specialists/security-auditor.md`
**Capabilities**:
- Validates Supabase authentication security configurations
- Reviews authentication implementation and security logging
- Ensures GDPR compliance with data handling
- Performs security vulnerability scanning
- Reviews rate limiting and account lockout policies
**Preferred Tools**: `Grep`, `Read`, `Task`, `Bash`
**Token Budget**: 40k per task
**Output Format**: Security reports, compliance checklists, audit logs

#### Documentation Writer
**ID**: `docs-writer` ⚪
**Color**: `#9CA3AF` (Light Gray - Documentation)
**Role**: API documentation, user guides, technical specifications
**Location**: `.claude/specialists/docs-writer.md`
**Capabilities**:
- Creates API documentation with OpenAPI specs
- Writes user guides and tutorials
- Documents architecture decisions
- Maintains README and setup guides
**Preferred Tools**: `Write`, `Read`, `WebFetch`
**Token Budget**: 30k per task
**Output Format**: Markdown documentation, OpenAPI specs

## 🔄 Communication Protocols

### Agent Invocation Format
```
AGENT: [agent-id]
TASK: [specific task description]
CONTEXT: [relevant context or dependencies]
INPUT: [required inputs or references]
OUTPUT: [expected deliverables]
CONSTRAINTS: [any limitations or requirements]
```

### Result Passing Format
```
AGENT: [agent-id]
STATUS: [completed|failed|partial]
OUTPUT: [deliverables produced]
METRICS: [performance metrics]
NEXT: [recommended next steps]
ISSUES: [any blockers or concerns]
```

### Context Sharing Rules
1. PRD reference is always available to all agents
2. Session state is maintained in `current-session.md`
3. Agents can read but not modify other agents' outputs
4. Critical decisions require master-orchestrator approval
5. Parallel agents must have independent scopes

## 📊 Orchestration Patterns

### Sequential Execution
```
1. master-orchestrator → strategic planning
2. elasticsearch-architect → schema design
3. backend-engineer → API implementation
4. ai-engineer → AI integration
5. frontend-specialist → UI development
6. qa-engineer → testing
7. security-auditor → security review
8. master-orchestrator → final integration
```

### Parallel Execution Groups
```
Group 1 (Foundation):
- elasticsearch-architect
- devops-specialist

Group 2 (Core Development):
- backend-engineer
- frontend-specialist
- ai-engineer

Group 3 (Quality):
- qa-engineer
- security-auditor
- docs-writer
```

### Decision Trees
```
IF task.complexity > HIGH:
  USE master-orchestrator
ELIF task.type == "UI":
  USE frontend-specialist
ELIF task.type == "API":
  USE backend-engineer
ELIF task.type == "AI":
  USE ai-engineer
ELSE:
  USE master-orchestrator → delegate
```

## 🎯 Task Assignment Matrix

| Task Type | Primary Agent | Support Agents | Execution Mode |
|-----------|--------------|----------------|----------------|
| Schema Design | elasticsearch-architect | ai-engineer | Sequential |
| API Development | backend-engineer | elasticsearch-architect | Sequential |
| UI Implementation | frontend-specialist | - | Parallel |
| AI Integration | ai-engineer | backend-engineer | Sequential |
| Testing | qa-engineer | all specialists | Sequential |
| Deployment | devops-specialist | security-auditor | Sequential |
| Documentation | docs-writer | all specialists | Parallel |
| Security Review | security-auditor | backend-engineer | Sequential |
| Integration | master-orchestrator | all agents | Sequential |

## 🎨 Visual Status System

### Color-Coded Agent Status
```yaml
agent_visual_status:
  active: "🔴 {color_emoji} {agent-name} ({task_description})"
  completed: "✅ {color_emoji} {agent-name} ({task_description})"
  queued: "⏳ {color_emoji} {agent-name} ({task_description})"
  failed: "❌ {color_emoji} {agent-name} ({error_description})"
  blocked: "🚧 {color_emoji} {agent-name} ({blocking_reason})"
```

### Real-Time Status Updates
```markdown
Session Progress: [████████░░] 80% (4/5 agents completed)
Active: 🔵 ai-engineer (Implementing opportunity scoring)
Completed: 🟣 master-orchestrator, 🟠 backend-engineer, 🟢 frontend-specialist
Next: 🔴 security-auditor (Security review)
```

### Performance Dashboard
```yaml
live_metrics:
  session_id: "planning-explorer-dev-20250928"
  phase: "AI Integration"
  agents_active: ["ai-engineer"]
  agents_completed: ["master-orchestrator", "backend-engineer", "frontend-specialist"]
  progress_percentage: 80
  estimated_completion: "15 minutes"

  current_agent:
    name: "ai-engineer"
    color: "#06B6D4"
    emoji: "🔵"
    task: "Implementing opportunity scoring system"
    tools_used: 12
    tokens_consumed: 45800
    elapsed_time: "5m 23s"
    progress: 60
```

## 💾 State Management

### Session State Structure
```yaml
session:
  id: [uuid]
  started: [timestamp]
  phase: [planning|development|testing|deployment]
  agents_active: []
  tasks_completed: []
  tasks_pending: []
  context: {}
  metrics: {}
```

### State Persistence Rules
1. **Real-time Updates**: Save state on every agent status change
2. **Visual Tracking**: Include color-coded status in all updates
3. **Performance Metrics**: Track tools, tokens, and timing per agent
4. **Audit Trail**: Maintain complete decision and execution history
5. **Session Archives**: Preserve completed sessions with visual summaries
6. **Live Dashboard**: Update current-session.md with visual status grid
7. **Notification System**: Trigger alerts on completions and blocks

## 📊 Session Update Protocols

### Automatic Status Updates
```yaml
update_triggers:
  agent_start: "Update session with 🔴 active status"
  agent_complete: "Update session with ✅ completed status + metrics"
  agent_blocked: "Update session with 🚧 blocked status + reason"
  progress_milestone: "Update progress bar and estimated completion"
  token_threshold: "Update token usage dashboard every 10k tokens"
  time_interval: "Refresh live metrics every 30 seconds"
```

### Visual Status Grid Format
```markdown
┌─────────────────────┬──────────┬─────────────┬──────────────┬─────────────┐
│ Agent               │ Status   │ Current Task│ Progress     │ Metrics     │
├─────────────────────┼──────────┼─────────────┼──────────────┼─────────────┤
│ 🟣 master-orchestrator │ ✅ Done  │ Strategic Planning │ 100%    │ 15 tools, 81.3k tokens, 2m43s │
│ 🟠 backend-engineer    │ ✅ Done  │ API Development    │ 100%    │ 24 tools, 103.5k tokens, 15m3s │
│ 🟢 frontend-specialist │ ✅ Done  │ UI Implementation  │ 100%    │ 55 tools, 110.3k tokens, 21m54s │
│ 🔵 ai-engineer        │ 🔴 Active │ AI Integration     │ 60%     │ 12 tools, 45.8k tokens, 5m23s │
│ 🔴 security-auditor   │ ⏳ Queued │ Security Review    │ 0%      │ Waiting for AI completion │
└─────────────────────┴──────────┴─────────────┴──────────────┴─────────────┘
```

### Session Animation Display
```
🔄 Live Session: Planning Explorer Development
   Phase: AI Integration [████████░░] 80%

   🔴 ai-engineer processing... [▓▓▓▓▓▓░░░░] 60%
   └── Implementing opportunity scoring system
       Tools: OpenAI integration ✓ | Vector embeddings ⚡ | Scoring logic 📊

   Next: 🔴 security-auditor (Security review)
   ETA: ~15 minutes remaining
```

## 🚀 Optimization Strategies

### Token Efficiency
- Share common context via agents.md
- Use focused prompts for specialists
- Batch similar operations
- Clear intermediate results
- Compress session data

### Parallel Processing
- Identify independent tasks
- Group compatible agents
- Use Task tool for complex searches
- Batch file operations
- Minimize context switching

### Quality Assurance
- Mandatory review checkpoints
- Automated testing gates
- Security validation steps
- Performance benchmarks
- Integration verification

## 📈 Success Metrics

### Agent Performance KPIs
- **Response Time**: < 30 seconds per invocation
- **Success Rate**: > 95% task completion
- **Token Usage**: Within budget limits
- **Output Quality**: Meets specifications
- **Integration**: Seamless handoffs

### Project Delivery Metrics
- **Code Coverage**: > 80%
- **API Performance**: < 200ms response
- **AI Accuracy**: > 85% scoring precision
- **UI Match**: 100% Planning Insights fidelity
- **Security Score**: A+ rating

## 🔧 Tool Assignment

### Tool Priority by Agent
```yaml
master-orchestrator: [Task, TodoWrite, Read, Grep]
elasticsearch-architect: [Write, MultiEdit, Read, Grep]
backend-engineer: [Write, MultiEdit, Bash, Read]
frontend-specialist: [Write, MultiEdit, WebFetch, Read]
ai-engineer: [Task, Write, WebFetch, Read]
devops-specialist: [Bash, Write, Edit, Read]
qa-engineer: [Bash, Write, Read, Grep]
security-auditor: [Grep, Read, Task, Bash]
docs-writer: [Write, Read, WebFetch]
```

## 🆘 Error Recovery

### Failure Handling
1. Agent timeout → Retry with reduced scope
2. Token limit → Split task and continue
3. Dependency failure → Notify orchestrator
4. Integration conflict → Rollback and replan
5. Quality failure → Invoke specialist for fixes

### Escalation Path
1. Specialist agent fails → Retry once
2. Second failure → Escalate to orchestrator
3. Orchestrator fails → Request user intervention
4. Critical failure → Full state dump and recovery plan

## 📋 Validation Checklist

### Pre-Execution
- [ ] PRD requirements clear
- [ ] Dependencies identified
- [ ] Agents available
- [ ] Token budget approved
- [ ] Session initialized

### Post-Execution
- [ ] Outputs validated
- [ ] Tests passing
- [ ] Security reviewed
- [ ] Documentation updated
- [ ] Metrics recorded

## 🎓 Learning & Improvement

### Continuous Optimization
1. Track agent performance metrics
2. Identify bottlenecks and inefficiencies
3. Update prompts based on outcomes
4. Refine orchestration patterns
5. Share learnings across sessions

### Feedback Loop
- Collect metrics after each session
- Analyze token usage patterns
- Review agent success rates
- Update templates and patterns
- Optimize based on results

---

*This central configuration serves as the brain of the Planning Explorer AI development framework. All agents reference this file for coordination, communication protocols, and optimization strategies.*