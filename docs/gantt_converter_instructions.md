# Markdown to GanttProject Converter Instructions

## Overview
This document provides detailed instructions for creating a utility that converts structured markdown project files into GanttProject-compatible XML files (.gan format). Use these instructions to implement a converter that can parse project roadmaps and timelines from markdown and generate valid GanttProject files.

## Input Format Specification

### Markdown Structure
The input markdown file should follow this standardized structure:

```markdown
# Project: [Project Name]
**Start Date:** YYYY-MM-DD
**Duration:** X weeks

## Resources
- [Name] ([Role])
- [Name] ([Role])

## Tasks
### [Phase Name]
- **[Task Name]** ([duration] days, [Resource Name])
  - Start: [YYYY-MM-DD] OR "After [Task Name]"
  - Dependencies: [Task Name 1], [Task Name 2]
  - Priority: [High|Medium|Low]
  - Progress: [0-100]%

## Milestones
- [ ] [Milestone Name] ([YYYY-MM-DD])
```

### Parsing Rules

1. **Project Metadata:**
   - Extract project name from `# Project: [Name]` header
   - Parse start date from `**Start Date:** YYYY-MM-DD` format
   - Extract duration from `**Duration:** X weeks/days` format

2. **Resources Section:**
   - Each line starting with `-` defines a resource
   - Format: `- [Full Name] ([Role/Title])`
   - Assign sequential integer IDs starting from 0
   - Store name-to-ID mapping for task assignments

3. **Tasks Section:**
   - `###` headers define project phases (parent tasks with 0 duration)
   - Lines starting with `- **[Task Name]**` define individual tasks
   - Parse parenthetical content for duration and resource assignment
   - Support sub-bullets for additional task properties:
     - `Start:` - absolute date or relative to another task
     - `Dependencies:` - comma-separated list of prerequisite tasks
     - `Priority:` - High/Medium/Low priority level
     - `Progress:` - completion percentage (0-100)

4. **Milestones Section:**
   - Lines starting with `- [ ]` define milestones
   - Extract milestone name and target date
   - Create as zero-duration tasks marked as meetings

## Date Calculation Logic

### Sequential Scheduling (Default)
If no specific start dates or dependencies are provided:
1. Start all tasks sequentially from project start date
2. Each task begins after the previous task ends
3. Skip weekends (add 2 days for each weekend crossed)

### Dependency-Based Scheduling
When dependencies are specified:
1. Parse dependency strings to identify prerequisite tasks
2. Calculate start date as the latest end date of all dependencies + 1 day
3. Respect dependency chains and detect circular dependencies
4. Issue warnings for unresolvable dependencies

### Date Parsing
- Support absolute dates in YYYY-MM-DD format
- Support relative references like "After [Task Name]"
- Handle business day calculations (skip weekends)
- Default to project start date if no start date specified

## GanttProject XML Structure

### Root Element
```xml
<project name="[Project Name]" 
         company="" 
         webLink="" 
         view-date="[Start Date]" 
         view-index="0" 
         gantt-divider-location="300" 
         resource-divider-location="300" 
         version="3.2.3200" 
         locale="en_US">
```

### Required Child Elements

1. **Description:** `<description></description>` (can be empty)

2. **View Configuration:**
```xml
<view zooming-state="default:6" id="gantt-chart">
  <field id="tpd3" name="Name" width="200" order="0"/>
  <field id="tpd4" name="Begin date" width="75" order="1"/>
  <field id="tpd5" name="End date" width="75" order="2"/>
</view>
```

3. **Calendar Setup:**
```xml
<calendars>
  <day-types>
    <day-type id="0"/>
    <day-type id="1"/>
  </day-types>
  <default-week id="1" name="default" sun="1" mon="0" tue="0" wed="0" thu="0" fri="0" sat="1"/>
</calendars>
```

4. **Tasks Container:**
```xml
<tasks empty-milestones="true">
  <taskproperties>
    <taskproperty id="tpd0" name="type" type="default" valuetype="icon"/>
    <taskproperty id="tpd1" name="priority" type="default" valuetype="icon"/>
    <taskproperty id="tpd2" name="info" type="default" valuetype="icon"/>
    <taskproperty id="tpd3" name="name" type="default" valuetype="text"/>
    <taskproperty id="tpd4" name="begindate" type="default" valuetype="date"/>
    <taskproperty id="tpd5" name="enddate" type="default" valuetype="date"/>
    <taskproperty id="tpd6" name="duration" type="default" valuetype="int"/>
    <taskproperty id="tpd7" name="completion" type="default" valuetype="int"/>
    <taskproperty id="tpd8" name="coordinator" type="default" valuetype="text"/>
    <taskproperty id="tpd9" name="predecessorsr" type="default" valuetype="text"/>
  </taskproperties>
  
  <!-- Task elements go here -->
</tasks>
```

### Task Elements
Each task should be represented as:
```xml
<task id="[unique_id]" 
      name="[Task Name]" 
      meeting="[true for milestones, false for tasks]" 
      start="[YYYY-MM-DD]" 
      duration="[number of days]" 
      complete="[0-100]" 
      expand="true">
  
  <!-- Dependencies (if any) -->
  <depend id="[dependent_task_id]" type="2" difference="0" hardness="Strong"/>
</task>
```

### Resources Section
```xml
<resources>
  <resource id="[resource_id]" 
            name="[Full Name]" 
            function="[Role]" 
            contacts="" 
            phone=""/>
</resources>
```

### Resource Allocations
```xml
<allocations>
  <allocation task-id="[task_id]" 
              resource-id="[resource_id]" 
              function="Default:1" 
              responsible="true" 
              load="100.0"/>
</allocations>
```

### Additional Required Elements
```xml
<vacations/>
<previous/>
<roles roleset-name="Default"/>
```

## Implementation Guidelines

### Data Structures
Define classes/structures for:
- `Project`: name, start_date, duration, resources, tasks, milestones
- `Task`: id, name, start_date, end_date, duration, resource_id, dependencies, is_milestone, progress, priority
- `Resource`: id, name, role
- `Dependency`: from_task_id, to_task_id, type

### Processing Steps
1. **Parse Markdown:**
   - Read file line by line
   - Track current section (project, resources, tasks, milestones)
   - Extract data according to format rules
   - Build internal data structures

2. **Validate Data:**
   - Check for required fields (project name, start date)
   - Validate date formats
   - Ensure all referenced resources exist
   - Detect circular dependencies

3. **Calculate Schedules:**
   - Resolve dependencies and calculate start/end dates
   - Handle business day calculations
   - Generate warnings for scheduling conflicts

4. **Generate XML:**
   - Create properly formatted XML structure
   - Assign unique IDs to all elements
   - Include all required GanttProject metadata
   - Format dates consistently (YYYY-MM-DD)

### Error Handling
- Gracefully handle malformed markdown
- Provide clear error messages for invalid dates
- Warn about missing resources or unresolvable dependencies
- Validate that generated XML is well-formed

### Business Day Logic
- Skip weekends when calculating durations
- Add weekend days to duration calculations
- Support custom calendar definitions if needed

### Testing
Create test cases with:
- Simple linear project (no dependencies)
- Complex project with dependencies
- Projects with milestones
- Projects with resource assignments
- Edge cases (circular dependencies, invalid dates)

## Output Requirements
- Generate valid .gan XML file that opens in GanttProject
- Preserve all task hierarchies and relationships
- Include proper resource assignments
- Set reasonable default view settings
- Ensure dates are calculated correctly for business days

## Usage Pattern
The utility should be invokable as:
```bash
converter input_project.md output_project.gan
```

And should provide clear success/error feedback including:
- Number of tasks processed
- Number of resources created
- Any warnings or errors encountered
- Confirmation of successful file generation