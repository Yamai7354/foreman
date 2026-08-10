# portfolio - API Reference

*Auto-generated on 2026-08-10*

## Classes

### `AutoLogEntry`
*Defined in: tools\auto_logger.py:39*

A single auto-log entry.

---

### `AutoLogStore`
*Defined in: tools\auto_logger.py:171*

Manages central log storage.

**Methods:**

#### `__init__()`

#### `load_logs()`
> Load all log entries.

#### `save_logs(logs)`
> Save all log entries.

#### `add_entry(entry)`
> Add a new log entry.

#### `get_recent(limit, log_type, project)`
> Get recent log entries with optional filters.

#### `get_last_error(project)`
> Get the most recent error for linking fixes.

---

### `CodeIssue`
*Defined in: tools\code_watcher.py:79*

A detected code issue.

---

### `IssueStore`
*Defined in: tools\code_watcher.py:96*

Manages code issue storage.

**Methods:**

#### `__init__()`

#### `load_issues()`
> Load all issues.

#### `save_issues(issues)`
> Save all issues.

#### `add_issue(issue)`
> Add a new issue.

#### `get_issues(unresolved_only, file_path)`
> Get issues with optional filters.

#### `clear_issues_for_file(file_path)`
> Clear all issues for a specific file (re-scan clears old issues).

---

### `CodeWatchHandler`
*Defined in: tools\code_watcher.py:259*

Handler for file system events.

**Methods:**

#### `__init__(watch_path)`

#### `should_watch(path)`
> Check if file should be watched.

#### `on_modified(path)`
> Handle file modification.

#### `process_pending()`
> Process files that have been stable for debounce period.

#### `analyze_file(path)`
> Analyze a single file.

---

### `WatchdogHandler`
*Defined in: tools\code_watcher.py:447*

**Methods:**

#### `on_modified(event)`

#### `on_created(event)`

---

### `Config`
*Defined in: tools\config.py:20*

Central configuration for Foreman.

**Methods:**

#### `__post_init__()`
> Ensure directories exist.

#### `from_file(cls, config_path)`
> Load configuration from a YAML file.

#### `save(config_path)`
> Save configuration to a YAML file.

---

### `PythonAnalyzer`
*Defined in: tools\doc_generator.py:82*

Analyze Python files for documentation extraction.

**Methods:**

#### `__init__(file_path)`

#### `get_module_docstring()`
> Get the module-level docstring.

#### `get_classes()`
> Get all classes with their docstrings and methods.

#### `get_functions()`
> Get all top-level functions with their docstrings.

---

### `LogEntry`
*Defined in: tools\workflow_tracker.py:36*

A single log entry (change, problem, solution, or note).

---

### `WorkSession`
*Defined in: tools\workflow_tracker.py:48*

A work session with start/end times and associated logs.

---

### `WorkflowStore`
*Defined in: tools\workflow_tracker.py:90*

SQLite-backed storage for workflow tracking data (sessions + entries).

**Methods:**

#### `__init__()`

#### `load_sessions()`
> Load all work sessions, keyed by id.

#### `load_entries()`
> Load all log entries, keyed by id.

#### `get_current_session()`
> Get the current active session, freshly read from `sessions`.

#### `set_current_session(session)`
> Mark `session` (or None) as the active session.

#### `add_session(session)`
> Add a new session.

#### `update_session(session_id, updates)`
> Update an existing session.

#### `add_entry(entry)`
> Add a new log entry, linked to the current session if one is active.

#### `get_sessions_in_range(start_date, end_date)`
> Get sessions within a date range (inclusive, YYYY-MM-DD).

#### `get_entries_for_session(session_id)`
> Get all entries for a session, oldest first.

---

## Functions

### `test_root_help()`
*Defined in: tests\test_cli_smoke.py:8*


---

### `test_core_groups_available()`
*Defined in: tests\test_cli_smoke.py:16*


---

### `detect_project()`
*Defined in: tools\auto_logger.py:57*

Auto-detect project name and path from current directory.

Checks (in order):
1. Git repository name
2. pyproject.toml project name
3. package.json name
4. Current directory name

Returns: (project_name, project_path)

---

### `generate_summary(log_type, message)`
*Defined in: tools\auto_logger.py:122*

Generate an LLM summary for the log entry using autolog-specific LLM.

---

### `get_store()`
*Defined in: tools\auto_logger.py:222*

Get the global store instance.

---

### `log_entry(log_type, message, link_to_error, tags)`
*Defined in: tools\auto_logger.py:234*

Log an entry with optional LLM summary.

---

### `display_entry(entry)`
*Defined in: tools\auto_logger.py:267*

Display a log entry nicely.

---

### `cli_main()`
*Defined in: tools\auto_logger.py:300*

🔍 Auto-Logger - Track errors, fixes, and changes across projects.

Logs are stored centrally at ~/.foreman_logs/

---

### `cmd_error(message, tags)`
*Defined in: tools\auto_logger.py:312*

Log an error.

---

### `cmd_fix(message, tags, link)`
*Defined in: tools\auto_logger.py:324*

Log a fix/resolution.

---

### `cmd_change(message, tags)`
*Defined in: tools\auto_logger.py:337*

Log a change.

---

### `cmd_note(message, tags)`
*Defined in: tools\auto_logger.py:348*

Log a note.

---

### `cmd_todo(message, tags)`
*Defined in: tools\auto_logger.py:357*

Log a todo item.

---

### `cmd_list(log_type, project, limit, show_all)`
*Defined in: tools\auto_logger.py:368*

List recent log entries.

---

### `cmd_report(project, output)`
*Defined in: tools\auto_logger.py:398*

Generate a summary report.

---

### `register_commands(main_cli)`
*Defined in: tools\auto_logger.py:470*

Register autolog commands with the main foreman CLI.

---

### `main()`
*Defined in: tools\cli.py:30*

🚧 Foreman - Your complete toolkit for managing developer projects.

Documentation, diagrams, GitHub integration, and workflow tracking.

---

### `docs()`
*Defined in: tools\cli.py:44*

📝 Documentation generation tools.

---

### `docs_generate(project_path, output, format)`
*Defined in: tools\cli.py:53*

Generate documentation for a project.

---

### `docs_readme(project_path, template)`
*Defined in: tools\cli.py:62*

Generate a README.md for a project.

---

### `docs_api(project_path, output)`
*Defined in: tools\cli.py:71*

Extract API documentation from code.

---

### `diagram()`
*Defined in: tools\cli.py:82*

📊 Diagram generation tools.

---

### `diagram_architecture(project_path, output, format)`
*Defined in: tools\cli.py:91*

Generate architecture diagram from project structure.

---

### `diagram_flowchart(file_path, output, function)`
*Defined in: tools\cli.py:101*

Generate flowchart from code logic.

---

### `diagram_classes(project_path, output)`
*Defined in: tools\cli.py:110*

Generate class diagram from project.

---

### `github()`
*Defined in: tools\cli.py:121*

🐙 GitHub repository management.

---

### `github_init(project_path, name, description, private, template)`
*Defined in: tools\cli.py:132*

Initialize a new GitHub repository.

---

### `github_gitignore(project_path, project_type)`
*Defined in: tools\cli.py:141*

Generate .gitignore for project.

---

### `github_actions(project_path, workflow)`
*Defined in: tools\cli.py:150*

Add GitHub Actions workflow.

---

### `track()`
*Defined in: tools\cli.py:161*

📋 Workflow and session tracking.

---

### `track_start(description, project, tags)`
*Defined in: tools\cli.py:170*

Start a new work session.

---

### `track_end(summary)`
*Defined in: tools\cli.py:178*

End current work session.

---

### `track_log(message, log_type)`
*Defined in: tools\cli.py:187*

Log a change, problem, or note.

---

### `track_status()`
*Defined in: tools\cli.py:194*

Show current session status.

---

### `track_history(days)`
*Defined in: tools\cli.py:202*

Show session history.

---

### `report()`
*Defined in: tools\cli.py:213*

📈 Report generation.

---

### `report_daily(date, output)`
*Defined in: tools\cli.py:221*

Generate daily report.

---

### `report_weekly(week, output)`
*Defined in: tools\cli.py:230*

Generate weekly report.

---

### `report_project(project_name, output)`
*Defined in: tools\cli.py:239*

Generate project status report.

---

### `config()`
*Defined in: tools\cli.py:250*

⚙️ Configuration management.

---

### `config_show()`
*Defined in: tools\cli.py:256*

Show current configuration.

---

### `config_set(key, value)`
*Defined in: tools\cli.py:274*

Set a configuration value and persist it to config.yaml.

---

### `get_system_prompt()`
*Defined in: tools\code_watcher.py:147*

Get the system prompt, allowing customization via file.

---

### `analyze_code(file_path, content)`
*Defined in: tools\code_watcher.py:157*

Analyze code using LLM and return detected issues.

---

### `log_to_file(message)`
*Defined in: tools\code_watcher.py:223*

Log message to codewatch log file.

---

### `detect_project(path)`
*Defined in: tools\code_watcher.py:235*

Detect project name from path.

---

### `is_daemon_running()`
*Defined in: tools\code_watcher.py:357*

Check if daemon is running.

---

### `crawl_all_files(watch_path, handler)`
*Defined in: tools\code_watcher.py:371*

Crawl and analyze all code files in directory.

---

### `start_daemon(watch_path, initial_crawl, scan_only)`
*Defined in: tools\code_watcher.py:384*

Start the watcher daemon.

---

### `run_watcher(watch_path, initial_crawl, scan_only)`
*Defined in: tools\code_watcher.py:426*

Run the file watcher loop.

---

### `stop_daemon()`
*Defined in: tools\code_watcher.py:472*

Stop the watcher daemon.

---

### `cli_main()`
*Defined in: tools\code_watcher.py:492*

🔍 Code Watcher - Background LLM-powered code analyzer.

Watches code files and uses an LLM to detect potential issues.

---

### `cmd_start(path, crawl, scan_only)`
*Defined in: tools\code_watcher.py:505*

Start the code watcher daemon.

---

### `cmd_stop()`
*Defined in: tools\code_watcher.py:513*

Stop the code watcher daemon.

---

### `cmd_status()`
*Defined in: tools\code_watcher.py:519*

Check if the daemon is running.

---

### `cmd_issues(unresolved, file_path, limit)`
*Defined in: tools\code_watcher.py:532*

View detected issues.

---

### `cmd_scan(path, extensions)`
*Defined in: tools\code_watcher.py:565*

Perform a one-time scan of a directory.

---

### `cmd_clear(clear_all, file_path)`
*Defined in: tools\code_watcher.py:599*

Clear stored issues.

---

### `cmd_log(lines, follow)`
*Defined in: tools\code_watcher.py:616*

View the daemon log.

---

### `cmd_prompt(show, edit, reset)`
*Defined in: tools\code_watcher.py:642*

Configure the LLM system prompt.

---

### `get_config()`
*Defined in: tools\config.py:83*

Get the global configuration instance.

---

### `get_db_path()`
*Defined in: tools\db.py:43*


---

### `get_connection()`
*Defined in: tools\db.py:47*


---

### `dumps(value)`
*Defined in: tools\db.py:57*


---

### `loads(value)`
*Defined in: tools\db.py:61*


---

### `generate_architecture_diagram(project_path, output, format)`
*Defined in: tools\diagram_generator.py:36*

Generate architecture diagram from project structure.

---

### `analyze_imports(project_path)`
*Defined in: tools\diagram_generator.py:106*

Analyze Python imports to find module connections.

---

### `generate_class_diagram(project_path, output)`
*Defined in: tools\diagram_generator.py:149*

Generate class diagram from Python code.

---

### `generate_flowchart(file_path, output, function)`
*Defined in: tools\diagram_generator.py:240*

Generate flowchart from function logic.

---

### `generate_function_flowchart(func_node)`
*Defined in: tools\diagram_generator.py:304*

Generate Mermaid flowchart for a single function.

---

### `analyze_project(project_path)`
*Defined in: tools\doc_generator.py:145*

Analyze a project and extract documentation info.

---

### `generate_structure_tree(project_path, max_depth)`
*Defined in: tools\doc_generator.py:189*

Generate a tree view of project structure.

---

### `generate_documentation(project_path, output, format)`
*Defined in: tools\doc_generator.py:219*

Generate comprehensive documentation for a project.

---

### `generate_readme(project_path, template)`
*Defined in: tools\doc_generator.py:253*

Generate a README.md for a project.

---

### `generate_api_docs(project_path, output)`
*Defined in: tools\doc_generator.py:315*

Extract API documentation from code.

---

### `generate_api_markdown(info)`
*Defined in: tools\doc_generator.py:337*

Generate API reference in Markdown format.

---

### `init_repository(project_path, name, description, private, template)`
*Defined in: tools\github_manager.py:390*

Initialize a new GitHub repository with proper structure.

---

### `generate_gitignore(project_path, project_type)`
*Defined in: tools\github_manager.py:505*

Generate .gitignore for project based on its type.

---

### `add_github_action(project_path, workflow)`
*Defined in: tools\github_manager.py:542*

Add GitHub Actions workflow to project.

---

### `call_llm(prompt)`
*Defined in: tools\report_agent.py:32*

Call the local LLM to generate a summary.

---

### `generate_markdown_report(title, subtitle, sessions, entries, llm_summary)`
*Defined in: tools\report_agent.py:68*

Generate a markdown report from session and entry data.

---

### `generate_daily_report(date, output)`
*Defined in: tools\report_agent.py:193*

Generate a daily work report.

---

### `generate_weekly_report(week_start, output)`
*Defined in: tools\report_agent.py:251*

Generate a weekly work report.

---

### `generate_project_report(project_name, output)`
*Defined in: tools\report_agent.py:320*

Generate a project-specific report.

---

### `log_info(message)`
*Defined in: tools\utils.py:28*

Print an info message.

---

### `log_success(message)`
*Defined in: tools\utils.py:33*

Print a success message.

---

### `log_warning(message)`
*Defined in: tools\utils.py:38*

Print a warning message.

---

### `log_error(message)`
*Defined in: tools\utils.py:43*

Print an error message.

---

### `load_json(path)`
*Defined in: tools\utils.py:48*

Load JSON data from a file.

---

### `save_json(path, data, indent)`
*Defined in: tools\utils.py:56*

Save JSON data to a file.

---

### `get_timestamp()`
*Defined in: tools\utils.py:63*

Get current timestamp in ISO format.

---

### `get_date()`
*Defined in: tools\utils.py:68*

Get current date in YYYY-MM-DD format.

---

### `format_duration(seconds)`
*Defined in: tools\utils.py:73*

Format a duration in seconds to a human-readable string.

---

### `get_project_type(project_path)`
*Defined in: tools\utils.py:87*

Detect the type of project based on files present.

---

### `display_panel(title, content, style)`
*Defined in: tools\utils.py:113*

Display content in a styled panel.

---

### `display_code(code, language)`
*Defined in: tools\utils.py:118*

Display syntax-highlighted code.

---

### `display_table(title, columns, rows)`
*Defined in: tools\utils.py:124*

Display data in a table format.

---

### `find_python_files(directory)`
*Defined in: tools\utils.py:134*

Find all Python files in a directory.

---

### `find_js_files(directory)`
*Defined in: tools\utils.py:139*

Find all JavaScript files in a directory.

---

### `read_file_safely(path)`
*Defined in: tools\utils.py:144*

Read a file, returning None if it doesn't exist or can't be read.

---

### `_session_row_to_dict(row)`
*Defined in: tools\workflow_tracker.py:65*


---

### `_entry_row_to_dict(row)`
*Defined in: tools\workflow_tracker.py:78*


---

### `get_store()`
*Defined in: tools\workflow_tracker.py:179*

Get the global workflow store instance.

---

### `start_session(description, project, tags)`
*Defined in: tools\workflow_tracker.py:191*

Start a new work session.

---

### `end_session(summary)`
*Defined in: tools\workflow_tracker.py:227*

End the current work session.

---

### `log_entry(message, log_type)`
*Defined in: tools\workflow_tracker.py:283*

Log a change, problem, solution, or note.

---

### `show_status()`
*Defined in: tools\workflow_tracker.py:314*

Show current session status.

---

### `show_history(days)`
*Defined in: tools\workflow_tracker.py:356*

Show session history for the past N days.

---

### `get_sessions_for_date(date)`
*Defined in: tools\workflow_tracker.py:400*

Get all sessions for a specific date.

---

### `get_sessions_for_week(week_start)`
*Defined in: tools\workflow_tracker.py:406*

Get all sessions for a week starting from the given date.

---

### `get_all_entries_for_sessions(sessions)`
*Defined in: tools\workflow_tracker.py:414*

Get all log entries for a list of sessions.

---

### `export_session_data(session_id)`
*Defined in: tools\workflow_tracker.py:423*

Export full session data including entries.

---
