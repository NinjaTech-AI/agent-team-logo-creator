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

All inter-agent and human-agent communication flows through Slack:

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

### MCP Tools Available

All agents run in Claude Code with pre-configured MCPs:

| MCP | Available To | Capabilities |
|-----|--------------|--------------|
| **Slack MCP** | All agents | Post messages, read history, reply in threads, upload files |
| **Image Generation MCP** | Pixel only | Generate UI mockups, wireframes, design concepts |
| **Internet Search MCP** | All agents | Web search for research, documentation, best practices |

### Slack MCP Usage

```
# Key capabilities via Slack MCP
- Post messages to #logo-creator
- Read channel history
- Reply in threads
- Upload files (designs, reports)
- Mention other agents (@nova, @pixel, etc.)
```

### Image Generation MCP Usage (Pixel)

```
# Key capabilities via Image Generation MCP
- Generate high-fidelity UI mockups
- Create wireframes and layouts
- Design visual concepts
- Produce component designs
```

### Internet Search MCP Usage

```
# Key capabilities via Internet Search MCP
- Research best practices
- Find documentation
- Competitor analysis
- Look up error solutions
```

### GitHub Integration (via Claude Code)

```
# Key capabilities via Claude Code
- Create/update issues
- Create pull requests
- Post review comments
- Merge PRs (Nova only)
- Read repository state
- Commit code changes
```

## Security Considerations

1. **Token Management**: All API tokens stored in environment variables
2. **Least Privilege**: Each agent has only necessary permissions
3. **Audit Trail**: All actions logged in Slack and GitHub
4. **Human Override**: Humans can intervene at any point via Slack

## Scalability

The system is designed to be extensible:
- New agents can be added by implementing `BaseAgent`
- Additional integrations (Jira, Figma, etc.) can be added
- Multiple projects can run in parallel with separate channels