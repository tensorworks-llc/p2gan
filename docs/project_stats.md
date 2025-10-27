# project_stats.py

**Purpose:** Generates comprehensive code statistics and metrics for software projects.

## Overview

This utility analyzes a project directory to provide detailed statistics about:
- Lines of code (LOC) with non-overlapping categories
- Code vs comments vs blanks breakdown
- File counts by type and directory
- Technical debt markers (TODO, FIXME, HACK)
- Top files by size and line count

Special handling for documentation files to separate actual source code from markdown documentation.

## Features

- **Non-Overlapping Line Categories**:
  - Source Code (actual executable code)
  - Source Comments (in-code comments)
  - Source Blanks (blank lines in source files)
  - Documentation (.md files, excluding notes)
  - Notes/Transcripts (docs/notes/*.md specifically)
- **Multi-Language Support**: Comment detection for Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, Shell, Ruby
- **Directory Breakdown**: Stats per top-level directory
- **File Type Analysis**: Stats per file extension
- **Technical Debt Tracking**: Count TODO, FIXME, HACK markers
- **Top Files**: Identify largest files and files with most lines
- **Multiple Export Formats**: Console, Markdown, JSON

## Usage

```bash
# Basic analysis (console output)
python project_stats.py /path/to/project

# Show file type breakdown
python project_stats.py /path/to/project --by-type

# Export as JSON
python project_stats.py /path/to/project --json stats.json

# Export as Markdown report
python project_stats.py /path/to/project --markdown report.md

# Both JSON and Markdown
python project_stats.py /path/to/project --json stats.json --markdown report.md

# Include all files (don't skip common directories)
python project_stats.py /path/to/project --all

# Show top 20 files instead of default 10
python project_stats.py /path/to/project --top 20
```

## Command-Line Options

- `project_path` (required): Path to project directory to analyze
- `--json FILE`: Export statistics as JSON
- `--markdown FILE`: Export statistics as markdown report
- `--by-type`: Show detailed breakdown by file type
- `--all`: Include all files (don't skip common ignore patterns)
- `--top N`: Number of top files to show (default: 10)

## Output Format

### Console Output

```
======================================================================
PROJECT SUMMARY
======================================================================
Total Files:         381
Total Size:          17.1 MB
Total Lines:         123,585

Line Breakdown (non-overlapping):
  Source Code:             34,177 (27.7%)
  Source Comments:         4,478 (3.6%)
  Source Blanks:           10,184 (8.2%)
  Documentation (.md):      61,875 (50.1%)
  Notes/Transcripts:        12,871 (10.4%)
  ─────────────────────────
  Sum of categories:       123,585

Technical Debt Markers:
  TODO:              86
  FIXME:             0
  HACK:              0
```

### By Top-Level Directory

```
Directory               Files      Lines       Code   Comments
----------------------------------------------------------------------
src                        36      6,125      4,185        745
tests                      63     17,356     11,494      2,050
docs                      163     26,369     20,292          0
examples                   31      9,996      6,950      1,029
```

### By File Type

```
Type                    Files      Lines       Code   Comments
----------------------------------------------------------------------
Documentation (.md)        68     61,875          ─          ─
Notes/Trans               128     12,871          ─          ─
.py                       144     37,376     25,073      4,460
.js                        23      5,432      4,120        456
```

## Line Category Definitions

**Non-Overlapping Categories** (sum equals total):

1. **Source Code**: Actual executable code from .py, .js, .ts, .java, .c, .cpp, .go, .rs, etc.
   - Excludes comments and blank lines
   - Excludes .md files entirely

2. **Source Comments**: Comment lines in source files
   - Single-line comments (#, //)
   - Multi-line comments (/* */, """, ''')
   - Language-specific detection

3. **Source Blanks**: Blank lines in source files
   - Empty lines
   - Lines with only whitespace

4. **Documentation (.md)**: All markdown files EXCEPT docs/notes/*.md
   - README files
   - Documentation in docs/
   - Other .md files

5. **Notes/Transcripts**: Files in docs/notes/*.md specifically
   - Chat transcripts
   - Development notes
   - Session logs

**Guarantee**: Sum of all categories = Total Lines

## Comment Detection

Language-specific patterns:
- **Python**: `#` and `"""` / `'''`
- **JavaScript/TypeScript**: `//` and `/* */`
- **Java/C/C++/Go/Rust**: `//` and `/* */`
- **Shell/Ruby**: `#`

## JSON Export Structure

```json
{
  "project_path": "/path/to/project",
  "summary": {
    "total_files": 381,
    "total_size": 17896329,
    "total_lines": 123585,
    "source_code_lines": 34177,
    "source_comment_lines": 4478,
    "source_blank_lines": 10184,
    "documentation_lines": 61875,
    "notes_transcripts_lines": 12871,
    "todo_count": 86,
    "fixme_count": 0,
    "hack_count": 0
  },
  "documentation": {
    "files": 68,
    "lines": 61875,
    "size": 7678163
  },
  "notes_transcripts": {
    "files": 128,
    "lines": 12871,
    "size": 610545
  },
  "by_subdir": { ... },
  "by_type": { ... }
}
```

## Use Cases

1. **Project Metrics**: Quantify codebase size and complexity
2. **Documentation Ratio**: Track actual code vs documentation
3. **Technical Debt**: Identify areas needing cleanup (TODO/FIXME counts)
4. **Refactoring Targets**: Find largest/most complex files
5. **Language Distribution**: See breakdown by programming language
6. **Code Quality Reports**: Export data for presentations or reports

## Directory Exclusions (Default)

Automatically skips:
- `.git`, `.svn` - Version control
- `__pycache__`, `.mypy_cache` - Python caches
- `node_modules` - Node.js dependencies
- `.pytest_cache`, `.tox` - Testing tools
- `venv`, `.venv` - Virtual environments
- `dist`, `build`, `.egg-info`, `.eggs` - Build artifacts
- `.coverage`, `htmlcov` - Coverage reports

## Special Features

### Documentation vs Notes Separation

Recognizes that `docs/notes/*.md` files are often:
- Chat transcripts from AI coding sessions
- Development logs
- Session histories

These are tracked separately from actual project documentation to give accurate metrics.

### Sum Verification

Console output shows "Sum of categories" to verify non-overlapping totals:
```
  ─────────────────────────
  Sum of categories:       123,585
```

If sum ≠ total, shows "Other (non-text files)" line.

## Integration

- Can feed data into GanttProject file generation for project metrics
- JSON export can be processed by other analysis tools
- Complements `analyze_project_history.py` for comprehensive project analysis

## Example Workflow

```bash
# Quick stats check
python project_stats.py ~/my_project

# Detailed analysis with exports
python project_stats.py ~/my_project \
  --by-type \
  --json stats.json \
  --markdown report.md \
  --top 20

# View markdown report
cat report.md
```

## Related Utilities

- `analyze_project_history.py` - Timeline and phase detection
- `date_histogram.py` - Day-by-day activity visualization
