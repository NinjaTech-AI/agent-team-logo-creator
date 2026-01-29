# Agent Team Logo Creator

A multi-agent AI system for creating team logos, powered by collaborative AI agents communicating via Slack.

## 🤖 The Agent Team

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Nova** 🌟 | Product Manager | PRD interviews with Babak/Arash, GitHub issues/PRs, task coordination, code reviews |
| **Pixel** 🎨 | UX Designer | High-level UX designs as images, wireframes, visual mockups |
| **Bolt** ⚡ | Full-Stack Developer | Frontend & backend implementation, code commits |
| **Scout** 🔍 | QA Engineer | Testing, bug reports, quality assurance |

## 👤 Human Stakeholders

**Babak and Arash** - Product Owners
- Provide product vision and requirements
- Participate in PRD interviews with Nova
- Review and approve key decisions
- Available in #logo-creator Slack channel
- All agents take orders from Babak or Arash

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATOR                               │
│                    (src/orchestrator.py)                         │
│                                                                  │
│   Runs Claude Code 4 times per sync cycle, once per agent       │
│   Each agent's prompt is built from their spec MD file          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TOOLS                                    │
│                                                                  │
│   ┌─────────────────┐  ┌─────────────┐  ┌─────────────┐         │
│   │slack_interface  │  │ Image Gen   │  │  Internet   │         │
│   │  (all agents)   │  │(Pixel only) │  │   Search    │         │
│   └─────────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AGENT SPECS (Prompts)                        │
│                      agent-docs/*.md                             │
│                                                                  │
│   NOVA_SPEC.md → PIXEL_SPEC.md → BOLT_SPEC.md → SCOUT_SPEC.md  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     SLACK CHANNEL                                │
│                    #logo-creator                                 │
│                                                                  │
│   All agents + Babak/Arash communicate here                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MEMORY FILES                                │
│                       memory/*.md                                │
│                                                                  │
│   Each agent persists context between sessions                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔧 Tools

Agents have access to these tools:

| Tool | Available To | Purpose |
|------|--------------|---------|
| **slack_interface.py** | All agents | Communication in #logo-creator |
| **Image Generation** | Pixel | Create UI mockups, wireframes, designs |
| **Internet Search** | All agents | Research, documentation, best practices |
| **GitHub CLI** | All agents | Code commits, issues, PRs |

### Slack Interface

All agent communication uses the `slack_interface.py` CLI tool:

```bash
# First-time setup (required)
python slack_interface.py config --set-channel "#logo-creator"
python slack_interface.py config --set-agent nova

# Send messages as configured agent
python slack_interface.py say "Sprint planning at 2pm!"

# Read messages from the channel
python slack_interface.py read              # Last 50 messages
python slack_interface.py read -l 100       # Last 100 messages

# Upload files
python slack_interface.py upload design.png --title "New Design"

# Show configuration
python slack_interface.py config
```

See [agent-docs/SLACK_INTERFACE.md](agent-docs/SLACK_INTERFACE.md) for complete documentation.

## 🔄 How It Works

### Simple Orchestration

The orchestrator runs Claude Code **4 times per sync cycle**:

1. **Nova** (PM) - Reads spec from `NOVA_SPEC.md`, checks Slack, manages project
2. **Pixel** (UX) - Reads spec from `PIXEL_SPEC.md`, creates designs
3. **Bolt** (Dev) - Reads spec from `BOLT_SPEC.md`, writes code
4. **Scout** (QA) - Reads spec from `SCOUT_SPEC.md`, tests and reports bugs

Each agent:
- Gets their behavior/personality from their spec MD file
- Reads their memory file for previous context
- Communicates via Slack #logo-creator channel using `slack_interface.py`
- Updates their memory file after work
- Commits work to GitHub

### PRD Creation Phase

Before development begins:
1. **Nova interviews Babak/Arash** - Gathers requirements through structured questions in Slack
2. **Nova drafts PRD** - Documents vision, features, and acceptance criteria
3. **Babak/Arash review & approve** - PRD finalized before development begins

### Hourly Sync Cycle

1. **Wake Up** - Orchestrator triggers all agents
2. **Sync Meeting** - Agents post status updates to #logo-creator
3. **Work Phase** - Agents execute their tasks
4. **Commit & Document** - Agents update memory and push to GitHub

## 📁 Project Structure

```
agent-team-logo-creator/
├── README.md
├── requirements.txt
├── slack_interface.py       # Slack communication CLI tool
│
├── agent-docs/              # Agent specifications (prompts)
│   ├── ARCHITECTURE.md
│   ├── AGENT_PROTOCOL.md
│   ├── ONBOARDING.md        # Agent onboarding guide
│   ├── SLACK_INTERFACE.md   # Slack tool documentation
│   ├── NOVA_SPEC.md         # Nova's behavior & personality
│   ├── PIXEL_SPEC.md        # Pixel's behavior & personality
│   ├── BOLT_SPEC.md         # Bolt's behavior & personality
│   ├── SCOUT_SPEC.md        # Scout's behavior & personality
│   └── PRD.md               # Product Requirements (created by Nova)
│
├── memory/                  # Agent memory files
│   ├── nova_memory.md
│   ├── pixel_memory.md
│   ├── bolt_memory.md
│   └── scout_memory.md
│
├── avatars/                 # Agent avatar images
│   ├── nova.png
│   ├── pixel.png
│   ├── bolt.png
│   └── scout.png
│
└── src/                     # Orchestrator code
    └── orchestrator.py      # Main orchestrator
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Claude Code CLI
- GitHub CLI (`gh`)
- Slack workspace with #logo-creator channel
- Bot token with required scopes (channels:history, chat:write, etc.)

### First-Time Setup: Onboarding

When an agent wakes up for the first time, follow the [Onboarding Guide](agent-docs/ONBOARDING.md):

1. **Read your agent specification** - Understand your role and responsibilities
2. **Configure Slack** - Set default channel and agent identity
3. **Test capabilities** - Verify all tools work
4. **Check memory** - Read context from previous sessions

⚠️ **IMPORTANT**: Agents should **never assume** anything. If information is missing, use the `ask` tool to request clarification from the user.

See [agent-docs/ONBOARDING.md](agent-docs/ONBOARDING.md) for complete documentation.

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Slack (required before use)
python slack_interface.py config --set-channel "#logo-creator"
python slack_interface.py config --set-agent nova

# Test Slack connection
python slack_interface.py scopes
python slack_interface.py read
```

### Usage

```bash
# Run all agents (Nova → Pixel → Bolt → Scout)
python src/orchestrator.py

# Run a specific agent
python src/orchestrator.py --agent Nova
python src/orchestrator.py --agent Pixel --task "Create homepage wireframe"

# List available agents
python src/orchestrator.py --list
```

## 📄 License

MIT License - NinjaTech AI