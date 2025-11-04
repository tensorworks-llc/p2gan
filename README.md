# p2gan - Project to Gantt Converter

[![PyPI Version](https://img.shields.io/pypi/v/p2gan)](https://pypi.org/project/p2gan/)
[![Python Versions](https://img.shields.io/pypi/pyversions/p2gan)](https://pypi.org/project/p2gan/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**p2gan** (Project to Gantt) is a Python library that empowers **LLMs to automatically understand and visualize projects as Gantt charts**. By providing powerful analysis tools—file history, date patterns, project statistics—p2gan enables AI agents (Claude Code, ChatGPT, local models) to infer project complexity, completion status, logical task breakdown, and dependencies, then generate comprehensive GanttProject (.gan) files.

**The Core Workflow:** LLM analyzes project → uses p2gan analyzers → infers project state → generates Gantt chart

While p2gan can also be used manually (CLI, Python API, markdown conversion), its primary design is to give LLMs the tools they need to automatically create project timelines from any codebase.

> **Note:** [GanttProject](https://www.ganttproject.biz/) is a free, open-source project management application written in Java and maintained by BarDSoftware. p2gan is an independent tool that generates `.gan` files compatible with GanttProject, but is not affiliated with or endorsed by the GanttProject team.

## Features

- 🤖 **AI-Assisted Analysis** - Designed for AI agents to analyze diverse project materials and generate timelines
- 🔧 **Pure Python** - Zero external dependencies, uses only Python stdlib
- 📊 **Full GanttProject Support** - Tasks, resources, dependencies, milestones
- 🏗️ **Programmatic API** - Build projects in Python code
- 🎯 **Project Analysis** - Analyze project complexity and stakeholders
- 🚀 **CI/CD Ready** - Integrate into automated workflows

## Quick Start

### Installation

```bash
pip install p2gan
```

## Primary Use: LLM-Driven Project Analysis

**This is how p2gan is meant to be used**: An LLM uses the built-in analyzers to understand your project, then generates a Gantt chart automatically.

### Step 1: LLM Runs the Analyzers

The LLM should use p2gan's powerful analysis tools to gather project intelligence:

```python
from p2gan import ProjectHistoryAnalyzer, DateHistogram, ProjectStats

# Comprehensive project history analysis
analyzer = ProjectHistoryAnalyzer("/path/to/project")
history = analyzer.analyze()
# Returns: file dates, categories, timeline, suggested phases

# File activity timeline
histogram = DateHistogram("/path/to/project")
activity = histogram.analyze()
# Returns: creation/modification patterns, development phases

# Project statistics and metrics
stats = ProjectStats("/path/to/project")
metrics = stats.analyze()
# Returns: complexity, file counts, language breakdown
```

### Step 2: LLM Infers Project Structure

Based on analyzer output, the LLM:
- Identifies logical phases from file creation patterns
- Infers task difficulty from code complexity and file sizes
- Determines completion status from file dates and git history
- Discovers dependencies from imports and directory structure
- Extracts TODOs, FIXMEs, and planned work from code comments

### Step 3: LLM Generates the Gantt Chart

```python
from p2gan import Project, Task, Resource, GanttGenerator
from datetime import datetime

# LLM creates project based on analysis
project = Project(
    name="Analyzed Project",
    start_date=datetime(2025, 1, 1)
)

# LLM adds inferred tasks, resources, dependencies
# ... (based on analyzer output)

# Generate GanttProject file
generator = GanttGenerator(project)
generator.save("project_timeline.gan")
```

### ⚠️ Important: Human-In-The-Loop Review Required

**LLM-generated Gantt charts are preliminary and require human validation.** The LLM infers project structure from code patterns, git history, and file dates, but cannot guarantee 100% accuracy.

**Always review and validate:**
- **Task accuracy**: Are all tasks captured? Any missing or incorrect tasks?
- **Completion status**: Do the progress percentages reflect reality?
- **Timeline estimates**: Are durations and dates realistic?
- **Dependencies**: Are task dependencies correct and complete?
- **Resource allocations**: Are team members assigned appropriately?
- **Project scope**: Does the chart capture the full project scope?

**Workflow:** Use the LLM-generated `.gan` file as a starting point, then open it in GanttProject to refine, correct, and customize based on actual project requirements.

### Quick LLM Prompt

```
Analyze this project using p2gan's built-in analyzers:
1. Run ProjectHistoryAnalyzer, DateHistogram, and ProjectStats
2. Examine file dates, code structure, and documentation
3. Infer tasks, completion status, and logical phases
4. Generate a comprehensive Gantt chart (.gan file)
```

See [AI_PROMPT_EXAMPLE.md](AI_PROMPT_EXAMPLE.md) for detailed LLM prompts.

---

## Alternative Use: Manual Creation

p2gan can also be used without an LLM for manual project management.

### Command Line Usage

Convert a project file to GanttProject format:

```bash
p2gan convert project.md output.gan
```

### Python API Usage

```python
from p2gan import Project, Task, Resource, GanttGenerator
from datetime import datetime

# Create a project
project = Project(
    name="My Software Project",
    start_date=datetime(2025, 1, 1)
)

# Add resources
developer = Resource(id=0, name="Alice", role="Developer")
project.add_resource(developer)

# Add tasks
task = Task(
    id=0,
    name="Setup Development Environment",
    duration=3,
    start_date=datetime(2025, 1, 1)
)
task.add_allocation(developer, load=100.0)
project.add_task(task)

# Generate GanttProject file
generator = GanttGenerator(project)
generator.save("my_project.gan")
```

## Input Formats

p2gan can process various input formats. Here's an example using markdown for project plans:

```markdown
# Project: Website Redesign

**Start Date:** 2025-01-15
**Duration:** 8 weeks

## Resources
- Alice Johnson (Frontend Developer)
- Bob Smith (Backend Developer)
- Carol White (Designer)

## Tasks
### Phase 1: Planning
- **Requirements Gathering** (5 days, Alice Johnson)
  - Priority: High
  - Progress: 0%

- **Design Mockups** (7 days, Carol White)
  - Dependencies: Requirements Gathering
  - Priority: High

### Phase 2: Development
- **Frontend Development** (15 days, Alice Johnson)
  - Dependencies: Design Mockups
  - Priority: Medium

## Milestones
- [ ] Planning Complete (2025-01-25)
- [ ] Design Approved (2025-02-03)
```

## Supported Features

### Task Management
- ✅ Hierarchical tasks (unlimited nesting)
- ✅ Task dependencies (FS, SS, FF, SF)
- ✅ Task priorities (Low, Medium, High)
- ✅ Progress tracking
- ✅ Task constraints and deadlines
- ✅ Custom fields

### Resource Management
- ✅ Resource roles and rates
- ✅ Resource allocation percentages
- ✅ Resource calendars
- ✅ Vacation/unavailability periods

### Dependencies
- ✅ Finish-to-Start (FS)
- ✅ Start-to-Start (SS)
- ✅ Finish-to-Finish (FF)
- ✅ Start-to-Finish (SF)
- ✅ Lag/lead time

## Examples

Check out the `samples/` directory for example projects:

```bash
# Simple project
p2gan convert samples/sample_project.md my_gantt.gan

# Complex project with multiple phases
p2gan convert samples/dhg_ecosystem_project.md ecosystem.gan
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/tensorworks-llc/p2gan
cd p2gan

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
black src/p2gan/
flake8 src/p2gan/
mypy src/p2gan/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=p2gan

# Run specific test file
pytest tests/test_models.py
```

## Documentation

Full documentation is available at [https://p2gan.readthedocs.io](https://p2gan.readthedocs.io)

- [Getting Started Guide](docs/getting-started.md)
- [Markdown Format Reference](docs/markdown-format.md)
- [Python API Reference](docs/api-reference.md)
- [GanttProject Compatibility](docs/GANTTPROJECT_CAPABILITIES.md)

## Use Cases

### Primary: LLM-Driven Analysis
- **Automated Project Understanding** - LLM analyzes any codebase and generates timeline
- **Retroactive Documentation** - Turn existing projects into visual Gantt charts automatically
- **Complexity Assessment** - LLM infers project difficulty, completion status, and effort
- **Intelligent Task Breakdown** - Automatic phase detection from file patterns and git history

### Secondary: Manual/Traditional Use
- **Agile to Traditional Bridge** - Convert sprint plans to Gantt charts
- **Documentation to Timeline** - Transform markdown roadmaps to visual schedules
- **CI/CD Integration** - Generate project reports in automated pipelines
- **Template-Based Planning** - Maintain reusable project templates

## AI Integration

**p2gan's core purpose** is to work with LLMs (Claude Code, ChatGPT, local models) to automatically understand and visualize projects.

### How LLMs Should Use p2gan

The LLM acts as the intelligence layer that:
1. **Runs the analyzers** (`ProjectHistoryAnalyzer`, `DateHistogram`, `ProjectStats`)
2. **Examines** file/folder dates, content, structure, git history
3. **Infers** complexity, completion level, logical task breakdown, dependencies
4. **Generates** the preliminary `.gan` file based on analysis

### Using p2gan with AI Agents

See [AI_PROMPT_EXAMPLE.md](AI_PROMPT_EXAMPLE.md) for comprehensive prompts showing:
- How to orchestrate the built-in analyzers
- How to infer project structure from analyzer output
- How to extract tasks from multiple sources (code, git, TODOs, docs)
- How to generate timelines based on file dates and complexity
- Complete examples of LLM-driven project analysis

### Quick Start with AI
```
"Analyze this project and create a Gantt chart using p2gan:
1. Run ProjectHistoryAnalyzer, DateHistogram, and ProjectStats
2. Examine file dates, code structure, git history, and documentation
3. Infer tasks, phases, completion status, and dependencies
4. Generate a comprehensive .gan file"
```

## Roadmap

- [x] Core functionality (v0.1.0)
- [ ] Comprehensive test suite (v0.2.0)
- [ ] Import from CSV/Excel (v0.3.0)
- [ ] Export to HTML/PDF (v0.4.0)
- [ ] Web UI (v0.5.0)
- [ ] AI-powered planning (v1.0.0)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [GanttProject](https://www.ganttproject.biz/) by BarDSoftware for creating and maintaining the excellent open-source project management application
- The GanttProject team for their well-documented `.gan` XML file format
- Contributors and early adopters
- Anthropic Claude for development assistance

## Support

- **Issues:** [GitHub Issues](https://github.com/tensorworks-llc/p2gan/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tensorworks-llc/p2gan/discussions)
- **Documentation:** [Read the Docs](https://p2gan.readthedocs.io)