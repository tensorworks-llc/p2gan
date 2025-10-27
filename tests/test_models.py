"""Tests for p2gan.models module."""

import pytest
from datetime import datetime, timedelta
from p2gan.models import (
    Project, Task, Resource, Milestone, Dependency,
    ResourceAllocation, TaskPriority, DependencyType
)


class TestProject:
    """Test Project model."""

    def test_create_project(self):
        """Test creating a basic project."""
        project = Project(
            name="Test Project",
            start_date=datetime(2025, 1, 1),
            company="Test Company"
        )
        assert project.name == "Test Project"
        assert project.start_date == datetime(2025, 1, 1)
        assert project.company == "Test Company"
        assert len(project.tasks) == 0
        assert len(project.resources) == 0

    def test_add_task(self):
        """Test adding tasks to project."""
        project = Project(name="Test", start_date=datetime(2025, 1, 1))
        task = Task(id=0, name="Task 1", start_date=datetime(2025, 1, 1), duration=5)

        project.add_task(task)
        assert len(project.tasks) == 1
        assert project.tasks[0].name == "Task 1"

    def test_add_resource(self):
        """Test adding resources to project."""
        project = Project(name="Test", start_date=datetime(2025, 1, 1))
        resource = Resource(id=0, name="Alice", role="Developer")

        project.add_resource(resource)
        assert len(project.resources) == 1
        assert project.resources[0].name == "Alice"


class TestTask:
    """Test Task model."""

    def test_create_task(self):
        """Test creating a basic task."""
        task = Task(
            id=0,
            name="Development",
            start_date=datetime(2025, 1, 1),
            duration=10,
            progress=25,
            priority=TaskPriority.HIGH
        )
        assert task.name == "Development"
        assert task.duration == 10
        assert task.progress == 25
        assert task.priority == TaskPriority.HIGH

    def test_calculate_end_date(self):
        """Test end date calculation."""
        task = Task(
            id=0,
            name="Test Task",
            start_date=datetime(2025, 1, 1),
            duration=5
        )
        # 5 business days from Jan 1, 2025 (Wednesday)
        # Jan 1 (Wed) + 5 business days = Jan 7 (Tue)
        expected_end = datetime(2025, 1, 7)
        assert task.calculate_end_date() == expected_end

    def test_add_dependency(self):
        """Test adding task dependencies."""
        task1 = Task(id=0, name="Task 1", start_date=datetime(2025, 1, 1), duration=5)
        task2 = Task(id=1, name="Task 2", start_date=datetime(2025, 1, 6), duration=3)

        dependency = Dependency(
            task_id=1,
            depends_on=0,
            type=DependencyType.FINISH_TO_START
        )
        task2.dependencies.append(dependency)

        assert len(task2.dependencies) == 1
        assert task2.dependencies[0].depends_on == 0

    def test_add_subtask(self):
        """Test hierarchical task structure."""
        parent = Task(id=0, name="Parent", start_date=datetime(2025, 1, 1), duration=10)
        child = Task(id=1, name="Child", start_date=datetime(2025, 1, 1), duration=5)

        parent.add_subtask(child)
        assert len(parent.subtasks) == 1
        assert parent.subtasks[0].name == "Child"
        assert child.parent_id == 0


class TestMilestone:
    """Test Milestone model."""

    def test_create_milestone(self):
        """Test creating a milestone (zero-duration task)."""
        milestone = Milestone(
            id=0,
            name="Project Kickoff",
            date=datetime(2025, 1, 1)
        )
        assert milestone.name == "Project Kickoff"
        assert milestone.duration == 0
        assert milestone.meeting is True
        assert milestone.start_date == datetime(2025, 1, 1)

    def test_milestone_has_zero_duration(self):
        """Test that milestones always have zero duration."""
        milestone = Milestone(
            id=0,
            name="Deadline",
            date=datetime(2025, 2, 1)
        )
        # Even if we try to set duration, it should remain 0
        milestone.duration = 5
        assert milestone.duration == 0


class TestResource:
    """Test Resource model."""

    def test_create_resource(self):
        """Test creating a resource."""
        resource = Resource(
            id=0,
            name="Bob Smith",
            role="Project Manager",
            email="bob@example.com",
            phone="555-0100"
        )
        assert resource.name == "Bob Smith"
        assert resource.role == "Project Manager"
        assert resource.email == "bob@example.com"
        assert resource.phone == "555-0100"

    def test_resource_with_rate(self):
        """Test resource with standard rate."""
        resource = Resource(
            id=0,
            name="Consultant",
            role="Senior Consultant",
            standard_rate=150.0
        )
        assert resource.standard_rate == 150.0


class TestResourceAllocation:
    """Test ResourceAllocation model."""

    def test_create_allocation(self):
        """Test creating a resource allocation."""
        allocation = ResourceAllocation(
            task_id=0,
            resource_id=0,
            load=50.0,
            responsible=True
        )
        assert allocation.task_id == 0
        assert allocation.resource_id == 0
        assert allocation.load == 50.0
        assert allocation.responsible is True

    def test_full_allocation(self):
        """Test 100% resource allocation."""
        allocation = ResourceAllocation(
            task_id=1,
            resource_id=2,
            load=100.0
        )
        assert allocation.load == 100.0
        assert allocation.responsible is False  # Default value


class TestDependency:
    """Test Dependency model."""

    def test_create_dependency(self):
        """Test creating task dependencies."""
        dep = Dependency(
            task_id=1,
            depends_on=0,
            type=DependencyType.FINISH_TO_START,
            lag=2
        )
        assert dep.task_id == 1
        assert dep.depends_on == 0
        assert dep.type == DependencyType.FINISH_TO_START
        assert dep.lag == 2

    def test_dependency_types(self):
        """Test all dependency types."""
        types = [
            DependencyType.FINISH_TO_START,
            DependencyType.START_TO_START,
            DependencyType.FINISH_TO_FINISH,
            DependencyType.START_TO_FINISH
        ]
        for dep_type in types:
            dep = Dependency(task_id=1, depends_on=0, type=dep_type)
            assert dep.type == dep_type


class TestTaskPriority:
    """Test TaskPriority enum."""

    def test_priority_values(self):
        """Test priority enum values."""
        assert TaskPriority.LOW.value == 0
        assert TaskPriority.NORMAL.value == 1
        assert TaskPriority.HIGH.value == 2

    def test_priority_names(self):
        """Test priority enum names."""
        assert TaskPriority.LOW.name == "LOW"
        assert TaskPriority.NORMAL.name == "NORMAL"
        assert TaskPriority.HIGH.name == "HIGH"