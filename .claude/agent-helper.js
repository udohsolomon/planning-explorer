#!/usr/bin/env node

/**
 * Planning Explorer Agent Helper
 * Simplifies invocation of specialist agents through Claude Code
 */

const fs = require('fs');
const path = require('path');

const AGENTS_DIR = path.join(__dirname, 'specialists');
const ORCHESTRATOR_DIR = path.join(__dirname, 'orchestrator');

class AgentHelper {
  constructor() {
    this.availableAgents = this.loadAvailableAgents();
  }

  loadAvailableAgents() {
    const agents = {};

    // Load specialists
    const specialistFiles = fs.readdirSync(AGENTS_DIR);
    specialistFiles.forEach(file => {
      if (file.endsWith('.md')) {
        const agentId = file.replace('.md', '');
        agents[agentId] = {
          type: 'specialist',
          path: path.join(AGENTS_DIR, file),
          content: fs.readFileSync(path.join(AGENTS_DIR, file), 'utf8')
        };
      }
    });

    // Load orchestrator
    const orchestratorFiles = fs.readdirSync(ORCHESTRATOR_DIR);
    orchestratorFiles.forEach(file => {
      if (file.endsWith('.md')) {
        const agentId = file.replace('.md', '');
        agents[agentId] = {
          type: 'orchestrator',
          path: path.join(ORCHESTRATOR_DIR, file),
          content: fs.readFileSync(path.join(ORCHESTRATOR_DIR, file), 'utf8')
        };
      }
    });

    return agents;
  }

  generateInvocation(agentId, task, context = '', parallel = false) {
    const agent = this.availableAgents[agentId];
    if (!agent) {
      throw new Error(`Agent '${agentId}' not found. Available agents: ${Object.keys(this.availableAgents).join(', ')}`);
    }

    const agentInstructions = agent.content;
    const capitalizedId = agentId.split('-').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');

    if (parallel) {
      return this.generateParallelInvocation(agentId, task, context);
    }

    return `
I need you to use the Task tool to act as the ${capitalizedId} from the Planning Explorer specialist framework.

**Instructions:**
- Use subagent_type: "general-purpose"
- Include the following specialist instructions in your prompt:

\`\`\`
${agentInstructions}
\`\`\`

**Task**: ${task}
**Context**: ${context}

Please ensure you:
1. Follow the specialist's role and capabilities exactly
2. Use the preferred tools listed in the specialist profile
3. Maintain the token budget specified
4. Update TodoWrite for task tracking
5. Follow the communication protocols from the framework
`;
  }

  generateParallelInvocation(agents, tasks, context = '') {
    if (!Array.isArray(agents) || !Array.isArray(tasks)) {
      throw new Error('For parallel execution, provide arrays of agents and tasks');
    }

    if (agents.length !== tasks.length) {
      throw new Error('Number of agents must match number of tasks for parallel execution');
    }

    let invocation = `
I need you to execute multiple Planning Explorer specialists in parallel using the Task tool.

**Instructions:**
- Use multiple Task tool calls in a single message
- Each should use subagent_type: "general-purpose"
- Include the specialist instructions for each agent

**Context**: ${context}

**Parallel Execution:**
`;

    agents.forEach((agentId, index) => {
      const agent = this.availableAgents[agentId];
      if (!agent) {
        throw new Error(`Agent '${agentId}' not found`);
      }

      const capitalizedId = agentId.split('-').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');

      invocation += `
${index + 1}. **${capitalizedId}**
   - Task: ${tasks[index]}
   - Instructions: Include content from ${agent.path}
`;
    });

    return invocation;
  }

  listAgents() {
    console.log('\n🤖 Available Planning Explorer Agents:\n');

    Object.entries(this.availableAgents).forEach(([id, agent]) => {
      const capitalizedId = id.split('-').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');

      const typeEmoji = agent.type === 'orchestrator' ? '🎯' : '⚙️';
      console.log(`${typeEmoji} ${id} (${capitalizedId})`);
      console.log(`   Path: ${agent.path}`);
      console.log(`   Type: ${agent.type}\n`);
    });
  }

  generateQuickCommands() {
    return {
      'ai-engineer-search': this.generateInvocation('ai-engineer', 'Investigate semantic search quality issues', 'Current search results are not meeting quality expectations'),
      'master-orchestrator-plan': this.generateInvocation('master-orchestrator', 'Analyze PRD and create strategic implementation plan', 'Initial development phase for Planning Explorer'),
      'frontend-ui': this.generateInvocation('frontend-specialist', 'Implement Planning Insights UI components with shadcn/ui', 'Need to match existing design system exactly'),
      'backend-api': this.generateInvocation('backend-engineer', 'Set up FastAPI endpoints and Supabase integration', 'Initial API development phase'),
      'elasticsearch-schema': this.generateInvocation('elasticsearch-architect', 'Design enhanced ES schema with vector embeddings', 'Need to support AI-powered search and analytics')
    };
  }
}

// CLI Usage
if (require.main === module) {
  const helper = new AgentHelper();
  const command = process.argv[2];
  const agentId = process.argv[3];
  const task = process.argv[4];
  const context = process.argv[5] || '';

  try {
    switch (command) {
      case 'list':
        helper.listAgents();
        break;

      case 'invoke':
        if (!agentId || !task) {
          console.error('Usage: node agent-helper.js invoke <agent-id> "<task>" ["<context>"]');
          process.exit(1);
        }
        console.log(helper.generateInvocation(agentId, task, context));
        break;

      case 'parallel':
        console.log('For parallel execution, use the helper.generateParallelInvocation() method');
        break;

      case 'quick':
        const commands = helper.generateQuickCommands();
        console.log('\n🚀 Quick Commands:\n');
        Object.entries(commands).forEach(([name, command]) => {
          console.log(`**${name}:**`);
          console.log(command);
          console.log('\n---\n');
        });
        break;

      default:
        console.log(`
🤖 Planning Explorer Agent Helper

Usage:
  node agent-helper.js list                           # List all available agents
  node agent-helper.js invoke <agent-id> "<task>"     # Generate invocation for agent
  node agent-helper.js quick                          # Show quick command examples

Examples:
  node agent-helper.js list
  node agent-helper.js invoke ai-engineer "Fix semantic search quality"
  node agent-helper.js quick
        `);
    }
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

module.exports = AgentHelper;