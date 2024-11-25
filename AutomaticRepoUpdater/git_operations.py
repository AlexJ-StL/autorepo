from typing import List, Tuple, Generator
from git import Repo, GitCommandError
from pathlib import Path


class GitOperations:
    def __init__(self, settings, logger) -> None:
        self.settings = settings
        self.logger = logger

    def scan_directories(
        self,
        root_path: str,
        max_depth: int = 2
    ) -> List[Path]:
        """
        Scan directories up to specified depth for git repositories.

        Args:
            root_path: The root directory to start scanning from
            max_depth: Maximum depth to scan (default: 2)

        Returns:
            List of Path objects representing git repositories
        """
        git_repos = []
        root = Path(root_path)

        for path in self._walk_with_depth(root, max_depth):
            if self._is_git_repo(path):
                git_repos.append(path)

        return git_repos

    def _walk_with_depth(
        self,
        path: Path,
        max_depth: int
    ) -> Generator[Path, None, None]:
        """
        Helper to walk directory with depth limit.

        Args:
            path: Directory path to walk
            max_depth: Maximum depth to traverse

        Yields:
            Path objects for each valid directory
        """
        path = Path(path)
        if max_depth <= 0:
            return
        try:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    yield item
                    yield from self._walk_with_depth(item, max_depth - 1)
        except PermissionError:
            self.logger.log_error(f"Permission denied accessing: {path}")
        except OSError as e:
            self.logger.log_error(f"Error accessing {path}: {e}")

    def _is_git_repo(self, path: Path) -> bool:
        """
        Check if directory is a git repository.

        Args:
            path: Directory path to check

        Returns:
            True if directory is a git repo, False otherwise
        """
        try:
            Repo(path)
            return True
        except GitCommandError:
            return False
        except Exception:
            return False

    def pull_repository(self, repo_path: str) -> Tuple[bool, str]:
        """
        Pull updates from remote without pushing.

        Args:
            repo_path: Path to the git repository

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            repo = Repo(repo_path)
            if repo.is_dirty():
                self.logger.log_event(
                    f"Skipping pull for dirty repo: {repo_path}"
                )
                return False, "Repository has uncommitted changes"

            # Ensure we're not pushing
            old_push_url = None
            try:
                old_push_url = repo.remote().set_url(push_url="", push=True)
            except:
                pass

            # Perform pull
            result = repo.remote().pull()

            if old_push_url:
                repo.remote().set_url(old_push_url, push=True)
            self.logger.log_event(f"Successfully pulled: {repo_path}")
            return True, "Success"

        except GitCommandError as e:
            self.logger.log_error(f"Git error in {repo_path}: {str(e)}")
            return False, str(e)
        except Exception as e:
            self.logger.log_error(f"Error in {repo_path}: {str(e)}")
            return False, str(e)
