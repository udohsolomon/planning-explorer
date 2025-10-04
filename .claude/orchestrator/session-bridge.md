# 🌉 Session Bridge - Task Tool Integration
*Auto-connect session management with Claude Code orchestration*

## Purpose
This bridge automatically activates session management and colour schemes when agents are invoked through the Task tool during orchestration.

## Integration Protocol

### Agent Invocation Format
When invoking agents through Task tool, use this format to trigger session management:

```
AGENT: [agent-id]
SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
TASK: [specific task description]
CONTEXT: [relevant context or dependencies]
INPUT: [required inputs or references]
OUTPUT: [expected deliverables]
CONSTRAINTS: [any limitations or requirements]
```

### Auto-Detection Patterns
The session bridge auto-activates when Task prompts contain:
- Agent ID patterns: `master-orchestrator`, `elasticsearch-architect`, etc.
- Session keywords: `SESSION_TRACKING`, `VISUAL_FEEDBACK`
- Orchestration phrases: "invoke", "coordinate", "parallel execution"

### Visual Feedback Integration
```yaml
task_tool_enhancements:
  agent_identification:
    - Parse agent ID from Task prompts
    - Apply corresponding colour scheme
    - Display agent emoji and name

  progress_tracking:
    - Auto-create TodoWrite entries for agents
    - Update progress based on Task completion
    - Maintain visual status grid

  result_formatting:
    - Apply agent colours to Task results
    - Include performance metrics
    - Generate session summaries
```

## Implementation Hooks

### Pre-Task Execution
```markdown
1. Detect agent ID in Task prompt
2. Initialize session tracking if not active
3. Update agent status to "active"
4. Apply colour scheme to terminal output
```

### During Task Execution
```markdown
1. Monitor Task tool usage and token consumption
2. Update real-time metrics
3. Maintain visual progress indicators
4. Log agent activities
```

### Post-Task Completion
```markdown
1. Update agent status to "completed"
2. Record final metrics and performance
3. Generate agent summary
4. Update session dashboard
```

## Master Orchestrator Integration

### Enhanced Orchestrator Prompts
```
Please invoke the master-orchestrator agent with session tracking enabled to analyze the PRD and coordinate the Planning Explorer build.

SESSION_TRACKING: enabled
VISUAL_FEEDBACK: colored
AGENT: master-orchestrator
TASK: Analyze Planning Explorer PRD and create comprehensive implementation plan
EXPECTED_OUTPUT: Strategic development plan with phase-by-phase execution roadmap
```

### Parallel Agent Coordination
```
Execute in parallel with session tracking:
AGENT: backend-engineer
SESSION_TRACKING: enabled
TASK: FastAPI setup and Supabase integration

AGENT: frontend-specialist
SESSION_TRACKING: enabled
TASK: Next.js + shadcn/ui initialization

AGENT: elasticsearch-architect
SESSION_TRACKING: enabled
TASK: Enhanced schema design with vector embeddings
```

## Auto-Session Commands

### Quick Session Management
```bash
# Auto-start session when orchestration begins
session:auto-init

# Display live agent status during orchestration
session:live-status

# Generate real-time visual dashboard
session:dashboard-live

# Export orchestration report
session:export-orchestration
```

### Integration Status Indicators
```markdown
🔄 SESSION ACTIVE: Planning Explorer Development
   Phase: AI Integration [████████░░] 80%

   🔴 ai-engineer processing... [▓▓▓▓▓▓░░░░] 60%
   └── Implementing opportunity scoring system
       Task Status: Task tool active ⚡
       Tools: OpenAI integration ✓ | Vector embeddings ⚡ | Scoring logic 📊

   Next: 🔴 security-auditor (Security review)
   ETA: ~15 minutes remaining
```

## Session Bridge Activation

### Manual Activation
Add to any Task tool prompt:
```
SESSION_BRIDGE: activate
AGENT: [agent-name]
VISUAL_MODE: enhanced
```

### Auto-Activation Triggers
- Task prompts containing agent IDs
- Orchestration-related keywords
- Multi-agent coordination requests
- Planning Explorer specific tasks

---

*This bridge ensures seamless integration between Claude Code's Task tool and the Planning Explorer session management system, providing visual feedback and progress tracking during orchestration.*