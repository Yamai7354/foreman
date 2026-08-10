"""
GitHub Manager - Repository setup and management tools.

Features:
- Initialize new repositories with proper structure
- Generate .gitignore files based on project type
- Add GitHub Actions workflow templates
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from .config import get_config
from .utils import get_project_type, log_error, log_info, log_success, log_warning

console = Console()


# ============================================================================
# Gitignore Templates
# ============================================================================

GITIGNORE_TEMPLATES = {
    "python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv/
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.tox/
.coverage
.coverage.*
htmlcov/
.pytest_cache/
.mypy_cache/

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db
""",

    "node": """# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# Build
dist/
build/
.next/
out/

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp

# Testing
coverage/

# OS
.DS_Store
Thumbs.db
""",

    "mixed": """# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
.eggs/
dist/
build/
.venv/
venv/

# Node.js
node_modules/
npm-debug.log*
.next/

# Environment
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*~

# Testing
.coverage
.pytest_cache/
coverage/

# OS
.DS_Store
Thumbs.db
""",

    "default": """# IDE
.idea/
.vscode/
*.swp
*~

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
"""
}


# ============================================================================
# GitHub Actions Templates
# ============================================================================

ACTIONS_TEMPLATES = {
    "ci": {
        "python": """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Run tests
      run: pytest

    - name: Run linting
      run: |
        pip install ruff
        ruff check .
""",
        "node": """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
    - uses: actions/checkout@v4

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Run linting
      run: npm run lint
"""
    },

    "deploy": {
        "python": """name: Deploy

on:
  push:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      if: github.event_name == 'release'
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
      run: twine upload dist/*
""",
        "node": """name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Use Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Build
      run: npm run build

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./dist
"""
    },

    "test": {
        "python": """name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]

    - name: Run tests with coverage
      run: |
        pip install pytest-cov
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
""",
        "node": """name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Use Node.js
      uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests with coverage
      run: npm run test:coverage

    - name: Upload coverage
      uses: codecov/codecov-action@v3
"""
    }
}


# ============================================================================
# CLI Functions
# ============================================================================

def init_repository(project_path: str, name: Optional[str], description: Optional[str],
                   private: bool, template: str):
    """Initialize a new GitHub repository with proper structure."""
    project_path = Path(project_path).resolve()
    config = get_config()

    # Create directory if it doesn't exist
    project_path.mkdir(parents=True, exist_ok=True)

    repo_name = name or project_path.name
    log_info(f"Initializing repository: {repo_name}")

    # Check if git is already initialized
    git_dir = project_path / ".git"
    if not git_dir.exists():
        # Initialize git
        result = subprocess.run(
            ["git", "init"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log_success("Git repository initialized")
        else:
            log_error(f"Failed to initialize git: {result.stderr}")
            return
    else:
        log_info("Git already initialized")

    # Detect project type and generate gitignore
    project_type = get_project_type(project_path)
    generate_gitignore(str(project_path), project_type)

    # Create README if it doesn't exist
    readme_path = project_path / "README.md"
    if not readme_path.exists():
        readme_content = f"""# {repo_name}

{description or 'A new project.'}

## Installation

```bash
# Add installation instructions
```

## Usage

```bash
# Add usage examples
```

## License

MIT
"""
        readme_path.write_text(readme_content, encoding="utf-8")
        log_success("README.md created")

    # Create LICENSE if it doesn't exist
    license_path = project_path / "LICENSE"
    if not license_path.exists():
        license_content = f"""MIT License

Copyright (c) {datetime.now().year} {config.author_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        license_path.write_text(license_content, encoding="utf-8")
        log_success("LICENSE (MIT) created")

    # Add GitHub Actions CI
    add_github_action(str(project_path), "ci")

    # Create initial commit
    subprocess.run(["git", "add", "."], cwd=project_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project_path,
        capture_output=True
    )
    log_success("Initial commit created")

    # Display next steps
    console.print(Panel(
        f"[bold green]Repository Ready![/bold green]\n\n"
        f"📁 Location: {project_path}\n"
        f"📦 Name: {repo_name}\n"
        f"🔧 Type: {project_type}\n\n"
        f"[bold]Next steps:[/bold]\n"
        f"1. Create repo on GitHub: https://github.com/new\n"
        f"2. Add remote: git remote add origin https://github.com/{config.github_username}/{repo_name}.git\n"
        f"3. Push: git push -u origin main",
        title="🐙 GitHub Setup",
        border_style="green"
    ))


def generate_gitignore(project_path: str, project_type: Optional[str]):
    """Generate .gitignore for project based on its type."""
    project_path = Path(project_path).resolve()

    # Auto-detect if not specified
    if not project_type:
        project_type = get_project_type(project_path)

    log_info(f"Generating .gitignore for {project_type} project")

    # Get template
    template = GITIGNORE_TEMPLATES.get(project_type, GITIGNORE_TEMPLATES["default"])

    # Write file
    gitignore_path = project_path / ".gitignore"

    if gitignore_path.exists():
        log_warning(".gitignore already exists, appending new rules")
        existing = gitignore_path.read_text(encoding="utf-8")
        # Add new rules that aren't already present
        new_rules = []
        for line in template.strip().split('\n'):
            if line and not line.startswith('#') and line not in existing:
                new_rules.append(line)

        if new_rules:
            with open(gitignore_path, 'a', encoding="utf-8") as f:
                f.write("\n# Added by Foreman\n")
                f.write("\n".join(new_rules))
            log_success(f"Added {len(new_rules)} new rules to .gitignore")
        else:
            log_info("No new rules to add")
    else:
        gitignore_path.write_text(template, encoding="utf-8")
        log_success(f".gitignore created for {project_type} project")


def add_github_action(project_path: str, workflow: str):
    """Add GitHub Actions workflow to project."""
    project_path = Path(project_path).resolve()

    # Detect project type
    project_type = get_project_type(project_path)
    if project_type not in ("python", "node"):
        project_type = "python"  # Default to Python

    log_info(f"Adding {workflow} workflow for {project_type} project")

    # Get template
    if workflow not in ACTIONS_TEMPLATES:
        log_error(f"Unknown workflow: {workflow}. Available: ci, deploy, test")
        return

    template = ACTIONS_TEMPLATES[workflow].get(project_type, ACTIONS_TEMPLATES[workflow].get("python"))

    # Create workflows directory
    workflows_dir = project_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Write workflow file
    workflow_file = workflows_dir / f"{workflow}.yml"

    if workflow_file.exists():
        log_warning(f"{workflow}.yml already exists, skipping")
        return

    workflow_file.write_text(template, encoding="utf-8")
    log_success(f"Created .github/workflows/{workflow}.yml")

    # Display preview
    console.print(Panel(
        template[:500] + "..." if len(template) > 500 else template,
        title=f"📋 {workflow.upper()} Workflow",
        border_style="blue"
    ))
