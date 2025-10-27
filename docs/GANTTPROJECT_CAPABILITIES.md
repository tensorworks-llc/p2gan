# GanttProject Capabilities & Features Overview

## What is GanttProject?
GanttProject is a free, open-source project management application written in Java that runs on Windows, Linux, and macOS. It provides Gantt charts, resource management, and PERT chart generation for project planning and tracking.

## Core Capabilities

### 1. Task Management
- **Hierarchical Task Structure**: Tasks can be organized in a tree structure with unlimited nesting
- **Task Properties**:
  - Name, Start Date, End Date, Duration
  - Progress percentage (0-100%)
  - Priority (5 levels)
  - Color coding
  - Notes and custom fields
  - Cost tracking
  - Web links and attachments

### 2. Task Dependencies & Constraints
- **Dependency Types**:
  - **Finish-to-Start (FS)**: Default - Task B starts after Task A finishes
  - **Start-to-Start (SS)**: Task B starts when Task A starts
  - **Finish-to-Finish (FF)**: Task B finishes when Task A finishes
  - **Start-to-Finish (SF)**: Task B finishes when Task A starts (rare)
- **Lag/Lead Time**: Add delays or overlaps between dependent tasks
- **Constraints**:
  - Must Start On
  - Must Finish On
  - Start No Earlier Than
  - Start No Later Than
  - Finish No Earlier Than
  - Finish No Later Than

### 3. Resource Management
- **Resource Properties**:
  - Name, Role/Function
  - Email, Phone
  - Standard rate, overtime rate
  - Resource calendar (availability)
  - Maximum daily workload
- **Resource Allocation**:
  - Assign multiple resources to tasks
  - Set allocation percentage (0-100%)
  - Track resource overallocation
  - Resource load charts

### 4. Milestones
- Zero-duration tasks marking important events
- Can have dependencies like regular tasks
- Displayed as diamonds in Gantt chart
- Can trigger notifications

### 5. Calendars & Working Time
- **Project Calendar**: Define working/non-working days
- **Resource Calendars**: Individual availability
- **Holiday Management**: Company-wide and regional holidays
- **Working Hours**: Customizable daily working hours

### 6. Views & Visualization
- **Gantt Chart View**: Timeline with bars, dependencies, and milestones
- **Resource Chart View**: Resource allocation over time
- **PERT Chart**: Network diagram showing task relationships
- **Task Properties View**: Detailed table view

### 7. Baselines & Tracking
- **Baseline Saving**: Capture planned schedule
- **Actual vs Planned**: Compare current progress to baseline
- **Critical Path**: Highlight tasks affecting project end date
- **Earned Value Management**: Cost and schedule performance

### 8. Import/Export Capabilities
- **Import Formats**:
  - Microsoft Project (.mpp, .mpx, .xml)
  - CSV files
  - iCalendar
  - Previous GanttProject versions
- **Export Formats**:
  - PDF, PNG, JPEG images
  - HTML reports
  - CSV
  - Microsoft Project XML
  - iCalendar

## XML Structure Elements

### Key XML Components for .gan Files

```xml
<!-- Root project element -->
<project name="" version="" view-date="">
  
  <!-- Task hierarchy -->
  <tasks>
    <task id="" name="" start="" duration="" complete="" expand="true">
      <!-- Nested subtasks -->
      <task id="" name="" .../>
      <!-- Dependencies -->
      <depend id="" type="" difference="" hardness=""/>
      <!-- Custom properties -->
      <customproperty taskproperty-id="" value=""/>
    </task>
  </tasks>
  
  <!-- Resources -->
  <resources>
    <resource id="" name="" function="">
      <!-- Resource calendar -->
      <calendar id="">
        <default-week/>
        <exception date=""/>
      </calendar>
    </resource>
  </resources>
  
  <!-- Allocations -->
  <allocations>
    <allocation task-id="" resource-id="" load=""/>
  </allocations>
  
  <!-- Baselines -->
  <baselines>
    <baseline id="" name="" date="">
      <task id="" start="" duration="" complete=""/>
    </baseline>
  </baselines>
  
  <!-- Custom fields -->
  <taskproperties>
    <taskproperty id="" name="" type="" valuetype=""/>
  </taskproperties>
</project>
```

## Advanced Features

### 1. Cost Management
- Resource costs (standard/overtime rates)
- Task fixed costs
- Total project cost calculation
- Cost variance tracking

### 2. Risk Management
- Risk identification fields
- Impact and probability assessment
- Mitigation planning

### 3. Collaboration Features
- WebDAV server integration
- Cloud storage support
- Multi-user project access (with limitations)

### 4. Reporting
- HTML reports with customizable templates
- PDF export with various layouts
- Chart and table generation

### 5. Customization
- Custom task fields
- Custom resource fields
- Color schemes
- UI language support (30+ languages)

## Limitations to Consider
- No real-time collaboration (file-based)
- Limited resource leveling algorithms
- No built-in time tracking
- No native mobile apps
- Limited integration with other tools

## File Format Notes
- **.gan files**: Native XML format (most complete)
- **Version compatibility**: Newer versions can read older files
- **Character encoding**: UTF-8 recommended
- **Date format**: ISO 8601 (YYYY-MM-DD)

## Best Practices for Automation
1. Always include unique task IDs
2. Maintain parent-child relationships properly
3. Validate dependency cycles
4. Use ISO date formats consistently
5. Escape XML special characters
6. Set reasonable default values
7. Include task hierarchies for organization