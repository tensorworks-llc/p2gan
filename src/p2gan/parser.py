"""
Enhanced markdown parser with hierarchical task support and advanced dependency management
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from .models import Project, Task, Resource, Milestone, TaskPriority, DependencyType
from .stakeholders import StakeholderManager, get_default_manager


class MarkdownParser:
    """Enhanced parser for project markdown files"""
    
    def __init__(self, stakeholder_manager: Optional[StakeholderManager] = None):
        self.stakeholder_manager = stakeholder_manager or get_default_manager()
        self.project = None
        self.current_section = None
        self.task_counter = 0
        self.resource_counter = 0
        self.task_name_to_id = {}  # Map task names to IDs for dependency resolution
        self.pending_dependencies = []  # Dependencies to resolve after all tasks are created
        
    def parse_file(self, filepath: str) -> Project:
        """Parse a markdown file and return a Project object"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Project:
        """Parse markdown content and return a Project object"""
        lines = content.split('\n')
        current_phase = None
        current_subphase = None
        current_taskgroup = None
        
        for line_num, line in enumerate(lines):
            if not line.strip():
                continue
            
            # Detect section headers
            if line.startswith('# Project:'):
                self._parse_project_header(line)
            elif line.startswith('**Start Date:**'):
                self._parse_start_date(line)
            elif line.startswith('**Duration:**'):
                self._parse_duration(line)
            elif line.startswith('## Resources'):
                self.current_section = 'resources'
                continue
            elif line.startswith('## Tasks'):
                self.current_section = 'tasks'
                continue
            elif line.startswith('## Milestones'):
                self.current_section = 'milestones'
                continue
            elif line.startswith('###'):
                # Phase header
                if self.current_section == 'tasks':
                    current_phase = self._parse_phase(line)
                    current_subphase = None  # Reset subphase
                    current_taskgroup = None  # Reset task group
            elif line.startswith('####'):
                # Sub-phase header
                if self.current_section == 'tasks' and current_phase:
                    current_subphase = self._parse_subphase(line, current_phase)
                    current_taskgroup = None  # Reset task group
            elif line.startswith('#####'):
                # Task group header
                if self.current_section == 'tasks' and current_subphase:
                    current_taskgroup = self._parse_taskgroup(line, current_subphase)
            elif line.startswith('- [ ]') and self.current_section == 'tasks':
                # Embedded milestone in tasks section
                self._parse_embedded_milestone(line, current_phase, current_subphase, current_taskgroup)
            elif line.startswith('- '):
                # Task, resource, or milestone line
                if self.current_section == 'resources':
                    self._parse_resource(line)
                elif self.current_section == 'tasks':
                    parent = current_taskgroup if current_taskgroup else (current_subphase if current_subphase else current_phase)
                    self._parse_task(line, parent)
                elif self.current_section == 'milestones':
                    self._parse_milestone(line)
            elif line.strip().startswith('- ') and self.current_section == 'tasks':
                # Subtask properties (indented)
                self._parse_task_property(line)
        
        # Resolve all pending dependencies
        self._resolve_dependencies()
        
        # Calculate dates
        self._calculate_dates()
        
        # Import stakeholders for this project
        if self.project:
            self.stakeholder_manager.import_from_markdown(content, self.project.name)
        
        return self.project
    
    def _parse_project_header(self, line: str):
        """Parse project name from header"""
        match = re.search(r'# Project:\s*(.+)', line)
        if match:
            project_name = match.group(1).strip()
            self.project = Project(
                name=project_name,
                start_date=datetime.now()  # Default, will be updated
            )
    
    def _parse_start_date(self, line: str):
        """Parse start date"""
        match = re.search(r'\*\*Start Date:\*\*\s*(\d{4}-\d{2}-\d{2})', line)
        if match and self.project:
            date_str = match.group(1)
            self.project.start_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    def _parse_duration(self, line: str):
        """Parse project duration"""
        match = re.search(r'\*\*Duration:\*\*\s*(\d+)\s*(weeks?|days?)', line)
        if match and self.project:
            duration = int(match.group(1))
            unit = match.group(2)
            if 'week' in unit:
                self.project.duration_weeks = duration
                self.project.duration_days = duration * 7
            else:
                self.project.duration_days = duration
    
    def _parse_resource(self, line: str):
        """Parse resource from markdown line"""
        # Format: - Name (Role)
        match = re.match(r'^-\s*([^(]+?)\s*(?:\(([^)]+)\))?', line.strip())
        if match:
            name = match.group(1).strip()
            role = match.group(2).strip() if match.group(2) else ""
            
            # Get or create stakeholder
            stakeholder = self.stakeholder_manager.find_or_create(name=name, role=role)
            
            resource = Resource(
                id=self.resource_counter,
                name=name,
                function=role if role else "Default:1",
                contacts=stakeholder.email
            )
            
            self.project.add_resource(resource)
            self.resource_counter += 1
    
    def _parse_phase(self, line: str) -> Task:
        """Parse phase header and create phase task"""
        phase_name = line.replace('###', '').strip()
        
        phase = Task(
            id=self.task_counter,
            name=phase_name,
            duration=0,  # Summary task
            is_summary=True
        )
        
        self.project.add_task(phase)
        self.task_name_to_id[phase_name] = self.task_counter
        self.task_counter += 1
        
        return phase
    
    def _parse_subphase(self, line: str, parent_phase: Task) -> Task:
        """Parse sub-phase header and create sub-phase task"""
        subphase_name = line.replace('####', '').strip()
        
        subphase = Task(
            id=self.task_counter,
            name=subphase_name,
            duration=0,  # Summary task
            is_summary=True,
            parent_id=parent_phase.id
        )
        
        parent_phase.add_subtask(subphase)
        self.task_name_to_id[subphase_name] = self.task_counter
        self.task_counter += 1
        
        return subphase
    
    def _parse_taskgroup(self, line: str, parent_subphase: Task) -> Task:
        """Parse task group header and create task group"""
        taskgroup_name = line.replace('#####', '').strip()
        
        taskgroup = Task(
            id=self.task_counter,
            name=taskgroup_name,
            duration=0,  # Summary task
            is_summary=True,
            parent_id=parent_subphase.id
        )
        
        parent_subphase.add_subtask(taskgroup)
        self.task_name_to_id[taskgroup_name] = self.task_counter
        self.task_counter += 1
        
        return taskgroup
    
    def _parse_embedded_milestone(self, line: str, current_phase: Optional[Task], current_subphase: Optional[Task], current_taskgroup: Optional[Task] = None):
        """Parse milestone embedded within task section"""
        # Format: - [ ] Milestone Name (YYYY-MM-DD)
        match = re.match(r'^-\s*\[\s*\]\s*([^(]+)\s*(?:\(([^)]+)\))?', line.strip())
        if match:
            milestone_name = match.group(1).strip()
            date_str = match.group(2).strip() if match.group(2) else None
            
            milestone_date = self.project.start_date
            if date_str:
                try:
                    milestone_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    pass
            
            # Create milestone as a task with meeting=true and duration=0
            milestone_task = Task(
                id=self.task_counter,
                name=milestone_name,
                duration=0,
                start_date=milestone_date,
                is_milestone=True,
                parent_id=current_subphase.id if current_subphase else (current_phase.id if current_phase else None)
            )
            
            # Add milestone task to appropriate parent
            if current_taskgroup:
                current_taskgroup.add_subtask(milestone_task)
            elif current_subphase:
                current_subphase.add_subtask(milestone_task)
            elif current_phase:
                current_phase.add_subtask(milestone_task)
            else:
                self.project.add_task(milestone_task)
            
            # Also add as milestone to project for counting
            milestone = Milestone(
                id=self.task_counter,
                name=milestone_name,
                date=milestone_date
            )
            self.project.add_milestone(milestone)
            
            self.task_name_to_id[milestone_name] = self.task_counter
            self.task_counter += 1
    
    def _parse_task(self, line: str, current_phase: Optional[Task]):
        """Parse task from markdown line"""
        # Format: - **Task Name** (duration days, Resource Name)
        match = re.match(r'^-\s*\*\*([^*]+)\*\*\s*(?:\(([^)]+)\))?', line.strip())
        if not match:
            return
        
        task_name = match.group(1).strip()
        details = match.group(2) if match.group(2) else ""
        
        # Parse duration and resource from details
        duration = 1
        resource_name = None
        
        if details:
            # Try to parse "X days, ResourceName" format
            parts = [p.strip() for p in details.split(',')]
            for part in parts:
                # Check for duration
                duration_match = re.search(r'(\d+)\s*days?', part)
                if duration_match:
                    duration = int(duration_match.group(1))
                else:
                    # Assume it's a resource name if no duration pattern
                    if not duration_match and part and not part.isdigit():
                        resource_name = part
        
        # Find resource ID
        resource_id = None
        if resource_name:
            for resource in self.project.resources:
                if resource.name == resource_name:
                    resource_id = resource.id
                    break
        
        task = Task(
            id=self.task_counter,
            name=task_name,
            duration=duration,
            resource_ids=[resource_id] if resource_id is not None else []
        )
        
        # Add to phase if we're in one
        if current_phase:
            current_phase.add_subtask(task)
        else:
            self.project.add_task(task)
        
        self.task_name_to_id[task_name] = self.task_counter
        self.task_counter += 1
        
        return task
    
    def _parse_task_property(self, line: str):
        """Parse task properties like start date, dependencies, priority"""
        line = line.strip()
        
        # Skip if not a property line
        if not line.startswith('- '):
            return
        
        property_line = line[2:].strip()  # Remove "- "
        
        # Get the last task created (this property belongs to it)
        if self.task_counter == 0:
            return
        
        last_task_id = self.task_counter - 1
        last_task = self._find_task_by_id(last_task_id)
        if not last_task:
            return
        
        # Parse different property types
        if property_line.startswith('Start:'):
            self._parse_start_property(property_line, last_task)
        elif property_line.startswith('Dependencies:'):
            self._parse_dependencies_property(property_line, last_task)
        elif property_line.startswith('Priority:'):
            self._parse_priority_property(property_line, last_task)
        elif property_line.startswith('Progress:'):
            self._parse_progress_property(property_line, last_task)
    
    def _parse_start_property(self, property_line: str, task: Task):
        """Parse start date property"""
        start_value = property_line.replace('Start:', '').strip()
        
        # Check for absolute date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', start_value)
        if date_match:
            task.start_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
            return
        
        # Check for "After TaskName" format
        after_match = re.search(r'After\s+(.+)', start_value, re.IGNORECASE)
        if after_match:
            prerequisite_name = after_match.group(1).strip()
            # Store for later resolution
            self.pending_dependencies.append((task.id, prerequisite_name, DependencyType.FINISH_TO_START))
    
    def _parse_dependencies_property(self, property_line: str, task: Task):
        """Parse dependencies property"""
        deps_value = property_line.replace('Dependencies:', '').strip()
        
        # Split by commas and process each dependency
        for dep_name in deps_value.split(','):
            dep_name = dep_name.strip()
            if dep_name:
                self.pending_dependencies.append((task.id, dep_name, DependencyType.FINISH_TO_START))
    
    def _parse_priority_property(self, property_line: str, task: Task):
        """Parse priority property"""
        priority_value = property_line.replace('Priority:', '').strip().lower()
        
        priority_map = {
            'low': TaskPriority.LOW,
            'medium': None,  # Normal priority = no attribute in XML
            'normal': None,
            'high': TaskPriority.HIGH,
            'highest': TaskPriority.HIGHEST,
            'critical': TaskPriority.HIGHEST
        }

        task.priority = priority_map.get(priority_value, None)
    
    def _parse_progress_property(self, property_line: str, task: Task):
        """Parse progress property"""
        progress_match = re.search(r'(\d+)%?', property_line.replace('Progress:', '').strip())
        if progress_match:
            task.progress = int(progress_match.group(1))
    
    def _parse_milestone(self, line: str):
        """Parse milestone from markdown line"""
        # Format: - [ ] Milestone Name (YYYY-MM-DD)
        match = re.match(r'^-\s*\[\s*\]\s*([^(]+)\s*(?:\(([^)]+)\))?', line.strip())
        if match:
            milestone_name = match.group(1).strip()
            date_str = match.group(2).strip() if match.group(2) else None
            
            milestone_date = self.project.start_date
            if date_str:
                try:
                    milestone_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    pass
            
            milestone = Milestone(
                id=self.task_counter,
                name=milestone_name,
                date=milestone_date
            )
            
            self.project.add_milestone(milestone)
            self.task_name_to_id[milestone_name] = self.task_counter
            self.task_counter += 1
    
    def _find_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by ID in the project"""
        all_tasks = self.project.get_all_tasks()
        for task in all_tasks:
            if task.id == task_id:
                return task
        return None
    
    def _resolve_dependencies(self):
        """Resolve all pending dependencies"""
        for task_id, dep_name, dep_type in self.pending_dependencies:
            task = self._find_task_by_id(task_id)
            if not task:
                continue
            
            # Find the dependency task - try exact match first
            dep_task_id = self.task_name_to_id.get(dep_name)
            if dep_task_id is None:
                # Try partial matching for short names
                for full_name, full_id in self.task_name_to_id.items():
                    if dep_name in full_name or full_name.endswith(dep_name):
                        dep_task_id = full_id
                        break
            
            if dep_task_id is not None:
                # Check if this dependency already exists to avoid duplicates
                already_exists = any(d.successor_id == dep_task_id for d in task.dependencies)
                if not already_exists:
                    task.add_dependency(dep_task_id, dep_type)
    
    def _calculate_dates(self):
        """Calculate start and end dates for all tasks based on dependencies"""
        if not self.project:
            return
        
        # Get all tasks and sort by dependencies (topological sort)
        all_tasks = self.project.get_all_tasks()
        scheduled_tasks = set()
        
        # First pass: schedule tasks without dependencies
        for task in all_tasks:
            if not task.dependencies:
                if task.start_date is None:
                    task.start_date = self.project.start_date
                task.calculate_dates(task.start_date)
                scheduled_tasks.add(task.id)
        
        # Keep scheduling dependent tasks until all are done
        max_iterations = len(all_tasks) * 2  # Prevent infinite loops
        iteration = 0
        
        while len(scheduled_tasks) < len(all_tasks) and iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            for task in all_tasks:
                if task.id in scheduled_tasks:
                    continue
                
                # Check if all dependencies are scheduled
                all_deps_ready = True
                latest_end_date = self.project.start_date
                
                for dep in task.dependencies:
                    if dep.to_task_id not in scheduled_tasks:
                        all_deps_ready = False
                        break
                    
                    # Find the dependency task and get its end date
                    dep_task = self._find_task_by_id(dep.to_task_id)
                    if dep_task and dep_task.end_date:
                        # For FINISH_TO_START dependencies, start after predecessor ends
                        if dep.type == DependencyType.FINISH_TO_START:
                            candidate_start = dep_task.end_date + timedelta(days=1)
                            if candidate_start > latest_end_date:
                                latest_end_date = candidate_start
                
                if all_deps_ready:
                    # Schedule this task
                    if task.start_date is None:
                        task.start_date = latest_end_date
                    task.calculate_dates(task.start_date)
                    scheduled_tasks.add(task.id)
                    progress_made = True
            
            if not progress_made:
                # Handle remaining tasks without dependencies
                for task in all_tasks:
                    if task.id not in scheduled_tasks:
                        if task.start_date is None:
                            task.start_date = self.project.start_date
                        task.calculate_dates(task.start_date)
                        scheduled_tasks.add(task.id)
                break


class ProjectAnalyzer:
    """Analyzes various project types and generates Gantt charts"""
    
    def __init__(self, stakeholder_manager: Optional[StakeholderManager] = None):
        self.stakeholder_manager = stakeholder_manager or get_default_manager()
    
    def analyze_project(self, project_path: str, project_type: str = "auto") -> Project:
        """Analyze a project and generate a Gantt chart"""
        from .analyzer import PythonPackageAnalyzer
        
        project_path = Path(project_path)
        
        if project_type == "auto":
            project_type = self._detect_project_type(project_path)
        
        if project_type == "python":
            analyzer = PythonPackageAnalyzer(self.stakeholder_manager)
            analysis = analyzer.analyze_package(project_path)
            return analyzer.generate_gantt_project(
                analysis, 
                datetime.now(),
                team_size=3
            )
        elif project_type == "markdown":
            parser = MarkdownParser(self.stakeholder_manager)
            # Look for project markdown files
            md_files = list(project_path.glob("**/PROJECT_*.md"))
            if md_files:
                return parser.parse_file(str(md_files[0]))
        
        # Fallback: create basic project structure
        return self._create_basic_project(project_path)
    
    def _detect_project_type(self, project_path: Path) -> str:
        """Detect project type based on files present"""
        if (project_path / "__init__.py").exists() or (project_path / "setup.py").exists():
            return "python"
        elif list(project_path.glob("**/*.md")):
            return "markdown"
        elif (project_path / "package.json").exists():
            return "javascript"
        elif (project_path / "Cargo.toml").exists():
            return "rust"
        else:
            return "generic"
    
    def _create_basic_project(self, project_path: Path) -> Project:
        """Create a basic project structure for unknown types"""
        project = Project(
            name=f"{project_path.name} Project",
            start_date=datetime.now(),
            description=f"Generic project for {project_path.name}"
        )
        
        # Add basic phases
        phases = [
            ("Analysis", 5),
            ("Planning", 3),
            ("Implementation", 15),
            ("Testing", 7),
            ("Documentation", 5),
            ("Deployment", 2)
        ]
        
        task_id = 0
        for phase_name, duration in phases:
            phase = Task(
                id=task_id,
                name=phase_name,
                duration=duration
            )
            project.add_task(phase)
            task_id += 1
        
        return project