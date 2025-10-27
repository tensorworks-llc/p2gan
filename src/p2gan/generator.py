"""
Advanced GanttProject XML generator with hierarchical task support
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from xml.dom import minidom

from .models import Project, Task, Resource, Milestone, DependencyType


class GanttGenerator:
    """Generates GanttProject XML files from Project objects"""
    
    def __init__(self):
        self.task_id_map = {}  # Map original IDs to sequential IDs
        self.next_id = 0
    
    def _ensure_task_dates_calculated(self, project: Project):
        """Ensure all tasks have calculated dates based on dependencies"""
        all_tasks = project.get_all_tasks()
        scheduled_tasks = set()
        
        # First pass: schedule tasks without dependencies
        for task in all_tasks:
            if not task.dependencies:
                if task.start_date is None:
                    task.start_date = project.start_date
                task.calculate_dates(task.start_date)
                scheduled_tasks.add(task.id)
        
        # Keep scheduling dependent tasks until all are done
        max_iterations = len(all_tasks) * 2
        iteration = 0
        
        while len(scheduled_tasks) < len(all_tasks) and iteration < max_iterations:
            iteration += 1
            progress_made = False
            
            for task in all_tasks:
                if task.id in scheduled_tasks:
                    continue
                
                # Check if all dependencies are scheduled
                all_deps_ready = True
                latest_end_date = project.start_date
                
                for dep in task.dependencies:
                    if dep.to_task_id not in scheduled_tasks:
                        all_deps_ready = False
                        break
                    
                    # Find dependency task and calculate start date
                    dep_task = None
                    for t in all_tasks:
                        if t.id == dep.to_task_id:
                            dep_task = t
                            break
                    
                    if dep_task and dep_task.end_date:
                        candidate_start = dep_task.end_date + timedelta(days=1)
                        if candidate_start > latest_end_date:
                            latest_end_date = candidate_start
                
                if all_deps_ready:
                    if task.start_date is None:
                        task.start_date = latest_end_date
                    task.calculate_dates(task.start_date)
                    scheduled_tasks.add(task.id)
                    progress_made = True
            
            if not progress_made:
                break
    
    def generate_xml(self, project: Project) -> str:
        """Generate GanttProject XML from a Project object"""
        # Ensure all task dates are calculated
        self._ensure_task_dates_calculated(project)
        
        # Create root element
        root = ET.Element("project")
        root.set("name", project.name)
        root.set("company", project.company)
        root.set("webLink", project.web_link)
        root.set("view-date", project.start_date.strftime('%Y-%m-%d'))
        root.set("view-index", "0")
        root.set("gantt-divider-location", str(project.gantt_divider_location))
        root.set("resource-divider-location", str(project.resource_divider_location))
        root.set("version", project.version)
        root.set("locale", project.locale)
        
        # Add description (with CDATA if present)
        description = ET.SubElement(root, "description")
        if project.description:
            description.text = project.description
            description.set("_cdata", "true")  # Mark for CDATA wrapping
        
        # Add view configuration
        self._add_view_config(root)
        
        # Add calendar configuration
        self._add_calendar_config(root, project)
        
        # Add tasks section
        self._add_tasks_section(root, project)
        
        # Add resources section
        self._add_resources_section(root, project)
        
        # Add allocations section
        self._add_allocations_section(root, project)
        
        # Add other required sections
        self._add_required_sections(root, project)
        
        # Format and return XML
        return self._format_xml(root)
    
    def _add_view_config(self, root: ET.Element):
        """Add view configuration"""
        view = ET.SubElement(root, "view")
        view.set("zooming-state", "default:6")
        view.set("id", "gantt-chart")
        
        # Add field definitions
        fields = [
            ("tpd3", "Name", "200", "0"),
            ("tpd4", "Begin date", "75", "1"),
            ("tpd5", "End date", "75", "2")
        ]
        
        for field_id, name, width, order in fields:
            field = ET.SubElement(view, "field")
            field.set("id", field_id)
            field.set("name", name)
            field.set("width", width)
            field.set("order", order)
    
    def _add_calendar_config(self, root: ET.Element, project: Project):
        """Add calendar configuration"""
        calendars = ET.SubElement(root, "calendars")
        
        # Add day types
        day_types = ET.SubElement(calendars, "day-types")
        for i in range(2):
            day_type = ET.SubElement(day_types, "day-type")
            day_type.set("id", str(i))
        
        # Add default week (0=Sunday, 1=Monday, etc.)
        default_week = ET.SubElement(calendars, "default-week")
        default_week.set("id", "1")
        default_week.set("name", "default")
        
        # Set working days (1=non-working, 0=working)
        days = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]
        for i, day in enumerate(days):
            # Default: weekends are non-working (1), weekdays are working (0)
            value = "1" if i in [0, 6] else "0"  # Sunday=0, Saturday=6
            default_week.set(day, value)
    
    def _add_tasks_section(self, root: ET.Element, project: Project):
        """Add tasks section with hierarchical structure"""
        tasks_root = ET.SubElement(root, "tasks")
        tasks_root.set("empty-milestones", "true")

        # Add task properties
        self._add_task_properties(tasks_root, project)

        # Reset ID mapping and build complete map first (so dependencies work)
        self.task_id_map = {}
        self.next_id = 0

        # First pass: Build task ID map for all tasks (including subtasks)
        all_items = project.tasks + project.milestones
        for item in all_items:
            self._build_task_id_map(item)

        # Second pass: Add all task elements with dependencies
        for item in all_items:
            self._add_task_element(tasks_root, item, project)

    def _build_task_id_map(self, task: Task):
        """Recursively build task ID map before adding elements"""
        if task.id not in self.task_id_map:
            self.task_id_map[task.id] = self.next_id
            self.next_id += 1

        # Process subtasks
        for subtask in task.subtasks:
            self._build_task_id_map(subtask)
    
    def _add_task_properties(self, tasks_root: ET.Element, project: Project):
        """Add task property definitions"""
        taskproperties = ET.SubElement(tasks_root, "taskproperties")

        # Default properties
        properties = [
            ("tpd0", "type", "default", "icon"),
            ("tpd1", "priority", "default", "icon"),
            ("tpd2", "info", "default", "icon"),
            ("tpd3", "name", "default", "text"),
            ("tpd4", "begindate", "default", "date"),
            ("tpd5", "enddate", "default", "date"),
            ("tpd6", "duration", "default", "int"),
            ("tpd7", "completion", "default", "int"),
            ("tpd8", "coordinator", "default", "text"),
            ("tpd9", "predecessorsr", "default", "text")
        ]

        for prop_id, name, prop_type, valuetype in properties:
            taskproperty = ET.SubElement(taskproperties, "taskproperty")
            taskproperty.set("id", prop_id)
            taskproperty.set("name", name)
            taskproperty.set("type", prop_type)
            taskproperty.set("valuetype", valuetype)

        # Custom properties
        for custom_prop in project.custom_task_properties:
            taskproperty = ET.SubElement(taskproperties, "taskproperty")
            taskproperty.set("id", custom_prop.id)
            taskproperty.set("name", custom_prop.name)
            taskproperty.set("type", "custom")
            taskproperty.set("valuetype", custom_prop.valuetype)
            if custom_prop.defaultvalue:
                taskproperty.set("defaultvalue", custom_prop.defaultvalue)

            # Add simple-select if present
            if custom_prop.simple_select is not None:
                simple_select = ET.SubElement(taskproperty, "simple-select")
                simple_select.set("select", custom_prop.simple_select)
    
    def _add_task_element(self, parent: ET.Element, task: Task, project: Project):
        """Add a task element and its subtasks recursively"""
        # Get the pre-assigned sequential ID from the map
        task_element = ET.SubElement(parent, "task")
        
        # Set basic attributes
        xml_id = str(self.task_id_map[task.id])
        task_element.set("id", xml_id)
        task_element.set("uid", task.uid)
        task_element.set("name", task.name)
        task_element.set("meeting", "true" if task.is_milestone else "false")
        task_element.set("complete", str(task.progress))
        task_element.set("expand", "true")
        
        # Set dates and duration
        if task.is_summary and task.subtasks:
            # Find earliest start and latest end from all descendants
            def get_all_leaf_tasks(t):
                if not t.subtasks:
                    return [t]
                leaves = []
                for st in t.subtasks:
                    leaves.extend(get_all_leaf_tasks(st))
                return leaves
            
            leaf_tasks = get_all_leaf_tasks(task)
            if leaf_tasks:
                earliest_start = min((t.start_date for t in leaf_tasks if t.start_date), default=task.start_date)
                if earliest_start:
                    task_element.set("start", earliest_start.strftime('%Y-%m-%d'))
            else:
                if task.start_date:
                    task_element.set("start", task.start_date.strftime('%Y-%m-%d'))
            # Summary tasks have duration of 0 in GanttProject
            task_element.set("duration", "0")
        else:
            if task.start_date:
                task_element.set("start", task.start_date.strftime('%Y-%m-%d'))
            task_element.set("duration", str(task.duration))
        
        # Set priority (only if not NORMAL/None)
        if task.priority is not None:
            task_element.set("priority", str(task.priority.value))

        # Set optional attributes
        if task.color:
            task_element.set("color", task.color)

        if task.shape:
            task_element.set("shape", task.shape)

        if task.web_link:
            from urllib.parse import quote
            task_element.set("webLink", quote(task.web_link, safe=''))

        if task.third_date:
            task_element.set("thirdDate", task.third_date.strftime('%Y-%m-%d'))

        if task.third_date_constraint is not None:
            task_element.set("thirdDate-constraint", str(task.third_date_constraint))

        # Add cost attributes (only if manual cost is set)
        if task.cost_manual_value is not None:
            task_element.set("cost-manual-value", str(task.cost_manual_value))
            task_element.set("cost-calculated", "true" if task.cost_calculated else "false")

        # Add notes if present (with CDATA wrapper for XML safety)
        if task.notes:
            notes_element = ET.SubElement(task_element, "notes")
            # Use text content - CDATA will be added in post-processing
            notes_element.text = task.notes
            # Mark element for CDATA wrapping
            notes_element.set("_cdata", "true")
        
        # Add custom properties
        for prop_id, prop_value in task.custom_properties.items():
            customproperty = ET.SubElement(task_element, "customproperty")
            customproperty.set("taskproperty-id", prop_id)
            customproperty.set("value", prop_value)
        
        # Add dependencies - stored in predecessor, pointing to successors
        # This task is a predecessor for these successor tasks
        for dependency in task.dependencies:
            successor_id = dependency.successor_id if hasattr(dependency, 'successor_id') else dependency.to_task_id
            if successor_id in self.task_id_map:
                depend = ET.SubElement(task_element, "depend")
                depend.set("id", str(self.task_id_map[successor_id]))
                depend.set("type", str(dependency.type.value))
                depend.set("difference", str(dependency.lag))
                depend.set("hardness", dependency.hardness if hasattr(dependency, 'hardness') else "Strong")
        
        # Add subtasks recursively (moved back to original position)
        for subtask in task.subtasks:
            self._add_task_element(task_element, subtask, project)
    
    def _add_resources_section(self, root: ET.Element, project: Project):
        """Add resources section"""
        resources_root = ET.SubElement(root, "resources")

        for resource in project.resources:
            resource_element = ET.SubElement(resources_root, "resource")
            resource_element.set("id", str(resource.id))
            resource_element.set("name", resource.name)
            resource_element.set("function", resource.function)
            resource_element.set("contacts", resource.contacts)
            resource_element.set("phone", resource.phone)

            # Add standard rate if specified
            if resource.standard_rate > 0:
                rate = ET.SubElement(resource_element, "rate")
                rate.set("name", "standard")
                rate.set("value", str(resource.standard_rate))
    
    def _add_allocations_section(self, root: ET.Element, project: Project):
        """Add resource allocations section"""
        allocations_root = ET.SubElement(root, "allocations")

        for alloc in project.allocations:
            # Only add if task ID has been mapped
            if alloc.task_id in self.task_id_map:
                allocation = ET.SubElement(allocations_root, "allocation")
                allocation.set("task-id", str(self.task_id_map[alloc.task_id]))
                allocation.set("resource-id", str(alloc.resource_id))
                allocation.set("function", alloc.function)
                allocation.set("responsible", 'true' if alloc.responsible else 'false')
                allocation.set("load", str(alloc.load))
    
    def _add_required_sections(self, root: ET.Element, project: Project):
        """Add other required sections"""
        # Add vacations
        vacations_root = ET.SubElement(root, "vacations")
        for vacation in project.vacations:
            vacation_elem = ET.SubElement(vacations_root, "vacation")
            vacation_elem.set("start", vacation.start_date.strftime('%Y-%m-%d'))
            vacation_elem.set("end", vacation.end_date.strftime('%Y-%m-%d'))
            vacation_elem.set("resourceid", str(vacation.resource_id))

        # Add previous (empty)
        ET.SubElement(root, "previous")

        # Add default roles element
        roles_default = ET.SubElement(root, "roles")
        roles_default.set("roleset-name", "Default")

        # Add roles with definitions
        if project.roles:
            roles = ET.SubElement(root, "roles")
            for role in project.roles:
                role_elem = ET.SubElement(roles, "role")
                role_elem.set("id", str(role.id))
                role_elem.set("name", role.name)
    
    def _format_xml(self, root: ET.Element) -> str:
        """Format XML with proper indentation and CDATA for notes and description"""
        import re

        # First, remove the _cdata marker attributes before serializing
        for elem in root.iter():
            if elem.get("_cdata") == "true":
                elem.attrib.pop("_cdata", None)

        rough_string = ET.tostring(root, 'unicode')

        # Wrap notes and description content in CDATA
        rough_string = re.sub(
            r'<notes>(.*?)</notes>',
            r'<notes><![CDATA[\1]]></notes>',
            rough_string,
            flags=re.DOTALL
        )
        rough_string = re.sub(
            r'<description>(.*?)</description>',
            r'<description><![CDATA[\1]]></description>',
            rough_string,
            flags=re.DOTALL
        )

        reparsed = minidom.parseString(rough_string)
        formatted = reparsed.toprettyxml(indent="  ")

        # Remove empty lines
        lines = [line for line in formatted.split('\\n') if line.strip()]
        return '\\n'.join(lines)
    
    def save_to_file(self, project: Project, filepath: str):
        """Generate XML and save to file"""
        xml_content = self.generate_xml(project)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"Successfully saved GanttProject file: {filepath}")
        print(f"Project: {project.name}")
        print(f"Tasks: {len(project.get_all_tasks())}")
        print(f"Resources: {len(project.resources)}")
        print(f"Milestones: {len(project.milestones)}")


class GanttProjectBuilder:
    """High-level builder for creating GanttProject files"""
    
    def __init__(self):
        self.generator = GanttGenerator()
    
    def from_markdown(self, markdown_path: str, output_path: str):
        """Create GanttProject file from markdown"""
        from .parser import MarkdownParser
        
        parser = MarkdownParser()
        project = parser.parse_file(markdown_path)
        self.generator.save_to_file(project, output_path)
        
        return project
    
    def from_python_package(self, package_path: str, output_path: str, 
                           start_date: Optional[datetime] = None):
        """Create GanttProject file from Python package analysis"""
        from .analyzer import PythonPackageAnalyzer
        from pathlib import Path
        
        analyzer = PythonPackageAnalyzer()
        analysis = analyzer.analyze_package(Path(package_path))
        
        project = analyzer.generate_gantt_project(
            analysis,
            start_date or datetime.now(),
            team_size=3
        )
        
        self.generator.save_to_file(project, output_path)
        return project
    
    def auto_analyze(self, project_path: str, output_path: str):
        """Auto-analyze project and create GanttProject file"""
        from .parser import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer()
        project = analyzer.analyze_project(project_path, "auto")
        self.generator.save_to_file(project, output_path)
        
        return project