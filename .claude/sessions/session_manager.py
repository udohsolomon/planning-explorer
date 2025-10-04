"""
Enhanced Session Management System for Planning Explorer AI Agents
Provides real-time tracking, visual status updates, and color-coded displays
"""

import json
import os
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Literal
from enum import Enum
from pathlib import Path
import hashlib


class AgentID(Enum):
    """Agent identifiers with associated colors and emojis"""
    ORCHESTRATOR = ("master-orchestrator", "#8B5CF6", "🟣", "\033[95m")
    ELASTICSEARCH = ("elasticsearch-architect", "#3B82F6", "🔵", "\033[94m")
    BACKEND = ("backend-engineer", "#F59E0B", "🟠", "\033[93m")
    FRONTEND = ("frontend-specialist", "#10B981", "🟢", "\033[92m")
    AI = ("ai-engineer", "#06B6D4", "🔵", "\033[96m")
    DEVOPS = ("devops-specialist", "#6B7280", "⚫", "\033[90m")
    QA = ("qa-engineer", "#A855F7", "🟣", "\033[35m")
    SECURITY = ("security-auditor", "#EF4444", "🔴", "\033[91m")
    DOCS = ("docs-writer", "#9CA3AF", "⚪", "\033[37m")

    def __init__(self, agent_id: str, color_hex: str, emoji: str, terminal_code: str):
        self.agent_id = agent_id
        self.color_hex = color_hex
        self.emoji = emoji
        self.terminal_code = terminal_code


class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "idle"
    QUEUED = "queued"
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class SessionPhase(Enum):
    """Session development phases"""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"


@dataclass
class AgentMetrics:
    """Metrics tracking for individual agents"""
    tokens_used: int = 0
    tools_used: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    elapsed_seconds: float = 0
    efficiency_score: float = 100.0


@dataclass
class AgentActivity:
    """Individual agent activity record"""
    timestamp: datetime
    agent_id: str
    action: str
    tools: List[str]
    tokens: int
    status: str = "info"
    details: Optional[str] = None


@dataclass
class Task:
    """Task representation"""
    id: str
    description: str
    agent_id: Optional[str] = None
    status: str = "pending"
    progress: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class AgentState:
    """Complete state for an individual agent"""
    agent_id: str
    name: str
    color_hex: str
    emoji: str
    terminal_code: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    progress: int = 0
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    history: List[AgentActivity] = field(default_factory=list)


@dataclass
class SessionState:
    """Complete session state"""
    id: str
    name: str
    started: datetime
    last_updated: datetime
    phase: SessionPhase = SessionPhase.PLANNING
    status: str = "active"
    agents: Dict[str, AgentState] = field(default_factory=dict)
    tasks_completed: List[Task] = field(default_factory=list)
    tasks_active: List[Task] = field(default_factory=list)
    tasks_pending: List[Task] = field(default_factory=list)
    tasks_blocked: List[Task] = field(default_factory=list)
    total_tokens: int = 0
    total_tools: int = 0
    elapsed_time: float = 0
    progress_percentage: float = 0
    estimated_completion: str = "Calculating..."
    activity_feed: List[AgentActivity] = field(default_factory=list)


class SessionManager:
    """Enhanced session management with visual tracking"""

    def __init__(self, base_path: str = ".claude"):
        self.base_path = Path(base_path)
        self.sessions_path = self.base_path / "sessions"
        self.current_session_path = self.sessions_path / "current-session.md"
        self.metrics_path = self.sessions_path / "session-metrics.json"
        self.activities_path = self.sessions_path / "agent-activities.log"
        self.dashboard_path = self.sessions_path / "visual-dashboard.md"
        self.history_path = self.sessions_path / "session-history"

        # Create directories if they don't exist
        self.sessions_path.mkdir(parents=True, exist_ok=True)
        self.history_path.mkdir(exist_ok=True)

        # Initialize agent registry
        self.agents = self._initialize_agents()

        # Current session
        self.current_session: Optional[SessionState] = None

    def _initialize_agents(self) -> Dict[str, AgentState]:
        """Initialize all agents with their configurations"""
        agents = {}
        for agent_enum in AgentID:
            agent = AgentState(
                agent_id=agent_enum.agent_id,
                name=agent_enum.agent_id.replace("-", " ").title(),
                color_hex=agent_enum.color_hex,
                emoji=agent_enum.emoji,
                terminal_code=agent_enum.terminal_code
            )
            agents[agent_enum.agent_id] = agent
        return agents

    def create_session(self, name: str) -> SessionState:
        """Create a new session"""
        session_id = f"{name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        session_hash = hashlib.md5(session_id.encode()).hexdigest()[:8]

        session = SessionState(
            id=f"{session_id}-{session_hash}",
            name=name,
            started=datetime.now(),
            last_updated=datetime.now(),
            agents=self.agents.copy()
        )

        self.current_session = session
        self.save_session()
        self.update_visual_dashboard()

        return session

    def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
        task: Optional[str] = None,
        progress: int = 0
    ):
        """Update an agent's status"""
        if not self.current_session:
            raise ValueError("No active session")

        agent = self.current_session.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_id}")

        # Update agent state
        agent.status = status
        agent.current_task = task
        agent.progress = progress

        # Update metrics
        if status == AgentStatus.ACTIVE and not agent.metrics.start_time:
            agent.metrics.start_time = datetime.now()
        elif status == AgentStatus.COMPLETED and agent.metrics.start_time:
            agent.metrics.end_time = datetime.now()
            agent.metrics.elapsed_seconds = (
                agent.metrics.end_time - agent.metrics.start_time
            ).total_seconds()

        # Add to activity feed
        activity = AgentActivity(
            timestamp=datetime.now(),
            agent_id=agent_id,
            action=f"Status changed to {status.value}",
            tools=[],
            tokens=0,
            status=status.value,
            details=task
        )
        agent.history.append(activity)
        self.current_session.activity_feed.append(activity)

        # Update session
        self.current_session.last_updated = datetime.now()
        self.save_session()
        self.update_visual_dashboard()

    def add_agent_activity(
        self,
        agent_id: str,
        action: str,
        tools: List[str],
        tokens: int,
        status: str = "info"
    ):
        """Add an activity to agent history"""
        if not self.current_session:
            raise ValueError("No active session")

        agent = self.current_session.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_id}")

        activity = AgentActivity(
            timestamp=datetime.now(),
            agent_id=agent_id,
            action=action,
            tools=tools,
            tokens=tokens,
            status=status
        )

        agent.history.append(activity)
        agent.metrics.tokens_used += tokens
        agent.metrics.tools_used += len(tools)

        self.current_session.activity_feed.append(activity)
        self.current_session.total_tokens += tokens
        self.current_session.total_tools += len(tools)

        self.save_session()
        self.update_visual_dashboard()

    def generate_progress_bar(self, percentage: float, width: int = 10) -> str:
        """Generate a visual progress bar"""
        filled = int(percentage / 100 * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percentage:.0f}%"

    def generate_status_grid(self) -> str:
        """Generate the visual status grid"""
        if not self.current_session:
            return "No active session"

        grid = []
        grid.append("┌─────────────────┬────────┬──────────────────┬─────────┬──────────────────┐")
        grid.append("│ Agent           │ Status │ Current Task     │ Progress│ Live Metrics     │")
        grid.append("├─────────────────┼────────┼──────────────────┼─────────┼──────────────────┤")

        for agent_id, agent in self.current_session.agents.items():
            name = agent.name[:15].ljust(15)
            status_icon = self._get_status_icon(agent.status)
            task = (agent.current_task or "Idle")[:16].ljust(16)
            progress = f"{agent.progress}%".rjust(7)

            metrics = f"{agent.metrics.tools_used}🔧 "
            metrics += f"{agent.metrics.tokens_used // 1000}k🪙 "
            if agent.metrics.elapsed_seconds > 0:
                minutes = int(agent.metrics.elapsed_seconds // 60)
                seconds = int(agent.metrics.elapsed_seconds % 60)
                metrics += f"{minutes}m{seconds}s"
            else:
                metrics += "Waiting..."

            row = f"│ {agent.emoji} {name} │ {status_icon}     │ {task} │ {progress} │ {metrics[:16].ljust(16)} │"
            grid.append(row)

        grid.append("└─────────────────┴────────┴──────────────────┴─────────┴──────────────────┘")

        return "\n".join(grid)

    def _get_status_icon(self, status: AgentStatus) -> str:
        """Get icon for agent status"""
        icons = {
            AgentStatus.IDLE: "⚪",
            AgentStatus.QUEUED: "⏳",
            AgentStatus.ACTIVE: "🔴",
            AgentStatus.COMPLETED: "✅",
            AgentStatus.BLOCKED: "🚧",
            AgentStatus.FAILED: "❌"
        }
        return icons.get(status, "❓")

    def generate_activity_feed(self, limit: int = 10) -> str:
        """Generate the activity feed display"""
        if not self.current_session:
            return "No active session"

        feed = ["## 📡 Live Activity Feed\n"]
        activities = sorted(
            self.current_session.activity_feed,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]

        for activity in activities:
            agent = self.current_session.agents.get(activity.agent_id)
            if not agent:
                continue

            time_str = activity.timestamp.strftime("%H:%M:%S")
            feed.append(f"{time_str} {agent.emoji} {agent.name}")
            feed.append(f"         └─ {activity.action}")

            if activity.tools:
                tools_str = ", ".join(activity.tools)
                feed.append(f"         └─ Tools: {tools_str} | Tokens: {activity.tokens / 1000:.1f}k")

            if activity.status == "completed":
                feed.append(f"         └─ ✅ Success")
            elif activity.status == "failed":
                feed.append(f"         └─ ❌ Failed")

            feed.append("")

        return "\n".join(feed)

    def calculate_progress(self) -> float:
        """Calculate overall session progress"""
        if not self.current_session:
            return 0

        total_tasks = (
            len(self.current_session.tasks_completed) +
            len(self.current_session.tasks_active) +
            len(self.current_session.tasks_pending) +
            len(self.current_session.tasks_blocked)
        )

        if total_tasks == 0:
            return 0

        completed = len(self.current_session.tasks_completed)
        return (completed / total_tasks) * 100

    def estimate_completion(self) -> str:
        """Estimate time to completion"""
        if not self.current_session:
            return "Unknown"

        progress = self.calculate_progress()
        if progress == 0:
            return "Calculating..."

        elapsed = (datetime.now() - self.current_session.started).total_seconds()
        if progress > 0:
            total_estimated = elapsed / (progress / 100)
            remaining = total_estimated - elapsed

            if remaining < 60:
                return f"~{int(remaining)}s remaining"
            elif remaining < 3600:
                return f"~{int(remaining / 60)}m remaining"
            else:
                hours = int(remaining / 3600)
                minutes = int((remaining % 3600) / 60)
                return f"~{hours}h {minutes}m remaining"

        return "Calculating..."

    def update_visual_dashboard(self):
        """Update the visual dashboard file"""
        if not self.current_session:
            return

        dashboard = []
        dashboard.append(f"# 📊 Session Dashboard: {self.current_session.name}")
        dashboard.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Overall progress
        progress = self.calculate_progress()
        dashboard.append(f"## Overall Progress")
        dashboard.append(f"{self.generate_progress_bar(progress, 20)}\n")

        # Phase status
        dashboard.append(f"**Phase**: {self.current_session.phase.value.title()}")
        dashboard.append(f"**Status**: {self.current_session.status}")
        dashboard.append(f"**Elapsed**: {self._format_elapsed_time()}")
        dashboard.append(f"**Estimated**: {self.estimate_completion()}\n")

        # Agent status grid
        dashboard.append("## Agent Status")
        dashboard.append("```")
        dashboard.append(self.generate_status_grid())
        dashboard.append("```\n")

        # Activity feed
        dashboard.append(self.generate_activity_feed())

        # Metrics summary
        dashboard.append("\n## Session Metrics")
        dashboard.append(f"- **Total Tokens**: {self.current_session.total_tokens:,}")
        dashboard.append(f"- **Total Tools**: {self.current_session.total_tools}")
        dashboard.append(f"- **Active Agents**: {self._count_active_agents()}")
        dashboard.append(f"- **Completed Tasks**: {len(self.current_session.tasks_completed)}")

        # Write dashboard
        with open(self.dashboard_path, "w") as f:
            f.write("\n".join(dashboard))

    def _format_elapsed_time(self) -> str:
        """Format elapsed time"""
        if not self.current_session:
            return "0s"

        elapsed = (datetime.now() - self.current_session.started).total_seconds()
        hours = int(elapsed / 3600)
        minutes = int((elapsed % 3600) / 60)
        seconds = int(elapsed % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def _count_active_agents(self) -> int:
        """Count currently active agents"""
        if not self.current_session:
            return 0

        return sum(
            1 for agent in self.current_session.agents.values()
            if agent.status == AgentStatus.ACTIVE
        )

    def save_session(self):
        """Save current session state"""
        if not self.current_session:
            return

        # Convert to serializable format
        session_data = {
            "id": self.current_session.id,
            "name": self.current_session.name,
            "started": self.current_session.started.isoformat(),
            "last_updated": self.current_session.last_updated.isoformat(),
            "phase": self.current_session.phase.value,
            "status": self.current_session.status,
            "progress_percentage": self.calculate_progress(),
            "estimated_completion": self.estimate_completion(),
            "total_tokens": self.current_session.total_tokens,
            "total_tools": self.current_session.total_tools,
            "agents": {}
        }

        # Add agent data
        for agent_id, agent in self.current_session.agents.items():
            session_data["agents"][agent_id] = {
                "status": agent.status.value,
                "current_task": agent.current_task,
                "progress": agent.progress,
                "metrics": {
                    "tokens_used": agent.metrics.tokens_used,
                    "tools_used": agent.metrics.tools_used,
                    "elapsed_seconds": agent.metrics.elapsed_seconds,
                    "efficiency_score": agent.metrics.efficiency_score
                }
            }

        # Save to JSON
        with open(self.metrics_path, "w") as f:
            json.dump(session_data, f, indent=2)

        # Update markdown session file
        self._update_session_markdown()

    def _update_session_markdown(self):
        """Update the current-session.md file"""
        # This would update the existing markdown file with new status
        # Implementation depends on specific format requirements
        pass

    def archive_session(self):
        """Archive current session to history"""
        if not self.current_session:
            return

        # Create archive directory
        archive_dir = self.history_path / self.current_session.id
        archive_dir.mkdir(exist_ok=True)

        # Copy current files to archive
        import shutil
        if self.dashboard_path.exists():
            shutil.copy(self.dashboard_path, archive_dir / "visual-dashboard.md")
        if self.metrics_path.exists():
            shutil.copy(self.metrics_path, archive_dir / "session-metrics.json")

        # Generate final report
        self._generate_final_report(archive_dir)

        # Clear current session
        self.current_session = None

    def _generate_final_report(self, archive_dir: Path):
        """Generate final session report"""
        # Implementation for comprehensive final report
        pass


# Example usage and testing
if __name__ == "__main__":
    # Create session manager
    manager = SessionManager()

    # Create new session
    session = manager.create_session("planning-explorer-dev")
    print(f"Created session: {session.id}")

    # Simulate agent activities
    manager.update_agent_status("master-orchestrator", AgentStatus.ACTIVE, "Strategic planning", 30)
    manager.add_agent_activity("master-orchestrator", "Analyzing PRD", ["Read", "Task"], 5000)

    time.sleep(1)

    manager.update_agent_status("backend-engineer", AgentStatus.ACTIVE, "API development", 50)
    manager.add_agent_activity("backend-engineer", "Creating FastAPI endpoints", ["Write", "MultiEdit"], 8000)

    time.sleep(1)

    manager.update_agent_status("frontend-specialist", AgentStatus.QUEUED, "UI implementation", 0)

    # Display dashboard
    print("\n" + "="*60)
    print(manager.generate_status_grid())
    print("\n" + "="*60)
    print(manager.generate_activity_feed())