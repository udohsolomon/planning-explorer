# 📋 Task Patterns & Templates
*Reusable Task Structures for Agent Coordination*

## 🎯 Task Pattern Library

### Pattern 1: Agent Invocation Template
```markdown
## Agent Task Assignment

**Agent**: [agent-id]
**Priority**: [high|medium|low]
**Execution Mode**: [sequential|parallel]
**Dependencies**: [prerequisite tasks]

### Task Description
[Clear, specific description of what needs to be accomplished]

### Context
- **Project Phase**: [foundation|development|testing|deployment]
- **Related Components**: [list of related systems/modules]
- **Previous Tasks**: [completed dependencies]

### Input Requirements
- [ ] [Required input 1]
- [ ] [Required input 2]
- [ ] [Required input 3]

### Expected Outputs
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

### Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Performance target]

### Constraints
- **Timeline**: [deadline or duration]
- **Token Budget**: [max tokens]
- **Quality Standards**: [specific requirements]

### Validation Steps
1. [Validation step 1]
2. [Validation step 2]
3. [Final verification]
```

### Pattern 2: Parallel Execution Template
```markdown
## Parallel Agent Execution

**Coordination**: master-orchestrator
**Execution Group**: [group-name]
**Total Agents**: [number]

### Agent Assignments
| Agent | Task | Priority | Token Budget | Dependencies |
|-------|------|----------|--------------|--------------|
| [agent-1] | [task-1] | high | [budget] | [deps] |
| [agent-2] | [task-2] | high | [budget] | [deps] |
| [agent-3] | [task-3] | medium | [budget] | [deps] |

### Synchronization Points
1. **Checkpoint 1**: [milestone] - [expected time]
2. **Checkpoint 2**: [milestone] - [expected time]
3. **Final Review**: [integration] - [expected time]

### Conflict Resolution
- **Overlapping Outputs**: [resolution strategy]
- **Resource Conflicts**: [allocation rules]
- **Integration Issues**: [escalation path]
```

### Pattern 3: Sequential Workflow Template
```markdown
## Sequential Workflow

**Workflow Name**: [workflow-name]
**Total Steps**: [number]
**Estimated Duration**: [time]

### Workflow Steps
1. **Step 1**: [agent] → [task] → [output]
   - Duration: [time]
   - Success Criteria: [criteria]
   - Handoff: [next step requirements]

2. **Step 2**: [agent] → [task] → [output]
   - Duration: [time]
   - Dependencies: [from step 1]
   - Success Criteria: [criteria]

3. **Step 3**: [agent] → [task] → [output]
   - Duration: [time]
   - Dependencies: [from step 2]
   - Success Criteria: [criteria]

### Quality Gates
- [ ] Gate 1: [verification requirements]
- [ ] Gate 2: [validation requirements]
- [ ] Gate 3: [final approval requirements]

### Rollback Plan
If Step X fails:
1. [Immediate action]
2. [Recovery steps]
3. [Resume point]
```

## 🔄 Common Task Patterns

### Development Phase Patterns

#### Schema Design Task
```markdown
**Agent**: elasticsearch-architect
**Task**: Design Enhanced ES Schema for Planning Explorer

**Context**: Design comprehensive Elasticsearch mappings with AI enhancement fields

**Inputs**:
- Planning Explorer PRD
- AI field requirements
- Vector embedding specifications
- Performance requirements

**Process**:
1. Analyze data types and search patterns
2. Design core planning application fields
3. Add AI enhancement fields (scores, summaries, embeddings)
4. Configure analyzers and mappings
5. Set up index settings for performance
6. Create sample data insertion scripts

**Outputs**:
- Complete ES mapping JSON
- Index creation scripts
- Data ingestion templates
- Performance optimization settings

**Success Criteria**:
- All PRD data fields covered
- Vector search capabilities included
- < 100ms search response time design
- Scalable to 10M+ documents
```

#### API Development Task
```markdown
**Agent**: backend-engineer
**Task**: Implement FastAPI Backend with Supabase Integration

**Context**: Build production-ready API with authentication and AI integration

**Inputs**:
- Elasticsearch schema
- Supabase configuration
- API requirements from PRD
- Authentication specifications

**Process**:
1. Setup FastAPI project structure
2. Implement Supabase client integration
3. Create authentication middleware
4. Build search endpoints
5. Add AI processing endpoints
6. Implement rate limiting and validation
7. Add comprehensive error handling

**Outputs**:
- FastAPI application
- Authentication system
- API endpoints
- Request/response models
- Error handling middleware

**Success Criteria**:
- All endpoints respond < 200ms
- 100% test coverage
- Proper error handling
- Security best practices implemented
```

#### Frontend Development Task
```markdown
**Agent**: frontend-specialist
**Task**: Build Next.js Frontend Matching Planning Insights Design

**Context**: Create pixel-perfect UI implementation with AI features

**Inputs**:
- Planning Insights design reference
- API endpoints specification
- Component requirements
- Responsive design requirements

**Process**:
1. Setup Next.js 14 with TypeScript
2. Implement exact Planning Insights design system
3. Create reusable component library
4. Build search interface with AI features
5. Implement state management
6. Add responsive design
7. Optimize for performance

**Outputs**:
- Next.js application
- Component library
- State management setup
- Responsive layouts
- Performance optimizations

**Success Criteria**:
- 100% Planning Insights design match
- Lighthouse score > 95
- Mobile-first responsive
- Accessibility compliance
```

### AI Integration Patterns

#### AI Processing Pipeline Task
```markdown
**Agent**: ai-engineer
**Task**: Implement AI Processing Pipeline for Planning Applications

**Context**: Build comprehensive AI enhancement system

**Inputs**:
- Planning application data structure
- LLM API credentials
- Scoring algorithm requirements
- Performance targets

**Process**:
1. Setup OpenAI and Claude API clients
2. Implement summary generation
3. Create opportunity scoring algorithm
4. Build vector embedding generation
5. Add prediction models
6. Implement caching strategy
7. Add monitoring and metrics

**Outputs**:
- AI processing service
- Scoring algorithms
- Summary generation
- Vector embeddings
- Performance monitoring

**Success Criteria**:
- < 2 seconds processing time
- 85%+ scoring accuracy
- 4.2/5 summary quality rating
- Token cost < $0.10 per application
```

### Quality Assurance Patterns

#### Testing Implementation Task
```markdown
**Agent**: qa-engineer
**Task**: Implement Comprehensive Test Suite

**Context**: Build testing framework covering all components

**Inputs**:
- Application codebase
- API specifications
- UI components
- Performance requirements

**Process**:
1. Setup pytest framework
2. Implement unit tests for all modules
3. Create integration tests for APIs
4. Build E2E tests with Playwright
5. Add performance testing with Locust
6. Implement AI model validation
7. Setup CI/CD integration

**Outputs**:
- Complete test suite
- Test automation
- Performance benchmarks
- CI/CD integration
- Quality metrics

**Success Criteria**:
- > 85% code coverage
- All tests pass in CI/CD
- Performance targets met
- Zero critical bugs in production
```

### Deployment Patterns

#### Infrastructure Setup Task
```markdown
**Agent**: devops-specialist
**Task**: Setup Production Infrastructure with Docker

**Context**: Deploy scalable, monitored infrastructure

**Inputs**:
- Application components
- VPS specifications
- Security requirements
- Monitoring needs

**Process**:
1. Create Docker configurations
2. Setup docker-compose for services
3. Configure Nginx reverse proxy
4. Implement SSL with Let's Encrypt
5. Setup monitoring and logging
6. Create backup strategies
7. Implement CI/CD pipeline

**Outputs**:
- Docker configurations
- Deployment scripts
- Monitoring setup
- Backup systems
- CI/CD pipeline

**Success Criteria**:
- 99.9% uptime target
- Automated deployments
- Complete monitoring coverage
- Disaster recovery plan
```

## 🔧 Template Customization

### Task Complexity Levels

#### Simple Task Template
```markdown
**Agent**: [agent-id]
**Task**: [brief description]
**Input**: [single input]
**Output**: [single deliverable]
**Time**: [< 30 minutes]
```

#### Complex Task Template
```markdown
**Agent**: [agent-id]
**Task**: [detailed description]
**Inputs**: [multiple inputs with specifications]
**Process**: [step-by-step breakdown]
**Outputs**: [multiple deliverables with criteria]
**Dependencies**: [prerequisite tasks]
**Validation**: [quality checks]
**Time**: [> 1 hour]
```

### Priority Levels

#### High Priority Template
```markdown
**Priority**: HIGH 🔴
**Blocking**: [what this blocks]
**Timeline**: [urgent deadline]
**Resource Allocation**: [dedicated resources]
**Escalation**: [immediate escalation path]
```

#### Medium Priority Template
```markdown
**Priority**: MEDIUM 🟡
**Sequence**: [optimal timing]
**Resources**: [standard allocation]
**Flexibility**: [adjustment options]
```

#### Low Priority Template
```markdown
**Priority**: LOW 🟢
**Schedule**: [when convenient]
**Optimization**: [efficiency focus]
**Deferrable**: [can be postponed if needed]
```

## 📊 Task Tracking Templates

### Progress Tracking
```markdown
## Task Progress Tracker

**Task ID**: [unique-id]
**Agent**: [agent-name]
**Status**: [not_started|in_progress|blocked|completed|failed]
**Progress**: [0-100%]

### Timeline
- **Started**: [timestamp]
- **Expected Completion**: [timestamp]
- **Actual Completion**: [timestamp]

### Metrics
- **Token Usage**: [used/budget]
- **Quality Score**: [rating]
- **Performance**: [meets targets Y/N]

### Issues
- [ ] [Issue 1] - [status]
- [ ] [Issue 2] - [status]

### Next Steps
1. [Next action]
2. [Following action]
```

### Handoff Template
```markdown
## Task Handoff

**From Agent**: [previous-agent]
**To Agent**: [next-agent]
**Handoff Time**: [timestamp]

### Completed Work
- [Deliverable 1] ✅
- [Deliverable 2] ✅
- [Deliverable 3] ✅

### Context for Next Agent
- **Current State**: [description]
- **Key Decisions Made**: [list]
- **Known Issues**: [any concerns]
- **Resources Available**: [what's ready to use]

### Success Criteria for Next Phase
- [Criteria 1]
- [Criteria 2]
- [Criteria 3]
```

## 🎯 Agent-Specific Templates

### For Master Orchestrator
```markdown
**Orchestration Task**: [coordination-need]
**Agents Involved**: [list]
**Coordination Type**: [parallel|sequential|hybrid]
**Synchronization Points**: [when to check progress]
**Success Metrics**: [overall success criteria]
```

### For Elasticsearch Architect
```markdown
**Schema Task**: [schema-component]
**Data Types**: [field specifications]
**Performance Targets**: [query speed, index size]
**Integration Points**: [with AI, backend]
```

### For Backend Engineer
```markdown
**API Task**: [endpoint-group]
**Authentication**: [auth requirements]
**Data Flow**: [input → processing → output]
**Error Handling**: [failure scenarios]
```

### For Frontend Specialist
```markdown
**UI Task**: [component or page]
**Design Reference**: [Planning Insights elements]
**Responsive Needs**: [breakpoints]
**Interaction Patterns**: [user behaviors]
```

### For AI Engineer
```markdown
**AI Task**: [AI feature]
**Model Requirements**: [LLM, embeddings, ML]
**Accuracy Targets**: [performance metrics]
**Cost Constraints**: [token budgets]
```

---

*These task patterns provide consistent, reusable templates for agent coordination and task execution in the Planning Explorer development framework.*