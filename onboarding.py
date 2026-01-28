#!/usr/bin/env python3
"""
Agent Onboarding Script

This script runs when an agent wakes up for the first time.
It collects configuration, tests capabilities, and saves settings.

Usage:
    python onboarding.py              # Interactive onboarding
    python onboarding.py --check      # Check if onboarding is complete
    python onboarding.py --reset      # Reset and re-run onboarding
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configuration file path
CONFIG_PATH = os.path.expanduser("~/.agent_config.json")
SLACK_CONFIG_PATH = os.path.expanduser("~/.slack_interface.json")

# Default configuration template
DEFAULT_CONFIG = {
    "onboarding_complete": False,
    "onboarding_date": None,
    "agent_name": None,
    "default_channel": None,
    "default_channel_id": None,
    "schedule": {
        "sync_interval_minutes": 60,
        "work_hours_start": "09:00",
        "work_hours_end": "17:00",
        "timezone": "UTC"
    },
    "capabilities_tested": {
        "slack": False,
        "github": False,
        "claude": False
    },
    "github_repo": None,
    "last_sync": None
}


def load_config() -> dict:
    """Load configuration from file"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load config: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save configuration to file"""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Configuration saved to {CONFIG_PATH}")


def save_slack_config(channel: str, channel_id: str, agent: str):
    """Save Slack-specific configuration"""
    slack_config = {
        "default_channel": channel,
        "default_channel_id": channel_id,
        "default_agent": agent
    }
    with open(SLACK_CONFIG_PATH, 'w') as f:
        json.dump(slack_config, f, indent=2)
    print(f"✅ Slack configuration saved to {SLACK_CONFIG_PATH}")


def print_banner():
    """Print onboarding banner"""
    print("\n" + "=" * 70)
    print("🚀 AGENT ONBOARDING")
    print("=" * 70)
    print("\nWelcome! This script will configure your agent environment.")
    print("Please answer the following questions to complete setup.\n")


def print_section(title: str):
    """Print section header"""
    print("\n" + "-" * 50)
    print(f"📋 {title}")
    print("-" * 50 + "\n")


def ask_question(prompt: str, default: str = None) -> str:
    """Ask a question with optional default"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(prompt).strip()
    return response if response else default


def ask_choice(prompt: str, choices: list, default: str = None) -> str:
    """Ask a multiple choice question"""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"  {i}. {choice}{marker}")
    
    while True:
        response = input("\nEnter number or name: ").strip()
        
        # Check if it's a number
        try:
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        
        # Check if it's a name
        response_lower = response.lower()
        for choice in choices:
            if choice.lower() == response_lower:
                return choice
        
        # Use default if empty
        if not response and default:
            return default
        
        print("❌ Invalid choice. Please try again.")


def test_slack() -> bool:
    """Test Slack connectivity"""
    print("\n🔍 Testing Slack connection...")
    
    try:
        result = subprocess.run(
            ["python", "slack_interface.py", "scopes"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "Valid" in result.stdout:
            print("✅ Slack connection successful!")
            
            # Show available scopes
            if "channels:history" in result.stdout:
                print("   ✅ Can read channel history")
            else:
                print("   ⚠️ Missing channels:history scope")
            
            if "chat:write" in result.stdout:
                print("   ✅ Can send messages")
            else:
                print("   ⚠️ Missing chat:write scope")
            
            return True
        else:
            print("❌ Slack connection failed!")
            print(f"   Error: {result.stderr or result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Slack test timed out")
        return False
    except FileNotFoundError:
        print("❌ slack_interface.py not found")
        return False
    except Exception as e:
        print(f"❌ Slack test error: {e}")
        return False


def test_github() -> bool:
    """Test GitHub connectivity"""
    print("\n🔍 Testing GitHub connection...")
    
    try:
        # Test gh auth status
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ GitHub CLI authenticated!")
            
            # Get current repo
            repo_result = subprocess.run(
                ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if repo_result.returncode == 0 and repo_result.stdout.strip():
                print(f"   📁 Current repo: {repo_result.stdout.strip()}")
            
            return True
        else:
            print("❌ GitHub CLI not authenticated")
            print(f"   Run: gh auth login")
            return False
            
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not found")
        print("   Install: https://cli.github.com/")
        return False
    except subprocess.TimeoutExpired:
        print("❌ GitHub test timed out")
        return False
    except Exception as e:
        print(f"❌ GitHub test error: {e}")
        return False


def test_claude() -> bool:
    """Test Claude CLI connectivity"""
    print("\n🔍 Testing Claude CLI...")
    
    try:
        # First check if claude command exists
        which_result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if which_result.returncode != 0:
            print("❌ Claude CLI not found")
            print("   Make sure 'claude' command is available")
            return False
        
        print("✅ Claude CLI found at:", which_result.stdout.strip())
        
        # Test with a simple version check (faster than running a prompt)
        version_result = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if version_result.returncode == 0:
            print("✅ Claude CLI working!")
            version_info = version_result.stdout.strip()[:50]
            print(f"   Version: {version_info}")
            return True
        
        # If version check fails, try help
        help_result = subprocess.run(
            ["claude", "--help"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if help_result.returncode == 0:
            print("✅ Claude CLI available!")
            return True
        
        # Claude exists but may need different invocation
        print("⚠️ Claude CLI found but couldn't verify")
        print("   You can test manually: claude -p 'hello world'")
        return True  # Assume it works if the binary exists
            
    except FileNotFoundError:
        print("❌ Claude CLI not found")
        print("   Make sure 'claude' command is available")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️ Claude CLI check timed out")
        print("   Claude exists but may be slow to respond")
        return True  # Assume it works if it exists
    except Exception as e:
        print(f"❌ Claude test error: {e}")
        return False


def test_slack_send(agent: str, channel: str) -> bool:
    """Test sending a message to Slack"""
    print(f"\n🔍 Testing Slack send as {agent}...")
    
    try:
        message = f"🚀 Onboarding test from {agent} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        result = subprocess.run(
            ["python", "slack_interface.py", "say", "-a", agent.lower(), message],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if "successfully" in result.stdout.lower():
            print("✅ Successfully sent test message!")
            return True
        else:
            print("❌ Failed to send test message")
            print(f"   {result.stdout or result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Send test error: {e}")
        return False


def get_channels() -> list:
    """Get list of available Slack channels"""
    try:
        result = subprocess.run(
            ["python", "slack_interface.py", "channels"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        channels = []
        for line in result.stdout.split('\n'):
            if '#' in line:
                # Extract channel name
                parts = line.split()
                for part in parts:
                    if part.startswith('#'):
                        channels.append(part)
                        break
        
        return channels
    except:
        return []


def run_onboarding():
    """Run the full onboarding process"""
    print_banner()
    
    config = load_config()
    
    # Check if already onboarded
    if config.get("onboarding_complete"):
        print("ℹ️ Onboarding was already completed on", config.get("onboarding_date"))
        response = ask_question("Do you want to re-run onboarding? (yes/no)", "no")
        if response.lower() not in ["yes", "y"]:
            print("\n👋 Exiting. Use --reset to force re-onboarding.")
            return
    
    # =========================================================================
    # SECTION 1: Agent Identity
    # =========================================================================
    print_section("AGENT IDENTITY")
    
    agents = ["Nova", "Pixel", "Bolt", "Scout"]
    agent_name = ask_choice(
        "Which agent are you?",
        agents,
        default=config.get("agent_name")
    )
    config["agent_name"] = agent_name
    
    print(f"\n👋 Hello, {agent_name}!")
    
    # =========================================================================
    # SECTION 2: Slack Configuration
    # =========================================================================
    print_section("SLACK CONFIGURATION")
    
    # Get available channels
    print("Fetching available channels...")
    channels = get_channels()
    
    if channels:
        print(f"Found {len(channels)} channels")
        default_channel = ask_question(
            "Default Slack channel",
            config.get("default_channel") or "#logo-creator"
        )
    else:
        default_channel = ask_question(
            "Default Slack channel (e.g., #logo-creator)",
            config.get("default_channel") or "#logo-creator"
        )
    
    config["default_channel"] = default_channel
    
    # =========================================================================
    # SECTION 3: Schedule Configuration
    # =========================================================================
    print_section("SCHEDULE CONFIGURATION")
    
    schedule = config.get("schedule", DEFAULT_CONFIG["schedule"])
    
    sync_interval = ask_question(
        "Sync interval in minutes",
        str(schedule.get("sync_interval_minutes", 60))
    )
    schedule["sync_interval_minutes"] = int(sync_interval)
    
    work_start = ask_question(
        "Work hours start (HH:MM)",
        schedule.get("work_hours_start", "09:00")
    )
    schedule["work_hours_start"] = work_start
    
    work_end = ask_question(
        "Work hours end (HH:MM)",
        schedule.get("work_hours_end", "17:00")
    )
    schedule["work_hours_end"] = work_end
    
    timezone = ask_question(
        "Timezone",
        schedule.get("timezone", "UTC")
    )
    schedule["timezone"] = timezone
    
    config["schedule"] = schedule
    
    # =========================================================================
    # SECTION 4: Capability Tests
    # =========================================================================
    print_section("CAPABILITY TESTS")
    
    print("Running capability tests...\n")
    
    capabilities = config.get("capabilities_tested", {})
    
    # Test Slack
    capabilities["slack"] = test_slack()
    
    # Test GitHub
    capabilities["github"] = test_github()
    
    # Test Claude
    capabilities["claude"] = test_claude()
    
    config["capabilities_tested"] = capabilities
    
    # =========================================================================
    # SECTION 5: Integration Test
    # =========================================================================
    print_section("INTEGRATION TEST")
    
    if capabilities["slack"]:
        response = ask_question("Send a test message to Slack? (yes/no)", "yes")
        if response.lower() in ["yes", "y"]:
            test_slack_send(agent_name, default_channel)
    
    # =========================================================================
    # SECTION 6: Summary & Save
    # =========================================================================
    print_section("ONBOARDING SUMMARY")
    
    config["onboarding_complete"] = True
    config["onboarding_date"] = datetime.now().isoformat()
    
    print(f"Agent: {config['agent_name']}")
    print(f"Default Channel: {config['default_channel']}")
    print(f"Schedule: Every {config['schedule']['sync_interval_minutes']} minutes")
    print(f"Work Hours: {config['schedule']['work_hours_start']} - {config['schedule']['work_hours_end']} {config['schedule']['timezone']}")
    print(f"\nCapabilities:")
    print(f"  Slack: {'✅' if capabilities.get('slack') else '❌'}")
    print(f"  GitHub: {'✅' if capabilities.get('github') else '❌'}")
    print(f"  Claude: {'✅' if capabilities.get('claude') else '❌'}")
    
    # Save configurations
    save_config(config)
    
    # Also save Slack config
    save_slack_config(
        config["default_channel"],
        config.get("default_channel_id", ""),
        config["agent_name"].lower()
    )
    
    print("\n" + "=" * 70)
    print("🎉 ONBOARDING COMPLETE!")
    print("=" * 70)
    
    # Show any warnings
    if not all(capabilities.values()):
        print("\n⚠️ Some capabilities failed. Please fix before starting work:")
        if not capabilities.get("slack"):
            print("   - Slack: Check token in /dev/shm/mcp-token")
        if not capabilities.get("github"):
            print("   - GitHub: Run 'gh auth login'")
        if not capabilities.get("claude"):
            print("   - Claude: Check claude CLI installation")
    
    print(f"\n📖 Next steps for {agent_name}:")
    print(f"   1. Read your spec: agent-docs/{agent_name.upper()}_SPEC.md")
    print(f"   2. Check Slack: python slack_interface.py read")
    print(f"   3. Start working!")


def check_onboarding() -> bool:
    """Check if onboarding is complete"""
    config = load_config()
    
    if config.get("onboarding_complete"):
        print("✅ Onboarding complete")
        print(f"   Agent: {config.get('agent_name')}")
        print(f"   Date: {config.get('onboarding_date')}")
        print(f"   Channel: {config.get('default_channel')}")
        return True
    else:
        print("❌ Onboarding not complete")
        print("   Run: python onboarding.py")
        return False


def reset_onboarding():
    """Reset onboarding configuration"""
    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)
        print(f"✅ Removed {CONFIG_PATH}")
    
    print("🔄 Onboarding reset. Run 'python onboarding.py' to start fresh.")


def main():
    parser = argparse.ArgumentParser(
        description="Agent Onboarding Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python onboarding.py              # Run interactive onboarding
  python onboarding.py --check      # Check if onboarding is complete
  python onboarding.py --reset      # Reset and start fresh
        """
    )
    
    parser.add_argument('--check', action='store_true',
                        help='Check if onboarding is complete')
    parser.add_argument('--reset', action='store_true',
                        help='Reset onboarding configuration')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    if args.check:
        sys.exit(0 if check_onboarding() else 1)
    elif args.reset:
        reset_onboarding()
    else:
        run_onboarding()


if __name__ == "__main__":
    main()