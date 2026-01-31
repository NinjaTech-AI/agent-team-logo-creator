"""
Agent Team Orchestrator

Simple orchestrator that runs Claude Code for the configured agent.
Agent identity is read from ~/.agent_settings.json config file.
Agent behavior is defined by their markdown spec files in agent-docs/.

Usage:
    python orchestrator.py                    # Run work + monitor in parallel
    python orchestrator.py --task "Do X"      # Run single task
    python orchestrator.py --list             # List all agents
    python orchestrator.py --test             # Run capability tests

When run without --task, starts two parallel processes:
  1. Work mode: Claude agent does work (check Slack, sync, update memory)
  2. Monitor mode: Watches for Slack mentions and responds (45s + 5s jitter)
"""

import subprocess
import argparse
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Import centralized agent configuration
from agents_config import AGENTS

REPO_ROOT = Path(__file__).parent
CONFIG_PATH = Path.home() / ".agent_settings.json"
LOCK_FILE = REPO_ROOT / ".orchestrator.lock"


def check_single_instance():
    """
    Ensure only one instance of the orchestrator is running.
    Uses a lock file with PID to detect and prevent duplicate instances.
    
    Raises:
        SystemExit if another instance is already running
    """
    import os
    
    current_pid = os.getpid()
    
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_data = json.load(f)
            
            old_pid = lock_data.get('pid')
            old_agent = lock_data.get('agent', 'unknown')
            old_started = lock_data.get('started', 'unknown')
            
            # Check if the old process is still running
            if old_pid:
                try:
                    # Send signal 0 to check if process exists
                    os.kill(old_pid, 0)
                    # Process exists - another instance is running
                    print("=" * 70, file=sys.stderr)
                    print("ERROR: Another orchestrator instance is already running!", file=sys.stderr)
                    print("=" * 70, file=sys.stderr)
                    print("", file=sys.stderr)
                    print(f"   Existing instance:", file=sys.stderr)
                    print(f"   - PID: {old_pid}", file=sys.stderr)
                    print(f"   - Agent: {old_agent}", file=sys.stderr)
                    print(f"   - Started: {old_started}", file=sys.stderr)
                    print("", file=sys.stderr)
                    print("   To stop the existing instance:", file=sys.stderr)
                    print(f"   - kill {old_pid}", file=sys.stderr)
                    print("   - Or: pkill -f 'orchestrator.py'", file=sys.stderr)
                    print("", file=sys.stderr)
                    print("   To force remove the lock (if process is stuck):", file=sys.stderr)
                    print(f"   - rm {LOCK_FILE}", file=sys.stderr)
                    print("=" * 70, file=sys.stderr)
                    sys.exit(1)
                except OSError:
                    # Process doesn't exist - stale lock file, we can proceed
                    print(f"Removing stale lock file (PID {old_pid} no longer running)")
        except (json.JSONDecodeError, IOError, KeyError):
            # Corrupted lock file, remove it
            print("Removing corrupted lock file")
    
    # Create/update lock file with current process info
    lock_data = {
        'pid': current_pid,
        'agent': None,  # Will be updated after agent is determined
        'started': datetime.now().isoformat(),
    }
    
    try:
        with open(LOCK_FILE, 'w') as f:
            json.dump(lock_data, f)
    except IOError as e:
        print(f"Warning: Could not create lock file: {e}", file=sys.stderr)


def update_lock_file(agent_name: str):
    """Update the lock file with the agent name after it's determined."""
    if LOCK_FILE.exists():
        try:
            with open(LOCK_FILE, 'r') as f:
                lock_data = json.load(f)
            lock_data['agent'] = agent_name
            with open(LOCK_FILE, 'w') as f:
                json.dump(lock_data, f)
        except (json.JSONDecodeError, IOError):
            pass


def remove_lock_file():
    """Remove the lock file when orchestrator exits."""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except IOError:
        pass


def load_config() -> dict:
    """Load agent configuration from ~/.agent_settings.json"""
    if not CONFIG_PATH.exists():
        return {}
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read config: {e}", file=sys.stderr)
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


def build_prompt(agent: dict, task: str = "", use_references: bool = True) -> str:
    """Build the prompt for an agent from their spec and memory.
    
    Args:
        agent: Agent configuration dict
        task: Optional specific task
        use_references: If True, use file references instead of embedding content (saves ~100KB)
    """
    
    # Get default channel from config
    config = load_config()
    channel = config.get("default_channel_name", config.get("default_channel", "#logo-creator"))
    default_task = f"Check Slack {channel}, sync with team, do your work, update your memory file."
    
    if use_references:
        # OPTIMIZED: Use file references instead of embedding content
        # This reduces prompt size from ~100KB to ~3KB
        memory = read_file(REPO_ROOT / "memory" / f"{agent['name'].lower()}_memory.md")
        prd = read_file(REPO_ROOT / "agent-docs" / "PRD.md")
        
        return f"""# You are {agent['name']} {agent['emoji']}

## Your Identity
- **Name:** {agent['name']}
- **Role:** {agent['role']}
- **Emoji:** {agent['emoji']}

---

## Documentation Files (READ THESE FIRST)

Before starting work, read these files for full context:

1. **Your Specification:** `cat agent-docs/{agent['spec']}`
2. **Architecture:** `cat agent-docs/ARCHITECTURE.md`
3. **Communication Protocol:** `cat agent-docs/AGENT_PROTOCOL.md`
4. **Slack Interface Docs:** `cat agent-docs/SLACK_INTERFACE.md`
5. **Onboarding Guide:** `cat agent-docs/ONBOARDING.md`

---

## Current PRD

{prd if prd else "No PRD yet. Nova needs to interview the human (Babak/Arash) to create it. See agent-docs/PRD.md"}

---

## Your Memory

{memory if memory else "No previous memory. This is your first session."}

---

## Quick Reference

**Slack Commands:**
- `python slack_interface.py read -l 50` - Read recent messages
- `python slack_interface.py say "message"` - Post updates
- `python slack_interface.py config` - Check configuration

**GitHub Commands:**
- `gh issue list` - List issues
- `gh issue create --title "..." --body "..."` - Create issue

---

## Headless Mode

You are running in **headless CLI mode** - there is no human at the terminal.

**Communicate via Slack only** using `python slack_interface.py`.

**Workflow:**
1. Read your spec file first: `cat agent-docs/{agent['spec']}`
2. Read Slack for context
3. Do your work
4. Post updates to Slack
5. Commit changes to git
6. Update your memory file (`memory/{agent['name'].lower()}_memory.md`)

---

## Current Task

{task if task else default_task}
"""
    else:
        # LEGACY: Embed full content (large prompt ~100KB)
        spec = read_file(REPO_ROOT / "agent-docs" / agent["spec"])
        memory = read_file(REPO_ROOT / "memory" / f"{agent['name'].lower()}_memory.md")
        prd = read_file(REPO_ROOT / "agent-docs" / "PRD.md")
        protocol = read_file(REPO_ROOT / "agent-docs" / "AGENT_PROTOCOL.md")
        slack_docs = read_file(REPO_ROOT / "agent-docs" / "SLACK_INTERFACE.md")
        architecture = read_file(REPO_ROOT / "agent-docs" / "ARCHITECTURE.md")
        
        return f"""# You are {agent['name']} {agent['emoji']}

## Your Identity
- **Name:** {agent['name']}
- **Role:** {agent['role']}
- **Emoji:** {agent['emoji']}

---

## Your Specification

{spec}

---

## Architecture

{architecture}

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

---

## Current Task

{task if task else default_task}
"""


def run_agent(agent: dict, task: str = "") -> None:
    """Run Claude Code for a single agent in headless autonomous mode."""
    
    print(f"\n{'='*60}")
    print(f"{agent['emoji']} Starting {agent['name']} ({agent['role']})")
    print(f"{'='*60}\n")
    
    prompt = build_prompt(agent, task)
    
    # Run Claude Code CLI
    # -p: Print mode (non-interactive)
    # Permissions are configured in ~/.claude/settings.json
    # Timeout: 15 minutes (900 seconds) to allow for complex tasks
    try:
        subprocess.run(
            [str(REPO_ROOT / "claude-wrapper.sh"), "-p", prompt],
            cwd=str(REPO_ROOT),
            timeout=900,  # 15 minutes
        )
    except subprocess.TimeoutExpired:
        print("⏰ Claude CLI timed out after 15 minutes")
        print("")
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
    
    # Check for existing instance BEFORE doing anything else
    check_single_instance()
    
    # Register cleanup handler to remove lock file on exit
    import atexit
    import signal
    
    atexit.register(remove_lock_file)
    
    # Also handle SIGTERM and SIGINT to clean up lock file
    def signal_handler(signum, frame):
        remove_lock_file()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Get agent from config (will exit if not configured)
    agent = get_agent_from_config()
    
    # Update lock file with agent name
    update_lock_file(agent['name'])
    
    # Show which agent we're running
    config = load_config()
    print(f"\n🔧 Config: {CONFIG_PATH}")
    print(f"🤖 Agent: {agent['name']} ({agent['role']})")
    if config.get("default_channel"):
        print(f"📢 Channel: {config.get('default_channel')}")
    
    # If a specific task is provided, run single agent
    if args.task:
        run_agent(agent, args.task)
    else:
        # No task specified - run work + monitor in parallel (monitor only for Nova)
        import multiprocessing
        
        work_task = "Check Slack, sync with team, do your work, update your memory file."
        
        def run_monitor():
            """Run monitor.py in a subprocess."""
            subprocess.run(
                ["python", "monitor.py"],
                cwd=str(REPO_ROOT),
            )
        
        # Only Nova gets the monitor process
        is_nova = agent["name"].lower() == "nova"
        
        if is_nova:
            print(f"\n🚀 Starting two parallel processes...")
            print(f"   Process 1: Work mode (Claude agent)")
            print(f"   Process 2: Monitor mode (Slack watcher)")
            print(f"   Press Ctrl+C to stop\n")
        else:
            print(f"\n🚀 Starting work process...")
            print(f"   Process 1: Work mode (Claude agent)")
            print(f"   ℹ️  Monitor mode is only enabled for Nova (PM)")
            print(f"   Press Ctrl+C to stop\n")
        
        p1 = multiprocessing.Process(target=run_agent, args=(agent, work_task))
        
        processes = [p1]
        
        if is_nova:
            p2 = multiprocessing.Process(target=run_monitor)
            processes.append(p2)
        
        try:
            for p in processes:
                p.start()
            
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            print("\n\n👋 Stopping processes...")
            for p in processes:
                p.terminate()
            for p in processes:
                p.join()
        
        if is_nova:
            print(f"\n✅ Both processes completed")
        else:
            print(f"\n✅ Work process completed")


if __name__ == "__main__":
    main()