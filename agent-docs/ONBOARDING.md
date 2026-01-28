# Agent Onboarding Guide

## Overview

When an agent wakes up for the first time, it must complete the onboarding process before starting work. This ensures all tools are configured and working properly.

## Quick Start

```bash
# Run onboarding
python onboarding.py

# Check if onboarding is complete
python onboarding.py --check

# Reset and re-run onboarding
python onboarding.py --reset
```

## Onboarding Process

### 1. Agent Identity

The agent identifies itself:
- **Nova** - Product Manager
- **Pixel** - UX Designer
- **Bolt** - Full-Stack Developer
- **Scout** - QA Engineer

### 2. Slack Configuration

Configure the default communication channel:
- Default channel (e.g., `#logo-creator`)
- Channel ID is auto-resolved

### 3. Schedule Configuration

Set up the work schedule:
- **Sync interval** - How often to sync (default: 60 minutes)
- **Work hours start** - When to start working (default: 09:00)
- **Work hours end** - When to stop working (default: 17:00)
- **Timezone** - Your timezone (default: UTC)

### 4. Capability Tests

The onboarding script tests all required capabilities:

#### Slack Test
```bash
python slack_interface.py scopes
```
- Verifies Slack connection
- Checks for required scopes (channels:history, chat:write)

#### GitHub Test
```bash
gh auth status
```
- Verifies GitHub CLI authentication
- Shows current repository

#### Claude Test
```bash
claude -p "hello world"
```
- Verifies Claude CLI is working
- Tests basic prompt execution

### 5. Integration Test

Optionally sends a test message to Slack:
```bash
python slack_interface.py say -a [agent] "🚀 Onboarding test..."
```

## Configuration Files

### Agent Config (`~/.agent_config.json`)

```json
{
  "onboarding_complete": true,
  "onboarding_date": "2024-01-22T10:00:00",
  "agent_name": "Nova",
  "default_channel": "#logo-creator",
  "default_channel_id": "C0AAAAMBR1R",
  "schedule": {
    "sync_interval_minutes": 60,
    "work_hours_start": "09:00",
    "work_hours_end": "17:00",
    "timezone": "UTC"
  },
  "capabilities_tested": {
    "slack": true,
    "github": true,
    "claude": true
  },
  "github_repo": "NinjaTech-AI/agent-team-logo-creator",
  "last_sync": null
}
```

### Slack Config (`~/.slack_interface.json`)

```json
{
  "default_channel": "#logo-creator",
  "default_channel_id": "C0AAAAMBR1R",
  "default_agent": "nova"
}
```

## First Wake-Up Checklist

When an agent wakes up for the first time:

### Step 1: Check Onboarding Status
```bash
python onboarding.py --check
```

If not complete, run onboarding:
```bash
python onboarding.py
```

### Step 2: Verify Capabilities

After onboarding, verify each capability manually:

```bash
# Test Slack read
python slack_interface.py read -l 5

# Test Slack send
python slack_interface.py say -a [agent] "Hello team! I'm online."

# Test GitHub
gh repo view

# Test Claude
claude -p "What is 2+2?"
```

### Step 3: Read Your Spec

Each agent should read their specification:
- Nova: `agent-docs/NOVA_SPEC.md`
- Pixel: `agent-docs/PIXEL_SPEC.md`
- Bolt: `agent-docs/BOLT_SPEC.md`
- Scout: `agent-docs/SCOUT_SPEC.md`

### Step 4: Check Memory

Read your memory file for context from previous sessions:
- Nova: `memory/nova_memory.md`
- Pixel: `memory/pixel_memory.md`
- Bolt: `memory/bolt_memory.md`
- Scout: `memory/scout_memory.md`

### Step 5: Announce Yourself

Post a message to the team:
```bash
python slack_interface.py say -a [agent] "🌟 [Agent] is online and ready to work!"
```

## Troubleshooting

### Slack Connection Failed

1. Check token file exists:
   ```bash
   cat /dev/shm/mcp-token | grep Slack
   ```

2. Verify token scopes:
   ```bash
   python slack_interface.py scopes
   ```

3. Required scopes:
   - `channels:history` - Read messages
   - `chat:write` - Send messages
   - `channels:read` - List channels

### GitHub Authentication Failed

1. Check auth status:
   ```bash
   gh auth status
   ```

2. Login if needed:
   ```bash
   gh auth login
   ```

3. Verify repo access:
   ```bash
   gh repo view
   ```

### Claude CLI Failed

1. Check if claude is installed:
   ```bash
   which claude
   ```

2. Test basic prompt:
   ```bash
   claude -p "hello"
   ```

3. Check for errors in output

## Re-Onboarding

To reset and re-run onboarding:

```bash
# Reset configuration
python onboarding.py --reset

# Run onboarding again
python onboarding.py
```

## Integration with Orchestrator

The orchestrator checks onboarding status before running an agent:

```python
# In orchestrator.py
def run_agent(agent_name):
    # Check onboarding
    result = subprocess.run(["python", "onboarding.py", "--check"])
    if result.returncode != 0:
        print(f"⚠️ {agent_name} needs onboarding!")
        subprocess.run(["python", "onboarding.py"])
    
    # Continue with agent execution...
```

## Example Onboarding Session

```
======================================================================
🚀 AGENT ONBOARDING
======================================================================

Welcome! This script will configure your agent environment.
Please answer the following questions to complete setup.

--------------------------------------------------
📋 AGENT IDENTITY
--------------------------------------------------

Which agent are you?
  1. Nova (default)
  2. Pixel
  3. Bolt
  4. Scout

Enter number or name: 1

👋 Hello, Nova!

--------------------------------------------------
📋 SLACK CONFIGURATION
--------------------------------------------------

Fetching available channels...
Found 5 channels
Default Slack channel [#logo-creator]: 

--------------------------------------------------
📋 SCHEDULE CONFIGURATION
--------------------------------------------------

Sync interval in minutes [60]: 
Work hours start (HH:MM) [09:00]: 
Work hours end (HH:MM) [17:00]: 
Timezone [UTC]: 

--------------------------------------------------
📋 CAPABILITY TESTS
--------------------------------------------------

Running capability tests...

🔍 Testing Slack connection...
✅ Slack connection successful!
   ✅ Can read channel history
   ✅ Can send messages

🔍 Testing GitHub connection...
✅ GitHub CLI authenticated!
   📁 Current repo: NinjaTech-AI/agent-team-logo-creator

🔍 Testing Claude CLI...
✅ Claude CLI working!
   Response: Hello! How can I help you today?...

--------------------------------------------------
📋 INTEGRATION TEST
--------------------------------------------------

Send a test message to Slack? (yes/no) [yes]: yes

🔍 Testing Slack send as Nova...
✅ Successfully sent test message!

--------------------------------------------------
📋 ONBOARDING SUMMARY
--------------------------------------------------

Agent: Nova
Default Channel: #logo-creator
Schedule: Every 60 minutes
Work Hours: 09:00 - 17:00 UTC

Capabilities:
  Slack: ✅
  GitHub: ✅
  Claude: ✅

✅ Configuration saved to /root/.agent_config.json
✅ Slack configuration saved to /root/.slack_interface.json

======================================================================
🎉 ONBOARDING COMPLETE!
======================================================================

📖 Next steps for Nova:
   1. Read your spec: agent-docs/NOVA_SPEC.md
   2. Check Slack: python slack_interface.py read
   3. Start working!
```