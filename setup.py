"""Setup configuration for ai-agent-cli package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-agent-cli",
    version="0.1.0",
    author="Francis Kiptengwer Chemorion",
    author_email="kchemorion@gmail.com",
    description="An autonomous AI agent for project development using Anthropic's Claude",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kchemorion/ai-agent-cli",
    packages=find_packages(),
    install_requires=[
        "anthropic>=0.7.0",
        "aiohttp>=3.8.0",
        "aiofiles>=0.8.0",
        "beautifulsoup4>=4.9.3",
        "click>=8.0.0",
        "pandas>=1.3.0",
        "PyGithub>=1.55",
        "python-dotenv>=0.19.0",
        "requests>=2.28.0",
        "rich>=12.0.0",
        "pyyaml>=6.0",
        "typing-extensions>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-agent=ai_agent_cli.agent:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
    ],
    python_requires=">=3.8",
    package_data={
        "ai_agent_cli": ["py.typed"],
    },
    include_package_data=True,
    keywords="ai, agent, automation, development, claude, anthropic",
)