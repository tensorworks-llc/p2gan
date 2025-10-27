"""Tests for p2gan.generator module."""

import pytest
import xml.etree.ElementTree as ET
from datetime import datetime
from p2gan.generator import GanttGenerator
from p2gan.models import Project, Task, Resource, ResourceAllocation, Milestone


class TestGanttGenerator:
    """Test GanttGenerator functionality."""

    @pytest.fixture
    def simple_project(self):
        """Create a simple project for testing."""
        project = Project(
            name="Test Project",
            start_date=datetime(2025, 1, 1),
            company="Test Corp"
        )

        # Add a resource
        resource = Resource(id=0, name="Alice", role="Developer")
        project.add_resource(resource)

        # Add a task
        task = Task(
            id=0,
            name="Development",
            start_date=datetime(2025, 1, 1),
            duration=5,
            progress=50
        )
        allocation = ResourceAllocation(task_id=0, resource_id=0, load=100.0)
        task.allocations.append(allocation)
        project.add_task(task)

        # Add a milestone
        milestone = Milestone(
            id=1,
            name="Project Complete",
            date=datetime(2025, 1, 8)
        )
        project.add_task(milestone)

        return project

    def test_generate_xml_structure(self, simple_project):
        """Test that generated XML has correct structure."""
        generator = GanttGenerator(simple_project)
        xml_string = generator.generate_xml()

        # Parse the XML to check structure
        root = ET.fromstring(xml_string)

        assert root.tag == "project"
        assert root.get("name") == "Test Project"
        assert root.get("version") == "3.2.3230"

    def test_generate_tasks_section(self, simple_project):
        """Test tasks section generation."""
        generator = GanttGenerator(simple_project)
        xml_string = generator.generate_xml()

        root = ET.fromstring(xml_string)
        tasks_elem = root.find("tasks")

        assert tasks_elem is not None
        task_elements = tasks_elem.findall("task")
        assert len(task_elements) == 2  # 1 task + 1 milestone

    def test_generate_resources_section(self, simple_project):
        """Test resources section generation."""
        generator = GanttGenerator(simple_project)
        xml_string = generator.generate_xml()

        root = ET.fromstring(xml_string)
        resources_elem = root.find("resources")

        assert resources_elem is not None
        resource_elements = resources_elem.findall("resource")
        assert len(resource_elements) == 1
        assert resource_elements[0].get("name") == "Alice"

    def test_generate_allocations_section(self, simple_project):
        """Test allocations section generation."""
        generator = GanttGenerator(simple_project)
        xml_string = generator.generate_xml()

        root = ET.fromstring(xml_string)
        allocations_elem = root.find("allocations")

        assert allocations_elem is not None
        allocation_elements = allocations_elem.findall("allocation")
        assert len(allocation_elements) == 1
        assert allocation_elements[0].get("task-id") == "0"
        assert allocation_elements[0].get("resource-id") == "0"

    def test_save_to_file(self, simple_project, tmp_path):
        """Test saving to file."""
        generator = GanttGenerator(simple_project)
        output_file = tmp_path / "test_output.gan"

        generator.save(str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert '<project' in content

    def test_milestone_generation(self, simple_project):
        """Test that milestones are generated correctly."""
        generator = GanttGenerator(simple_project)
        xml_string = generator.generate_xml()

        root = ET.fromstring(xml_string)
        tasks_elem = root.find("tasks")
        task_elements = tasks_elem.findall("task")

        # Find the milestone
        milestone_elem = next(
            (t for t in task_elements if t.get("name") == "Project Complete"),
            None
        )
        assert milestone_elem is not None
        assert milestone_elem.get("duration") == "0"
        assert milestone_elem.get("meeting") == "true"

    def test_task_with_dependencies(self):
        """Test generating tasks with dependencies."""
        project = Project(name="Dep Test", start_date=datetime(2025, 1, 1))

        task1 = Task(id=0, name="Task 1", start_date=datetime(2025, 1, 1), duration=3)
        task2 = Task(id=1, name="Task 2", start_date=datetime(2025, 1, 4), duration=2)

        # Task 2 depends on Task 1
        from p2gan.models import Dependency, DependencyType
        dep = Dependency(
            task_id=1,
            depends_on=0,
            type=DependencyType.FINISH_TO_START
        )
        task2.dependencies.append(dep)

        project.add_task(task1)
        project.add_task(task2)

        generator = GanttGenerator(project)
        xml_string = generator.generate_xml()

        root = ET.fromstring(xml_string)
        tasks_elem = root.find("tasks")
        task2_elem = next(
            (t for t in tasks_elem.findall("task") if t.get("name") == "Task 2"),
            None
        )

        depend_elem = task2_elem.find("depend")
        assert depend_elem is not None
        assert depend_elem.get("id") == "0"
        assert depend_elem.get("type") == "2"  # FS dependency

    def test_empty_project(self):
        """Test generating empty project."""
        project = Project(name="Empty", start_date=datetime(2025, 1, 1))
        generator = GanttGenerator(project)

        xml_string = generator.generate_xml()
        root = ET.fromstring(xml_string)

        assert root.tag == "project"
        assert root.get("name") == "Empty"

        # Should still have sections even if empty
        assert root.find("tasks") is not None
        assert root.find("resources") is not None
        assert root.find("allocations") is not None

    def test_special_characters_in_names(self):
        """Test handling of special characters in names."""
        project = Project(
            name='Test & "Special" <Characters>',
            start_date=datetime(2025, 1, 1)
        )
        task = Task(
            id=0,
            name='Task with & "quotes" <brackets>',
            start_date=datetime(2025, 1, 1),
            duration=1
        )
        project.add_task(task)

        generator = GanttGenerator(project)
        xml_string = generator.generate_xml()

        # Should not raise any parsing errors
        root = ET.fromstring(xml_string)
        assert root is not None

    def test_date_format(self):
        """Test that dates are formatted correctly."""
        project = Project(name="Date Test", start_date=datetime(2025, 3, 15))
        task = Task(
            id=0,
            name="March Task",
            start_date=datetime(2025, 3, 15),
            duration=1
        )
        project.add_task(task)

        generator = GanttGenerator(project)
        xml_string = generator.generate_xml()

        root = ET.fromstring(xml_string)
        task_elem = root.find(".//task[@name='March Task']")
        assert task_elem.get("start") == "2025-03-15"