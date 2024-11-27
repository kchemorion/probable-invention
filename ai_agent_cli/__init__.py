"""AI Agent CLI - Autonomous Development System"""

from .agent import AIAgent
from .config import Config
from .ai_service import AnthropicService
from .reasoning import ReasoningEngine
from .multi_agent.core import AgentNetwork

__version__ = "0.1.0"
__author__ = "Francis Kiptengwer Chemorion"
__email__ = "kchemorion@gmail.com"

__all__ = [
    "AIAgent",
    "Config",
    "AnthropicService",
    "ReasoningEngine",
    "AgentNetwork"
]