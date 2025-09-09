import requests
import re
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import urlparse
import base64

from ..config import get_settings


class GitHubIntegration:
    """Handles fetching markdown files from GitHub repositories"""
    
    def __init__(self):
        self.settings = get_settings()
        self.session = requests.Session()
        
        if self.settings.github_token:
            self.session.headers.update({
                'Authorization': f'token {self.settings.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
    
    def extract_repo_info(self, github_url: str) -> Tuple[str, str, Optional[str]]:
        """
        Extract owner, repo, and path from GitHub URL
        Returns: (owner, repo, path)
        """
        # Handle various GitHub URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+)/?$',  # Base repo
            r'github\.com/([^/]+)/([^/]+)/tree/[^/]+/(.+)',  # With path
            r'github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)',  # Single file
            r'github\.com/([^/]+)/([^/]+)/(?:tree|blob)/[^/]+/?$',  # Branch root
        ]
        
        # Clean URL
        url = github_url.replace('https://', '').replace('http://', '')
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2).replace('.git', '')
                path = match.group(3) if len(match.groups()) > 2 else None
                return owner, repo, path
        
        raise ValueError(f"Invalid GitHub URL format: {github_url}")
    
    def fetch_markdown_files(self, github_url: str, folder_path: str = "") -> List[Tuple[str, str]]:
        """
        Fetch all markdown files from a GitHub repository
        Returns list of (filename, content) tuples
        """
        owner, repo, extracted_path = self.extract_repo_info(github_url)
        
        # Use provided folder_path or extracted path
        path = folder_path or extracted_path or ""
        
        files = self._get_repository_contents(owner, repo, path)
        markdown_files = []
        
        for file_info in files:
            if self._is_markdown_file(file_info['name']):
                content = self._fetch_file_content(file_info['download_url'])
                markdown_files.append((file_info['name'], content))
        
        return markdown_files
    
    def fetch_single_file(self, github_url: str) -> Tuple[str, str]:
        """
        Fetch a single markdown file from GitHub
        Returns (filename, content)
        """
        owner, repo, file_path = self.extract_repo_info(github_url)
        
        if not file_path:
            raise ValueError("URL does not point to a specific file")
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        response = self.session.get(api_url)
        response.raise_for_status()
        
        file_data = response.json()
        
        if file_data['type'] != 'file':
            raise ValueError("URL does not point to a file")
        
        # Decode base64 content
        content = base64.b64decode(file_data['content']).decode('utf-8')
        filename = file_data['name']
        
        return filename, content
    
    def _get_repository_contents(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """Get contents of a repository directory"""
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        if path:
            api_url += f"/{path}"
        
        response = self.session.get(api_url)
        response.raise_for_status()
        
        contents = response.json()
        
        # If it's a single file, wrap in list
        if isinstance(contents, dict):
            return [contents]
        
        files = []
        for item in contents:
            if item['type'] == 'file' and self._is_markdown_file(item['name']):
                files.append(item)
            elif item['type'] == 'dir':
                # Recursively fetch from subdirectories
                subfiles = self._get_repository_contents(owner, repo, item['path'])
                files.extend(subfiles)
        
        return files
    
    def _fetch_file_content(self, download_url: str) -> str:
        """Fetch file content from download URL"""
        response = self.session.get(download_url)
        response.raise_for_status()
        return response.text
    
    def _is_markdown_file(self, filename: str) -> bool:
        """Check if file is a markdown file"""
        markdown_extensions = ['.md', '.markdown', '.mdown', '.mkdn', '.mdx']
        return any(filename.lower().endswith(ext) for ext in markdown_extensions)
    
    def get_repository_metadata(self, github_url: str) -> Dict[str, Any]:
        """
        Get repository metadata for book information
        Returns repository info that can be used for book metadata
        """
        owner, repo, _ = self.extract_repo_info(github_url)
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = self.session.get(api_url)
        response.raise_for_status()
        
        repo_data = response.json()
        
        return {
            'title': repo_data.get('name', '').replace('-', ' ').replace('_', ' ').title(),
            'description': repo_data.get('description', ''),
            'author': repo_data.get('owner', {}).get('login', ''),
            'created_at': repo_data.get('created_at'),
            'updated_at': repo_data.get('updated_at'),
            'language': repo_data.get('language', ''),
            'topics': repo_data.get('topics', [])
        }