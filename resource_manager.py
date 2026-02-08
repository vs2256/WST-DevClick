"""
Resource Manager - Handles dynamic configuration file deployment
Processes template files and deploys them to appropriate locations
"""

import os
import shutil
import subprocess
from pathlib import Path
import logging
import re


class ResourceManager:
    """Manages resource file processing and deployment"""

    def __init__(self, config):
        """Initialize resource manager with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.resources_dir = Path(__file__).parent / "resources"

    def process_template(self, template_path, replacements):
        """
        Process a template file and replace placeholders with actual values
        
        Args:
            template_path: Path to template file
            replacements: Dictionary of placeholder -> value mappings
        
        Returns:
            Processed content as string
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace all placeholders in format ${VARIABLE_NAME}
            for key, value in replacements.items():
                placeholder = f"${{{key}}}"
                content = content.replace(placeholder, str(value))

            return content
        except Exception as e:
            self.logger.error(f"Failed to process template {template_path}: {str(e)}")
            raise

    def get_replacements(self, workspace_path):
        """
        Build dictionary of all replacement values from config
        
        Args:
            workspace_path: Current workspace path
            
        Returns:
            Dictionary of placeholder -> value mappings
        """
        primary_repo = self.config.repositories[0]  # Primary repository
        workspace_name = workspace_path.name  # e.g., "workspace_v1"
        
        # Create mount directory structure if it doesn't exist (shared across workspaces)
        mount_path = Path(self.config.mount_base_path)
        if not mount_path.exists():
            try:
                mount_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created mount directory: {mount_path}")
            except Exception as e:
                self.logger.warning(f"Could not create mount directory: {e}")
        
        # Construct repo path using .env base path directly (user's responsibility to use correct format)
        repo_primary_path = workspace_path / primary_repo['name']
        repo_primary_path_full = f"{self.config.workspace_base_path}\\{workspace_name}\\{primary_repo['name']}"

        replacements = {
            # Database Configuration
            "DB_URL": self.config.db_url,
            "DB_USERNAME": self.config.db_username,
            "DB_PASSWORD": self.config.db_password,
            "DB_DRIVER": self.config.db_driver,
            "DB_NAME": self.config.db_name,
            
            # Context.xml Configuration
            "CONTEXT_PATH": self.config.context_path,
            "CONTEXT_DOCBASE": self.config.context_docbase,
            "CONTEXT_DEBUG": self.config.context_debug,
            "CONTEXT_RELOADABLE": self.config.context_reloadable,
            "CONTEXT_CROSSCONTEXT": self.config.context_crosscontext,
            
            # Database Connection Pool Settings
            "DB_JNDI_NAME": self.config.db_jndi_name,
            "DB_MAX_TOTAL": self.config.db_max_total,
            "DB_MAX_IDLE": self.config.db_max_idle,
            "DB_MAX_WAIT_MILLIS": self.config.db_max_wait_millis,
            "DB_INITIAL_SIZE": self.config.db_initial_size,
            "DB_TEST_ON_BORROW": self.config.db_test_on_borrow,
            "DB_VALIDATION_QUERY": self.config.db_validation_query,
            
            # Server Configuration
            "SERVER_HOST": self.config.server_host,
            "SERVER_PORT": self.config.server_port,
            "TOMCAT_PORT": self.config.tomcat_port,
            
            # Application Configuration
            "APP_NAME": self.config.app_name,
            "APP_VERSION": self.config.app_version,
            "APP_ENVIRONMENT": self.config.app_environment,
            "APP_BASE_URL": self.config.app_base_url,
            "APP_PORT": self.config.app_port,
            
            # RFX Config Properties Configuration
            "RFX_APP_NAME": self.config.rfx_app_name,
            "RFX_APP_URL": self.config.rfx_app_url,
            "RFX_BATCH_PROFILE_MODE": self.config.rfx_batch_profile_mode,
            "RFX_LOAD_SPECIFIC_OWNERS": self.config.rfx_load_specific_owners,
            "MOUNT_BASE_PATH": self.config.mount_base_path,
            "RFX_KERNEL_WEB_URL": self.config.rfx_kernel_web_url,
            "RFX_KERNEL_DEFAULT_DOMAIN": self.config.rfx_kernel_default_domain,
            "RFX_KERNEL_CONNECTION_USER": self.config.rfx_kernel_connection_user,
            "RFX_KERNEL_CONNECTION_PASSWORD": self.config.rfx_kernel_connection_password,
            
            # RWS4 Batch Script Configuration
            "RWS4_OWNER_IDS": self.config.rws4_owner_ids,
            "REPO_PRIMARY_PATH": repo_primary_path_full,
            "WORKSPACE_BASE_PATH": self.config.workspace_base_path,
            "MOUNT_FOLDER_NAME": self.config.mount_folder_name,
            "KERNEL_CONFIG_FOLDER": self.config.kernel_config_folder,
            
            # Additional Path Information
            "REPO_PRIMARY_NAME": primary_repo["name"],
            "WORKSPACE_PATH": str(workspace_path),
            
            # Java/Tomcat Configuration
            "JAVA_HOME": self.config.java_home,
            "JAVA_VERSION": self.config.java_version,
            "TOMCAT_HOME": self.config.tomcat_home,
        }

        return replacements

    def deploy_config_files(self, workspace_path):
        """
        Deploy all configuration files to their target locations
        
        Args:
            workspace_path: Current workspace path
            
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            primary_repo = self.config.repositories[0]
            primary_repo_path = workspace_path / primary_repo["name"]

            if not primary_repo_path.exists():
                return False, f"Primary repository not found: {primary_repo_path}"

            self.logger.info("Processing and deploying configuration files...")
            print("[INFO] Processing resource files...")

            # Get all replacement values
            replacements = self.get_replacements(workspace_path)

            # Define deployment mapping: (template_file, target_path_relative_to_repo)
            deployments = [
                ("config.properties", "src/config.properties"),
                ("rfxconfig.properties", "src/rfxconfig.properties"),
                ("context.xml", "WebContent/META-INF/context.xml"),
            ]

            deployed_files = []
            for template_name, target_relative_path in deployments:
                template_path = self.resources_dir / template_name
                target_path = primary_repo_path / target_relative_path

                if not template_path.exists():
                    self.logger.warning(f"Template not found: {template_path}")
                    print(f"[SKIP] Template not found: {template_name}")
                    continue

                # Process template
                processed_content = self.process_template(template_path, replacements)

                # Create target directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Write processed file
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)

                deployed_files.append(target_relative_path)
                self.logger.info(f"Deployed: {target_relative_path}")
                print(f"[OK] Deployed: {template_name} -> {target_relative_path}")

            if deployed_files:
                return True, f"Successfully deployed {len(deployed_files)} file(s)"
            else:
                return False, "No files were deployed"

        except Exception as e:
            error_msg = f"Failed to deploy config files: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def execute_batch_script(self, workspace_path):
        """
        Execute the rws4-win.bat script after processing
        
        Args:
            workspace_path: Current workspace path
            
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            script_template = self.resources_dir / "rws4-win.bat"
            
            if not script_template.exists():
                self.logger.warning("rws4-win.bat not found in resources")
                return True, "Script not found, skipped"

            # Process the script template
            replacements = self.get_replacements(workspace_path)
            processed_script = self.process_template(script_template, replacements)

            # Create temporary script file
            temp_script = workspace_path / "rws4-win-processed.bat"
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(processed_script)

            self.logger.info("Executing rws4-win.bat script...")
            print("[INFO] Executing rws4-win.bat script...")

            # Execute the script
            result = subprocess.run(
                [str(temp_script)],
                cwd=str(workspace_path),
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                self.logger.info("Script executed successfully")
                if result.stdout:
                    print(result.stdout)
                return True, "Script executed successfully"
            else:
                error_msg = f"Script failed with code {result.returncode}"
                if result.stderr:
                    self.logger.error(result.stderr)
                    error_msg += f": {result.stderr}"
                return False, error_msg

        except Exception as e:
            error_msg = f"Failed to execute script: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def setup_resources(self, workspace_path):
        """
        Main method to setup all resources (deploy configs and run script)
        
        Args:
            workspace_path: Current workspace path
            
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            # Deploy configuration files
            deploy_success, deploy_msg = self.deploy_config_files(workspace_path)
            
            if not deploy_success:
                return False, deploy_msg

            # Execute batch script
            script_success, script_msg = self.execute_batch_script(workspace_path)
            
            if not script_success:
                self.logger.warning(f"Script execution had issues: {script_msg}")
                # Don't fail the whole process if script fails
                return True, f"{deploy_msg}; Script warning: {script_msg}"

            return True, f"{deploy_msg}; {script_msg}"

        except Exception as e:
            error_msg = f"Resource setup failed: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
