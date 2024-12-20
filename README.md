# AI Agent CLI

An autonomous AI development agent powered by Anthropic's Claude. This agent can analyze trends, generate projects, and manage development workflows either independently or as a team of specialized agents.

## Features

- 🤖 Multi-agent system with specialized roles
- 📊 Trend analysis and project opportunity detection
- 💻 Autonomous code generation and review
- 🔒 Security-first approach with built-in auditing
- 🧠 Advanced reasoning engine with memory persistence
- 🤝 Team collaboration through shared knowledge base

## Installation

```bash
# Clone the repository
git clone https://github.com/kchemorion/ai-agent-cli
cd ai-agent-cli

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Configuration

Before using the agent, you need to set up your API keys:

```bash
export GITHUB_TOKEN=your_github_token
export ANTHROPIC_API_KEY=your_anthropic_key
```

Or run the agent for interactive setup:
```bash
ai-agent start
```

## Usage

### Single Agent Mode

```bash
# Start in single agent mode
ai-agent start
```

### Multi-Agent Mode

```bash
# Start with multiple specialized agents
ai-agent start --multi-agent
```

### Configuration Options

```bash
# Specify custom config directory
ai-agent start --config-dir /path/to/config
```

## Agent Roles

The multi-agent system includes:

- **Coordinator**: Orchestrates other agents and manages workflows
- **Architect**: Designs system architectures and makes technical decisions
- **Researcher**: Analyzes trends and identifies opportunities
- **Developer**: Implements features and writes code
- **Reviewer**: Reviews code and suggests improvements
- **Security**: Conducts security audits and ensures best practices

## Project Structure

```
ai_agent_cli/
├── ai_agent_cli/
│   ├── __init__.py
│   ├── agent.py             # Main agent orchestration
│   ├── ai_service.py        # Anthropic service integration
│   ├── config.py            # Configuration management
│   ├── multi_agent/
│   │   ├── __init__.py
│   │   ├── agents.py        # Specialized agents
│   │   ├── core.py          # Multi-agent framework
│   │   └── memory.py        # Shared knowledge management
│   ├── reasoning.py         # Reasoning engine
│   └── utils.py             # Utility functions
├── setup.py
└── README.md
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Powered by [Anthropic's Claude](https://www.anthropic.com/claude)
- Built with Python and love ❤️

## Author

Francis Kiptengwer Chemorion (kchemorion@gmail.com)