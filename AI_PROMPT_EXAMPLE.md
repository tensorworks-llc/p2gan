# AI Agent Prompt for p2gan Project Analysis

## Standard Prompt Template for AI-Assisted Project Timeline Generation

Use this prompt with Claude Code, GitHub Copilot, or other AI coding assistants to analyze a project and generate a GanttProject (.gan) file.

**IMPORTANT**: p2gan includes powerful built-in analyzers that should be used FIRST before manual analysis!

---

## Full Analysis Prompt with Built-in Tools

```
Please analyze this project and create a comprehensive Gantt chart using p2gan's built-in analyzers. Follow these steps:

## 1. Use p2gan's Built-in Analyzers FIRST

Run the powerful built-in analysis tools via Python:

```python
from p2gan import ProjectHistoryAnalyzer, DateHistogram, ProjectStats

# Comprehensive project history analysis
analyzer = ProjectHistoryAnalyzer("/path/to/project")
history = analyzer.analyze()
report = analyzer.generate_report("project_history.md")

# Get file activity timeline
histogram = DateHistogram("/path/to/project")
activity_data = histogram.analyze()

# Get project statistics
stats = ProjectStats("/path/to/project")
project_metrics = stats.analyze()
```

Or use them as CLI tools:

```bash
# Generate comprehensive project history report
python -m p2gan.project_history /path/to/project --output history.md --json data.json

# Generate date histogram of file activity
python -m p2gan.date_histogram /path/to/project --csv timeline.csv

# Get project statistics
python -m p2gan.project_stats /path/to/project --markdown stats.md
```

These tools automatically:
- Analyze file creation/modification dates
- Categorize files by type and purpose
- Identify development phases
- Suggest task structure
- Generate timeline from file history
- Extract git history if available

## 2. Enhance with Manual Discovery
- Read key files: README, KANBAN, TODO, CHANGELOG
- Examine documentation in docs/, notes/, or similar directories
- Check for existing project plans, roadmaps, or task lists

## 3. Task Extraction
Identify tasks from multiple sources:
- TODO/FIXME comments in code
- GitHub issues (if accessible)
- Markdown task lists (- [ ] items)
- Kanban boards or project management files
- README roadmaps and "Future Features" sections
- Test files indicating planned functionality
- Documentation mentioning upcoming features
- Commit messages indicating work patterns

## 4. Task Categorization
Group tasks into categories:
- **Completed**: Already done (from git history, closed issues, checked boxes)
- **In Progress**: Currently being worked on (recent commits, open PRs)
- **Planned**: Documented future work
- **Inferred**: Logical next steps based on project structure

## 5. Timeline Analysis
For each task, determine:
- **Start Date**: Based on first commit or file creation
- **Duration**: Estimate from:
  - Complexity (lines of code, number of files)
  - Similar completed tasks in git history
  - Standard estimates (feature = 3-5 days, bugfix = 1-2 days, refactor = 2-3 days)
- **Dependencies**: Identify from:
  - Import statements and module dependencies
  - Logical order (database before API, API before UI)
  - Explicit mentions in documentation

## 6. Resource Assignment
Identify contributors:
- From git log: git log --format="%an" | sort -u
- From documentation credits
- Assign tasks based on commit history patterns

## 7. Generate Gantt Chart
Create the p2gan Python script:

```python
from datetime import datetime, timedelta
from p2gan.models import Project, Task, Resource, Dependency
from p2gan.generator import GanttGenerator

# Initialize project with discovered information
project = Project(
    name="[PROJECT_NAME]",
    company="[ORGANIZATION]",
    start_date=datetime(2024, 1, 1)  # Adjust based on git history
)

# Add discovered resources/contributors
# [Add resources based on git contributors]

# Add tasks with proper hierarchy
# [Add all discovered and inferred tasks]

# Define dependencies
# [Add logical dependencies]

# Generate the .gan file
generator = GanttGenerator(project)
generator.save("project_timeline.gan")

print(f"✓ Generated project_timeline.gan with {len(project.tasks)} tasks")
print("  Open in GanttProject to view and edit the timeline")
```

## 8. Output Summary
Provide:
- Total number of tasks identified
- Project duration estimate
- Critical path highlights
- Current completion percentage
- Suggested next actions

Execute this analysis now and generate the timeline.
```

---

## Quick Analysis Prompt (Simplified)

```
Analyze this project's structure, git history, and documentation to create a project timeline.
Use p2gan to generate a .gan file with:
1. All completed work (from git history)
2. Current tasks (from TODO/KANBAN files)
3. Future plans (from README/docs)
4. Logical dependencies between tasks
5. Reasonable duration estimates

Focus on file dates, commit history, and project documentation to build an accurate timeline.
```

---

## Specific Use Cases

### For a New Project
```
This is a new project. Please:
1. Analyze the planned features in README/docs
2. Break down into implementation tasks
3. Estimate effort for each component
4. Create a project timeline with p2gan
5. Suggest a development order considering dependencies
```

### For an Existing Project
```
Analyze the git history and current state of this project:
1. Map completed work from git log
2. Identify in-progress features from recent commits
3. Extract future plans from TODOs and documentation
4. Generate a Gantt chart showing past, present, and future
```

### For Project Documentation
```
Generate a project timeline visualization by:
1. Analyzing all markdown files, PDFs, and documentation
2. Extracting any mentioned tasks, milestones, or deliverables
3. Inferring a logical sequence and timeline
4. Creating a preliminary .gan file for project planning
```

---

## Integration Instructions

### With Claude Code
1. Navigate to your project directory
2. Paste the full analysis prompt
3. Claude will explore your project and generate the timeline
4. Review and refine the generated .gan file

### With Other AI Agents
1. Ensure the agent has file system access
2. Provide the project path
3. Use the appropriate prompt template
4. Run the generated Python script
5. Open the .gan file in GanttProject

---

## Tips for Best Results

1. **More Context = Better Timeline**: Include all project documentation
2. **Git History Helps**: Projects with git history get more accurate timelines
3. **Explicit Dates**: Mention any known deadlines or milestones
4. **Task Descriptions**: Clear task descriptions improve categorization
5. **Review and Refine**: The generated timeline is a starting point - refine in GanttProject

---

## Example Output Structure

The AI agent should generate a Python script that creates:
- Project metadata (name, dates, company)
- Resource list (team members)
- Task hierarchy with:
  - Work Breakdown Structure (WBS)
  - Start dates and durations
  - Progress percentages for completed work
  - Dependencies between related tasks
- Milestones for major deliverables

The resulting .gan file can be opened and refined in GanttProject.