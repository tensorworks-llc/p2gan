#!/usr/bin/env python3
"""
Basic usage example for p2gan package.

This example shows how to create a simple project programmatically
and generate a GanttProject file.
"""

from datetime import datetime
from p2gan import (
    Project, Task, Resource, Milestone,
    ResourceAllocation, GanttGenerator,
    TaskPriority
)


def create_simple_project():
    """Create a simple software development project."""

    # Create the project
    project = Project(
        name="Website Redesign",
        start_date=datetime(2025, 2, 1),
        company="Acme Corp",
        description="Complete redesign of company website"
    )

    # Add resources (team members)
    alice = Resource(id=0, name="Alice Johnson", role="Frontend Developer", email="alice@acme.com")
    bob = Resource(id=1, name="Bob Smith", role="Backend Developer", email="bob@acme.com")
    carol = Resource(id=2, name="Carol White", role="Designer", email="carol@acme.com")
    dave = Resource(id=3, name="Dave Brown", role="Project Manager", email="dave@acme.com")

    project.add_resource(alice)
    project.add_resource(bob)
    project.add_resource(carol)
    project.add_resource(dave)

    # Phase 1: Planning
    task_id = 0

    planning = Task(
        id=task_id,
        name="Planning Phase",
        start_date=datetime(2025, 2, 1),
        duration=10,
        priority=TaskPriority.HIGH
    )
    planning.add_allocation(dave, load=50.0)
    project.add_task(planning)
    task_id += 1

    requirements = Task(
        id=task_id,
        name="Requirements Gathering",
        start_date=datetime(2025, 2, 1),
        duration=5,
        progress=0,
        priority=TaskPriority.HIGH
    )
    requirements.add_allocation(dave, load=100.0)
    planning.add_subtask(requirements)
    project.add_task(requirements)
    task_id += 1

    design_specs = Task(
        id=task_id,
        name="Design Specifications",
        start_date=datetime(2025, 2, 8),
        duration=5,
        progress=0,
        priority=TaskPriority.HIGH
    )
    design_specs.add_allocation(carol, load=100.0)
    design_specs.add_allocation(dave, load=25.0)
    planning.add_subtask(design_specs)
    project.add_task(design_specs)
    task_id += 1

    # Milestone: Planning Complete
    planning_complete = Milestone(
        id=task_id,
        name="Planning Complete",
        date=datetime(2025, 2, 14)
    )
    project.add_task(planning_complete)
    task_id += 1

    # Phase 2: Development
    development = Task(
        id=task_id,
        name="Development Phase",
        start_date=datetime(2025, 2, 17),
        duration=20,
        priority=TaskPriority.NORMAL
    )
    project.add_task(development)
    task_id += 1

    frontend = Task(
        id=task_id,
        name="Frontend Development",
        start_date=datetime(2025, 2, 17),
        duration=15,
        progress=0,
        priority=TaskPriority.NORMAL
    )
    frontend.add_allocation(alice, load=100.0)
    development.add_subtask(frontend)
    project.add_task(frontend)
    task_id += 1

    backend = Task(
        id=task_id,
        name="Backend Development",
        start_date=datetime(2025, 2, 17),
        duration=15,
        progress=0,
        priority=TaskPriority.NORMAL
    )
    backend.add_allocation(bob, load=100.0)
    development.add_subtask(backend)
    project.add_task(backend)
    task_id += 1

    integration = Task(
        id=task_id,
        name="Integration Testing",
        start_date=datetime(2025, 3, 10),
        duration=5,
        progress=0,
        priority=TaskPriority.HIGH
    )
    integration.add_allocation(alice, load=50.0)
    integration.add_allocation(bob, load=50.0)
    development.add_subtask(integration)
    project.add_task(integration)
    task_id += 1

    # Milestone: Development Complete
    dev_complete = Milestone(
        id=task_id,
        name="Development Complete",
        date=datetime(2025, 3, 17)
    )
    project.add_task(dev_complete)
    task_id += 1

    # Phase 3: Deployment
    deployment = Task(
        id=task_id,
        name="Deployment",
        start_date=datetime(2025, 3, 17),
        duration=3,
        progress=0,
        priority=TaskPriority.HIGH
    )
    deployment.add_allocation(bob, load=100.0)
    deployment.add_allocation(dave, load=50.0)
    project.add_task(deployment)
    task_id += 1

    # Milestone: Project Complete
    project_complete = Milestone(
        id=task_id,
        name="Project Launch",
        date=datetime(2025, 3, 20)
    )
    project.add_task(project_complete)

    return project


def main():
    """Generate the GanttProject file."""
    print("Creating Website Redesign project...")
    project = create_simple_project()

    print(f"Project: {project.name}")
    print(f"Start Date: {project.start_date.strftime('%Y-%m-%d')}")
    print(f"Resources: {len(project.resources)}")
    print(f"Tasks: {len(project.tasks)}")

    # Generate the .gan file
    generator = GanttGenerator(project)
    output_file = "website_redesign.gan"
    generator.save(output_file)

    print(f"\nGanttProject file generated: {output_file}")
    print("Open this file in GanttProject to view the project timeline!")


if __name__ == "__main__":
    main()