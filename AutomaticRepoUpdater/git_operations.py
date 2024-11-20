import subprocess

import os

class GitOperations:
    def pull_repositories(self, directory):
        """Perform a git pull operation in the given directory and its subdirectories up to 2 tiers."""
        for root, dirs, _ in os.walk(directory):
            if root[len(directory)+1:].count(os.sep) < 2:
                if '.git' in dirs:
                    dirs.remove('.git')
                    subprocess.run(['git', 'pull'], cwd=root)
import os
