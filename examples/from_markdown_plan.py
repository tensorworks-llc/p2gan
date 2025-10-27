#!/usr/bin/env python3
"""
Example: Convert a Markdown Project Plan to Gantt Chart

This script demonstrates how to parse a markdown file
containing a project plan and generate a Gantt chart.
"""

from datetime import datetime, timedelta
from p2gan.models import Project, Task, Resource, Milestone
from p2gan.generator import GanttGenerator
from p2gan.parser import MarkdownParser

# Example markdown content (you would normally read this from a file)
SAMPLE_MARKDOWN = """
# Website Redesign Project

## Team
- Alice Johnson (Developer)
- Bob Smith (Designer)
- Carol White (Project Manager)

## Tasks

### Phase 1: Planning
- **Requirements Gathering** (5 days, Alice Johnson)
  - Priority: High
  - Progress: 100%

- **Design Mockups** (7 days, Bob Smith)
  - Dependencies: Requirements Gathering
  - Priority: High
  - Progress: 80%

### Phase 2: Development
- **Frontend Development** (15 days, Alice Johnson)
  - Dependencies: Design Mockups
  - Priority: Medium
  - Progress: 30%

- **Backend API** (12 days, Alice Johnson)
  - Dependencies: Requirements Gathering
  - Priority: High
  - Progress: 40%

- **Database Setup** (3 days, Alice Johnson)
  - Priority: High
  - Progress: 100%

### Phase 3: Testing
- **Unit Testing** (5 days, Alice Johnson)
  - Dependencies: Frontend Development, Backend API
  - Priority: Medium
  - Progress: 0%

- **User Acceptance Testing** (3 days, Carol White)
  - Dependencies: Unit Testing
  - Priority: High
  - Progress: 0%

## Milestones
- [x] Project Kickoff (2024-01-01)
- [x] Requirements Complete (2024-01-08)
- [ ] Design Approved (2024-01-17)
- [ ] Development Complete (2024-02-15)
- [ ] Go Live (2024-02-25)
"""

def create_project_from_markdown():
    """Parse markdown and create a Gantt chart."""

    # Option 1: Parse from string
    parser = MarkdownParser()
    project = parser.parse(SAMPLE_MARKDOWN)

    # Option 2: Parse from file (uncomment to use)
    # with open("project_plan.md", "r") as f:
    #     project = parser.parse(f.read())

    # Set project metadata if not in markdown
    if not project.name:
        project.name = "Website Redesign Project"
    if not project.company:
        project.company = "Example Corp"
    if not project.start_date:
        project.start_date = datetime(2024, 1, 1)

    # Generate the .gan file
    generator = GanttGenerator(project)
    output_file = "project_from_markdown.gan"
    generator.save(output_file)

    # Print summary
    print(f"✓ Generated {output_file}")
    print(f"\nProject Summary:")
    print(f"  Name: {project.name}")
    print(f"  Start Date: {project.start_date.strftime('%Y-%m-%d')}")
    print(f"  Resources: {len(project.resources)}")
    print(f"  Tasks: {len(project.tasks)}")
    print(f"  Milestones: {len(project.milestones)}")

    # Show task hierarchy
    print(f"\nTask Breakdown:")
    for task in project.tasks:
        indent = "  " * task.level
        status = "✓" if task.progress == 100 else f"{task.progress}%"
        print(f"{indent}- {task.name} ({task.duration} days) [{status}]")

    print(f"\nOpen {output_file} in GanttProject to view and edit.")

    return output_file

if __name__ == "__main__":
    create_project_from_markdown()