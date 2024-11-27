# ai_agent_cli/ai_service.py
import os
import anthropic
from typing import List, Dict, Any
import asyncio
from anthropic import Anthropic

class AnthropicService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"  # Using the latest Claude model

    async def analyze_project_opportunity(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a potential project opportunity using Claude"""
        prompt = f"""Given this trending repository data:
        Name: {trend_data['name']}
        Description: {trend_data['description']}
        Languages: {trend_data['languages']}
        Stars: {trend_data['stars']}

        Please analyze this trend and suggest a unique project idea that:
        1. Builds upon this trend but solves a new problem
        2. Has potential for community interest
        3. Is technically feasible as an open source project
        4. Has a clear scope and initial feature set

        Return your response as a structured project proposal with:
        - Project name
        - Core problem it solves
        - Key features
        - Technical architecture
        - Potential challenges
        """

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return self._parse_project_proposal(response.content)

    async def generate_project_code(self, project_spec: Dict[str, Any], file_path: str) -> str:
        """Generate code for a specific project file"""
        prompt = f"""Please generate production-quality code for this file: {file_path}
        Project Specification:
        Name: {project_spec['name']}
        Description: {project_spec['description']}
        Core Features: {project_spec['features']}
        
        Please generate complete, well-documented code following best practices.
        Include error handling, logging, and appropriate tests.
        """

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content

    async def generate_documentation(self, project_spec: Dict[str, Any], code_files: List[str]) -> str:
        """Generate comprehensive project documentation"""
        files_content = "\n".join(code_files)
        
        prompt = f"""Please generate comprehensive documentation for this project:
        Project Name: {project_spec['name']}
        Description: {project_spec['description']}
        
        Code files:
        {files_content}
        
        Generate complete documentation including:
        1. Project overview
        2. Installation instructions
        3. Usage examples
        4. API reference
        5. Contributing guidelines
        """

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content

    async def review_code(self, code: str) -> List[Dict[str, Any]]:
        """Review generated code for improvements"""
        prompt = f"""Please review this code for:
        1. Potential bugs
        2. Security issues
        3. Performance improvements
        4. Best practices
        5. Code style

        Code to review:
        {code}

        Provide specific, actionable feedback."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return self._parse_code_review(response.content)

    def _parse_project_proposal(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into a structured project proposal"""
        # Implementation would parse the response into a structured format
        # This is a simplified version
        return {
            "name": "Extracted project name",
            "description": "Extracted description",
            "features": ["Feature 1", "Feature 2"],
            "architecture": "Extracted architecture",
            "challenges": ["Challenge 1", "Challenge 2"]
        }

    def _parse_code_review(self, response: str) -> List[Dict[str, Any]]:
        """Parse Claude's code review response into structured feedback"""
        # Implementation would parse the response into a list of specific issues
        return [
            {
                "type": "bug",
                "description": "Description of issue",
                "suggestion": "How to fix it"
            }
        ]