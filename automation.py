"""
Workspace Automation - Main orchestration script
One-click setup for workspace, repositories, Eclipse, and Tomcat
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

from config import Config
from workspace_manager import WorkspaceManager
from eclipse_manager import EclipseManager
from build_manager import BuildManager
from resource_manager import ResourceManager


class WorkspaceAutomation:
    """Main automation orchestrator"""

    def __init__(self):
        """Initialize automation with configuration"""
        # Load config first to get log directory
        try:
            self.config = Config()
        except Exception as e:
            print(f"[ERROR] Configuration error: {str(e)}")
            sys.exit(1)

        self.setup_logging()
        self.logger = logging.getLogger(__name__)

        try:
            self.workspace_manager = WorkspaceManager(self.config)
            self.eclipse_manager = EclipseManager(self.config)
            self.build_manager = BuildManager(self.config)
            self.resource_manager = ResourceManager(self.config)
        except Exception as e:
            self.logger.error(f"Configuration error: {str(e)}")
            sys.exit(1)

    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(exist_ok=True)

        log_file = (
            log_dir / f'automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )

        log_format = "%(levelname)s | %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        # Suppress verbose logging from libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("git").setLevel(logging.WARNING)

    def validate_prerequisites(self):
        """Validate all prerequisites before starting"""
        print("\n" + "=" * 70)
        print("  VALIDATING PREREQUISITES")
        print("=" * 70)

        errors = []

        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            for error in config_errors:
                if error.startswith("Warning:"):
                    self.logger.warning(error)
                else:
                    errors.append(error)

        # Check Git installation
        if not self.workspace_manager.check_git_installed():
            errors.append("Git is not installed or not in PATH")

        if errors:
            print("\n[ERROR] Prerequisites validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        print("[OK] All prerequisites validated successfully!\n")
        return True

    def run(self):
        """Execute the full automation workflow"""
        print("\n" + "=" * 70)
        print("  WORKSPACE AUTOMATION STARTED")
        print("=" * 70)

        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            print("\n[ERROR] Automation aborted due to validation errors")
            return False

        # Step 2: Select or Create workspace
        print("\n" + "=" * 70)
        print("  STEP 1: Workspace Selection")
        print("=" * 70)

        try:
            workspace_path, is_new = self.workspace_manager.select_or_create_workspace()

            if is_new:
                self.workspace_manager.create_workspace(workspace_path)
                print(f"[OK] Workspace created: {workspace_path}\n")
            else:
                print(f"[OK] Using existing workspace: {workspace_path}\n")
        except Exception as e:
            print(f"\n[ERROR] Failed to create workspace: {str(e)}")
            return False

        # Step 3: Clone repositories
        print("\n" + "=" * 70)
        print("  STEP 2: Repository Management")
        print("=" * 70 + "\n")

        if is_new:
            # New workspace - clone all repositories
            print("Cloning all repositories...\n")
            clone_results = self.workspace_manager.clone_all_repositories(
                workspace_path
            )
        else:
            # Existing workspace - validate and clone missing repos
            print("Validating existing workspace...\n")
            existing_repos, missing_repos = (
                self.workspace_manager.validate_workspace_repos(workspace_path)
            )

            if existing_repos:
                print("[OK] Already cloned repositories:")
                for repo in existing_repos:
                    print(f"     - {repo['name']}")
                print("")

            if missing_repos:
                print(f"[INFO] Found {len(missing_repos)} missing repository(ies)\n")
                print("Cloning missing repositories...\n")
                clone_results = self.workspace_manager.clone_all_repositories(
                    workspace_path, missing_repos
                )
            else:
                print("[OK] All repositories already cloned\n")
                clone_results = []

        # Process clone results
        all_cloned = True
        for result in clone_results:
            if result["success"]:
                print(f"[OK] Successfully cloned: {result['repo']}")
            else:
                print(f"[FAIL] Failed to clone: {result['repo']} - {result['result']}")
                all_cloned = False

        if not all_cloned and clone_results:
            print("\n[WARNING] Some repositories failed to clone, continuing...")

        # Step 4: Deploy Resource Files
        print("\n" + "=" * 70)
        print("  STEP 3: Deploying Resource Files")
        print("=" * 70 + "\n")

        try:
            resource_success, resource_msg = self.resource_manager.setup_resources(
                workspace_path
            )
            if resource_success:
                print(f"[OK] {resource_msg}")
            else:
                print(f"[WARNING] {resource_msg}")
        except Exception as e:
            print(f"[WARNING] Resource deployment error: {str(e)}")

        # Step 5: Configure Eclipse project
        print("\n" + "=" * 70)
        print("  STEP 4: Configuring Eclipse Project")
        print("=" * 70 + "\n")

        try:
            success, eclipse_workspace = self.eclipse_manager.setup_project(
                workspace_path
            )
            if success:
                print(f"[OK] Eclipse project configured")
                print(f"     Eclipse workspace: {eclipse_workspace}")
            else:
                print("[ERROR] Failed to configure Eclipse project")
        except Exception as e:
            print(f"[ERROR] Eclipse configuration error: {str(e)}")

        # Step 6: Configure Gradle Files
        print("\n" + "=" * 70)
        print("  STEP 5: Configuring Gradle Files")
        print("=" * 70 + "\n")

        eclipse_repo = self.config.get_eclipse_repo()
        project_path = workspace_path / eclipse_repo["name"]

        try:
            config_success, config_msg = self.build_manager.configure_gradle_project(project_path)
            if config_success:
                print(f"\n[OK] {config_msg}")
            else:
                print(f"\n[WARNING] {config_msg}")
        except Exception as e:
            print(f"[WARNING] Gradle configuration error: {str(e)}")

        # Step 7: Build project
        print("\n" + "=" * 70)
        print("  STEP 6: Building Project")
        print("=" * 70 + "\n")

        build_success, build_msg = self.build_manager.build_project(project_path)

        if build_success:
            print(f"[OK] Build successful: {build_msg}")

            # Find and deploy WAR file
            war_file = self.build_manager.find_war_file(project_path)
            if war_file:
                print(f"[OK] Found WAR file: {war_file.name}")

                deploy_success, deploy_msg = self.build_manager.deploy_to_tomcat(
                    war_file
                )
                if deploy_success:
                    print(f"[OK] Deployed to Tomcat: {deploy_msg}")
                else:
                    print(f"[WARNING] Deployment warning: {deploy_msg}")
            else:
                print("[WARNING] No WAR file found, skipping deployment")
        else:
            print(f"[WARNING] Build skipped or failed: {build_msg}")

        # Step 7: Start Tomcat
        print("\n" + "=" * 70)
        print("  STEP 7: Starting Tomcat Server")
        print("=" * 70 + "\n")

        start_success, start_msg = self.build_manager.start_tomcat()

        if start_success:
            print(f"[OK] Tomcat started: {start_msg}")
        else:
            print(f"[WARNING] Tomcat start warning: {start_msg}")

        # Summary
        print("\n" + "=" * 70)
        print("  AUTOMATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\n  Workspace Location  : {workspace_path}")
        print(f"  Eclipse Workspace   : {eclipse_workspace}")
        print(f"  Application URL     : http://localhost:{self.config.tomcat_port}")
        print(f"\n  Next Steps:")
        print(f"    1. Launch Eclipse   : {self.config.eclipse_path}")
        print(f"    2. Select Workspace : {eclipse_workspace}")
        print(f"    3. Import Project   : {project_path}")
        print("\n" + "=" * 70 + "\n")

        return True


def main():
    """Main entry point"""
    try:
        automation = WorkspaceAutomation()
        success = automation.run()

        if success:
            sys.exit(0)
        else:
            print("\n[ERROR] Automation completed with errors\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Automation cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
