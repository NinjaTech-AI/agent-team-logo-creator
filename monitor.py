#!/usr/bin/env python3
"""
Agent Monitor - Watches Slack for mentions and triggers agent responses.

This script runs independently and only invokes Claude CLI when the agent
is mentioned in Slack. It polls every 45 seconds and tracks seen messages.

Features:
- Monitors main channel for mentions
- Monitors thread replies to agent's messages
- Batches all messages and sends to Claude in one prompt per cycle
- Exponential backoff on rate limiting

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

# Import centralized agent configuration
from agents_config import AGENTS

# Configuration
REPO_ROOT = Path(__file__).parent
CONFIG_PATH = Path.home() / ".agent_settings.json"
POLL_INTERVAL = 60  # base seconds
POLL_JITTER = 5  # random jitter seconds
MAX_RUNTIME = 60 * 60  # 60 minutes in seconds
SEEN_MESSAGES_FILE = REPO_ROOT / ".seen_messages.json"
AGENT_MESSAGES_FILE = REPO_ROOT / ".agent_messages.json"  # Track agent's own messages for thread monitoring

# Rate limiting configuration
BACKOFF_INITIAL = 60  # Initial backoff: 1 minute
BACKOFF_MAX = 600  # Max backoff: 10 minutes
BACKOFF_MULTIPLIER = 2  # Double the backoff each time


class RateLimitHandler:
    """Handles exponential backoff for rate limiting."""
    
    def __init__(self):
        self.current_backoff = 0
        self.consecutive_rate_limits = 0
        self.last_rate_limit_time = 0
    
    def on_rate_limit(self):
        """Called when a rate limit is encountered."""
        self.consecutive_rate_limits += 1
        self.last_rate_limit_time = time.time()
        
        if self.current_backoff == 0:
            self.current_backoff = BACKOFF_INITIAL
        else:
            self.current_backoff = min(self.current_backoff * BACKOFF_MULTIPLIER, BACKOFF_MAX)
        
        print(f"⚠️ Rate limited! Backing off for {self.current_backoff}s (attempt #{self.consecutive_rate_limits})", flush=True)
        return self.current_backoff
    
    def on_success(self):
        """Called when a request succeeds."""
        if self.consecutive_rate_limits > 0:
            print(f"✅ Rate limit cleared after {self.consecutive_rate_limits} retries", flush=True)
        self.current_backoff = 0
        self.consecutive_rate_limits = 0
    
    def is_backing_off(self) -> bool:
        """Check if we're currently in a backoff period."""
        if self.current_backoff == 0:
            return False
        elapsed = time.time() - self.last_rate_limit_time
        return elapsed < self.current_backoff
    
    def get_remaining_backoff(self) -> float:
        """Get remaining backoff time in seconds."""
        if not self.is_backing_off():
            return 0
        elapsed = time.time() - self.last_rate_limit_time
        return max(0, self.current_backoff - elapsed)


# Global rate limit handler
rate_limiter = RateLimitHandler()


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


def load_agent_messages() -> dict:
    """Load agent's own message timestamps for thread monitoring."""
    try:
        if AGENT_MESSAGES_FILE.exists():
            return json.loads(AGENT_MESSAGES_FILE.read_text())
    except Exception:
        pass
    return {"messages": [], "seen_replies": []}


def save_agent_messages(data: dict):
    """Save agent's message timestamps."""
    try:
        # Keep only last 20 messages to monitor
        data["messages"] = data.get("messages", [])[-20:]
        data["seen_replies"] = data.get("seen_replies", [])[-100:]
        AGENT_MESSAGES_FILE.write_text(json.dumps(data))
    except Exception as e:
        print(f"⚠️ Warning: Could not save agent messages: {e}", file=sys.stderr)


def is_rate_limited(output: str) -> bool:
    """Check if output indicates rate limiting."""
    rate_limit_indicators = [
        "ratelimited",
        "rate_limited", 
        "rate limit",
        "too many requests",
        "429",
    ]
    output_lower = output.lower()
    return any(indicator in output_lower for indicator in rate_limit_indicators)


def get_thread_replies(thread_ts: str) -> tuple[list, bool]:
    """
    Get replies to a specific thread using slack_interface.py.
    
    Returns:
        Tuple of (messages list, was_rate_limited bool)
    """
    try:
        result = subprocess.run(
            ["python", "slack_interface.py", "replies", thread_ts, "-l", "20"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check for rate limiting
        combined_output = result.stdout + result.stderr
        if is_rate_limited(combined_output):
            return [], True
        
        if result.returncode != 0:
            return [], False
        
        # Parse the output to extract messages
        messages = []
        output = result.stdout
        lines = output.split('\n')
        current_msg = None
        
        for line in lines:
            # Check for message header: ┌─ Username [YYYY-MM-DD HH:MM:SS]
            if line.startswith('┌─ '):
                if current_msg:
                    messages.append(current_msg)
                
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
                current_msg["text"] += line[3:] + "\n"
            elif line.startswith('└') and current_msg:
                current_msg["text"] = current_msg["text"].strip()
                messages.append(current_msg)
                current_msg = None
        
        return messages, False
        
    except subprocess.TimeoutExpired:
        return [], False
    except Exception:
        return [], False


def get_last_messages_raw(limit: int = 10) -> tuple[list, bool]:
    """
    Get recent messages from Slack using Python API directly (includes reply_count).
    
    Returns:
        Tuple of (messages list, was_rate_limited bool)
    """
    try:
        # Use Python to get raw message data including reply_count
        code = f'''
import json
import sys
sys.path.insert(0, "{REPO_ROOT}")
from slack_interface import SlackInterface
try:
    slack = SlackInterface()
    messages = slack.get_history(limit={limit})
    # Output as JSON for parsing
    print(json.dumps({{"ok": True, "messages": messages}}))
except Exception as e:
    error_str = str(e).lower()
    if "ratelimit" in error_str or "rate" in error_str:
        print(json.dumps({{"ok": False, "error": "ratelimited"}}))
    else:
        print(json.dumps({{"ok": False, "error": str(e)}}))
'''
        result = subprocess.run(
            ["python", "-c", code],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check for rate limiting in stderr
        if is_rate_limited(result.stderr):
            return [], True
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout.strip())
                if data.get("error") == "ratelimited":
                    return [], True
                if data.get("ok"):
                    return data.get("messages", []), False
            except json.JSONDecodeError:
                pass
        return [], False
    except Exception:
        return [], False


def get_last_messages(limit: int = 10) -> tuple[list, bool]:
    """
    Get recent messages from Slack using slack_interface.py.
    
    Returns:
        Tuple of (messages list, was_rate_limited bool)
    """
    try:
        result = subprocess.run(
            ["python", "slack_interface.py", "read", "-l", str(limit)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check for rate limiting
        combined_output = result.stdout + result.stderr
        if is_rate_limited(combined_output):
            return [], True
        
        if result.returncode != 0:
            print(f"⚠️ Error reading Slack: {result.stderr}", file=sys.stderr)
            return [], False
        
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
        
        return messages, False
        
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout reading Slack", file=sys.stderr)
        return [], False
    except Exception as e:
        print(f"⚠️ Error: {e}", file=sys.stderr)
        return [], False


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


def run_batched_response(agent: dict, pending_messages: list) -> bool:
    """
    Send all pending messages to Claude in a single prompt.
    Claude will respond to all of them at once using slack_interface.py.
    
    Args:
        agent: Agent configuration dict
        pending_messages: List of message dicts with keys:
            - user: Who sent the message
            - text: Message content
            - timestamp: When it was sent
            - thread_ts: Thread timestamp (if replying to a thread)
            - type: 'mention' or 'thread_reply'
    
    Returns:
        True if Claude successfully processed the messages
    """
    if not pending_messages:
        return True
    
    agent_name = agent["name"]
    agent_role = agent["role"]
    agent_emoji = agent["emoji"]
    
    # Build the messages list for the prompt
    messages_text = ""
    for i, msg in enumerate(pending_messages, 1):
        msg_type = msg.get("type", "mention")
        thread_info = ""
        if msg.get("thread_ts"):
            thread_info = f'\n   Thread: {msg["thread_ts"]} (reply with: python slack_interface.py say "message" -t {msg["thread_ts"]})'
        else:
            thread_info = '\n   Channel: main (reply with: python slack_interface.py say "message")'
        
        messages_text += f"""
--- Message {i} ({msg_type}) ---
From: {msg.get('user', 'Unknown')}
Time: {msg.get('timestamp', 'Unknown')}
Text: {msg.get('text', '')}{thread_info}
"""
    
    # Build the batched prompt
    prompt = f"""You are {agent_name} {agent_emoji}, the {agent_role} on the Logo Creator project team.

You have {len(pending_messages)} message(s) that need your response. Read ALL of them and respond to EACH ONE.

{messages_text}

YOUR TASK:
For EACH message above:
1. Compose a helpful, friendly response (1-3 sentences, sign off with {agent_emoji})
2. Post it to Slack using the appropriate command shown for each message
3. Move to the next message

RULES:
- Respond to ALL {len(pending_messages)} messages - don't skip any!
- Execute slack commands immediately, no confirmation needed
- Keep responses concise and helpful
- Stay in character as {agent_name} the {agent_role}
- Do NOT ask for permission - just do it
- For thread replies, use the -t flag with the thread_ts

Now respond to all {len(pending_messages)} message(s) by posting to Slack."""

    print(f"\n{agent_emoji} Sending {len(pending_messages)} message(s) to Claude for batch response...", flush=True)
    
    try:
        # Let Claude handle all responses
        result = subprocess.run(
            [str(REPO_ROOT / "claude-wrapper.sh"), "-c", "-p", prompt],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=180  # Give Claude more time for multiple messages
        )
        
        # Check if Claude successfully posted
        output = result.stdout + result.stderr
        success_count = output.count("Message sent") + output.count("✅") + output.count("Timestamp:")
        
        if success_count > 0:
            print(f"✅ Claude processed batch - {success_count} response indicator(s) found", flush=True)
            return True
        else:
            print(f"⚠️ Claude batch response (may have posted): {output[:300]}...", flush=True)
            return True  # Assume success even if we can't confirm
            
    except subprocess.TimeoutExpired:
        print("⚠️ Claude batch response timed out", flush=True)
        return False
    except Exception as e:
        print(f"⚠️ Error: {e}", flush=True)
        return False


def main():
    import argparse
    import random
    
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
║  Max runtime: {MAX_RUNTIME // 60} minutes
║  Mentions: {', '.join(agent['mentions'])}
║  Thread replies: ✅ Enabled
║  Batch mode: ✅ Enabled (one Claude call per cycle)
║  Rate limit backoff: ✅ Enabled ({BACKOFF_INITIAL}s-{BACKOFF_MAX}s)
╚══════════════════════════════════════════════════════════════╝
""", flush=True)
    
    seen_messages = load_seen_messages()
    agent_data = load_agent_messages()
    start_time = time.time()
    print(f"📡 Starting monitor loop (max {MAX_RUNTIME // 60} minutes)...", flush=True)
    
    try:
        while True:
            # Check if max runtime exceeded
            elapsed = time.time() - start_time
            if elapsed >= MAX_RUNTIME:
                print(f"\n⏰ Max runtime ({MAX_RUNTIME // 60} minutes) reached. Stopping monitor.", flush=True)
                break
            
            # Check if we're in a backoff period
            if rate_limiter.is_backing_off():
                remaining = rate_limiter.get_remaining_backoff()
                print(f"⏳ Rate limit backoff: {remaining:.0f}s remaining...", flush=True)
                time.sleep(min(remaining, 30))  # Sleep in chunks of max 30s
                continue
            
            # Collect all pending messages for this cycle
            pending_messages = []
            
            # Get recent messages
            messages, was_rate_limited = get_last_messages(10)
            
            if was_rate_limited:
                backoff_time = rate_limiter.on_rate_limit()
                time.sleep(min(backoff_time, 30))
                continue
            else:
                rate_limiter.on_success()
            
            print(f"📨 Got {len(messages)} messages", flush=True)
            
            # Check for new mentions in main channel
            for msg in messages:
                msg_id = msg.get("timestamp", "")
                
                if msg_id in seen_messages:
                    continue
                
                seen_messages.add(msg_id)
                
                if check_for_mention(msg, agent):
                    print(f"  📬 New mention from {msg.get('user', 'Unknown')}: {msg.get('text', '')[:50]}...")
                    pending_messages.append({
                        "user": msg.get("user", "Unknown"),
                        "text": msg.get("text", ""),
                        "timestamp": msg.get("timestamp", ""),
                        "thread_ts": None,
                        "type": "mention"
                    })
            
            # Check for thread replies (only if not rate limited recently)
            if rate_limiter.consecutive_rate_limits == 0:
                raw_messages, was_rate_limited = get_last_messages_raw(20)
                
                if was_rate_limited:
                    backoff_time = rate_limiter.on_rate_limit()
                    save_seen_messages(seen_messages)
                    save_agent_messages(agent_data)
                    time.sleep(min(backoff_time, 30))
                    continue
                
                # Get list of agent's own thread timestamps
                agent_thread_timestamps = set(m.get("ts") for m in agent_data.get("messages", []) if m.get("ts"))
                
                threads_checked = 0
                for raw_msg in raw_messages:
                    if threads_checked >= 3:  # Limit threads per cycle
                        break
                    
                    reply_count = raw_msg.get("reply_count", 0)
                    if reply_count == 0:
                        continue
                    
                    thread_ts = raw_msg.get("ts")
                    latest_reply = raw_msg.get("latest_reply", "")
                    
                    # Check if this is agent's own thread
                    msg_user = raw_msg.get("user", "") or raw_msg.get("username", "")
                    is_agent_thread = (
                        agent["name"].lower() in msg_user.lower() or
                        thread_ts in agent_thread_timestamps
                    )
                    
                    # Check if we've seen this latest reply
                    reply_key = f"{thread_ts}:{latest_reply}"
                    if reply_key in agent_data.get("seen_replies", []):
                        continue
                    
                    # Get thread replies
                    if rate_limiter.is_backing_off():
                        break
                    
                    replies, was_rate_limited = get_thread_replies(thread_ts)
                    threads_checked += 1
                    
                    if was_rate_limited:
                        rate_limiter.on_rate_limit()
                        break
                    
                    # Check each reply
                    for reply in replies[1:]:  # Skip parent message
                        reply_id = f"{thread_ts}:{reply.get('timestamp', '')}"
                        
                        if reply_id in agent_data.get("seen_replies", []):
                            continue
                        
                        # Skip agent's own messages
                        if agent["name"].lower() in reply.get("user", "").lower():
                            agent_data.setdefault("seen_replies", []).append(reply_id)
                            continue
                        
                        # Check if should respond
                        reply_text = reply.get("text", "").lower()
                        is_mention = any(m.lower() in reply_text for m in agent["mentions"])
                        should_respond = is_agent_thread or is_mention
                        
                        if should_respond:
                            print(f"  🧵 New thread reply from {reply.get('user', 'Unknown')}: {reply.get('text', '')[:50]}...")
                            pending_messages.append({
                                "user": reply.get("user", "Unknown"),
                                "text": reply.get("text", ""),
                                "timestamp": reply.get("timestamp", ""),
                                "thread_ts": thread_ts,
                                "type": "thread_reply"
                            })
                        
                        # Mark as seen
                        agent_data.setdefault("seen_replies", []).append(reply_id)
                    
                    # Mark latest reply as seen
                    agent_data.setdefault("seen_replies", []).append(reply_key)
            
            # Process all pending messages in one batch
            if pending_messages:
                print(f"\n📋 Processing {len(pending_messages)} pending message(s) in batch...", flush=True)
                run_batched_response(agent, pending_messages)
            
            # Save state
            save_seen_messages(seen_messages)
            save_agent_messages(agent_data)
            
            # Wait for next poll
            jitter = random.uniform(0, POLL_JITTER)
            sleep_time = args.interval + jitter
            
            if rate_limiter.consecutive_rate_limits > 0:
                sleep_time += BACKOFF_INITIAL / 2
                print(f"💤 Extended sleep due to recent rate limits: {sleep_time:.0f}s", flush=True)
            
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped")
        save_seen_messages(seen_messages)
        save_agent_messages(agent_data)


if __name__ == "__main__":
    main()