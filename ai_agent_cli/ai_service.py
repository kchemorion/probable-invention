"""Anthropic service integration module."""

import os
import re
from typing import List, Dict, Any
import anthropic
from anthropic import Anthropic
import json

class AnthropicService:
    def __init__(self, api_key: str = None):
        """Initialize the Anthropic service."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-sonnet-20240229"

    async def analyze_project_opportunity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project opportunities with context."""
        try:
            prompt = self._create_analysis_prompt(context)
            response = self.client.messages.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model=self.model,
                max_tokens=2000
            )
            return self._parse_structured_response(response.content)
        except Exception as e:
            logging.error(f"Error in analyze_project_opportunity: {str(e)}")
            raise

    async def generate_project_code(self, spec: Dict[str, Any], file_path: str) -> str:
        """Generate code for a specific project file."""
        prompt = self._create_code_generation_prompt(spec, file_path)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._extract_code_blocks(response.content)

    async def review_code(self, code: str) -> List[Dict[str, Any]]:
        """Review code and provide structured feedback."""
        prompt = self._create_code_review_prompt(code)
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_review_response(response.content)

    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create a detailed prompt for project analysis."""
        return f"""Given this development context:
        {json.dumps(context, indent=2)}

        Please analyze potential project opportunities. Consider:
        1. Current technology trends
        2. Market needs and gaps
        3. Technical feasibility
        4. Community impact potential
        5. Resource requirements

        Provide a structured response with:
        - Project ideas (at least 3)
        - Technology stack recommendations
        - Implementation approach
        - Risk assessment
        - Success metrics

        Format the response as JSON with clear sections."""

    def _create_code_generation_prompt(self, spec: Dict[str, Any], file_path: str) -> str:
        """Create a detailed prompt for code generation."""
        return f"""Generate production-quality code for:
        File: {file_path}
        Specification: {json.dumps(spec, indent=2)}

        Requirements:
        1. Follow Python best practices and PEP standards
        2. Include comprehensive error handling
        3. Add detailed docstrings and comments
        4. Implement logging
        5. Include type hints
        6. Add unit tests

        Return the code in clearly marked code blocks."""

    def _create_code_review_prompt(self, code: str) -> str:
        """Create a detailed prompt for code review."""
        return f"""Review this code for quality and improvements:

        {code}

        Analyze:
        1. Code structure and organization
        2. Error handling and edge cases
        3. Performance considerations
        4. Security implications
        5. Testing coverage
        6. Documentation quality

        Provide specific, actionable feedback in JSON format."""

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into structured data."""
        try:
            # Look for JSON blocks in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Fallback to structured parsing if no JSON found
            sections = re.split(r'\n(?=\w+:)', response)
            parsed = {}
            for section in sections:
                if ':' in section:
                    key, value = section.split(':', 1)
                    parsed[key.strip()] = value.strip()
            return parsed
            
        except Exception as e:
            return {
                "error": "Failed to parse response",
                "raw_response": response,
                "exception": str(e)
            }

    def _extract_code_blocks(self, response: str) -> str:
        """Extract code blocks from Claude's response."""
        code_blocks = re.findall(r'```(?:python)?\n([\s\S]*?)\n```', response)
        if code_blocks:
            return '\n\n'.join(code_blocks)
        return response.strip()

    def _parse_review_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse code review response into structured feedback."""
        try:
            # Try to parse as JSON first
            if '{' in response and '}' in response:
                json_str = re.search(r'\{[\s\S]*\}', response).group(0)
                return json.loads(json_str)
            
            # Fallback to parsing sections
            sections = re.split(r'\n(?=\d+\.)', response)
            feedback = []
            for section in sections:
                if section.strip():
                    matches = re.match(r'(\d+)\.\s+(.*?):\s+(.*)', section.strip())
                    if matches:
                        feedback.append({
                            "id": matches.group(1),
                            "type": matches.group(2),
                            "description": matches.group(3)
                        })
            return feedback
            
        except Exception as e:
            return [{
                "type": "error",
                "description": "Failed to parse review response",
                "details": str(e)
            }]