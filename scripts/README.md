# Scripts

Utility scripts for managing the agent-team-logo-creator project.

## reset_project.py

Resets the project to a clean state after agents have worked on it.

### What it does:
1. **Removes agent-created files** - Deletes any files/directories not in the protected whitelist
2. **Cleans agent-docs** - Removes any files except the core spec files
3. **Resets memory files** - Restores all memory files to clean templates
4. **Deletes GitHub issues** - Permanently deletes all issues (open and closed)
5. **Commits and pushes** - Commits all changes and pushes to GitHub

### Protected files (never deleted):
- `.gitignore`, `README.md`, `cover_photo.png`
- `claude-wrapper.sh`, `orchestrator.py`, `monitor.py`
- `slack_interface.py`, `agents_config.py`, `requirements.txt`
- `WAKE_UP_PROTOCOL.md`

### Protected directories (never deleted):
- `.git`, `scripts`, `agent-docs`, `avatars`, `memory`, `reports`

### Usage:

```bash
# Dry run - see what would be deleted without making changes
python scripts/reset_project.py --dry-run

# Full reset
python scripts/reset_project.py

# Reset without closing GitHub issues
python scripts/reset_project.py --skip-issues

# Reset without git commit/push
python scripts/reset_project.py --skip-git
```

### Example output:

```
============================================================
  PROJECT RESET SCRIPT
============================================================

Project root: /workspace/agent-team-logo-creator

============================================================
  Step 1: Removing agent-created files and directories
============================================================

  Removing directory: frontend
  Removing directory: backend
  Removing file: APP_README.md

  ✓ Removed 3 items

============================================================
  Step 2: Cleaning agent-docs directory
============================================================

  Removing agent-doc: PRD.md

  ✓ Removed 1 items from agent-docs

============================================================
  Step 3: Resetting memory files
============================================================

  Resetting: memory/nova_memory.md
  Resetting: memory/pixel_memory.md
  Resetting: memory/bolt_memory.md
  Resetting: memory/scout_memory.md

  ✓ Reset 4 memory files

============================================================
  Step 4: Deleting GitHub issues
============================================================

  Deleting issue #18: Design: Create UI Mockups for Logo Creator
  Deleting issue #19: Frontend: Build React UI Components

  ✓ Deleted 2 issues

============================================================
  Step 5: Committing and pushing changes
============================================================

  ✓ Changes committed and pushed

============================================================
  RESET COMPLETE
============================================================

  ✅ Project has been reset to a clean state
```
