# 📊 Dynamic Session Status Template
*Real-time Agent Execution Tracking*

## 🎨 Agent Color Coding System
*Based on Claude Fast Hero Image Color Scheme*

```yaml
agent_colors:
  master-orchestrator: "#8B5CF6"     # Purple - Strategic leadership
  supabase-specialist: "#EC4899"     # Pink - Database foundation
  backend-engineer: "#F59E0B"        # Orange - Core infrastructure
  frontend-specialist: "#10B981"     # Green - User interface
  performance-optimizer: "#EAB308"   # Yellow - Speed & efficiency
  security-auditor: "#EF4444"        # Red - Security & protection
  qa-engineer: "#8B5CF6"             # Purple - Quality assurance
  elasticsearch-architect: "#3B82F6" # Blue - Data architecture
  ai-engineer: "#06B6D4"             # Cyan - AI & intelligence
  devops-specialist: "#6B7280"       # Gray - Infrastructure
  docs-writer: "#9CA3AF"             # Light Gray - Documentation
```

## 🔄 Real-Time Status Display Format

### Active Agent Execution
```markdown
🔴 {agent_name} ({task_description})
└── In Progress ({tool_uses} tool uses • {token_count} tokens • {elapsed_time})
```

### Completed Agent Tasks
```markdown
✅ {agent_name} ({task_description})
└── Done ({tool_uses} tool uses • {token_count} tokens • {total_time})
```

### Queued/Pending Agents
```markdown
⏳ {agent_name} ({task_description})
└── Queued (Waiting for dependencies)
```

## 📈 Session Progress Tracking

### Dynamic Progress Bar
```
Overall Progress: [████████░░] 80% (4/5 agents completed)
Current Phase: AI Integration
Active: ai-engineer (Implementing opportunity scoring)
Next: qa-engineer (Testing AI accuracy)
```

### Live Agent Status Grid
```yaml
┌─────────────────────┬──────────┬─────────────┬──────────────┬─────────────┐
│ Agent               │ Status   │ Current Task│ Tool Uses    │ Tokens      │
├─────────────────────┼──────────┼─────────────┼──────────────┼─────────────┤
│ 🟣 master-orchestrator │ Complete │ Strategic Planning │ 15 • 43s   │ 81.3k      │
│ 🟢 frontend-specialist │ Complete │ UI Implementation  │ 55 • 21m   │ 110.3k     │
│ 🟠 backend-engineer    │ Complete │ API Development    │ 24 • 15m   │ 103.5k     │
│ 🔵 elasticsearch-arch  │ Complete │ Schema Design      │ 18 • 8m    │ 67.2k      │
│ 🟡 ai-engineer        │ Active   │ AI Integration     │ 12 • 5m    │ 45.8k      │
│ 🔴 security-auditor   │ Queued   │ Security Review    │ -           │ -           │
│ 🟣 qa-engineer        │ Queued   │ Testing Suite      │ -           │ -           │
└─────────────────────┴──────────┴─────────────┴──────────────┴─────────────┘
```

## ⚡ Live Update Protocol

### Session State Updates
```yaml
session_update:
  timestamp: "2025-09-28T14:30:15Z"
  phase: "development"
  active_agents: ["ai-engineer"]
  completed_count: 4
  total_count: 7
  progress_percentage: 57
  estimated_completion: "2025-09-28T16:45:00Z"

  current_activity:
    agent: "ai-engineer"
    task: "Implementing opportunity scoring system"
    status: "processing"
    tools_used: 12
    tokens_consumed: 45800
    elapsed_time: "5m 23s"
    progress: "60%"
```

### Agent Status Change Events
```yaml
agent_event:
  type: "status_change"
  agent: "backend-engineer"
  previous_status: "active"
  new_status: "completed"
  completion_metrics:
    tools_used: 24
    tokens_consumed: 103500
    duration: "15m 3.8s"
    success_rate: 100
    quality_score: "A+"
```

## 🎯 Enhanced Task Tracking

### Task Decomposition Display
```markdown
🟠 backend-engineer (Backend API and business logic)
├── ✅ FastAPI project structure setup
├── ✅ Supabase integration configuration
├── ✅ Authentication middleware implementation
├── 🔄 Planning data API endpoints (60% complete)
├── ⏳ AI integration endpoints
└── ⏳ Performance optimization
```

### Parallel Execution Visualization
```
Parallel Group 2 - Core Development:
┌─ 🟠 backend-engineer ────── [████████░░] 80% ─┐
├─ 🟢 frontend-specialist ─── [██████████] 100% ─┤ → Integration Ready
└─ 🔵 ai-engineer ─────────── [██████░░░░] 60% ─┘
```

## 🔔 Smart Notifications

### Agent Completion Alerts
```markdown
🎉 Agent Completed Successfully!
🟢 frontend-specialist finished "Analytics dashboard UI implementation"
   • Duration: 21m 54.8s
   • Quality Score: A+ (100% Planning Insights match)
   • Token Efficiency: 110.3k tokens (within budget)
   • Next: Ready for integration testing
```

### Blocking Issues Detection
```markdown
🚨 Agent Blocked - Attention Required!
🔴 security-auditor waiting for backend-engineer completion
   • Dependency: API security review requires completed endpoints
   • Estimated Delay: 15 minutes
   • Action: Continue with parallel tasks or wait
```

## 📊 Performance Metrics Dashboard

### Real-Time Metrics
```yaml
session_metrics:
  efficiency:
    average_completion_time: "18m 30s"
    token_usage_rate: 85.2  # percentage of budget
    success_rate: 100       # percentage successful
    parallel_efficiency: 92 # percentage optimal

  quality:
    code_coverage: 87       # percentage
    test_pass_rate: 100     # percentage
    security_score: "A+"    # grade
    performance_score: 94   # percentage

  progress:
    tasks_completed: 24
    tasks_remaining: 8
    estimated_completion: "45 minutes"
    confidence_level: 95    # percentage
```

### Agent Performance Comparison
```
Token Efficiency Ranking:
1. 🟣 master-orchestrator: 81.3k tokens (81% budget used)
2. 🔵 elasticsearch-architect: 67.2k tokens (65% budget used)
3. 🟠 backend-engineer: 103.5k tokens (69% budget used)
4. 🟢 frontend-specialist: 110.3k tokens (73% budget used)

Speed Ranking:
1. 🔵 elasticsearch-architect: 8m 15s
2. 🟣 master-orchestrator: 2m 43s
3. 🟠 backend-engineer: 15m 3.8s
4. 🟢 frontend-specialist: 21m 54.8s
```

## 🎪 Session Animation Effects

### Progress Animation
```
🔄 Processing... [▓▓▓▓▓▓▓░░░] 70%
🟡 ai-engineer working on opportunity scoring implementation...
   Tools: OpenAI API integration ✓ | Vector embeddings ⚡ | Scoring logic 📊
```

### Completion Celebration
```
🎊 MILESTONE ACHIEVED! 🎊
Planning Explorer Backend Infrastructure Complete!
🟠 backend-engineer + 🔵 elasticsearch-architect + 🟣 master-orchestrator
Total: 3 agents • 67 tool uses • 252.1k tokens • 26m 42s
Success Rate: 100% | Quality Score: A+ | Performance: Optimal
```

## 🔄 Session Auto-Update Rules

### Update Triggers
1. **Agent Status Change**: Active → Completed/Failed
2. **Task Progress**: Every 25% completion milestone
3. **Tool Usage**: Every 5 tool uses or significant operation
4. **Token Threshold**: Every 10k tokens consumed
5. **Time Interval**: Every 2 minutes during active execution
6. **Dependency Resolution**: When blocking conditions clear
7. **Quality Gate**: When review checkpoints reached

### Update Frequency
```yaml
update_intervals:
  agent_status: "real-time"           # Immediate on status change
  progress_metrics: "30 seconds"     # Regular progress updates
  token_usage: "1 minute"           # Token consumption tracking
  quality_metrics: "on_completion"   # After each agent finishes
  session_summary: "5 minutes"       # Periodic comprehensive updates
```

---

*This template enables dynamic, color-coded, real-time tracking of agent execution with comprehensive progress visualization and performance metrics.*