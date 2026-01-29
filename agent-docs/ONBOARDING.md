# Agent Onboarding Guide

## Overview

When an agent wakes up, it must complete the onboarding process before starting work. This ensures all tools are configured and the agent understands its environment.

## ⚠️ CRITICAL: Never Assume - Always Ask

**The most important rule for agents: DO NOT ASSUME ANYTHING.**

If you need information that is not explicitly provided, you MUST use the `ask` tool to request clarification from the user. Never make assumptions about:
- User preferences
- Project requirements
- Technical decisions
- File locations
- Configuration values

### Using the `ask` Tool

The `ask` tool is your primary way to get information from users. Use it whenever:
- Requirements are unclear
- You need to make a decision that affects the user
- Information is missing
- You need confirmation before proceeding

**Example - Asking for clarification:**
```
I need some information before proceeding:

1. What is the target channel for Slack messages?
2. Which agent identity should I use (nova, pixel, bolt, scout)?
3. Are there any specific requirements I should know about?

Please provide these details so I can configure correctly.
```

**Example - Confirming before action:**
```
I'm about to send a message to #general as Nova. 

Should I proceed? (yes/no)
```

**Example - Requesting missing information:**
```
I noticed the configuration file is missing the following required fields:
- default_channel
- default_agent

Could you please provide these values?
```

## Onboarding Steps

### Step 1: Read Documentation

Read all relevant documentation files:

```bash
# Read your agent specification
cat agent-docs/NOVA_SPEC.md      # For Nova
cat agent-docs/PIXEL_SPEC.md     # For Pixel
cat agent-docs/BOLT_SPEC.md      # For Bolt
cat agent-docs/SCOUT_SPEC.md     # For Scout

# Read the architecture
cat agent-docs/ARCHITECTURE.md

# Read the agent protocol
cat agent-docs/AGENT_PROTOCOL.md

# Read the Slack interface docs
cat agent-docs/SLACK_INTERFACE.md
```

### Step 2: Check Slack Connection

Test that Slack is properly configured:

```bash
# Check token scopes
python slack_interface.py scopes

# List available channels
python slack_interface.py channels

# Show current configuration
python slack_interface.py config
```

### Step 3: Configure Defaults (If Not Set)

If configuration is missing, **ASK THE USER** what values to use:

```bash
# Set default channel (after asking user)
python slack_interface.py config --set-channel "#channel-name"

# Set default agent (after asking user)
python slack_interface.py config --set-agent nova
```

### Step 4: Test Capabilities

Run these tests to verify everything works:

```bash
# Test 1: Read messages from channel
python slack_interface.py read -l 5

# Test 2: Send a test message
python slack_interface.py say "Hello! Agent online and ready."

# Test 3: Check GitHub access
gh repo view

# Test 4: List files in project
ls -la
```

### Step 5: Check Memory

Read your memory file for context from previous sessions:

```bash
cat memory/nova_memory.md      # For Nova
cat memory/pixel_memory.md     # For Pixel
cat memory/bolt_memory.md      # For Bolt
cat memory/scout_memory.md     # For Scout
```

## Configuration Files

### Slack Config (`~/.agent_settings.json`)

```json
{
  "default_channel": "#logo-creator",
  "default_channel_id": "C0AAAAMBR1R",
  "default_agent": "nova",
  "workspace": "RenovateAI",
  "bot_token": "xoxb-...",
  "access_token": "xoxp-..."
}
```

## Agent Identities

| Agent | Role | Emoji |
|-------|------|-------|
| Nova | Product Manager | 🌟 |
| Pixel | UX Designer | 🎨 |
| Bolt | Full-Stack Developer | ⚡ |
| Scout | QA Engineer | 🔍 |

## Quick Test Commands

```bash
# Test Slack connection
python slack_interface.py scopes

# Test sending message
python slack_interface.py say "Test message"

# Test file upload
python slack_interface.py upload avatars/nova.png --title "Test Upload"

# Test reading messages
python slack_interface.py read -l 10

# Test GitHub
gh issue list
gh pr list
```

## Troubleshooting

### Slack Connection Failed

```bash
# Check if tokens are cached
cat ~/.agent_settings.json

# Check token file
cat /dev/shm/mcp-token | grep Slack

# Verify scopes
python slack_interface.py scopes
```

### Missing Configuration

**DO NOT GUESS VALUES.** Use the `ask` tool to request the information:

```
I need to configure the Slack interface but the following settings are missing:
- Default channel
- Default agent

What values should I use for these settings?
```

### GitHub Authentication Failed

```bash
# Check auth status
gh auth status

# View current repo
gh repo view
```

## Remember: Always Ask!

When in doubt, use the `ask` tool. It's better to ask for clarification than to make incorrect assumptions. The user will appreciate being consulted rather than having to fix mistakes later.

**Good practice:**
- Ask before sending messages to channels
- Ask before making configuration changes
- Ask when requirements are ambiguous
- Ask when you need to choose between options

**Bad practice:**
- Assuming default values
- Guessing user preferences
- Making decisions without confirmation
- Proceeding when information is missing