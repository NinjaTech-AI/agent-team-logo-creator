# Slack Interface CLI

A powerful command-line tool and Python API for interacting with Slack workspaces.

## Features

- 🔑 **Automatic Token Detection** - Reads tokens from `/dev/shm/mcp-token` or environment variables
- 📢 **Default Channel Support** - Configure a default channel for quick messaging
- 🤖 **Agent Avatars** - Send messages as specific agents with custom avatars
- 🐍 **Python API** - Use as a library in your Python scripts
- 🔍 **Scope Detection** - Shows available permissions for each token type
- 💬 **Full Slack Operations** - Send messages, list channels/users, get history, and more

## Installation

The tool is included in this repository. No additional installation required.

```bash
# Make executable (optional)
chmod +x slack_interface.py
```

### Dependencies

```bash
pip install requests
```

## Quick Start

### 1. Connect Slack

Click the **'Connect'** button in the chat interface to link your Slack workspace. This automatically provides the necessary authentication tokens.

### 2. Set Default Channel and Agent

```bash
# Set your default communication channel
python slack_interface.py config --set-channel "#logo-creator"

# Set your default agent (required for 'say' command)
python slack_interface.py config --set-agent nova
```

### 3. Send Messages

```bash
# Send as default agent to default channel
python slack_interface.py say "Hello team!"

# Send as specific agent
python slack_interface.py say -a bolt "Building the feature now!"

# Send to specific channel
python slack_interface.py say -a pixel -c "#general" "Design review ready!"
```

## Agents

The `say` command **requires an agent identity**. Either specify with `-a` flag or set a default agent.

| Agent | Role | Emoji | Color |
|-------|------|-------|-------|
| `nova` | Product Manager | 🌟 | Purple |
| `pixel` | UX Designer | 🎨 | Pink |
| `bolt` | Full-Stack Developer | ⚡ | Yellow |
| `scout` | QA Engineer | 🔍 | Green |

```bash
# List all agents
python slack_interface.py agents

# Send as specific agent
python slack_interface.py say -a nova "Sprint planning at 2pm"
python slack_interface.py say -a pixel "Mockups are ready for review"
python slack_interface.py say -a bolt "PR submitted for review"
python slack_interface.py say -a scout "Found 3 bugs in testing"
```

## Configuration

### Config File Location

The configuration is stored at `~/.slack_interface.json`:

```json
{
  "default_channel": "#logo-creator",
  "default_channel_id": "C0AAAAMBR1R",
  "default_agent": "nova",
  "workspace": "RenovateAI"
}
```

### Setting Defaults

```bash
# Set default channel (by name)
python slack_interface.py config --set-channel "#logo-creator"

# Set default channel (by ID)
python slack_interface.py config --set-channel "C0AAAAMBR1R"

# Set default agent
python slack_interface.py config --set-agent nova

# View current config
python slack_interface.py config
```

### Custom Config File

```bash
python slack_interface.py -C /path/to/config.json config
```

## CLI Commands

### Configuration

```bash
# Show current configuration
python slack_interface.py config

# Set default channel
python slack_interface.py config --set-channel "#channel-name"

# Set default agent
python slack_interface.py config --set-agent nova
```

### Messaging with Agents

```bash
# Send as default agent to default channel
python slack_interface.py say "Your message here"

# Send as specific agent
python slack_interface.py say -a bolt "Message from Bolt"

# Send to different channel
python slack_interface.py say -a nova -c "#other-channel" "Message"

# Reply in thread
python slack_interface.py say -a scout -t "1234567890.123456" "Thread reply"
```

### Generic Messaging (No Agent)

```bash
# Send to specific channel without agent identity
python slack_interface.py send "#channel" "Message"
```

### Channel Operations

```bash
# List all channels
python slack_interface.py channels

# List only public channels
python slack_interface.py channels -t public_channel

# Save to file
python slack_interface.py channels -o channels.json

# Get channel info
python slack_interface.py info "#channel-name"

# Join a channel
python slack_interface.py join "#channel-name"

# Create a channel
python slack_interface.py create new-channel-name
python slack_interface.py create private-channel --private
```

### User Operations

```bash
# List all users
python slack_interface.py users

# Include bots and deleted users
python slack_interface.py users --all

# Save to file
python slack_interface.py users -o users.json
```

### History

```bash
# Get channel history (default: 20 messages)
python slack_interface.py history "#channel-name"

# Get more messages
python slack_interface.py history "#channel-name" -l 50
```

### Token Information

```bash
# Show available scopes for each token
python slack_interface.py scopes
```

## Python API

### Basic Usage

```python
from slack_interface import SlackInterface

# Initialize
slack = SlackInterface()

# Send as default agent to default channel
slack.say("Hello team!")

# Send with custom username and icon
slack.say("Hello!", username="Nova", icon_url="https://example.com/nova.png")
```

### Full API Example

```python
from slack_interface import SlackInterface

# Initialize
slack = SlackInterface()

# Check connection
if not slack.is_connected:
    print("Please connect Slack first!")
    exit(1)

# Get default channel
print(f"Default channel: {slack.default_channel}")

# Set default channel
slack.set_default_channel("#logo-creator")

# List channels
channels = slack.list_channels()
for ch in channels:
    print(f"#{ch['name']} - {ch.get('num_members', 0)} members")

# List users
users = slack.list_users()
for user in users:
    print(f"@{user['name']} - {user.get('real_name', 'N/A')}")

# Get channel history
messages = slack.get_history(limit=10)
for msg in messages:
    print(f"{msg.get('user')}: {msg.get('text')}")

# Send message with custom identity
result = slack.say(
    "Hello from the API!",
    username="Nova",
    icon_url="https://sites.super.betamyninja.ai/.../nova.png"
)
if result.get('ok'):
    print(f"Message sent! ts={result['ts']}")

# Join a channel
slack.join_channel("#new-channel")

# Create a channel
slack.create_channel("my-new-channel", is_private=False)
```

### Error Handling

```python
from slack_interface import SlackInterface

slack = SlackInterface()

try:
    slack.say("Hello!")
except RuntimeError as e:
    print(f"Connection error: {e}")
    print("Please click 'Connect' button to link Slack")
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Set default channel with: slack.set_default_channel('#channel')")
```

## Token Sources

Tokens are loaded in this order of priority:

1. **`/dev/shm/mcp-token`** - Auto-populated when you click 'Connect' in chat
2. **Environment Variables**:
   - `SLACK_TOKEN` or `SLACK_MCP_XOXP_TOKEN` (User token)
   - `SLACK_BOT_TOKEN` or `SLACK_MCP_XOXB_TOKEN` (Bot token)

### Manual Token Setup

If you need to set tokens manually:

```bash
export SLACK_TOKEN='xoxp-your-user-token'
export SLACK_BOT_TOKEN='xoxb-your-bot-token'
```

## Token Types & Scopes

### User Token (xoxp-*)
- Full user permissions
- Can access all channels user is in
- Can search messages
- Required scopes: `channels:read`, `chat:write`, `users:read`

### Bot Token (xoxb-*)
- Bot-specific permissions
- Limited to channels bot is invited to
- Cannot search messages
- Required scopes: `channels:read`, `chat:write`, `users:read`

## Troubleshooting

### "Slack Not Connected" Error

```
======================================================================
❌ SLACK NOT CONNECTED
======================================================================

No Slack tokens found. Please connect your Slack workspace first.

👉 To connect Slack:
   Click the 'Connect' button in the chat interface to link your
   Slack workspace.
======================================================================
```

**Solution**: Click the 'Connect' button in the chat interface.

### "No agent specified" Error

```
❌ No agent specified and no default agent configured

🤖 The 'say' command requires an agent identity.

💡 To specify an agent:
   python slack_interface.py say -a nova 'message'
```

**Solution**: Either specify an agent with `-a` or set a default:
```bash
python slack_interface.py config --set-agent nova
```

### "No default channel configured" Error

**Solution**: Set a default channel:
```bash
python slack_interface.py config --set-channel "#your-channel"
```

### "channel_not_found" Error

The channel might be private or the bot isn't a member.

**Solution**: 
```bash
# Join the channel first
python slack_interface.py join "#channel-name"
```

### "missing_scope" Error

The token doesn't have required permissions.

**Solution**: Check available scopes:
```bash
python slack_interface.py scopes
```

## Examples

### Agent Communication Setup

```bash
# 1. Connect Slack (click Connect button in chat)

# 2. Set default channel for agent communication
python slack_interface.py config --set-channel "#logo-creator"

# 3. Set default agent
python slack_interface.py config --set-agent nova

# 4. Verify setup
python slack_interface.py config

# 5. Test messaging
python slack_interface.py say "🤖 Nova is online and ready!"
```

### Multi-Agent Communication

```bash
# Nova announces sprint planning
python slack_interface.py say -a nova "📋 Sprint planning starts in 10 minutes!"

# Pixel shares design updates
python slack_interface.py say -a pixel "🎨 New mockups uploaded to Figma"

# Bolt reports development progress
python slack_interface.py say -a bolt "⚡ Feature branch merged to main"

# Scout reports test results
python slack_interface.py say -a scout "🔍 All tests passing - ready for release"
```

### Channel Monitor

```python
from slack_interface import SlackInterface

slack = SlackInterface()

# Get recent messages from default channel
messages = slack.get_history(limit=5)

print("Recent messages:")
for msg in reversed(messages):
    user = msg.get('user', 'unknown')
    text = msg.get('text', '')[:50]
    print(f"  <{user}>: {text}")
```

## License

MIT License - NinjaTech AI