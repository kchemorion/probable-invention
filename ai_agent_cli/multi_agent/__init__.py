"""Multi-agent system package."""

from .core import AgentNetwork, AgentRole, Message, SpecializedAgent
from .agents import (
    CoordinatorAgent,
    ArchitectAgent,
    ResearcherAgent,
    DeveloperAgent,
    ReviewerAgent,
    SecurityAgent
)
from rich.console import Console
import aiohttp
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Initialize shared console
console = Console()

__all__ = [
    'AgentNetwork',
    'AgentRole',
    'Message',
    'SpecializedAgent',
    'CoordinatorAgent',
    'ArchitectAgent',
    'ResearcherAgent',
    'DeveloperAgent',
    'ReviewerAgent',
    'SecurityAgent',
    'console'
]