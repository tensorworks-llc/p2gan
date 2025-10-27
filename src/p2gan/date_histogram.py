#!/usr/bin/env python3
"""
Date Histogram Utility

Analyzes a project folder and generates a histogram showing file activity by day:
- Number of files created per day
- Number of files modified per day

Usage:
    python date_histogram.py /path/to/project [--created] [--modified] [--both] [--csv output.csv]

Options:
    --created       Show only creation dates (default if neither specified)
    --modified      Show only modification dates
    --both          Show both creation and modification dates
    --csv FILE      Export data to CSV file
    --all           Include all files (default skips common ignore patterns)
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import argparse


class DateHistogram:
    """Generate histograms of file creation/modification activity"""

    def __init__(self, project_path: str, skip_common_dirs: bool = True):
        self.project_path = Path(project_path).resolve()
        self.skip_common_dirs = skip_common_dirs
        self.created_by_date = defaultdict(int)
        self.modified_by_date = defaultdict(int)
        self.files_created = defaultdict(list)
        self.files_modified = defaultdict(list)

    def analyze(self):
        """Walk directory and collect file date information"""
        print(f"📊 Analyzing file dates in: {self.project_path}")
        print("="*70)

        total_files = 0

        for root, dirs, files in os.walk(self.project_path):
            # Skip common ignore patterns
            if self.skip_common_dirs:
                dirs[:] = [d for d in dirs if d not in {
                    '.git', '__pycache__', 'node_modules', '.pytest_cache',
                    'venv', '.venv', '.tox', 'dist', 'build', '.egg-info',
                    '.mypy_cache', '.coverage', 'htmlcov'
                }]

            root_path = Path(root)

            for file in files:
                file_path = root_path / file
                try:
                    stat = file_path.stat()
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    ctime = datetime.fromtimestamp(stat.st_ctime)

                    # Group by date (not time)
                    created_date = ctime.date()
                    modified_date = mtime.date()

                    self.created_by_date[created_date] += 1
                    self.modified_by_date[modified_date] += 1

                    # Track which files for detailed view
                    self.files_created[created_date].append(file_path.relative_to(self.project_path))
                    self.files_modified[modified_date].append(file_path.relative_to(self.project_path))

                    total_files += 1

                except Exception as e:
                    print(f"⚠ Error processing {file_path}: {e}")

        print(f"✓ Analyzed {total_files} files")
        print(f"✓ Date range: {min(self.created_by_date.keys())} to {max(self.modified_by_date.keys())}\n")

    def print_histogram(self, date_dict: Dict, title: str, max_bar_width: int = 50):
        """Print ASCII histogram"""
        if not date_dict:
            print(f"No data for {title}")
            return

        print(f"\n{title}")
        print("="*70)

        # Sort by date
        sorted_dates = sorted(date_dict.items())

        # Find max count for scaling
        max_count = max(count for _, count in sorted_dates)

        # Print histogram
        for date, count in sorted_dates:
            # Scale bar width
            bar_width = int((count / max_count) * max_bar_width) if max_count > 0 else 0
            bar = "█" * bar_width

            print(f"{date.strftime('%Y-%m-%d')} | {count:4d} | {bar}")

        print(f"\nTotal: {sum(date_dict.values())} files")
        print(f"Peak: {max_count} files on {max(sorted_dates, key=lambda x: x[1])[0]}")

    def export_csv(self, output_file: str, include_created: bool = True, include_modified: bool = True):
        """Export histogram data to CSV"""
        import csv

        # Collect all unique dates
        all_dates = set()
        if include_created:
            all_dates.update(self.created_by_date.keys())
        if include_modified:
            all_dates.update(self.modified_by_date.keys())

        with open(output_file, 'w', newline='') as f:
            fieldnames = ['date']
            if include_created:
                fieldnames.append('files_created')
            if include_modified:
                fieldnames.append('files_modified')

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for date in sorted(all_dates):
                row = {'date': date.strftime('%Y-%m-%d')}
                if include_created:
                    row['files_created'] = self.created_by_date.get(date, 0)
                if include_modified:
                    row['files_modified'] = self.modified_by_date.get(date, 0)
                writer.writerow(row)

        print(f"✅ CSV exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate histogram of file creation/modification dates"
    )
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--created", action="store_true", help="Show creation dates")
    parser.add_argument("--modified", action="store_true", help="Show modification dates")
    parser.add_argument("--both", action="store_true", help="Show both creation and modification")
    parser.add_argument("--csv", help="Export to CSV file")
    parser.add_argument("--all", action="store_true", help="Include all files (don't skip common dirs)")
    parser.add_argument("--width", type=int, default=50, help="Maximum bar width (default: 50)")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"❌ Error: Project path does not exist: {args.project_path}")
        return 1

    # Default to showing both if none specified
    show_created = args.created or args.both or (not args.created and not args.modified)
    show_modified = args.modified or args.both or (not args.created and not args.modified)

    # Analyze project
    histogram = DateHistogram(args.project_path, skip_common_dirs=not args.all)
    histogram.analyze()

    # Print histograms
    if show_created:
        histogram.print_histogram(histogram.created_by_date, "📅 Files Created by Date", args.width)

    if show_modified:
        histogram.print_histogram(histogram.modified_by_date, "📝 Files Modified by Date", args.width)

    # Export CSV if requested
    if args.csv:
        histogram.export_csv(args.csv, include_created=show_created, include_modified=show_modified)

    print("\n" + "="*70)
    print("Histogram generation complete!")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
