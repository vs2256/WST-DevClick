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

    def get_existing_workspaces(self):
        """Get list of existing workspaces"""
        base_path = Path(self.config.workspace_base_path)
        prefix = self.config.workspace_prefix
        
        if not base_path.exists():
            return []
        
        workspaces = []
        for item in base_path.iterdir():
            if item.is_dir() and item.name.startswith(prefix):
                workspaces.append(item)
        
        return sorted(workspaces, key=lambda x: x.name)

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

    def select_or_create_workspace(self):
        """Interactive workspace selection or creation"""
        existing = self.get_existing_workspaces()
        
        if existing:
            print("\n" + "=" * 70)
            print("  EXISTING WORKSPACES")
            print("=" * 70)
            for idx, ws in enumerate(existing, 1):
                print(f"  {idx}. {ws.name} ({ws})")
            
            next_ws = self.get_next_workspace_path()
            print(f"  {len(existing) + 1}. Create new workspace: {next_ws.name}")
            print("=" * 70)
            
            while True:
                try:
                    choice = input(f"\nSelect workspace (1-{len(existing) + 1}): ").strip()
                    if not choice:
                        print("[INFO] No selection made, creating new workspace...")
                        return self.get_next_workspace_path(), True
                    
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(existing):
                        selected = existing[choice_num - 1]
                        print(f"[INFO] Using existing workspace: {selected}")
                        return selected, False
                    elif choice_num == len(existing) + 1:
                        print(f"[INFO] Creating new workspace: {next_ws}")
                        return next_ws, True
                    else:
                        print(f"[ERROR] Invalid choice. Please enter 1-{len(existing) + 1}")
                except ValueError:
                    print("[ERROR] Invalid input. Please enter a number.")
                except KeyboardInterrupt:
                    print("\n[INFO] Using new workspace by default...")
                    return self.get_next_workspace_path(), True
        else:
            print("\n[INFO] No existing workspaces found.")
            return self.get_next_workspace_path(), True

    def validate_workspace_repos(self, workspace_path):
        """Check which repositories are missing in the workspace"""
        workspace_path = Path(workspace_path)
        missing_repos = []
        existing_repos = []
        
        for repo in self.config.repositories:
            repo_path = workspace_path / repo["name"]
            if repo_path.exists() and repo_path.is_dir():
                existing_repos.append(repo)
            else:
                missing_repos.append(repo)
        
        return existing_repos, missing_repos

    def create_workspace(self, workspace_path=None):
        """Create a new workspace directory"""
        if workspace_path is None:
            workspace_path = self.get_next_workspace_path()

        print(f"Creating workspace: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)

        return workspace_path

    def clone_repository(self, repo, workspace_path):
        """Clone a single repository with real-time progress"""
        repo_url = repo["url"]
        repo_name = repo["name"]
        repo_branch = repo.get("branch", "")
        repo_path = workspace_path / repo_name

        print(f"Cloning: {repo_name}")
        print(f"Source : {repo_url}")
        if repo_branch:
            print(f"Branch : {repo_branch}")

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
                # Switch to specified branch if provided
                if repo_branch:
                    print(f"  Switching to branch: {repo_branch}")
                    checkout_process = subprocess.run(
                        ["git", "-C", str(repo_path), "checkout", repo_branch],
                        capture_output=True,
                        text=True
                    )
                    if checkout_process.returncode == 0:
                        print(f"  [OK] Checked out branch: {repo_branch}")
                    else:
                        error_msg = checkout_process.stderr.strip()
                        print(f"  [WARNING] Branch checkout failed: {error_msg}")
                
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

    def clone_all_repositories(self, workspace_path, repos_to_clone=None):
        """Clone all configured repositories or specific list"""
        results = []
        
        repos = repos_to_clone if repos_to_clone is not None else self.config.repositories

        for repo in repos:
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
