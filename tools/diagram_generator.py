"""
Diagram Generator - Generate Mermaid diagrams from code.

Features:
- Architecture diagrams from project structure
- Class diagrams from Python code
- Flowcharts from function logic
"""

import ast
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .utils import (
    find_python_files,
    log_error,
    log_info,
    log_success,
    log_warning,
    read_file_safely,
)

console = Console()


# ============================================================================
# Architecture Diagram Generator
# ============================================================================


def generate_architecture_diagram(project_path: str, output: Optional[str], format: str):
    """Generate architecture diagram from project structure."""
    project_path = Path(project_path).resolve()
    log_info(f"Generating architecture diagram for: {project_path.name}")

    # Find all directories and key files
    dirs = set()
    files_by_dir = {}

    for item in project_path.rglob("*"):
        # Skip hidden and common ignore patterns
        if any(
            part.startswith(".")
            or part in ("__pycache__", "node_modules", "venv", ".venv", ".git", "egg-info")
            for part in item.parts
        ):
            continue

        if item.is_file() and item.suffix in (".py", ".js", ".ts", ".jsx", ".tsx"):
            rel_path = item.relative_to(project_path)
            parent = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
            dirs.add(parent)

            if parent not in files_by_dir:
                files_by_dir[parent] = []
            files_by_dir[parent].append(item.stem)

    # Build Mermaid diagram
    lines = ["```mermaid", "graph TB"]

    # Add subgraphs for each directory
    for i, (dir_name, files) in enumerate(sorted(files_by_dir.items())):
        safe_dir = dir_name.replace("/", "_").replace(".", "_")
        display_name = dir_name if dir_name != "root" else project_path.name

        lines.append(f'    subgraph {safe_dir}["{display_name}"]')
        for j, file in enumerate(files[:10]):  # Limit to 10 files per dir
            node_id = f"{safe_dir}_{j}"
            lines.append(f"        {node_id}[{file}]")
        if len(files) > 10:
            lines.append(f'        {safe_dir}_more["... +{len(files) - 10} more"]')
        lines.append("    end")

    # Add connections between directories based on imports
    import_connections = analyze_imports(project_path)
    for src, dst in import_connections[:20]:  # Limit connections
        lines.append(f"    {src} --> {dst}")

    lines.append("```")
    diagram = "\n".join(lines)

    # Output
    if output:
        output_path = Path(output)
    else:
        output_path = project_path / "docs" / "architecture.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = f"# {project_path.name} - Architecture\n\n*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n{diagram}"
    output_path.write_text(content, encoding="utf-8")

    log_success(f"Architecture diagram saved to: {output_path}")

    # Display preview
    console.print(
        Panel(Syntax(diagram, "markdown", theme="monokai"), title="📊 Architecture Diagram")
    )


def analyze_imports(project_path: Path) -> list[tuple[str, str]]:
    """Analyze Python imports to find module connections."""
    connections = []

    for py_file in find_python_files(project_path):
        if any(
            part.startswith(".") or part in ("__pycache__", "venv", ".venv")
            for part in py_file.parts
        ):
            continue

        content = read_file_safely(py_file)
        if not content:
            continue

        try:
            tree = ast.parse(content)
            rel_path = py_file.relative_to(project_path)
            src_module = str(rel_path.parent).replace("/", "_")
            if src_module == ".":
                src_module = "root"

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not alias.name.startswith("_"):
                            dst = alias.name.split(".")[0]
                            connections.append((f"{src_module}_0", f"ext_{dst}"))
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 1:  # Relative import
                        dst = node.module.split(".")[0]
                        connections.append((f"{src_module}_0", f"{src_module}_{dst}"))
        except Exception:
            pass

    return list(set(connections))


# ============================================================================
# Class Diagram Generator
# ============================================================================


def generate_class_diagram(project_path: str, output: Optional[str]):
    """Generate class diagram from Python code."""
    project_path = Path(project_path).resolve()
    log_info(f"Generating class diagram for: {project_path.name}")

    classes = []

    # Find all classes
    for py_file in find_python_files(project_path):
        if any(
            part.startswith(".") or part in ("__pycache__", "venv", ".venv")
            for part in py_file.parts
        ):
            continue

        content = read_file_safely(py_file)
        if not content:
            continue

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    cls_info = {
                        "name": node.name,
                        "bases": [base.id for base in node.bases if isinstance(base, ast.Name)],
                        "methods": [],
                        "attributes": [],
                    }

                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            visibility = "+" if not item.name.startswith("_") else "-"
                            args = [a.arg for a in item.args.args if a.arg != "self"]
                            cls_info["methods"].append(
                                f"{visibility}{item.name}({', '.join(args)})"
                            )
                        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            cls_info["attributes"].append(f"+{item.target.id}")

                    classes.append(cls_info)
        except Exception:
            pass

    if not classes:
        log_warning("No classes found in project")
        return

    # Build Mermaid class diagram
    lines = ["```mermaid", "classDiagram"]

    for cls in classes:
        lines.append(f"    class {cls['name']} {{")
        for attr in cls["attributes"][:5]:
            lines.append(f"        {attr}")
        for method in cls["methods"][:10]:
            lines.append(f"        {method}")
        lines.append("    }")

        # Add inheritance relationships
        for base in cls["bases"]:
            if any(c["name"] == base for c in classes):
                lines.append(f"    {base} <|-- {cls['name']}")

    lines.append("```")
    diagram = "\n".join(lines)

    # Output
    if output:
        output_path = Path(output)
    else:
        output_path = project_path / "docs" / "classes.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = f"# {project_path.name} - Class Diagram\n\n*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n{diagram}"
    output_path.write_text(content, encoding="utf-8")

    log_success(f"Class diagram saved to: {output_path}")
    console.print(f"[bold]Classes documented:[/bold] {len(classes)}")

    # Display preview
    console.print(Panel(Syntax(diagram, "markdown", theme="monokai"), title="📊 Class Diagram"))


# ============================================================================
# Flowchart Generator
# ============================================================================


def generate_flowchart(file_path: str, output: Optional[str], function: Optional[str]):
    """Generate flowchart from function logic."""
    file_path = Path(file_path)
    log_info(f"Generating flowchart for: {file_path.name}")

    content = read_file_safely(file_path)
    if not content:
        log_error(f"Could not read file: {file_path}")
        return

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        log_error(f"Syntax error in file: {e}")
        return

    # Find target function(s)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if function is None or node.name == function:
                functions.append(node)

    if not functions:
        log_warning("No functions found" + (f" matching '{function}'" if function else ""))
        return

    diagrams = []
    for func in functions[:5]:  # Limit to 5 functions
        diagram = generate_function_flowchart(func)
        diagrams.append((func.name, diagram))

    # Output
    if output:
        output_path = Path(output)
    else:
        output_path = file_path.parent / "docs" / f"flowchart_{file_path.stem}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {file_path.stem} - Flowcharts\n",
        f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n",
    ]

    for func_name, diagram in diagrams:
        lines.append(f"\n## `{func_name}`\n")
        lines.append(diagram)

    output_path.write_text("\n".join(lines), encoding="utf-8")

    log_success(f"Flowcharts saved to: {output_path}")
    console.print(f"[bold]Functions diagrammed:[/bold] {len(diagrams)}")

    # Display first diagram
    if diagrams:
        console.print(
            Panel(
                Syntax(diagrams[0][1], "markdown", theme="monokai"),
                title=f"📊 Flowchart: {diagrams[0][0]}",
            )
        )


def generate_function_flowchart(func_node: ast.FunctionDef) -> str:
    """Generate Mermaid flowchart for a single function."""
    lines = ["```mermaid", "flowchart TD"]
    node_id = [0]

    def get_id():
        node_id[0] += 1
        return f"N{node_id[0]}"

    def process_body(body: list, parent_id: str = None) -> str:
        """Process a list of statements and return the last node ID."""
        last_id = parent_id

        for stmt in body:
            current_id = get_id()

            if isinstance(stmt, ast.If):
                # Condition node (diamond)
                cond_text = ast.unparse(stmt.test)[:30]
                lines.append(f"    {current_id}{{{{{cond_text}}}}}")

                if last_id:
                    lines.append(f"    {last_id} --> {current_id}")

                # True branch
                yes_id = get_id()
                lines.append(f'    {yes_id}["Yes branch"]')
                lines.append(f"    {current_id} -->|Yes| {yes_id}")
                if stmt.body:
                    process_body(stmt.body[:3], yes_id)

                # False branch
                if stmt.orelse:
                    no_id = get_id()
                    lines.append(f'    {no_id}["No branch"]')
                    lines.append(f"    {current_id} -->|No| {no_id}")
                    process_body(stmt.orelse[:3], no_id)

                last_id = current_id

            elif isinstance(stmt, ast.For):
                loop_text = f"for {ast.unparse(stmt.target)} in ..."
                lines.append(f"    {current_id}{{{{{loop_text}}}}}")
                if last_id:
                    lines.append(f"    {last_id} --> {current_id}")

                body_id = get_id()
                lines.append(f'    {body_id}["Loop body"]')
                lines.append(f"    {current_id} --> {body_id}")
                lines.append(f"    {body_id} --> {current_id}")

                last_id = current_id

            elif isinstance(stmt, ast.While):
                lines.append(f"    {current_id}{{{{while loop}}}}")
                if last_id:
                    lines.append(f"    {last_id} --> {current_id}")
                last_id = current_id

            elif isinstance(stmt, ast.Return):
                ret_text = ast.unparse(stmt.value)[:20] if stmt.value else "None"
                lines.append(f'    {current_id}(["return {ret_text}"])')
                if last_id:
                    lines.append(f"    {last_id} --> {current_id}")
                last_id = current_id

            elif isinstance(stmt, ast.Assign):
                target = ast.unparse(stmt.targets[0])[:15]
                lines.append(f'    {current_id}["{target} = ..."]')
                if last_id:
                    lines.append(f"    {last_id} --> {current_id}")
                last_id = current_id

            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call_text = ast.unparse(stmt.value)[:25]
                lines.append(f'    {current_id}["{call_text}"]')
                if last_id:
                    lines.append(f"    {last_id} --> {current_id}")
                last_id = current_id

        return last_id

    # Start node
    args = [a.arg for a in func_node.args.args]
    start_id = get_id()
    lines.append(f'    {start_id}(["Start: {func_node.name}({", ".join(args[:3])})"])')

    # Process function body (limit to first 15 statements for readability)
    process_body(func_node.body[:15], start_id)

    lines.append("```")
    return "\n".join(lines)
