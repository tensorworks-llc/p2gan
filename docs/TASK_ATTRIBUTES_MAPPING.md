# GanttProject Task Attributes - Complete Mapping

## Source Information
Based on actual GanttProject application UI analysis (2025-10-06)

---

## Task Properties Overview

### General Tab

| UI Field | Data Type | XML Attribute | XML Example | Python Model Field | Notes |
|----------|-----------|---------------|-------------|-------------------|-------|
| **Name** | string | `name` | `name="Project Setup"` | `name: str` | Required. XML entities: `&` → `&amp;` |
| **Milestone** | Boolean | `meeting` | `meeting="true"` | `is_milestone: bool` | `true` for milestones, `false` for tasks |
| **Begin date** | date | `start` | `start="2025-10-01"` | `start_date: datetime` | ISO format YYYY-MM-DD |
| **End date** | date | ??? | ??? | `end_date: datetime` | Optional - may be calculated |
| **Duration** | float | `duration` | `duration="3"` | `duration: int` | Days. `0` for milestones/parent tasks |
| **Earliest begin** | Boolean | ??? | ??? | ??? | Checkbox - constraint type? |
| **Begin date** (constraint) | date | ??? | ??? | `constraint_date: datetime` | Depends on checkbox |
| **Priority** | enum | `priority` | `priority="3"` | `priority: TaskPriority` | 0=LOWEST, 1=LOW, 2=NORMAL, 3=HIGH, 4=HIGHEST |
| **Progress** | int (0-100) | `complete` | `complete="75"` | `progress: int` | Percentage |
| **Show in timeline** | Boolean | ??? | ??? | ??? | Not yet identified |
| **Shape** | texture | ??? | ??? | ??? | Visual display option |
| **Colors** | color | `color` | `color="#8cb6ce"` | `color: str` | Hex color code (not in sample files) |
| **Web Link** | URL | `webLink` | `webLink="https://..."` | `web_link: str` | Not in sample files |

### Additional Attributes (Not in UI but in XML)

| XML Attribute | Data Type | Example | Purpose |
|---------------|-----------|---------|---------|
| `id` | int | `id="5"` | Unique task identifier (auto-generated) |
| `expand` | Boolean | `expand="true"` | UI state - whether task is expanded in tree |

---

## Task Child Elements

### 1. Dependencies (`<depend>`)

From **Predecessors Tab** - shows tasks that THIS task depends on.

| UI Column | XML Attribute | Data Type | Values | Notes |
|-----------|---------------|-----------|--------|-------|
| **ID** | `id` | int | `2`, `5` | ID of the PREDECESSOR task (task being depended upon) |
| **Task name** | - | - | - | Display only (not in XML) |
| **Type** | `type` | int | `1`, `2`, `3`, `4` | 1=FS, 2=SS, 3=FF, 4=SF |
| **Delay** | `difference` | int | `0`, `5`, `-2` | Lag (positive) or lead (negative) in days |
| **Link hardness** | `hardness` | enum | `"Strong"`, `"Rubber"` | Constraint strength |

**Dependency Types:**
- `type="1"` - **Finish-to-Start (FS)**: Predecessor must finish before this task starts
- `type="2"` - **Start-to-Start (SS)**: Predecessor must start before this task starts
- `type="3"` - **Finish-to-Finish (FF)**: Predecessor must finish before this task finishes
- `type="4"` - **Start-to-Finish (SF)**: Predecessor must start before this task finishes (rare)

**Link Hardness:**
- `"Strong"` - Hard constraint (default)
- `"Rubber"` - Flexible constraint (allows scheduling flexibility)

**XML Structure:**
```xml
<task id="5" name="Frontend Implementation">
  <depend id="4" type="1" difference="0" hardness="Strong"/>
</task>
```
**Interpretation**: Task 5 depends ON Task 4 (Task 4 must finish before Task 5 starts)

### 2. Notes (`<notes>`)

```xml
<task id="31" name="Risk Mitigation">
  <notes>Detailed task notes here</notes>
</task>
```

### 3. Custom Fields (`<customproperty>`)

From **Custom Columns Tab** - user-defined fields.

```xml
<task id="5" name="...">
  <customproperty taskproperty-id="tpc1" value="Some value"/>
</task>
```

**Custom field definitions** (at project level):
```xml
<taskproperties>
  <!-- Built-in properties -->
  <taskproperty id="tpd0" name="type" type="default" valuetype="icon"/>
  ...
  <!-- Custom properties -->
  <taskproperty id="tpc1" name="Department" type="custom" valuetype="text"/>
  <taskproperty id="tpc2" name="Budget" type="custom" valuetype="double"/>
</taskproperties>
```

---

## Task Hierarchy (Nesting)

Tasks can contain child tasks through XML nesting:

```xml
<task id="0" name="Phase 1: Planning" duration="0">
  <task id="1" name="Project Setup" duration="3"/>
  <task id="2" name="Requirements Gathering" duration="5">
    <task id="20" name="User Interviews" duration="2"/>
  </task>
</task>
```

**Rules:**
- Parent tasks typically have `duration="0"` (calculated from children)
- Unlimited nesting depth
- Parent relationship is structural (no explicit parent_id attribute)

---

## Constraints (To Be Verified)

The **"Earliest begin"** checkbox with associated date likely maps to task constraints:

**Possible constraint types** (from GanttProject docs):
- As Soon As Possible (ASAP) - default
- As Late As Possible (ALAP)
- Must Start On (MSO)
- Must Finish On (MFO)
- Start No Earlier Than (SNET)
- Start No Later Than (SNLT)
- Finish No Earlier Than (FNET)
- Finish No Later Than (FNLT)

**Needs verification in actual .gan files created with constraints set**

---

## Current Implementation Status

### ✅ Correctly Implemented

- `id` - Unique identifier
- `name` - Task name
- `meeting` - Milestone flag
- `start` - Begin date
- `duration` - Duration in days
- `complete` - Progress percentage
- `priority` - Priority level (0-4)
- `expand` - Tree expansion state

### 🔴 CRITICAL ISSUES

#### 1. Dependency Semantics **INVERTED**

**Current Python Model (WRONG):**
```python
class Dependency:
    from_task_id: int  # Currently: task that creates the dependency
    to_task_id: int    # Currently: task being depended on
```

**Correct Interpretation:**
The `<depend>` element is placed **inside the dependent task**, and the `id` attribute points to the **predecessor**.

```xml
<task id="5" name="Frontend">
  <depend id="4" type="1" .../>  <!-- Task 5 depends ON Task 4 -->
</task>
```

**Should be:**
```python
class Dependency:
    dependent_task_id: int  # The task that HAS the dependency
    predecessor_task_id: int  # The task being depended upon (id in XML)
    type: DependencyType
    lag: int
```

**Or store in Task:**
```python
class Task:
    predecessors: List[Dependency]  # Tasks THIS task depends on
```

### 🟡 Partially Implemented

- `color` - Field exists, not in XML generation
- `web_link` - Field exists, not in XML generation
- `notes` - Not in model
- `end_date` - In model, but may be auto-calculated

### ❌ Not Implemented

- Constraints (earliest begin, etc.)
- Show in timeline flag
- Shape/texture
- Custom fields support
- End date handling (optional vs. calculated)
- Rubber link hardness (only "Strong" currently used)

---

## Recommended Python Model Updates

### Task Class Additions

```python
@dataclass
class Task:
    # Current attributes...

    # Add missing attributes:
    notes: str = ""
    show_in_timeline: bool = True  # To be verified
    shape: Optional[str] = None  # To be verified

    # Fix dependency storage:
    predecessors: List['TaskDependency'] = field(default_factory=list)
    # Remove: dependencies: List[Dependency]  (this was confusing)
```

### TaskDependency Class

```python
@dataclass
class TaskDependency:
    """Represents a task dependency - stored in the DEPENDENT task"""
    predecessor_id: int  # The task this depends ON
    type: DependencyType = DependencyType.FINISH_TO_START
    lag: int = 0  # Days (negative = lead time)
    hardness: str = "Strong"  # "Strong" or "Rubber"

    def to_xml_element(self) -> ET.Element:
        """Generate <depend> element"""
        return ET.Element('depend', {
            'id': str(self.predecessor_id),
            'type': str(self.type.value),
            'difference': str(self.lag),
            'hardness': self.hardness
        })
```

### Constraint Class (New)

```python
@dataclass
class TaskConstraint:
    """Task scheduling constraint"""
    type: ConstraintType  # ASAP, MSO, SNET, etc.
    date: Optional[datetime] = None  # For date-based constraints
```

---

## Testing Requirements

### Need .gan files created with GanttProject demonstrating:

1. **All dependency types:**
   - [ ] Finish-to-Start (FS)
   - [ ] Start-to-Start (SS)
   - [ ] Finish-to-Finish (FF)
   - [ ] Start-to-Finish (SF)

2. **Dependency features:**
   - [ ] Positive lag (delay)
   - [ ] Negative lag (lead time)
   - [ ] Strong vs. Rubber hardness

3. **Task attributes:**
   - [ ] Color assigned
   - [ ] Web link set
   - [ ] Notes added
   - [ ] Different shapes
   - [ ] Show in timeline unchecked

4. **Constraints:**
   - [ ] Earliest begin set
   - [ ] Different constraint types
   - [ ] End date manually set

5. **Custom fields:**
   - [ ] Text custom field
   - [ ] Number custom field
   - [ ] Date custom field

6. **Task types:**
   - [ ] Regular task
   - [ ] Milestone (0 duration)
   - [ ] Summary task (parent)
   - [ ] Task with subtasks

---

## Next Steps

1. **Fix dependency implementation** - critical bug
2. **Create test .gan files** from GanttProject app with all features
3. **Update Python models** based on verified attributes
4. **Implement XML parser** (read .gan → Python objects)
5. **Add missing attributes** to XML generator
6. **Comprehensive testing** of round-trip conversion

---

*Document Version: 1.0*
*Last Updated: 2025-10-06*
*Status: Initial analysis - requires verification with real GanttProject files*
