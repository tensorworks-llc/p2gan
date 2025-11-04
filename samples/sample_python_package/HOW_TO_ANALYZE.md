# How to Analyze This Sample Package with an LLM

This sample Python package (`weatherapi-client`) is designed to demonstrate how an LLM can use p2gan to automatically generate a Gantt chart from a codebase.

> **Note about Git History**: This sample package includes a complete git history (with backdated commits from Sept-Oct 2024) stored in the `DOT_git` directory. To enable p2gan's `ProjectHistoryAnalyzer` to analyze the git history, **rename `DOT_git` to `.git`** before running the analysis. The directory was renamed to avoid git submodule issues in the main p2gan repository.
>
> ```bash
> cd samples/sample_python_package
> mv DOT_git .git
> # Now you can run ProjectHistoryAnalyzer
> ```

## What This Package Demonstrates

The `weatherapi` package simulates a real project with:

- ✅ **Completed work**: Core client, models, caching, rate limiting
- 🚧 **In-progress work**: Historical data, forecast improvements
- 📋 **Planned work**: Async support, GraphQL, CLI tool (see TODOs in code)
- **Logical dependencies**: Setup → Core → Testing → Documentation
- **Team structure**: Inferred from git or documentation
- **Multiple phases**: Project setup, core development, testing, documentation

## Using with an LLM (Claude Code, ChatGPT, Ollama)

### Method 1: Quick Analysis

Navigate to this directory and run:

```bash
# If p2gan is installed globally
cd samples/sample_python_package
```

Then use this prompt with your LLM:

```
Use p2gan to analyze this WeatherAPI package and create a Gantt chart:

1. Run ProjectHistoryAnalyzer, DateHistogram, and ProjectStats on this directory
2. Examine the code structure, README.md, CHANGELOG.md, and TODO comments
3. Infer the project timeline:
   - Phase 1: Initial setup (pyproject.toml, __init__.py)
   - Phase 2: Core development (models, client, providers)
   - Phase 3: Advanced features (cache, rate_limiter)
   - Phase 4: Testing (test files)
   - Phase 5: Documentation (docs/)
4. Identify completion status:
   - Completed: Core client, models, cache, rate limiter, basic tests
   - In Progress: Historical data, forecast improvements
   - Planned: Async support (from TODOs), GraphQL, CLI
5. Create dependencies:
   - Setup → Core → Advanced → Testing → Documentation
6. Generate weatherapi_timeline.gan file

Focus on INFERENCE from file structure and TODO comments.
```

### Method 2: Using the LLM Orchestration Example

Run the provided orchestration example:

```bash
cd ../../  # Back to p2gan root
python examples/llm_orchestration_example.py samples/sample_python_package
```

This will generate `llm_generated_timeline.gan` showing the inferred project structure.

### Method 3: Using Ollama (Local LLM)

If using Ollama with a code-capable model:

```bash
# Start Ollama with a code model
ollama run codellama

# Or deepseek-coder
ollama run deepseek-coder
```

Then provide this context:

```
I'm using p2gan, a Python library that helps LLMs analyze projects and create Gantt charts.

Please analyze the weatherapi package in samples/sample_python_package/:

1. First, write Python code to run these analyzers:
   - ProjectHistoryAnalyzer
   - DateHistogram
   - ProjectStats

2. Based on the analyzer output, infer:
   - Development phases (Setup, Core, Features, Testing, Docs)
   - Task completion status (files with TODOs = 0%, old files = 100%)
   - Dependencies (logical order)
   - Duration estimates (based on file count and complexity)

3. Generate a .gan file with the timeline

Show me the Python code to do this analysis.
```

## Expected Output

The LLM should generate a Gantt chart showing:

### Phase 1: Project Setup (100% complete)
- Create project structure
- Setup dependencies
- Duration: ~2 days

### Phase 2: Core Development (100% complete)
- Implement data models
- Build WeatherClient
- Add provider support
- Duration: ~15 days
- Dependencies: Requires Phase 1

### Phase 3: Advanced Features (80% complete)
- Implement caching
- Add rate limiting
- Historical data (in progress)
- Duration: ~10 days
- Dependencies: Requires Phase 2

### Phase 4: Testing (60% complete)
- Unit tests for models
- Unit tests for cache
- Integration tests (TODO)
- Duration: ~8 days
- Dependencies: Requires Phase 3

### Phase 5: Documentation (70% complete)
- API reference
- User guide
- CHANGELOG
- Duration: ~5 days
- Dependencies: Requires Phase 2

### Phase 6: Future Work (0% complete - Planned)
- Async API support
- GraphQL interface
- CLI tool
- Duration: ~20 days (estimated)
- Dependencies: Requires Phase 3

## Key Features to Observe

The LLM should infer:

1. **Completion from file age**: Older files like models.py are complete
2. **In-progress from TODOs**: Files with TODO comments are partially complete
3. **Planned from README**: Features listed in README roadmap
4. **Dependencies from logic**: Can't test before implementing, can't document before building
5. **Duration from complexity**: More files/complexity = longer duration
6. **Team from git**: Contributors extracted from commit history

## Verification

Open the generated `.gan` file in GanttProject to verify:
- Phases are properly ordered
- Dependencies make logical sense
- Completion percentages match actual code state
- Timeline reflects realistic project progression

## Example Output

Here's what the generated Gantt chart looks like when opened in GanttProject:

![WeatherAPI Gantt Chart Visualization](weatherapi_gantt_visualization.png)

**What you can see in the visualization:**
- **6 project phases** spanning Sept 1 - Nov 24, 2024
- **Phase completion status**: Setup and Core Development (100%), Advanced Features (75%), Testing (60%), Documentation (70%), Future Work (0%)
- **Task dependencies** shown by connecting arrows
- **Team member assignments** for each phase
- **Timeline view** showing when work occurred and is planned
- **Milestones** marking v0.1.0, v0.2.0, and v0.3.0 releases

This chart was generated entirely by LLM analysis of the project code, git history, and TODO comments!

### ⚠️ Important: This is a Preliminary Analysis

**LLM-generated Gantt charts require human review and validation.** The LLM inferred this timeline from code patterns and git history, but cannot guarantee 100% accuracy.

**Before using this chart for planning, validate:**
- Task accuracy and completeness
- Timeline estimates and dates
- Completion percentages
- Resource assignments
- Dependencies and project scope

**Use the generated `.gan` file as a starting point**, then refine it in GanttProject based on actual project requirements and domain knowledge.
