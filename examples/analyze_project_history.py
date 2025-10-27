#!/usr/bin/env python3
"""
Project History Analyzer

Analyzes a project directory to reconstruct its development timeline based on:
- File creation/modification dates
- Directory structure organization
- File types and naming patterns
- Git history (if available)
- Documentation files (README, CHANGELOG, etc.)

Generates a comprehensive analysis that can be used to:
1. Create historical Gantt charts
2. Understand project evolution
3. Identify development phases
4. Document completed work retroactively

Usage:
    python analyze_project_history.py /path/to/project [--output report.md]

The tool provides a detailed timeline and suggestions for structuring
the historical data in a GanttProject file.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import subprocess

class ProjectHistoryAnalyzer:
    """Analyzes project directory structure and file metadata to reconstruct history"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.files_by_date = []
        self.directories_by_date = []
        self.file_categories = defaultdict(list)
        self.git_available = False
        self.earliest_date = None
        self.latest_date = None

    def analyze(self) -> Dict:
        """Perform complete project analysis"""
        print(f"🔍 Analyzing project: {self.project_path}")
        print("="*70)

        # Check for git
        self.check_git()

        # Collect file metadata
        self.collect_file_metadata()

        # Analyze patterns
        self.analyze_file_patterns()

        # Generate timeline
        timeline = self.generate_timeline()

        # Suggest project phases
        phases = self.suggest_phases()

        return {
            "project_path": str(self.project_path),
            "git_available": self.git_available,
            "earliest_date": self.earliest_date,
            "latest_date": self.latest_date,
            "total_files": len(self.files_by_date),
            "file_categories": dict(self.file_categories),
            "timeline": timeline,
            "suggested_phases": phases
        }

    def check_git(self):
        """Check if project is a git repository"""
        git_dir = self.project_path / ".git"
        if git_dir.exists():
            self.git_available = True
            print("✓ Git repository detected")
        else:
            print("ℹ Not a git repository - using file system dates")

    def collect_file_metadata(self):
        """Collect all files with creation/modification dates"""
        print(f"\n📁 Collecting file metadata...")

        for root, dirs, files in os.walk(self.project_path):
            # Skip common ignore patterns
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'venv', '.venv'}]

            root_path = Path(root)

            for file in files:
                file_path = root_path / file
                try:
                    stat = file_path.stat()
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    ctime = datetime.fromtimestamp(stat.st_ctime)

                    # Use modification time as primary date
                    self.files_by_date.append({
                        'path': file_path,
                        'relative_path': file_path.relative_to(self.project_path),
                        'name': file,
                        'modified': mtime,
                        'created': ctime,
                        'size': stat.st_size,
                        'extension': file_path.suffix
                    })

                    # Track date range
                    if self.earliest_date is None or ctime < self.earliest_date:
                        self.earliest_date = ctime
                    if self.latest_date is None or mtime > self.latest_date:
                        self.latest_date = mtime

                except Exception as e:
                    print(f"⚠ Error processing {file_path}: {e}")

        # Sort by modification date
        self.files_by_date.sort(key=lambda x: x['modified'])

        print(f"  Found {len(self.files_by_date)} files")
        print(f"  Date range: {self.earliest_date.strftime('%Y-%m-%d')} to {self.latest_date.strftime('%Y-%m-%d')}")

    def analyze_file_patterns(self):
        """Categorize files by type and purpose"""
        print(f"\n🏷️  Categorizing files...")

        for file_info in self.files_by_date:
            path = str(file_info['relative_path'])
            name = file_info['name']
            ext = file_info['extension']

            # Categorize by type
            if ext in {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}:
                self.file_categories['source_code'].append(file_info)
            elif ext in {'.md', '.txt', '.rst', '.adoc'}:
                self.file_categories['documentation'].append(file_info)
            elif ext in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'}:
                self.file_categories['configuration'].append(file_info)
            elif ext in {'.html', '.css', '.scss', '.sass'}:
                self.file_categories['frontend'].append(file_info)
            elif 'test' in path.lower() or name.startswith('test_'):
                self.file_categories['tests'].append(file_info)
            elif 'doc' in path.lower() or name in {'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md'}:
                self.file_categories['documentation'].append(file_info)
            elif name in {'Makefile', 'pyproject.toml', 'package.json', 'Cargo.toml', 'pom.xml'}:
                self.file_categories['build_system'].append(file_info)
            elif 'example' in path.lower():
                self.file_categories['examples'].append(file_info)
            else:
                self.file_categories['other'].append(file_info)

        # Print summary
        for category, files in sorted(self.file_categories.items()):
            print(f"  {category}: {len(files)} files")

    def generate_timeline(self) -> List[Dict]:
        """Generate timeline of significant development milestones"""
        print(f"\n📅 Generating timeline...")

        timeline = []

        # Group files by week
        weeks = defaultdict(list)
        for file_info in self.files_by_date:
            week_start = file_info['modified'].replace(hour=0, minute=0, second=0, microsecond=0)
            # Get Monday of that week
            week_start = week_start - timedelta(days=week_start.weekday())
            weeks[week_start].append(file_info)

        # Create timeline entries for significant weeks
        for week_start in sorted(weeks.keys()):
            files = weeks[week_start]

            # Analyze what happened this week
            categories_changed = defaultdict(int)
            for file_info in files:
                for category, file_list in self.file_categories.items():
                    if file_info in file_list:
                        categories_changed[category] += 1
                        break

            timeline.append({
                'date': week_start,
                'files_changed': len(files),
                'categories': dict(categories_changed),
                'notable_files': [f['name'] for f in files[:5]]  # Top 5 files
            })

        return timeline

    def suggest_phases(self) -> List[Dict]:
        """Suggest development phases based on file patterns"""
        print(f"\n🎯 Suggesting project phases...")

        phases = []

        # Phase 1: Initial Setup (first build system / config files)
        setup_files = [f for f in self.file_categories['build_system'] + self.file_categories['configuration']]
        if setup_files:
            earliest_setup = min(setup_files, key=lambda x: x['created'])
            phases.append({
                'name': "Project Setup & Infrastructure",
                'start_date': earliest_setup['created'],
                'indicators': ['Build system', 'Configuration files'],
                'files': len(setup_files)
            })

        # Phase 2: Core Development (first source code files)
        source_files = self.file_categories['source_code']
        if source_files:
            earliest_source = min(source_files, key=lambda x: x['created'])
            phases.append({
                'name': "Core Implementation",
                'start_date': earliest_source['created'],
                'indicators': ['Source code files'],
                'files': len(source_files)
            })

        # Phase 3: Testing (first test files)
        test_files = self.file_categories['tests']
        if test_files:
            earliest_test = min(test_files, key=lambda x: x['created'])
            phases.append({
                'name': "Testing & Quality Assurance",
                'start_date': earliest_test['created'],
                'indicators': ['Test files'],
                'files': len(test_files)
            })

        # Phase 4: Documentation
        doc_files = self.file_categories['documentation']
        if doc_files:
            earliest_doc = min(doc_files, key=lambda x: x['created'])
            phases.append({
                'name': "Documentation",
                'start_date': earliest_doc['created'],
                'indicators': ['Documentation files'],
                'files': len(doc_files)
            })

        # Phase 5: Examples (if present)
        example_files = self.file_categories['examples']
        if example_files:
            earliest_example = min(example_files, key=lambda x: x['created'])
            phases.append({
                'name': "Examples & Demos",
                'start_date': earliest_example['created'],
                'indicators': ['Example files'],
                'files': len(example_files)
            })

        # Sort phases by date
        phases.sort(key=lambda x: x['start_date'])

        for i, phase in enumerate(phases, 1):
            print(f"  Phase {i}: {phase['name']}")
            print(f"    Started: {phase['start_date'].strftime('%Y-%m-%d')}")
            print(f"    Files: {phase['files']}")

        return phases

    def generate_report(self, output_file: Optional[str] = None, analysis: Optional[Dict] = None) -> str:
        """Generate markdown report of project history"""
        if analysis is None:
            analysis = self.analyze()

        report = f"""# Project History Analysis

**Project:** `{analysis['project_path']}`
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Git Available:** {'Yes' if analysis['git_available'] else 'No'}

## Timeline

**Project Start:** {analysis['earliest_date'].strftime('%Y-%m-%d')}
**Last Modified:** {analysis['latest_date'].strftime('%Y-%m-%d')}
**Duration:** {(analysis['latest_date'] - analysis['earliest_date']).days} days
**Total Files:** {analysis['total_files']}

## File Categories

"""

        for category, files in sorted(analysis['file_categories'].items()):
            report += f"- **{category.replace('_', ' ').title()}:** {len(files)} files\n"

        report += "\n## Suggested Development Phases\n\n"

        for i, phase in enumerate(analysis['suggested_phases'], 1):
            report += f"### Phase {i}: {phase['name']}\n\n"
            report += f"- **Start Date:** {phase['start_date'].strftime('%Y-%m-%d')}\n"
            report += f"- **Files:** {phase['files']}\n"
            report += f"- **Indicators:** {', '.join(phase['indicators'])}\n\n"

        report += "\n## Activity Timeline\n\n"
        report += "| Week Starting | Files Changed | Categories |\n"
        report += "|---------------|---------------|------------|\n"

        for entry in analysis['timeline'][:20]:  # First 20 weeks
            date_str = entry['date'].strftime('%Y-%m-%d')
            categories_str = ', '.join(f"{k}({v})" for k, v in entry['categories'].items())
            report += f"| {date_str} | {entry['files_changed']} | {categories_str} |\n"

        report += "\n## Recommendations for GanttProject\n\n"
        report += """Based on this analysis, consider creating the following task structure:

1. **Phase 0: Historical Development (COMPLETED)**
   - Mark all discovered phases as 100% complete
   - Assign actual start dates from analysis
   - Estimate task durations based on file creation patterns
   - Assign to primary developer(s)

2. **Task Organization**
   - Create parent tasks for each suggested phase
   - Add subtasks for major file categories (setup, core, tests, docs)
   - Include milestones at phase boundaries

3. **Timeline Accuracy**
   - Use earliest file dates for phase start dates
   - Estimate completion dates from last modifications in each phase
   - Account for overlapping development activities

4. **Resource Allocation**
   - Review git commit history (if available) for contributor data
   - Assign 100% allocation to primary developer for historical tasks
   - Mark all historical tasks as complete
"""

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\n✅ Report saved to: {output_file}")

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze project history from file metadata")
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--output", "-o", help="Output file for analysis report (markdown)")
    parser.add_argument("--json", help="Export raw analysis as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"❌ Error: Project path does not exist: {args.project_path}")
        return 1

    # Run analysis once
    analyzer = ProjectHistoryAnalyzer(args.project_path)
    analysis = analyzer.analyze()

    # Generate report
    output_file = args.output or f"{Path(args.project_path).name}_history.md"
    report = analyzer.generate_report(output_file, analysis=analysis)

    # Export JSON if requested
    if args.json:
        # Convert dates to strings for JSON
        def date_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()
            elif isinstance(o, Path):
                return str(o)
            return o.__dict__

        with open(args.json, 'w') as f:
            json.dump(analysis, f, indent=2, default=date_converter)
        print(f"✅ JSON export saved to: {args.json}")

    print("\n" + "="*70)
    print("Analysis complete! Review the report for historical timeline.")
    print("="*70)

    return 0


if __name__ == "__main__":
    from datetime import timedelta
    sys.exit(main())
