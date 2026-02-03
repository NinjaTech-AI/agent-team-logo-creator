# Agent Communication Protocol

## Overview

This document defines the communication standards and protocols for agent interaction within the #your-channel Slack channel using the `slack_interface.py` CLI tool.

## 🚨 CRITICAL: Workflow Dependencies

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PROJECT INITIALIZATION PROTOCOL                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   STEP 1: Nova (PM) Initializes Project                                 │
│   ─────────────────────────────────────                                 │
│   • Nova completes onboarding                                           │
│   • Nova interviews Human (stakeholders) via Slack                       │
│   • Nova writes PRD → agent-docs/PRD.md                                 │
│   • Nova creates GitHub Issues for all tasks                            │
│   • Nova assigns issues to agents                                       │
│   • Nova runs orchestrator                                              │
│                                                                          │
│   STEP 2: Other Agents Start Work                                       │
│   ───────────────────────────────                                       │
│   • Pixel, Bolt, Scout complete onboarding                              │
│   • Check for PRD: cat agent-docs/PRD.md                                │
│   • Check for assigned issues: gh issue list --assignee @me             │
│   • If no PRD/issues → ask Nova in Slack and WAIT                       │
│   • Run orchestrator: python orchestrator.py                            │
│                                                                          │
│   WAKE UP INSTRUCTION                                                    │
│   ═══════════════════                                                    │
│   When any agent receives "WAKE UP" → Run: python orchestrator.py       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Slack Interface Tool

All agents communicate via the `slack_interface.py` CLI tool. See [SLACK_INTERFACE.md](SLACK_INTERFACE.md) for complete documentation.

### Quick Reference

```bash
# Configure your agent identity (do this first!)
python slack_interface.py config --set-agent nova
python slack_interface.py config --set-channel "#your-channel"

# Read messages from the channel
python slack_interface.py read              # Last 50 messages
python slack_interface.py read -l 100       # Last 100 messages

# Send messages as configured agent
python slack_interface.py say "Message from your agent"

# Upload files
python slack_interface.py upload design.png --title "Design Mockup"
```

## Channel Structure

### Primary Channel
- **Name**: `#your-channel`
- **Purpose**: All agent and human communication
- **Visibility**: All agents + human team members

### Thread Usage
- Use threads for focused discussions on specific topics
- Main channel for announcements and sync meetings
- Threads for technical discussions, reviews, and debugging

## Agent Identities

| Agent | Slack Handle | Emoji | Color | Role |
|-------|--------------|-------|-------|------|
| Nova | `@nova` | 🌟 | Purple | PM - Initializes project, creates PRD & issues |
| Pixel | `@pixel` | 🎨 | Pink | UX - Waits for PRD & issues before designing |
| Bolt | `@bolt` | ⚡ | Yellow | Dev - Waits for PRD & issues before coding |
| Scout | `@scout` | 🔍 | Green | QA - Waits for PRD & issues before testing |
| Babak | `@babak` | 👤 | Blue | Human Product Owner |
| Arash | `@arash` | 👤 | Blue | Human Product Owner |

## Message Formats

### Project Initialization Messages

#### Nova's PRD Interview Start
```bash
python slack_interface.py say "🌟 **Nova - PRD Interview**

Hi @babak @arash! I'd like to understand your vision for this project.

**Question:** What problem are we solving with this project?

**Context:** This will help me define the core value proposition in the PRD.

Take your time - I want to make sure we capture your vision accurately!"
```

#### Nova's Issue Creation Announcement
```bash
python slack_interface.py say "🌟 **GitHub Issues Created**

I've created the following issues based on the approved PRD:

**Design Tasks (@pixel):**
- #1: Create homepage mockup
- #2: Design feature preview component

**Development Tasks (@bolt):**
- #3: Implement feature implementation API
- #4: Build frontend UI

**QA Tasks (@scout):**
- #5: Create test plan
- #6: Execute integration tests

@pixel @bolt @scout - Please check your assigned issues and begin work!"
```

#### Non-Nova Agent Waiting for Tasks
```bash
python slack_interface.py say "🎨 **Pixel - Awaiting Tasks**

@nova I've completed onboarding but don't see:
- PRD document (agent-docs/PRD.md)
- GitHub issues assigned to me

Could you please create the PRD and assign design tasks? I'm ready to start!"
```

### Sync Meeting Messages

#### Nova's Sync Start
```bash
python slack_interface.py say "🌟 **HOURLY SYNC - [TIMESTAMP]**

Good [morning/afternoon] team! Let's do a quick sync.

📋 **Agenda:**
1. Status updates from each agent
2. Blockers and dependencies
3. Task assignments for this cycle

@pixel @bolt @scout - Please share your updates."
```

#### Agent Status Update
```bash
python slack_interface.py say "[EMOJI] **[AGENT_NAME] Status Update**

✅ **Completed:**
- [Task 1]
- [Task 2]

🔄 **In Progress:**
- [Current task]

🚧 **Blockers:**
- [Blocker if any, or 'None']

📝 **Notes:**
- [Any additional context]"
```

#### Nova's Task Assignment
```bash
python slack_interface.py say "🌟 **Task Assignments - This Cycle**

@pixel:
- [ ] [Task description]
- [ ] [Task description]

@bolt:
- [ ] [Task description]

@scout:
- [ ] [Task description]

⏰ Next sync in ~1 hour. Ping me if you hit any blockers!"
```

### Work Phase Messages

#### Asking for Help
```bash
python slack_interface.py say "@[agent_name] Quick question about [topic]:
[Question details]"
```

#### Sharing Work
```bash
python slack_interface.py say "[EMOJI] **[Work Type] Update**

[Description of work completed]

📎 [Link to PR/Issue/File]

@[relevant_agent] - [Request for review/feedback if needed]"
```

#### Reporting Blockers
```bash
python slack_interface.py say "🚨 **Blocker Alert**

@nova I'm blocked on [task]:
- **Issue**: [Description]
- **Need**: [What's needed to unblock]
- **Impact**: [What's affected]"
```

### End of Cycle Messages

#### Work Summary
```bash
python slack_interface.py say "[EMOJI] **[AGENT_NAME] - Cycle Summary**

📊 **This Cycle:**
- [Accomplishment 1]
- [Accomplishment 2]

📝 **Memory Updated:** [Brief note on what was saved]

🔜 **Next Cycle:**
- [Planned work]"
```

## Communication Rules

### 1. Mention Protocol
- Always mention relevant agents when their input is needed
- Use `@nova` for escalations and blockers
- Use `@channel` sparingly (emergencies only)

### 2. Response Expectations
- During sync: Respond within the sync window
- During work phase: Respond when relevant to current task
- Blockers: Respond as soon as possible

### 3. Thread Etiquette
- Start threads for detailed discussions
- Keep main channel for high-level updates
- Summarize thread conclusions in main channel

### 4. File Sharing
**All files go to the repo, links posted to Slack:**
- Designs: Commit to `designs/` folder → post GitHub link to Slack
- Code: Commit to repo → post PR/commit link to Slack
- Documents: Commit to `docs/` folder → post GitHub link to Slack
- Test Reports: Commit to `reports/` folder → post GitHub link to Slack

**Never upload files directly to Slack** - always commit to repo first, then share the GitHub link.

## Interaction Patterns

### Nova → Other Agents
```
Direction Flow:
Nova ──assigns──▶ Pixel (design tasks)
Nova ──assigns──▶ Bolt (dev tasks)
Nova ──assigns──▶ Scout (QA tasks)

Review Flow:
Nova ◀──reviews── All agents (PRs, work)
```

### Pixel → Bolt
```
Design Handoff:
Pixel ──designs──▶ Bolt
Pixel ◀──questions── Bolt (clarifications)
```

### Bolt → Scout
```
Testing Flow:
Bolt ──code ready──▶ Scout
Bolt ◀──bug reports── Scout
```

### stakeholders → Agents
```
your stakeholders can:
- Provide direction to any agent
- Override agent decisions
- Approve/reject work
- Add context and requirements
- All agents take orders from stakeholders
```

## GitHub Integration Protocol

### Issue References
```
When referencing GitHub issues in Slack:
"Working on #42 - [Issue Title]"
```

### PR Notifications
```bash
python slack_interface.py say "🔀 PR Ready: [Title] - [GitHub Link]
@nova ready for review"
```

### Code Review Comments
```bash
python slack_interface.py say "📝 Review feedback on PR #[number]:
- [Comment 1]
- [Comment 2]
@bolt please address these"
```

## Error Handling

### Agent Failure
```
If an agent fails to respond during sync:
1. Nova notes the absence
2. Work continues with available agents
3. Failed agent catches up next cycle via memory
```

### Integration Failure
```
If Slack is unavailable:
1. Agent logs the failure
2. Retries with exponential backoff
3. Stores pending messages for later delivery
```

## Escalation to stakeholders

### When to Escalate to stakeholders
- Conflicting requirements
- Technical decisions with major impact
- Blockers that can't be resolved by agents
- Approval needed for significant changes

### Escalation Format
```bash
python slack_interface.py say "👤 **stakeholders Input Needed**

@babak @arash We need your input on:
- **Topic**: [Description]
- **Options**: 
  1. [Option A]
  2. [Option B]
- **Recommendation**: [Agent's suggestion]
- **Deadline**: [When decision is needed]"
```

## Running the Orchestrator

After completing onboarding, all agents should run:

```bash
python orchestrator.py
```

This starts:
- **Nova**: Work process + Monitor process (watches for Slack mentions)
- **Other agents**: Work process only