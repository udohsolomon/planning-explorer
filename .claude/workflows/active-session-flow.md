# 🔄 Active Session Flow - Live Development Workflow
*Real-time session management during active development*

## Workflow Overview
This workflow activates session management automatically during active Planning Explorer development, providing live tracking and visual feedback.

## Auto-Activation Triggers

### 1. Master Orchestrator Invocation
```
Invoke master-orchestrator with session tracking to analyze the Planning Explorer PRD and coordinate development

SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
AGENT: master-orchestrator
TASK: Analyze PRD and create comprehensive implementation plan
```

**Auto-Actions:**
- Initialize new session: `planning-explorer-dev-[timestamp]`
- Set phase to `planning`
- Update agent status to `active`
- Display colour-coded progress

### 2. Parallel Development Coordination
```
Execute in parallel with session tracking:

AGENT: elasticsearch-architect
SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
TASK: Design enhanced ES schema with vector embeddings

AGENT: backend-engineer
SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
TASK: Implement FastAPI with Supabase integration

AGENT: frontend-specialist
SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
TASK: Build Next.js UI matching Planning Insights design exactly
```

**Auto-Actions:**
- Update session phase to `development`
- Track parallel agent execution
- Display live progress grid
- Update metrics dashboard

### 3. AI Integration Phase
```
AGENT: ai-engineer
SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
TASK: Integrate OpenAI and Claude APIs for opportunity scoring
```

**Auto-Actions:**
- Update session phase to `ai-integration`
- Track AI model implementations
- Monitor token usage for AI operations
- Display embedding processing progress

## Live Dashboard Integration

### Real-Time Session Display
```markdown
🔄 LIVE SESSION: Planning Explorer Development
   Phase: Backend Development [████████░░] 80%

   🟠 backend-engineer active [▓▓▓▓▓▓▓▓░░] 85%
   └── Implementing FastAPI endpoints with Supabase auth
       Current: POST /api/opportunities with role-based access
       Tools: Write, MultiEdit, Bash | Tokens: 45.8k/75k

   🟢 frontend-specialist active [▓▓▓▓▓▓░░░░] 65%
   └── Building Planning Insights UI components
       Current: PropertySearch component with shadcn/ui
       Tools: Write, WebFetch | Tokens: 38.2k/75k

   Next: 🔵 ai-engineer (AI integration)
   Session Tokens: 184k/500k | Time: 2h 15m | ETA: ~45m
```

### Auto-TodoWrite Integration
Session management automatically creates and updates TodoWrite entries:

```yaml
session_todo_sync:
  agent_start: "Create TodoWrite entry for agent task"
  progress_update: "Update TodoWrite progress percentage"
  agent_complete: "Mark TodoWrite as completed"
  phase_transition: "Create new TodoWrite for next phase"
```

## Active Development Commands

### Session Control During Development
```bash
# Display current session status
session:status

# Show live agent activities
session:agents-live

# Update session phase
session:phase development|testing|deployment

# Force session sync with current TodoWrite
session:sync-todos

# Generate progress report
session:report-now
```

### Emergency Session Management
```bash
# Save session checkpoint
session:checkpoint "pre-deployment"

# Rollback to previous state
session:rollback

# Archive current and start fresh
session:restart "Planning Explorer Dev v2"
```

## Integration with CLAUDE.md Workflow

### Auto-Session Initialization
When following CLAUDE.md instructions, sessions auto-start:

1. **Framework Invocation Detection**
   - Detects master-orchestrator invocation commands
   - Auto-creates session with project context
   - Applies Planning Explorer specific settings

2. **Agent Coordination Tracking**
   - Monitors parallel agent execution
   - Tracks sequential handoffs between specialists
   - Updates visual progress indicators

3. **Development Phase Management**
   - Auto-advances session phases based on task completion
   - Triggers appropriate specialist agents
   - Maintains development timeline

## Session State Persistence

### Continuous Auto-Save
```yaml
autosave_triggers:
  every_agent_action: true
  every_30_seconds: true
  on_phase_change: true
  on_error: true
  before_shutdown: true
```

### Development Session Recovery
```markdown
If session interrupted:
1. Auto-restore from last checkpoint
2. Resume agent activities from last known state
3. Maintain TodoWrite synchronization
4. Continue visual progress tracking
```

## Quality Gates Integration

### Automated Quality Checkpoints
```yaml
quality_gates:
  backend_complete:
    trigger: "backend-engineer status: completed"
    action: "invoke qa-engineer for API testing"

  frontend_complete:
    trigger: "frontend-specialist status: completed"
    action: "invoke qa-engineer for UI testing"

  ai_integration_complete:
    trigger: "ai-engineer status: completed"
    action: "invoke security-auditor for security review"
```

### Testing Phase Automation
```
When development phase completes:
AGENT: qa-engineer
SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
TASK: Execute comprehensive test suite with Playwright automation
AUTO_TRIGGER: development_phase_complete
```

## Session Analytics

### Real-Time Performance Metrics
```yaml
live_metrics:
  development_velocity: "Tasks completed per hour"
  agent_efficiency: "Successful tasks / Total attempts"
  token_optimization: "Average tokens per task completion"
  parallel_utilization: "Parallel agents / Total available"
  quality_score: "Tests passed / Total tests"
```

### Development Timeline Tracking
```markdown
📊 Development Timeline
├─ 09:00 🟣 Planning started (master-orchestrator)
├─ 09:45 🔵 Schema design (elasticsearch-architect)
├─ 10:30 🟠🟢 Parallel dev started (backend + frontend)
├─ 12:15 🔵 AI integration (ai-engineer)
├─ 14:00 🟣🔴 Testing phase (qa + security)
└─ 15:30 ⚫ Deployment (devops-specialist)
```

---

*This workflow ensures seamless session management during active Planning Explorer development, providing continuous visual feedback and automated progress tracking.*