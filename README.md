# Agent Team Logo Creator

A multi-agent AI system for creating team logos, powered by collaborative AI agents communicating via Slack.

## 🤖 The Agent Team

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Nova** 🌟 | Product Manager | PRD interviews with Arash, GitHub issues/PRs, task coordination, code reviews |
| **Pixel** 🎨 | UX Designer | High-level UX designs as images, wireframes, visual mockups |
| **Bolt** ⚡ | Full-Stack Developer | Frontend & backend implementation, code commits |
| **Scout** 🔍 | QA Engineer | Testing, bug reports, quality assurance |

## 👤 Human Stakeholder

**Arash Sadrieh** - Product Owner
- Provides product vision and requirements
- Participates in PRD interviews with Nova
- Reviews and approves key decisions
- Available in #logo-creator Slack channel

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATOR                               │
│                    (src/orchestrator.py)                         │
│                                                                  │
│   Runs Claude Code 4 times per sync cycle, once per agent       │
│   Each agent's prompt is built from their spec MD file          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT SPECS (Prompts)                        │
│                      agent-docs/*.md                             │
│                                                                  │
│   NOVA_SPEC.md → Pixel_SPEC.md → BOLT_SPEC.md → SCOUT_SPEC.md  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SLACK CHANNEL                                │
│                    #logo-creator                                 │
│                                                                  │
│   All agents + Arash communicate here                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MEMORY FILES                                │
│                       memory/*.md                                │
│                                                                  │
│   Each agent persists context between sessions                  │
└─────────────────────────────────────────────────────────────────┘
```

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
- Communicates via Slack #logo-creator channel
- Updates their memory file after work
- Commits work to GitHub

### PRD Creation Phase

Before development begins:
1. **Nova interviews Arash** - Gathers requirements through structured questions in Slack
2. **Nova drafts PRD** - Documents vision, features, and acceptance criteria
3. **Arash reviews & approves** - PRD finalized before development begins

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
├── .env.example
│
├── agent-docs/              # Agent specifications (prompts)
│   ├── ARCHITECTURE.md
│   ├── AGENT_PROTOCOL.md
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
└── src/                     # Orchestrator code
    ├── orchestrator.py      # Main orchestrator
    └── config.py            # Configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Claude Code CLI installed
- Slack Workspace with Bot Token
- GitHub Personal Access Token

### Installation

```bash
# Clone the repository
git clone https://github.com/NinjaTech-AI/agent-team-logo-creator.git
cd agent-team-logo-creator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Usage

```bash
# Run full sync cycle (all 4 agents)
python src/orchestrator.py --sync

# Run a specific agent
python src/orchestrator.py --agent Nova
python src/orchestrator.py --agent Pixel --task "Create homepage wireframe"

# List available agents
python src/orchestrator.py --list
```

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `SLACK_BOT_TOKEN` | Slack Bot OAuth Token |
| `SLACK_CHANNEL_ID` | ID of #logo-creator channel |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `GITHUB_REPO` | Repository name (owner/repo) |
| `CLAUDE_MODEL` | Claude model to use |
| `SYNC_INTERVAL_MINUTES` | Minutes between sync cycles |

## 📝 Customizing Agents

Each agent's behavior is defined in their spec MD file:

- **`agent-docs/NOVA_SPEC.md`** - Edit to change Nova's PM behavior
- **`agent-docs/PIXEL_SPEC.md`** - Edit to change Pixel's design approach
- **`agent-docs/BOLT_SPEC.md`** - Edit to change Bolt's coding style
- **`agent-docs/SCOUT_SPEC.md`** - Edit to change Scout's testing strategy

The orchestrator reads these files and uses them as prompts for Claude Code.

## 📄 License

MIT License - NinjaTech AI