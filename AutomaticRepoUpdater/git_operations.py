from git import Repo, GitCommandError
from pathlib import Path
import os

class GitOperations:
    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger

    def scan_directories(self, root_path, max_depth=2):
        """Scan directories up to specified depth for git repositories"""
        git_repos = []
        root = Path(root_path)

        for path in self._walk_with_depth(root, max_depth):
            if self._is_git_repo(path):
                git_repos.append(path)

        return git_repos

    def _walk_with_depth(self, path, max_depth):
        """Helper to walk directory with depth limit"""
        path = Path(path)
        if max_depth <= 0:
            return
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                yield item
                yield from self._walk_with_depth(item, max_depth - 1)

    def _is_git_repo(self, path):
        """Check if directory is a git repository"""
        try:
            Repo(path)
            return True
        except:
            return False
import os
