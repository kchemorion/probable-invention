# ai_agent_cli/config.py
import os
from pathlib import Path
import json
from typing import Any, Dict, Optional
from rich.console import Console

console = Console()

class Config:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_dir = config_path or Path.home() / ".ai_agent_cli"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.load_config()

    def ensure_config_dir(self) -> None:
        """Create configuration directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> None:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                console.print("[red]Error reading config file. Using defaults.[/red]")
                self.data = self.get_default_config()
        else:
            self.data = self.get_default_config()
            self.save_config()

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving config: {str(e)}[/red]")

    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration settings"""
        return {
            "github_token": os.getenv("GITHUB_TOKEN", ""),
            "workspace_dir": str(Path.home() / "ai_agent_projects"),
            "max_concurrent_projects": 3,
            "project_types": ["library", "cli-tool", "web-app"],
            "analysis_sources": {
                "github": True,
                "stackoverflow": True,
                "hackernews": True,
            },
            "logging": {
                "level": "INFO",
                "file": str(self.config_dir / "ai_agent.log"),
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save"""
        self.data[key] = value
        self.save_config()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.data.update(updates)
        self.save_config()

    def validate(self) -> bool:
        """Validate configuration"""
        required_keys = ["github_token", "workspace_dir"]
        return all(key in self.data and self.data[key] for key in required_keys)

    def setup_initial_config(self) -> None:
        """Interactive configuration setup"""
        console.print("[bold]Initial Configuration Setup[/bold]")
        
        if not self.data.get("github_token"):
            token = console.input("[yellow]Enter your GitHub token: [/yellow]").strip()
            if token:
                self.set("github_token", token)

        workspace = console.input(
            f"[yellow]Enter workspace directory (default: {self.get('workspace_dir')}): [/yellow]"
        ).strip()
        if workspace:
            self.set("workspace_dir", str(Path(workspace).expanduser().resolve()))

        # Create workspace directory if it doesn't exist
        Path(self.get("workspace_dir")).mkdir(parents=True, exist_ok=True)

        console.print("[green]Configuration saved successfully![/green]")