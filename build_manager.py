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
    
    def configure_gradle_properties(self, project_path):
        """Update gradle.properties with JAVA_HOME from .env"""
        gradle_props = project_path / 'gradle.properties'
        
        if not gradle_props.exists():
            self.logger.warning(f"gradle.properties not found: {gradle_props}")
            return False, "gradle.properties not found"
        
        try:
            with open(gradle_props, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Convert Java path to forward slashes for Gradle
            java_path = self.config.java_home.replace('\\', '/')
            
            # Update org.gradle.java.home
            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith('org.gradle.java.home'):
                    lines[i] = f'org.gradle.java.home={java_path}\n'
                    updated = True
                    self.logger.info(f"Updated org.gradle.java.home to: {java_path}")
                    break
                elif line.strip().startswith('# org.gradle.java.home'):
                    lines[i] = f'org.gradle.java.home={java_path}\n'
                    updated = True
                    self.logger.info(f"Uncommented and set org.gradle.java.home to: {java_path}")
                    break
            
            if not updated:
                # Add the property if it doesn't exist
                lines.append(f'org.gradle.java.home={java_path}\n')
                self.logger.info(f"Added org.gradle.java.home={java_path}")
            
            with open(gradle_props, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True, f"Updated gradle.properties with JAVA_HOME: {java_path}"
            
        except Exception as e:
            error_msg = f"Failed to update gradle.properties: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def configure_build_gradle(self, project_path):
        """Configure build.gradle - comment out test sourceSets and ensure eclipse block is present"""
        build_gradle = project_path / 'build.gradle'
        
        if not build_gradle.exists():
            self.logger.warning(f"build.gradle not found: {build_gradle}")
            return False, "build.gradle not found"
        
        try:
            with open(build_gradle, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            
            # Check if test sourceSets is already commented
            if 'test {' in content and '/*' not in content.split('sourceSets')[1].split('test {')[0]:
                # Comment out test sourceSets block
                import re
                # Find test block within sourceSets
                pattern = r'(sourceSets\s*\{[^}]*?)(\s+test\s*\{[^}]*?\}[^}]*?\*/?)'
                if re.search(pattern, content, re.DOTALL):
                    # Already has comment markers, skip
                    self.logger.info("test sourceSets already commented")
                else:
                    # Add comment markers if test block exists and isn't commented
                    test_pattern = r'(\n)(\s+)(test\s*\{(?:[^{}]|\{[^}]*\})*\})'
                    def comment_test(match):
                        return f"{match.group(1)}{match.group(2)}/*{match.group(3)}*/"
                    
                    new_content = re.sub(test_pattern, comment_test, content, count=1)
                    if new_content != content:
                        content = new_content
                        modified = True
                        self.logger.info("Commented out test sourceSets block")
            
            # Check if eclipse block exists after sourceSets
            if 'eclipse {' in content:
                # Check if it has the correct configuration
                if 'containers.remove' in content and 'org.eclipse.jst.j2ee.internal.web.container' in content:
                    self.logger.info("eclipse block already configured correctly")
                else:
                    # Eclipse block exists but might need updating
                    self.logger.info("eclipse block exists with different configuration")
            else:
                # Add eclipse block after sourceSets
                eclipse_block = '''\neclipse {\n    classpath {\n        // This removes the 'Web App Libraries' container from the build path\n        // so only Gradle dependencies are used for compilation\n        containers.remove('org.eclipse.jst.j2ee.internal.web.container')\n    }\n}\n'''
                
                # Find the closing brace of sourceSets block
                import re
                pattern = r'(sourceSets\s*\{(?:[^{}]|\{[^}]*\})*\})'
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    insert_pos = match.end()
                    content = content[:insert_pos] + eclipse_block + content[insert_pos:]
                    modified = True
                    self.logger.info("Added eclipse block after sourceSets")
            
            if modified:
                with open(build_gradle, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, "Updated build.gradle successfully"
            else:
                return True, "build.gradle already configured correctly"
            
        except Exception as e:
            error_msg = f"Failed to update build.gradle: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def delete_spring_web_jars(self, project_path):
        """Delete spring-web-5.3*.jar files from WEB-INF/lib"""
        web_inf_lib = project_path / 'WebContent' / 'WEB-INF' / 'lib'
        
        if not web_inf_lib.exists():
            self.logger.warning(f"WEB-INF/lib not found: {web_inf_lib}")
            return False, "WEB-INF/lib directory not found"
        
        try:
            deleted_files = []
            # Find and delete spring-web-5.3*.jar (not spring-webmvc or spring-websocket)
            for jar_file in web_inf_lib.glob('spring-web-5.3*.jar'):
                # Exclude webmvc and websocket variants
                if 'webmvc' not in jar_file.name.lower() and 'websocket' not in jar_file.name.lower():
                    jar_file.unlink()
                    deleted_files.append(jar_file.name)
                    self.logger.info(f"Deleted: {jar_file.name}")
            
            if deleted_files:
                return True, f"Deleted {len(deleted_files)} file(s): {', '.join(deleted_files)}"
            else:
                return True, "No spring-web-5.3*.jar files found to delete"
            
        except Exception as e:
            error_msg = f"Failed to delete spring-web JARs: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def configure_gradle_project(self, project_path):
        """Main method to configure Gradle project files"""
        self.logger.info("Configuring Gradle project files...")
        print("[INFO] Configuring Gradle project files...")
        
        results = []
        
        # 1. Update gradle.properties
        success, msg = self.configure_gradle_properties(project_path)
        results.append(("gradle.properties", success, msg))
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        
        # 2. Update build.gradle
        success, msg = self.configure_build_gradle(project_path)
        results.append(("build.gradle", success, msg))
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        
        # 3. Delete spring-web JARs
        success, msg = self.delete_spring_web_jars(project_path)
        results.append(("spring-web JARs", success, msg))
        print(f"[{'OK' if success else 'FAIL'}] {msg}")
        
        # Check if all operations succeeded
        all_success = all(r[1] for r in results)
        
        if all_success:
            return True, "All Gradle configurations completed successfully"
        else:
            failed = [r[0] for r in results if not r[1]]
            return False, f"Some configurations failed: {', '.join(failed)}"
