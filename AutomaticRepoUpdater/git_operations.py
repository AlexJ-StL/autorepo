from git import Repo, GitCommandError
from pathlib import Path


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

        return [
            path for path in self._walk_with_depth(root, max_depth)
            if self._is_git_repo(path)
        ]

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

    def pull_repository(self, repo_path):
        """Pull updates from remote without pushing"""
        try:
            repo = Repo(repo_path)
            if repo.is_dirty():
                self.logger.log_event(
                    f"Skipping pull for dirty repo: {repo_path}"
                )
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

            # Restore push URL if it existed
            with repo.remote().config_writer as cw:
                old_push_url = cw.get("url")
            if old_push_url:
                repo.remote().set_url(old_push_url, push=True)
                cw.set("url", "")

        result = repo.remote().pull()

            if old_push_url:
                with repo.remote().config_writer as cw:
                    cw.set("url", old_push_url)

            self.logger.log_event(f"Successfully pulled: {repo_path}")
            return True, "Success"

        except GitCommandError as e:
            self.logger.log_error(f"Git error in {repo_path}: {str(e)}")
            return False, str(e)
        except Exception as e:
            self.logger.log_error(f"Error in {repo_path}: {str(e)}")
            return False, str(e)
