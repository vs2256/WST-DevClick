# Workspace Automation

One-click automation to setup development workspace with repository cloning, Eclipse configuration, Java/Tomcat setup, and application deployment.

## Features

✓ **Automatic Workspace Creation** - Creates versioned workspace directories (workspace_v1, workspace_v2, etc.)
✓ **Repository Cloning** - Clones multiple Git repositories in parallel
✓ **Eclipse Configuration** - Auto-generates Eclipse project files, classpath, and settings
✓ **Java & Tomcat Setup** - Configures Java version and Tomcat server
✓ **Build & Deploy** - Builds project (Gradle) and deploys to Tomcat
✓ **One-Click Execution** - Everything runs with a single command
✓ **Fully Configurable** - All settings in .env file (no code changes needed)

## Prerequisites

- Python 3.7 or higher (with venv module)
- Git
- Java JDK
- Apache Tomcat
- Gradle (if building projects)
- Eclipse IDE (optional)

## Quick Start

### 1. Configure Settings

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```properties
# Repository URLs
REPO_1_URL=https://github.com/your-org/repo1.git
REPO_2_URL=https://github.com/your-org/repo2.git
REPO_3_URL=https://github.com/your-org/repo3.git

# Which repository to configure in Eclipse (1, 2, or 3)
ECLIPSE_REPO_TO_CONFIGURE=1

# Paths
JAVA_HOME=C:/Program Files/Java/jdk-17
TOMCAT_HOME=C:/apache-tomcat-9.0.80
ECLIPSE_PATH=C:/eclipse/eclipse.exe

# Server Port
TOMCAT_PORT=8080
```

### 2. Run One-Click Setup

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Access Your Application

After setup completes:
- Application URL: `http://localhost:8080`
- Eclipse Workspace: `workspace_vX/eclipse-workspace`
- Project Location: `workspace_vX/repo-name`

## Configuration Reference

### Repository Configuration

```properties
# Add up to any number of repositories
REPO_1_URL=https://github.com/org/repo1.git
REPO_1_NAME=repo1

REPO_2_URL=https://github.com/org/repo2.git
REPO_2_NAME=repo2

REPO_3_URL=https://github.com/org/repo3.git
REPO_3_NAME=repo3
```

### Eclipse Configuration

```properties
# Which repo to configure (1, 2, or 3)
ECLIPSE_REPO_TO_CONFIGURE=1

# Eclipse paths
ECLIPSE_PATH=C:/eclipse/eclipse.exe
ECLIPSE_WORKSPACE_NAME=eclipse-workspace
```

### Java & Tomcat

```properties
JAVA_HOME=C:/Program Files/Java/jdk-17
JAVA_VERSION=17

TOMCAT_HOME=C:/apache-tomcat-9.0.80
TOMCAT_VERSION=9.0
TOMCAT_PORT=8080
```

## What Does It Do?

The automation performs these steps:

1. **Validates Prerequisites** - Checks Git, Java, Tomcat installations
2. **Creates Workspace** - Creates `workspace_v1` (or next available version)
3. **Clones Repositories** - Clones all configured repositories
4. **Configures Eclipse** - Generates `.project`, `.classpath`, and settings files
5. **Builds Project** - Runs Gradle build
6. **Deploys to Tomcat** - Copies WAR file to Tomcat webapps
7. **Starts Server** - Launches Tomcat on configured port

## Project Structure

```
WST DevClick/
├── automation.py           # Main orchestration script
├── config.py              # Configuration manager
├── workspace_manager.py   # Workspace & repo operations
├── eclipse_manager.py     # Eclipse configuration
├── build_manager.py       # Build & deployment
├── .env.example           # Configuration template
├── .env                   # Your configuration (git-ignored)
├── setup.bat              # Windows launcher
├── setup.sh               # Linux/Mac launcher
└── README.md              # This file
```

## Manual Execution

If you prefer to run directly:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automation
python automation.py
```

## Import Project in Eclipse

1. Launch Eclipse: `C:/eclipse/eclipse.exe`
2. Select workspace: `C:/work/WST DevClick/workspace_v1/eclipse-workspace`
3. File → Import → Existing Projects into Workspace
4. Browse to: `C:/work/WST DevClick/workspace_v1/repo-name`
5. Click Finish

## Troubleshooting

### Git Clone Fails
- Verify Git is installed: `git --version`
- Check repository URLs in .env
- Ensure you have access to repositories

### Build Fails
- Verify Gradle is installed
- Check JAVA_HOME is set correctly
- Review build logs in `automation_*.log`

### Tomcat Won't Start
- Verify TOMCAT_HOME path in .env
- Check if port 8080 is already in use
- Review Tomcat logs in `TOMCAT_HOME/logs`

### Eclipse Configuration Issues
- Ensure Eclipse is installed
- Check ECLIPSE_PATH in .env
- Verify Java version matches project requirements

## Logs

Automation creates detailed logs: `automation_YYYYMMDD_HHMMSS.log`

Check logs for detailed error messages and execution steps.

## Customization

### Adding More Repositories

Add to `.env`:
```properties
REPO_4_URL=https://github.com/org/repo4.git
REPO_4_NAME=repo4
```

### Changing Eclipse Project

Set `ECLIPSE_REPO_TO_CONFIGURE` to the repo number (1, 2, 3, etc.)

### Using Different Ports

Update `TOMCAT_PORT` and `APP_PORT` in `.env`

## License

This automation tool is provided as-is for development use.
