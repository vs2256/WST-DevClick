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


class WorkspaceAutomation:
    """Main automation orchestrator"""
    
    def __init__(self):
        """Initialize automation with configuration"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        try:
            self.config = Config()
            self.workspace_manager = WorkspaceManager(self.config)
            self.eclipse_manager = EclipseManager(self.config)
            self.build_manager = BuildManager(self.config)
        except Exception as e:
            self.logger.error(f"Configuration error: {str(e)}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(f'automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def validate_prerequisites(self):
        """Validate all prerequisites before starting"""
        self.logger.info("=" * 60)
        self.logger.info("Validating prerequisites...")
        self.logger.info("=" * 60)
        
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
            self.logger.error("Prerequisites validation failed:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False
        
        self.logger.info("Prerequisites validation passed!")
        return True
    
    def run(self):
        """Execute the full automation workflow"""
        self.logger.info("=" * 60)
        self.logger.info("WORKSPACE AUTOMATION STARTED")
        self.logger.info("=" * 60)
        
        # Step 1: Validate prerequisites
        if not self.validate_prerequisites():
            self.logger.error("Automation aborted due to validation errors")
            return False
        
        # Step 2: Create workspace
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEP 1: Creating Workspace")
        self.logger.info("=" * 60)
        
        try:
            workspace_path = self.workspace_manager.create_workspace()
            self.logger.info(f"✓ Workspace created: {workspace_path}")
        except Exception as e:
            self.logger.error(f"Failed to create workspace: {str(e)}")
            return False
        
        # Step 3: Clone repositories
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEP 2: Cloning Repositories")
        self.logger.info("=" * 60)
        
        clone_results = self.workspace_manager.clone_all_repositories(workspace_path)
        
        all_cloned = True
        for result in clone_results:
            if result['success']:
                self.logger.info(f"✓ Cloned: {result['repo']}")
            else:
                self.logger.error(f"✗ Failed: {result['repo']} - {result['result']}")
                all_cloned = False
        
        if not all_cloned:
            self.logger.warning("Some repositories failed to clone, continuing...")
        
        # Step 4: Configure Eclipse project
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEP 3: Configuring Eclipse Project")
        self.logger.info("=" * 60)
        
        try:
            success, eclipse_workspace = self.eclipse_manager.setup_project(workspace_path)
            if success:
                self.logger.info(f"✓ Eclipse project configured")
                self.logger.info(f"  Eclipse workspace: {eclipse_workspace}")
            else:
                self.logger.error("Failed to configure Eclipse project")
        except Exception as e:
            self.logger.error(f"Eclipse configuration error: {str(e)}")
        
        # Step 5: Build project
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEP 4: Building Project")
        self.logger.info("=" * 60)
        
        eclipse_repo = self.config.get_eclipse_repo()
        project_path = workspace_path / eclipse_repo['name']
        
        build_success, build_msg = self.build_manager.build_project(project_path)
        
        if build_success:
            self.logger.info(f"✓ Build successful: {build_msg}")
            
            # Find and deploy WAR file
            war_file = self.build_manager.find_war_file(project_path)
            if war_file:
                self.logger.info(f"✓ Found WAR file: {war_file.name}")
                
                deploy_success, deploy_msg = self.build_manager.deploy_to_tomcat(war_file)
                if deploy_success:
                    self.logger.info(f"✓ Deployed to Tomcat: {deploy_msg}")
                else:
                    self.logger.warning(f"Deployment warning: {deploy_msg}")
            else:
                self.logger.warning("No WAR file found, skipping deployment")
        else:
            self.logger.warning(f"Build skipped or failed: {build_msg}")
        
        # Step 6: Start Tomcat
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STEP 5: Starting Tomcat Server")
        self.logger.info("=" * 60)
        
        start_success, start_msg = self.build_manager.start_tomcat()
        
        if start_success:
            self.logger.info(f"✓ Tomcat started: {start_msg}")
        else:
            self.logger.warning(f"Tomcat start warning: {start_msg}")
        
        # Summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("AUTOMATION COMPLETED!")
        self.logger.info("=" * 60)
        self.logger.info(f"\nWorkspace Location: {workspace_path}")
        self.logger.info(f"Eclipse Workspace: {eclipse_workspace}")
        self.logger.info(f"Application URL: http://localhost:{self.config.tomcat_port}")
        self.logger.info(f"\nTo open in Eclipse:")
        self.logger.info(f"  1. Launch Eclipse: {self.config.eclipse_path}")
        self.logger.info(f"  2. Select workspace: {eclipse_workspace}")
        self.logger.info(f"  3. Import project: {project_path}")
        
        return True


def main():
    """Main entry point"""
    try:
        automation = WorkspaceAutomation()
        success = automation.run()
        
        if success:
            print("\n✓ Automation completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Automation completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nAutomation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
