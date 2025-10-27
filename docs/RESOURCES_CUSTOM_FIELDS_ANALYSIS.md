# Resources, Custom Fields, and Costs Analysis

## Source
File: `test_all_task_attributes.gan` (updated 2025-10-06)
GanttProject Version: 3.3.3311

---

## 1. Resources

### XML Structure

```xml
<resources>
    <resource id="0" name="Alex Developer" function="Default:1"
              contacts="alex@example.com" phone="+1 (555) 123-4567">
        <rate name="standard" value="40"/>
    </resource>
    <resource id="1" name="Dev One" function="1"
              contacts="dev1@example.com" phone="+1 (555) 234-5678">
        <rate name="standard" value="35"/>
    </resource>
    <resource id="2" name="Dev Two" function="3"
              contacts="dev2@example.com" phone="+1 (555) 345-6789">
        <rate name="standard" value="50"/>
    </resource>
</resources>
```

### Resource Attributes

| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| `id` | int | `0`, `1`, `2` | Sequential numeric ID |
| `name` | string | `"Alex Developer"` | Full name of resource |
| `function` | string | `"Default:1"`, `"1"`, `"3"` | Role/function ID or "Default:1" |
| `contacts` | string | `"alex@example.com"` | Email address |
| `phone` | string | `"+1 (555) 123-4567"` | Phone number |

### Function/Role Values

- `"Default:1"` - Default role (no specific role assigned)
- `"1"`, `"2"`, `"3"` - Role IDs (reference to `<roles>` definitions)

### Rate Child Element

```xml
<rate name="standard" value="40"/>
```

- `name="standard"` - Standard hourly rate
- `value` - Numeric rate value (presumably per hour)
- Could also have `name="overtime"` for overtime rates (not in this example)

---

## 2. Resource Allocations

### XML Structure

```xml
<allocations>
    <allocation task-id="1" resource-id="0" function="Default:1"
                responsible="false" load="30.0"/>
    <allocation task-id="4" resource-id="0" function="Default:1"
                responsible="false" load="60.0"/>
    <allocation task-id="7" resource-id="1" function="1"
                responsible="false" load="100.0"/>
    <allocation task-id="23" resource-id="2" function="3"
                responsible="false" load="100.0"/>
</allocations>
```

### Allocation Attributes

| Attribute | Type | Values | Notes |
|-----------|------|--------|-------|
| `task-id` | int | `1`, `4`, `7`, `23` | Task being assigned to |
| `resource-id` | int | `0`, `1`, `2` | Resource being assigned |
| `function` | string | `"Default:1"`, `"1"`, `"3"` | Role for this assignment |
| `responsible` | boolean | `true`, `false` | Is this resource responsible? |
| `load` | float | `30.0`, `60.0`, `100.0` | Allocation percentage |

### Key Observations

1. **Multiple allocations per resource**: Resource 0 is allocated to both Task 1 (30%) and Task 4 (60%)
2. **Load percentages**: Can be less than 100% (partial allocation) or 100% (full allocation)
3. **Responsible flag**: Marks primary responsibility (was `true` in older examples, `false` here)
4. **Function matches resource**: The `function` in allocation typically matches the resource's default function

---

## 3. Vacations (Resource Calendars)

### XML Structure

```xml
<vacations>
    <vacation start="2025-10-11" end="2025-10-13" resourceid="1"/>
    <vacation start="2025-10-18" end="2025-11-01" resourceid="1"/>
</vacations>
```

### Vacation Attributes

| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| `start` | date | `2025-10-11` | Vacation start date (ISO format) |
| `end` | date | `2025-10-13` | Vacation end date (ISO format) |
| `resourceid` | int | `1` | Resource ID taking vacation |

### Key Observations

- Multiple vacation periods per resource
- Date range is inclusive (start and end dates)
- Used for resource availability calculations

---

## 4. Roles

### XML Structure

```xml
<roles roleset-name="Default"/>
<roles>
    <role id="1" name="Researcher"/>
    <role id="2" name="Programmer"/>
    <role id="3" name="Fundraiser"/>
</roles>
```

### Interesting: Two `<roles>` Elements

1. **First element**: `<roles roleset-name="Default"/>` - Empty, references default roleset
2. **Second element**: `<roles>...</roles>` - Contains actual role definitions

### Role Attributes

| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| `id` | int | `1`, `2`, `3` | Role ID (referenced in resource `function`) |
| `name` | string | `"Researcher"` | Role display name |

---

## 5. Custom Task Properties (Custom Columns)

### Property Definitions in `<taskproperties>`

```xml
<taskproperties>
    <!-- Built-in properties (tpd0-tpd9) -->
    <taskproperty id="tpd0" name="type" type="default" valuetype="icon"/>
    ...

    <!-- Custom properties (tpc0, tpc1, etc.) -->
    <taskproperty id="tpc0" name="Text Column" type="custom" valuetype="text" defaultvalue="44"/>
    <taskproperty id="tpc1" name="Uid Column" type="custom" valuetype="text" defaultvalue="0">
        <simple-select select=""/>
    </taskproperty>
    <taskproperty id="tpc5" name="Int Column Cost" type="custom" valuetype="int" defaultvalue="0">
        <simple-select select="cost"/>
    </taskproperty>
    <taskproperty id="tpc6" name="Boolean Column" type="custom" valuetype="boolean" defaultvalue="true">
        <simple-select select="is_milestone"/>
    </taskproperty>
</taskproperties>
```

### Task Property Attributes

| Attribute | Type | Values | Notes |
|-----------|------|--------|-------|
| `id` | string | `tpc0`, `tpc1`, `tpc5`, `tpc6` | Custom IDs start with "tpc" |
| `name` | string | `"Text Column"` | Display name |
| `type` | enum | `"default"`, `"custom"` | Property type |
| `valuetype` | enum | `"text"`, `"int"`, `"boolean"`, `"icon"`, `"date"` | Data type |
| `defaultvalue` | string | `"44"`, `"0"`, `"true"` | Default value for new tasks |

### Value Types Observed

- `text` - String values
- `int` - Integer values
- `boolean` - true/false values
- `icon` - Built-in icons (for default properties)

**Likely also supported** (from GanttProject docs):
- `date` - Date values
- `double` - Floating-point numbers

### Simple-Select Element

```xml
<simple-select select="cost"/>
<simple-select select="is_milestone"/>
<simple-select select=""/>
```

**Purpose**: Links custom property to built-in task attributes
- `select="cost"` - Linked to task cost
- `select="is_milestone"` - Linked to milestone flag
- `select=""` - No linkage (standalone custom field)

---

## 6. Custom Property Values in Tasks

### XML Structure

```xml
<task id="1" uid="..." name="Basic Task" ...>
    <customproperty taskproperty-id="tpc0" value="44"/>
    <customproperty taskproperty-id="tpc1" value="uuid-here-4454-f4f4-etc"/>
    <customproperty taskproperty-id="tpc5" value="45"/>
    <customproperty taskproperty-id="tpc6" value="false"/>
</task>
```

### Custom Property Attributes

| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| `taskproperty-id` | string | `tpc0`, `tpc1` | References property definition |
| `value` | string | `"44"`, `"false"` | Value (stored as string, type from definition) |

### Key Observations

1. Values are **always stored as strings** in XML
2. Type interpretation comes from the property definition's `valuetype`
3. Boolean values are `"true"` or `"false"` (lowercase strings)
4. Numeric values are stored as numeric strings (`"45"`, `"100"`)

---

## 7. Task Costs

### Question: Where is Cost Stored?

Looking at the file, I see:
- Custom property: `"Int Column Cost"` with `<simple-select select="cost"/>`
- No direct `cost` attribute on `<task>` elements

**Two possibilities:**
1. **Cost is stored in custom properties only** (as shown)
2. **Cost can be a task attribute** (need example with built-in cost field)

**Question for user**: Did you set any "Cost" values on tasks using GanttProject's built-in cost field, or only through the custom column?

---

## 8. View Configuration (Bonus Discovery)

### Custom Column Display

```xml
<view zooming-state="default:2" id="gantt-chart">
    <field id="tpd3" name="Name" width="303" order="0"/>
    <field id="tpd4" name="Begin date" width="114" order="1"/>
    ...
    <field id="tpc0" name="Text Column" width="49" order="6"/>
    <field id="tpc1" name="Uid Column" width="50" order="7"/>
    <field id="tpc5" name="Int Column Cost" width="50" order="8"/>
    <field id="tpc6" name="Boolean Column" width="50" order="9"/>
</view>
```

Custom properties (`tpc0`, `tpc1`, etc.) appear as columns in the view configuration!

---

## Current Python Model Status

### Resource Model - Partially Implemented ✅

```python
@dataclass
class Resource:
    id: int
    name: str
    role: str = ""
    email: str = ""
    phone: str = ""
    standard_rate: float = 0.0
    overtime_rate: float = 0.0
    max_daily_hours: float = 8.0
    calendar_exceptions: List[datetime] = field(default_factory=list)
```

**Needs:**
- ✅ Has most fields
- ❌ `function` stored as `role` (different semantics)
- ❌ `contacts` stored as `email` (attribute name mismatch)
- ❌ No `overtime_rate` in XML examples (may not be used)
- ❌ `calendar_exceptions` doesn't match vacation structure

### Resource Allocation - Missing ❌

**Current approach**: Stored in Task
```python
resource_ids: List[int] = field(default_factory=list)
allocations: Dict[int, float] = field(default_factory=dict)
```

**Should be**: Separate Allocation model at Project level

### Custom Properties - Missing ❌

**Not implemented** in models

### Vacations - Partially Implemented

**Current**: `calendar_exceptions: List[datetime]` in Resource
**Should be**: Vacation periods with start/end dates

---

## Recommended Python Model Updates

### 1. ResourceAllocation Model (New)

```python
@dataclass
class ResourceAllocation:
    """Links a resource to a task with specific allocation parameters"""
    task_id: int
    resource_id: int
    function: str = "Default:1"  # Role for this assignment
    responsible: bool = False
    load: float = 100.0  # Allocation percentage
```

### 2. Vacation Model (New)

```python
@dataclass
class Vacation:
    """Resource vacation/unavailability period"""
    resource_id: int
    start_date: datetime
    end_date: datetime
```

### 3. Role Model (New)

```python
@dataclass
class Role:
    """Project role definition"""
    id: int
    name: str
```

### 4. CustomTaskProperty Model (New)

```python
@dataclass
class CustomTaskProperty:
    """Definition of a custom task property"""
    id: str  # e.g., "tpc0"
    name: str
    valuetype: str  # "text", "int", "boolean", "date", "double"
    defaultvalue: str = ""
    simple_select: Optional[str] = None  # Links to built-in property
```

### 5. Update Resource Model

```python
@dataclass
class Resource:
    id: int
    name: str
    function: str = "Default:1"  # Changed from role
    contacts: str = ""  # Changed from email
    phone: str = ""
    standard_rate: float = 0.0
    # Remove: overtime_rate (not seen in examples)
    # Remove: calendar_exceptions (replaced by Vacation)
```

### 6. Update Task Model

```python
@dataclass
class Task:
    # ... existing fields ...

    # Custom properties stored as dict
    custom_properties: Dict[str, str] = field(default_factory=dict)
    # Key = property ID (tpc0), Value = value as string
```

### 7. Update Project Model

```python
@dataclass
class Project:
    # ... existing fields ...

    # NEW: Resource allocations
    allocations: List[ResourceAllocation] = field(default_factory=list)

    # NEW: Vacations
    vacations: List[Vacation] = field(default_factory=list)

    # NEW: Roles
    roles: List[Role] = field(default_factory=list)

    # NEW: Custom property definitions
    custom_task_properties: List[CustomTaskProperty] = field(default_factory=list)
```

---

## Implementation Priority

### High Priority
1. ✅ Resource model updates
2. ✅ ResourceAllocation model and storage
3. ✅ Custom properties (definition and values)
4. ✅ XML generation for resources and allocations

### Medium Priority
5. ⚠️ Vacation model and storage
6. ⚠️ Role model and storage
7. ⚠️ XML generation for vacations and roles

### Low Priority
8. ⚠️ Cost handling (clarify storage mechanism first)
9. ⚠️ Resource calendar calculations
10. ⚠️ View configuration for custom columns

---

## Questions for User

1. **Task Cost**: Is there a built-in "Cost" field on tasks (separate from custom columns)? If so, please set it on a task so I can see the XML structure.

2. **Overtime Rates**: The Resource model has `overtime_rate` but I didn't see it in XML. Is this supported in GanttProject? If so, how do you set it?

3. **Resource Functions**: I see `function="Default:1"` and `function="1"`. Does this always reference role IDs, or is "Default:1" special?

---

*Analysis Version: 1.0*
*Date: 2025-10-06*
*Verified with GanttProject 3.3.3311*
