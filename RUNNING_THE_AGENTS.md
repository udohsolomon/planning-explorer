# 🚀 Running the Autonomous Agent Workflow

## Quick Start Guide

### Prerequisites

1. **Python 3.11+** (You have 3.12.3 ✅)
2. **API Keys** configured in `.env`:
   ```bash
   ANTHROPIC_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here  # Optional
   ```

3. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

---

## 🧪 Option 1: Run Tests (Verify Everything Works)

### Test All Collaboration Components
```bash
cd backend
python3 -m pytest tests/test_collaboration.py -v
```

This runs **60 integration tests** covering:
- Negotiation & consensus
- Knowledge base & patterns
- Collaborative problem solving
- Task redistribution
- Agent swarms
- Collective memory
- Emergent coordination

**Expected**: All tests should pass (or skip if dependencies missing)

### Test Specific Components
```bash
# Test only negotiation
python3 -m pytest tests/test_collaboration.py::TestNegotiationProtocol -v

# Test only knowledge base
python3 -m pytest tests/test_collaboration.py::TestKnowledgeBase -v

# Test only swarms
python3 -m pytest tests/test_collaboration.py::TestAgentSwarms -v
```

---

## 🎮 Option 2: Interactive Demo Script

### Create a Demo Script

Create `backend/demo_agents.py`:

```python
"""
Demo: Autonomous Agent Collaboration
Shows agents working together on a real task
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import framework components
from app.agents.llm import LLMClient, LLMModel
from app.agents.orchestrator_agent import AgentRole

# Import collaboration components
from app.agents.collaboration import (
    # Negotiation
    NegotiationProtocol,
    ProposalType,
    ConsensusEngine,
    ConsensusStrategy,

    # Knowledge
    KnowledgeBase,
    KnowledgeType,
    KnowledgeQuery,
    PatternLibrary,
    SolutionRepository,
    SolutionType,

    # Problem Solving
    CollaborativeSolver,
    InvestigationType,
    SolutionSynthesizer,
    SynthesisStrategy,

    # Task Management
    TaskRedistributor,
    TaskPriority,

    # Swarms
    AgentSwarm,
    SwarmBehavior,

    # Memory
    CollectiveMemory,
    MemoryType,
    MemoryQuery,

    # Coordination
    EmergentCoordination,
    SignalType,
)


async def demo_negotiation():
    """Demo: Agents negotiate on a technical decision"""
    print("\n" + "="*60)
    print("DEMO 1: Agent Negotiation - Database Choice")
    print("="*60 + "\n")

    # Initialize LLM client
    llm_client = LLMClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_model=LLMModel.CLAUDE_3_5_SONNET
    )

    # Create negotiation protocol
    negotiator = NegotiationProtocol(llm_client=llm_client)

    # Backend agent proposes using PostgreSQL
    print("📋 Backend Agent proposes: Use PostgreSQL for database")
    proposal = await negotiator.propose(
        proposer=AgentRole.BACKEND,
        proposal_type=ProposalType.TECHNICAL_CHANGE,
        title="Use PostgreSQL as primary database",
        description="PostgreSQL provides ACID compliance, JSON support, and strong ecosystem",
        context={"current_db": "none", "requirements": ["ACID", "JSON", "scalability"]}
    )

    print(f"✅ Proposal created: {proposal.proposal_id}")
    print(f"   Rationale: {proposal.rationale[:100]}...")

    # Negotiate with other agents
    print("\n🤝 Starting negotiation with Frontend and DevOps agents...")
    result = await negotiator.negotiate(
        proposal=proposal,
        participating_agents=[AgentRole.FRONTEND, AgentRole.DEVOPS],
        context={}
    )

    print(f"\n📊 Negotiation Result:")
    print(f"   Status: {result.status}")
    print(f"   Rounds: {result.rounds_completed}")
    print(f"   Final Decision: {result.final_decision or 'Pending'}")

    return result


async def demo_collaborative_investigation():
    """Demo: Multiple agents investigate a problem together"""
    print("\n" + "="*60)
    print("DEMO 2: Collaborative Investigation - Performance Issue")
    print("="*60 + "\n")

    llm_client = LLMClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_model=LLMModel.CLAUDE_3_5_SONNET
    )

    # Setup components
    knowledge_base = KnowledgeBase(llm_client=llm_client)
    solution_repo = SolutionRepository(llm_client=llm_client, knowledge_base=knowledge_base)
    solver = CollaborativeSolver(
        llm_client=llm_client,
        knowledge_base=knowledge_base,
        solution_repository=solution_repo
    )

    # Multiple agents investigate performance problem
    print("🔍 Backend, DevOps, and AI agents investigating performance degradation...")
    investigation = await solver.investigate(
        problem="API response times have increased from 200ms to 2000ms under load",
        investigation_type=InvestigationType.PERFORMANCE_ANALYSIS,
        agents=[AgentRole.BACKEND, AgentRole.DEVOPS, AgentRole.AI],
        context={
            "metrics": {
                "avg_response_time": "2000ms",
                "p95_response_time": "5000ms",
                "concurrent_users": 1000
            }
        }
    )

    print(f"\n📊 Investigation Complete:")
    print(f"   Participating Agents: {len(investigation.participating_agents)}")
    print(f"   Total Findings: {len(investigation.findings)}")
    print(f"   Proposed Solutions: {len(investigation.proposals)}")

    if investigation.synthesized_solution:
        print(f"\n💡 Synthesized Solution:")
        print(f"   Approach: {investigation.synthesized_solution.get('approach', 'N/A')}")

    return investigation


async def demo_agent_swarm():
    """Demo: Agent swarm optimizes the system"""
    print("\n" + "="*60)
    print("DEMO 3: Agent Swarm - Parallel Exploration")
    print("="*60 + "\n")

    llm_client = LLMClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_model=LLMModel.CLAUDE_3_5_SONNET
    )

    swarm_system = AgentSwarm(llm_client=llm_client)

    # Create swarm for optimization task
    print("🐝 Creating agent swarm for system optimization...")
    swarm = await swarm_system.create_swarm(
        task_description="Find and implement performance optimizations across the application",
        agents=[AgentRole.BACKEND, AgentRole.FRONTEND, AgentRole.AI, AgentRole.DEVOPS],
        behavior=SwarmBehavior.PARALLEL_EXPLORATION,
        max_iterations=5
    )

    print(f"✅ Swarm created: {swarm.task_id}")
    print(f"   Behavior: {swarm.behavior.value}")
    print(f"   Agents: {len(swarm.participating_agents)}")

    # Execute swarm
    print(f"\n🚀 Executing swarm (max {swarm.max_iterations} iterations)...")
    result = await swarm_system.execute_swarm(swarm.task_id)

    print(f"\n📊 Swarm Execution Complete:")
    print(f"   Status: {swarm.status}")
    print(f"   Iterations: {swarm.iterations_completed}")
    print(f"   Discoveries: {len(swarm.discoveries)}")

    stats = swarm_system.get_swarm_statistics(swarm.task_id)
    print(f"\n📈 Swarm Statistics:")
    for agent, contribution in stats['agent_contributions'].items():
        print(f"   {agent}: {contribution:.2f} contribution points")

    return result


async def demo_task_redistribution():
    """Demo: Dynamic task redistribution based on load"""
    print("\n" + "="*60)
    print("DEMO 4: Task Redistribution - Load Balancing")
    print("="*60 + "\n")

    llm_client = LLMClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_model=LLMModel.CLAUDE_3_5_SONNET
    )

    redistributor = TaskRedistributor(llm_client=llm_client)

    # Initialize agents with expertise
    redistributor.initialize_agents(
        agents=[AgentRole.BACKEND, AgentRole.FRONTEND, AgentRole.AI],
        expertise_map={
            AgentRole.BACKEND: ["api", "database", "python"],
            AgentRole.FRONTEND: ["ui", "react", "typescript"],
            AgentRole.AI: ["ml", "embeddings", "llm"]
        }
    )

    print("📋 Submitting tasks to the system...")

    # Submit various tasks
    tasks = []
    task_specs = [
        ("api_development", "Build user authentication API", TaskPriority.CRITICAL, ["api", "python"]),
        ("ui_design", "Design dashboard UI", TaskPriority.HIGH, ["ui", "react"]),
        ("ml_model", "Train recommendation model", TaskPriority.MEDIUM, ["ml", "embeddings"]),
        ("database_optimization", "Optimize queries", TaskPriority.HIGH, ["database"]),
        ("testing", "Write integration tests", TaskPriority.LOW, ["testing"]),
    ]

    for task_type, description, priority, expertise in task_specs:
        task = await redistributor.submit_task(
            task_type=task_type,
            description=description,
            priority=priority,
            required_expertise=expertise
        )
        tasks.append(task)
        print(f"   ✅ {task.task_id}: '{description}' → {task.assigned_to.value}")

    print(f"\n📊 Task Distribution:")
    stats = redistributor.get_statistics()
    for agent, agent_stats in stats['agent_statistics'].items():
        print(f"   {agent}:")
        print(f"      Current load: {agent_stats['current_tasks']} tasks")
        print(f"      Utilization: {agent_stats['utilization']:.1%}")

    # Complete some tasks to trigger rebalancing
    print(f"\n✅ Completing first 2 tasks...")
    await redistributor.complete_task(tasks[0].task_id, success=True, duration=300)
    await redistributor.complete_task(tasks[1].task_id, success=True, duration=450)

    print(f"\n📊 Updated Statistics:")
    stats = redistributor.get_statistics()
    print(f"   Completed: {stats['tasks_by_status'].get('completed', 0)}")
    print(f"   Redistributions: {stats.get('redistributions', 0)}")

    return tasks


async def demo_collective_memory():
    """Demo: Agents share and retrieve collective memories"""
    print("\n" + "="*60)
    print("DEMO 5: Collective Memory - Shared Learning")
    print("="*60 + "\n")

    llm_client = LLMClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_model=LLMModel.CLAUDE_3_5_SONNET
    )

    memory_system = CollectiveMemory(llm_client=llm_client)

    # Agents store memories
    print("💾 Agents storing memories...")

    memories = []

    # Backend stores deployment success
    mem1 = await memory_system.store(
        memory_type=MemoryType.EPISODIC,
        content="Successfully deployed v2.0 with zero downtime using blue-green deployment",
        structured_data={
            "version": "2.0",
            "strategy": "blue-green",
            "downtime": 0,
            "duration_minutes": 15
        },
        created_by=AgentRole.DEVOPS,
        tags=["deployment", "success", "blue-green"]
    )
    memories.append(mem1)
    print(f"   ✅ DevOps: Deployment success (importance: {mem1.importance:.2f})")

    # Frontend stores UI pattern
    mem2 = await memory_system.store(
        memory_type=MemoryType.BEST_PRACTICE,
        content="Dark mode toggle implemented using CSS variables and localStorage",
        structured_data={
            "pattern": "css-variables",
            "persistence": "localStorage",
            "performance": "excellent"
        },
        created_by=AgentRole.FRONTEND,
        tags=["ui", "dark-mode", "css"]
    )
    memories.append(mem2)
    print(f"   ✅ Frontend: UI pattern (importance: {mem2.importance:.2f})")

    # AI stores optimization technique
    mem3 = await memory_system.store(
        memory_type=MemoryType.OPTIMIZATION,
        content="Reduced embedding generation time by 70% using batch processing",
        structured_data={
            "technique": "batch-processing",
            "improvement": 0.7,
            "batch_size": 100
        },
        created_by=AgentRole.AI,
        tags=["optimization", "embeddings", "performance"]
    )
    memories.append(mem3)
    print(f"   ✅ AI: Optimization technique (importance: {mem3.importance:.2f})")

    # Retrieve memories
    print(f"\n🔍 Querying memories: 'How to optimize performance?'")
    query = MemoryQuery(
        query_text="How to optimize performance and speed?",
        tags=["optimization", "performance"]
    )

    result = await memory_system.retrieve(query, limit=5)

    print(f"\n📊 Retrieved {len(result.memories)} relevant memories:")
    for memory in result.memories:
        relevance = result.relevance_scores.get(memory.memory_id, 0)
        print(f"   • {memory.content[:60]}... (relevance: {relevance:.2f})")
        print(f"     Created by: {memory.created_by.value}, accessed {memory.access_count} times")

    # Consolidate memories
    print(f"\n🔄 Running memory consolidation...")
    await memory_system.consolidate_memories()

    stats = memory_system.get_statistics()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Total stores: {stats['total_stores']}")
    print(f"   Total retrievals: {stats['total_retrievals']}")
    print(f"   Consolidations: {stats['total_consolidations']}")

    return memories


async def demo_emergent_coordination():
    """Demo: Agents self-organize through signals"""
    print("\n" + "="*60)
    print("DEMO 6: Emergent Coordination - Self-Organization")
    print("="*60 + "\n")

    llm_client = LLMClient(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        default_model=LLMModel.CLAUDE_3_5_SONNET
    )

    coordinator = EmergentCoordination(llm_client=llm_client)

    # Initialize agents
    coordinator.initialize_agent(AgentRole.BACKEND, specializations=["api", "database"])
    coordinator.initialize_agent(AgentRole.FRONTEND, specializations=["ui", "react"])
    coordinator.initialize_agent(AgentRole.AI, specializations=["ml", "embeddings"])

    print("🎯 Agents initialized in coordination system")

    # Backend emits help signal
    print(f"\n📡 Backend emits HELP_NEEDED signal (overloaded)...")
    signal1 = await coordinator.emit_signal(
        agent=AgentRole.BACKEND,
        signal_type=SignalType.HELP_NEEDED,
        content={"reason": "High API request volume", "priority": "high"},
        strength=0.9
    )
    print(f"   Signal: {signal1.signal_id}")

    # Frontend senses signals
    print(f"\n👂 Frontend sensing signals...")
    signals = await coordinator.sense_signals(
        agent=AgentRole.FRONTEND,
        signal_types=[SignalType.HELP_NEEDED, SignalType.TASK_AVAILABLE]
    )
    print(f"   Sensed {len(signals)} signals:")
    for sig in signals:
        print(f"      • {sig.signal_type.value} from {sig.emitted_by.value} (strength: {sig.current_strength():.2f})")

    # Frontend responds
    if signals:
        print(f"\n✅ Frontend responding to help signal...")
        await coordinator.respond_to_signal(
            agent=AgentRole.FRONTEND,
            signal_id=signals[0].signal_id,
            response={"action": "Will help with API documentation", "eta": "30min"}
        )

    # AI emits solution found
    print(f"\n📡 AI emits SOLUTION_FOUND signal...")
    signal2 = await coordinator.emit_signal(
        agent=AgentRole.AI,
        signal_type=SignalType.SOLUTION_FOUND,
        content={"solution": "Implemented caching layer", "impact": "70% reduction in load"},
        strength=0.95
    )

    # Update agent states
    print(f"\n📊 Updating agent workloads...")
    await coordinator.update_agent_state(AgentRole.BACKEND, workload=0.85)
    await coordinator.update_agent_state(AgentRole.FRONTEND, workload=0.45)
    await coordinator.update_agent_state(AgentRole.AI, workload=0.60)

    # Get coordination recommendations
    print(f"\n💡 Getting coordination recommendations for Backend...")
    recommendations = await coordinator.get_coordination_recommendations(
        agent=AgentRole.BACKEND,
        task="Reduce API latency",
        context={"current_latency": "500ms", "target": "100ms"}
    )

    print(f"   Recommendations:")
    print(f"      Collaborate with: {recommendations.get('collaborate_with', [])}")
    print(f"      Suggested pattern: {recommendations.get('suggested_pattern', 'N/A')}")
    if recommendations.get('reasoning'):
        print(f"      Reasoning: {recommendations['reasoning'][:100]}...")

    # Statistics
    stats = coordinator.get_statistics()
    print(f"\n📈 Coordination Statistics:")
    print(f"   Total signals emitted: {stats['total_signals_emitted']}")
    print(f"   Active signals: {stats['active_signals']}")
    print(f"   Total responses: {stats['total_responses']}")
    print(f"   Patterns detected: {stats['emergent_patterns_detected']}")

    return stats


async def run_all_demos():
    """Run all demos in sequence"""
    print("\n" + "🤖 "*30)
    print("  AUTONOMOUS AGENT COLLABORATION FRAMEWORK - DEMO")
    print("🤖 "*30 + "\n")

    try:
        # Run demos
        await demo_negotiation()
        await demo_collaborative_investigation()
        await demo_agent_swarm()
        await demo_task_redistribution()
        await demo_collective_memory()
        await demo_emergent_coordination()

        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")

        print("🎉 The autonomous agent framework is working!")
        print("\nNext steps:")
        print("  1. Integrate into Planning Explorer workflows")
        print("  2. Add database backend for persistence")
        print("  3. Deploy to production with monitoring")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all demos
    asyncio.run(run_all_demos())
```

### Run the Demo
```bash
cd backend
python3 demo_agents.py
```

This will run **6 interactive demos** showing all collaboration features in action!

---

## 📦 Option 3: Integrate into Planning Explorer

### Use in Your Application

```python
# In your Planning Explorer code
from app.agents.collaboration import (
    KnowledgeBase,
    TaskRedistributor,
    CollectiveMemory,
    # ... other components
)

# Example: PSEO Agent uses knowledge base
kb = KnowledgeBase(llm_client)

# Store SEO best practices
await kb.add_knowledge(
    knowledge_type=KnowledgeType.BEST_PRACTICE,
    title="Meta description optimization",
    description="150-160 characters with primary keyword",
    content={"best_length": 155, "include": ["keyword", "call_to_action"]},
    discovered_by=AgentRole.AI
)

# Later: Retrieve when writing meta descriptions
query = KnowledgeQuery(query_text="How to write meta descriptions?")
result = await kb.query_knowledge(query)
```

---

## 🔧 Option 4: Production Deployment

### Step 1: Add Database Backend

The current implementation uses in-memory storage. For production:

```python
# Replace in-memory storage with PostgreSQL
# 1. Install pgvector
# 2. Update knowledge_base.py to use database
# 3. Add migrations
```

### Step 2: Add Monitoring

```python
# Add observability
from opentelemetry import trace
from prometheus_client import Counter, Histogram

# Track agent operations
agent_tasks_counter = Counter('agent_tasks_total', 'Total tasks processed')
task_duration = Histogram('task_duration_seconds', 'Task execution time')
```

### Step 3: Deploy with Docker

```bash
# Build container
docker build -t planning-explorer-agents .

# Run with environment
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY planning-explorer-agents
```

---

## 🎯 What Each Component Does

### For Planning Explorer Use Cases

1. **Negotiation Protocol**
   - Use for: Complex decisions requiring multiple agent perspectives
   - Example: "Should we use this SEO strategy?"

2. **Knowledge Base**
   - Use for: Storing and retrieving SEO patterns, planning insights
   - Example: "What enrichment patterns work best for this location?"

3. **Collaborative Solving**
   - Use for: Complex bugs, performance issues
   - Example: "Why is the enrichment agent slow?"

4. **Task Redistribution**
   - Use for: Load balancing across agents
   - Example: Distribute 1000 enrichment tasks across agents

5. **Agent Swarms**
   - Use for: Large-scale parallel work
   - Example: Optimize SEO for 10,000 planning applications

6. **Collective Memory**
   - Use for: Long-term learning across sessions
   - Example: Remember successful PSEO strategies

7. **Emergent Coordination**
   - Use for: Self-organizing workflows
   - Example: Agents autonomously help each other when overloaded

---

## 📝 Quick Reference Commands

```bash
# Test everything
cd backend && python3 -m pytest tests/test_collaboration.py -v

# Run interactive demo
cd backend && python3 demo_agents.py

# Test specific component
python3 -m pytest tests/test_collaboration.py::TestNegotiationProtocol -v

# Check Python version
python3 --version

# Install missing dependencies
pip install -r requirements.txt

# Run with verbose logging
export LOG_LEVEL=DEBUG
python3 demo_agents.py
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'app.agents'"
**Solution**:
```bash
cd backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 demo_agents.py
```

### Issue: "ANTHROPIC_API_KEY not found"
**Solution**: Create `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: Tests fail with "LLM client error"
**Solution**: Check API key is valid and has credits

---

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Tests pass (at least 50+ of 60)
- ✅ Demo script runs without errors
- ✅ Agents negotiate and reach consensus
- ✅ Knowledge is stored and retrieved
- ✅ Swarms execute and complete
- ✅ Memories are stored and consolidated

---

## 📚 Next Steps

After verifying the framework works:

1. **Integrate into Planning Explorer**:
   - Add to PSEO agent for SEO optimization
   - Add to Enrichment agent for collaborative enrichment
   - Add to search for collaborative ranking

2. **Production Readiness**:
   - Add PostgreSQL + pgvector backend
   - Add monitoring and metrics
   - Add error recovery and retries

3. **Choose Next Phase** (Optional):
   - Meta-Learning & Self-Improvement
   - Advanced Planning & Scheduling
   - External Tool Integration (MCP servers)
   - Production Deployment & Monitoring

---

**Questions? Issues?**

1. Check logs: `export LOG_LEVEL=DEBUG`
2. Run tests with verbose: `pytest -vv`
3. Review completion reports in root directory

**The framework is ready to use!** 🚀
