# LLM-Driven Project Analysis with p2gan

## Overview: How p2gan Works with LLMs

**p2gan's primary purpose** is to enable LLMs to automatically understand projects and generate Gantt charts. The workflow is:

1. **LLM runs p2gan's analyzers** to gather intelligence about the project
2. **LLM infers** project structure, complexity, completion status, and dependencies
3. **LLM generates** a comprehensive `.gan` file based on the analysis

This document provides prompts and guidance for LLMs to effectively use p2gan.

---

## The Complete LLM Workflow

### Phase 1: Intelligence Gathering (Use the Analyzers)

**CRITICAL**: The LLM must first run p2gan's built-in analyzers to understand the project.

```python
from p2gan import ProjectHistoryAnalyzer, DateHistogram, ProjectStats

# Step 1: Analyze project history and file patterns
analyzer = ProjectHistoryAnalyzer("/path/to/project")
history = analyzer.analyze()
# Returns: {
#   "earliest_date": datetime,
#   "latest_date": datetime,
#   "total_files": int,
#   "file_categories": {...},  # Files grouped by type
#   "timeline": [...],          # Chronological file events
#   "suggested_phases": [...]   # Inferred development phases
# }

# Step 2: Get file activity timeline
histogram = DateHistogram("/path/to/project")
activity = histogram.analyze()
# Returns: Activity patterns, creation/modification timeline

# Step 3: Get project statistics
stats = ProjectStats("/path/to/project")
metrics = stats.analyze()
# Returns: Complexity metrics, file counts, language breakdown
```

**What the LLM learns from analyzers:**
- **File dates** → Task start/end dates, project phases
- **File categories** → Task breakdown (setup, tests, docs, features)
- **Git history** → Contributor activity, completion patterns
- **Complexity metrics** → Effort estimation, task duration
- **Directory structure** → Logical dependencies

### Phase 2: Inference (LLM Reasoning)

Based on analyzer output, the LLM should infer:

**Tasks & Phases:**
- Group files by creation date to identify development phases
- Categorize by file type (setup, core features, tests, docs, deployment)
- Estimate duration based on file count and complexity

**Completion Status:**
- Files with recent modification dates = in progress
- Old files with no recent changes = completed
- TODO/FIXME comments = planned work (0% complete)

**Complexity & Effort:**
- Large files / many dependencies = longer duration
- Test files present = quality-focused (add testing tasks)
- Documentation files = mature project (add doc tasks)

**Dependencies:**
- Setup files must come first (requirements.txt, package.json)
- Core code before tests
- Tests before deployment
- Import statements reveal code dependencies

**Resources (Team Members):**
- Extract from git log: `git log --format="%an" | sort -u`
- Assign tasks based on file authorship patterns

### Phase 3: Generation (Create the Gantt Chart)

```python
from p2gan import Project, Task, Resource, GanttGenerator, Dependency, TaskPriority
from datetime import datetime

# LLM creates project based on inference
project = Project(
    name="[Inferred from README or directory name]",
    start_date=history["earliest_date"],
    company="[From git config or docs]"
)

# Add resources (from git contributors)
for contributor_name in contributors:
    resource = Resource(
        id=len(project.resources),
        name=contributor_name,
        role="Developer"
    )
    project.add_resource(resource)

# Add inferred tasks with hierarchy
# Example: Setup Phase
setup_phase = Task(
    id=0,
    name="Project Setup",
    start_date=history["earliest_date"],
    duration=3,
    progress=100,  # Old files = completed
    priority=TaskPriority.HIGH
)
project.add_task(setup_phase)

# Add subtasks based on file analysis
# ... (LLM generates tasks from analyzer output)

# Add dependencies (LLM infers logical order)
# setup_task.add_dependency(development_task.id)

# Generate the .gan file
generator = GanttGenerator(project)
generator.save("project_timeline.gan")
```

---

## Standard Prompt Template for LLMs

Use this prompt with Claude Code, ChatGPT, or other LLM-based tools:

```
Please analyze this project and create a comprehensive Gantt chart using p2gan. Follow these steps:

## 1. INTELLIGENCE GATHERING - Run p2gan Analyzers

**YOU MUST run these analyzers first to understand the project:**

```python
from p2gan import ProjectHistoryAnalyzer, DateHistogram, ProjectStats

# Analyzer 1: Project history and file patterns
analyzer = ProjectHistoryAnalyzer("/path/to/project")
history = analyzer.analyze()
# USE THIS DATA: earliest_date, file_categories, timeline, suggested_phases

# Analyzer 2: File activity timeline
histogram = DateHistogram("/path/to/project")
activity = histogram.analyze()
# USE THIS DATA: creation/modification patterns, development phases

# Analyzer 3: Project statistics
stats = ProjectStats("/path/to/project")
metrics = stats.analyze()
# USE THIS DATA: complexity, file counts, language breakdown
```

**What you learn from analyzers:**
- File dates → Task timing (start/end dates, phases)
- File categories → Task types (setup, features, tests, docs)
- Git history → Contributors, completion patterns
- Complexity metrics → Effort estimates, task duration
- Directory structure → Logical dependencies

## 2. INFERENCE - Reason About Project Structure

**Based on analyzer output, you must infer:**

**Tasks & Phases:**
- Group files by creation date → development phases
- Categorize by file type → task breakdown (setup, core, tests, docs, deploy)
- Use file count + complexity → duration estimates

**Completion Status:**
- Recent file modifications → in progress (30-70% complete)
- Old, unchanged files → completed (100% complete)
- TODO/FIXME comments → planned work (0% complete)

**Effort Estimation:**
- Large files / many dependencies → longer duration
- Test files present → add testing phase
- Documentation files → add documentation tasks
- Use history: feature = 3-5 days, bugfix = 1-2 days, refactor = 2-3 days

**Dependencies:**
- Setup files (requirements.txt, package.json) → must come first
- Core code → before tests
- Tests → before deployment
- Import statements → reveal code dependencies

**Resources:**
- Extract from: `git log --format="%an" | sort -u`
- Assign tasks based on file authorship

## 3. ADDITIONAL DISCOVERY - Enhance Your Understanding

**Read key files:**
- README, CHANGELOG, TODO, KANBAN files
- Documentation in docs/, notes/ directories
- Existing project plans or roadmaps

**Extract tasks from:**
- TODO/FIXME comments in code
- Markdown task lists (- [ ] items)
- README "Future Features" sections
- Test files (indicate planned functionality)
- Commit messages (work patterns)

## 4. GENERATION - Create the Gantt Chart

**Now create the p2gan project using your inferred knowledge:**

```python
from datetime import datetime, timedelta
from p2gan import Project, Task, Resource, GanttGenerator, TaskPriority
from p2gan.models import DependencyType

# Initialize project with INFERRED information
project = Project(
    name="[Inferred from README or directory name]",
    company="[From git config or docs]",
    start_date=history["earliest_date"]  # From analyzer!
)

# Add resources (INFERRED from git contributors)
contributors = [...]  # From git log --format="%an" | sort -u
for idx, name in enumerate(contributors):
    resource = Resource(
        id=idx,
        name=name,
        role="Developer"  # Or infer from file patterns
    )
    project.add_resource(resource)

# Add tasks with proper hierarchy (INFERRED from analyzer data)
# Example: Setup Phase (from earliest files)
setup_task = Task(
    id=0,
    name="Project Setup",
    start_date=history["earliest_date"],
    duration=3,  # Inferred from file count
    progress=100,  # Old files = completed
    priority=TaskPriority.HIGH
)
project.add_task(setup_task)

# Add more tasks based on file_categories and timeline...
# [LLM generates tasks from analyzer output]

# Define dependencies (INFERRED from logical order)
# Example: setup must come before development
# setup_task.add_dependency(dev_task.id, DependencyType.FINISH_TO_START)

# Generate the .gan file
generator = GanttGenerator(project)
generator.save("project_timeline.gan")

print(f"✓ Generated project_timeline.gan with {len(project.tasks)} tasks")
print(f"  Project spans {(history['latest_date'] - history['earliest_date']).days} days")
print(f"  Completion: {sum(t.progress for t in project.tasks) / len(project.tasks):.0f}%")
print("\n  Open in GanttProject to view and refine the timeline")
```

## 5. OUTPUT SUMMARY

**Provide the user with:**
- Total tasks identified and categorized (completed/in-progress/planned)
- Project duration and date range
- Completion percentage estimate
- Key phases discovered
- Critical dependencies
- Team member assignments
- Path to generated .gan file

**Example:**
```
✓ Generated project_timeline.gan

Project Analysis:
  • Name: MyProject (inferred from directory)
  • Duration: 2024-01-15 to 2024-06-20 (157 days)
  • Total Tasks: 23
    - Completed: 15 (65%)
    - In Progress: 5 (22%)
    - Planned: 3 (13%)

Phases Discovered:
  1. Project Setup (Jan 15-18, 100% complete)
  2. Core Development (Jan 19-Apr 30, 100% complete)
  3. Testing & QA (May 1-15, 80% complete)
  4. Documentation (May 10-30, 40% complete)
  5. Deployment Prep (Jun 1-20, 20% complete)

Team: 4 contributors identified from git history

📂 Open project_timeline.gan in GanttProject to view and customize.

⚠️  IMPORTANT: This is a preliminary analysis requiring human review.
    Please validate task accuracy, timeline estimates, dependencies,
    resource allocations, and project scope before using for planning.
```

Execute this complete analysis workflow now.
```

---

## ⚠️ Critical Disclaimer: Human-In-The-Loop Review Required

**LLM-generated Gantt charts are preliminary and NOT 100% accurate.** The analysis is based on inference from code patterns, file dates, git history, and TODO comments—but the LLM cannot guarantee correctness.

### What Requires Human Validation

**Before using the generated Gantt chart for planning or decision-making, you MUST review:**

1. **Task Accuracy**
   - Are all project tasks captured?
   - Are any tasks incorrectly identified or missing?
   - Do task descriptions match actual work?

2. **Completion Status**
   - Do progress percentages reflect reality?
   - Are "completed" tasks actually finished?
   - Are in-progress tasks at the estimated completion level?

3. **Timeline Estimates**
   - Are task durations realistic?
   - Are start/end dates accurate?
   - Does the overall timeline match project history?

4. **Dependencies**
   - Are task dependencies correct?
   - Are any dependencies missing?
   - Are dependencies overly conservative or incorrect?

5. **Resource Allocations**
   - Are team members assigned to the right tasks?
   - Are allocation percentages realistic?
   - Are any contributors missing or misidentified?

6. **Project Scope**
   - Does the chart capture the full project scope?
   - Are future/planned features accurately represented?
   - Are any project areas overlooked?

### Recommended Workflow

1. **LLM generates preliminary .gan file** (using p2gan analyzers and inference)
2. **Human opens in GanttProject** to review the generated timeline
3. **Human validates and corrects** all tasks, dates, dependencies, and resources
4. **Human refines** based on actual project requirements and domain knowledge
5. **Iterate**: Use corrected chart as baseline for ongoing project management

**The LLM provides a strong starting point—human expertise ensures accuracy.**

---

## Quick Analysis Prompt (Simplified)

**For when you need a concise prompt:**

```
Use p2gan to analyze this project and create a Gantt chart:

1. Run ProjectHistoryAnalyzer, DateHistogram, and ProjectStats
2. Infer project structure from file dates, categories, and complexity
3. Determine completion status from file modification patterns
4. Extract tasks from code, git history, TODOs, and documentation
5. Generate a comprehensive .gan file with tasks, phases, and dependencies

Focus on INFERENCE: use analyzer data to reason about the project.
```

---

## Specific Use Cases

### For a New Project (Planned Work)
```
This is a new project with planned features. Use p2gan to create a timeline:

1. Run analyzers to understand what exists (initial setup files)
2. Read README/docs to extract planned features
3. Infer task breakdown from feature descriptions
4. Estimate effort based on similar project patterns
5. Create logical dependencies (setup → core → testing → deployment)
6. Generate .gan file with forward-looking timeline

Focus: INFERENCE from documentation, logical task ordering
```

### For an Existing Project (Historical Analysis)
```
This project has development history. Use p2gan to create a retroactive timeline:

1. Run ProjectHistoryAnalyzer to get file creation/modification timeline
2. Use DateHistogram to identify development phases
3. Extract git contributors and map to resources
4. Infer completion status from file dates (old = done, recent = in-progress)
5. Extract future work from TODOs, issues, open PRs
6. Generate .gan showing past, present, and future

Focus: INFERENCE from file dates and git history
```

### For Complex Projects (Deep Analysis)
```
This is a mature codebase. Use p2gan for comprehensive analysis:

1. Run all analyzers (ProjectHistory, DateHistogram, ProjectStats)
2. Analyze directory structure to infer architecture phases
3. Use complexity metrics to estimate remaining effort
4. Map import dependencies to task dependencies
5. Identify testing/documentation maturity
6. Generate detailed .gan with multiple phases and subtasks

Focus: INFERENCE from code structure, complexity, and patterns
```

---

## Integration Instructions

### With Claude Code
1. Navigate to your project directory in the terminal
2. Paste the full analysis prompt (or simplified version)
3. **Claude will**: Run analyzers → infer structure → generate .gan
4. Review the analysis summary and generated .gan file
5. Open in GanttProject to refine and customize

### With ChatGPT (Code Interpreter / Advanced Data Analysis)
1. Upload project files or provide repo access
2. Use the full analysis prompt
3. **ChatGPT will**: Run analyzers → infer structure → generate code
4. Execute the generated Python code
5. Download the .gan file and open in GanttProject

### With Other LLMs (Local, API-based)
1. Ensure the LLM has:
   - File system access
   - Python execution capability
   - p2gan package installed
2. Provide project path in the prompt
3. **LLM should**: Run analyzers → infer → generate
4. Open resulting .gan file in GanttProject

---

## Tips for Best LLM Results

1. **Emphasize Inference**: Remind the LLM to infer, not just convert
2. **Analyzer First**: Ensure the LLM runs analyzers before manual exploration
3. **Git History**: Projects with git history yield richer timelines
4. **Documentation Helps**: READMEs, CHANGELOGs improve task extraction
5. **Iterative Refinement**:
   - First pass: LLM generates preliminary .gan
   - Review in GanttProject
   - Ask LLM to refine based on your feedback
6. **Explicit Guidance**: Tell the LLM your priorities:
   - "Focus on completed work" → historical analysis
   - "Focus on future roadmap" → forward planning
   - "Show everything" → comprehensive past/present/future

---

## Example Output Structure

**The LLM should generate a Python script that creates:**

### 1. Project Metadata (INFERRED)
- **Name**: From README, directory name, or git config
- **Start Date**: From earliest file creation date (analyzer)
- **Company**: From git config, documentation, or inferred

### 2. Resources (INFERRED from git)
- **Team members**: Extracted from `git log --format="%an" | sort -u`
- **Roles**: Inferred from file patterns (who works on what)
- **Assignments**: Based on file authorship

### 3. Task Hierarchy (INFERRED from analysis)
- **Phases**: From file_categories and timeline patterns
  - Setup Phase (requirements.txt, config files)
  - Core Development (src/, lib/, main code)
  - Testing (test files, QA patterns)
  - Documentation (docs/, README updates)
  - Deployment (docker, CI/CD files)
- **Start Dates**: From file creation timestamps
- **Durations**: Estimated from file count, complexity, and patterns
- **Progress**: Based on file modification dates
  - Old unchanged files → 100%
  - Recently modified → 50-80%
  - TODO comments → 0%
- **Dependencies**: Logical order (setup → dev → test → deploy)

### 4. Milestones (INFERRED or extracted)
- From git tags
- From CHANGELOG.md version markers
- From logical phase completion points

### 5. The .gan File
The resulting file opens in GanttProject and shows:
- Visual timeline of all inferred work
- Task dependencies and critical path
- Team member assignments
- Progress indicators
- Editable for refinement