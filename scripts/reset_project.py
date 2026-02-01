#!/usr/bin/env python3
"""
Project Reset Script

This script resets the agent-team-logo-creator project to a clean state after agents have worked on it.
It removes all agent-created files, resets memory files, and closes GitHub issues.

Usage:
    python scripts/reset_project.py [--dry-run] [--skip-issues] [--skip-git]

Options:
    --dry-run       Show what would be deleted without actually deleting
    --skip-issues   Skip closing GitHub issues
    --skip-git      Skip git commit and push
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

# Project root directory
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# =============================================================================
# CONFIGURATION - Directories and files to preserve (whitelist)
# =============================================================================

# Directories that should NEVER be deleted
PROTECTED_DIRS = {
    '.git',
    'scripts',
    'agent-docs',
    'avatars',
    'memory',
    'reports',
}

# Files that should NEVER be deleted
PROTECTED_FILES = {
    '.gitignore',
    'README.md',
    'cover_photo.png',
    'claude-wrapper.sh',
    'orchestrator.py',
    'monitor.py',
    'slack_interface.py',
    'agents_config.py',
    'requirements.txt',
    'WAKE_UP_PROTOCOL.md',
}

# Files in agent-docs that should be preserved
PROTECTED_AGENT_DOCS = {
    'AGENT_PROTOCOL.md',
    'ARCHITECTURE.md',
    'BOLT_SPEC.md',
    'NOVA_SPEC.md',
    'ONBOARDING.md',
    'PIXEL_SPEC.md',
    'SCOUT_SPEC.md',
    'SLACK_INTERFACE.md',
}

# =============================================================================
# MEMORY FILE TEMPLATES
# =============================================================================

MEMORY_TEMPLATES = {
    'nova_memory.md': '''# Nova Memory

## Session Log
<!-- Nova will record session notes here -->

## Decisions Made
<!-- Important decisions and their rationale -->

## Pending Items
<!-- Items to follow up on -->
''',
    'pixel_memory.md': '''# Pixel Memory

## Session Log
<!-- Pixel will record session notes here -->

## Design Decisions
<!-- Design choices and their rationale -->

## Pending Items
<!-- Items to follow up on -->
''',
    'bolt_memory.md': '''# Bolt Memory

## Session Log
<!-- Bolt will record session notes here -->

## Technical Decisions
<!-- Technical choices and their rationale -->

## Pending Items
<!-- Items to follow up on -->
''',
    'scout_memory.md': '''# Scout Memory

## Session Log
<!-- Scout will record session notes here -->

## QA Findings
<!-- Test results and issues found -->

## Pending Items
<!-- Items to follow up on -->
''',
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def run_command(cmd, capture=True, check=True):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture, 
            text=True, 
            check=check,
            cwd=PROJECT_ROOT
        )
        return result.stdout.strip() if capture else None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Command failed: {cmd}")
        print(f"      Error: {e.stderr}")
        return None

def print_header(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_action(action, item, dry_run=False):
    """Print an action being taken."""
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"  {prefix}{action}: {item}")

# =============================================================================
# CLEANUP FUNCTIONS
# =============================================================================

def find_files_to_delete():
    """Find all files and directories that should be deleted."""
    to_delete = {
        'dirs': [],
        'files': [],
    }
    
    for item in PROJECT_ROOT.iterdir():
        name = item.name
        
        # Skip protected items
        if name in PROTECTED_DIRS or name in PROTECTED_FILES:
            continue
        
        # Skip hidden files (except .git which is already protected)
        if name.startswith('.') and name != '.git':
            # Delete other hidden files/dirs created by agents
            if item.is_dir():
                to_delete['dirs'].append(item)
            else:
                to_delete['files'].append(item)
            continue
        
        if item.is_dir():
            to_delete['dirs'].append(item)
        elif item.is_file():
            to_delete['files'].append(item)
    
    return to_delete

def find_agent_docs_to_delete():
    """Find files in agent-docs that should be deleted."""
    agent_docs_dir = PROJECT_ROOT / 'agent-docs'
    to_delete = []
    
    if agent_docs_dir.exists():
        for item in agent_docs_dir.iterdir():
            if item.name not in PROTECTED_AGENT_DOCS:
                to_delete.append(item)
    
    return to_delete

def delete_files_and_dirs(to_delete, dry_run=False):
    """Delete the specified files and directories."""
    deleted_count = 0
    
    # Delete directories
    for dir_path in to_delete['dirs']:
        print_action("Removing directory", dir_path.name, dry_run)
        if not dry_run:
            shutil.rmtree(dir_path, ignore_errors=True)
        deleted_count += 1
    
    # Delete files
    for file_path in to_delete['files']:
        print_action("Removing file", file_path.name, dry_run)
        if not dry_run:
            file_path.unlink(missing_ok=True)
        deleted_count += 1
    
    return deleted_count

def delete_agent_docs(to_delete, dry_run=False):
    """Delete extra files in agent-docs."""
    deleted_count = 0
    
    for item in to_delete:
        print_action("Removing agent-doc", item.name, dry_run)
        if not dry_run:
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)
        deleted_count += 1
    
    return deleted_count

def reset_memory_files(dry_run=False):
    """Reset all memory files to clean templates."""
    memory_dir = PROJECT_ROOT / 'memory'
    reset_count = 0
    
    if not memory_dir.exists():
        if not dry_run:
            memory_dir.mkdir(parents=True)
        print_action("Creating directory", "memory/", dry_run)
    
    for filename, template in MEMORY_TEMPLATES.items():
        filepath = memory_dir / filename
        print_action("Resetting", f"memory/{filename}", dry_run)
        if not dry_run:
            filepath.write_text(template)
        reset_count += 1
    
    return reset_count

def close_github_issues(dry_run=False):
    """Close all open GitHub issues."""
    print("  Fetching open issues...")
    
    # Get list of open issues
    output = run_command("gh issue list --state open --json number,title --limit 100", check=False)
    
    if not output:
        print("  No open issues found or gh CLI not available")
        return 0
    
    import json
    try:
        issues = json.loads(output)
    except json.JSONDecodeError:
        print("  Could not parse issue list")
        return 0
    
    if not issues:
        print("  No open issues to close")
        return 0
    
    closed_count = 0
    for issue in issues:
        number = issue['number']
        title = issue['title'][:50]
        print_action(f"Closing issue #{number}", title, dry_run)
        
        if not dry_run:
            run_command(
                f'gh issue close {number} --comment "Closing - project reset for clean start"',
                check=False
            )
        closed_count += 1
    
    return closed_count

def git_commit_and_push(dry_run=False):
    """Commit and push all changes."""
    # Check if there are changes
    status = run_command("git status --porcelain")
    
    if not status:
        print("  No changes to commit")
        return False
    
    print_action("Staging all changes", "git add -A", dry_run)
    if not dry_run:
        run_command("git add -A")
    
    print_action("Committing", "project reset", dry_run)
    if not dry_run:
        run_command('git commit -m "chore: reset project to clean state (automated)"', check=False)
    
    print_action("Pushing", "to origin/main", dry_run)
    if not dry_run:
        # Force push to handle any conflicts from concurrent agent work
        result = run_command("git push", check=False)
        if result is None:
            print("  Regular push failed, trying force push...")
            run_command("git push --force", check=False)
    
    return True

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Reset the agent-team-logo-creator project to a clean state"
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        '--skip-issues',
        action='store_true', 
        help="Skip closing GitHub issues"
    )
    parser.add_argument(
        '--skip-git',
        action='store_true',
        help="Skip git commit and push"
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")
    
    print_header("PROJECT RESET SCRIPT")
    print(f"Project root: {PROJECT_ROOT}")
    
    # Step 1: Find and delete files/directories
    print_header("Step 1: Removing agent-created files and directories")
    to_delete = find_files_to_delete()
    
    if to_delete['dirs'] or to_delete['files']:
        deleted = delete_files_and_dirs(to_delete, args.dry_run)
        print(f"\n  ✓ Removed {deleted} items")
    else:
        print("  No extra files/directories to remove")
    
    # Step 2: Clean agent-docs
    print_header("Step 2: Cleaning agent-docs directory")
    agent_docs_to_delete = find_agent_docs_to_delete()
    
    if agent_docs_to_delete:
        deleted = delete_agent_docs(agent_docs_to_delete, args.dry_run)
        print(f"\n  ✓ Removed {deleted} items from agent-docs")
    else:
        print("  No extra files in agent-docs")
    
    # Step 3: Reset memory files
    print_header("Step 3: Resetting memory files")
    reset_count = reset_memory_files(args.dry_run)
    print(f"\n  ✓ Reset {reset_count} memory files")
    
    # Step 4: Close GitHub issues
    if not args.skip_issues:
        print_header("Step 4: Closing GitHub issues")
        closed = close_github_issues(args.dry_run)
        print(f"\n  ✓ Closed {closed} issues")
    else:
        print_header("Step 4: Closing GitHub issues (SKIPPED)")
    
    # Step 5: Git commit and push
    if not args.skip_git:
        print_header("Step 5: Committing and pushing changes")
        git_commit_and_push(args.dry_run)
        print("\n  ✓ Changes committed and pushed")
    else:
        print_header("Step 5: Committing and pushing changes (SKIPPED)")
    
    # Summary
    print_header("RESET COMPLETE")
    if args.dry_run:
        print("  This was a dry run. No changes were made.")
        print("  Run without --dry-run to apply changes.")
    else:
        print("  ✅ Project has been reset to a clean state")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
