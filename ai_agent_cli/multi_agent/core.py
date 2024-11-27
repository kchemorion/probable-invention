"""Core multi-agent system framework."""

from typing import Dict, List, Any
import asyncio
from dataclasses import dataclass
from enum import Enum
import anthropic
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime
from pathlib import Path
from .memory import SharedKnowledgeBase

console = Console()

class AgentRole(Enum):
    ARCHITECT = "architect"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    SECURITY = "security"
    COORDINATOR = "coordinator"

@dataclass
class Message:
    from_role: AgentRole
    to_role: AgentRole
    content: Dict[str, Any]
    priority: int = 1

class SpecializedAgent:
    def __init__(
        self,
        client: anthropic.Anthropic,
        message_queue: asyncio.Queue,
        shared_memory: SharedKnowledgeBase,
        role: AgentRole
    ):
        self.client = client
        self.message_queue = message_queue
        self.shared_memory = shared_memory
        self.role = role
        self.active = True

    async def process_messages(self):
        """Process incoming messages"""
        while self.active:
            message = await self.message_queue.get()
            if message.to_role == self.role:
                await self.handle_message(message)
            self.message_queue.task_done()

    async def handle_message(self, message: Message):
        """Handle incoming message based on role"""
        raise NotImplementedError("Specialized agents must implement handle_message")

    async def send_message(self, to_role: AgentRole, content: Dict[str, Any], priority: int = 1):
        """Send message to another agent"""
        message = Message(
            from_role=self.role,
            to_role=to_role,
            content=content,
            priority=priority
        )
        await self.message_queue.put(message)

    async def think(self, prompt: str) -> str:
        """Use Claude to think about a problem"""
        try:
            console.print(f"\n[cyan]Agent {self.role.value} thinking about:[/cyan]")
            console.print(f"[dim]{prompt}[/dim]")
            
            response = self.client.messages.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="claude-3-sonnet-20240229",
                max_tokens=2000
            )
            
            console.print(f"\n[green]Agent {self.role.value} response:[/green]")
            console.print(f"[yellow]{response.content}[/yellow]\n")
            
            # Log to file
            self._log_interaction(prompt, response.content)
            
            return response.content
        except Exception as e:
            console.print(f"[red]Error in think(): {str(e)}[/red]")
            raise

    def _log_interaction(self, prompt: str, response: str):
        """Log agent interactions to file"""
        timestamp = datetime.now().isoformat()
        log_dir = Path.home() / ".ai_agent_cli" / "logs" / "agents"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{self.role.value}_interactions.log"
        
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Agent: {self.role.value}\n")
            f.write(f"Prompt:\n{prompt}\n")
            f.write(f"Response:\n{response}\n")
            f.write(f"{'='*50}\n")

class AgentNetwork:
    def __init__(self, anthropic_client: anthropic.Anthropic):
        self.client = anthropic_client
        self.message_queue = asyncio.Queue()
        self.shared_memory = SharedKnowledgeBase()
        self.agents: Dict[AgentRole, SpecializedAgent] = {}
        self.log_dir = Path.home() / ".ai_agent_cli" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.initialize_agents()

    def initialize_agents(self):
        """Initialize all specialized agents"""
        # Import here to avoid circular imports
        from .agents import (
            CoordinatorAgent,
            ArchitectAgent,
            ResearcherAgent,
            DeveloperAgent,
            ReviewerAgent,
            SecurityAgent
        )

        self.agents = {
            AgentRole.COORDINATOR: CoordinatorAgent(self.client, self.message_queue, self.shared_memory),
            AgentRole.ARCHITECT: ArchitectAgent(self.client, self.message_queue, self.shared_memory),
            AgentRole.RESEARCHER: ResearcherAgent(self.client, self.message_queue, self.shared_memory),
            AgentRole.DEVELOPER: DeveloperAgent(self.client, self.message_queue, self.shared_memory),
            AgentRole.REVIEWER: ReviewerAgent(self.client, self.message_queue, self.shared_memory),
            AgentRole.SECURITY: SecurityAgent(self.client, self.message_queue, self.shared_memory)
        }

    async def start(self):
        """Start the agent network"""
        console.print("[bold green]Starting Agent Network...[/bold green]")
        console.print("[bold blue]Monitoring agent interactions - logs saved to ~/.ai_agent_cli/logs[/bold blue]\n")
        
        # Create status display with custom progress bar
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )
        
        with progress:
            # Create a task for each agent
            tasks = {
                role: progress.add_task(
                    f"[cyan]Agent {role.value} running...",
                    total=None
                )
                for role in self.agents.keys()
            }
            
            # Start message processing for all agents
            agent_tasks = [
                agent.process_messages() 
                for agent in self.agents.values()
            ]
            
            # Start the coordinator's main loop
            coordinator = self.agents[AgentRole.COORDINATOR]
            agent_tasks.append(coordinator.coordinate())
            
            # Run all agents concurrently
            try:
                await asyncio.gather(*agent_tasks)
            except Exception as e:
                console.print(f"[red]Error in agent network: {str(e)}[/red]")
                raise

    async def broadcast_message(self, message: str):
        """Broadcast a message to all agents"""
        timestamp = datetime.now().isoformat()
        console.print(f"\n[bold magenta]Network Broadcast ({timestamp}):[/bold magenta]")
        console.print(f"[magenta]{message}[/magenta]\n")
        
        # Log broadcast
        with open(self.log_dir / "network_broadcasts.log", 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Broadcast: {message}\n")
            f.write(f"{'='*50}\n")