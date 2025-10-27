# analyze_project_history.py

**Purpose:** Analyzes a project directory to reconstruct its development timeline based on file metadata.

## Overview

This utility walks through a project folder and extracts file creation/modification dates to generate:
- Timeline of development activity
- Suggested development phases
- File categorization by type
- Weekly activity breakdown
- Recommendations for creating GanttProject historical data

## Features

- **File Metadata Analysis**: Collects creation and modification dates for all files
- **Automatic Categorization**: Groups files into categories:
  - Source code (.py, .js, .ts, etc.)
  - Documentation (.md, .txt, .rst)
  - Configuration (.json, .yaml, .toml, etc.)
  - Tests (test files)
  - Build system (Makefile, pyproject.toml, etc.)
  - Examples
  - Frontend (.html, .css, .scss)
- **Timeline Generation**: Groups file activity by week
- **Phase Detection**: Automatically suggests development phases:
  - Project Setup & Infrastructure
  - Core Implementation
  - Testing & Quality Assurance
  - Documentation
  - Examples & Demos
- **Git Detection**: Checks for git repository (future enhancement)
- **Multiple Output Formats**:
  - Markdown report with comprehensive analysis
  - JSON export for programmatic access

## Usage

```bash
# Basic usage - generates markdown report
python analyze_project_history.py /path/to/project

# Custom output filename
python analyze_project_history.py /path/to/project --output my_report.md

# Export JSON data
python analyze_project_history.py /path/to/project --json analysis.json

# Both markdown and JSON
python analyze_project_history.py /path/to/project --output report.md --json data.json
```

## Command-Line Options

- `project_path` (required): Path to the project directory to analyze
- `--output`, `-o`: Output filename for markdown report (default: `{project_name}_history.md`)
- `--json`: Export raw analysis data as JSON

## Output Format

### Markdown Report Includes:
- Project timeline (start date, end date, duration)
- Total file count
- File categories breakdown
- Suggested development phases with start dates
- Activity timeline (first 20 weeks)
- Recommendations for structuring historical data in GanttProject

### JSON Export Includes:
- `project_path`: Full path to analyzed project
- `git_available`: Boolean indicating if git repo detected
- `earliest_date`: First file creation date
- `latest_date`: Most recent modification date
- `total_files`: Count of files analyzed
- `file_categories`: Detailed file lists per category
- `timeline`: Week-by-week activity breakdown
- `suggested_phases`: Detected development phases

## Use Cases

1. **Historical GanttProject Data**: Generate timeline data for adding completed historical work to project plans
2. **Project Analysis**: Understand development patterns and activity over time
3. **Documentation**: Create comprehensive project history reports
4. **Project Archaeology**: Reconstruct timeline for projects lacking formal tracking

## Directory Exclusions

Automatically skips common directories:
- `.git` (version control)
- `__pycache__` (Python cache)
- `node_modules` (Node.js dependencies)
- `.pytest_cache` (test cache)
- `venv`, `.venv` (virtual environments)

## Integration

Works standalone or as input for:
- `generate_project_with_history.py` - Uses file dates to add historical Phase 0 data
- GanttProject file generation - Provides date ranges and phase suggestions

## Example Output

```
🔍 Analyzing project: /home/user/my_project
======================================================================
✓ Git repository detected
📁 Collecting file metadata...
  Found 381 files
  Date range: 2025-09-15 to 2025-10-07

🏷️  Categorizing files...
  source_code: 145 files
  documentation: 198 files
  tests: 63 files
  configuration: 247 files

📅 Generating timeline...

🎯 Suggesting project phases...
  Phase 1: Project Setup & Infrastructure
    Started: 2025-09-15
    Files: 248
  Phase 2: Core Implementation
    Started: 2025-09-15
    Files: 145
  ...

✅ Report saved to: my_project_history.md
```

## Implementation Notes

- Uses file system stat() calls for dates (mtime and ctime)
- Groups activity by week (Monday start)
- Phases determined by earliest file of each category
- Future enhancement: Parse git history for more accurate timeline

## Related Utilities

- `date_histogram.py` - Shows day-by-day file activity as histogram
- `project_stats.py` - Provides code statistics and metrics
