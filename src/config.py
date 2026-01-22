"""
Configuration for the Agent Team Orchestrator

Environment variables and settings.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class SlackConfig:
    """Slack integration configuration."""
    bot_token: str
    channel_id: str
    channel_name: str = "logo-creator"
    
    @classmethod
    def from_env(cls) -> "SlackConfig":
        return cls(
            bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
            channel_id=os.getenv("SLACK_CHANNEL_ID", ""),
            channel_name=os.getenv("SLACK_CHANNEL_NAME", "logo-creator"),
        )


@dataclass
class GitHubConfig:
    """GitHub integration configuration."""
    token: str
    repo: str
    owner: str
    
    @classmethod
    def from_env(cls) -> "GitHubConfig":
        repo_full = os.getenv("GITHUB_REPO", "NinjaTech-AI/agent-team-logo-creator")
        parts = repo_full.split("/")
        return cls(
            token=os.getenv("GITHUB_TOKEN", ""),
            repo=parts[1] if len(parts) > 1 else repo_full,
            owner=parts[0] if len(parts) > 1 else "",
        )


@dataclass
class ClaudeConfig:
    """Claude Code CLI configuration."""
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 16000
    
    @classmethod
    def from_env(cls) -> "ClaudeConfig":
        return cls(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "16000")),
        )


@dataclass
class Config:
    """Main configuration container."""
    slack: SlackConfig
    github: GitHubConfig
    claude: ClaudeConfig
    repo_root: Path
    
    # Timing
    sync_interval_minutes: int = 60
    
    # Human stakeholder
    human_name: str = "Arash Sadrieh"
    human_slack_handle: str = "@arash"
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment."""
        return cls(
            slack=SlackConfig.from_env(),
            github=GitHubConfig.from_env(),
            claude=ClaudeConfig.from_env(),
            repo_root=Path(__file__).parent.parent,
            sync_interval_minutes=int(os.getenv("SYNC_INTERVAL_MINUTES", "60")),
            human_name=os.getenv("HUMAN_NAME", "Arash Sadrieh"),
            human_slack_handle=os.getenv("HUMAN_SLACK_HANDLE", "@arash"),
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.slack.bot_token:
            errors.append("SLACK_BOT_TOKEN is not set")
        if not self.slack.channel_id:
            errors.append("SLACK_CHANNEL_ID is not set")
        if not self.github.token:
            errors.append("GITHUB_TOKEN is not set")
        if not self.github.repo:
            errors.append("GITHUB_REPO is not set")
        
        return errors


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config