# Task Attribute Analysis - Real GanttProject File

## Source
File: `test_all_task_attributes.gan`
Created: 2025-10-06
GanttProject Version: 3.3.3311

---

## CRITICAL CORRECTIONS

### 1. Dependency Type Numbers - CORRECTED ✅

**Previous (WRONG) mapping:**
```python
FINISH_TO_START = 1  # FS - WRONG!
START_TO_START = 2   # SS - WRONG!
FINISH_TO_FINISH = 3 # FF
START_TO_FINISH = 4  # SF
```

**CORRECT mapping from actual GanttProject file:**
```python
START_TO_START = 1   # SS ✓
FINISH_TO_START = 2  # FS ✓
FINISH_TO_FINISH = 3 # FF ✓
START_TO_FINISH = 4  # SF ✓
```

**Verified examples:**
- Task 8 → Task 10 (SS Dependent): `type="1"` = Start-to-Start
- Task 8 → Task 9 (FS Dependent): `type="2"` = Finish-to-Start
- Task 8 → Task 11 (FF Dependent): `type="3"` = Finish-to-Finish
- Task 8 → Task 12 (SF Dependent): `type="4"` = Start-to-Finish

### 2. Dependency Semantics - CONFIRMED ✅

The `<depend>` element is placed **inside the PREDECESSOR task** and points to the **SUCCESSOR task**.

```xml
<task id="8" name="Dependency Base Task">
    <depend id="9" type="2" difference="0" hardness="Strong"/>
</task>
```

**Meaning:** Task 8 has a successor (Task 9). Task 9 depends ON Task 8.

**Arrow direction:** Task 8 → Task 9

**Correct Python model:**
```python
class Task:
    successors: List['TaskDependency']  # Tasks that depend on THIS task
    # OR store as relationships in Project
```

---

## New Attributes Discovered

### 1. Task UID (Universally Unique Identifier)

Every task has a `uid` attribute - a UUID string:

```xml
<task id="1" uid="9e9dfb36c885438b9b4d4d0750d25fbd" name="Basic Task" .../>
<task id="2" uid="6e802b961ba2448f89251d28559a6951" name="Fully Configured Task" .../>
```

**Purpose:** Unique identifier that persists across file changes (unlike numeric `id`)

**Python model needs:**
```python
@dataclass
class Task:
    id: int  # Numeric ID (sequential)
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))  # UUID
```

### 2. Task Color

Hex color code:

```xml
<task id="2" color="#9933ff" .../>
<task id="3" color="#00cc66" .../>
```

**Already in Python model** ✅ but not in XML generator

### 3. Task Shape/Texture

Pattern for task bar appearance:

```xml
<task id="2" shape="1,0,0,0,1,0,0,0,1,0,0,0,1,1,1,1" .../>
```

**Format:** Comma-separated pattern (16 values, appears to be a texture bitmap)

**Python model needs:**
```python
shape: Optional[str] = None  # Pattern string
```

### 4. Web Link (URL Encoded)

```xml
<task id="2" webLink="https%3A%2F%2Fexample.com" .../>
```

**Format:** URL-encoded string (`%3A` = `:`, `%2F` = `/`)

**Already in Python model** ✅ but needs URL encoding in generator

### 5. Third Date Constraint

```xml
<task id="2" thirdDate="2025-11-03" thirdDate-constraint="1" .../>
```

**Purpose:** Task constraint (relates to "Earliest begin" checkbox)

**Possible values for `thirdDate-constraint`:**
- `0` = constraint disabled?
- `1` = constraint enabled?

**Need more examples to understand fully**

### 6. Task Complete (Progress)

Confirmed as integer percentage:

```xml
<task id="2" complete="50" .../>
<task id="3" complete="70" .../>
```

**Already correct in Python model** ✅

### 7. Task Priority

Confirmed mapping:

```xml
<task id="3" priority="4" .../>  <!-- Highest -->
<task id="18" priority="4" .../>  <!-- Highest Priority Task -->
<task id="2" priority="2" .../>  <!-- High (but shows as "2" not "3") -->
```

**Wait - there's a discrepancy here!**

Task 2 is named "Fully Configured Task" and should be High priority...
- Expected: `priority="3"` for High
- Actual: `priority="2"`

**Need to verify priority mapping:**
- Is `priority="2"` = High or Normal?
- Does GanttProject use 0-4 or 1-5?

### 8. Lag/Lead Time

Confirmed in dependencies:

```xml
<depend id="13" type="2" difference="3" hardness="Strong"/>   <!-- +3 days lag -->
<depend id="14" type="2" difference="-2" hardness="Strong"/>  <!-- -2 days lead -->
```

**Already correct in Python model** ✅

### 9. Link Hardness - Rubber vs Strong

Confirmed:

```xml
<depend id="15" type="2" difference="0" hardness="Rubber"/>  <!-- Flexible -->
```

**Already correct in documentation** ✅

---

## Task Hierarchy - Deep Nesting

Confirmed 4-level deep nesting works:

```xml
<task id="19" name="Parent Task">
    <task id="20" name="Child Task">
        <task id="21" name="Child Child Task">
            <task id="22" name="Child Child Child Task"/>
        </task>
    </task>
</task>
```

**No apparent depth limit** ✅

---

## View Configuration Attributes

### Timeline Feature

```xml
<timeline><![CDATA[0,3,2]]></timeline>
```

**Appears to reference task IDs shown in timeline view**

### Recent Colors

```xml
<option id="color.recent"><![CDATA[#00cc66 #9933ff]]></option>
```

**Color picker history**

### View Fields

```xml
<field id="tpd3" name="Name" width="200" order="0"/>
<field id="tpd4" name="Begin date" width="75" order="1"/>
<field id="tpd5" name="End date" width="75" order="2"/>
<field id="tpd15" name="Notes" width="20" order="3"/>
```

**Field `tpd15` = Notes column** (shown in task list)

---

## All Task Attributes Found

### Required Attributes

| Attribute | Type | Example | Python Field |
|-----------|------|---------|--------------|
| `id` | int | `1` | `id: int` |
| `uid` | UUID | `9e9dfb36c885438b9b4d4d0750d25fbd` | `uid: str` ⚠️ NEW |
| `name` | string | `"Basic Task"` | `name: str` |
| `meeting` | boolean | `true`/`false` | `is_milestone: bool` |
| `start` | date | `2025-10-03` | `start_date: datetime` |
| `duration` | int | `1` | `duration: int` |
| `complete` | int | `0` to `100` | `progress: int` |
| `expand` | boolean | `true`/`false` | ??? (UI state) |

### Optional Attributes

| Attribute | Type | Example | Python Field |
|-----------|------|---------|--------------|
| `color` | hex | `#9933ff` | `color: str` ✅ |
| `shape` | pattern | `1,0,0,0,1,0,0,0,1,0,0,0,1,1,1,1` | `shape: str` ⚠️ NEW |
| `webLink` | URL | `https%3A%2F%2Fexample.com` | `web_link: str` ✅ |
| `priority` | int | `0` to `4` | `priority: TaskPriority` ⚠️ VERIFY |
| `thirdDate` | date | `2025-11-03` | ??? ⚠️ NEW |
| `thirdDate-constraint` | int | `0`/`1` | ??? ⚠️ NEW |

---

## Dependencies - Complete Specification

### Attributes

```xml
<depend id="9" type="2" difference="0" hardness="Strong"/>
```

| Attribute | Type | Values | Meaning |
|-----------|------|--------|---------|
| `id` | int | Task ID | Successor task (task that depends on this) |
| `type` | int | 1, 2, 3, 4 | SS, FS, FF, SF |
| `difference` | int | ..., -2, 0, 3, ... | Lag (positive) or lead (negative) days |
| `hardness` | enum | `Strong`, `Rubber` | Link constraint strength |

### Placement

`<depend>` elements are **children of the PREDECESSOR task**.

---

## Missing from Sample File

These were NOT demonstrated in the file (still unknown):

- [ ] Notes element (mentioned in view but no `<notes>` element in tasks)
- [ ] Custom fields (`<customproperty>`)
- [ ] Multiple constraints (only saw `thirdDate-constraint="1"`)
- [ ] Different shape patterns (only saw one pattern)
- [ ] Show in timeline flag
- [ ] Cost attribute
- [ ] Task with end date explicitly set (vs calculated)

---

## Bugs Found in Current Python Implementation

### 🔴 CRITICAL

1. **Dependency type enum values are WRONG**
   - Current: `FINISH_TO_START = 1`
   - Should be: `FINISH_TO_START = 2`

2. **Dependency storage model is BACKWARDS**
   - Current: `Task.dependencies` (ambiguous)
   - Should be: `Task.successors` or store separately

### 🟡 MEDIUM

3. **Missing `uid` attribute**
   - Every task needs a UUID

4. **Priority mapping unclear**
   - Need to verify 0-4 mapping to UI labels

5. **URL encoding not applied to webLink**

6. **Color and webLink not in XML generator**

### 🟢 LOW

7. **Missing `shape` attribute**

8. **Missing `thirdDate` constraint attributes**

9. **Missing `expand` attribute** (UI state, less critical)

---

## Recommended Python Model Updates

```python
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DependencyType(Enum):
    """CORRECTED dependency types"""
    START_TO_START = 1       # SS
    FINISH_TO_START = 2      # FS
    FINISH_TO_FINISH = 3     # FF
    START_TO_FINISH = 4      # SF


@dataclass
class TaskDependency:
    """Dependency stored in PREDECESSOR task, pointing to SUCCESSOR"""
    successor_id: int  # Task that depends on the predecessor
    type: DependencyType = DependencyType.FINISH_TO_START
    lag: int = 0  # Positive = delay, negative = lead time
    hardness: str = "Strong"  # "Strong" or "Rubber"


@dataclass
class Task:
    id: int
    name: str
    duration: int

    # NEW: UUID
    uid: str = field(default_factory=lambda: str(uuid.uuid4()).replace('-', ''))

    # Dates
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Status
    progress: int = 0  # 0-100
    priority: int = 2  # 0-4, default = Normal (verify mapping!)
    is_milestone: bool = False

    # Dependencies - CORRECTED
    successors: List[TaskDependency] = field(default_factory=list)

    # Visual
    color: Optional[str] = None  # Hex: "#9933ff"
    shape: Optional[str] = None  # Pattern: "1,0,0,0,1,..."

    # Links & Notes
    web_link: Optional[str] = None  # Will be URL-encoded in XML
    notes: str = ""

    # Constraints - NEW
    third_date: Optional[datetime] = None
    third_date_constraint: Optional[int] = None  # 0 or 1?

    # Hierarchy
    parent_id: Optional[int] = None
    level: int = 0

    # UI State (less critical)
    expand: bool = True
```

---

## Next Steps

1. ✅ Fix DependencyType enum values (1=SS, 2=FS, 3=FF, 4=SF)
2. ✅ Add `uid` field to Task model
3. ✅ Add `shape`, `thirdDate`, `thirdDate-constraint` fields
4. ⚠️ Verify priority mapping (create test with all 5 priority levels)
5. ⚠️ Test notes functionality (add notes to a task and examine XML)
6. ⚠️ Fix dependency storage (predecessors vs successors)
7. ⚠️ Implement URL encoding for webLink
8. ⚠️ Add color/webLink to XML generator
9. ⚠️ Create XML parser (read .gan → Python objects)

---

*Analysis Version: 1.0*
*Date: 2025-10-06*
*Verified with real GanttProject 3.3.3311 file*
