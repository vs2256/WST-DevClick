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

    def _load_repositories(self):
        """Load repository configurations"""
        repos = []
        index = 1
        while True:
            url = os.getenv(f"REPO_{index}_URL")
            if not url:
                break
            name = os.getenv(f"REPO_{index}_NAME", f"repo{index}")
            repos.append({"url": url, "name": name, "index": index})
            index += 1

        if not repos:
            raise ValueError(
                "No repositories configured. Please add REPO_*_URL in .env file"
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
