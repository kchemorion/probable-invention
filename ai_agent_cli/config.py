"""Configuration management module."""

import os
from pathlib import Path
import json
from typing import Any, Dict, Optional
from rich.console import Console
from rich.prompt import Prompt
import logging

console = Console()

class Config:
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration system."""
        self.config_dir = config_path or Path.home() / ".ai_agent_cli"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.load_config()

    def ensure_config_dir(self) -> None:
        """Create configuration directory if it doesn't exist."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"[red]Error creating config directory: {str(e)}[/red]")
            raise

    def load_config(self) -> None:
        """Load configuration from file or create default."""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    self.data = json.load(f)
            else:
                self.data = self.get_default_config()
                self.save_config()
        except json.JSONDecodeError:
            console.print("[red]Error reading config file. Using defaults.[/red]")
            self.data = self.get_default_config()
        except Exception as e:
            console.print(f"[red]Error loading config: {str(e)}[/red]")
            raise

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving config: {str(e)}[/red]")
            raise

    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration settings."""
        return {
            "github_token": os.getenv("GITHUB_TOKEN", ""),
            "anthropic_token": os.getenv("ANTHROPIC_API_KEY", ""),
            "workspace_dir": str(Path.home() / "ai_agent_projects"),
            "max_concurrent_projects": 3,
            "multi_agent_mode": True,
            "project_types": ["library", "cli-tool", "web-app", "api"],
            "analysis_sources": {
                "github": True,
                "stackoverflow": True,
                "hackernews": True,
                "research_papers": True
            },
            "agent_settings": {
                "coordinator": {"active": True},
                "architect": {"active": True},
                "researcher": {"active": True},
                "developer": {"active": True},
                "reviewer": {"active": True},
                "security": {"active": True}
            },
            "logging": {
                "level": "INFO",
                "file": str(self.config_dir / "ai_agent.log"),
                "max_size": 10485760,  # 10MB
                "backup_count": 5
            },
            "security": {
                "enable_code_signing": False,
                "enable_dependency_scanning": True,
                "allowed_domains": ["github.com", "pypi.org"]
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        try:
            keys = key.split('.')
            value = self.data
            for k in keys:
                value = value.get(k, default)
                if value is None:
                    return default
            return value
        except Exception as e:
            logging.error(f"Error retrieving config key {key}: {str(e)}")
            return default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        try:
            keys = key.split('.')
            data = self.data
            for k in keys[:-1]:
                data = data.setdefault(k, {})
            data[keys[-1]] = value
            self.save_config()
        except Exception as e:
            logging.error(f"Error setting config key {key}: {str(e)}")
            raise

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)

    def validate(self) -> bool:
        """Validate configuration."""
        required_keys = ["github_token", "anthropic_token", "workspace_dir"]
        return all(self.get(key) for key in required_keys)

    def setup_initial_config(self) -> None:
        """Interactive configuration setup."""
        console.print("[bold]Initial Configuration Setup[/bold]")
        
        # Get GitHub token
        if not self.data.get("github_token"):
            token = Prompt.ask(
                "[yellow]Enter your GitHub token[/yellow]",
                password=True
            )
            if token:
                self.set("github_token", token)

        # Get Anthropic token
        if not self.data.get("anthropic_token"):
            token = Prompt.ask(
                "[yellow]Enter your Anthropic API key[/yellow]",
                password=True
            )
            if token:
                self.set("anthropic_token", token)

        # Get workspace directory
        workspace = Prompt.ask(
            "[yellow]Enter workspace directory[/yellow]",
            default=str(self.get("workspace_dir"))
        )
        self.set("workspace_dir", str(Path(workspace).expanduser().resolve()))

        # Create workspace directory
        Path(self.get("workspace_dir")).mkdir(parents=True, exist_ok=True)

        # Configure multi-agent mode
        multi_agent = Prompt.ask(
            "[yellow]Enable multi-agent mode? (yes/no)[/yellow]",
            default="yes"
        ).lower() in ['y', 'yes']
        self.set("multi_agent_mode", multi_agent)

        console.print("[green]Configuration saved successfully![/green]")