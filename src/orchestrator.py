"""
Agent Team Orchestrator

Simple orchestrator that runs Claude Code 4 times (once per agent).
Each agent runs in its own sandbox VM with pre-configured MCPs.
Agent behavior is defined by their markdown spec files in agent-docs/.

Usage:
    python src/orchestrator.py                    # Run all agents
    python src/orchestrator.py --agent Nova       # Run specific agent
    python src/orchestrator.py --agent Nova --task "Interview Arash for PRD"
"""

import subprocess
import argparse
from pathlib import Path
from datetime import datetime


# Agent configuration
AGENTS = [
    {"name": "Nova",  "role": "Product Manager",      "emoji": "🌟", "spec": "NOVA_SPEC.md"},
    {"name": "Pixel", "role": "UX Designer",          "emoji": "🎨", "spec": "PIXEL_SPEC.md"},
    {"name": "Bolt",  "role": "Full-Stack Developer", "emoji": "⚡", "spec": "BOLT_SPEC.md"},
    {"name": "Scout", "role": "QA Engineer",          "emoji": "🔍", "spec": "SCOUT_SPEC.md"},
]

REPO_ROOT = Path(__file__).parent.parent


def read_file(path: Path) -> str:
    """Read file content or return empty string."""
    return path.read_text() if path.exists() else ""


def build_prompt(agent: dict, task: str = "") -> str:
    """Build the prompt for an agent from their spec and memory."""
    
    spec = read_file(REPO_ROOT / "agent-docs" / agent["spec"])
    memory = read_file(REPO_ROOT / "memory" / f"{agent['name'].lower()}_memory.md")
    prd = read_file(REPO_ROOT / "agent-docs" / "PRD.md")
    protocol = read_file(REPO_ROOT / "agent-docs" / "AGENT_PROTOCOL.md")
    
    return f"""# You are {agent['name']} {agent['emoji']}

## Your Identity
- **Name:** {agent['name']}
- **Role:** {agent['role']}
- **Emoji:** {agent['emoji']}

---

## Your Specification

{spec}

---

## Communication Protocol

{protocol}

---

## Current PRD

{prd if prd else "No PRD yet. Nova needs to interview Arash to create it."}

---

## Your Memory

{memory if memory else "No previous memory. This is your first session."}

---

## Current Task

{task if task else "Check Slack #logo-creator, sync with team, do your work, update your memory file."}

---

## Instructions

1. Use **Slack MCP** to read #logo-creator channel and post updates
2. Do your work based on your role and current tasks
3. Commit any files to the repo, share GitHub links in Slack
4. Update your memory file: `memory/{agent['name'].lower()}_memory.md`
5. Stay in character as {agent['name']}, the {agent['role']}

You are running in your own sandbox VM. All MCPs are pre-configured.
"""


def run_agent(agent: dict, task: str = "") -> None:
    """Run Claude Code for a single agent."""
    
    print(f"\n{'='*60}")
    print(f"{agent['emoji']} Starting {agent['name']} ({agent['role']})")
    print(f"{'='*60}\n")
    
    prompt = build_prompt(agent, task)
    
    # Run Claude Code CLI
    try:
        subprocess.run(
            ["claude", "--prompt", prompt, "--workdir", str(REPO_ROOT)],
            cwd=str(REPO_ROOT),
        )
    except FileNotFoundError:
        print("❌ Claude CLI not found. Install Claude Code CLI first.")
        return
    
    print(f"\n✅ {agent['name']} completed\n")


def run_all_agents() -> None:
    """Run all agents in sequence: Nova → Pixel → Bolt → Scout"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n{'#'*60}")
    print(f"# AGENT SYNC CYCLE - {timestamp}")
    print(f"{'#'*60}")
    
    for i, agent in enumerate(AGENTS, 1):
        print(f"\n[{i}/{len(AGENTS)}] {agent['emoji']} {agent['name']}")
        run_agent(agent)
    
    print(f"\n{'#'*60}")
    print(f"# SYNC COMPLETE")
    print(f"{'#'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Agent Team Orchestrator")
    parser.add_argument("--agent", "-a", help="Run specific agent (Nova, Pixel, Bolt, Scout)")
    parser.add_argument("--task", "-t", default="", help="Specific task for the agent")
    parser.add_argument("--list", "-l", action="store_true", help="List agents")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 Agents:\n")
        for a in AGENTS:
            print(f"  {a['emoji']} {a['name']:8} - {a['role']}")
        print()
        return
    
    if args.agent:
        agent = next((a for a in AGENTS if a["name"].lower() == args.agent.lower()), None)
        if not agent:
            print(f"❌ Unknown agent: {args.agent}")
            print(f"   Available: {', '.join(a['name'] for a in AGENTS)}")
            return
        run_agent(agent, args.task)
    else:
        run_all_agents()


if __name__ == "__main__":
    main()