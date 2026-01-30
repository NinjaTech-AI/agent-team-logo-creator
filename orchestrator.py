"""
Agent Team Orchestrator

Simple orchestrator that runs Claude Code for the configured agent.
Agent identity is read from ~/.agent_settings.json config file.
Agent behavior is defined by their markdown spec files in agent-docs/.

Usage:
    python orchestrator.py                    # Run configured agent
    python orchestrator.py --task "Interview Arash for PRD"
    python orchestrator.py --list             # List all agents
    python orchestrator.py --test             # Run capability tests
"""

import subprocess
import argparse
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime


# Agent configuration
AGENTS = {
    "nova":  {"name": "Nova",  "role": "Product Manager",      "emoji": "🌟", "spec": "NOVA_SPEC.md"},
    "pixel": {"name": "Pixel", "role": "UX Designer",          "emoji": "🎨", "spec": "PIXEL_SPEC.md"},
    "bolt":  {"name": "Bolt",  "role": "Full-Stack Developer", "emoji": "⚡", "spec": "BOLT_SPEC.md"},
    "scout": {"name": "Scout", "role": "QA Engineer",          "emoji": "🔍", "spec": "SCOUT_SPEC.md"},
}

REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = Path.home() / ".agent_settings.json"


def load_config() -> dict:
    """Load agent configuration from ~/.agent_settings.json"""
    if not CONFIG_PATH.exists():
        return {}
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"⚠️ Warning: Could not read config: {e}", file=sys.stderr)
        return {}


def get_agent_from_config() -> dict:
    """
    Get the agent configuration from the config file.
    
    Returns:
        Agent dict with name, role, emoji, spec
        
    Raises:
        SystemExit if no agent is configured
    """
    config = load_config()
    agent_id = config.get("default_agent", "").lower()
    
    if not agent_id:
        print("❌ ERROR: No agent configured!", file=sys.stderr)
        print("", file=sys.stderr)
        print("The orchestrator requires an agent identity to be set in the config file.", file=sys.stderr)
        print(f"Config file: {CONFIG_PATH}", file=sys.stderr)
        print("", file=sys.stderr)
        print("💡 To configure your agent, run:", file=sys.stderr)
        print("   python slack_interface.py config --set-agent nova", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"🤖 Available agents: {', '.join(AGENTS.keys())}", file=sys.stderr)
        sys.exit(1)
    
    if agent_id not in AGENTS:
        print(f"❌ ERROR: Invalid agent '{agent_id}' in config!", file=sys.stderr)
        print("", file=sys.stderr)
        print(f"💡 Valid agents: {', '.join(AGENTS.keys())}", file=sys.stderr)
        print("", file=sys.stderr)
        print("💡 To fix, run:", file=sys.stderr)
        print("   python slack_interface.py config --set-agent nova", file=sys.stderr)
        sys.exit(1)
    
    return AGENTS[agent_id]


def read_file(path: Path) -> str:
    """Read file content or return empty string."""
    return path.read_text() if path.exists() else ""


def build_prompt(agent: dict, task: str = "") -> str:
    """Build the prompt for an agent from their spec and memory."""
    
    spec = read_file(REPO_ROOT / "agent-docs" / agent["spec"])
    memory = read_file(REPO_ROOT / "memory" / f"{agent['name'].lower()}_memory.md")
    prd = read_file(REPO_ROOT / "agent-docs" / "PRD.md")
    protocol = read_file(REPO_ROOT / "agent-docs" / "AGENT_PROTOCOL.md")
    slack_docs = read_file(REPO_ROOT / "agent-docs" / "SLACK_INTERFACE.md")
    
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

## Slack Interface Documentation

{slack_docs}

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

## Headless Mode

You are running in **headless CLI mode** - there is no human at the terminal.

**Communicate via Slack only** using `python slack_interface.py`:
- `python slack_interface.py read -l 50` - Read recent messages
- `python slack_interface.py say "message"` - Post updates

**Workflow:**
1. Read Slack for context
2. Do your work
3. Post updates to Slack
4. Commit changes to git
5. Update your memory file (`memory/{agent['name'].lower()}_memory.md`)
"""


def run_agent(agent: dict, task: str = "") -> None:
    """Run Claude Code for a single agent in headless autonomous mode."""
    
    print(f"\n{'='*60}")
    print(f"{agent['emoji']} Starting {agent['name']} ({agent['role']})")
    print(f"{'='*60}\n")
    
    prompt = build_prompt(agent, task)
    
    # Run Claude Code CLI
    # -p: Print mode (non-interactive)
    try:
        subprocess.run(
            ["claude", "-p", prompt],
            cwd=str(REPO_ROOT),
        )
    except FileNotFoundError:
        print("❌ Claude CLI not found!")
        print("")
        print("Claude CLI is REQUIRED to run agents.")
        print("Please install Claude Code CLI first.")
        sys.exit(1)
    
    print(f"\n✅ {agent['name']} completed\n")


def run_capability_tests() -> bool:
    """
    Run all capability tests and report results.
    
    Returns:
        True if all tests pass, False otherwise
    """
    print("\n" + "=" * 60)
    print("🧪 CAPABILITY TESTS")
    print("=" * 60)
    
    results = {}
    all_passed = True
    
    # Test 1: Config file
    print("\n📋 Test 1: Configuration File")
    config = load_config()
    if config.get("default_agent"):
        print(f"   ✅ Agent configured: {config.get('default_agent')}")
        results["config"] = True
    else:
        print("   ❌ No agent configured")
        results["config"] = False
        all_passed = False
    
    if config.get("default_channel"):
        print(f"   ✅ Channel configured: {config.get('default_channel')}")
    else:
        print("   ⚠️  No default channel configured")
    
    # Test 2: GitHub CLI
    print("\n📋 Test 2: GitHub CLI")
    if shutil.which("gh"):
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("   ✅ GitHub CLI authenticated")
                results["github"] = True
            else:
                print("   ❌ GitHub CLI not authenticated")
                results["github"] = False
                all_passed = False
        except Exception as e:
            print(f"   ❌ GitHub test error: {e}")
            results["github"] = False
            all_passed = False
    else:
        print("   ❌ GitHub CLI (gh) not installed")
        results["github"] = False
        all_passed = False
    
    # Test 3: Claude CLI (MANDATORY)
    print("\n📋 Test 3: Claude CLI (REQUIRED)")
    if shutil.which("claude"):
        print("   ✅ Claude CLI installed")
        results["claude"] = True
    else:
        print("   ❌ Claude CLI not installed")
        print("   ⚠️  Claude CLI is REQUIRED to run agents")
        results["claude"] = False
        all_passed = False
    
    # Test 4: Project Files
    print("\n📋 Test 4: Project Files")
    required_files = [
        "slack_interface.py",
        "agent-docs/ONBOARDING.md",
        "agent-docs/AGENT_PROTOCOL.md",
        "agent-docs/SLACK_INTERFACE.md",
        "memory",
    ]
    files_ok = True
    for f in required_files:
        path = REPO_ROOT / f
        if path.exists():
            print(f"   ✅ {f}")
        else:
            print(f"   ❌ {f} missing")
            files_ok = False
            all_passed = False
    results["files"] = files_ok
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test, passed in results.items():
        if passed is True:
            status = "✅ PASS"
        elif passed is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"   {test:12} {status}")
    
    print()
    if all_passed:
        print("🎉 All tests passed! Agent is ready to work.")
    else:
        print("⚠️  Some tests failed. Please fix issues before running agent.")
    print("=" * 60 + "\n")
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description='Agent Team Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python orchestrator.py                    Run configured agent
  python orchestrator.py --task "Do X"      Run with specific task
  python orchestrator.py --list             List all agents
  python orchestrator.py --test             Run capability tests

Configuration:
  Agent identity is read from ~/.agent_settings.json
  Set with: python slack_interface.py config --set-agent nova
        """
    )
    parser.add_argument("--task", "-t", default="", help="Specific task for the agent")
    parser.add_argument("--list", "-l", action="store_true", help="List all available agents")
    parser.add_argument("--test", action="store_true", help="Run capability tests")
    
    args = parser.parse_args()
    
    if args.test:
        success = run_capability_tests()
        sys.exit(0 if success else 1)
    
    if args.list:
        print("\n📋 Available Agents:\n")
        for agent_id, agent in AGENTS.items():
            print(f"  {agent['emoji']} {agent['name']:8} - {agent['role']}")
        print()
        
        # Show current config
        config = load_config()
        current = config.get("default_agent", "")
        if current:
            print(f"📌 Currently configured: {current}")
        else:
            print("⚠️  No agent configured. Run: python slack_interface.py config --set-agent <name>")
        print()
        return
    
    # Get agent from config (will exit if not configured)
    agent = get_agent_from_config()
    
    # Show which agent we're running
    config = load_config()
    print(f"\n🔧 Config: {CONFIG_PATH}")
    print(f"🤖 Agent: {agent['name']} ({agent['role']})")
    if config.get("default_channel"):
        print(f"📢 Channel: {config.get('default_channel')}")
    
    # Run the agent
    run_agent(agent, args.task)


if __name__ == "__main__":
    main()