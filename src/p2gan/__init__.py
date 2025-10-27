"""
p2gan - Project to Gantt Converter

A comprehensive Python package for generating, manipulating, and analyzing
GanttProject files from various sources including markdown plans,
code repositories, and structured project definitions.
"""

__version__ = "0.1.2"
__author__ = "Tensorworks LLC"
__package__ = "p2gan"

from .models import (
    Project, Task, Resource, Milestone, Dependency,
    ResourceAllocation, Vacation, Role, CustomTaskProperty,
    TaskPriority, DependencyType
)
from .parser import MarkdownParser, ProjectAnalyzer
from .generator import GanttGenerator
from .stakeholders import StakeholderManager
from .project_history import ProjectHistoryAnalyzer
from .date_histogram import DateHistogram
from .project_stats import ProjectStats

__all__ = [
    'Project',
    'Task',
    'Resource',
    'ResourceAllocation',
    'Vacation',
    'Role',
    'CustomTaskProperty',
    'Milestone',
    'Dependency',
    'TaskPriority',
    'DependencyType',
    'MarkdownParser',
    'ProjectAnalyzer',
    'GanttGenerator',
    'StakeholderManager',
    'ProjectHistoryAnalyzer',
    'DateHistogram',
    'ProjectStats'
]