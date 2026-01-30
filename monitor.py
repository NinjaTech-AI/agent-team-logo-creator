#!/usr/bin/env python3
"""
Agent Monitor - Watches Slack for mentions and triggers agent responses.

This script runs independently and only invokes Claude CLI when the agent
is mentioned in Slack. It polls every 10 seconds and tracks seen messages.

Usage:
    python monitor.py              # Run with configured agent
    python monitor.py --agent nova # Run as specific agent
"""

import subprocess
import time
import json
import sys
import re
from pathlib import Path

# Configuration
REPO_ROOT = Path(__file__).parent
CONFIG_PATH = Path.home() / ".agent_settings.json"
POLL_INTERVAL = 45  # base seconds
POLL_JITTER = 5  # random jitter seconds
SEEN_MESSAGES_FILE = REPO_ROOT / ".seen_messages.json"

# Agent configuration
AGENTS = {
    "nova": {"name": "Nova", "role": "Product Manager", "emoji": "🌟", "mentions": ["nova", "Nova", "@nova"]},
    "pixel": {"name": "Pixel", "role": "UX Designer", "emoji": "🎨", "mentions": ["pixel", "Pixel", "@pixel"]},
    "bolt": {"name": "Bolt", "role": "Full-Stack Developer", "emoji": "⚡", "mentions": ["bolt", "Bolt", "@bolt"]},
    "scout": {"name": "Scout", "role": "QA Engineer", "emoji": "🔍", "mentions": ["scout", "Scout", "@scout"]},
}


def load_config() -> dict:
    """Load agent configuration from ~/.agent_settings.json"""
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
    except Exception as e:
        print(f"⚠️ Warning: Could not read config: {e}", file=sys.stderr)
    return {}


def load_seen_messages() -> set:
    """Load previously seen message timestamps."""
    try:
        if SEEN_MESSAGES_FILE.exists():
            data = json.loads(SEEN_MESSAGES_FILE.read_text())
            return set(data.get("seen", []))
    except Exception:
        pass
    return set()


def save_seen_messages(seen: set):
    """Save seen message timestamps."""
    try:
        # Keep only last 100 messages to prevent file from growing too large
        recent = sorted(seen)[-100:]
        SEEN_MESSAGES_FILE.write_text(json.dumps({"seen": recent}))
    except Exception as e:
        print(f"⚠️ Warning: Could not save seen messages: {e}", file=sys.stderr)


def get_last_messages(limit: int = 10) -> list:
    """Get recent messages from Slack using slack_interface.py"""
    try:
        result = subprocess.run(
            ["python", "slack_interface.py", "read", "-l", str(limit)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"⚠️ Error reading Slack: {result.stderr}", file=sys.stderr)
            return []
        
        # Parse the output to extract messages
        messages = []
        output = result.stdout
        
        # Extract message blocks - look for timestamp pattern in header
        # Format: ┌─ Username [YYYY-MM-DD HH:MM:SS]
        lines = output.split('\n')
        current_msg = None
        
        for line in lines:
            # Check for message header
            if line.startswith('┌─ '):
                if current_msg:
                    messages.append(current_msg)
                
                # Parse header: ┌─ Username [2026-01-30 03:11:03]
                match = re.match(r'┌─ (.+?) \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                if match:
                    current_msg = {
                        "user": match.group(1),
                        "timestamp": match.group(2),
                        "text": ""
                    }
                else:
                    current_msg = None
            elif line.startswith('│  ') and current_msg:
                # Message content line
                current_msg["text"] += line[3:] + "\n"
            elif line.startswith('└') and current_msg:
                # End of message
                current_msg["text"] = current_msg["text"].strip()
                messages.append(current_msg)
                current_msg = None
        
        return messages
        
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout reading Slack", file=sys.stderr)
        return []
    except Exception as e:
        print(f"⚠️ Error: {e}", file=sys.stderr)
        return []


def check_for_mention(message: dict, agent: dict) -> bool:
    """Check if message mentions the agent."""
    text = message.get("text", "").lower()
    user = message.get("user", "").lower()
    
    # Don't respond to own messages
    if agent["name"].lower() in user.lower():
        return False
    
    # Check for mentions
    for mention in agent["mentions"]:
        if mention.lower() in text:
            return True
    
    return False


def run_agent_response(agent: dict, message: dict):
    """Generate a response using Claude and post it directly to Slack."""
    
    agent_name = agent["name"]
    agent_role = agent["role"]
    agent_emoji = agent["emoji"]
    
    # Build a focused task prompt - ask Claude to generate ONLY the response text
    task = f"""Someone mentioned you in Slack! Here's the message:

From: {message.get('user', 'Unknown')}
Time: {message.get('timestamp', 'Unknown')}
Message: {message.get('text', '')}

Generate a helpful, friendly response as {agent_name} the {agent_role}.
Keep it concise (1-3 sentences).
Do NOT include any commands or code blocks.
Do NOT ask for permission or confirmation.
Just output the response text that should be posted to Slack.
Sign off with your emoji {agent_emoji}"""

    # Read agent spec for context
    spec_file = REPO_ROOT / "agent-docs" / f"{agent_name.upper()}_SPEC.md"
    spec = ""
    if spec_file.exists():
        spec = spec_file.read_text()[:1500]  # First 1500 chars for context
    
    prompt = f"""# You are {agent_name} {agent_emoji}

## Identity
- Name: {agent_name}
- Role: {agent_role}

## Brief Context
{spec[:800] if spec else "You are an AI agent on a development team."}

## Task
{task}

OUTPUT ONLY THE RESPONSE TEXT - NO COMMANDS, NO EXPLANATIONS:"""

    print(f"\n{agent_emoji} Generating response to {message.get('user', 'Unknown')}...", flush=True)
    
    try:
        # Get response from Claude
        result = subprocess.run(
            ["claude", "-p", prompt],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        response_text = result.stdout.strip()
        
        if not response_text:
            response_text = f"Hey! {agent_emoji} I'm {agent_name}, the {agent_role}. I'm online and ready to help!"
        
        # Clean up response - remove any markdown code blocks or command artifacts
        response_text = response_text.replace("```", "").strip()
        if response_text.startswith("bash") or response_text.startswith("python"):
            response_text = f"Hey! {agent_emoji} I'm {agent_name}, online and ready to help!"
        
        # Limit response length
        if len(response_text) > 500:
            response_text = response_text[:500] + "..."
        
        print(f"📝 Response: {response_text[:100]}...", flush=True)
        
        # Post directly to Slack using slack_interface.py
        slack_result = subprocess.run(
            ["python", "slack_interface.py", "say", response_text],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if slack_result.returncode == 0:
            print(f"✅ Response posted to Slack!", flush=True)
        else:
            print(f"⚠️ Slack error: {slack_result.stderr}", flush=True)
            
    except subprocess.TimeoutExpired:
        print("⚠️ Response timed out", flush=True)
    except Exception as e:
        print(f"⚠️ Error: {e}", flush=True)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Monitor - Watch Slack for mentions')
    parser.add_argument('--agent', '-a', help='Agent to run as (default: from config)')
    parser.add_argument('--interval', '-i', type=int, default=POLL_INTERVAL, help='Poll interval in seconds')
    args = parser.parse_args()
    
    # Get agent from args or config
    config = load_config()
    agent_id = args.agent or config.get("default_agent", "").lower()
    
    if not agent_id or agent_id not in AGENTS:
        print("❌ No valid agent configured!", file=sys.stderr)
        print(f"Available agents: {', '.join(AGENTS.keys())}", file=sys.stderr)
        print("Set with: python slack_interface.py config --set-agent <name>", file=sys.stderr)
        sys.exit(1)
    
    agent = AGENTS[agent_id]
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  {agent['emoji']} {agent['name']} Monitor - Watching for Slack mentions
╠══════════════════════════════════════════════════════════════╣
║  Agent: {agent['name']} ({agent['role']})
║  Polling: Every {args.interval}s (+{POLL_JITTER}s jitter)
║  Mentions: {', '.join(agent['mentions'])}
╚══════════════════════════════════════════════════════════════╝
""", flush=True)
    
    seen_messages = load_seen_messages()
    print(f"📡 Starting monitor loop...", flush=True)
    
    try:
        while True:
            # Get recent messages
            messages = get_last_messages(10)
            print(f"📨 Got {len(messages)} messages", flush=True)
            
            for msg in messages:
                # Create unique ID from timestamp
                msg_id = msg.get("timestamp", "")
                
                # Skip if already seen
                if msg_id in seen_messages:
                    continue
                
                # Mark as seen
                seen_messages.add(msg_id)
                
                # Check for mention
                if check_for_mention(msg, agent):
                    print(f"\n📨 New mention detected!")
                    print(f"   From: {msg.get('user', 'Unknown')}")
                    print(f"   Text: {msg.get('text', '')[:100]}...")
                    
                    # Run agent response
                    run_agent_response(agent, msg)
            
            # Save seen messages
            save_seen_messages(seen_messages)
            
            # Wait for next poll (interval + random jitter)
            import random
            jitter = random.uniform(0, POLL_JITTER)
            time.sleep(args.interval + jitter)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped")
        save_seen_messages(seen_messages)


if __name__ == "__main__":
    main()