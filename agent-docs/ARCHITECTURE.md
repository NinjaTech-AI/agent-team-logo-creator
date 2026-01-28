# System Architecture

## Overview

The Agent Team Logo Creator is a multi-agent collaborative system where AI agents work together to build a logo creation application. The system is designed around asynchronous collaboration with periodic synchronization.

## Core Components

### 1. Agent Layer

Four specialized agents, each with distinct responsibilities:

```
┌────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                │
├─────────────┬─────────────┬─────────────┬─────────────────────────┤
│    NOVA     │    PIXEL    │    BOLT     │         SCOUT           │
│     PM      │     UX      │     Dev     │          QA             │
├─────────────┼─────────────┼─────────────┼─────────────────────────┤
│ • Planning  │ • Wireframes│ • Frontend  │ • Test Plans            │
│ • Issues    │ • Mockups   │ • Backend   │ • Bug Reports           │
│ • Reviews   │ • UX Flows  │ • APIs      │ • Validation            │
│ • Coord.    │ • Assets    │ • Deploy    │ • Regression            │
└─────────────┴─────────────┴─────────────┴─────────────────────────┘
```

### 2. Communication Layer

All inter-agent and human-agent communication flows through Slack using the `slack_interface.py` CLI tool:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SLACK: #logo-creator                          │
│                                                                  │
│  Message Types:                                                  │
│  • @nova - PM directives, task assignments                      │
│  • @pixel - Design updates, mockup shares                       │
│  • @bolt - Code updates, technical questions                    │
│  • @scout - Test results, bug reports                           │
│  • @human - Direction, feedback, approvals                      │
│                                                                  │
│  Threads: Used for focused discussions on specific topics       │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Persistence Layer

#### GitHub Repository
- Source code
- Issues and project tracking
- Pull requests and code reviews
- Documentation

#### Memory Files
- Agent-specific context persistence
- Work history and decisions
- Cross-session continuity

```
┌─────────────────────────────────────────────────────────────────┐
│                      PERSISTENCE LAYER                           │
├────────────────────────────┬────────────────────────────────────┤
│         GITHUB             │            MEMORY FILES            │
├────────────────────────────┼────────────────────────────────────┤
│ • Code commits             │ • nova_memory.md                   │
│ • Issues/PRs               │ • pixel_memory.md                  │
│ • Reviews/Comments         │ • bolt_memory.md                   │
│ • Project boards           │ • scout_memory.md                  │
└────────────────────────────┴────────────────────────────────────┘
```

### 4. Orchestration Layer

The orchestrator manages the agent lifecycle:

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                                │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  Scheduler  │───▶│ Sync Manager│───▶│   Agents    │         │
│  │  (Hourly)   │    │             │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│  Responsibilities:                                               │
│  • Trigger hourly syncs                                         │
│  • Coordinate agent wake-up sequence                            │
│  • Manage sync meeting flow                                     │
│  • Handle failures and retries                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Hourly Sync Cycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  WAKE UP │────▶│   SYNC   │────▶│   WORK   │────▶│  COMMIT  │
│          │     │ MEETING  │     │  PHASE   │     │ & MEMORY │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     ▼                ▼                ▼                ▼
 Orchestrator    Slack Channel    Independent      GitHub +
triggers all    #logo-creator    task execution   Memory files
agents          Nova leads
```

### Detailed Sync Flow

```
Time: T+0 (Sync Start)
├── Orchestrator triggers sync
├── All agents wake up
├── Agents read their memory files
└── Agents join #logo-creator

Time: T+1 (Standup)
├── Nova posts sync agenda
├── Each agent reports:
│   ├── What they completed
│   ├── What they're working on
│   └── Any blockers
└── Nova assigns/clarifies tasks

Time: T+2 to T+55 (Work Phase)
├── Agents work independently
├── Async communication in Slack as needed
├── Code commits to GitHub
└── Design uploads, test runs, etc.

Time: T+55 (Wrap Up)
├── Agents summarize work
├── Update memory files
├── Post summary to Slack
└── Agents go idle until next sync
```

## Integration Points

### Tools Available

All agents have access to the following tools:

| Tool | Available To | Capabilities |
|------|--------------|--------------|
| **slack_interface.py** | All agents | Send/read messages, list channels/users, manage communication |
| **Image Generation** | Pixel only | Generate UI mockups, wireframes, design concepts |
| **Internet Search** | All agents | Web search for research, documentation, best practices |
| **GitHub CLI** | All agents | Code commits, issues, PRs, reviews |

### Slack Interface Usage

The `slack_interface.py` CLI tool provides all Slack communication capabilities:

```bash
# Read messages from default channel
python slack_interface.py read
python slack_interface.py read -l 50  # Last 50 messages

# Send messages as an agent
python slack_interface.py say -a nova "Sprint planning at 2pm"
python slack_interface.py say -a pixel "Design mockups ready for review"
python slack_interface.py say -a bolt "PR submitted for review"
python slack_interface.py say -a scout "All tests passing"

# Configuration
python slack_interface.py config --set-channel "#logo-creator"
python slack_interface.py config --set-agent nova

# Other operations
python slack_interface.py channels    # List channels
python slack_interface.py users       # List users
python slack_interface.py history "#channel"  # Get specific channel history
```

See [SLACK_INTERFACE.md](SLACK_INTERFACE.md) for complete documentation.

### Image Generation Usage (Pixel)

```
# Key capabilities via Image Generation
- Generate high-fidelity UI mockups
- Create wireframes and layouts
- Design visual concepts
- Produce component designs
```

### Internet Search Usage

```
# Key capabilities via Internet Search
- Research best practices
- Find documentation
- Competitor analysis
- Look up error solutions
```

### GitHub Integration (via CLI)

```bash
# Key capabilities via GitHub CLI
gh issue create --title "Bug: ..." --body "..."
gh pr create --title "Feature: ..." --body "..."
gh pr review --approve
git commit -m "feat: ..."
git push origin main
```

## Security Considerations

1. **Token Management**: All API tokens stored securely in `/dev/shm/mcp-token`
2. **Least Privilege**: Each agent has only necessary permissions
3. **Audit Trail**: All actions logged in Slack and GitHub
4. **Human Override**: Humans can intervene at any point via Slack

## Scalability

The system is designed to be extensible:
- New agents can be added by implementing `BaseAgent`
- Additional integrations (Jira, Figma, etc.) can be added
- Multiple projects can run in parallel with separate channels