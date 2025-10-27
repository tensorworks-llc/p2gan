"""
Core data models for GanttProject representation
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum


class TaskPriority(Enum):
    """Task priority levels matching GanttProject - VERIFIED from real .gan files"""
    LOW = 0
    HIGH = 2
    LOWEST = 3
    HIGHEST = 4
    # Note: NORMAL has no priority attribute in XML (omitted = default)


class DependencyType(Enum):
    """Dependency types in GanttProject - VERIFIED from real .gan files"""
    START_TO_START = 1   # SS - Task starts when predecessor starts
    FINISH_TO_START = 2  # FS - Task starts when predecessor finishes (most common)
    FINISH_TO_FINISH = 3 # FF - Task finishes when predecessor finishes
    START_TO_FINISH = 4  # SF - Task finishes when predecessor starts (rare)


class ConstraintType(Enum):
    """Task constraint types"""
    AS_SOON_AS_POSSIBLE = "asap"
    AS_LATE_AS_POSSIBLE = "alap"
    MUST_START_ON = "mso"
    MUST_FINISH_ON = "mfo"
    START_NO_EARLIER_THAN = "snet"
    START_NO_LATER_THAN = "snlt"
    FINISH_NO_EARLIER_THAN = "fnet"
    FINISH_NO_LATER_THAN = "fnlt"


@dataclass
class Resource:
    """Represents a project resource (person, equipment, etc.)"""
    id: int
    name: str
    function: str = "Default:1"  # Role ID or "Default:1"
    contacts: str = ""  # Email address
    phone: str = ""
    standard_rate: float = 0.0

    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        return {
            'id': str(self.id),
            'name': self.name,
            'function': self.function,
            'contacts': self.contacts,
            'phone': self.phone
        }


@dataclass
class ResourceAllocation:
    """Links a resource to a task with allocation parameters"""
    task_id: int
    resource_id: int
    function: str = "Default:1"  # Role for this specific assignment
    responsible: bool = False  # Is this resource responsible for the task?
    load: float = 100.0  # Allocation percentage (can exceed 100%)

    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        return {
            'task-id': str(self.task_id),
            'resource-id': str(self.resource_id),
            'function': self.function,
            'responsible': 'true' if self.responsible else 'false',
            'load': str(self.load)
        }


@dataclass
class Vacation:
    """Resource vacation/unavailability period"""
    resource_id: int
    start_date: datetime
    end_date: datetime

    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        return {
            'start': self.start_date.strftime('%Y-%m-%d'),
            'end': self.end_date.strftime('%Y-%m-%d'),
            'resourceid': str(self.resource_id)
        }


@dataclass
class Role:
    """Project role definition"""
    id: int
    name: str

    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        return {
            'id': str(self.id),
            'name': self.name
        }


@dataclass
class CustomTaskProperty:
    """Definition of a custom task property"""
    id: str  # e.g., "tpc0", "tpc1"
    name: str
    valuetype: str  # "text", "int", "boolean", "date", "double"
    defaultvalue: str = ""
    simple_select: Optional[str] = None  # Links to built-in property like "cost"

    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        attrs = {
            'id': self.id,
            'name': self.name,
            'type': 'custom',
            'valuetype': self.valuetype
        }
        if self.defaultvalue:
            attrs['defaultvalue'] = self.defaultvalue
        return attrs


@dataclass
class Dependency:
    """Represents a task dependency - stored IN predecessor task, points TO successor task

    The <depend> XML element is placed inside the predecessor task and contains
    the ID of the successor task (the task that depends on the predecessor).

    Example: If Task A must finish before Task B starts:
        Task A (predecessor) contains: <depend id="B" type="2" .../>
    """
    successor_id: int  # ID of task that depends on this (was: to_task_id)
    type: DependencyType = DependencyType.FINISH_TO_START
    lag: int = 0  # Days of lag (positive) or lead (negative)
    hardness: str = "Strong"  # "Strong" or "Rubber"

    # Legacy aliases for backwards compatibility
    @property
    def to_task_id(self) -> int:
        """Deprecated: Use successor_id instead"""
        return self.successor_id

    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        return {
            'id': str(self.successor_id),
            'type': str(self.type.value),
            'difference': str(self.lag),
            'hardness': self.hardness
        }


@dataclass
class Task:
    """Represents a project task or subtask"""
    id: int
    name: str
    duration: int  # in days
    uid: str = field(default_factory=lambda: uuid.uuid4().hex)  # UUID without hyphens
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    progress: int = 0  # 0-100
    priority: Optional[TaskPriority] = None  # None = NORMAL (no attribute in XML)
    
    # Hierarchy
    parent_id: Optional[int] = None
    subtasks: List['Task'] = field(default_factory=list)
    level: int = 0  # indentation level
    
    # Resources & Dependencies
    resource_ids: List[int] = field(default_factory=list)
    allocations: Dict[int, float] = field(default_factory=dict)  # resource_id: percentage
    dependencies: List[Dependency] = field(default_factory=list)
    
    # Constraints
    constraint_type: Optional[ConstraintType] = None
    constraint_date: Optional[datetime] = None
    
    # Additional properties
    is_milestone: bool = False
    is_summary: bool = False  # True for parent tasks
    notes: str = ""
    web_link: str = ""
    color: Optional[str] = None
    shape: Optional[str] = None  # Texture pattern, e.g., "1,0,0,0,1,0,0,0,1,0,0,0,1,1,1,1"

    # Cost management
    cost_manual_value: Optional[float] = None  # Fixed/manual cost
    cost_calculated: bool = True  # True = calculate from resources, False = use manual value

    # Custom properties (key = property ID like "tpc0", value = string value)
    custom_properties: Dict[str, str] = field(default_factory=dict)

    # Constraints
    third_date: Optional[datetime] = None  # Constraint date
    third_date_constraint: Optional[int] = None  # 0 or 1 (constraint enabled/disabled)
    
    def add_subtask(self, subtask: 'Task'):
        """Add a subtask and update hierarchy"""
        subtask.parent_id = self.id
        subtask.level = self.level + 1
        self.subtasks.append(subtask)
        self.is_summary = True
        if not self.is_milestone:
            self.duration = 0  # Summary tasks have 0 duration in GanttProject
    
    def add_dependency(self, target_task_id: int,
                      dep_type: DependencyType = DependencyType.FINISH_TO_START,
                      lag: int = 0):
        """Add a dependency to another task (this task is predecessor, target is successor)"""
        dep = Dependency(
            successor_id=target_task_id,
            type=dep_type,
            lag=lag
        )
        self.dependencies.append(dep)
    
    def calculate_dates(self, project_start: datetime, 
                       skip_weekends: bool = True) -> Tuple[datetime, datetime]:
        """Calculate start and end dates based on duration"""
        if self.start_date is None:
            self.start_date = project_start
        
        # Calculate end date considering weekends
        days_added = 0
        current_date = self.start_date
        
        while days_added < self.duration:
            current_date += timedelta(days=1)
            if not skip_weekends or current_date.weekday() < 5:  # Mon-Fri
                days_added += 1
        
        self.end_date = current_date
        return self.start_date, self.end_date
    
    def to_xml_dict(self) -> Dict[str, Any]:
        """Convert to XML-compatible dictionary"""
        from urllib.parse import quote

        xml_dict = {
            'id': str(self.id),
            'uid': self.uid,
            'name': self.name,
            'meeting': 'true' if self.is_milestone else 'false',
            'start': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'duration': str(self.duration),
            'complete': str(self.progress),
            'expand': 'true'
        }

        # Only include priority if not NORMAL (None)
        if self.priority is not None:
            xml_dict['priority'] = str(self.priority.value)

        # Optional attributes
        if self.color:
            xml_dict['color'] = self.color
        if self.shape:
            xml_dict['shape'] = self.shape
        if self.web_link:
            xml_dict['webLink'] = quote(self.web_link, safe='')
        if self.third_date:
            xml_dict['thirdDate'] = self.third_date.strftime('%Y-%m-%d')
        if self.third_date_constraint is not None:
            xml_dict['thirdDate-constraint'] = str(self.third_date_constraint)

        # Cost attributes (only if manual cost is set)
        if self.cost_manual_value is not None:
            xml_dict['cost-manual-value'] = str(self.cost_manual_value)
            xml_dict['cost-calculated'] = 'true' if self.cost_calculated else 'false'

        return xml_dict


@dataclass
class Milestone(Task):
    """Specialized task representing a milestone"""
    def __init__(self, id: int, name: str, date: datetime, **kwargs):
        super().__init__(
            id=id,
            name=name,
            duration=0,
            start_date=date,
            end_date=date,
            is_milestone=True,
            **kwargs
        )


@dataclass
class Project:
    """Represents a complete GanttProject"""
    name: str
    start_date: datetime
    company: str = ""
    web_link: str = ""
    description: str = ""
    
    # Duration
    duration_weeks: Optional[int] = None
    duration_days: Optional[int] = None
    
    # Components
    resources: List[Resource] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)

    # Resource management
    allocations: List[ResourceAllocation] = field(default_factory=list)
    vacations: List[Vacation] = field(default_factory=list)
    roles: List[Role] = field(default_factory=list)

    # Custom properties
    custom_task_properties: List[CustomTaskProperty] = field(default_factory=list)

    # Settings
    view_date: Optional[datetime] = None
    gantt_divider_location: int = 300
    resource_divider_location: int = 300
    version: str = "3.2.3200"
    locale: str = "en_US"

    # Calendar
    calendar_base_id: Optional[str] = None  # e.g., "us.federal"
    working_days: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])  # Mon-Fri
    holidays: List[datetime] = field(default_factory=list)

    # Baselines for tracking
    baselines: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_task(self, task: Task, parent_task: Optional[Task] = None):
        """Add a task to the project"""
        if parent_task:
            parent_task.add_subtask(task)
        else:
            self.tasks.append(task)
    
    def add_milestone(self, milestone: Milestone, parent_task: Optional[Task] = None):
        """Add a milestone to the project"""
        if parent_task:
            parent_task.add_subtask(milestone)
        else:
            self.milestones.append(milestone)
    
    def add_resource(self, resource: Resource) -> Resource:
        """Add a resource to the project"""
        self.resources.append(resource)
        return resource
    
    def find_task_by_name(self, name: str) -> Optional[Task]:
        """Find a task by name (searches all levels)"""
        def search_tasks(tasks: List[Task]) -> Optional[Task]:
            for task in tasks:
                if task.name == name:
                    return task
                if task.subtasks:
                    found = search_tasks(task.subtasks)
                    if found:
                        return found
            return None
        
        # Search in both tasks and milestones
        result = search_tasks(self.tasks)
        if not result:
            result = search_tasks([m for m in self.milestones])
        return result
    
    def find_resource_by_name(self, name: str) -> Optional[Resource]:
        """Find a resource by name"""
        for resource in self.resources:
            if resource.name == name:
                return resource
        return None
    
    def get_all_tasks(self, include_milestones: bool = True) -> List[Task]:
        """Get flat list of all tasks including subtasks"""
        all_tasks = []
        
        def collect_tasks(tasks: List[Task]):
            for task in tasks:
                all_tasks.append(task)
                if task.subtasks:
                    collect_tasks(task.subtasks)
        
        collect_tasks(self.tasks)
        if include_milestones:
            collect_tasks(self.milestones)
        
        return all_tasks
    
    def calculate_critical_path(self) -> List[Task]:
        """Calculate the critical path through the project"""
        # TODO: Implement critical path algorithm
        pass
    
    def validate(self) -> List[str]:
        """Validate project structure and return warnings"""
        warnings = []
        
        # Check for circular dependencies
        # Check for resource overallocation
        # Check for invalid dates
        # Check for orphaned tasks
        
        return warnings