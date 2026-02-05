"""
Workspace Manager - Handles workspace creation and repository cloning
"""

import os
import subprocess
from pathlib import Path
import logging


class WorkspaceManager:
    """Manages workspace creation and repository operations"""

    def __init__(self, config):
        """Initialize workspace manager with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)

    def get_next_workspace_path(self):
        """Determine the next workspace version number"""
        base_path = Path(self.config.workspace_base_path)
        prefix = self.config.workspace_prefix

        version = 1
        while True:
            workspace_path = base_path / f"{prefix}{version}"
            if not workspace_path.exists():
                return workspace_path
            version += 1

    def create_workspace(self):
        """Create a new workspace directory"""
        workspace_path = self.get_next_workspace_path()

        print(f"Creating workspace: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)

        return workspace_path

    def clone_repository(self, repo, workspace_path):
        """Clone a single repository with real-time progress"""
        repo_url = repo["url"]
        repo_name = repo["name"]
        repo_path = workspace_path / repo_name

        print(f"Cloning: {repo_name}")
        print(f"Source : {repo_url}")

        try:
            # Clone with progress output
            process = subprocess.Popen(
                ["git", "clone", "--progress", repo_url, str(repo_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream output in real-time
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    print(f"  {line}")

            process.wait()

            if process.returncode == 0:
                print("")
                return True, repo_path
            else:
                error_msg = f"Clone failed (exit code: {process.returncode})"
                print(f"[ERROR] {error_msg}\n")
                return False, error_msg

        except FileNotFoundError:
            error_msg = "Git is not installed or not in PATH"
            print(f"[ERROR] {error_msg}\n")
            return False, error_msg
        except Exception as e:
            error_msg = f"Clone failed: {str(e)}"
            print(f"[ERROR] {error_msg}\n")
            return False, error_msg

    def clone_all_repositories(self, workspace_path):
        """Clone all configured repositories"""
        results = []

        for repo in self.config.repositories:
            success, result = self.clone_repository(repo, workspace_path)
            results.append({"repo": repo["name"], "success": success, "result": result})

        return results

    def check_git_installed(self):
        """Check if Git is installed"""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
