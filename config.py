"""
Configuration Manager for Workspace Automation
Loads and validates configuration from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration class to manage all settings"""

    def __init__(self, env_file=".env"):
        """Initialize configuration from .env file"""
        self.env_file = env_file
        self.base_dir = Path(__file__).parent
        self.load_config()

    def load_config(self):
        """Load configuration from .env file"""
        env_path = self.base_dir / self.env_file
        if not env_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {env_path}\n"
                f"Please copy .env.example to .env and configure it."
            )

        load_dotenv(env_path)

        # Workspace Configuration
        self.workspace_base_path = self.get_env("WORKSPACE_BASE_PATH")
        self.workspace_prefix = self.get_env("WORKSPACE_PREFIX", "workspace_v")
        
        # Logging Configuration
        self.log_dir = self.get_env("LOG_DIR", "logs")

        # Repository Configuration
        self.repositories = self._load_repositories()

        # Eclipse Configuration
        self.eclipse_repo_index = (
            int(self.get_env("ECLIPSE_REPO_TO_CONFIGURE", "1")) - 1
        )
        self.eclipse_path = self.get_env("ECLIPSE_PATH")
        self.eclipse_workspace_name = self.get_env(
            "ECLIPSE_WORKSPACE_NAME", "eclipse-workspace"
        )

        # Java Configuration
        self.java_home = self.get_env("JAVA_HOME")
        self.java_version = self.get_env("JAVA_VERSION", "17")

        # Tomcat Configuration
        self.tomcat_home = self.get_env("TOMCAT_HOME")
        self.tomcat_version = self.get_env("TOMCAT_VERSION", "9.0")
        self.tomcat_port = self.get_env("TOMCAT_PORT", "8080")

        # Application Configuration
        self.app_port = self.get_env("APP_PORT", "8080")
        self.server_port = self.get_env("SERVER_PORT", "8080")

        # Database Configuration
        self.db_url = self.get_env("DB_URL", "jdbc:postgresql://localhost:5432/mydb")
        self.db_username = self.get_env("DB_USERNAME", "dbuser")
        self.db_password = self.get_env("DB_PASSWORD", "dbpassword")
        self.db_driver = self.get_env("DB_DRIVER", "org.postgresql.Driver")
        self.db_name = self.get_env("DB_NAME", "mydb")

        # Context.xml Configuration
        self.context_path = self.get_env("CONTEXT_PATH", "/RWS4")
        self.context_docbase = self.get_env("CONTEXT_DOCBASE", "RWS4")
        self.context_debug = self.get_env("CONTEXT_DEBUG", "5")
        self.context_reloadable = self.get_env("CONTEXT_RELOADABLE", "true")
        self.context_crosscontext = self.get_env("CONTEXT_CROSSCONTEXT", "true")

        # Database Connection Pool Settings
        self.db_jndi_name = self.get_env("DB_JNDI_NAME", "jdbc/RWS4")
        self.db_max_total = self.get_env("DB_MAX_TOTAL", "15")
        self.db_max_idle = self.get_env("DB_MAX_IDLE", "5")
        self.db_max_wait_millis = self.get_env("DB_MAX_WAIT_MILLIS", "500")
        self.db_initial_size = self.get_env("DB_INITIAL_SIZE", "5")
        self.db_test_on_borrow = self.get_env("DB_TEST_ON_BORROW", "true")
        self.db_validation_query = self.get_env("DB_VALIDATION_QUERY", "select 1")

        # Server Configuration
        self.server_host = self.get_env("SERVER_HOST", "localhost")

        # Application Details
        self.app_name = self.get_env("APP_NAME", "MyApplication")
        self.app_version = self.get_env("APP_VERSION", "1.0.0")
        self.app_environment = self.get_env("APP_ENVIRONMENT", "development")
        self.app_base_url = self.get_env("APP_BASE_URL", "http://localhost:8080")

        # RFX Config Properties Configuration
        self.rfx_app_name = self.get_env("RFX_APP_NAME", "RWS4")
        self.rfx_app_url = self.get_env("RFX_APP_URL", "http://localhost:8080/RWS4")
        self.rfx_batch_profile_mode = self.get_env("RFX_BATCH_PROFILE_MODE", "DEMO")
        self.rfx_load_specific_owners = self.get_env("RFX_LOAD_SPECIFIC_OWNERS", "111110099")
        self.mount_base_path = self.get_env("MOUNT_BASE_PATH")
        self.rfx_kernel_web_url = self.get_env("RFX_KERNEL_WEB_URL", "https://wfmeng01.reflexisinc.co.in/kernel")
        self.rfx_kernel_default_domain = self.get_env("RFX_KERNEL_DEFAULT_DOMAIN", "REFLEXIS")
        self.rfx_kernel_connection_user = self.get_env("RFX_KERNEL_CONNECTION_USER", "admin")
        self.rfx_kernel_connection_password = self.get_env("RFX_KERNEL_CONNECTION_PASSWORD", "k3rn3l@2018")

        # RWS4 Batch Script Configuration
        self.rws4_owner_ids = self.get_env("RWS4_OWNER_IDS", "111110099 121500199")
        self.mount_folder_name = self.get_env("MOUNT_FOLDER_NAME", "mount")
        self.kernel_config_folder = self.get_env("KERNEL_CONFIG_FOLDER", "knlconfig")

    def _load_repositories(self):
        """Load repository configurations"""
        repos = []
        
        # Check for primary repository first
        primary_url = os.getenv("REPO_PRIMARY_URL")
        if primary_url:
            primary_name = os.getenv("REPO_PRIMARY_NAME", "repo_primary")
            primary_branch = os.getenv("REPO_PRIMARY_BRANCH", "")
            repos.append({
                "url": primary_url,
                "name": primary_name,
                "branch": primary_branch,
                "index": 1
            })
        
        # Load numbered repositories (starting from 2)
        index = 2
        while True:
            url = os.getenv(f"REPO_{index}_URL")
            if not url:
                break
            name = os.getenv(f"REPO_{index}_NAME", f"repo{index}")
            branch = os.getenv(f"REPO_{index}_BRANCH", "")
            repos.append({
                "url": url,
                "name": name,
                "branch": branch,
                "index": index
            })
            index += 1

        if not repos:
            raise ValueError(
                "No repositories configured. Please add REPO_PRIMARY_URL or REPO_*_URL in .env file"
            )

        return repos

    def get_env(self, key, default=None):
        """Get environment variable with optional default"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Required configuration '{key}' not found in .env file")
        return value

    def get_eclipse_repo(self):
        """Get the repository to configure in Eclipse"""
        if self.eclipse_repo_index >= len(self.repositories):
            raise ValueError(
                f"ECLIPSE_REPO_TO_CONFIGURE ({self.eclipse_repo_index + 1}) "
                f"is out of range. Only {len(self.repositories)} repos configured."
            )
        return self.repositories[self.eclipse_repo_index]

    def validate(self):
        """Validate configuration paths and settings"""
        errors = []

        # Validate Java Home
        if not Path(self.java_home).exists():
            errors.append(f"JAVA_HOME path does not exist: {self.java_home}")

        # Validate Tomcat Home
        if not Path(self.tomcat_home).exists():
            errors.append(f"TOMCAT_HOME path does not exist: {self.tomcat_home}")

        # Validate Eclipse Path (optional warning)
        if not Path(self.eclipse_path).exists():
            errors.append(f"Warning: ECLIPSE_PATH does not exist: {self.eclipse_path}")

        return errors
