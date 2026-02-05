"""
Eclipse Manager - Handles Eclipse workspace and project configuration
"""
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import logging


class EclipseManager:
    """Manages Eclipse configuration and project setup"""
    
    def __init__(self, config):
        """Initialize Eclipse manager with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def create_eclipse_workspace(self, workspace_path):
        """Create Eclipse workspace directory structure"""
        eclipse_workspace = workspace_path / self.config.eclipse_workspace_name
        eclipse_workspace.mkdir(parents=True, exist_ok=True)
        
        # Create .metadata directory
        metadata_dir = eclipse_workspace / '.metadata'
        metadata_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Created Eclipse workspace: {eclipse_workspace}")
        return eclipse_workspace
    
    def generate_project_file(self, project_path, project_name):
        """Generate .project file for Eclipse"""
        project_file = project_path / '.project'
        
        if project_file.exists():
            self.logger.info(f".project file already exists for {project_name}")
            return True
        
        project_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
    <name>{project_name}</name>
    <comment></comment>
    <projects>
    </projects>
    <buildSpec>
        <buildCommand>
            <name>org.eclipse.jdt.core.javabuilder</name>
            <arguments>
            </arguments>
        </buildCommand>
        <buildCommand>
            <name>org.eclipse.wst.common.project.facet.core.builder</name>
            <arguments>
            </arguments>
        </buildCommand>
        <buildCommand>
            <name>org.eclipse.wst.validation.validationbuilder</name>
            <arguments>
            </arguments>
        </buildCommand>
    </buildSpec>
    <natures>
        <nature>org.eclipse.jem.workbench.JavaEMFNature</nature>
        <nature>org.eclipse.wst.common.modulecore.ModuleCoreNature</nature>
        <nature>org.eclipse.jdt.core.javanature</nature>
        <nature>org.eclipse.wst.common.project.facet.core.nature</nature>
        <nature>org.eclipse.wst.jsdt.core.jsNature</nature>
    </natures>
</projectDescription>
"""
        
        with open(project_file, 'w', encoding='utf-8') as f:
            f.write(project_xml)
        
        self.logger.info(f"Generated .project file for {project_name}")
        return True
    
    def generate_classpath_file(self, project_path):
        """Generate .classpath file for Eclipse"""
        classpath_file = project_path / '.classpath'
        
        if classpath_file.exists():
            self.logger.info(f".classpath file already exists")
            return True
        
        classpath_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<classpath>
    <classpathentry kind="src" output="bin/main" path="src/main/java">
        <attributes>
            <attribute name="optional" value="true"/>
            <attribute name="gradle_used_by_scope" value="main,test"/>
        </attributes>
    </classpathentry>
    <classpathentry kind="src" output="bin/test" path="src/test/java">
        <attributes>
            <attribute name="optional" value="true"/>
            <attribute name="gradle_used_by_scope" value="test"/>
            <attribute name="test" value="true"/>
        </attributes>
    </classpathentry>
    <classpathentry kind="src" path="src/main/resources"/>
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-{self.config.java_version}"/>
    <classpathentry kind="con" path="org.eclipse.buildship.core.gradleclasspathcontainer"/>
    <classpathentry kind="output" path="bin/default"/>
</classpath>
"""
        
        with open(classpath_file, 'w', encoding='utf-8') as f:
            f.write(classpath_xml)
        
        self.logger.info(f"Generated .classpath file")
        return True
    
    def generate_settings(self, project_path):
        """Generate Eclipse settings files"""
        settings_dir = project_path / '.settings'
        settings_dir.mkdir(exist_ok=True)
        
        # Generate org.eclipse.jdt.core.prefs
        jdt_prefs = settings_dir / 'org.eclipse.jdt.core.prefs'
        jdt_content = f"""eclipse.preferences.version=1
org.eclipse.jdt.core.compiler.codegen.inlineJsrBytecode=enabled
org.eclipse.jdt.core.compiler.codegen.targetPlatform={self.config.java_version}
org.eclipse.jdt.core.compiler.compliance={self.config.java_version}
org.eclipse.jdt.core.compiler.problem.assertIdentifier=error
org.eclipse.jdt.core.compiler.problem.enablePreviewFeatures=disabled
org.eclipse.jdt.core.compiler.problem.enumIdentifier=error
org.eclipse.jdt.core.compiler.problem.forbiddenReference=warning
org.eclipse.jdt.core.compiler.problem.reportPreviewFeatures=warning
org.eclipse.jdt.core.compiler.release=enabled
org.eclipse.jdt.core.compiler.source={self.config.java_version}
"""
        with open(jdt_prefs, 'w', encoding='utf-8') as f:
            f.write(jdt_content)
        
        # Generate org.eclipse.wst.common.project.facet.core.xml
        facet_file = settings_dir / 'org.eclipse.wst.common.project.facet.core.xml'
        facet_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<faceted-project>
  <runtime name="Apache Tomcat v{self.config.tomcat_version}"/>
  <fixed facet="wst.jsdt.web"/>
  <installed facet="java" version="{self.config.java_version}"/>
  <installed facet="jst.web" version="4.0"/>
  <installed facet="wst.jsdt.web" version="1.0"/>
</faceted-project>
"""
        with open(facet_file, 'w', encoding='utf-8') as f:
            f.write(facet_content)
        
        self.logger.info(f"Generated Eclipse settings")
        return True
    
    def configure_tomcat_server(self, eclipse_workspace):
        """Configure Tomcat server in Eclipse workspace"""
        servers_dir = eclipse_workspace / 'Servers'
        servers_dir.mkdir(exist_ok=True)
        
        # Create server.xml configuration
        server_xml = servers_dir / 'server.xml'
        server_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Server port="8005" shutdown="SHUTDOWN">
  <Service name="Catalina">
    <Connector connectionTimeout="20000" port="{self.config.tomcat_port}" 
               protocol="HTTP/1.1" redirectPort="8443"/>
    <Engine defaultHost="localhost" name="Catalina">
      <Host appBase="webapps" autoDeploy="true" name="localhost" 
            unpackWARs="true"/>
    </Engine>
  </Service>
</Server>
"""
        with open(server_xml, 'w', encoding='utf-8') as f:
            f.write(server_content)
        
        self.logger.info(f"Configured Tomcat server on port {self.config.tomcat_port}")
        return True
    
    def setup_project(self, workspace_path):
        """Setup the configured project in Eclipse"""
        eclipse_repo = self.config.get_eclipse_repo()
        project_path = workspace_path / eclipse_repo['name']
        
        if not project_path.exists():
            self.logger.error(f"Project path does not exist: {project_path}")
            return False
        
        # Generate Eclipse project files
        self.generate_project_file(project_path, eclipse_repo['name'])
        self.generate_classpath_file(project_path)
        self.generate_settings(project_path)
        
        # Create Eclipse workspace
        eclipse_workspace = self.create_eclipse_workspace(workspace_path)
        
        # Configure Tomcat server
        self.configure_tomcat_server(eclipse_workspace)
        
        self.logger.info(f"Successfully configured project: {eclipse_repo['name']}")
        return True, eclipse_workspace
