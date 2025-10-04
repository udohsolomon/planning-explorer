# How to Invoke Planning Explorer Specialists
*Proper Usage Guide for Custom Subagent Framework*

## 🎯 Framework Overview

The Planning Explorer framework uses **custom role-switching**, NOT the built-in Claude Code Task tool. Each specialist is a detailed instruction file that Claude loads and executes directly.

---

## ✅ Correct Invocation Methods

### Method 1: Direct Specialist Loading (Recommended)
**Best for:** Single-specialist tasks with clear objectives

```
Load and follow the instructions from @.claude/specialists/frontend-specialist.md

Task: Build the search interface with shadcn/ui components
Requirements:
- SearchBar with Command dialog
- ApplicationCard matching Planning Insights design
- Responsive layout for mobile/tablet/desktop
```

**What happens:**
1. Claude reads the specialist instructions
2. Adopts that specialist persona and expertise
3. Executes the task following specialist guidelines
4. Updates session state in `.claude/sessions/current-session.md`
5. Uses TodoWrite to track progress

---

### Method 2: Master Orchestrator Coordination
**Best for:** Complex multi-phase projects requiring multiple specialists

```
Load and follow the instructions from @.claude/orchestrator/master-orchestrator.md

Coordinate development of the semantic search feature:
- Elasticsearch schema updates (vector embeddings)
- FastAPI backend endpoints
- Next.js frontend integration
- Playwright E2E testing
```

**What happens:**
1. Master Orchestrator analyzes requirements
2. Creates development plan with specialist sequence
3. Invokes first specialist (e.g., elasticsearch-architect)
4. Updates session state after completion
5. Invokes next specialist with context from session
6. Continues until all phases complete

---

### Method 3: Sequential Specialist Handoff
**Best for:** Workflows where output of one specialist feeds into next

```
Phase 1: Load @.claude/specialists/elasticsearch-architect.md
Design the enhanced schema for Planning Explorer with vector embeddings.
[Wait for completion and session update]

Phase 2: Load @.claude/specialists/backend-engineer.md
Read session state and implement FastAPI endpoints for the new schema.
[Wait for completion and session update]

Phase 3: Load @.claude/specialists/frontend-specialist.md
Read session state and build the UI components to consume the new endpoints.
```

**What happens:**
1. User explicitly controls specialist transitions
2. Each specialist updates session with their work
3. Next specialist reads session for context
4. TodoWrite maintains task continuity across switches

---

## ❌ Incorrect Methods (DO NOT USE)

### ❌ Using @agent-general-purpose with Task Tool
```
DON'T: Use the Task tool with general-purpose agent type and include
instructions from .claude/specialists/frontend-specialist.md
```
**Why wrong:** This spawns a separate agent instance, breaking session continuity and TodoWrite integration.

---

### ❌ Generic Agent Requests Without Loading Instructions
```
DON'T: Act as a frontend specialist and build the search interface
```
**Why wrong:** Claude doesn't have the Planning Explorer context, specialist instructions, or framework coordination.

---

### ❌ Parallel Task Tool Execution
```
DON'T: Execute these specialists in parallel using Task tool:
1. Backend Engineer for API
2. Frontend Specialist for UI
```
**Why wrong:** Breaks session state management, creates context fragmentation, no TodoWrite continuity.

---

## 📝 Session State Management

### Current Session File
**Location:** `.claude/sessions/current-session.md`

**Purpose:**
- Tracks active specialist and current work
- Maintains context between specialist switches
- Records completed work and next steps
- Enables seamless handoffs

### Session Update Protocol
Each specialist should update the session file with:
```yaml
specialist: frontend-specialist
status: in_progress
current_phase: search_interface_implementation
completed_tasks:
  - SearchBar component with Command dialog
  - ApplicationCard with Planning Insights styling
  - Responsive layout breakpoints
next_steps:
  - Integrate with backend API endpoints
  - Add error handling and loading states
  - Implement Playwright E2E tests
handoff_notes:
  - API endpoints expected at /api/search
  - Using shadcn/ui components from components/ui/
  - Planning Insights theme configured in globals.css
```

---

## 🔄 Common Workflow Patterns

### Pattern 1: Master Orchestrator → Specialists
```
1. Load @.claude/orchestrator/master-orchestrator.md
   "Plan and coordinate the opportunity scoring feature"

2. Master Orchestrator creates plan and invokes first specialist

3. Each specialist completes work, updates session, signals completion

4. Master Orchestrator reviews and invokes next specialist

5. Final integration review by Master Orchestrator
```

---

### Pattern 2: Direct Specialist Sequence
```
1. Load @.claude/specialists/elasticsearch-architect.md
   "Design schema for opportunity scoring with vector fields"

2. [Specialist completes, updates session]

3. Load @.claude/specialists/ai-engineer.md
   "Read session and implement opportunity scoring algorithm"

4. [Specialist completes, updates session]

5. Load @.claude/specialists/backend-engineer.md
   "Read session and create FastAPI endpoints for opportunity scoring"
```

---

### Pattern 3: Iterative Development with Single Specialist
```
Load @.claude/specialists/frontend-specialist.md

Task 1: Build SearchBar component
[Specialist completes]

Task 2: Build ApplicationCard component
[Specialist completes]

Task 3: Integrate components in search page
[Specialist completes]

All tasks use same specialist context, maintaining continuity
```

---

## 🛠️ Tool Usage Guidelines

### TodoWrite Integration
**All specialists must:**
- Create TodoWrite items at task start
- Mark in_progress when working on a task
- Mark completed ONLY when task is fully done
- Add new todos if blockers or issues discovered

```
Specialist starts work:
- TodoWrite: "Build SearchBar component" → in_progress

Specialist completes:
- TodoWrite: "Build SearchBar component" → completed

Specialist discovers issue:
- TodoWrite: "Fix shadcn/ui Command import error" → pending
```

---

### Session Updates
**Update session after:**
- Completing a major component or feature
- Before switching to another specialist
- When blocked and need handoff
- After discovering important context for next specialist

---

### File Operations
**Specialists should:**
- Use Read to check existing code before editing
- Use Edit for modifying existing files
- Use Write for creating new files
- Use Glob/Grep for discovering file locations
- Use Bash for terminal operations (git, npm, etc.)

---

## 📊 Example: Full Feature Development

### Feature: Semantic Search with AI Insights

#### Step 1: Master Orchestrator Planning
```
Load @.claude/orchestrator/master-orchestrator.md

Coordinate development of semantic search feature with:
- Vector embeddings in Elasticsearch
- AI-powered search ranking
- Frontend search interface
- E2E testing
```

#### Step 2: Elasticsearch Architect
```
Load @.claude/specialists/elasticsearch-architect.md

Design enhanced schema with:
- dense_vector field for embeddings
- AI metadata fields
- Hybrid search configuration
Update session when complete.
```

#### Step 3: AI Engineer
```
Load @.claude/specialists/ai-engineer.md

Read session state and implement:
- Embedding generation pipeline
- Semantic similarity search
- Search result ranking
Update session when complete.
```

#### Step 4: Backend Engineer
```
Load @.claude/specialists/backend-engineer.md

Read session state and create:
- /api/search/semantic endpoint
- Integration with ES vector search
- Response formatting with AI insights
Update session when complete.
```

#### Step 5: Frontend Specialist
```
Load @.claude/specialists/frontend-specialist.md

Read session state and build:
- SearchBar with semantic mode toggle
- Results display with AI insights
- Loading/error states
Update session when complete.
```

#### Step 6: QA Engineer
```
Load @.claude/specialists/qa-engineer.md

Read session state and create:
- Playwright E2E tests for search flow
- Component tests for SearchBar
- API integration tests
Update session when complete.
```

#### Step 7: Master Orchestrator Review
```
Load @.claude/orchestrator/master-orchestrator.md

Review session state and:
- Verify all components integrated
- Check test coverage
- Validate against requirements
- Archive session to session-history/
```

---

## 🎓 Best Practices

### 1. Always Load Instructions First
✅ **DO:** `Load @.claude/specialists/frontend-specialist.md` then give task
❌ **DON'T:** Give task without loading specialist context

### 2. Use Session State for Handoffs
✅ **DO:** Update session with completed work and context for next specialist
❌ **DON'T:** Switch specialists without documenting progress

### 3. Maintain TodoWrite Continuity
✅ **DO:** Keep todos updated as work progresses
❌ **DON'T:** Batch complete multiple todos or skip updates

### 4. Leverage Master Orchestrator for Complexity
✅ **DO:** Use orchestrator for multi-specialist coordination
❌ **DON'T:** Try to manually coordinate 5+ specialist switches

### 5. Keep Specialist Focus Narrow
✅ **DO:** One specialist completes their expertise area fully
❌ **DON'T:** Have frontend specialist also write backend code

---

## 🔍 Troubleshooting

### Issue: Specialist seems confused about context
**Solution:** Check if specialist instructions were loaded. Reload with `@.claude/specialists/[name].md`

### Issue: Work doesn't carry over between specialists
**Solution:** Verify session file is being updated. Check `.claude/sessions/current-session.md`

### Issue: TodoWrite items disappearing
**Solution:** Ensure using TodoWrite (not Task tool). Todos persist across specialist switches.

### Issue: Too many specialist switches, losing focus
**Solution:** Use Master Orchestrator to coordinate instead of manual switches.

### Issue: Specialist doing work outside their expertise
**Solution:** Be specific in task description. Reference specialist's core responsibilities.

---

## 📚 Quick Reference Card

| **Task Type** | **Method** | **Command** |
|---------------|------------|-------------|
| Single specialist task | Direct load | `Load @.claude/specialists/[name].md` |
| Multi-specialist project | Orchestrator | `Load @.claude/orchestrator/master-orchestrator.md` |
| Sequential handoff | Manual switching | Load specialist → work → update session → next |
| Check progress | Session review | `Read @.claude/sessions/current-session.md` |
| Review todos | TodoWrite check | Todos visible in Claude Code interface |

---

**Remember:** This is a role-switching framework where Claude adopts specialist personas by loading their instruction files. NO Task tool, NO separate agent instances, ONLY direct context loading and execution.
