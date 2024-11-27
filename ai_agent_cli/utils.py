# ai_agent_cli/utils.py
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from github import Github
from rich.logging import RichHandler
from rich.console import Console
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

console = Console()

def setup_logging(log_file: Optional[Path] = None, level: str = "INFO") -> logging.Logger:
    """Configure logging with rich output"""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    return logging.getLogger("ai_agent")

def create_github_client(token: str) -> Github:
    """Create authenticated GitHub client"""
    try:
        client = Github(token)
        # Test the connection
        client.get_user().login
        return client
    except Exception as e:
        console.print(f"[red]Error connecting to GitHub: {str(e)}[/red]")
        raise

async def analyze_repository(repo_url: str) -> Dict[str, Any]:
    """Analyze a GitHub repository for various metrics"""
    async with aiohttp.ClientSession() as session:
        async with session.get(repo_url) as response:
            if response.status != 200:
                raise ValueError(f"Failed to fetch repository: {response.status}")
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract basic repository information
            repo_info = {
                "url": repo_url,
                "name": extract_repo_name(repo_url),
                "stars": extract_stars(soup),
                "forks": extract_forks(soup),
                "languages": extract_languages(soup),
                "topics": extract_topics(soup),
                "last_updated": extract_last_updated(soup)
            }
            
            return repo_info

def extract_repo_name(url: str) -> str:
    """Extract repository name from URL"""
    match = re.search(r"github\.com/[\w-]+/([\w-]+)", url)
    return match.group(1) if match else ""

def extract_stars(soup: BeautifulSoup) -> int:
    """Extract star count from repository page"""
    stars_element = soup.find("span", {"id": "repo-stars-counter-star"})
    return int(stars_element.get("title", "0").replace(",", "")) if stars_element else 0

def extract_forks(soup: BeautifulSoup) -> int:
    """Extract fork count from repository page"""
    forks_element = soup.find("span", {"id": "repo-network-counter"})
    return int(forks_element.get("title", "0").replace(",", "")) if forks_element else 0

def extract_languages(soup: BeautifulSoup) -> Dict[str, float]:
    """Extract programming languages and their percentages"""
    languages = {}
    lang_elements = soup.find_all("span", {"class": "color-fg-default text-bold mr-1"})
    
    for element in lang_elements:
        lang = element.text.strip()
        percentage = element.find_next("span").text.strip().rstrip("%")
        languages[lang] = float(percentage)
    
    return languages

def extract_topics(soup: BeautifulSoup) -> list:
    """Extract repository topics"""
    topics_elements = soup.find_all("a", {"class": "topic-tag"})
    return [topic.text.strip() for topic in topics_elements]

def extract_last_updated(soup: BeautifulSoup) -> str:
    """Extract last update timestamp"""
    time_element = soup.find("relative-time")
    return time_element.get("datetime") if time_element else ""

async def fetch_trending_projects(session: aiohttp.ClientSession, days: int = 7) -> list:
    """Fetch trending projects from GitHub"""
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
                "stars": repo.find("a", {"class": "Link--muted d-inline-block mr-3"}).text.strip()
            })
        
        return trending

def generate_project_structure(project_type: str, project_path: Path) -> None:
    """Generate basic project structure based on type"""
    templates = {
        "library": {
            "dirs": ["src", "tests", "docs", "examples"],
            "files": {
                "README.md": "# {project_name}\n\nDescription of your project",
                "setup.py": "from setuptools import setup, find_packages\n\nsetup(\n    name='{project_name}'\n)",
                "requirements.txt": "",
                ".gitignore": "*.pyc\n__pycache__/\n*.egg-info/\n",
            }
        },
        "cli-tool": {
            "dirs": ["src", "tests"],
            "files": {
                "README.md": "# {project_name}\n\nCLI tool description",
                "setup.py": "from setuptools import setup\n\nsetup(\n    name='{project_name}',\n    entry_points={\n        'console_scripts': ['{project_name}=src.main:main'],\n    }\n)",
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