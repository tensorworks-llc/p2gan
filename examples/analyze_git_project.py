#!/usr/bin/env python3
"""
Example: Analyze a Git Project History to Generate a Gantt Chart

This script shows how to use p2gan to analyze a git repository
and create a Gantt chart based on commit history and file dates.
"""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from p2gan.models import Project, Task, Resource, Dependency
from p2gan.generator import GanttGenerator

def get_git_contributors():
    """Extract unique contributors from git history."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%an", "--all"],
            capture_output=True, text=True
        )
        contributors = list(set(result.stdout.strip().split("\n")))
        return contributors if contributors[0] else []
    except:
        return []

def get_first_commit_date():
    """Get the date of the first commit."""
    try:
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%ai", "--max-count=1"],
            capture_output=True, text=True
        )
        date_str = result.stdout.strip().split()[0]
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return datetime.now() - timedelta(days=30)

def analyze_repository(repo_path="."):
    """Analyze a git repository and generate a Gantt chart."""

    # Get project info
    project_name = Path(repo_path).name
    start_date = get_first_commit_date()
    contributors = get_git_contributors()

    # Initialize project
    project = Project(
        name=f"{project_name} Development Timeline",
        company="Auto-generated from Git",
        start_date=start_date
    )

    # Add contributors as resources
    for idx, contributor in enumerate(contributors[:5]):  # Limit to 5 for readability
        resource = Resource(
            id=f"res_{idx}",
            name=contributor,
            email=f"{contributor.lower().replace(' ', '.')}@example.com"
        )
        project.add_resource(resource)

    # Example: Add initial setup phase
    setup_task = Task(
        id="setup",
        name="Initial Setup",
        start_date=start_date,
        duration=5,
        progress=100,
        priority="High"
    )
    project.add_task(setup_task)

    # Example: Add development phase
    dev_task = Task(
        id="dev",
        name="Core Development",
        start_date=start_date + timedelta(days=5),
        duration=20,
        progress=75,
        priority="High"
    )
    project.add_task(dev_task)

    # Add dependency
    project.add_dependency(Dependency(
        source_id="setup",
        target_id="dev",
        type="FS"  # Finish-to-Start
    ))

    # Example: Add testing phase
    test_task = Task(
        id="test",
        name="Testing & QA",
        start_date=start_date + timedelta(days=20),
        duration=10,
        progress=50,
        priority="Medium"
    )
    project.add_task(test_task)

    # Example: Add documentation
    docs_task = Task(
        id="docs",
        name="Documentation",
        start_date=start_date + timedelta(days=15),
        duration=15,
        progress=30,
        priority="Low"
    )
    project.add_task(docs_task)

    # Generate the .gan file
    generator = GanttGenerator(project)
    output_file = f"{project_name}_timeline.gan"
    generator.save(output_file)

    print(f"✓ Generated {output_file}")
    print(f"  Project: {project_name}")
    print(f"  Start Date: {start_date.strftime('%Y-%m-%d')}")
    print(f"  Contributors: {len(contributors)}")
    print(f"  Tasks: {len(project.tasks)}")
    print(f"\nOpen {output_file} in GanttProject to view the timeline.")

    return output_file

if __name__ == "__main__":
    analyze_repository()