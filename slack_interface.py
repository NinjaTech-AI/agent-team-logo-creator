#!/usr/bin/env python3
"""
Slack Interface CLI

A command-line tool to interact with Slack using tokens from /dev/shm/mcp-token.
Automatically detects available scopes and provides various Slack operations.

IMPORTANT: The 'say' command requires an agent identity (nova, pixel, bolt, scout).
Either specify with -a flag or set a default agent in config.

Usage:
    python slack_interface.py --help
    python slack_interface.py agents          # List all available agents
    python slack_interface.py scopes          # Show available scopes for each token
    python slack_interface.py channels        # List all channels
    python slack_interface.py users           # List all users
    python slack_interface.py send <channel> <message>  # Send a message (no agent)
    python slack_interface.py history <channel>         # Get channel history
    python slack_interface.py say -a nova <message>     # Send as Nova agent
    python slack_interface.py say <message>             # Send as default agent
    python slack_interface.py config          # Show/set configuration

Configuration:
    The tool uses a config file at ~/.slack_interface.json or can be specified
    with --config. The config file supports:
    
    {
        "default_channel": "#logo-creator",
        "default_channel_id": "C0AAAAMBR1R",
        "default_agent": "nova",
        "workspace": "RenovateAI"
    }
    
    Set default channel:
        python slack_interface.py config --set-channel "#logo-creator"
    
    Set default agent:
        python slack_interface.py config --set-agent nova

Agents:
    nova  - Product Manager (purple robot)
    pixel - UX Designer (pink robot)
    bolt  - Full-Stack Developer (yellow robot)
    scout - QA Engineer (green robot)
"""

import argparse
import json
import os
import sys
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# ============================================================================
# Agent Avatar URLs (Deployed to web)
# ============================================================================

AVATAR_BASE_URL = "https://sites.super.betamyninja.ai/44664728-914e-4c05-bdf2-d171ad4edcb3/5e27c2ca"

AGENT_AVATARS = {
    "nova": {
        "name": "Nova",
        "role": "Product Manager",
        "emoji": "🌟",
        "color": "purple",
        "icon_url": f"{AVATAR_BASE_URL}/nova.png",
        "icon_emoji": ":star:"
    },
    "pixel": {
        "name": "Pixel",
        "role": "UX Designer",
        "emoji": "🎨",
        "color": "pink",
        "icon_url": f"{AVATAR_BASE_URL}/pixel.png",
        "icon_emoji": ":art:"
    },
    "bolt": {
        "name": "Bolt",
        "role": "Full-Stack Developer",
        "emoji": "⚡",
        "color": "yellow",
        "icon_url": f"{AVATAR_BASE_URL}/bolt.png",
        "icon_emoji": ":zap:"
    },
    "scout": {
        "name": "Scout",
        "role": "QA Engineer",
        "emoji": "🔍",
        "color": "green",
        "icon_url": f"{AVATAR_BASE_URL}/scout.png",
        "icon_emoji": ":mag:"
    }
}


def get_agent_avatar(agent_name: str) -> Optional[Dict[str, str]]:
    """Get avatar info for an agent by name"""
    return AGENT_AVATARS.get(agent_name.lower())


# ============================================================================
# Configuration Management
# ============================================================================

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.slack_interface.json")

@dataclass
class SlackConfig:
    """Configuration for Slack Interface"""
    default_channel: Optional[str] = None
    default_channel_id: Optional[str] = None
    default_agent: Optional[str] = None  # Default agent for say command (nova, pixel, bolt, scout)
    workspace: Optional[str] = None
    
    @classmethod
    def load(cls, filepath: str = DEFAULT_CONFIG_PATH) -> 'SlackConfig':
        """Load configuration from file"""
        config = cls()
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                config.default_channel = data.get('default_channel')
                config.default_channel_id = data.get('default_channel_id')
                config.default_agent = data.get('default_agent')
                config.workspace = data.get('workspace')
        except Exception as e:
            print(f"⚠️ Warning: Could not load config: {e}", file=sys.stderr)
        return config
    
    def save(self, filepath: str = DEFAULT_CONFIG_PATH):
        """Save configuration to file"""
        data = {
            'default_channel': self.default_channel,
            'default_channel_id': self.default_channel_id,
            'default_agent': self.default_agent,
            'workspace': self.workspace
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Configuration saved to {filepath}")
    
    def get_default_channel(self) -> Optional[str]:
        """Get the default channel (ID preferred, then name)"""
        return self.default_channel_id or self.default_channel


# ============================================================================
# Token Management
# ============================================================================

@dataclass
class SlackTokens:
    """Container for Slack tokens"""
    access_token: Optional[str] = None  # xoxp-* (user token)
    bot_token: Optional[str] = None     # xoxb-* (bot token)
    xoxc_token: Optional[str] = None    # xoxc-* (browser token)
    xoxd_token: Optional[str] = None    # xoxd-* (browser cookie)


def parse_mcp_tokens(filepath: str = '/dev/shm/mcp-token') -> Dict[str, Any]:
    """Parse all tokens from the MCP token file"""
    tokens = {}
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        for line in content.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to parse as JSON
                if value.startswith('{'):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass
                
                tokens[key] = value
        
        return tokens
    
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"⚠️ Error parsing tokens: {e}", file=sys.stderr)
        return {}


def get_slack_tokens(filepath: str = '/dev/shm/mcp-token') -> SlackTokens:
    """Extract Slack tokens from MCP token file or environment variables"""
    tokens = SlackTokens()
    
    # Try to get from file first
    all_tokens = parse_mcp_tokens(filepath)
    slack_data = all_tokens.get('Slack', {})
    
    if isinstance(slack_data, dict):
        tokens.access_token = slack_data.get('access_token')
        tokens.bot_token = slack_data.get('bot_token')
    
    # Fall back to environment variables
    if not tokens.access_token:
        tokens.access_token = os.environ.get('SLACK_TOKEN') or os.environ.get('SLACK_MCP_XOXP_TOKEN')
    
    if not tokens.bot_token:
        tokens.bot_token = os.environ.get('SLACK_BOT_TOKEN') or os.environ.get('SLACK_MCP_XOXB_TOKEN')
    
    if not tokens.xoxc_token:
        tokens.xoxc_token = os.environ.get('SLACK_MCP_XOXC_TOKEN')
    
    if not tokens.xoxd_token:
        tokens.xoxd_token = os.environ.get('SLACK_MCP_XOXD_TOKEN')
    
    return tokens


# ============================================================================
# Slack API Client
# ============================================================================

class SlackClient:
    """Slack API client with automatic token selection"""
    
    BASE_URL = "https://slack.com/api"
    
    def __init__(self, tokens: SlackTokens):
        self.tokens = tokens
        self._scopes_cache: Dict[str, List[str]] = {}
    
    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get headers for API request"""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _api_call(self, method: str, token: str, params: Optional[Dict] = None) -> Dict:
        """Make a Slack API call"""
        url = f"{self.BASE_URL}/{method}"
        headers = self._get_headers(token)
        
        try:
            if params:
                response = requests.post(url, headers=headers, json=params, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            return response.json()
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}
    
    def test_auth(self, token: str) -> Dict:
        """Test authentication and get token info"""
        return self._api_call("auth.test", token)
    
    def get_scopes(self, token: str) -> List[str]:
        """Get available scopes for a token"""
        if token in self._scopes_cache:
            return self._scopes_cache[token]
        
        # Make a request and check the response headers
        url = f"{self.BASE_URL}/auth.test"
        headers = self._get_headers(token)
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            scopes_header = response.headers.get('x-oauth-scopes', '')
            scopes = [s.strip() for s in scopes_header.split(',') if s.strip()]
            self._scopes_cache[token] = scopes
            return scopes
        except:
            return []
    
    def list_channels(self, token: str, types: str = "public_channel,private_channel", 
                      limit: int = 200) -> List[Dict]:
        """List all channels"""
        all_channels = []
        cursor = None
        
        while True:
            params = {
                "types": types,
                "limit": min(limit, 200),
                "exclude_archived": False
            }
            if cursor:
                params["cursor"] = cursor
            
            result = self._api_call("conversations.list", token, params)
            
            if not result.get("ok"):
                print(f"❌ Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
                break
            
            channels = result.get("channels", [])
            all_channels.extend(channels)
            
            # Check for pagination
            cursor = result.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return all_channels
    
    def list_users(self, token: str, limit: int = 200) -> List[Dict]:
        """List all users"""
        all_users = []
        cursor = None
        
        while True:
            params = {"limit": min(limit, 200)}
            if cursor:
                params["cursor"] = cursor
            
            result = self._api_call("users.list", token, params)
            
            if not result.get("ok"):
                print(f"❌ Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
                break
            
            users = result.get("members", [])
            all_users.extend(users)
            
            cursor = result.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return all_users
    
    def get_channel_history(self, token: str, channel: str, limit: int = 50) -> List[Dict]:
        """Get channel message history"""
        params = {
            "channel": channel,
            "limit": limit
        }
        
        result = self._api_call("conversations.history", token, params)
        
        if not result.get("ok"):
            print(f"❌ Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            return []
        
        return result.get("messages", [])
    
    def send_message(self, token: str, channel: str, text: str, 
                     thread_ts: Optional[str] = None,
                     username: Optional[str] = None,
                     icon_emoji: Optional[str] = None,
                     icon_url: Optional[str] = None) -> Dict:
        """Send a message to a channel with optional custom username and icon"""
        params = {
            "channel": channel,
            "text": text
        }
        if thread_ts:
            params["thread_ts"] = thread_ts
        
        # Custom bot appearance (only works with bot tokens)
        if username:
            params["username"] = username
        if icon_emoji:
            params["icon_emoji"] = icon_emoji
        if icon_url:
            params["icon_url"] = icon_url
        
        return self._api_call("chat.postMessage", token, params)
    
    def get_channel_info(self, token: str, channel: str) -> Dict:
        """Get channel information"""
        params = {"channel": channel}
        return self._api_call("conversations.info", token, params)
    
    def join_channel(self, token: str, channel: str) -> Dict:
        """Join a channel"""
        params = {"channel": channel}
        return self._api_call("conversations.join", token, params)
    
    def create_channel(self, token: str, name: str, is_private: bool = False) -> Dict:
        """Create a new channel"""
        params = {
            "name": name,
            "is_private": is_private
        }
        return self._api_call("conversations.create", token, params)


# ============================================================================
# CLI Commands
# ============================================================================

def cmd_agents(client: SlackClient, tokens: SlackTokens, args):
    """List all available agents with their avatars"""
    print("\n" + "=" * 60)
    print("🤖 AVAILABLE AGENTS")
    print("=" * 60)
    
    for agent_id, info in AGENT_AVATARS.items():
        print(f"\n{info['emoji']} {info['name']} ({agent_id})")
        print(f"   Role: {info['role']}")
        print(f"   Color: {info['color']}")
        print(f"   Avatar: {info['icon_url']}")
    
    print("\n" + "-" * 60)
    print("💡 Usage:")
    print("   python slack_interface.py say -a nova 'Hello from Nova!'")
    print("   python slack_interface.py say -a pixel 'Design ready!'")
    print("   python slack_interface.py say -a bolt 'Code deployed!'")
    print("   python slack_interface.py say -a scout 'Tests passed!'")
    print("=" * 60 + "\n")


def cmd_config(client: SlackClient, tokens: SlackTokens, args):
    """Show or set configuration"""
    config = SlackConfig.load(args.config_file)
    
    # Set default channel
    if hasattr(args, 'set_channel') and args.set_channel:
        channel = args.set_channel
        
        # Try to resolve channel ID if it's a name
        if channel.startswith('#'):
            token = tokens.access_token or tokens.bot_token
            if token:
                channels = client.list_channels(token)
                channel_name = channel[1:]  # Remove #
                for ch in channels:
                    if ch.get('name') == channel_name:
                        config.default_channel = channel
                        config.default_channel_id = ch.get('id')
                        print(f"✅ Found channel: {channel} (ID: {config.default_channel_id})")
                        break
                else:
                    print(f"⚠️ Channel {channel} not found, saving name only")
                    config.default_channel = channel
                    config.default_channel_id = None
            else:
                config.default_channel = channel
        else:
            # Assume it's a channel ID
            config.default_channel_id = channel
        
        config.save(args.config_file)
        return
    
    # Set default agent
    if hasattr(args, 'set_agent') and args.set_agent:
        agent = args.set_agent.lower()
        if agent not in AGENT_AVATARS:
            print(f"❌ Invalid agent: {agent}", file=sys.stderr)
            print(f"   Valid agents: {', '.join(AGENT_AVATARS.keys())}", file=sys.stderr)
            sys.exit(1)
        
        config.default_agent = agent
        agent_info = AGENT_AVATARS[agent]
        print(f"✅ Default agent set to: {agent_info['name']} ({agent_info['role']})")
        config.save(args.config_file)
        return
    
    # Show current configuration
    print("\n" + "=" * 60)
    print("⚙️  SLACK INTERFACE CONFIGURATION")
    print("=" * 60)
    print(f"\n📁 Config file: {args.config_file}")
    print(f"\n📋 Current Settings:")
    print(f"   Default Channel: {config.default_channel or '(not set)'}")
    print(f"   Default Channel ID: {config.default_channel_id or '(not set)'}")
    if config.default_agent:
        agent_info = AGENT_AVATARS.get(config.default_agent, {})
        print(f"   Default Agent: {config.default_agent} ({agent_info.get('name', '')} - {agent_info.get('role', '')})")
    else:
        print(f"   Default Agent: (not set)")
    print(f"   Workspace: {config.workspace or '(not set)'}")
    
    print(f"\n💡 Configuration Commands:")
    print(f"   python slack_interface.py config --set-channel '#channel-name'")
    print(f"   python slack_interface.py config --set-agent nova")
    print(f"\n🤖 Available Agents: {', '.join(AGENT_AVATARS.keys())}")
    print("=" * 60 + "\n")


def cmd_say(client: SlackClient, tokens: SlackTokens, args):
    """Send a message to the default channel as a specific agent"""
    config = SlackConfig.load(args.config_file)
    
    # Determine agent: CLI arg > config default (REQUIRED)
    agent = None
    if hasattr(args, 'agent') and args.agent:
        agent = args.agent.lower()
    elif config.default_agent:
        agent = config.default_agent.lower()
    
    if not agent:
        print("❌ No agent specified and no default agent configured", file=sys.stderr)
        print("\n🤖 The 'say' command requires an agent identity.", file=sys.stderr)
        print("\n💡 To specify an agent:", file=sys.stderr)
        print("   python slack_interface.py say -a nova 'message'", file=sys.stderr)
        print("   python slack_interface.py say -a pixel 'message'", file=sys.stderr)
        print("   python slack_interface.py say -a bolt 'message'", file=sys.stderr)
        print("   python slack_interface.py say -a scout 'message'", file=sys.stderr)
        print("\n💡 Or set a default agent:", file=sys.stderr)
        print("   python slack_interface.py config --set-agent nova", file=sys.stderr)
        print(f"\n🤖 Available agents: {', '.join(AGENT_AVATARS.keys())}", file=sys.stderr)
        sys.exit(1)
    
    # Validate agent
    if agent not in AGENT_AVATARS:
        print(f"❌ Invalid agent: {agent}", file=sys.stderr)
        print(f"   Valid agents: {', '.join(AGENT_AVATARS.keys())}", file=sys.stderr)
        sys.exit(1)
    
    # Determine channel: CLI arg > config default
    channel = None
    if hasattr(args, 'channel') and args.channel:
        channel = args.channel
    else:
        channel = config.get_default_channel()
    
    if not channel:
        print("❌ No channel specified and no default channel configured", file=sys.stderr)
        print("\n💡 To set a default channel:", file=sys.stderr)
        print("   python slack_interface.py config --set-channel '#channel-name'", file=sys.stderr)
        print("\n   Or specify channel with -c:", file=sys.stderr)
        print("   python slack_interface.py say -a nova -c '#channel' 'message'", file=sys.stderr)
        sys.exit(1)
    
    # Prefer bot token for sending messages (customizable username/icon)
    token = tokens.bot_token or tokens.access_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        sys.exit(1)
    
    message = args.message
    thread = args.thread if hasattr(args, 'thread') else None
    
    # Get agent avatar info
    agent_info = get_agent_avatar(agent)
    username = agent_info['name']
    icon_url = agent_info['icon_url']
    icon_emoji = None  # Don't use emoji when we have custom avatar URL
    
    # Show which channel we're sending to
    channel_display = channel if channel.startswith('#') else f"ID:{channel}"
    print(f"\n📤 Sending to {channel_display}...")
    print(f"   As: {username} ({agent_info['role']})")
    print(f"   Avatar: {agent_info['emoji']} Custom image")
    
    result = client.send_message(token, channel, message, thread, 
                                  username=username, icon_emoji=icon_emoji, icon_url=icon_url)
    
    if result.get("ok"):
        print(f"✅ Message sent successfully!")
        print(f"   Channel: {result.get('channel')}")
        print(f"   Timestamp: {result.get('ts')}")
    else:
        print(f"❌ Failed to send: {result.get('error', 'Unknown error')}")
        sys.exit(1)


def cmd_read(client: SlackClient, tokens: SlackTokens, args):
    """Read messages from the default channel"""
    config = SlackConfig.load(args.config_file)
    
    # Determine channel: CLI arg > config default
    channel = None
    if hasattr(args, 'channel') and args.channel:
        channel = args.channel
    else:
        channel = config.get_default_channel()
    
    if not channel:
        print("❌ No channel specified and no default channel configured", file=sys.stderr)
        print("\n💡 To set a default channel:", file=sys.stderr)
        print("   python slack_interface.py config --set-channel '#channel-name'", file=sys.stderr)
        print("\n   Or specify channel with -c:", file=sys.stderr)
        print("   python slack_interface.py read -c '#channel'", file=sys.stderr)
        sys.exit(1)
    
    # Try bot token first (has channels:history scope), then user token
    token = tokens.bot_token or tokens.access_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        sys.exit(1)
    
    limit = args.limit if hasattr(args, 'limit') else 50
    
    # Show which channel we're reading from
    channel_display = channel if channel.startswith('#') else f"ID:{channel}"
    print(f"\n📖 Reading messages from {channel_display}...")
    
    messages = client.get_channel_history(token, channel, limit)
    
    if not messages:
        print("📭 No messages found or channel is empty")
        print("\n💡 Troubleshooting:")
        print("   • 'missing_scope' error: Add 'channels:history' scope to your Slack app")
        print("   • 'not_in_channel' error: Invite the bot to the channel first:")
        print("     → Go to the channel in Slack and type: /invite @superninja")
        print("   • Or add 'channels:join' scope to allow the bot to join automatically")
        return
    
    print(f"\n💬 Last {len(messages)} messages:\n")
    print("=" * 80)
    
    # Get user info for better display
    users_cache = {}
    try:
        users = client.list_users(token)
        for user in users:
            users_cache[user.get('id')] = user.get('real_name') or user.get('name') or user.get('id')
    except:
        pass  # Continue without user names if it fails
    
    for msg in reversed(messages):
        user_id = msg.get('user', 'unknown')
        user_name = users_cache.get(user_id, user_id)
        text = msg.get('text', '')
        ts = msg.get('ts', '')
        
        # Check for bot messages with custom username
        if msg.get('bot_id') and msg.get('username'):
            user_name = msg.get('username')
        
        # Convert timestamp
        try:
            dt = datetime.fromtimestamp(float(ts))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = ts
        
        # Format output
        print(f"┌─ {user_name} [{time_str}]")
        
        # Handle multi-line messages
        for line in text.split('\n'):
            print(f"│  {line}")
        
        print("└" + "─" * 79)
    
    print(f"\n📊 Total: {len(messages)} messages from {channel_display}")


def cmd_scopes(client: SlackClient, tokens: SlackTokens, args):
    """Show available scopes for each token"""
    print("\n" + "=" * 70)
    print("🔑 SLACK TOKEN SCOPES")
    print("=" * 70)
    
    token_info = [
        ("User Token (xoxp)", tokens.access_token),
        ("Bot Token (xoxb)", tokens.bot_token),
    ]
    
    for name, token in token_info:
        print(f"\n📦 {name}:")
        
        if not token:
            print("   ❌ Not available")
            continue
        
        # Mask token for display
        masked = token[:15] + "..." + token[-8:]
        print(f"   Token: {masked}")
        
        # Test auth
        auth_result = client.test_auth(token)
        if auth_result.get("ok"):
            print(f"   ✅ Valid")
            print(f"   User: {auth_result.get('user', 'N/A')}")
            print(f"   Team: {auth_result.get('team', 'N/A')}")
            print(f"   URL: {auth_result.get('url', 'N/A')}")
        else:
            print(f"   ❌ Invalid: {auth_result.get('error', 'Unknown error')}")
            continue
        
        # Get scopes
        scopes = client.get_scopes(token)
        if scopes:
            print(f"\n   📋 Scopes ({len(scopes)}):")
            # Group scopes by category
            categories = {}
            for scope in sorted(scopes):
                category = scope.split(':')[0] if ':' in scope else scope.split('.')[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append(scope)
            
            for category in sorted(categories.keys()):
                print(f"      [{category}]")
                for scope in categories[category]:
                    print(f"         • {scope}")
        else:
            print("   ⚠️  No scopes found (may be a legacy token)")
    
    print("\n" + "=" * 70)


def cmd_channels(client: SlackClient, tokens: SlackTokens, args):
    """List all channels"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    print("\n🔍 Fetching channels...")
    
    channel_types = args.types if hasattr(args, 'types') and args.types else "public_channel,private_channel"
    channels = client.list_channels(token, types=channel_types)
    
    if not channels:
        print("❌ No channels found or error occurred")
        return
    
    # Sort by member count
    channels.sort(key=lambda x: x.get('num_members', 0), reverse=True)
    
    print(f"\n📢 Found {len(channels)} channels:\n")
    print(f"{'#':<4} {'Channel Name':<35} {'ID':<15} {'Members':<10} {'Private':<8}")
    print("-" * 75)
    
    for i, ch in enumerate(channels, 1):
        name = ch.get('name', 'unknown')
        cid = ch.get('id', 'N/A')
        members = ch.get('num_members', 0)
        is_private = "🔒" if ch.get('is_private') else ""
        print(f"{i:<4} #{name:<34} {cid:<15} {members:<10} {is_private}")
    
    print("-" * 75)
    
    # Save to file if requested
    if hasattr(args, 'output') and args.output:
        with open(args.output, 'w') as f:
            json.dump(channels, f, indent=2)
        print(f"\n💾 Saved to {args.output}")


def cmd_users(client: SlackClient, tokens: SlackTokens, args):
    """List all users"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    print("\n🔍 Fetching users...")
    users = client.list_users(token)
    
    if not users:
        print("❌ No users found or error occurred")
        return
    
    # Filter out bots and deleted users unless requested
    if not (hasattr(args, 'all') and args.all):
        users = [u for u in users if not u.get('is_bot') and not u.get('deleted')]
    
    print(f"\n👥 Found {len(users)} users:\n")
    print(f"{'#':<4} {'Username':<20} {'Real Name':<30} {'ID':<15}")
    print("-" * 70)
    
    for i, user in enumerate(users, 1):
        username = user.get('name', 'unknown')
        real_name = user.get('real_name', user.get('profile', {}).get('real_name', 'N/A'))
        uid = user.get('id', 'N/A')
        print(f"{i:<4} @{username:<19} {real_name:<30} {uid:<15}")
    
    print("-" * 70)
    
    if hasattr(args, 'output') and args.output:
        with open(args.output, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"\n💾 Saved to {args.output}")


def cmd_history(client: SlackClient, tokens: SlackTokens, args):
    """Get channel history"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    limit = args.limit if hasattr(args, 'limit') else 20
    
    print(f"\n🔍 Fetching history for {channel}...")
    messages = client.get_channel_history(token, channel, limit)
    
    if not messages:
        print("❌ No messages found or error occurred")
        return
    
    print(f"\n💬 Last {len(messages)} messages:\n")
    print("-" * 70)
    
    for msg in reversed(messages):
        user = msg.get('user', 'unknown')
        text = msg.get('text', '')[:100]
        ts = msg.get('ts', '')
        
        # Convert timestamp
        try:
            dt = datetime.fromtimestamp(float(ts))
            time_str = dt.strftime('%Y-%m-%d %H:%M')
        except:
            time_str = ts
        
        print(f"[{time_str}] <{user}>: {text}")
    
    print("-" * 70)


def cmd_send(client: SlackClient, tokens: SlackTokens, args):
    """Send a message"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    message = args.message
    thread = args.thread if hasattr(args, 'thread') else None
    
    print(f"\n📤 Sending message to {channel}...")
    result = client.send_message(token, channel, message, thread)
    
    if result.get("ok"):
        print(f"✅ Message sent successfully!")
        print(f"   Channel: {result.get('channel')}")
        print(f"   Timestamp: {result.get('ts')}")
    else:
        print(f"❌ Failed to send: {result.get('error', 'Unknown error')}")


def cmd_join(client: SlackClient, tokens: SlackTokens, args):
    """Join a channel"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    
    print(f"\n🚪 Joining channel {channel}...")
    result = client.join_channel(token, channel)
    
    if result.get("ok"):
        ch = result.get('channel', {})
        print(f"✅ Successfully joined #{ch.get('name', channel)}!")
    else:
        print(f"❌ Failed to join: {result.get('error', 'Unknown error')}")


def cmd_create(client: SlackClient, tokens: SlackTokens, args):
    """Create a channel"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    name = args.name
    is_private = args.private if hasattr(args, 'private') else False
    
    print(f"\n🆕 Creating channel #{name}...")
    result = client.create_channel(token, name, is_private)
    
    if result.get("ok"):
        ch = result.get('channel', {})
        print(f"✅ Successfully created #{ch.get('name')}!")
        print(f"   ID: {ch.get('id')}")
    else:
        print(f"❌ Failed to create: {result.get('error', 'Unknown error')}")


def cmd_info(client: SlackClient, tokens: SlackTokens, args):
    """Get channel info"""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    
    print(f"\n🔍 Getting info for {channel}...")
    result = client.get_channel_info(token, channel)
    
    if result.get("ok"):
        ch = result.get('channel', {})
        print(f"\n📢 Channel Info:")
        print(f"   Name: #{ch.get('name')}")
        print(f"   ID: {ch.get('id')}")
        print(f"   Members: {ch.get('num_members', 'N/A')}")
        print(f"   Private: {'Yes' if ch.get('is_private') else 'No'}")
        print(f"   Archived: {'Yes' if ch.get('is_archived') else 'No'}")
        print(f"   Topic: {ch.get('topic', {}).get('value', 'N/A')}")
        print(f"   Purpose: {ch.get('purpose', {}).get('value', 'N/A')}")
    else:
        print(f"❌ Failed to get info: {result.get('error', 'Unknown error')}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Slack Interface CLI - Interact with Slack using tokens from /dev/shm/mcp-token",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s agents                    List all available agents
  %(prog)s read                      Read messages from default channel
  %(prog)s read -l 100               Read last 100 messages
  %(prog)s say -a nova "Hello!"      Send as Nova agent to default channel
  %(prog)s say -a bolt "Building..."  Send as Bolt agent
  %(prog)s say "Hello!"              Send as default agent (if configured)
  %(prog)s config                    Show current configuration
  %(prog)s config --set-channel "#logo-creator"  Set default channel
  %(prog)s config --set-agent nova   Set default agent
  %(prog)s scopes                    Show available scopes for each token
  %(prog)s channels                  List all channels
  %(prog)s users                     List all users
  %(prog)s history "#general"        Get history for specific channel
  %(prog)s send "#general" "Hello!"  Send a message (no agent identity)
  %(prog)s join "#logo-creator"      Join a channel
  %(prog)s info "#general"           Get channel info

Agents (required for 'say' command):
  nova   - Product Manager (purple robot)
  pixel  - UX Designer (pink robot)
  bolt   - Full-Stack Developer (yellow robot)
  scout  - QA Engineer (green robot)
        """
    )
    
    parser.add_argument('--token-file', '-f', default='/dev/shm/mcp-token',
                        help='Path to token file (default: /dev/shm/mcp-token)')
    parser.add_argument('--config-file', '-C', default=DEFAULT_CONFIG_PATH,
                        help=f'Path to config file (default: {DEFAULT_CONFIG_PATH})')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Agents command
    subparsers.add_parser('agents', help='List all available agents with avatars')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show or set configuration')
    config_parser.add_argument('--set-channel', metavar='CHANNEL',
                               help='Set default channel (e.g., "#logo-creator" or "C0AAAAMBR1R")')
    config_parser.add_argument('--set-agent', metavar='AGENT',
                               help='Set default agent (nova, pixel, bolt, scout)')
    
    # Say command (send to default channel as a specific agent)
    say_parser = subparsers.add_parser('say', help='Send message as an agent (agent required)')
    say_parser.add_argument('message', help='Message text')
    say_parser.add_argument('-a', '--agent', choices=['nova', 'pixel', 'bolt', 'scout'],
                           help='Agent to send as (required if no default agent set)')
    say_parser.add_argument('-c', '--channel', help='Override default channel')
    say_parser.add_argument('-t', '--thread', help='Thread timestamp for reply')
    
    # Read command (read messages from default channel)
    read_parser = subparsers.add_parser('read', help='Read messages from default channel')
    read_parser.add_argument('-c', '--channel', help='Override default channel')
    read_parser.add_argument('-l', '--limit', type=int, default=50,
                            help='Number of messages to fetch (default: 50)')
    
    # Scopes command
    subparsers.add_parser('scopes', help='Show available scopes for each token')
    
    # Channels command
    channels_parser = subparsers.add_parser('channels', help='List all channels')
    channels_parser.add_argument('-t', '--types', default='public_channel,private_channel',
                                  help='Channel types (comma-separated)')
    channels_parser.add_argument('-o', '--output', help='Save to JSON file')
    
    # Users command
    users_parser = subparsers.add_parser('users', help='List all users')
    users_parser.add_argument('-a', '--all', action='store_true', 
                              help='Include bots and deleted users')
    users_parser.add_argument('-o', '--output', help='Save to JSON file')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Get channel history')
    history_parser.add_argument('channel', help='Channel ID or name')
    history_parser.add_argument('-l', '--limit', type=int, default=20,
                                help='Number of messages (default: 20)')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send a message')
    send_parser.add_argument('channel', help='Channel ID or name')
    send_parser.add_argument('message', help='Message text')
    send_parser.add_argument('-t', '--thread', help='Thread timestamp for reply')
    
    # Join command
    join_parser = subparsers.add_parser('join', help='Join a channel')
    join_parser.add_argument('channel', help='Channel ID or name')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a channel')
    create_parser.add_argument('name', help='Channel name')
    create_parser.add_argument('-p', '--private', action='store_true',
                               help='Create as private channel')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get channel info')
    info_parser.add_argument('channel', help='Channel ID or name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load tokens
    tokens = get_slack_tokens(args.token_file)
    
    if not tokens.access_token and not tokens.bot_token:
        print("=" * 70, file=sys.stderr)
        print("❌ SLACK NOT CONNECTED", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(file=sys.stderr)
        print("No Slack tokens found. Please connect your Slack workspace first.", file=sys.stderr)
        print(file=sys.stderr)
        print("👉 To connect Slack:", file=sys.stderr)
        print("   Click the 'Connect' button in the chat interface to link your", file=sys.stderr)
        print("   Slack workspace. This will automatically provide the necessary", file=sys.stderr)
        print("   authentication tokens.", file=sys.stderr)
        print(file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(file=sys.stderr)
        print("🔍 Technical Details:", file=sys.stderr)
        print(f"   • Token file checked: {args.token_file}", file=sys.stderr)
        print(f"   • Environment variables checked:", file=sys.stderr)
        print(f"     - SLACK_TOKEN", file=sys.stderr)
        print(f"     - SLACK_BOT_TOKEN", file=sys.stderr)
        print(f"     - SLACK_MCP_XOXP_TOKEN", file=sys.stderr)
        print(f"     - SLACK_MCP_XOXB_TOKEN", file=sys.stderr)
        print(file=sys.stderr)
        print("💡 Alternative: If you have tokens, set them manually:", file=sys.stderr)
        print("   export SLACK_TOKEN='xoxp-your-token-here'", file=sys.stderr)
        print("   export SLACK_BOT_TOKEN='xoxb-your-bot-token-here'", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)
    
    # Create client
    client = SlackClient(tokens)
    
    # Execute command
    commands = {
        'agents': cmd_agents,
        'config': cmd_config,
        'say': cmd_say,
        'read': cmd_read,
        'scopes': cmd_scopes,
        'channels': cmd_channels,
        'users': cmd_users,
        'history': cmd_history,
        'send': cmd_send,
        'join': cmd_join,
        'create': cmd_create,
        'info': cmd_info,
    }
    
    if args.command in commands:
        commands[args.command](client, tokens, args)
    else:
        parser.print_help()


# ============================================================================
# Python API for Programmatic Access
# ============================================================================

class SlackInterface:
    """
    High-level Python API for Slack Interface.
    
    Usage:
        from slack_interface import SlackInterface
        
        # Initialize (auto-loads tokens and config)
        slack = SlackInterface()
        
        # Send to default channel
        slack.say("Hello from Python!")
        
        # Send to specific channel
        slack.say("Hello!", channel="#general")
        
        # Get default channel info
        print(slack.default_channel)
        
        # List channels
        channels = slack.list_channels()
    """
    
    def __init__(self, token_file: str = '/dev/shm/mcp-token', 
                 config_file: str = DEFAULT_CONFIG_PATH):
        """Initialize Slack Interface with tokens and config"""
        self.tokens = get_slack_tokens(token_file)
        self.config = SlackConfig.load(config_file)
        self.client = SlackClient(self.tokens)
        self._token = self.tokens.access_token or self.tokens.bot_token
    
    @property
    def default_channel(self) -> Optional[str]:
        """Get the default channel"""
        return self.config.get_default_channel()
    
    @property
    def default_channel_name(self) -> Optional[str]:
        """Get the default channel name"""
        return self.config.default_channel
    
    @property
    def is_connected(self) -> bool:
        """Check if Slack is connected (tokens available)"""
        return self._token is not None
    
    def say(self, message: str, channel: Optional[str] = None, 
            thread_ts: Optional[str] = None,
            username: Optional[str] = None,
            icon_emoji: Optional[str] = None,
            icon_url: Optional[str] = None) -> Dict:
        """
        Send a message to the default channel or specified channel.
        
        Args:
            message: The message text to send
            channel: Optional channel override (uses default if not specified)
            thread_ts: Optional thread timestamp for replies
            username: Optional custom bot username (e.g., "Nova", "Pixel")
            icon_emoji: Optional emoji icon (e.g., ":robot_face:", ":star:")
            icon_url: Optional URL to custom icon image
            
        Returns:
            Slack API response dict
            
        Raises:
            ValueError: If no channel specified and no default configured
            RuntimeError: If not connected to Slack
        """
        if not self.is_connected:
            raise RuntimeError(
                "Slack not connected. Please click the 'Connect' button in the "
                "chat interface to link your Slack workspace."
            )
        
        target_channel = channel or self.default_channel
        if not target_channel:
            raise ValueError(
                "No channel specified and no default channel configured. "
                "Set default with: slack.set_default_channel('#channel-name')"
            )
        
        # Prefer bot token for custom username/icon support
        token = self.tokens.bot_token or self._token
        
        return self.client.send_message(
            token, target_channel, message, thread_ts,
            username=username, icon_emoji=icon_emoji, icon_url=icon_url
        )
    
    def set_default_channel(self, channel: str, config_file: str = DEFAULT_CONFIG_PATH):
        """
        Set the default channel for future messages.
        
        Args:
            channel: Channel name (e.g., "#logo-creator") or ID (e.g., "C0AAAAMBR1R")
            config_file: Path to save config (default: ~/.slack_interface.json)
        """
        if channel.startswith('#'):
            # Try to resolve channel ID
            channels = self.list_channels()
            channel_name = channel[1:]
            for ch in channels:
                if ch.get('name') == channel_name:
                    self.config.default_channel = channel
                    self.config.default_channel_id = ch.get('id')
                    break
            else:
                self.config.default_channel = channel
                self.config.default_channel_id = None
        else:
            self.config.default_channel_id = channel
        
        self.config.save(config_file)
    
    def list_channels(self, types: str = "public_channel,private_channel") -> List[Dict]:
        """List all channels"""
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.list_channels(self._token, types)
    
    def list_users(self) -> List[Dict]:
        """List all users"""
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.list_users(self._token)
    
    def get_history(self, channel: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Get channel message history"""
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        target_channel = channel or self.default_channel
        if not target_channel:
            raise ValueError("No channel specified and no default configured")
        return self.client.get_channel_history(self._token, target_channel, limit)
    
    def join_channel(self, channel: str) -> Dict:
        """Join a channel"""
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.join_channel(self._token, channel)
    
    def create_channel(self, name: str, is_private: bool = False) -> Dict:
        """Create a new channel"""
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.create_channel(self._token, name, is_private)


# Convenience function for quick messaging
def say(message: str, channel: Optional[str] = None, 
        username: Optional[str] = None, icon_emoji: Optional[str] = None) -> Dict:
    """
    Quick function to send a message to the default channel.
    
    Usage:
        from slack_interface import say
        say("Hello from Python!")
        say("Hello!", channel="#general")
        say("Hello!", username="Nova", icon_emoji=":star:")
    """
    slack = SlackInterface()
    return slack.say(message, channel, username=username, icon_emoji=icon_emoji)


if __name__ == "__main__":
    main()