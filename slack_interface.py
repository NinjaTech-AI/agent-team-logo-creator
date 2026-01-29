#!/usr/bin/env python3
"""
Slack Interface CLI

A command-line tool and Python API for interacting with Slack workspaces.
Supports agent-based messaging with custom avatars, file uploads, and more.

Token Sources (in priority order):
    1. /dev/shm/mcp-token - Auto-populated when you click 'Connect' in chat
    2. Environment variables: SLACK_TOKEN, SLACK_BOT_TOKEN

Token Types:
    - User Token (xoxp-*): Full user permissions, can access all user's channels
    - Bot Token (xoxb-*): Bot permissions, limited to channels bot is invited to

Required Scopes:
    - channels:read      - List channels
    - channels:history   - Read channel messages
    - chat:write         - Send messages
    - users:read         - List users
    - files:write        - Upload files (optional, for file uploads)
    - files:read         - Read file info (optional)

Usage:
    python slack_interface.py --help
    python slack_interface.py agents                    # List all available agents
    python slack_interface.py scopes                    # Show available scopes
    python slack_interface.py channels                  # List all channels
    python slack_interface.py users                     # List all users
    python slack_interface.py read                      # Read from default channel
    python slack_interface.py say -a nova "message"     # Send as Nova agent
    python slack_interface.py say "message"             # Send as default agent
    python slack_interface.py upload file.png           # Upload file to default channel
    python slack_interface.py config                    # Show/set configuration

Configuration:
    The tool uses a config file at ~/.slack_interface.json:
    
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
    nova  - Product Manager (🌟 purple)
    pixel - UX Designer (🎨 pink)
    bolt  - Full-Stack Developer (⚡ yellow)
    scout - QA Engineer (🔍 green)

Examples:
    # Send message as agent
    python slack_interface.py say -a nova "Sprint planning at 2pm!"
    
    # Upload file with comment
    python slack_interface.py upload designs/mockup.png -m "New design ready!"
    
    # Read recent messages
    python slack_interface.py read -l 20
"""

import argparse
import json
import os
import sys
import requests
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# ============================================================================
# Agent Configuration
# ============================================================================
# Each agent has a unique identity with custom avatar for Slack messages.
# Avatars are hosted on a public URL and displayed in Slack when sending messages.

AVATAR_BASE_URL = "https://sites.super.betamyninja.ai/44664728-914e-4c05-bdf2-d171ad4edcb3/5e27c2ca"

AGENT_AVATARS = {
    "nova": {
        "name": "Nova",
        "role": "Product Manager",
        "emoji": "🌟",
        "color": "purple",
        "icon_url": f"{AVATAR_BASE_URL}/nova.png",
        "icon_emoji": ":star:"  # Fallback if icon_url not supported
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
    """
    Get avatar configuration for an agent by name.
    
    Args:
        agent_name: Agent identifier (nova, pixel, bolt, scout)
        
    Returns:
        Dict with agent info (name, role, emoji, color, icon_url, icon_emoji)
        or None if agent not found
    """
    return AGENT_AVATARS.get(agent_name.lower())


# ============================================================================
# Configuration Management
# ============================================================================
# Configuration is persisted to ~/.slack_interface.json and includes:
# - default_channel: Channel name (e.g., "#logo-creator")
# - default_channel_id: Channel ID (e.g., "C0AAAAMBR1R") - preferred for API calls
# - default_agent: Default agent for 'say' command
# - workspace: Workspace name (informational)

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.slack_interface.json")


@dataclass
class SlackConfig:
    """
    Configuration container for Slack Interface.
    
    Attributes:
        default_channel: Channel name (e.g., "#logo-creator")
        default_channel_id: Channel ID for API calls (e.g., "C0AAAAMBR1R")
        default_agent: Default agent for say command (nova, pixel, bolt, scout)
        workspace: Workspace name (informational only)
    """
    default_channel: Optional[str] = None
    default_channel_id: Optional[str] = None
    default_agent: Optional[str] = None
    workspace: Optional[str] = None
    
    @classmethod
    def load(cls, filepath: str = DEFAULT_CONFIG_PATH) -> 'SlackConfig':
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to config file (default: ~/.slack_interface.json)
            
        Returns:
            SlackConfig instance with loaded values (or defaults if file missing)
        """
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
    
    def save(self, filepath: str = DEFAULT_CONFIG_PATH) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save config (default: ~/.slack_interface.json)
        """
        data = {
            'default_channel': self.default_channel,
            'default_channel_id': self.default_channel_id,
            'default_agent': self.default_agent,
            'workspace': self.workspace
        }
        # Remove None values for cleaner JSON
        data = {k: v for k, v in data.items() if v is not None}
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Configuration saved to {filepath}")
    
    def get_default_channel(self) -> Optional[str]:
        """
        Get the default channel identifier for API calls.
        Prefers channel ID over name since IDs are more reliable.
        
        Returns:
            Channel ID if available, otherwise channel name, or None
        """
        return self.default_channel_id or self.default_channel


# ============================================================================
# Token Management
# ============================================================================
# Slack uses different token types with different capabilities:
#
# User Token (xoxp-*):
#   - Acts as the user who authorized the app
#   - Can access all channels the user is in
#   - Can search messages (with search:read scope)
#   - Scopes are granted during OAuth flow
#
# Bot Token (xoxb-*):
#   - Acts as the bot/app itself
#   - Can only access channels where bot is invited
#   - Better for automated messaging (custom username/icon)
#   - Scopes are configured in app settings
#
# For sending messages with custom avatars, bot tokens are preferred
# because they support the username and icon_url parameters.

@dataclass
class SlackTokens:
    """
    Container for Slack authentication tokens.
    
    Attributes:
        access_token: User token (xoxp-*) - acts as the authorizing user
        bot_token: Bot token (xoxb-*) - acts as the bot/app
        xoxc_token: Browser token (xoxc-*) - for browser-based auth (rarely used)
        xoxd_token: Browser cookie (xoxd-*) - for browser-based auth (rarely used)
    """
    access_token: Optional[str] = None  # xoxp-* (user token)
    bot_token: Optional[str] = None     # xoxb-* (bot token)
    xoxc_token: Optional[str] = None    # xoxc-* (browser token)
    xoxd_token: Optional[str] = None    # xoxd-* (browser cookie)


def parse_mcp_tokens(filepath: str = '/dev/shm/mcp-token') -> Dict[str, Any]:
    """
    Parse all tokens from the MCP token file.
    
    The MCP token file contains credentials for various services in the format:
        ServiceName=value
    or for JSON values:
        ServiceName={"key": "value"}
    
    Args:
        filepath: Path to MCP token file (default: /dev/shm/mcp-token)
        
    Returns:
        Dict mapping service names to their token values
    """
    tokens = {}
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        for line in content.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to parse JSON values (e.g., Slack tokens)
                if value.startswith('{'):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass  # Keep as string if not valid JSON
                
                tokens[key] = value
        
        return tokens
    
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"⚠️ Error parsing tokens: {e}", file=sys.stderr)
        return {}


def get_slack_tokens(filepath: str = '/dev/shm/mcp-token') -> SlackTokens:
    """
    Extract Slack tokens from MCP token file or environment variables.
    
    Token sources (in priority order):
        1. MCP token file (/dev/shm/mcp-token) - auto-populated by Connect button
        2. Environment variables:
           - SLACK_TOKEN or SLACK_MCP_XOXP_TOKEN (user token)
           - SLACK_BOT_TOKEN or SLACK_MCP_XOXB_TOKEN (bot token)
    
    Args:
        filepath: Path to MCP token file
        
    Returns:
        SlackTokens instance with available tokens
    """
    tokens = SlackTokens()
    
    # Try to get from MCP token file first
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
# Low-level client for Slack Web API calls.
# See https://api.slack.com/methods for full API documentation.

class SlackClient:
    """
    Low-level Slack API client with automatic token handling.
    
    This client provides direct access to Slack Web API methods.
    For higher-level operations, use the SlackInterface class instead.
    
    Attributes:
        tokens: SlackTokens instance with available tokens
        
    Example:
        tokens = get_slack_tokens()
        client = SlackClient(tokens)
        result = client.send_message(tokens.bot_token, "#general", "Hello!")
    """
    
    BASE_URL = "https://slack.com/api"
    
    def __init__(self, tokens: SlackTokens):
        """
        Initialize Slack client with tokens.
        
        Args:
            tokens: SlackTokens instance containing available tokens
        """
        self.tokens = tokens
        self._scopes_cache: Dict[str, List[str]] = {}
    
    def _get_headers(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for API request with Bearer token auth."""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _get_headers_multipart(self, token: str) -> Dict[str, str]:
        """Get HTTP headers for multipart/form-data requests (file uploads)."""
        return {
            "Authorization": f"Bearer {token}"
            # Note: Don't set Content-Type for multipart - requests handles it
        }
    
    def _api_call(self, method: str, token: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a Slack API call.
        
        Args:
            method: API method name (e.g., "chat.postMessage")
            token: Authentication token to use
            params: Optional parameters for the API call
            
        Returns:
            API response as dict (always contains 'ok' boolean)
        """
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
        """
        Test authentication and get token info.
        
        API Method: auth.test
        Required Scopes: None (works with any valid token)
        
        Args:
            token: Token to test
            
        Returns:
            Dict with 'ok', 'user', 'team', 'url' on success
        """
        return self._api_call("auth.test", token)
    
    def get_scopes(self, token: str) -> List[str]:
        """
        Get available OAuth scopes for a token.
        
        Scopes are returned in the x-oauth-scopes response header.
        Results are cached to avoid repeated API calls.
        
        Args:
            token: Token to check scopes for
            
        Returns:
            List of scope strings (e.g., ["chat:write", "channels:read"])
        """
        if token in self._scopes_cache:
            return self._scopes_cache[token]
        
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
        """
        List all channels in the workspace.
        
        API Method: conversations.list
        Required Scopes: channels:read, groups:read (for private channels)
        
        Args:
            token: Authentication token
            types: Comma-separated channel types (public_channel, private_channel, mpim, im)
            limit: Max channels per page (max 200, handles pagination automatically)
            
        Returns:
            List of channel dicts with 'id', 'name', 'num_members', etc.
        """
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
            
            # Handle pagination
            cursor = result.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        
        return all_channels
    
    def list_users(self, token: str, limit: int = 200) -> List[Dict]:
        """
        List all users in the workspace.
        
        API Method: users.list
        Required Scopes: users:read
        
        Args:
            token: Authentication token
            limit: Max users per page (handles pagination automatically)
            
        Returns:
            List of user dicts with 'id', 'name', 'real_name', 'profile', etc.
        """
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
        """
        Get message history from a channel.
        
        API Method: conversations.history
        Required Scopes: channels:history (public), groups:history (private)
        
        Args:
            token: Authentication token
            channel: Channel ID (e.g., "C0AAAAMBR1R")
            limit: Number of messages to retrieve (max 1000)
            
        Returns:
            List of message dicts with 'text', 'user', 'ts', etc.
            Messages are in reverse chronological order (newest first)
        """
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
        """
        Send a message to a channel.
        
        API Method: chat.postMessage
        Required Scopes: chat:write
        
        Note: username, icon_emoji, and icon_url only work with bot tokens
        and require chat:write.customize scope for full customization.
        
        Args:
            token: Authentication token (bot token preferred for custom identity)
            channel: Channel ID or name
            text: Message text (supports Slack markdown)
            thread_ts: Thread timestamp for replies (optional)
            username: Custom bot username (optional, bot token only)
            icon_emoji: Custom emoji icon like ":robot_face:" (optional)
            icon_url: Custom icon image URL (optional, overrides icon_emoji)
            
        Returns:
            API response with 'ok', 'ts' (timestamp), 'channel' on success
        """
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
    
    def upload_file(self, token: str, channels: Union[str, List[str]], 
                    file_path: Optional[str] = None,
                    content: Optional[str] = None,
                    filename: Optional[str] = None,
                    title: Optional[str] = None,
                    initial_comment: Optional[str] = None,
                    thread_ts: Optional[str] = None) -> Dict:
        """
        Upload a file to Slack.
        
        API Method: files.upload
        Required Scopes: files:write
        
        You can either provide a file_path to upload from disk, or provide
        content directly as a string.
        
        Args:
            token: Authentication token with files:write scope
            channels: Channel ID(s) to share file to (string or list)
            file_path: Path to file on disk (optional if content provided)
            content: File content as string (optional if file_path provided)
            filename: Filename to display in Slack (optional, derived from path)
            title: Title for the file (optional)
            initial_comment: Message to post with the file (optional)
            thread_ts: Thread timestamp to post file as reply (optional)
            
        Returns:
            API response with 'ok', 'file' object on success
        """
        url = f"{self.BASE_URL}/files.upload"
        headers = self._get_headers_multipart(token)
        
        # Prepare form data
        data = {}
        
        # Handle channels (can be string or list)
        if isinstance(channels, list):
            data['channels'] = ','.join(channels)
        else:
            data['channels'] = channels
        
        if filename:
            data['filename'] = filename
        if title:
            data['title'] = title
        if initial_comment:
            data['initial_comment'] = initial_comment
        if thread_ts:
            data['thread_ts'] = thread_ts
        
        files = None
        
        try:
            if file_path:
                # Upload from file path
                path = Path(file_path)
                if not path.exists():
                    return {"ok": False, "error": f"File not found: {file_path}"}
                
                if not filename:
                    data['filename'] = path.name
                
                files = {'file': (path.name, open(path, 'rb'))}
                response = requests.post(url, headers=headers, data=data, files=files, timeout=60)
            elif content:
                # Upload content directly
                data['content'] = content
                response = requests.post(url, headers=headers, data=data, timeout=60)
            else:
                return {"ok": False, "error": "Either file_path or content must be provided"}
            
            return response.json()
            
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}
        finally:
            # Close file handle if opened
            if files and 'file' in files:
                files['file'][1].close()
    
    def get_channel_info(self, token: str, channel: str) -> Dict:
        """
        Get information about a channel.
        
        API Method: conversations.info
        Required Scopes: channels:read (public), groups:read (private)
        
        Args:
            token: Authentication token
            channel: Channel ID
            
        Returns:
            API response with 'ok', 'channel' object on success
        """
        params = {"channel": channel}
        return self._api_call("conversations.info", token, params)
    
    def join_channel(self, token: str, channel: str) -> Dict:
        """
        Join a channel.
        
        API Method: conversations.join
        Required Scopes: channels:join
        
        Note: Bots can only join public channels. For private channels,
        the bot must be invited by a channel member.
        
        Args:
            token: Authentication token
            channel: Channel ID to join
            
        Returns:
            API response with 'ok', 'channel' object on success
        """
        params = {"channel": channel}
        return self._api_call("conversations.join", token, params)
    
    def create_channel(self, token: str, name: str, is_private: bool = False) -> Dict:
        """
        Create a new channel.
        
        API Method: conversations.create
        Required Scopes: channels:manage (public), groups:write (private)
        
        Args:
            token: Authentication token
            name: Channel name (lowercase, no spaces, max 80 chars)
            is_private: Create as private channel (default: False)
            
        Returns:
            API response with 'ok', 'channel' object on success
        """
        params = {
            "name": name,
            "is_private": is_private
        }
        return self._api_call("conversations.create", token, params)


# ============================================================================
# CLI Commands
# ============================================================================
# Each cmd_* function implements a CLI subcommand.
# Functions receive the client, tokens, and parsed args.

def cmd_agents(client: SlackClient, tokens: SlackTokens, args) -> None:
    """List all available agents with their avatars."""
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


def cmd_config(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Show or set configuration."""
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


def cmd_say(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Send a message to the default channel as a specific agent."""
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
    
    # Prefer bot token for sending messages (supports custom username/icon)
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


def cmd_read(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Read messages from the default channel."""
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
    
    # Try bot token first for reading (usually has channels:history scope)
    # Fall back to user token if bot token not available
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


def cmd_upload(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Upload a file to a channel."""
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
        print("   python slack_interface.py upload file.png -c '#channel'", file=sys.stderr)
        sys.exit(1)
    
    # Prefer bot token for uploads
    token = tokens.bot_token or tokens.access_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        sys.exit(1)
    
    # Check for files:write scope
    scopes = client.get_scopes(token)
    if scopes and 'files:write' not in scopes:
        print("⚠️ Warning: Token may not have 'files:write' scope", file=sys.stderr)
        print("   File upload might fail. Check scopes with: python slack_interface.py scopes", file=sys.stderr)
    
    file_path = args.file
    title = args.title if hasattr(args, 'title') and args.title else None
    comment = args.message if hasattr(args, 'message') and args.message else None
    thread = args.thread if hasattr(args, 'thread') else None
    
    # Show upload info
    channel_display = channel if channel.startswith('#') else f"ID:{channel}"
    print(f"\n📤 Uploading to {channel_display}...")
    print(f"   File: {file_path}")
    if title:
        print(f"   Title: {title}")
    if comment:
        print(f"   Comment: {comment[:50]}{'...' if len(comment) > 50 else ''}")
    
    result = client.upload_file(
        token, channel, 
        file_path=file_path,
        title=title,
        initial_comment=comment,
        thread_ts=thread
    )
    
    if result.get("ok"):
        file_info = result.get('file', {})
        print(f"✅ File uploaded successfully!")
        print(f"   Name: {file_info.get('name', 'N/A')}")
        print(f"   Size: {file_info.get('size', 0)} bytes")
        print(f"   URL: {file_info.get('permalink', 'N/A')}")
    else:
        error = result.get('error', 'Unknown error')
        print(f"❌ Failed to upload: {error}")
        if error == 'missing_scope':
            print("\n💡 The 'files:write' scope is required for file uploads.")
            print("   Add this scope to your Slack app at: https://api.slack.com/apps")
        elif error == 'channel_not_found':
            print("\n💡 Channel not found. Make sure the bot is a member of the channel.")
        sys.exit(1)


def cmd_scopes(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Show available scopes for each token."""
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
    
    # Show required scopes info
    print("\n" + "-" * 70)
    print("📋 REQUIRED SCOPES BY FEATURE:")
    print("-" * 70)
    print("   Basic Operations:")
    print("      • channels:read      - List channels")
    print("      • channels:history   - Read channel messages")
    print("      • chat:write         - Send messages")
    print("      • users:read         - List users")
    print("   File Uploads:")
    print("      • files:write        - Upload files")
    print("      • files:read         - Read file info (optional)")
    print("   Channel Management:")
    print("      • channels:join      - Join public channels")
    print("      • channels:manage    - Create/archive channels")
    print("   Private Channels:")
    print("      • groups:read        - List private channels")
    print("      • groups:history     - Read private channel messages")
    print("=" * 70 + "\n")


def cmd_channels(client: SlackClient, tokens: SlackTokens, args) -> None:
    """List all channels."""
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


def cmd_users(client: SlackClient, tokens: SlackTokens, args) -> None:
    """List all users."""
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


def cmd_history(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Get channel history."""
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
    
    for msg in reversed(messages):
        user = msg.get('user', 'unknown')
        text = msg.get('text', '')[:100]
        ts = msg.get('ts', '')
        
        # Check for bot messages
        if msg.get('bot_id') and msg.get('username'):
            user = msg.get('username')
        
        try:
            dt = datetime.fromtimestamp(float(ts))
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = ts
        
        print(f"[{time_str}] {user}: {text}")


def cmd_send(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Send a message without agent identity."""
    token = tokens.bot_token or tokens.access_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    message = args.message
    thread = args.thread if hasattr(args, 'thread') else None
    
    print(f"\n📤 Sending to {channel}...")
    result = client.send_message(token, channel, message, thread)
    
    if result.get("ok"):
        print(f"✅ Message sent!")
        print(f"   Timestamp: {result.get('ts')}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


def cmd_join(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Join a channel."""
    token = tokens.bot_token or tokens.access_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    print(f"\n🚪 Joining {channel}...")
    
    result = client.join_channel(token, channel)
    
    if result.get("ok"):
        ch = result.get('channel', {})
        print(f"✅ Joined #{ch.get('name', channel)}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


def cmd_create(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Create a new channel."""
    token = tokens.bot_token or tokens.access_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    name = args.name
    is_private = args.private if hasattr(args, 'private') else False
    
    print(f"\n🆕 Creating {'private ' if is_private else ''}channel #{name}...")
    
    result = client.create_channel(token, name, is_private)
    
    if result.get("ok"):
        ch = result.get('channel', {})
        print(f"✅ Created #{ch.get('name', name)}")
        print(f"   ID: {ch.get('id')}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


def cmd_info(client: SlackClient, tokens: SlackTokens, args) -> None:
    """Get channel info."""
    token = tokens.access_token or tokens.bot_token
    if not token:
        print("❌ No valid token available", file=sys.stderr)
        return
    
    channel = args.channel
    print(f"\n🔍 Getting info for {channel}...")
    
    result = client.get_channel_info(token, channel)
    
    if result.get("ok"):
        ch = result.get('channel', {})
        print(f"\n📢 Channel: #{ch.get('name', 'N/A')}")
        print(f"   ID: {ch.get('id', 'N/A')}")
        print(f"   Members: {ch.get('num_members', 0)}")
        print(f"   Private: {'Yes' if ch.get('is_private') else 'No'}")
        print(f"   Archived: {'Yes' if ch.get('is_archived') else 'No'}")
        print(f"   Topic: {ch.get('topic', {}).get('value', 'N/A')}")
        print(f"   Purpose: {ch.get('purpose', {}).get('value', 'N/A')}")
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Slack Interface CLI - Interact with Slack from the command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s agents                          List available agents
  %(prog)s say -a nova "Hello team!"       Send message as Nova
  %(prog)s read -l 20                      Read last 20 messages
  %(prog)s upload design.png -m "Review"   Upload file with comment
  %(prog)s scopes                          Show token scopes

For more info: https://github.com/NinjaTech-AI/agent-team-logo-creator
        """
    )
    parser.add_argument('-T', '--token-file', default='/dev/shm/mcp-token',
                        help='Path to MCP token file (default: /dev/shm/mcp-token)')
    parser.add_argument('-C', '--config-file', default=DEFAULT_CONFIG_PATH,
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
    
    # Upload command (upload file to channel)
    upload_parser = subparsers.add_parser('upload', help='Upload a file to a channel')
    upload_parser.add_argument('file', help='Path to file to upload')
    upload_parser.add_argument('-c', '--channel', help='Override default channel')
    upload_parser.add_argument('-m', '--message', help='Comment to post with file')
    upload_parser.add_argument('--title', help='Title for the file')
    upload_parser.add_argument('-t', '--thread', help='Thread timestamp for reply')
    
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
    send_parser = subparsers.add_parser('send', help='Send a message (no agent identity)')
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
        'upload': cmd_upload,
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
    
    This class provides a convenient way to interact with Slack from Python code.
    It handles token loading, configuration, and provides simple methods for
    common operations.
    
    Attributes:
        tokens: SlackTokens instance with available tokens
        config: SlackConfig instance with user configuration
        client: SlackClient instance for API calls
    
    Example:
        from slack_interface import SlackInterface
        
        # Initialize (auto-loads tokens and config)
        slack = SlackInterface()
        
        # Check connection
        if not slack.is_connected:
            print("Please connect Slack first!")
            exit(1)
        
        # Send message to default channel
        slack.say("Hello from Python!")
        
        # Send to specific channel with custom identity
        slack.say("Hello!", channel="#general", 
                  username="Nova", icon_url="https://...")
        
        # Upload a file
        slack.upload_file("design.png", comment="New design!")
        
        # Get channel history
        messages = slack.get_history(limit=10)
        for msg in messages:
            print(f"{msg.get('user')}: {msg.get('text')}")
    """
    
    def __init__(self, token_file: str = '/dev/shm/mcp-token', 
                 config_file: str = DEFAULT_CONFIG_PATH):
        """
        Initialize Slack Interface with tokens and config.
        
        Args:
            token_file: Path to MCP token file (default: /dev/shm/mcp-token)
            config_file: Path to config file (default: ~/.slack_interface.json)
        """
        self.tokens = get_slack_tokens(token_file)
        self.config = SlackConfig.load(config_file)
        self.client = SlackClient(self.tokens)
        self._token = self.tokens.bot_token or self.tokens.access_token
    
    @property
    def default_channel(self) -> Optional[str]:
        """Get the default channel (ID preferred, then name)."""
        return self.config.get_default_channel()
    
    @property
    def default_channel_name(self) -> Optional[str]:
        """Get the default channel name (e.g., "#logo-creator")."""
        return self.config.default_channel
    
    @property
    def is_connected(self) -> bool:
        """Check if Slack is connected (tokens available)."""
        return self._token is not None
    
    def say(self, message: str, channel: Optional[str] = None, 
            thread_ts: Optional[str] = None,
            username: Optional[str] = None,
            icon_emoji: Optional[str] = None,
            icon_url: Optional[str] = None) -> Dict:
        """
        Send a message to the default channel or specified channel.
        
        Args:
            message: The message text to send (supports Slack markdown)
            channel: Optional channel override (uses default if not specified)
            thread_ts: Optional thread timestamp for replies
            username: Optional custom bot username (e.g., "Nova", "Pixel")
            icon_emoji: Optional emoji icon (e.g., ":robot_face:", ":star:")
            icon_url: Optional URL to custom icon image (overrides icon_emoji)
            
        Returns:
            Slack API response dict with 'ok', 'ts', 'channel' on success
            
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
    
    def upload_file(self, file_path: str, channel: Optional[str] = None,
                    title: Optional[str] = None, comment: Optional[str] = None,
                    thread_ts: Optional[str] = None) -> Dict:
        """
        Upload a file to the default channel or specified channel.
        
        Requires 'files:write' scope on the token.
        
        Args:
            file_path: Path to file on disk
            channel: Optional channel override (uses default if not specified)
            title: Optional title for the file
            comment: Optional comment to post with the file
            thread_ts: Optional thread timestamp for replies
            
        Returns:
            Slack API response dict with 'ok', 'file' object on success
            
        Raises:
            ValueError: If no channel specified and no default configured
            RuntimeError: If not connected to Slack
        """
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        
        target_channel = channel or self.default_channel
        if not target_channel:
            raise ValueError("No channel specified and no default configured")
        
        token = self.tokens.bot_token or self._token
        
        return self.client.upload_file(
            token, target_channel,
            file_path=file_path,
            title=title,
            initial_comment=comment,
            thread_ts=thread_ts
        )
    
    def set_default_channel(self, channel: str, config_file: str = DEFAULT_CONFIG_PATH) -> None:
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
        """
        List all channels in the workspace.
        
        Args:
            types: Comma-separated channel types to include
            
        Returns:
            List of channel dicts with 'id', 'name', 'num_members', etc.
        """
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.list_channels(self._token, types)
    
    def list_users(self) -> List[Dict]:
        """
        List all users in the workspace.
        
        Returns:
            List of user dicts with 'id', 'name', 'real_name', etc.
        """
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.list_users(self._token)
    
    def get_history(self, channel: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get channel message history.
        
        Args:
            channel: Optional channel override (uses default if not specified)
            limit: Number of messages to retrieve (default: 50)
            
        Returns:
            List of message dicts (newest first)
        """
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        target_channel = channel or self.default_channel
        if not target_channel:
            raise ValueError("No channel specified and no default configured")
        # Prefer bot token for reading (usually has channels:history scope)
        token = self.tokens.bot_token or self._token
        return self.client.get_channel_history(token, target_channel, limit)
    
    def join_channel(self, channel: str) -> Dict:
        """
        Join a channel.
        
        Args:
            channel: Channel ID to join
            
        Returns:
            API response dict
        """
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.join_channel(self._token, channel)
    
    def create_channel(self, name: str, is_private: bool = False) -> Dict:
        """
        Create a new channel.
        
        Args:
            name: Channel name (lowercase, no spaces)
            is_private: Create as private channel (default: False)
            
        Returns:
            API response dict with 'channel' object on success
        """
        if not self.is_connected:
            raise RuntimeError("Slack not connected")
        return self.client.create_channel(self._token, name, is_private)
    
    def get_scopes(self) -> List[str]:
        """
        Get available OAuth scopes for the current token.
        
        Returns:
            List of scope strings
        """
        if not self.is_connected:
            return []
        return self.client.get_scopes(self._token)


# Convenience function for quick messaging
def say(message: str, channel: Optional[str] = None, 
        username: Optional[str] = None, icon_emoji: Optional[str] = None) -> Dict:
    """
    Quick function to send a message to the default channel.
    
    This is a convenience wrapper around SlackInterface for simple use cases.
    
    Args:
        message: Message text to send
        channel: Optional channel override
        username: Optional custom username
        icon_emoji: Optional emoji icon
        
    Returns:
        Slack API response dict
        
    Example:
        from slack_interface import say
        say("Hello from Python!")
        say("Hello!", channel="#general")
        say("Hello!", username="Nova", icon_emoji=":star:")
    """
    slack = SlackInterface()
    return slack.say(message, channel, username=username, icon_emoji=icon_emoji)


if __name__ == "__main__":
    main()