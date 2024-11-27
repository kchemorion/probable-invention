"""Shared memory management for multi-agent system."""

import asyncio
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from datetime import datetime
import logging
import aiofiles

class SharedKnowledgeBase:
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize shared knowledge base."""
        self.storage_path = storage_path or Path.home() / ".ai_agent_cli" / "knowledge"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.memory: Dict[str, Any] = {}
        self.lock = asyncio.Lock()
        self.load_persistent_memory()

    def load_persistent_memory(self):
        """Load persistent memory from disk."""
        memory_file = self.storage_path / "memory.json"
        try:
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    self.memory = json.load(f)
        except Exception as e:
            logging.error(f"Error loading persistent memory: {str(e)}")
            self.memory = {}

    async def save_persistent_memory(self):
        """Save memory to disk."""
        memory_file = self.storage_path / "memory.json"
        try:
            async with aiofiles.open(memory_file, 'w') as f:
                await f.write(json.dumps(self.memory, indent=2))
        except Exception as e:
            logging.error(f"Error saving persistent memory: {str(e)}")

    async def store(self, key: str, value: Any, persistent: bool = True):
        """Store data in shared memory."""
        async with self.lock:
            self.memory[key] = {
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'persistent': persistent
            }
            if persistent:
                await self.save_persistent_memory()

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from shared memory."""
        async with self.lock:
            data = self.memory.get(key)
            return data['value'] if data else None

    async def update(self, key: str, value: Any):
        """Update existing memory entry."""
        if key in self.memory:
            await self.store(key, value, self.memory[key]['persistent'])

    async def delete(self, key: str):
        """Delete memory entry."""
        async with self.lock:
            if key in self.memory:
                del self.memory[key]
                await self.save_persistent_memory()

    async def list_keys(self) -> List[str]:
        """List all memory keys."""
        async with self.lock:
            return list(self.memory.keys())

    async def search(self, pattern: str) -> Dict[str, Any]:
        """Search memory entries matching pattern."""
        async with self.lock:
            return {
                k: v['value'] 
                for k, v in self.memory.items() 
                if pattern.lower() in k.lower()
            }

    async def clear_temporary(self):
        """Clear non-persistent memory entries."""
        async with self.lock:
            self.memory = {
                k: v for k, v in self.memory.items() 
                if v.get('persistent', False)
            }
            await self.save_persistent_memory()

    async def get_recent(self, limit: int = 10) -> Dict[str, Any]:
        """Get most recent memory entries."""
        async with self.lock:
            sorted_entries = sorted(
                self.memory.items(),
                key=lambda x: x[1]['timestamp'],
                reverse=True
            )
            return {
                k: v['value'] 
                for k, v in sorted_entries[:limit]
            }