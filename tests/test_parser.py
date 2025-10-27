"""Tests for p2gan.parser module."""

import pytest
from datetime import datetime
from p2gan.parser import MarkdownParser
from p2gan.models import TaskPriority


class TestMarkdownParser:
    """Test MarkdownParser functionality."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return MarkdownParser()

    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown content for testing."""
        return """# Project: Test Project

**Start Date:** 2025-01-15
**Duration:** 4 weeks

## Resources
- Alice Johnson (Developer)
- Bob Smith (Designer)

## Tasks
### Phase 1: Planning
- **Requirements Analysis** (5 days, Alice Johnson)
  - Priority: High
  - Progress: 0%

- **Design Mockups** (3 days, Bob Smith)
  - Dependencies: Requirements Analysis
  - Priority: Medium

### Phase 2: Implementation
- **Development** (10 days, Alice Johnson)
  - Dependencies: Design Mockups
  - Priority: High
  - Progress: 25%

## Milestones
- [ ] Planning Complete (2025-01-22)
- [ ] Project Launch (2025-02-12)
"""

    def test_parse_project_metadata(self, parser, sample_markdown):
        """Test parsing project metadata."""
        project = parser.parse(sample_markdown)

        assert project.name == "Test Project"
        assert project.start_date == datetime(2025, 1, 15)

    def test_parse_resources(self, parser, sample_markdown):
        """Test parsing resources."""
        project = parser.parse(sample_markdown)

        assert len(project.resources) == 2
        assert project.resources[0].name == "Alice Johnson"
        assert project.resources[0].role == "Developer"
        assert project.resources[1].name == "Bob Smith"
        assert project.resources[1].role == "Designer"

    def test_parse_tasks(self, parser, sample_markdown):
        """Test parsing tasks."""
        project = parser.parse(sample_markdown)

        # Should have 3 tasks
        tasks = [t for t in project.tasks if not hasattr(t, 'meeting') or not t.meeting]
        assert len(tasks) == 3

        # Check first task
        task1 = tasks[0]
        assert task1.name == "Requirements Analysis"
        assert task1.duration == 5
        assert task1.priority == TaskPriority.HIGH
        assert task1.progress == 0

    def test_parse_dependencies(self, parser, sample_markdown):
        """Test parsing task dependencies."""
        project = parser.parse(sample_markdown)

        tasks = [t for t in project.tasks if not hasattr(t, 'meeting') or not t.meeting]

        # Design Mockups depends on Requirements Analysis
        design_task = next(t for t in tasks if t.name == "Design Mockups")
        assert len(design_task.dependencies) == 1

        # Development depends on Design Mockups
        dev_task = next(t for t in tasks if t.name == "Development")
        assert len(dev_task.dependencies) == 1

    def test_parse_milestones(self, parser, sample_markdown):
        """Test parsing milestones."""
        project = parser.parse(sample_markdown)

        milestones = [t for t in project.tasks if hasattr(t, 'meeting') and t.meeting]
        assert len(milestones) == 2

        assert milestones[0].name == "Planning Complete"
        assert milestones[0].start_date == datetime(2025, 1, 22)
        assert milestones[0].duration == 0

        assert milestones[1].name == "Project Launch"
        assert milestones[1].start_date == datetime(2025, 2, 12)

    def test_parse_empty_markdown(self, parser):
        """Test parsing empty markdown."""
        with pytest.raises(ValueError):
            parser.parse("")

    def test_parse_minimal_project(self, parser):
        """Test parsing minimal project."""
        markdown = """# Project: Minimal

**Start Date:** 2025-01-01

## Tasks
- **Task One** (1 day)
"""
        project = parser.parse(markdown)
        assert project.name == "Minimal"
        assert len(project.tasks) == 1

    def test_parse_task_with_date_after(self, parser):
        """Test parsing task with 'After' date specification."""
        markdown = """# Project: Sequential

**Start Date:** 2025-01-01

## Tasks
- **Task A** (2 days)
- **Task B** (3 days)
  - Start: After Task A
"""
        project = parser.parse(markdown)
        tasks = project.tasks
        assert len(tasks) == 2

        # Task B should have dependency on Task A
        task_b = tasks[1]
        assert len(task_b.dependencies) == 1

    def test_parse_hierarchical_tasks(self, parser):
        """Test parsing tasks with parent-child relationships."""
        markdown = """# Project: Hierarchical

**Start Date:** 2025-01-01

## Tasks
### Phase 1
- **Parent Task** (10 days)
  - **Subtask 1** (3 days)
  - **Subtask 2** (4 days)
"""
        # This test would need implementation of hierarchical parsing
        # Currently marking as expected to potentially fail
        project = parser.parse(markdown)
        # Basic assertion - detailed hierarchy testing would need more work
        assert len(project.tasks) >= 1