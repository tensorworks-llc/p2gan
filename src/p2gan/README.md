# p2gan - Python Library for GanttProject Files

**Purpose:** Core library for programmatically generating, manipulating, and analyzing GanttProject (.gan) XML files.

## Overview

This Python package provides a complete object-oriented API for working with GanttProject files. It allows you to create project plans, tasks, resources, dependencies, and all GanttProject features entirely from Python code, without needing the GanttProject GUI application.

## Features

### Core Models
- **Project**: Top-level project container with metadata
- **Task**: Project tasks with full attribute support
- **Resource**: People, equipment, or other project resources
- **Milestone**: Zero-duration tasks marking important events
- **Dependency**: Task dependencies with all 4 types (SS, FS, FF, SF)
- **ResourceAllocation**: Assign resources to tasks with allocation %
- **Vacation**: Resource unavailability periods
- **Role**: Custom role definitions
- **CustomTaskProperty**: User-defined task fields

### Task Attributes (Fully Supported)
- Name, duration, start date, end date
- Priority levels: LOW, HIGH, LOWEST, HIGHEST, NORMAL
- Progress (0-100%)
- Color customization
- Notes/description (CDATA-wrapped for special characters)
- Parent-child hierarchical relationships
- Cost (calculated or fixed)
- Milestones (zero-duration tasks)

### Dependency Types (All 4 Verified)
- **START_TO_START (SS)**: Task B starts when Task A starts
- **FINISH_TO_START (FS)**: Task B starts when Task A finishes (most common)
- **FINISH_TO_FINISH (FF)**: Task B finishes when Task A finishes
- **START_TO_FINISH (SF)**: Task B finishes when Task A starts (rare)

### Resource Management
- Define resources with roles, contacts, rates
- Allocate resources to tasks with load percentage (can exceed 100%)
- Mark resources as "responsible" for tasks
- Define vacation/unavailability periods
- Custom role definitions with role IDs

### Advanced Features
- Hierarchical tasks (parent-child relationships, unlimited depth)
- Custom task properties (5 types: text, int, boolean, date, double)
- Calculated columns (future enhancement)
- Task constraints (ASAP, MFO, etc.)
- Calendar definitions (work week, holidays)

## Installation

```bash
# From source (development mode)
cd /path/to/p2gan
pip install -e .
```

## Quick Start

```python
from datetime import datetime, timedelta
from ganttproject import (
    Project, Task, Resource, Milestone, Dependency,
    ResourceAllocation, TaskPriority, DependencyType,
    GanttGenerator
)

# Create project
project = Project(
    name="My Project",
    company="Acme Corp",
    view_date=datetime(2025, 10, 1),
    view_index=0
)

# Add resources
alex = Resource(id=0, name="Alex Developer", function="1", contacts="alex@example.com")
project.resources.append(alex)

# Create tasks
task1 = Task(
    id=1,
    name="Phase 1: Planning",
    duration=5,
    start_date=datetime(2025, 10, 1),
    priority=TaskPriority.HIGH,
    progress=100,
    notes="Initial planning phase"
)

task2 = Task(
    id=2,
    name="Implementation",
    duration=10,
    start_date=datetime(2025, 10, 8),
    priority=TaskPriority.HIGH,
    progress=50
)

# Add subtask
task3 = Task(
    id=3,
    name="Build Core Module",
    duration=5,
    start_date=datetime(2025, 10, 8)
)
task2.add_subtask(task3)

# Add tasks to project
project.add_task(task1)
project.add_task(task2)

# Create dependency: task2 starts when task1 finishes
task2.dependencies.append(
    Dependency(successor_id=1, type=DependencyType.FINISH_TO_START)
)

# Create milestone
milestone = Milestone(
    id=4,
    name="✓ Phase 1 Complete",
    date=datetime(2025, 10, 7),
    progress=100
)
project.add_task(milestone)

# Allocate resource to task
project.allocations.append(
    ResourceAllocation(
        task_id=2,
        resource_id=0,
        function="1",  # Programmer role
        load=100.0,
        responsible=True
    )
)

# Generate .gan file
generator = GanttGenerator(project)
generator.write("my_project.gan")
```

## API Reference

### Project

```python
project = Project(
    name="Project Name",
    company="Company Name",
    description="Project description",
    view_date=datetime(2025, 10, 1),
    view_index=0  # 0 = Gantt chart view
)

project.add_task(task)
project.add_custom_property(property_def)
```

### Task

```python
task = Task(
    id=1,
    name="Task Name",
    duration=5,  # working days
    start_date=datetime(2025, 10, 1),
    end_date=datetime(2025, 10, 7),  # optional
    priority=TaskPriority.HIGH,
    progress=50,  # 0-100
    color="#8cb6ce",
    notes="Task description with <special> characters",
    cost=1000.0  # fixed cost
)

# Hierarchical tasks
parent_task.add_subtask(child_task)

# Dependencies
task.dependencies.append(
    Dependency(successor_id=predecessor_id, type=DependencyType.FINISH_TO_START)
)
```

### Resource

```python
resource = Resource(
    id=0,
    name="John Doe",
    function="1",  # Role ID (1=Programmer, 6=Project Manager, etc.)
    contacts="john@example.com",
    phone="555-1234",
    standard_rate=100.0  # cost per day
)

# Allocation
allocation = ResourceAllocation(
    task_id=1,
    resource_id=0,
    function="1",
    load=100.0,  # percentage (can exceed 100%)
    responsible=True
)

# Vacation
vacation = Vacation(
    resource_id=0,
    start_date=datetime(2025, 12, 20),
    end_date=datetime(2025, 12, 31)
)
```

### Milestone

```python
milestone = Milestone(
    id=10,
    name="✓ Milestone Name",
    date=datetime(2025, 10, 15),
    progress=100  # milestones usually 100% when reached
)
```

### Custom Properties

```python
from ganttproject.models import CustomTaskProperty, PropertyType

# Define custom property
prop = CustomTaskProperty(
    id="tpc0",
    name="Sprint",
    value_type=PropertyType.TEXT,
    default_value="Sprint 1"
)
project.custom_properties.append(prop)

# Set value on task
task.custom_properties["tpc0"] = "Sprint 2"
```

## Role IDs (Built-in)

- `"Default:1"` or `"1"` - Programmer
- `"2"` - Analyst
- `"3"` - Designer
- `"4"` - Tester
- `"5"` - Researcher
- `"6"` - Project Manager
- `"7"` - Educator
- `"8"` - Documenter
- `"9"` - Coordinator
- `"10"` - Marketer

## Dependency Types Explained

```python
# FINISH_TO_START (most common)
# Task B starts when Task A finishes
Dependency(successor_id=task_a.id, type=DependencyType.FINISH_TO_START)

# START_TO_START
# Task B starts when Task A starts (parallel tasks)
Dependency(successor_id=task_a.id, type=DependencyType.START_TO_START)

# FINISH_TO_FINISH
# Task B finishes when Task A finishes
Dependency(successor_id=task_a.id, type=DependencyType.FINISH_TO_FINISH)

# START_TO_FINISH (rare)
# Task B finishes when Task A starts
Dependency(successor_id=task_a.id, type=DependencyType.START_TO_FINISH)
```

## Important Notes

### Task Hierarchy & Dependencies
- When adding dependencies to parent tasks, they inherit to ALL subtasks
- This can cause circular dependency errors
- **Best Practice**: Add dependencies to leaf tasks, not summary/parent tasks

### CDATA Wrapping
- Task notes/descriptions automatically wrapped in CDATA
- Safely handles special XML characters: `<`, `>`, `&`, etc.

### Progress Values
- 0-100 integer
- 0 = not started
- 100 = completed

### Resource Overallocation
- `load` can exceed 100% (e.g., 150% = overtime)
- GanttProject will show overallocation warnings

## Modules

- `models.py` - Core data models (Project, Task, Resource, etc.)
- `generator.py` - GanttGenerator for creating .gan XML files
- `parser.py` - MarkdownParser for importing from markdown
- `analyzer.py` - ProjectAnalyzer for examining existing projects
- `stakeholders.py` - StakeholderManager for multi-stakeholder projects
- `cli.py` - Command-line interface

## Example Scripts

See the parent directory for complete examples:
- `test_new_features.py` - Comprehensive feature demonstration
- `generate_project_example.py` - Real-world project example
- `generate_project_with_history.py` - Project with historical data

## Verifying Output

Open generated .gan files in GanttProject:
```bash
ganttproject my_project.gan
```

Or use the analyzer:
```python
from ganttproject import ProjectAnalyzer

analyzer = ProjectAnalyzer("my_project.gan")
stats = analyzer.get_stats()
print(stats)
```

## Related Utilities

- `../analyze_project_history.py` - Generate historical project data
- `../project_stats.py` - Analyze code metrics for project planning
- `../date_histogram.py` - Visualize development activity

## Version

Current version: 0.1.0

## License

See LICENSE file in project root.
