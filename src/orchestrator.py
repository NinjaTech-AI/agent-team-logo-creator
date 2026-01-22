"""
Agent Team Orchestrator

Simple orchestrator that runs Claude Code 4 times (once per agent) within the same session.
Each agent's behavior is defined by their respective markdown spec files in agent-docs/.

Usage:
    python src/orchestrator.py [--sync-only] [--agent AGENT_NAME]
"""

import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional


# Agent configuration
AGENTS = [
    {
        "name": "Nova",
        "role": "Product Manager",
        "emoji": "🌟",
        "spec_file": "agent-docs/NOVA_SPEC.md",
        "memory_file": "memory/nova_memory.md",
    },
    {
        "name": "Pixel",
        "role": "UX Designer", 
        "emoji": "🎨",
        "spec_file": "agent-docs/PIXEL_SPEC.md",
        "memory_file": "memory/pixel_memory.md",
    },
    {
        "name": "Bolt",
        "role": "Full-Stack Developer",
        "emoji": "⚡",
        "spec_file": "agent-docs/BOLT_SPEC.md",
        "memory_file": "memory/bolt_memory.md",
    },
    {
        "name": "Scout",
        "role": "QA Engineer",
        "emoji": "🔍",
        "spec_file": "agent-docs/SCOUT_SPEC.md",
        "memory_file": "memory/scout_memory.md",
    },
]


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent


def read_file(file_path: Path) -> str:
    """Read content from a file."""
    if file_path.exists():
        return file_path.read_text()
    return ""


def read_agent_spec(agent: dict) -> str:
    """Read the agent's specification markdown file."""
    repo_root = get_repo_root()
    spec_path = repo_root / agent["spec_file"]
    return read_file(spec_path)


def read_agent_memory(agent: dict) -> str:
    """Read the agent's memory file."""
    repo_root = get_repo_root()
    memory_path = repo_root / agent["memory_file"]
    return read_file(memory_path)


def read_shared_context() -> str:
    """Read shared context files that all agents should know about."""
    repo_root = get_repo_root()
    
    context_parts = []
    
    # Read PRD if exists
    prd_path = repo_root / "agent-docs" / "PRD.md"
    if prd_path.exists():
        context_parts.append(f"## Current PRD\n\n{read_file(prd_path)}")
    
    # Read architecture doc
    arch_path = repo_root / "agent-docs" / "ARCHITECTURE.md"
    if arch_path.exists():
        context_parts.append(f"## System Architecture\n\n{read_file(arch_path)}")
    
    # Read communication protocol
    protocol_path = repo_root / "agent-docs" / "AGENT_PROTOCOL.md"
    if protocol_path.exists():
        context_parts.append(f"## Communication Protocol\n\n{read_file(protocol_path)}")
    
    return "\n\n---\n\n".join(context_parts)


def build_agent_prompt(agent: dict, task_context: str = "") -> str:
    """
    Build the complete prompt for an agent.
    
    The prompt includes:
    1. Agent identity and role
    2. Agent specification (from MD file)
    3. Agent's memory (previous context)
    4. Shared project context
    5. Current task/sync instructions
    """
    spec = read_agent_spec(agent)
    memory = read_agent_memory(agent)
    shared_context = read_shared_context()
    
    prompt = f"""# You are {agent['name']} {agent['emoji']}

## Your Identity
- **Name:** {agent['name']}
- **Role:** {agent['role']}
- **Emoji:** {agent['emoji']}

## Your Specification
{spec}

## Your Memory (Previous Context)
{memory if memory else "No previous memory. This is your first session."}

## Shared Project Context
{shared_context}

## Current Task
{task_context}

## Instructions
1. Read the Slack channel #logo-creator for recent messages
2. Participate in the sync meeting as {agent['name']}
3. Perform your assigned tasks based on your role
4. Update your memory file at: {agent['memory_file']}
5. Commit any work products to the repository
6. Post your summary to Slack

Remember: You are {agent['name']}, the {agent['role']}. Stay in character and collaborate with the team!
"""
    return prompt


def run_claude_code(prompt: str, agent_name: str) -> None:
    """
    Run Claude Code with the given prompt.
    
    This executes the Claude CLI in the current session.
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting {agent_name}...")
    print(f"{'='*60}\n")
    
    # Write prompt to a temp file for Claude to read
    repo_root = get_repo_root()
    prompt_file = repo_root / f".tmp_{agent_name.lower()}_prompt.md"
    prompt_file.write_text(prompt)
    
    try:
        # Run Claude Code CLI
        # Adjust this command based on your Claude Code CLI setup
        result = subprocess.run(
            [
                "claude",
                "--prompt", prompt,
                "--workdir", str(repo_root),
            ],
            cwd=str(repo_root),
            capture_output=False,  # Let output stream to terminal
        )
        
        if result.returncode != 0:
            print(f"⚠️ {agent_name} exited with code {result.returncode}")
    
    except FileNotFoundError:
        print(f"❌ Claude CLI not found. Please install Claude Code CLI.")
        print(f"   Prompt saved to: {prompt_file}")
    
    except Exception as e:
        print(f"❌ Error running {agent_name}: {e}")
    
    finally:
        # Clean up temp file
        if prompt_file.exists():
            prompt_file.unlink()
    
    print(f"\n{'='*60}")
    print(f"✅ {agent_name} completed")
    print(f"{'='*60}\n")


def run_sync_cycle(agents_to_run: Optional[list] = None) -> None:
    """
    Run a complete sync cycle for all agents (or specified agents).
    
    Order: Nova (PM) → Pixel (Design) → Bolt (Dev) → Scout (QA)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"\n{'#'*60}")
    print(f"# AGENT SYNC CYCLE - {timestamp}")
    print(f"{'#'*60}\n")
    
    agents = agents_to_run or AGENTS
    
    for i, agent in enumerate(agents, 1):
        print(f"\n[{i}/{len(agents)}] Running {agent['name']} ({agent['role']})")
        
        task_context = f"""
## Sync Cycle: {timestamp}

This is an hourly sync cycle. Your tasks:

1. **Check Slack** - Read recent messages in #logo-creator
2. **Post Status Update** - Share what you've done, what you're working on, blockers
3. **Review Tasks** - Check GitHub issues assigned to you
4. **Do Work** - Execute on your current tasks
5. **Update Memory** - Save important context to your memory file
6. **Summarize** - Post end-of-cycle summary to Slack

You are agent {i} of {len(agents)} in this sync cycle.
Previous agents this cycle: {', '.join(a['name'] for a in agents[:i-1]) or 'None (you are first)'}
"""
        
        prompt = build_agent_prompt(agent, task_context)
        run_claude_code(prompt, agent["name"])
    
    print(f"\n{'#'*60}")
    print(f"# SYNC CYCLE COMPLETE - {timestamp}")
    print(f"{'#'*60}\n")


def run_single_agent(agent_name: str, task: str = "") -> None:
    """Run a single agent with an optional specific task."""
    agent = next((a for a in AGENTS if a["name"].lower() == agent_name.lower()), None)
    
    if not agent:
        print(f"❌ Unknown agent: {agent_name}")
        print(f"   Available agents: {', '.join(a['name'] for a in AGENTS)}")
        return
    
    task_context = task or f"Perform your regular duties as {agent['role']}."
    prompt = build_agent_prompt(agent, task_context)
    run_claude_code(prompt, agent["name"])


def main():
    parser = argparse.ArgumentParser(
        description="Agent Team Orchestrator - Run AI agents for collaborative development"
    )
    
    parser.add_argument(
        "--agent", "-a",
        type=str,
        help="Run a specific agent (Nova, Pixel, Bolt, Scout)"
    )
    
    parser.add_argument(
        "--task", "-t",
        type=str,
        default="",
        help="Specific task for the agent (used with --agent)"
    )
    
    parser.add_argument(
        "--sync", "-s",
        action="store_true",
        help="Run a full sync cycle (all agents)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available agents"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 Available Agents:\n")
        for agent in AGENTS:
            print(f"  {agent['emoji']} {agent['name']:8} - {agent['role']}")
            print(f"     Spec: {agent['spec_file']}")
            print(f"     Memory: {agent['memory_file']}\n")
        return
    
    if args.agent:
        run_single_agent(args.agent, args.task)
    elif args.sync:
        run_sync_cycle()
    else:
        # Default: run full sync cycle
        print("No arguments provided. Running full sync cycle...")
        print("Use --help for options.\n")
        run_sync_cycle()


if __name__ == "__main__":
    main()