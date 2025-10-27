"""
Command-line interface for GanttProject Python
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .generator import GanttProjectBuilder
from .stakeholders import get_default_manager
from .parser import MarkdownParser, ProjectAnalyzer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate GanttProject files from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert markdown to GanttProject
  ganttproject-python convert project.md project.gan

  # Analyze Python package
  ganttproject-python analyze /path/to/package --output package.gan

  # Auto-detect project type
  ganttproject-python auto /path/to/project project.gan

  # Manage stakeholders
  ganttproject-python stakeholders add "John Doe" "Developer" --email john@example.com
  ganttproject-python stakeholders list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert markdown to GanttProject')
    convert_parser.add_argument('input', help='Input markdown file')
    convert_parser.add_argument('output', help='Output .gan file')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze project and generate GanttProject')
    analyze_parser.add_argument('path', help='Path to project')
    analyze_parser.add_argument('--output', '-o', required=True, help='Output .gan file')
    analyze_parser.add_argument('--type', choices=['python', 'javascript', 'rust', 'generic'], 
                               help='Project type (auto-detected if not specified)')
    analyze_parser.add_argument('--start-date', help='Project start date (YYYY-MM-DD)')
    analyze_parser.add_argument('--team-size', type=int, default=3, help='Team size for resource allocation')
    
    # Auto command
    auto_parser = subparsers.add_parser('auto', help='Auto-detect project type and generate GanttProject')
    auto_parser.add_argument('path', help='Path to project')
    auto_parser.add_argument('output', help='Output .gan file')
    auto_parser.add_argument('--start-date', help='Project start date (YYYY-MM-DD)')
    
    # Stakeholders command
    stakeholders_parser = subparsers.add_parser('stakeholders', help='Manage stakeholders')
    stakeholder_subparsers = stakeholders_parser.add_subparsers(dest='stakeholder_command')
    
    # Add stakeholder
    add_stakeholder = stakeholder_subparsers.add_parser('add', help='Add a stakeholder')
    add_stakeholder.add_argument('name', help='Stakeholder name')
    add_stakeholder.add_argument('role', help='Stakeholder role')
    add_stakeholder.add_argument('--email', help='Email address')
    add_stakeholder.add_argument('--phone', help='Phone number')
    add_stakeholder.add_argument('--department', help='Department')
    add_stakeholder.add_argument('--skills', nargs='+', help='Skills (space-separated)')
    add_stakeholder.add_argument('--availability', type=float, default=1.0, help='Availability (0.0-1.0)')
    
    # List stakeholders
    stakeholder_subparsers.add_parser('list', help='List all stakeholders')
    
    # Export stakeholders
    export_stakeholder = stakeholder_subparsers.add_parser('export', help='Export stakeholders to CSV')
    export_stakeholder.add_argument('output', help='Output CSV file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'convert':
            cmd_convert(args)
        elif args.command == 'analyze':
            cmd_analyze(args)
        elif args.command == 'auto':
            cmd_auto(args)
        elif args.command == 'stakeholders':
            cmd_stakeholders(args)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_convert(args):
    """Handle convert command"""
    if not Path(args.input).exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")
    
    builder = GanttProjectBuilder()
    project = builder.from_markdown(args.input, args.output)
    
    print(f"✅ Successfully converted {args.input} to {args.output}")
    print(f"📊 Project: {project.name}")
    print(f"📋 Tasks: {len(project.get_all_tasks())}")
    print(f"👥 Resources: {len(project.resources)}")
    print(f"🎯 Milestones: {len(project.milestones)}")


def cmd_analyze(args):
    """Handle analyze command"""
    project_path = Path(args.path)
    if not project_path.exists():
        raise FileNotFoundError(f"Project path not found: {args.path}")
    
    # Parse start date if provided
    start_date = None
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")
    
    if args.type == 'python' or (not args.type and _is_python_project(project_path)):
        builder = GanttProjectBuilder()
        project = builder.from_python_package(str(project_path), args.output, start_date)
    else:
        analyzer = ProjectAnalyzer()
        project = analyzer.analyze_project(str(project_path), args.type or "auto")
        builder = GanttProjectBuilder()
        builder.generator.save_to_file(project, args.output)
    
    print(f"✅ Successfully analyzed {args.path} and created {args.output}")
    print(f"📊 Project: {project.name}")
    print(f"📋 Tasks: {len(project.get_all_tasks())}")
    print(f"👥 Resources: {len(project.resources)}")


def cmd_auto(args):
    """Handle auto command"""
    project_path = Path(args.path)
    if not project_path.exists():
        raise FileNotFoundError(f"Project path not found: {args.path}")
    
    builder = GanttProjectBuilder()
    project = builder.auto_analyze(args.path, args.output)
    
    print(f"✅ Successfully analyzed {args.path} and created {args.output}")
    print(f"📊 Project: {project.name}")
    print(f"📋 Tasks: {len(project.get_all_tasks())}")
    print(f"👥 Resources: {len(project.resources)}")


def cmd_stakeholders(args):
    """Handle stakeholders command"""
    manager = get_default_manager()
    
    if args.stakeholder_command == 'add':
        from .stakeholders import Stakeholder
        
        stakeholder = Stakeholder(
            name=args.name,
            role=args.role,
            email=args.email or "",
            phone=args.phone or "",
            department=args.department or "",
            skills=args.skills or [],
            availability=args.availability
        )
        
        manager.add_stakeholder(stakeholder)
        print(f"✅ Added stakeholder: {args.name} ({args.role})")
        
    elif args.stakeholder_command == 'list':
        stakeholders = manager.list_stakeholders()
        if not stakeholders:
            print("No stakeholders found.")
            return
        
        print(f"📋 Found {len(stakeholders)} stakeholders:")
        print()
        for s in stakeholders:
            print(f"👤 {s.name}")
            print(f"   Role: {s.role}")
            if s.email:
                print(f"   Email: {s.email}")
            if s.department:
                print(f"   Department: {s.department}")
            print(f"   Availability: {s.availability * 100:.0f}%")
            if s.projects:
                print(f"   Projects: {', '.join(s.projects)}")
            if s.skills:
                print(f"   Skills: {', '.join(s.skills)}")
            print()
            
    elif args.stakeholder_command == 'export':
        manager.export_to_csv(args.output)
        print(f"✅ Exported stakeholders to {args.output}")
    
    else:
        print("Available stakeholder commands: add, list, export")


def _is_python_project(project_path: Path) -> bool:
    """Check if path contains a Python project"""
    return (project_path / "__init__.py").exists() or (project_path / "setup.py").exists()


if __name__ == "__main__":
    main()