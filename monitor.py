#!/usr/bin/env python3
"""
Agent Monitor - Watches Slack for mentions and triggers agent responses.

This script runs independently and only invokes Claude CLI when the agent
is mentioned in Slack. It polls every 45 seconds and tracks seen messages.

Features:
- Monitors main channel for mentions
- Monitors thread replies to agent's messages
- Strips ANSI escape codes from responses
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
POLL_INTERVAL = 45  # base seconds
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


def run_agent_response(agent: dict, message: dict, thread_ts: str = None, is_thread_reply: bool = False) -> str:
    """Generate a response using Claude and post it directly to Slack.
    
    Args:
        agent: Agent configuration dict
        message: The message to respond to
        thread_ts: Optional thread timestamp to reply in
        is_thread_reply: Whether this is a reply to a thread on agent's message
        
    Returns:
        The timestamp of the posted message, or None if failed
    """
    
    agent_name = agent["name"]
    agent_role = agent["role"]
    agent_emoji = agent["emoji"]
    
    # Build context for thread replies
    context = ""
    if is_thread_reply:
        context = "\nThis is a reply in a thread on one of your previous messages. Respond helpfully to continue the conversation."
    
    # Build a focused task prompt - ask Claude to generate ONLY the response text
    task = f"""Someone mentioned you in Slack! Here's the message:

From: {message.get('user', 'Unknown')}
Time: {message.get('timestamp', 'Unknown')}
Message: {message.get('text', '')}
{context}

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

    reply_type = "thread reply" if is_thread_reply else "mention"
    print(f"\n{agent_emoji} Generating response to {reply_type} from {message.get('user', 'Unknown')}...", flush=True)
    
    try:
        # Get response from Claude
        result = subprocess.run(
            [str(REPO_ROOT / "claude-wrapper.sh"), "-p", prompt],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        response_text = result.stdout.strip()
        
        if not response_text:
            response_text = f"Hey! {agent_emoji} I'm {agent_name}, the {agent_role}. I'm online and ready to help!"
        
        # Clean up response - remove ANSI escape codes and terminal artifacts
        # Remove OSC (Operating System Command) sequences like ]9;4;0;
        response_text = re.sub(r'\][\d;]*[^\a\x07]*[\a\x07]?', '', response_text)
        response_text = re.sub(r'\x1b\][\d;]*[^\x07]*\x07?', '', response_text)
        # Remove other ANSI escape sequences
        response_text = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', response_text)
        # Remove any remaining escape characters and control codes
        response_text = re.sub(r'[\x00-\x1f\x7f]', '', response_text)
        # Clean up any leftover artifacts like ]9;4;0;
        response_text = re.sub(r'\][\d;]+;?', '', response_text)
        
        # Clean up response - remove any markdown code blocks or command artifacts
        response_text = response_text.replace("```", "").strip()
        if response_text.startswith("bash") or response_text.startswith("python"):
            response_text = f"Hey! {agent_emoji} I'm {agent_name}, online and ready to help!"
        
        # Limit response length
        if len(response_text) > 500:
            response_text = response_text[:500] + "..."
        
        print(f"📝 Response: {response_text[:100]}...", flush=True)
        
        # Build slack command - add thread flag if replying to a thread
        slack_cmd = ["python", "slack_interface.py", "say", response_text]
        if thread_ts:
            slack_cmd.extend(["-t", thread_ts])
        
        # Post directly to Slack using slack_interface.py
        slack_result = subprocess.run(
            slack_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if slack_result.returncode == 0:
            print(f"✅ Response posted to Slack!", flush=True)
            # Try to extract timestamp from output
            ts_match = re.search(r'Timestamp: (\d+\.\d+)', slack_result.stdout)
            if ts_match:
                return ts_match.group(1)
        else:
            print(f"⚠️ Slack error: {slack_result.stderr}", flush=True)
            
    except subprocess.TimeoutExpired:
        print("⚠️ Response timed out", flush=True)
    except Exception as e:
        print(f"⚠️ Error: {e}", flush=True)
    
    return None


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
            
            # Get recent messages
            messages, was_rate_limited = get_last_messages(10)
            
            if was_rate_limited:
                backoff_time = rate_limiter.on_rate_limit()
                time.sleep(min(backoff_time, 30))  # Start backing off immediately
                continue
            else:
                rate_limiter.on_success()
            
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
                    
                    # Run agent response and track the message
                    response_ts = run_agent_response(agent, msg)
                    if response_ts:
                        agent_data["messages"].append({
                            "ts": response_ts,
                            "time": msg_id
                        })
            
            # Check for thread replies using raw message data (more efficient)
            # Only check threads that have replies (reply_count > 0)
            # Skip if we just recovered from rate limiting
            if rate_limiter.consecutive_rate_limits == 0:
                raw_messages, was_rate_limited = get_last_messages_raw(20)
                
                if was_rate_limited:
                    backoff_time = rate_limiter.on_rate_limit()
                    save_seen_messages(seen_messages)
                    save_agent_messages(agent_data)
                    time.sleep(min(backoff_time, 30))
                    continue
                
                threads_to_check = []
                
                # Get list of agent's own thread timestamps
                agent_thread_timestamps = set(m.get("ts") for m in agent_data.get("messages", []) if m.get("ts"))
                
                for raw_msg in raw_messages:
                    reply_count = raw_msg.get("reply_count", 0)
                    if reply_count > 0:
                        thread_ts = raw_msg.get("ts")
                        latest_reply = raw_msg.get("latest_reply", "")
                        
                        # Check if this is agent's own thread (agent started it)
                        msg_user = raw_msg.get("user", "") or raw_msg.get("username", "")
                        is_agent_thread = (
                            agent["name"].lower() in msg_user.lower() or
                            thread_ts in agent_thread_timestamps
                        )
                        
                        # Check if we've seen this latest reply
                        reply_key = f"{thread_ts}:{latest_reply}"
                        if reply_key not in agent_data.get("seen_replies", []):
                            threads_to_check.append({
                                "thread_ts": thread_ts,
                                "reply_count": reply_count,
                                "latest_reply": latest_reply,
                                "is_agent_thread": is_agent_thread
                            })
                
                if threads_to_check:
                    print(f"🧵 Found {len(threads_to_check)} threads with new replies to check...", flush=True)
                    
                    for thread_info in threads_to_check[:3]:  # Limit to 3 threads per cycle to avoid rate limits
                        # Check rate limit before each thread request
                        if rate_limiter.is_backing_off():
                            break
                        
                        thread_ts = thread_info["thread_ts"]
                        is_agent_thread = thread_info["is_agent_thread"]
                        replies, was_rate_limited = get_thread_replies(thread_ts)
                        
                        if was_rate_limited:
                            rate_limiter.on_rate_limit()
                            break  # Stop checking threads, will retry next cycle
                        
                        # Skip first message (it's the parent) and check replies
                        for reply in replies[1:]:
                            reply_id = f"{thread_ts}:{reply.get('timestamp', '')}"
                            
                            # Skip if already seen
                            if reply_id in agent_data.get("seen_replies", []):
                                continue
                            
                            # Skip if it's from the agent itself
                            if agent["name"].lower() in reply.get("user", "").lower():
                                agent_data.setdefault("seen_replies", []).append(reply_id)
                                continue
                            
                            # Check if this reply mentions the agent
                            reply_text = reply.get("text", "").lower()
                            is_mention = any(m.lower() in reply_text for m in agent["mentions"])
                            
                            # Respond if: it's agent's own thread OR reply mentions the agent
                            should_respond = is_agent_thread or is_mention
                            
                            if should_respond:
                                # New reply to respond to!
                                reason = "agent's thread" if is_agent_thread else "mention"
                                print(f"\n🧵 New thread reply detected ({reason})!")
                                print(f"   From: {reply.get('user', 'Unknown')}")
                                print(f"   Text: {reply.get('text', '')[:100]}...")
                                
                                # Mark as seen
                                agent_data.setdefault("seen_replies", []).append(reply_id)
                                
                                # Respond in the thread
                                run_agent_response(agent, reply, thread_ts=thread_ts, is_thread_reply=True)
                            else:
                                # Mark as seen even if not responding (to avoid re-checking)
                                agent_data.setdefault("seen_replies", []).append(reply_id)
                        
                        # Mark the latest reply as seen for this thread
                        latest_key = f"{thread_ts}:{thread_info['latest_reply']}"
                        if latest_key not in agent_data.get("seen_replies", []):
                            agent_data.setdefault("seen_replies", []).append(latest_key)
            
            # Save state
            save_seen_messages(seen_messages)
            save_agent_messages(agent_data)
            
            # Wait for next poll (interval + random jitter)
            jitter = random.uniform(0, POLL_JITTER)
            sleep_time = args.interval + jitter
            
            # If we had any rate limiting recently, add extra delay
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