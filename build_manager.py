"""
Build Manager - Handles Gradle builds and application deployment
"""
import os
import subprocess
from pathlib import Path
import logging


class BuildManager:
    """Manages build operations and application deployment"""
    
    def __init__(self, config):
        """Initialize build manager with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def detect_build_system(self, project_path):
        """Detect the build system used (Gradle)"""
        if (project_path / 'build.gradle').exists() or (project_path / 'build.gradle.kts').exists():
            return 'gradle'
        else:
            return None
    
    def build_gradle_project(self, project_path):
        """Build Gradle project"""
        self.logger.info(f"Building Gradle project: {project_path}")
        
        try:
            # Use gradlew if available, otherwise gradle
            gradlew = project_path / 'gradlew.bat' if os.name == 'nt' else project_path / 'gradlew'
            
            if gradlew.exists():
                cmd = [str(gradlew), 'clean', 'build', '-x', 'test']
            else:
                cmd = ['gradle', 'clean', 'build', '-x', 'test']
            
            result = subprocess.run(
                cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"Gradle build successful")
            return True, "Build successful"
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Gradle build failed: {e.stderr}"
            self.logger.error(error_msg)
            return False, error_msg
        except FileNotFoundError:
            error_msg = "Gradle is not installed or not in PATH"
            self.logger.error(error_msg)
            return False, error_msg
    
    def build_project(self, project_path):
        """Build the project using detected build system"""
        build_system = self.detect_build_system(project_path)
        
        if build_system == 'gradle':
            return self.build_gradle_project(project_path)
        else:
            msg = "No build system detected (build.gradle not found)"
            self.logger.warning(msg)
            return False, msg
    
    def find_war_file(self, project_path):
        """Find the generated WAR file"""
        # Check Gradle build directory
        build_dir = project_path / 'build' / 'libs'
        if build_dir.exists():
            war_files = list(build_dir.glob('*.war'))
            if war_files:
                return war_files[0]
        
        return None
    
    def deploy_to_tomcat(self, war_file, app_name=None):
        """Deploy WAR file to Tomcat"""
        if not war_file or not war_file.exists():
            return False, "WAR file not found"
        
        tomcat_webapps = Path(self.config.tomcat_home) / 'webapps'
        
        if not tomcat_webapps.exists():
            return False, f"Tomcat webapps directory not found: {tomcat_webapps}"
        
        # Copy WAR file to Tomcat webapps
        if app_name:
            dest_war = tomcat_webapps / f"{app_name}.war"
        else:
            dest_war = tomcat_webapps / war_file.name
        
        try:
            import shutil
            shutil.copy2(war_file, dest_war)
            self.logger.info(f"Deployed WAR to: {dest_war}")
            return True, str(dest_war)
        except Exception as e:
            error_msg = f"Failed to deploy WAR: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def start_tomcat(self):
        """Start Tomcat server"""
        tomcat_bin = Path(self.config.tomcat_home) / 'bin'
        startup_script = tomcat_bin / 'startup.bat' if os.name == 'nt' else tomcat_bin / 'startup.sh'
        
        if not startup_script.exists():
            return False, f"Tomcat startup script not found: {startup_script}"
        
        try:
            self.logger.info(f"Starting Tomcat server on port {self.config.tomcat_port}")
            
            subprocess.Popen(
                [str(startup_script)],
                cwd=str(tomcat_bin),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.logger.info(f"Tomcat server started successfully")
            self.logger.info(f"Application will be available at: http://localhost:{self.config.tomcat_port}")
            return True, f"http://localhost:{self.config.tomcat_port}"
            
        except Exception as e:
            error_msg = f"Failed to start Tomcat: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
