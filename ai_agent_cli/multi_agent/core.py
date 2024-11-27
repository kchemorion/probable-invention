from typing import Dict, List, Any
import asyncio
from dataclasses import dataclass
from enum import Enum
import anthropic
from rich.console import Console

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

class AgentNetwork:
    def __init__(self, anthropic_client: anthropic.Anthropic):
        self.client = anthropic_client
        self.message_queue = asyncio.Queue()
        self.agents: Dict[AgentRole, SpecializedAgent] = {}
        self.shared_memory = SharedKnowledgeBase()
        self.initialize_agents()

    def initialize_agents(self):
        """Initialize all specialized agents"""
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
        
        # Start message processing for all agents
        agent_tasks = [
            agent.process_messages() 
            for agent in self.agents.values()
        ]
        
        # Start the coordinator's main loop
        coordinator = self.agents[AgentRole.COORDINATOR]
        agent_tasks.append(coordinator.coordinate())
        
        # Run all agents concurrently
        await asyncio.gather(*agent_tasks)

class SharedKnowledgeBase:
    def __init__(self):
        self.knowledge: Dict[str, Any] = {}
        self.lock = asyncio.Lock()

    async def store(self, key: str, value: Any):
        async with self.lock:
            self.knowledge[key] = value

    async def retrieve(self, key: str) -> Any:
        async with self.lock:
            return self.knowledge.get(key)

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
        response = await self.client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content