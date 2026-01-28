#!/usr/bin/env python3
"""
Slack Interface CLI

A command-line tool to interact with Slack using tokens from /dev/shm/mcp-token.
Automatically detects available scopes and provides various Slack operations.

Usage:
    python slack_interface.py --help
    python slack_interface.py scopes          # Show available scopes for each token
    python slack_interface.py channels        # List all channels
    python slack_interface.py users           # List all users
    python slack_interface.py send <channel> <message>  # Send a message
    python slack_interface.py history <channel>         # Get channel history
"""

import argparse
import json
import os
import sys
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


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
                     thread_ts: Optional[str] = None) -> Dict:
        """Send a message to a channel"""
        params = {
            "channel": channel,
            "text": text
        }
        if thread_ts:
            params["thread_ts"] = thread_ts
        
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
  %(prog)s scopes                    Show available scopes for each token
  %(prog)s channels                  List all channels
  %(prog)s channels -t public_channel  List only public channels
  %(prog)s users                     List all users
  %(prog)s history C048ANAEC8P       Get history for channel by ID
  %(prog)s history "#general"        Get history for channel by name
  %(prog)s send "#general" "Hello!"  Send a message
  %(prog)s join "#logo-creator"      Join a channel
  %(prog)s create logo-creator       Create a new channel
  %(prog)s info "#general"           Get channel info
        """
    )
    
    parser.add_argument('--token-file', '-f', default='/dev/shm/mcp-token',
                        help='Path to token file (default: /dev/shm/mcp-token)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
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


if __name__ == "__main__":
    main()