# p2gan - Project to Gantt Converter

[![PyPI Version](https://img.shields.io/pypi/v/p2gan)](https://pypi.org/project/p2gan/)
[![Python Versions](https://img.shields.io/pypi/pyversions/p2gan)](https://pypi.org/project/p2gan/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**p2gan** (Project to Gantt) is a Python library enabling AI agents (Claude Code, Codex, and other coding assistants) to analyze diverse project materials—PDFs, code, markdown, documentation—and generate preliminary GanttProject (.gan) files based on discovered structure, dependencies, and file timestamps. Create professional Gantt charts programmatically without manual editing.

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

### Command Line Usage

Convert a project file to GanttProject format (markdown example):

```bash
p2gan convert project.md output.gan
```

### Python API Usage

```python
from ganttproject import Project, Task, Resource, GanttGenerator
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
git clone https://github.com/ecphoria/p2gan
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

- **Agile to Traditional Bridge** - Convert sprint plans to Gantt charts
- **Documentation to Timeline** - Transform markdown roadmaps to visual schedules
- **CI/CD Integration** - Generate project reports in automated pipelines
- **Template-Based Planning** - Maintain reusable project templates

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

- **Issues:** [GitHub Issues](https://github.com/ecphoria/p2gan/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ecphoria/p2gan/discussions)
- **Documentation:** [Read the Docs](https://p2gan.readthedocs.io)