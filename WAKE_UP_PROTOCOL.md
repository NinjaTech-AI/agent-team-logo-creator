# Wake-Up Protocol

When you are "woken up" (i.e., asked to do summarization and reporting on running services), you MUST:

## 1. Read All Documentation First

Before doing anything else, read these files in order:

```bash
# Core documentation
cat README.md
cat ARCHITECTURE.md
cat AGENT_PROTOCOL.md

# Agent specifications
cat agent-docs/NOVA_SPEC.md
cat agent-docs/PIXEL_SPEC.md
cat agent-docs/BOLT_SPEC.md
cat agent-docs/SCOUT_SPEC.md

# Onboarding and Slack
cat agent-docs/ONBOARDING.md
cat agent-docs/SLACK_INTERFACE.md
```

## 2. Run Onboarding

After reading documentation, run the onboarding process:

```bash
cd /workspace/agent-team-logo-creator
python onboarding.py --check  # Check current status first
python onboarding.py          # Run full onboarding if needed
```

## 3. Then Proceed with Tasks

Only after completing steps 1 and 2 should you proceed with any other tasks.

---

**This protocol ensures continuity between sessions and proper agent identity.**
