#!/usr/bin/env python3
"""
Project Statistics Utility

Generates comprehensive statistics about a project based on folder analysis:
- Total lines of code (LOC)
- LOC per top-level sub-package/sub-project
- Code vs comments vs blank lines
- File counts and sizes
- Additional metrics

Usage:
    python project_stats.py /path/to/project [--json output.json] [--markdown report.md]

Options:
    --json FILE       Export statistics as JSON
    --markdown FILE   Export statistics as markdown report
    --by-type         Show breakdown by file type
    --all             Include all files (default skips common ignore patterns)
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import argparse
import re


class ProjectStats:
    """Generate comprehensive project statistics"""

    # Comment patterns for different languages
    COMMENT_PATTERNS = {
        '.py': [
            (re.compile(r'^\s*#'), 'single'),           # Python single-line
            (re.compile(r'^\s*"""'), 'multi_start'),    # Python docstring
            (re.compile(r'^\s*\'\'\''), 'multi_start'), # Python docstring
        ],
        '.js': [
            (re.compile(r'^\s*//'), 'single'),          # JS single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # JS multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # JS multi-line end
        ],
        '.ts': [
            (re.compile(r'^\s*//'), 'single'),          # TS single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # TS multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # TS multi-line end
        ],
        '.java': [
            (re.compile(r'^\s*//'), 'single'),          # Java single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # Java multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # Java multi-line end
        ],
        '.c': [
            (re.compile(r'^\s*//'), 'single'),          # C single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # C multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # C multi-line end
        ],
        '.cpp': [
            (re.compile(r'^\s*//'), 'single'),          # C++ single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # C++ multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # C++ multi-line end
        ],
        '.go': [
            (re.compile(r'^\s*//'), 'single'),          # Go single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # Go multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # Go multi-line end
        ],
        '.rs': [
            (re.compile(r'^\s*//'), 'single'),          # Rust single-line
            (re.compile(r'^\s*/\*'), 'multi_start'),    # Rust multi-line start
            (re.compile(r'\*/'), 'multi_end'),          # Rust multi-line end
        ],
        '.sh': [
            (re.compile(r'^\s*#'), 'single'),           # Shell single-line
        ],
        '.rb': [
            (re.compile(r'^\s*#'), 'single'),           # Ruby single-line
        ],
    }

    def __init__(self, project_path: str, skip_common_dirs: bool = True):
        self.project_path = Path(project_path).resolve()
        self.skip_common_dirs = skip_common_dirs

        # Overall stats
        self.total_files = 0
        self.total_lines = 0
        self.total_size = 0

        # Source code stats (non-.md files only)
        self.source_code_lines = 0
        self.source_comment_lines = 0
        self.source_blank_lines = 0

        # Documentation categories (mutually exclusive from source code)
        self.documentation_lines = 0  # .md files (excluding notes)
        self.notes_transcripts_lines = 0  # docs/notes/*.md

        # Detailed stats for documentation
        self.documentation_stats = {
            'files': 0,
            'lines': 0,
            'size': 0
        }
        self.notes_transcripts_stats = {
            'files': 0,
            'lines': 0,
            'size': 0
        }

        # By top-level directory
        self.stats_by_subdir = defaultdict(lambda: {
            'files': 0,
            'lines': 0,
            'code': 0,
            'comments': 0,
            'blanks': 0,
            'size': 0
        })

        # By file type (excluding .md which is handled separately)
        self.stats_by_type = defaultdict(lambda: {
            'files': 0,
            'lines': 0,
            'code': 0,
            'comments': 0,
            'blanks': 0,
            'size': 0
        })

        # Special markers
        self.todo_count = 0
        self.fixme_count = 0
        self.hack_count = 0

        # File tracking
        self.largest_files = []  # (size, path) tuples
        self.most_lines = []     # (lines, path) tuples

    def analyze(self):
        """Walk directory and collect statistics"""
        print(f"📊 Analyzing project: {self.project_path}")
        print("="*70)

        for root, dirs, files in os.walk(self.project_path):
            # Skip common ignore patterns
            if self.skip_common_dirs:
                dirs[:] = [d for d in dirs if d not in {
                    '.git', '__pycache__', 'node_modules', '.pytest_cache',
                    'venv', '.venv', '.tox', 'dist', 'build', '.egg-info',
                    '.mypy_cache', '.coverage', 'htmlcov', '.eggs'
                }]

            root_path = Path(root)

            for file in files:
                file_path = root_path / file
                try:
                    self._analyze_file(file_path)
                except Exception as e:
                    print(f"⚠ Error processing {file_path}: {e}")

        print(f"✓ Analyzed {self.total_files} files")
        print(f"✓ Total size: {self._format_size(self.total_size)}")
        print(f"✓ Total lines: {self.total_lines:,}\n")

    def _analyze_file(self, file_path: Path):
        """Analyze a single file"""
        stat = file_path.stat()
        size = stat.st_size

        # Get top-level subdirectory
        relative = file_path.relative_to(self.project_path)
        parts = relative.parts
        top_dir = parts[0] if len(parts) > 1 else '.'

        # Get file extension
        ext = file_path.suffix.lower()

        # Check if this is a notes/transcript file
        relative_str = str(relative)
        is_notes_transcript = relative_str.startswith('docs/notes/') and ext == '.md'

        # Update counts
        self.total_files += 1
        self.total_size += size
        self.stats_by_subdir[top_dir]['files'] += 1
        self.stats_by_subdir[top_dir]['size'] += size

        # Handle .md files specially
        if ext == '.md':
            if is_notes_transcript:
                self.notes_transcripts_stats['files'] += 1
                self.notes_transcripts_stats['size'] += size
            else:
                self.documentation_stats['files'] += 1
                self.documentation_stats['size'] += size
        else:
            # Regular file type tracking
            self.stats_by_type[ext]['files'] += 1
            self.stats_by_type[ext]['size'] += size

        # Track largest files
        self.largest_files.append((size, file_path))

        # Count lines for text files
        if self._is_text_file(file_path):
            lines, code, comments, blanks, todos, fixmes, hacks = self._count_lines(file_path, ext)

            self.total_lines += lines

            self.stats_by_subdir[top_dir]['lines'] += lines
            self.stats_by_subdir[top_dir]['code'] += code
            self.stats_by_subdir[top_dir]['comments'] += comments
            self.stats_by_subdir[top_dir]['blanks'] += blanks

            # Route .md files to documentation categories (NOT source code)
            if ext == '.md':
                if is_notes_transcript:
                    self.notes_transcripts_lines += lines
                    self.notes_transcripts_stats['lines'] += lines
                else:
                    self.documentation_lines += lines
                    self.documentation_stats['lines'] += lines
            else:
                # Source code files - add to source totals
                self.source_code_lines += code
                self.source_comment_lines += comments
                self.source_blank_lines += blanks

                self.stats_by_type[ext]['lines'] += lines
                self.stats_by_type[ext]['code'] += code
                self.stats_by_type[ext]['comments'] += comments
                self.stats_by_type[ext]['blanks'] += blanks

            self.todo_count += todos
            self.fixme_count += fixmes
            self.hack_count += hacks

            self.most_lines.append((lines, file_path))

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php', '.pl', '.sh', '.bash', '.zsh',
            '.html', '.css', '.scss', '.sass', '.less',
            '.xml', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
            '.md', '.txt', '.rst', '.adoc',
            '.sql', '.r', '.m', '.swift', '.kt', '.scala',
        }
        return file_path.suffix.lower() in text_extensions

    def _count_lines(self, file_path: Path, ext: str) -> Tuple[int, int, int, int, int, int, int]:
        """Count lines, code, comments, blanks for a file"""
        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0
        todo_count = 0
        fixme_count = 0
        hack_count = 0

        in_multiline_comment = False

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    total_lines += 1
                    stripped = line.strip()

                    # Check for special markers (in any line)
                    if 'TODO' in line.upper():
                        todo_count += 1
                    if 'FIXME' in line.upper():
                        fixme_count += 1
                    if 'HACK' in line.upper():
                        hack_count += 1

                    # Blank line
                    if not stripped:
                        blank_lines += 1
                        continue

                    # Check for comments
                    is_comment = False

                    # Handle multi-line comments
                    if in_multiline_comment:
                        comment_lines += 1
                        if self._is_multiline_end(stripped, ext):
                            in_multiline_comment = False
                        continue

                    # Check for comment start
                    if ext in self.COMMENT_PATTERNS:
                        for pattern, comment_type in self.COMMENT_PATTERNS[ext]:
                            if pattern.search(line):
                                is_comment = True
                                if comment_type == 'multi_start':
                                    in_multiline_comment = True
                                    # Check if it also ends on same line
                                    if self._is_multiline_end(line, ext):
                                        in_multiline_comment = False
                                break

                    if is_comment:
                        comment_lines += 1
                    else:
                        code_lines += 1

        except Exception as e:
            # If we can't read it, just skip line counting
            pass

        return total_lines, code_lines, comment_lines, blank_lines, todo_count, fixme_count, hack_count

    def _is_multiline_end(self, line: str, ext: str) -> bool:
        """Check if line ends a multi-line comment"""
        if ext == '.py':
            return '"""' in line or "'''" in line
        elif ext in {'.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs'}:
            return '*/' in line
        return False

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def print_summary(self):
        """Print summary statistics"""
        print("\n" + "="*70)
        print("PROJECT SUMMARY")
        print("="*70)
        print(f"Total Files:         {self.total_files:,}")
        print(f"Total Size:          {self._format_size(self.total_size)}")
        print(f"Total Lines:         {self.total_lines:,}")

        print(f"\nLine Breakdown (non-overlapping):")
        print(f"  Source Code:             {self.source_code_lines:,} ({self._percent(self.source_code_lines, self.total_lines)})")
        print(f"  Source Comments:         {self.source_comment_lines:,} ({self._percent(self.source_comment_lines, self.total_lines)})")
        print(f"  Source Blanks:           {self.source_blank_lines:,} ({self._percent(self.source_blank_lines, self.total_lines)})")

        if self.documentation_lines > 0:
            print(f"  Documentation (.md):      {self.documentation_lines:,} ({self._percent(self.documentation_lines, self.total_lines)})")
        if self.notes_transcripts_lines > 0:
            print(f"  Notes/Transcripts:        {self.notes_transcripts_lines:,} ({self._percent(self.notes_transcripts_lines, self.total_lines)})")

        # Verify non-overlapping (show sum for debugging)
        calculated_total = (self.source_code_lines + self.source_comment_lines +
                           self.source_blank_lines + self.documentation_lines +
                           self.notes_transcripts_lines)
        print(f"  ─────────────────────────")
        print(f"  Sum of categories:       {calculated_total:,}")
        if calculated_total != self.total_lines:
            other_lines = self.total_lines - calculated_total
            print(f"  Other (non-text files):  {other_lines:,}")

        print(f"\nTechnical Debt Markers:")
        print(f"  TODO:              {self.todo_count}")
        print(f"  FIXME:             {self.fixme_count}")
        print(f"  HACK:              {self.hack_count}")

    def print_by_subdir(self):
        """Print statistics by top-level subdirectory"""
        if not self.stats_by_subdir:
            return

        print("\n" + "="*70)
        print("BY TOP-LEVEL DIRECTORY")
        print("="*70)

        # Sort by lines of code descending
        sorted_dirs = sorted(
            self.stats_by_subdir.items(),
            key=lambda x: x[1]['code'],
            reverse=True
        )

        print(f"{'Directory':<20} {'Files':>8} {'Lines':>10} {'Code':>10} {'Comments':>10}")
        print("-"*70)

        for dir_name, stats in sorted_dirs:
            print(f"{dir_name:<20} {stats['files']:>8} {stats['lines']:>10,} "
                  f"{stats['code']:>10,} {stats['comments']:>10,}")

    def print_by_type(self):
        """Print statistics by file type"""
        print("\n" + "="*70)
        print("BY FILE TYPE")
        print("="*70)

        print(f"{'Type':<20} {'Files':>8} {'Lines':>10} {'Code':>10} {'Comments':>10}")
        print("-"*70)

        # Show documentation categories first (no code/comment breakdown)
        if self.documentation_stats['files'] > 0:
            print(f"{'Documentation (.md)':<20} {self.documentation_stats['files']:>8} "
                  f"{self.documentation_stats['lines']:>10,} "
                  f"{'─':>10} {'─':>10}")

        if self.notes_transcripts_stats['files'] > 0:
            print(f"{'Notes/Trans':<20} {self.notes_transcripts_stats['files']:>8} "
                  f"{self.notes_transcripts_stats['lines']:>10,} "
                  f"{'─':>10} {'─':>10}")

        # Sort remaining file types by lines of code descending
        if self.stats_by_type:
            sorted_types = sorted(
                self.stats_by_type.items(),
                key=lambda x: x[1]['code'],
                reverse=True
            )

            for ext, stats in sorted_types[:20]:  # Top 20 types
                ext_display = ext if ext else '(no ext)'
                print(f"{ext_display:<20} {stats['files']:>8} {stats['lines']:>10,} "
                      f"{stats['code']:>10,} {stats['comments']:>10,}")

    def print_top_files(self, n: int = 10):
        """Print top N largest/longest files"""
        print("\n" + "="*70)
        print(f"TOP {n} LARGEST FILES")
        print("="*70)

        largest = sorted(self.largest_files, reverse=True)[:n]
        for size, path in largest:
            rel_path = path.relative_to(self.project_path)
            print(f"{self._format_size(size):>10} - {rel_path}")

        print("\n" + "="*70)
        print(f"TOP {n} FILES BY LINE COUNT")
        print("="*70)

        most_lines = sorted(self.most_lines, reverse=True)[:n]
        for lines, path in most_lines:
            rel_path = path.relative_to(self.project_path)
            print(f"{lines:>8,} lines - {rel_path}")

    def _percent(self, part: int, total: int) -> str:
        """Calculate percentage string"""
        if total == 0:
            return "0.0%"
        return f"{(part / total * 100):.1f}%"

    def export_json(self, output_file: str):
        """Export statistics as JSON"""
        import json

        data = {
            'project_path': str(self.project_path),
            'summary': {
                'total_files': self.total_files,
                'total_size': self.total_size,
                'total_lines': self.total_lines,
                'source_code_lines': self.source_code_lines,
                'source_comment_lines': self.source_comment_lines,
                'source_blank_lines': self.source_blank_lines,
                'documentation_lines': self.documentation_lines,
                'notes_transcripts_lines': self.notes_transcripts_lines,
                'todo_count': self.todo_count,
                'fixme_count': self.fixme_count,
                'hack_count': self.hack_count,
            },
            'documentation': self.documentation_stats,
            'notes_transcripts': self.notes_transcripts_stats,
            'by_subdir': dict(self.stats_by_subdir),
            'by_type': dict(self.stats_by_type),
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✅ JSON exported to: {output_file}")

    def export_markdown(self, output_file: str):
        """Export statistics as markdown report"""
        report = f"""# Project Statistics

**Project:** `{self.project_path}`
**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Files | {self.total_files:,} |
| Total Size | {self._format_size(self.total_size)} |
| Total Lines | {self.total_lines:,} |

## Line Breakdown (Non-Overlapping)

| Category | Lines | Percentage |
|----------|-------|------------|
| Source Code | {self.source_code_lines:,} | {self._percent(self.source_code_lines, self.total_lines)} |
| Source Comments | {self.source_comment_lines:,} | {self._percent(self.source_comment_lines, self.total_lines)} |
| Source Blanks | {self.source_blank_lines:,} | {self._percent(self.source_blank_lines, self.total_lines)} |
| Documentation (.md) | {self.documentation_lines:,} | {self._percent(self.documentation_lines, self.total_lines)} |
| Notes/Transcripts (docs/notes/*.md) | {self.notes_transcripts_lines:,} | {self._percent(self.notes_transcripts_lines, self.total_lines)} |

## Technical Debt Markers

| Marker | Count |
|--------|-------|
| TODO | {self.todo_count} |
| FIXME | {self.fixme_count} |
| HACK | {self.hack_count} |

## By Top-Level Directory

| Directory | Files | Lines | Code | Comments |
|-----------|-------|-------|------|----------|
"""
        # Add subdirectory stats
        sorted_dirs = sorted(
            self.stats_by_subdir.items(),
            key=lambda x: x[1]['code'],
            reverse=True
        )

        for dir_name, stats in sorted_dirs:
            report += f"| {dir_name} | {stats['files']:,} | {stats['lines']:,} | {stats['code']:,} | {stats['comments']:,} |\n"

        report += "\n## By File Type\n\n"
        report += "| Type | Files | Lines | Code | Comments |\n"
        report += "|------|-------|-------|------|----------|\n"

        # Add documentation categories first (no code/comment breakdown)
        if self.documentation_stats['files'] > 0:
            report += (f"| Documentation (.md) | {self.documentation_stats['files']:,} | "
                      f"{self.documentation_stats['lines']:,} | ─ | ─ |\n")

        if self.notes_transcripts_stats['files'] > 0:
            report += (f"| Notes/Trans | {self.notes_transcripts_stats['files']:,} | "
                      f"{self.notes_transcripts_stats['lines']:,} | ─ | ─ |\n")

        # Add other file types
        if self.stats_by_type:
            sorted_types = sorted(
                self.stats_by_type.items(),
                key=lambda x: x[1]['code'],
                reverse=True
            )

            for ext, stats in sorted_types[:20]:
                ext_display = ext if ext else '(no ext)'
                report += f"| {ext_display} | {stats['files']:,} | {stats['lines']:,} | {stats['code']:,} | {stats['comments']:,} |\n"

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"✅ Markdown report exported to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive project statistics"
    )
    parser.add_argument("project_path", help="Path to project directory")
    parser.add_argument("--json", help="Export statistics as JSON")
    parser.add_argument("--markdown", help="Export statistics as markdown report")
    parser.add_argument("--by-type", action="store_true", help="Show breakdown by file type")
    parser.add_argument("--all", action="store_true", help="Include all files (don't skip common dirs)")
    parser.add_argument("--top", type=int, default=10, help="Number of top files to show (default: 10)")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"❌ Error: Project path does not exist: {args.project_path}")
        return 1

    # Analyze project
    stats = ProjectStats(args.project_path, skip_common_dirs=not args.all)
    stats.analyze()

    # Print reports
    stats.print_summary()
    stats.print_by_subdir()

    if args.by_type:
        stats.print_by_type()

    stats.print_top_files(args.top)

    # Export if requested
    if args.json:
        stats.export_json(args.json)

    if args.markdown:
        stats.export_markdown(args.markdown)

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
