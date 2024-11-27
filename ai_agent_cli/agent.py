"""Main agent orchestration module."""

import asyncio
import click
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from rich.console import Console
from rich.progress import Progress

from .config import Config
from .ai_service import AnthropicService
from .reasoning import ReasoningEngine
from .utils import setup_logging, create_github_client, analyze_repository
from .multi_agent.core import AgentNetwork

console = Console()

class AIAgent:
    def __init__(self, config: Config):
        """Initialize the AI Agent with configuration."""
        self.config = config
        self.logger = setup_logging(
            Path(config.get("logging", {}).get("file")),
            config.get("logging", {}).get("level", "INFO")
        )
        self.github = create_github_client(config.get("github_token"))
        self.workspace = Path(config.get("workspace_dir"))
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # Initialize AI services
        self.ai = AnthropicService(config.get("anthropic_token"))
        self.reasoning = ReasoningEngine(
            self.ai.client,
            self.workspace / ".memory"
        )
        
        # Initialize agent network if multi-agent mode is enabled
        if config.get("multi_agent_mode", True):
            self.agent_network = AgentNetwork(self.ai.client)
        else:
            self.agent_network = None

    async def start(self):
        """Start the AI agent in appropriate mode."""
        try:
            self.logger.info("Starting AI Agent...")
            
            if self.agent_network:
                await self._start_multi_agent_mode()
            else:
                await self._start_single_agent_mode()
                
        except Exception as e:
            self.logger.error(f"Critical error in agent execution: {str(e)}")
            raise

    async def _start_multi_agent_mode(self):
        """Start in multi-agent mode with specialized agents."""
        self.logger.info("Starting in multi-agent mode...")
        await self.agent_network.start()

    async def _start_single_agent_mode(self):
        """Start in single agent mode."""
        self.logger.info("Starting in single agent mode...")
        
        initial_context = {
            "workspace": str(self.workspace),
            "github_username": self.github.get_user().login,
            "current_time": datetime.now().isoformat()
        }
        
        plan = await self.reasoning.reason_about_task(
            "Identify and develop valuable open source projects",
            initial_context
        )
        
        try:
            while plan.status == "in_progress":
                step = plan.steps[plan.current_step]
                self.logger.info(f"Executing step: {step}")
                
                try:
                    await self._execute_step(step)
                except Exception as e:
                    self.logger.error(f"Step failed: {str(e)}")
                    plan = await self.reasoning.adapt_plan(plan, {
                        "error": str(e),
                        "step": step
                    })
                    continue
                
                plan.current_step += 1
                if plan.current_step >= len(plan.steps):
                    plan.status = "completed"
                    
        except Exception as e:
            self.logger.error(f"Error in single agent mode: {str(e)}")
            raise

    async def _execute_step(self, step: Dict[str, Any]):
        """Execute a single step of the plan."""
        if step["type"] == "analyze_trends":
            trends = await self._analyze_trends()
            evaluation = await self.reasoning.evaluate_outcome(
                "trend_analysis",
                trends,
                {"step": step}
            )
            return evaluation
            
        elif step["type"] == "generate_project":
            project = await self._generate_project(step["parameters"])
            return await self.reasoning.evaluate_outcome(
                "project_generation",
                project,
                {"step": step}
            )
            
        elif step["type"] == "implement_feature":
            code = await self.ai.generate_project_code(
                step["parameters"],
                step["file_path"]
            )
            return await self.reasoning.evaluate_outcome(
                "code_generation",
                code,
                {"step": step}
            )
        
        else:
            raise ValueError(f"Unknown step type: {step['type']}")

    async def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze trends with reasoning capabilities."""
        self.logger.info("Analyzing trends...")
        return await self.ai.analyze_project_opportunity({
            "workspace": str(self.workspace),
            "github_username": self.github.get_user().login,
            "time": datetime.now().isoformat()
        })

    async def _generate_project(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new project based on parameters."""
        self.logger.info(f"Generating project: {parameters.get('name')}")
        project_data = await self.ai.generate_project_code(parameters, "main.py")
        return {
            "name": parameters.get("name"),
            "code": project_data,
            "timestamp": datetime.now().isoformat()
        }

@click.group()
def cli():
    """AI Agent CLI - Autonomous Development Assistant"""
    pass

@cli.command()
@click.option('--config-dir', type=click.Path(), help='Configuration directory')
@click.option('--multi-agent', is_flag=True, help='Enable multi-agent mode')
def start(config_dir: Optional[str], multi_agent: bool):
    """Start the AI agent."""
    config = Config(Path(config_dir) if config_dir else None)
    
    if not config.validate():
        config.setup_initial_config()
        if not config.validate():
            console.print("[red]Configuration is incomplete. Please set required values.[/red]")
            return

    # Set multi-agent mode in config
    config.set("multi_agent_mode", multi_agent)
    
    agent = AIAgent(config)
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise

def main():
    """Main entry point for the CLI."""
    cli()