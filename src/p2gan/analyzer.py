"""
Project analyzer for automatically generating Gantt charts from code and documentation
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from .models import Project, Task, Resource, Milestone, TaskPriority, DependencyType
from .stakeholders import StakeholderManager


@dataclass
class ProjectAnalysis:
    """Results from analyzing a project"""
    name: str
    description: str
    components: List[str]
    dependencies: Dict[str, List[str]]
    complexity_score: float
    suggested_phases: List[Dict[str, Any]]
    estimated_duration_weeks: int
    required_skills: List[str]
    risks: List[str]


class PythonPackageAnalyzer:
    """Analyzes Python packages to generate project plans"""
    
    def __init__(self, stakeholder_manager: Optional[StakeholderManager] = None):
        self.stakeholder_manager = stakeholder_manager or StakeholderManager()
    
    def analyze_package(self, package_path: Path) -> ProjectAnalysis:
        """Analyze a Python package and return project analysis"""
        package_path = Path(package_path)
        
        # Extract package name
        package_name = package_path.name
        
        # Analyze structure
        components = self._find_components(package_path)
        dependencies = self._analyze_dependencies(package_path)
        complexity = self._calculate_complexity(package_path)
        
        # Read documentation
        description = self._extract_description(package_path)
        
        # Identify required skills
        required_skills = self._identify_required_skills(package_path)
        
        # Identify risks
        risks = self._identify_risks(package_path, components, dependencies)
        
        # Generate suggested phases
        phases = self._suggest_phases(components, dependencies, complexity)
        
        # Estimate duration
        duration = self._estimate_duration(complexity, len(components))
        
        return ProjectAnalysis(
            name=package_name,
            description=description,
            components=components,
            dependencies=dependencies,
            complexity_score=complexity,
            suggested_phases=phases,
            estimated_duration_weeks=duration,
            required_skills=required_skills,
            risks=risks
        )
    
    def _find_components(self, package_path: Path) -> List[str]:
        """Find major components in the package"""
        components = []
        
        # Find Python modules
        for py_file in package_path.glob("**/*.py"):
            if '__pycache__' not in str(py_file):
                relative_path = py_file.relative_to(package_path)
                components.append(f"Module: {relative_path}")
        
        # Find subpackages
        for subdir in package_path.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                if (subdir / '__init__.py').exists():
                    components.append(f"Package: {subdir.name}")
        
        # Find tests
        test_dirs = ['tests', 'test', 'testing']
        for test_dir in test_dirs:
            test_path = package_path / test_dir
            if test_path.exists():
                test_count = len(list(test_path.glob("**/*.py")))
                if test_count > 0:
                    components.append(f"Tests: {test_count} test files")
        
        # Find documentation
        doc_files = list(package_path.glob("**/*.md")) + list(package_path.glob("**/*.rst"))
        if doc_files:
            components.append(f"Documentation: {len(doc_files)} files")
        
        return components
    
    def _analyze_dependencies(self, package_path: Path) -> Dict[str, List[str]]:
        """Analyze import dependencies between modules"""
        dependencies = {}
        
        for py_file in package_path.glob("**/*.py"):
            if '__pycache__' in str(py_file):
                continue
            
            module_name = py_file.stem
            deps = self._extract_imports(py_file)
            if deps:
                dependencies[module_name] = deps
        
        return dependencies
    
    def _extract_imports(self, py_file: Path) -> List[str]:
        """Extract imports from a Python file"""
        imports = []
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass  # Ignore parsing errors
        
        return imports
    
    def _calculate_complexity(self, package_path: Path) -> float:
        """Calculate project complexity score"""
        score = 0.0
        
        # Count lines of code
        total_lines = 0
        for py_file in package_path.glob("**/*.py"):
            if '__pycache__' not in str(py_file):
                try:
                    with open(py_file, 'r') as f:
                        total_lines += len(f.readlines())
                except:
                    pass
        
        # Complexity based on LOC
        if total_lines < 500:
            score = 1.0  # Simple
        elif total_lines < 2000:
            score = 2.0  # Moderate
        elif total_lines < 10000:
            score = 3.0  # Complex
        else:
            score = 4.0  # Very Complex
        
        # Adjust for number of files
        file_count = len(list(package_path.glob("**/*.py")))
        if file_count > 50:
            score += 1.0
        
        return min(score, 5.0)
    
    def _extract_description(self, package_path: Path) -> str:
        """Extract project description from README or docstrings"""
        # Try README files
        for readme_name in ['README.md', 'README.rst', 'README.txt', 'README']:
            readme_path = package_path / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path, 'r') as f:
                        content = f.read()
                        # Get first paragraph
                        lines = content.split('\n\n')[0].split('\n')
                        # Skip headers
                        description_lines = [l for l in lines if not l.startswith('#')]
                        if description_lines:
                            return ' '.join(description_lines).strip()
                except:
                    pass
        
        # Try __init__.py docstring
        init_path = package_path / '__init__.py'
        if init_path.exists():
            try:
                with open(init_path, 'r') as f:
                    content = f.read()
                    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if match:
                        return match.group(1).strip()
            except:
                pass
        
        return f"Python package: {package_path.name}"
    
    def _identify_required_skills(self, package_path: Path) -> List[str]:
        """Identify required skills based on package analysis"""
        skills = set(['Python'])
        
        # Check for common frameworks/libraries
        for py_file in package_path.glob("**/*.py"):
            if '__pycache__' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                    # Check for common frameworks
                    if 'django' in content.lower():
                        skills.add('Django')
                    if 'flask' in content.lower():
                        skills.add('Flask')
                    if 'fastapi' in content.lower():
                        skills.add('FastAPI')
                    if 'sqlalchemy' in content.lower():
                        skills.add('SQLAlchemy')
                    if 'pandas' in content.lower():
                        skills.add('Pandas')
                    if 'numpy' in content.lower():
                        skills.add('NumPy')
                    if 'tensorflow' in content.lower() or 'torch' in content.lower():
                        skills.add('Machine Learning')
                    if 'async' in content or 'await' in content:
                        skills.add('Async Programming')
            except:
                pass
        
        # Check for test frameworks
        if (package_path / 'tests').exists() or (package_path / 'test').exists():
            skills.add('Testing')
            skills.add('pytest')
        
        # Check for documentation
        if list(package_path.glob("**/*.md")) or list(package_path.glob("**/*.rst")):
            skills.add('Documentation')
        
        return list(skills)
    
    def _identify_risks(self, package_path: Path, components: List[str], 
                       dependencies: Dict[str, List[str]]) -> List[str]:
        """Identify project risks"""
        risks = []
        
        # Check for missing tests
        has_tests = any('Tests:' in c for c in components)
        if not has_tests:
            risks.append("No test suite found - quality assurance risk")
        
        # Check for missing documentation
        has_docs = any('Documentation:' in c for c in components)
        if not has_docs:
            risks.append("Limited documentation - knowledge transfer risk")
        
        # Check for complex dependencies
        if len(dependencies) > 20:
            risks.append("Complex dependency structure - integration risk")
        
        # Check for TODO/FIXME comments
        todo_count = 0
        for py_file in package_path.glob("**/*.py"):
            if '__pycache__' not in str(py_file):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        todo_count += content.count('TODO') + content.count('FIXME')
                except:
                    pass
        
        if todo_count > 10:
            risks.append(f"Found {todo_count} TODO/FIXME comments - technical debt risk")
        
        return risks
    
    def _suggest_phases(self, components: List[str], dependencies: Dict[str, List[str]], 
                       complexity: float) -> List[Dict[str, Any]]:
        """Suggest project phases based on analysis"""
        phases = []
        
        # Phase 1: Analysis & Planning
        phases.append({
            'name': 'Analysis & Planning',
            'tasks': [
                'Code Review & Documentation',
                'Dependency Analysis',
                'Architecture Assessment',
                'Risk Assessment',
                'Development Plan Creation'
            ],
            'duration_days': max(3, int(complexity * 2))
        })
        
        # Phase 2: Setup & Infrastructure
        phases.append({
            'name': 'Setup & Infrastructure',
            'tasks': [
                'Development Environment Setup',
                'CI/CD Pipeline Configuration',
                'Testing Framework Setup',
                'Documentation System Setup'
            ],
            'duration_days': 5
        })
        
        # Phase 3: Core Development
        if 'Module:' in str(components):
            module_count = sum(1 for c in components if 'Module:' in c)
            phases.append({
                'name': 'Core Development',
                'tasks': [
                    f'Implement Core Modules ({module_count} modules)',
                    'Unit Test Development',
                    'Integration Implementation',
                    'Error Handling & Logging'
                ],
                'duration_days': max(10, int(module_count * complexity))
            })
        
        # Phase 4: Testing if no tests exist
        if not any('Tests:' in c for c in components):
            phases.append({
                'name': 'Testing Implementation',
                'tasks': [
                    'Unit Test Creation',
                    'Integration Test Development',
                    'Test Coverage Analysis',
                    'Bug Fixing'
                ],
                'duration_days': max(5, int(complexity * 3))
            })
        
        # Phase 5: Documentation if limited
        if not any('Documentation:' in c for c in components):
            phases.append({
                'name': 'Documentation',
                'tasks': [
                    'API Documentation',
                    'User Guide Creation',
                    'Developer Documentation',
                    'Example Code Creation'
                ],
                'duration_days': max(3, int(complexity * 2))
            })
        
        # Phase 6: Optimization & Polish
        phases.append({
            'name': 'Optimization & Polish',
            'tasks': [
                'Performance Optimization',
                'Code Refactoring',
                'Security Review',
                'Final Testing'
            ],
            'duration_days': 5
        })
        
        # Phase 7: Deployment
        phases.append({
            'name': 'Deployment & Release',
            'tasks': [
                'Deployment Preparation',
                'Production Testing',
                'Release Documentation',
                'Post-Release Monitoring'
            ],
            'duration_days': 3
        })
        
        return phases
    
    def _estimate_duration(self, complexity: float, component_count: int) -> int:
        """Estimate project duration in weeks"""
        base_weeks = 2  # Minimum project duration
        
        # Add weeks based on complexity
        complexity_weeks = int(complexity * 2)
        
        # Add weeks based on component count
        component_weeks = component_count // 10
        
        return base_weeks + complexity_weeks + component_weeks
    
    def generate_gantt_project(self, analysis: ProjectAnalysis, 
                              start_date: datetime,
                              team_size: int = 3) -> Project:
        """Generate a GanttProject from analysis results"""
        project = Project(
            name=f"{analysis.name} Development",
            start_date=start_date,
            description=analysis.description
        )
        
        # Suggest team based on required skills
        suggested_team = self.stakeholder_manager.suggest_team(
            analysis.required_skills, 
            team_size
        )
        
        # Add resources
        resource_map = {}
        for i, stakeholder in enumerate(suggested_team):
            resource = Resource(
                id=i,
                name=stakeholder.name,
                role=stakeholder.role,
                email=stakeholder.email
            )
            project.add_resource(resource)
            resource_map[stakeholder.name] = resource
        
        # If not enough stakeholders, create generic ones
        if len(suggested_team) < team_size:
            for i in range(len(suggested_team), team_size):
                resource = Resource(
                    id=i,
                    name=f"Developer {i+1}",
                    role="Developer"
                )
                project.add_resource(resource)
        
        # Create tasks from phases
        task_id = 0
        current_date = start_date
        previous_phase = None
        
        for phase_data in analysis.suggested_phases:
            # Create phase as parent task
            phase = Task(
                id=task_id,
                name=phase_data['name'],
                duration=0,  # Summary task
                start_date=current_date,
                is_summary=True
            )
            task_id += 1
            
            # Add dependency on previous phase
            if previous_phase:
                phase.add_dependency(previous_phase.id)
            
            # Create subtasks
            phase_duration = 0
            for task_name in phase_data['tasks']:
                # Estimate task duration
                task_duration = max(1, phase_data['duration_days'] // len(phase_data['tasks']))
                
                subtask = Task(
                    id=task_id,
                    name=task_name,
                    duration=task_duration,
                    start_date=current_date,
                    parent_id=phase.id
                )
                
                # Assign resource (round-robin)
                if project.resources:
                    subtask.resource_ids.append(task_id % len(project.resources))
                
                phase.add_subtask(subtask)
                task_id += 1
                phase_duration += task_duration
            
            project.add_task(phase)
            
            # Update dates
            current_date += timedelta(days=phase_duration)
            previous_phase = phase
        
        # Add milestones
        for i, phase in enumerate(project.tasks):
            milestone = Milestone(
                id=task_id,
                name=f"{phase.name} Complete",
                date=phase.end_date or current_date
            )
            milestone.add_dependency(phase.id)
            project.add_milestone(milestone)
            task_id += 1
        
        # Add risks as notes
        if analysis.risks:
            risk_task = Task(
                id=task_id,
                name="Risk Mitigation",
                duration=5,
                notes="\n".join(analysis.risks),
                priority=TaskPriority.HIGH
            )
            project.add_task(risk_task)
        
        return project