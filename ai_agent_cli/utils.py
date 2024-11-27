"""Utility functions for the AI agent system."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from github import Github
from rich.logging import RichHandler
from rich.console import Console
import aiohttp
from bs4 import BeautifulSoup
import re
from datetime import datetime
import yaml

console = Console()

def setup_logging(log_file: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """Configure logging with rich output and file handler."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [RichHandler(console=console, rich_tracebacks=True)]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(message)s",
        handlers=handlers
    )

    logger = logging.getLogger("ai_agent")
    return logger

def create_github_client(token: str) -> Github:
    """Create authenticated GitHub client with connection test."""
    try:
        client = Github(token)
        # Test connection
        user = client.get_user()
        user.login  # This will raise an exception if authentication fails
        return client
    except Exception as e:
        console.print(f"[red]Error connecting to GitHub: {str(e)}[/red]")
        raise

async def analyze_repository(repo_url: str) -> Dict[str, Any]:
    """Analyze a GitHub repository for various metrics."""
    async with aiohttp.ClientSession() as session:
        repo_info = await _fetch_repository_info(session, repo_url)
        repo_info.update(await _analyze_repository_activity(session, repo_url))
        return repo_info

async def _fetch_repository_info(session: aiohttp.ClientSession, repo_url: str) -> Dict[str, Any]:
    """Fetch basic repository information."""
    async with session.get(repo_url) as response:
        if response.status != 200:
            raise ValueError(f"Failed to fetch repository: {response.status}")
            
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            "url": repo_url,
            "name": extract_repo_name(repo_url),
            "stars": extract_stars(soup),
            "forks": extract_forks(soup),
            "languages": extract_languages(soup),
            "topics": extract_topics(soup),
            "last_updated": extract_last_updated(soup)
        }

async def _analyze_repository_activity(session: aiohttp.ClientSession, repo_url: str) -> Dict[str, Any]:
    """Analyze repository activity and engagement."""
    base_url = repo_url.rstrip('/')
    
    # Analyze commits
    commits_url = f"{base_url}/commits"
    async with session.get(commits_url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        commit_activity = analyze_commit_activity(soup)

    # Analyze issues
    issues_url = f"{base_url}/issues"
    async with session.get(issues_url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        issue_activity = analyze_issue_activity(soup)

    return {
        "activity": {
            "commits": commit_activity,
            "issues": issue_activity,
            "analysis_timestamp": datetime.now().isoformat()
        }
    }

def extract_repo_name(url: str) -> str:
    """Extract repository name from URL."""
    match = re.search(r"github\.com/[\w-]+/([\w-]+)", url)
    return match.group(1) if match else ""

def extract_stars(soup: BeautifulSoup) -> int:
    """Extract star count from repository page."""
    stars_element = soup.find("span", {"id": "repo-stars-counter-star"})
    return int(stars_element.get("title", "0").replace(",", "")) if stars_element else 0

def extract_forks(soup: BeautifulSoup) -> int:
    """Extract fork count from repository page."""
    forks_element = soup.find("span", {"id": "repo-network-counter"})
    return int(forks_element.get("title", "0").replace(",", "")) if forks_element else 0

def extract_languages(soup: BeautifulSoup) -> Dict[str, float]:
    """Extract programming languages and their percentages."""
    languages = {}
    lang_elements = soup.find_all("span", {"class": "color-fg-default text-bold mr-1"})
    
    for element in lang_elements:
        lang = element.text.strip()
        percentage = element.find_next("span").text.strip().rstrip("%")
        try:
            languages[lang] = float(percentage)
        except ValueError:
            continue
    
    return languages

def extract_topics(soup: BeautifulSoup) -> List[str]:
    """Extract repository topics."""
    topics_elements = soup.find_all("a", {"class": "topic-tag"})
    return [topic.text.strip() for topic in topics_elements]

def extract_last_updated(soup: BeautifulSoup) -> str:
    """Extract last update timestamp."""
    time_element = soup.find("relative-time")
    return time_element.get("datetime") if time_element else ""

def analyze_commit_activity(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze commit patterns and frequency."""
    commit_elements = soup.find_all("div", {"class": "TimelineItem-body"})
    
    commits = []
    for element in commit_elements:
        commit_info = {
            "message": element.find("a", {"class": "Link--primary"}).text.strip() if element.find("a", {"class": "Link--primary"}) else "",
            "author": element.find("a", {"class": "commit-author"}).text.strip() if element.find("a", {"class": "commit-author"}) else "",
            "timestamp": element.find("relative-time").get("datetime") if element.find("relative-time") else ""
        }
        commits.append(commit_info)
    
    return {
        "recent_commits": commits[:10],
        "commit_count": len(commits)
    }

def analyze_issue_activity(soup: BeautifulSoup) -> Dict[str, Any]:
    """Analyze issue patterns and interactions."""
    issue_elements = soup.find_all("div", {"class": "js-issue-row"})
    
    issues = []
    for element in issue_elements:
        issue_info = {
            "title": element.find("a", {"class": "Link--primary"}).text.strip() if element.find("a", {"class": "Link--primary"}) else "",
            "state": "open" if element.find("span", {"class": "open"}) else "closed",
            "comments": int(element.find("a", {"class": "Link--muted"}).text.strip()) if element.find("a", {"class": "Link--muted"}) else 0
        }
        issues.append(issue_info)
    
    return {
        "open_issues": len([i for i in issues if i["state"] == "open"]),
        "closed_issues": len([i for i in issues if i["state"] == "closed"]),
        "recent_issues": issues[:5]
    }

async def fetch_trending_projects(session: aiohttp.ClientSession, days: int = 7) -> List[Dict[str, Any]]:
    """Fetch trending projects from GitHub."""
    url = f"https://github.com/trending?since={days}d"
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        
        trending = []
        repo_elements = soup.find_all("article", {"class": "Box-row"})
        
        for repo in repo_elements:
            repo_link = repo.find("h2", {"class": "h3"}).find("a")
            repo_url = f"https://github.com{repo_link.get('href')}"
            
            trending.append({
                "url": repo_url,
                "name": repo_link.text.strip(),
                "description": repo.find("p", {"class": "col-9"}).text.strip() if repo.find("p", {"class": "col-9"}) else "",
                "language": repo.find("span", {"class": "d-inline-block ml-0 mr-3"}).text.strip() if repo.find("span", {"class": "d-inline-block ml-0 mr-3"}) else "",
                "stars": repo.find("a", {"class": "Link--muted d-inline-block mr-3"}).text.strip() if repo.find("a", {"class": "Link--muted d-inline-block mr-3"}) else "0"
            })
        
        return trending

def generate_project_structure(project_type: str, project_path: Path) -> None:
    """Generate basic project structure based on type."""
    templates = {
        "library": {
            "dirs": ["src", "tests", "docs", "examples"],
            "files": {
                "README.md": "# {project_name}\n\nDescription of your project",
                "setup.py": "from setuptools import setup, find_packages\n\nsetup(\n    name='{project_name}'\n)",
                "requirements.txt": "",
                ".gitignore": "*.pyc\n__pycache__/\n*.egg-info/\n",
                "pyproject.toml": """[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
"""
            }
        },
        "cli-tool": {
            "dirs": ["src", "tests"],
            "files": {
                "README.md": "# {project_name}\n\nCLI tool description",
                "setup.py": """from setuptools import setup

setup(
    name='{project_name}',
    version='0.1.0',
    packages=['src'],
    entry_points={{
        'console_scripts': [
            '{project_name}=src.main:main',
        ],
    }},
)""",
                "src/main.py": """def main():
    \"\"\"Main entry point for the CLI.\"\"\"
    print("Hello from {project_name}!")

if __name__ == '__main__':
    main()
"""
            }
        },
        "web-app": {
            "dirs": ["app", "tests", "static", "templates"],
            "files": {
                "README.md": "# {project_name}\n\nWeb application",
                "requirements.txt": "flask>=2.0.0\nrequests>=2.26.0\n",
                "app/__init__.py": """from flask import Flask

def create_app():
    app = Flask(__name__)
    return app
""",
                "app/main.py": """from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
"""
            }
        }
    }
    
    template = templates.get(project_type, templates["library"])
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create directories
    for dir_name in template["dirs"]:
        (project_path / dir_name).mkdir(exist_ok=True)
    
    # Create files
    for file_name, content in template["files"].items():
        file_path = project_path / file_name
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(content.format(project_name=project_path.name))

def load_project_config(project_path: Path) -> Dict[str, Any]:
    """Load project configuration from yaml file."""
    config_file = project_path / "project.yml"
    if not config_file.exists():
        return {}
        
    try:
        with open(config_file) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading project config: {str(e)}")
        return {}