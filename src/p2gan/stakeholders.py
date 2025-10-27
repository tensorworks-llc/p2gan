"""
Stakeholder management system for project resource allocation
"""

import json
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Stakeholder:
    """Represents a project stakeholder who can be assigned to tasks"""
    name: str
    role: str
    email: str = ""
    phone: str = ""
    department: str = ""
    skills: List[str] = field(default_factory=list)
    availability: float = 1.0  # 0.0 to 1.0 (percentage of time available)
    standard_rate: float = 0.0
    overtime_rate: float = 0.0
    projects: Set[str] = field(default_factory=set)  # Projects involved in
    aliases: List[str] = field(default_factory=list)  # Alternative names
    
    def matches_name(self, name: str) -> bool:
        """Check if a name matches this stakeholder"""
        name_lower = name.lower()
        if name_lower == self.name.lower():
            return True
        return any(alias.lower() == name_lower for alias in self.aliases)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['projects'] = list(self.projects)  # Convert set to list
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Stakeholder':
        """Create from dictionary"""
        data['projects'] = set(data.get('projects', []))
        return cls(**data)


class StakeholderManager:
    """Manages a cache of stakeholders across projects"""
    
    DEFAULT_CACHE_PATH = Path.home() / '.p2gan' / 'stakeholders.json'
    
    def __init__(self, cache_path: Optional[Path] = None):
        """Initialize stakeholder manager with optional custom cache path"""
        self.cache_path = cache_path or self.DEFAULT_CACHE_PATH
        self.stakeholders: Dict[str, Stakeholder] = {}
        self.load_cache()
    
    def load_cache(self):
        """Load stakeholder cache from disk"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r') as f:
                    data = json.load(f)
                    for name, stakeholder_data in data.items():
                        self.stakeholders[name] = Stakeholder.from_dict(stakeholder_data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load stakeholder cache: {e}")
                self.stakeholders = {}
        else:
            # Create directory if it doesn't exist
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_cache(self):
        """Save stakeholder cache to disk"""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {name: s.to_dict() for name, s in self.stakeholders.items()}
        with open(self.cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_stakeholder(self, stakeholder: Stakeholder) -> Stakeholder:
        """Add or update a stakeholder in the cache"""
        self.stakeholders[stakeholder.name] = stakeholder
        self.save_cache()
        return stakeholder
    
    def get_stakeholder(self, name: str) -> Optional[Stakeholder]:
        """Get a stakeholder by name or alias"""
        # Direct lookup
        if name in self.stakeholders:
            return self.stakeholders[name]
        
        # Search by alias
        for stakeholder in self.stakeholders.values():
            if stakeholder.matches_name(name):
                return stakeholder
        
        return None
    
    def find_or_create(self, name: str, role: str = "", **kwargs) -> Stakeholder:
        """Find existing stakeholder or create new one"""
        stakeholder = self.get_stakeholder(name)
        if not stakeholder:
            stakeholder = Stakeholder(name=name, role=role, **kwargs)
            self.add_stakeholder(stakeholder)
        return stakeholder
    
    def list_stakeholders(self, project: Optional[str] = None, 
                         role: Optional[str] = None,
                         department: Optional[str] = None) -> List[Stakeholder]:
        """List stakeholders with optional filters"""
        results = list(self.stakeholders.values())
        
        if project:
            results = [s for s in results if project in s.projects]
        if role:
            results = [s for s in results if s.role == role]
        if department:
            results = [s for s in results if s.department == department]
        
        return results
    
    def get_available_stakeholders(self, min_availability: float = 0.5) -> List[Stakeholder]:
        """Get stakeholders with sufficient availability"""
        return [s for s in self.stakeholders.values() 
                if s.availability >= min_availability]
    
    def assign_to_project(self, stakeholder_name: str, project_name: str):
        """Assign a stakeholder to a project"""
        stakeholder = self.get_stakeholder(stakeholder_name)
        if stakeholder:
            stakeholder.projects.add(project_name)
            self.save_cache()
    
    def import_from_markdown(self, markdown_content: str, project_name: str):
        """Import stakeholders from markdown resource section"""
        import re
        
        # Look for Resources section
        resources_section = re.search(
            r'## Resources\s*\n((?:- .*\n?)*)',
            markdown_content,
            re.MULTILINE
        )
        
        if resources_section:
            resources_text = resources_section.group(1)
            
            # Parse each resource line: - Name (Role)
            for line in resources_text.split('\n'):
                match = re.match(r'^- ([^(]+)\s*(?:\(([^)]+)\))?', line.strip())
                if match:
                    name = match.group(1).strip()
                    role = match.group(2).strip() if match.group(2) else ""
                    
                    stakeholder = self.find_or_create(name=name, role=role)
                    stakeholder.projects.add(project_name)
            
            self.save_cache()
    
    def suggest_team(self, required_skills: List[str], 
                     team_size: int = 5) -> List[Stakeholder]:
        """Suggest a team based on required skills"""
        scored_stakeholders = []
        
        for stakeholder in self.stakeholders.values():
            if stakeholder.availability < 0.2:  # Skip unavailable
                continue
            
            # Score based on skill match
            skill_matches = sum(1 for skill in required_skills 
                              if skill.lower() in [s.lower() for s in stakeholder.skills])
            
            if skill_matches > 0:
                score = skill_matches * stakeholder.availability
                scored_stakeholders.append((score, stakeholder))
        
        # Sort by score and return top N
        scored_stakeholders.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored_stakeholders[:team_size]]
    
    def export_to_csv(self, filepath: str):
        """Export stakeholder list to CSV"""
        import csv
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Name', 'Role', 'Email', 'Phone', 'Department',
                'Skills', 'Availability', 'Projects'
            ])
            
            for stakeholder in self.stakeholders.values():
                writer.writerow([
                    stakeholder.name,
                    stakeholder.role,
                    stakeholder.email,
                    stakeholder.phone,
                    stakeholder.department,
                    ', '.join(stakeholder.skills),
                    f"{stakeholder.availability * 100}%",
                    ', '.join(stakeholder.projects)
                ])
    
    def merge_with(self, other_manager: 'StakeholderManager'):
        """Merge another stakeholder manager's data"""
        for name, stakeholder in other_manager.stakeholders.items():
            if name in self.stakeholders:
                # Merge projects and update other fields if newer
                self.stakeholders[name].projects.update(stakeholder.projects)
            else:
                self.stakeholders[name] = stakeholder
        
        self.save_cache()


# Default instance for convenience
_default_manager = None

def get_default_manager() -> StakeholderManager:
    """Get or create the default stakeholder manager"""
    global _default_manager
    if _default_manager is None:
        _default_manager = StakeholderManager()
    return _default_manager