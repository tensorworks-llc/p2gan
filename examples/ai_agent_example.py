#!/usr/bin/env python3
"""
Example: AI Agent Project Analysis Template

This script shows how an AI agent (Claude Code, Copilot, etc.)
would programmatically analyze a project and generate a Gantt chart.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from p2gan.models import Project, Task, Resource, Dependency, Milestone
from p2gan.generator import GanttGenerator

def find_todo_comments(directory="."):
    """Find TODO and FIXME comments in source code."""
    todos = []
    for root, dirs, files in os.walk(directory):
        # Skip hidden and build directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]

        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.go')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if match := re.search(r'(TODO|FIXME|HACK|XXX|BUG):\s*(.+)', line):
                                todos.append({
                                    'type': match.group(1),
                                    'description': match.group(2).strip(),
                                    'file': filepath,
                                    'line': line_num
                                })
                except:
                    pass
    return todos

def analyze_file_structure(directory="."):
    """Analyze project structure to infer components."""
    structure = {
        'has_tests': False,
        'has_docs': False,
        'has_ci': False,
        'has_docker': False,
        'has_package_json': False,
        'has_requirements': False,
        'has_readme': False,
        'main_language': None,
        'file_count': 0,
        'total_lines': 0
    }

    file_extensions = {}

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            structure['file_count'] += 1

            # Check for specific files/patterns
            if file.lower() == 'readme.md':
                structure['has_readme'] = True
            elif file in ['package.json', 'package-lock.json']:
                structure['has_package_json'] = True
            elif file in ['requirements.txt', 'Pipfile', 'pyproject.toml']:
                structure['has_requirements'] = True
            elif file.startswith('Dockerfile'):
                structure['has_docker'] = True
            elif 'test' in file.lower() or 'spec' in file.lower():
                structure['has_tests'] = True

            # Count file extensions
            ext = Path(file).suffix
            if ext:
                file_extensions[ext] = file_extensions.get(ext, 0) + 1

        # Check directories
        dir_names = [d.lower() for d in dirs]
        if 'docs' in dir_names or 'documentation' in dir_names:
            structure['has_docs'] = True
        if '.github' in dirs or '.circleci' in dirs:
            structure['has_ci'] = True

    # Determine main language
    if file_extensions:
        main_ext = max(file_extensions, key=file_extensions.get)
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        structure['main_language'] = lang_map.get(main_ext, 'Unknown')

    return structure

def create_ai_generated_timeline(project_name="Analyzed Project"):
    """
    Create a comprehensive project timeline based on AI analysis.
    This is what an AI agent would generate after analyzing a codebase.
    """

    # Analyze the project
    print("🔍 Analyzing project structure...")
    structure = analyze_file_structure()
    todos = find_todo_comments()

    print(f"  Found {structure['file_count']} files")
    print(f"  Main language: {structure['main_language']}")
    print(f"  Found {len(todos)} TODO/FIXME comments")

    # Initialize project
    project = Project(
        name=project_name,
        company="AI-Analyzed Project",
        start_date=datetime.now() - timedelta(days=30)  # Assume project started 30 days ago
    )

    # Add team members (in real scenario, from git log)
    team = [
        Resource("dev1", "Lead Developer", "lead@example.com", "Developer"),
        Resource("dev2", "Backend Developer", "backend@example.com", "Developer"),
        Resource("qa1", "QA Engineer", "qa@example.com", "Tester"),
        Resource("pm1", "Project Manager", "pm@example.com", "Manager")
    ]
    for resource in team:
        project.add_resource(resource)

    # Phase 1: Completed Work (based on existing files)
    completed_tasks = []

    if structure['has_readme']:
        completed_tasks.append(Task(
            id="init_project",
            name="Project Initialization",
            start_date=project.start_date,
            duration=2,
            progress=100,
            priority="High",
            resource_ids=["pm1"]
        ))

    if structure['has_requirements'] or structure['has_package_json']:
        completed_tasks.append(Task(
            id="setup_deps",
            name="Setup Dependencies",
            start_date=project.start_date + timedelta(days=2),
            duration=1,
            progress=100,
            priority="High",
            resource_ids=["dev1"]
        ))

    # Phase 2: In Progress (based on recent activity - simulated)
    current_tasks = []

    if structure['has_tests']:
        current_tasks.append(Task(
            id="write_tests",
            name="Write Unit Tests",
            start_date=datetime.now() - timedelta(days=5),
            duration=10,
            progress=60,
            priority="Medium",
            resource_ids=["dev2", "qa1"]
        ))

    if structure['has_docs']:
        current_tasks.append(Task(
            id="documentation",
            name="Update Documentation",
            start_date=datetime.now() - timedelta(days=3),
            duration=5,
            progress=40,
            priority="Low",
            resource_ids=["dev1"]
        ))

    # Phase 3: Future Work (from TODOs)
    future_tasks = []

    # Group TODOs by type
    todo_groups = {}
    for todo in todos[:10]:  # Limit to 10 for readability
        todo_type = todo['type']
        if todo_type not in todo_groups:
            todo_groups[todo_type] = []
        todo_groups[todo_type].append(todo)

    task_start = datetime.now() + timedelta(days=7)
    for todo_type, items in todo_groups.items():
        task_name = f"Fix {todo_type} items ({len(items)} issues)"
        priority = "High" if todo_type in ["BUG", "FIXME"] else "Medium"

        future_tasks.append(Task(
            id=f"fix_{todo_type.lower()}",
            name=task_name,
            start_date=task_start,
            duration=len(items) * 2,  # 2 days per issue
            progress=0,
            priority=priority,
            resource_ids=["dev1", "dev2"],
            note=f"Issues found in: {', '.join(set(t['file'] for t in items[:3]))}"
        ))
        task_start += timedelta(days=len(items) * 2)

    # Phase 4: Deployment Tasks
    deployment_tasks = []

    if structure['has_docker']:
        deployment_tasks.append(Task(
            id="docker_deploy",
            name="Docker Deployment Setup",
            start_date=task_start,
            duration=3,
            progress=0,
            priority="High",
            resource_ids=["dev1"]
        ))
        task_start += timedelta(days=3)

    if structure['has_ci']:
        deployment_tasks.append(Task(
            id="ci_pipeline",
            name="CI/CD Pipeline Configuration",
            start_date=task_start,
            duration=5,
            progress=0,
            priority="Medium",
            resource_ids=["dev1"]
        ))

    # Add all tasks to project with hierarchy
    all_tasks = [
        ("Completed Work", completed_tasks),
        ("Current Sprint", current_tasks),
        ("Backlog (from TODOs)", future_tasks),
        ("Deployment", deployment_tasks)
    ]

    for phase_name, tasks in all_tasks:
        if tasks:
            # Add phase as parent task
            phase = Task(
                id=phase_name.lower().replace(' ', '_'),
                name=phase_name,
                start_date=tasks[0].start_date if tasks else datetime.now(),
                duration=sum(t.duration for t in tasks),
                progress=int(sum(t.progress for t in tasks) / len(tasks)) if tasks else 0,
                priority="High"
            )
            project.add_task(phase)

            # Add subtasks
            for task in tasks:
                task.parent_id = phase.id
                task.level = 1
                project.add_task(task)

    # Add dependencies
    if "setup_deps" in [t.id for t in project.tasks]:
        if "write_tests" in [t.id for t in project.tasks]:
            project.add_dependency(Dependency("setup_deps", "write_tests", "FS"))

    # Add milestones
    project.add_milestone(Milestone(
        id="m1",
        name="Sprint Review",
        date=datetime.now() + timedelta(days=14),
        note="Review current progress and plan next sprint"
    ))

    project.add_milestone(Milestone(
        id="m2",
        name="Production Release",
        date=datetime.now() + timedelta(days=30),
        note="Target release date"
    ))

    # Generate .gan file
    generator = GanttGenerator(project)
    output_file = f"{project_name.replace(' ', '_').lower()}_timeline.gan"
    generator.save(output_file)

    # Print comprehensive summary
    print(f"\n✅ Generated {output_file}")
    print(f"\n📊 Project Analysis Summary:")
    print(f"  • Project: {project_name}")
    print(f"  • Language: {structure['main_language'] or 'Multi-language'}")
    print(f"  • Total Files: {structure['file_count']}")
    print(f"  • Has Tests: {'✓' if structure['has_tests'] else '✗'}")
    print(f"  • Has Docs: {'✓' if structure['has_docs'] else '✗'}")
    print(f"  • Has CI/CD: {'✓' if structure['has_ci'] else '✗'}")
    print(f"  • Has Docker: {'✓' if structure['has_docker'] else '✗'}")

    print(f"\n📅 Timeline Summary:")
    print(f"  • Total Tasks: {len(project.tasks)}")
    print(f"  • Completed: {len(completed_tasks)}")
    print(f"  • In Progress: {len(current_tasks)}")
    print(f"  • Planned: {len(future_tasks) + len(deployment_tasks)}")
    print(f"  • TODO Items Found: {len(todos)}")

    print(f"\n👥 Team:")
    for resource in project.resources:
        print(f"  • {resource.name} ({resource.role})")

    print(f"\n🎯 Milestones:")
    for milestone in project.milestones:
        print(f"  • {milestone.name}: {milestone.date.strftime('%Y-%m-%d')}")

    print(f"\n📂 Open {output_file} in GanttProject to view and customize the timeline.")

    return output_file

if __name__ == "__main__":
    # This is what an AI agent would run after analyzing your project
    create_ai_generated_timeline("My Analyzed Project")