# 🚀 Agent Invocation Guide for Planning Explorer

## Quick Start

To invoke any specialist agent, use the following format:

```typescript
Task({
  subagent_type: "general-purpose",
  description: "[Agent Name] - [Task Description]",
  prompt: `[Agent instructions from .md file] + [Your specific task]`
})
```

## Available Specialist Agents

### 🎯 Master Orchestrator
```typescript
Task({
  subagent_type: "general-purpose",
  description: "Master Orchestrator - Strategic Planning",
  prompt: `
    You are the master-orchestrator agent for Planning Explorer.
    Role: Strategic planning, task decomposition, agent coordination

    [Include content from .claude/orchestrator/master-orchestrator.md]

    TASK: [Your specific task]
    CONTEXT: [Relevant context]
  `
})
```

### 🔵 AI Engineer
```typescript
Task({
  subagent_type: "general-purpose",
  description: "AI Engineer - LLM Integration",
  prompt: `
    You are the ai-engineer specialist for Planning Explorer.
    Role: LLM integration, opportunity scoring, NLP pipeline

    [Include content from .claude/specialists/ai-engineer.md]

    TASK: [Your specific task]
    CONTEXT: [Relevant context]
  `
})
```

### 🟠 Backend Engineer
```typescript
Task({
  subagent_type: "general-purpose",
  description: "Backend Engineer - API Development",
  prompt: `
    You are the backend-engineer specialist for Planning Explorer.
    Role: FastAPI development, Supabase integration, API design

    [Include content from .claude/specialists/backend-engineer.md]

    TASK: [Your specific task]
    CONTEXT: [Relevant context]
  `
})
```

### 🟢 Frontend Specialist
```typescript
Task({
  subagent_type: "general-purpose",
  description: "Frontend Specialist - UI Development",
  prompt: `
    You are the frontend-specialist for Planning Explorer.
    Role: Next.js development, UI implementation

    [Include content from .claude/specialists/frontend-specialist.md]

    TASK: [Your specific task]
    CONTEXT: [Relevant context]
  `
})
```

### 🔵 Elasticsearch Architect
```typescript
Task({
  subagent_type: "general-purpose",
  description: "Elasticsearch Architect - Data Schema",
  prompt: `
    You are the elasticsearch-architect for Planning Explorer.
    Role: Data schema design, indexing strategy, vector embeddings

    [Include content from .claude/specialists/elasticsearch-architect.md]

    TASK: [Your specific task]
    CONTEXT: [Relevant context]
  `
})
```

## Correct Invocation Examples

### ✅ CORRECT - Using general-purpose with specialist instructions:
```
Please use the general-purpose agent to act as the ai-engineer and investigate semantic search quality issues
```

### ❌ INCORRECT - Trying to use specialist ID directly:
```
Please invoke the ai-engineer agent to investigate semantic search quality issues
```

## Helper Commands

### Invoke AI Engineer for Semantic Search
```
I need you to act as the AI Engineer specialist from the Planning Explorer framework. Read the specialist instructions from .claude/specialists/ai-engineer.md and investigate the semantic search quality issues. Use the general-purpose agent type with the ai-engineer instructions.
```

### Invoke Master Orchestrator for Planning
```
I need you to act as the Master Orchestrator from the Planning Explorer framework. Read the orchestrator instructions from .claude/orchestrator/master-orchestrator.md and create a strategic plan for the current development phase. Use the general-purpose agent type with the master-orchestrator instructions.
```

## Important Notes

1. **Always use `general-purpose` as the subagent_type** - The specialist IDs (ai-engineer, backend-engineer, etc.) are not valid subagent types
2. **Include the full specialist instructions** - Read the relevant .md file and include it in the prompt
3. **Maintain context** - Reference the session file at `.claude/sessions/current-session.md`
4. **Use TodoWrite** - Specialists should use TodoWrite for task tracking
5. **Follow token budgets** - Each specialist has a defined token budget in agents.md

## Session Management

Before invoking agents, ensure session is initialized:
1. Check/create `.claude/sessions/current-session.md`
2. Load relevant context from previous agent outputs
3. Update session after agent completion

## Parallel Execution

For parallel agent execution:
```typescript
// Execute multiple specialists in parallel
[
  Task({ subagent_type: "general-purpose", description: "Backend Engineer", prompt: "..." }),
  Task({ subagent_type: "general-purpose", description: "Frontend Specialist", prompt: "..." })
]
```

## Troubleshooting

### Error: "Agent type 'xxx' not found"
- Solution: Use `general-purpose` instead of the specialist ID
- Include specialist instructions in the prompt

### Error: "Context missing"
- Solution: Load session context from `.claude/sessions/current-session.md`
- Pass relevant context in the CONTEXT field

### Error: "Task unclear"
- Solution: Use the communication protocol format from agents.md
- Include TASK, CONTEXT, INPUT, and OUTPUT fields