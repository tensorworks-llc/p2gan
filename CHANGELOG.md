# Changelog

All notable changes to p2gan will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PyPI package structure with modern pyproject.toml
- Comprehensive test suite with pytest
- GitHub Actions CI/CD workflows
- Professional documentation (README, CONTRIBUTING, LICENSE)
- Sample projects in samples/ directory
- Utility scripts in utilities/ directory

### Changed
- Renamed package from ganttproject_python to p2gan for PyPI
- Reorganized project structure for better maintainability
- Moved documentation to docs/ directory
- Improved code organization

### Fixed
- Circular dependency handling in task hierarchies
- Business day calculations for task scheduling
- XML generation for GanttProject 3.2+ compatibility

## [0.1.0] - 2025-10-06

### Added
- Initial release as p2gan
- Core data models (Project, Task, Resource, Milestone)
- Markdown parser for project plans
- XML generator for .gan files
- Command-line interface
- Support for all dependency types (FS, SS, FF, SF)
- Resource allocation management
- Task priorities and progress tracking
- Hierarchical task structures
- Custom task properties
- Stakeholder analysis tools
- Project history analyzer
- Date histogram utility
- Project statistics calculator

### Features
- Convert markdown to GanttProject files
- Programmatic project creation
- Full GanttProject 3.2 compatibility
- Zero external dependencies
- Business day calculations
- CDATA support for special characters

### Known Issues
- No import from .gan files (read-only)
- Limited calendar customization
- No real-time collaboration features

## [0.0.1] - 2025-09-15

### Added
- Initial prototype
- Basic task and resource models
- Simple XML generation
- Proof of concept markdown parsing

---

## Version History Summary

- **0.1.0** (2025-10-06): First functional release
- **0.0.1** (2025-09-15): Initial prototype

## Upgrade Guide

### Upgrading to p2gan 0.2.0

1. **Update imports:**
   ```python
   # Old
   from ganttproject import Project, Task

   # New (same - internal package name unchanged)
   from ganttproject import Project, Task
   ```

2. **Update CLI commands:**
   ```bash
   # Old
   python -m ganttproject convert input.md output.gan

   # New
   p2gan convert input.md output.gan
   ```

3. **File reorganization:**
   - Sample files moved to `samples/`
   - Documentation moved to `docs/`
   - Utilities moved to `utilities/`

## Roadmap

### v0.2.0 (Next Release)
- [ ] Complete test coverage (>80%)
- [ ] Import .gan files
- [ ] Export to HTML reports
- [ ] Custom calendar support

### v0.3.0
- [ ] CSV/Excel import
- [ ] Critical path calculation
- [ ] Resource leveling

### v0.4.0
- [ ] Web UI prototype
- [ ] API server mode
- [ ] Real-time updates

### v1.0.0
- [ ] Production ready
- [ ] Full documentation
- [ ] Performance optimized
- [ ] Enterprise features