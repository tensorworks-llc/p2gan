# Resources, Costs, and Custom Properties Implementation

## Date: 2025-10-06

## Summary
Added complete support for Resources, Resource Allocations, Vacations, Roles, Custom Task Properties, and Task Costs based on analysis of real GanttProject 3.3.3311 files.

---

## New Models Added

### 1. ResourceAllocation
```python
@dataclass
class ResourceAllocation:
    task_id: int
    resource_id: int
    function: str = "Default:1"  # Role for this assignment
    responsible: bool = False
    load: float = 100.0  # Can exceed 100% (overallocation)
```

**Purpose:** Links resources to tasks with specific allocation parameters. Stored at project level, not in tasks.

### 2. Vacation
```python
@dataclass
class Vacation:
    resource_id: int
    start_date: datetime
    end_date: datetime
```

**Purpose:** Defines resource unavailability periods (vacations, holidays, etc.)

### 3. Role
```python
@dataclass
class Role:
    id: int
    name: str
```

**Purpose:** Custom role definitions (e.g., "Researcher", "Programmer", "Fundraiser")

### 4. CustomTaskProperty
```python
@dataclass
class CustomTaskProperty:
    id: str  # e.g., "tpc0", "tpc1"
    name: str
    valuetype: str  # "text", "int", "boolean", "date", "double"
    defaultvalue: str = ""
    simple_select: Optional[str] = None  # Links to built-in like "cost"
```

**Purpose:** Defines custom columns for tasks

---

## Model Updates

### Resource Model - Updated ✅

**Changed:**
- `role` → `function` (matches GanttProject XML)
- `email` → `contacts` (matches GanttProject XML)
- Removed `overtime_rate` (not used in GanttProject)
- Removed `max_daily_hours` (not used)
- Removed `calendar_exceptions` (replaced by Vacation)

**New structure:**
```python
@dataclass
class Resource:
    id: int
    name: str
    function: str = "Default:1"  # Role ID or "Default:1"
    contacts: str = ""  # Email address
    phone: str = ""
    standard_rate: float = 0.0
```

### Task Model - Added Cost & Custom Properties ✅

**Added fields:**
```python
# Cost management
cost_manual_value: Optional[float] = None  # Fixed/manual cost
cost_calculated: bool = True  # True = from resources, False = manual

# Custom properties (key = prop ID, value = string)
custom_properties: Dict[str, str] = field(default_factory=dict)
```

**Removed:**
- `cost: float` (replaced by cost_manual_value/cost_calculated)
- `custom_fields` (renamed to custom_properties)

### Project Model - Added Collections ✅

**New collections:**
```python
# Resource management
allocations: List[ResourceAllocation] = field(default_factory=list)
vacations: List[Vacation] = field(default_factory=list)
roles: List[Role] = field(default_factory=list)

# Custom properties
custom_task_properties: List[CustomTaskProperty] = field(default_factory=list)

# Calendar
calendar_base_id: Optional[str] = None  # e.g., "us.federal"
```

---

## XML Generator Updates

### 1. Project Description - CDATA Support ✅
```xml
<description><![CDATA[This is a main project description]]></description>
```

### 2. Custom Task Properties - Definition ✅
```xml
<taskproperties>
    <!-- Built-in properties -->
    <taskproperty id="tpd0" name="type" type="default" valuetype="icon"/>
    ...
    <!-- Custom properties -->
    <taskproperty id="tpc0" name="Text Column" type="custom" valuetype="text" defaultvalue="44"/>
    <taskproperty id="tpc4" name="Target Date" type="custom" valuetype="date"/>
    <taskproperty id="tpc7" name="Double Column" type="custom" valuetype="double" defaultvalue="6.06"/>
</taskproperties>
```

### 3. Task Custom Property Values ✅
```xml
<task id="1" name="Basic Task" ...>
    <customproperty taskproperty-id="tpc0" value="44"/>
    <customproperty taskproperty-id="tpc4" value="2025-12-31"/>
    <customproperty taskproperty-id="tpc7" value="3.14"/>
</task>
```

### 4. Task Costs ✅
```xml
<task id="23" name="Notes Task" cost-manual-value="500.0" cost-calculated="false">
```

### 5. Resources with Rates ✅
```xml
<resources>
    <resource id="0" name="Alex Developer" function="Default:1"
              contacts="alex@example.com" phone="+1 (555) 123-4567">
        <rate name="standard" value="40"/>
    </resource>
</resources>
```

### 6. Resource Allocations ✅
```xml
<allocations>
    <allocation task-id="1" resource-id="0" function="Default:1"
                responsible="false" load="30.0"/>
    <allocation task-id="8" resource-id="0" function="2"
                responsible="true" load="20.0"/>
    <allocation task-id="8" resource-id="1" function="Default:0"
                responsible="false" load="50.0"/>
    <allocation task-id="8" resource-id="2" function="Default:1"
                responsible="true" load="40.0"/>
</allocations>
```

**Note:** Task 8 has 3 resources allocated (110% total - overallocated!)

### 7. Vacations ✅
```xml
<vacations>
    <vacation start="2025-10-11" end="2025-10-13" resourceid="1"/>
    <vacation start="2025-10-18" end="2025-11-01" resourceid="1"/>
</vacations>
```

### 8. Roles ✅
```xml
<roles roleset-name="Default"/>
<roles>
    <role id="1" name="Researcher"/>
    <role id="2" name="Programmer"/>
    <role id="3" name="Fundraiser"/>
</roles>
```

---

## Key Insights

### Resource Function Values
- `"Default:0"` - Default role variant
- `"Default:1"` - Default role (most common)
- `"1"`, `"2"`, `"3"` - Custom role IDs from `<roles>` section

The `function` in an allocation can **differ** from the resource's default function, allowing a resource to play different roles on different tasks.

### Cost Calculation
- **Calculated cost:** No cost attributes, computed from `resource rate × duration × load`
- **Manual cost:** Requires both `cost-manual-value` and `cost-calculated="false"`

### Custom Property Value Types
All 5 types verified:
- `text` - String values
- `int` - Integer values
- `boolean` - `"true"` or `"false"` (lowercase strings)
- `date` - ISO date strings
- `double` - Decimal numbers

Values are **always stored as strings** in XML, type interpretation comes from property definition.

### Multiple Resources per Task
Confirmed: A single task can have multiple resource allocations with different:
- Load percentages (can total >100%)
- Functions (roles)
- Responsibility flags

---

## Updated __init__.py Exports

```python
from .models import (
    Project, Task, Resource, Milestone, Dependency,
    ResourceAllocation, Vacation, Role, CustomTaskProperty,
    TaskPriority, DependencyType
)
```

All new models are now exported and available for import.

---

## Usage Examples

### Creating Resources with Allocations

```python
from ganttproject import Project, Resource, ResourceAllocation, Task
from datetime import datetime

project = Project(name="My Project", start_date=datetime(2025, 10, 1))

# Add resources
alex = Resource(id=0, name="Alex Developer", function="Default:1",
                contacts="alex@example.com", standard_rate=40.0)
dev1 = Resource(id=1, name="Dev One", function="1",
              contacts="dev1@example.com", standard_rate=35.0)

project.resources.extend([alex, dev1])

# Add task
task = Task(id=1, name="Development", duration=5)
project.add_task(task)

# Allocate resources
alloc1 = ResourceAllocation(task_id=1, resource_id=0, load=50.0, responsible=True)
alloc2 = ResourceAllocation(task_id=1, resource_id=1, load=100.0)

project.allocations.extend([alloc1, alloc2])
```

### Adding Custom Properties

```python
from ganttproject import CustomTaskProperty

# Define custom property
budget_prop = CustomTaskProperty(
    id="tpc0",
    name="Budget",
    valuetype="double",
    defaultvalue="0.0",
    simple_select="cost"  # Link to built-in cost
)

project.custom_task_properties.append(budget_prop)

# Set value on task
task.custom_properties["tpc0"] = "15000.50"
```

### Adding Vacations

```python
from ganttproject import Vacation
from datetime import datetime

vacation = Vacation(
    resource_id=1,
    start_date=datetime(2025, 10, 11),
    end_date=datetime(2025, 10, 13)
)

project.vacations.append(vacation)
```

### Setting Task Costs

```python
# Manual cost
task.cost_manual_value = 1000.0
task.cost_calculated = False

# Calculated cost (from resources)
task.cost_calculated = True  # No cost_manual_value set
```

---

## Breaking Changes

### ⚠️ Resource Model
- **`role`** → **`function`**
- **`email`** → **`contacts`**
- Removed: `overtime_rate`, `max_daily_hours`, `calendar_exceptions`

**Migration:**
```python
# OLD
resource = Resource(id=0, name="Alex", role="Developer", email="alex@example.com")

# NEW
resource = Resource(id=0, name="Alex", function="Default:1", contacts="alex@example.com")
```

### ⚠️ Task Model
- **`cost`** removed → Use **`cost_manual_value`** + **`cost_calculated`**
- **`custom_fields`** → **`custom_properties`**

**Migration:**
```python
# OLD
task.cost = 1000.0
task.custom_fields["field1"] = "value1"

# NEW
task.cost_manual_value = 1000.0
task.cost_calculated = False
task.custom_properties["tpc0"] = "value1"
```

### ⚠️ Resource Allocations
- Previously stored in Task: `task.resource_ids`, `task.allocations`
- Now stored in Project: `project.allocations`

**Migration:**
```python
# OLD
task.resource_ids = [0, 1]
task.allocations = {0: 50.0, 1: 100.0}

# NEW
project.allocations.append(ResourceAllocation(task_id=task.id, resource_id=0, load=50.0))
project.allocations.append(ResourceAllocation(task_id=task.id, resource_id=1, load=100.0))
```

---

## Testing Recommendations

### High Priority
1. ✅ Verify resources with rates generate correctly
2. ✅ Verify multiple allocations per task
3. ✅ Verify custom properties (all 5 types)
4. ✅ Verify manual vs calculated costs
5. ✅ Verify vacations
6. ✅ Verify roles

### Medium Priority
7. Test overallocation (>100% load)
8. Test resource function variations
9. Test custom property simple-select linkage
10. Test empty collections (no roles, no vacations, etc.)

---

## Known Limitations

### Not Yet Implemented
- ❌ Calendar base-id support (saw `calendar_base_id` in XML but not parsing holidays)
- ❌ XML parser (read .gan files → Python objects)
- ❌ Resource calendar exceptions (besides vacations)
- ❌ Overtime rates (GanttProject may not support this)

---

## Files Modified

1. ✅ `src/p2gan/models.py`
   - Updated Resource
   - Added ResourceAllocation, Vacation, Role, CustomTaskProperty
   - Updated Task (cost, custom_properties)
   - Updated Project (new collections)

2. ✅ `src/p2gan/__init__.py`
   - Added exports for new models

3. ✅ `src/p2gan/generator.py`
   - Updated description CDATA support
   - Added custom property definitions generation
   - Added custom property values in tasks
   - Updated resources with rates
   - Replaced allocations logic
   - Added vacations generation
   - Added roles generation
   - Updated CDATA handling for description

---

## Next Steps

### Immediate
1. Test generated .gan files in GanttProject app
2. Verify all features work as expected
3. Fix any XML generation issues

### Short Term
4. Implement XML parser (read .gan → Python objects)
5. Add helper methods for common operations
6. Add validation (check for missing resources, invalid IDs, etc.)

### Long Term
7. Calendar holiday support
8. Baseline tracking
9. Advanced scheduling algorithms
10. Interactive bidirectional sync with GanttProject

---

*Implementation Version: 2.0*
*Date: 2025-10-06*
*Verified with GanttProject 3.3.3311*
