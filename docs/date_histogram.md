# date_histogram.py

**Purpose:** Generates ASCII histograms showing file creation and modification activity by day.

## Overview

This utility analyzes a project directory and creates visual histograms showing:
- Number of files created per day
- Number of files modified per day
- Development activity patterns over time

Perfect for visualizing project development rhythm and identifying high-activity periods.

## Features

- **Day-by-Day Analysis**: Groups files by creation/modification date (by day, not time)
- **ASCII Histogram Visualization**: Terminal-friendly bar charts
- **Dual Tracking**: Separate histograms for created vs modified files
- **CSV Export**: Export data for further analysis in spreadsheets
- **Flexible Display**: Show created, modified, or both
- **Automatic Scaling**: Histogram bars scale to fit terminal width
- **Directory Filtering**: Skips common ignore patterns by default

## Usage

```bash
# Show both creation and modification histograms (default)
python date_histogram.py /path/to/project

# Show only creation dates
python date_histogram.py /path/to/project --created

# Show only modification dates
python date_histogram.py /path/to/project --modified

# Explicitly show both
python date_histogram.py /path/to/project --both

# Export to CSV
python date_histogram.py /path/to/project --csv activity.csv

# Custom bar width (default: 50)
python date_histogram.py /path/to/project --width 80

# Include all files (don't skip common directories)
python date_histogram.py /path/to/project --all
```

## Command-Line Options

- `project_path` (required): Path to project directory to analyze
- `--created`: Show only file creation dates
- `--modified`: Show only file modification dates
- `--both`: Show both creation and modification dates
- `--csv FILE`: Export data to CSV file
- `--width N`: Maximum bar width in characters (default: 50)
- `--all`: Include all files (don't skip common ignore patterns)

## Output Format

### Console Output

```
📊 Analyzing file dates in: /home/user/my_project
======================================================================
✓ Analyzed 381 files
✓ Date range: 2025-09-15 to 2025-10-07


📅 Files Created by Date
======================================================================
2025-09-15 |   37 | ████████████████████████
2025-09-16 |   22 | ██████████████
2025-09-17 |   52 | ██████████████████████████████████
2025-09-20 |   75 | ██████████████████████████████████████████████████
...

Total: 381 files
Peak: 75 files on 2025-09-20
```

### CSV Export Format

```csv
date,files_created,files_modified
2025-09-15,37,37
2025-09-16,22,25
2025-09-17,52,49
...
```

## Use Cases

1. **Development Rhythm Analysis**: Identify sprint patterns and work cycles
2. **Project Timeline Visualization**: See when major development bursts occurred
3. **Activity Verification**: Confirm development periods for historical documentation
4. **Data Export**: Generate data for presentation charts or reports
5. **Project Health**: Track ongoing activity patterns

## Directory Exclusions (Default)

Automatically skips:
- `.git` - Git repository data
- `__pycache__` - Python cache
- `node_modules` - Node.js dependencies
- `.pytest_cache` - Pytest cache
- `venv`, `.venv` - Virtual environments
- `.tox` - Tox testing environments
- `dist`, `build` - Build artifacts
- `.mypy_cache` - MyPy type checker cache
- `.coverage`, `htmlcov` - Coverage reports

Use `--all` flag to include these directories.

## Histogram Scaling

- Bars automatically scale to fit terminal width
- Longest bar = max bar width (default 50 chars)
- All other bars proportional to max
- Shows exact file count next to each bar

## Integration with Other Utilities

- Complements `analyze_project_history.py` (which groups by week)
- Provides day-level granularity vs week-level
- CSV export can feed into spreadsheet analysis or `project_stats.py` workflows

## Example Workflow

```bash
# Generate histogram to identify peak development days
python date_histogram.py ~/my_project --both

# Export for detailed analysis
python date_histogram.py ~/my_project --csv activity.csv

# Import CSV into spreadsheet for charting
libreoffice activity.csv
```

## Technical Details

- Uses Python's `os.walk()` for directory traversal
- Extracts `st_mtime` (modification) and `st_ctime` (creation) from file stats
- Groups by `date()` only, ignoring time of day
- Histogram bars use Unicode block character: `█`

## Related Utilities

- `analyze_project_history.py` - Weekly timeline with phase detection
- `project_stats.py` - Code statistics and metrics
