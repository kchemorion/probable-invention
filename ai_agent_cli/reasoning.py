# ai_agent_cli/reasoning.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path
import anthropic
from datetime import datetime

@dataclass
class Thought:
    content: str
    timestamp: str
    context: Dict[str, Any]
    outcome: Optional[str] = None
    
@dataclass
class Plan:
    goal: str
    steps: List[Dict[str, Any]]
    current_step: int
    context: Dict[str, Any]
    status: str = "in_progress"

class ReasoningEngine:
    def __init__(self, anthropic_client, memory_path: Path):
        self.client = anthropic_client
        self.memory_path = memory_path
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.context_file = self.memory_path / "context.json"
        self.thoughts_file = self.memory_path / "thoughts.json"
        self.load_memory()

    def load_memory(self):
        """Load existing memory and context"""
        self.context = {}
        self.thoughts = []
        
        if self.context_file.exists():
            self.context = json.loads(self.context_file.read_text())
        if self.thoughts_file.exists():
            self.thoughts = [Thought(**t) for t in json.loads(self.thoughts_file.read_text())]

    def save_memory(self):
        """Save current memory state"""
        self.context_file.write_text(json.dumps(self.context, indent=2))
        thoughts_data = [vars(t) for t in self.thoughts]
        self.thoughts_file.write_text(json.dumps(thoughts_data, indent=2))

    async def reason_about_task(self, task: str, context: Dict[str, Any]) -> Plan:
        """Generate a reasoned plan for a given task"""
        # Combine task with relevant context and history
        recent_thoughts = self.thoughts[-5:] if self.thoughts else []
        thought_history = "\n".join([f"Previous thought: {t.content}" for t in recent_thoughts])
        
        prompt = f"""Task: {task}

Current Context:
{json.dumps(context, indent=2)}

Recent Thoughts:
{thought_history}

Please analyze this task and create a detailed plan. Consider:
1. Previous experiences and outcomes
2. Potential challenges and risks
3. Dependencies and prerequisites
4. Success criteria

Format your response as a structured plan with:
- Main goal
- Detailed steps (including validation points)
- Required context
- Success metrics"""

        response = await self.client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse Claude's response into a structured plan
        plan_data = self._parse_plan_response(response.content)
        return Plan(**plan_data)

    async def evaluate_outcome(self, action: str, result: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the outcome of an action and update learning"""
        prompt = f"""Please analyze this action and its outcome:

Action: {action}
Result: {result}
Context: {json.dumps(context, indent=2)}

Evaluate:
1. Was this outcome successful?
2. What went well?
3. What could be improved?
4. What should we learn from this?
5. How should this influence future decisions?

Provide structured analysis."""

        response = await self.client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}]
        )
        
        evaluation = self._parse_evaluation(response.content)
        
        # Record thought about this outcome
        thought = Thought(
            content=f"Evaluated outcome of {action}: {evaluation['summary']}",
            timestamp=datetime.now().isoformat(),
            context=context,
            outcome=evaluation['success']
        )
        self.thoughts.append(thought)
        self.save_memory()
        
        return evaluation

    async def adapt_plan(self, current_plan: Plan, new_information: Dict[str, Any]) -> Plan:
        """Adapt current plan based on new information"""
        prompt = f"""Current Plan:
{json.dumps(vars(current_plan), indent=2)}

New Information:
{json.dumps(new_information, indent=2)}

Please analyze if and how the current plan should be adapted based on this new information.
Consider:
1. Impact on current steps
2. Need for new steps
3. Risk adjustments
4. Priority changes

Provide updated plan structure."""

        response = await self.client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}]
        )
        
        updated_plan_data = self._parse_plan_response(response.content)
        return Plan(**updated_plan_data)

    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into a structured plan"""
        # In a real implementation, this would properly parse Claude's response
        # This is a simplified version
        return {
            "goal": "Extracted goal",
            "steps": [{"step": "Extracted step"}],
            "current_step": 0,
            "context": {},
        }

    def _parse_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse Claude's evaluation response"""
        # In a real implementation, this would properly parse Claude's response
        return {
            "success": True,
            "summary": "Evaluation summary",
            "lessons": ["Lesson 1"],
            "improvements": ["Improvement 1"]
        }