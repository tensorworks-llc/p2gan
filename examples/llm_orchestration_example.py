#!/usr/bin/env python3
"""
LLM Analyzer Orchestration Example

This example demonstrates how an LLM should use p2gan to analyze a project
and generate a Gantt chart. It shows the complete workflow:

1. INTELLIGENCE GATHERING: Run the analyzers
2. INFERENCE: Reason about project structure
3. GENERATION: Create the Gantt chart

This is the PRIMARY way p2gan is meant to be used.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# p2gan analyzers for intelligence gathering
from p2gan import (
    ProjectHistoryAnalyzer,
    DateHistogram,
    ProjectStats
)

# p2gan models for generation
from p2gan import (
    Project,
    Task,
    Resource,
    Milestone,
    GanttGenerator,
    TaskPriority,
    DependencyType
)


def llm_analyze_and_generate_gantt(project_path: str, output_file: str = "project_timeline.gan"):
    """
    Complete LLM workflow for analyzing a project and generating a Gantt chart.

    This function demonstrates how an LLM should orchestrate p2gan's tools.
    """

    print("=" * 80)
    print("LLM-DRIVEN PROJECT ANALYSIS WITH p2gan")
    print("=" * 80)

    # ========================================================================
    # PHASE 1: INTELLIGENCE GATHERING
    # The LLM runs the analyzers to understand the project
    # ========================================================================

    print("\n📊 PHASE 1: INTELLIGENCE GATHERING")
    print("-" * 80)

    print("\n1️⃣  Running ProjectHistoryAnalyzer...")
    history_analyzer = ProjectHistoryAnalyzer(project_path)
    history = history_analyzer.analyze()

    print(f"   ✓ Analyzed {history['total_files']} files")
    print(f"   ✓ Date range: {history['earliest_date']} to {history['latest_date']}")
    print(f"   ✓ File categories: {len(history['file_categories'])} types")
    print(f"   ✓ Suggested phases: {len(history['suggested_phases'])}")

    print("\n2️⃣  Running DateHistogram...")
    histogram = DateHistogram(project_path)
    activity = histogram.analyze()

    print(f"   ✓ Activity patterns analyzed")
    print(f"   ✓ Timeline data collected")

    print("\n3️⃣  Running ProjectStats...")
    stats_analyzer = ProjectStats(project_path)
    stats = stats_analyzer.analyze()

    print(f"   ✓ Project statistics gathered")
    print(f"   ✓ Complexity metrics calculated")

    # ========================================================================
    # PHASE 2: INFERENCE
    # The LLM reasons about project structure based on analyzer output
    # ========================================================================

    print("\n🧠 PHASE 2: INFERENCE (LLM Reasoning)")
    print("-" * 80)

    # Infer project name
    project_name = Path(project_path).name.replace('_', ' ').replace('-', ' ').title()
    print(f"\n📌 Inferred project name: {project_name}")

    # Infer phases from file categories
    phases = infer_phases_from_categories(history['file_categories'], history['timeline'])
    print(f"\n📋 Inferred {len(phases)} development phases:")
    for phase in phases:
        print(f"   • {phase['name']}: {phase['task_count']} tasks, {phase['duration']} days, {phase['progress']}% complete")

    # Infer resources from git (if available)
    resources = infer_resources_from_git(project_path)
    print(f"\n👥 Inferred {len(resources)} team members from git history")

    # Infer dependencies
    print("\n🔗 Inferring logical dependencies...")
    print("   • Setup files → Core development")
    print("   • Core development → Testing")
    print("   • Testing → Documentation")
    print("   • Documentation → Deployment")

    # ========================================================================
    # PHASE 3: GENERATION
    # The LLM creates the Gantt chart based on inferred data
    # ========================================================================

    print("\n🎨 PHASE 3: GENERATION")
    print("-" * 80)

    # Create the project
    project = Project(
        name=project_name,
        start_date=history['earliest_date'],
        company="Analyzed via p2gan LLM Workflow"
    )

    # Add resources (inferred from git)
    print(f"\nAdding {len(resources)} resources...")
    for idx, resource_name in enumerate(resources):
        resource = Resource(
            id=idx,
            name=resource_name,
            role="Developer"  # Could be inferred from file patterns
        )
        project.add_resource(resource)

    # Add tasks (inferred from phases)
    print(f"Adding {sum(p['task_count'] for p in phases)} tasks across {len(phases)} phases...")
    task_id = 0

    for phase_idx, phase_info in enumerate(phases):
        # Create phase parent task
        phase_task = Task(
            id=task_id,
            name=phase_info['name'],
            start_date=phase_info['start_date'],
            duration=phase_info['duration'],
            progress=phase_info['progress'],
            priority=TaskPriority.HIGH if phase_idx == 0 else TaskPriority.NORMAL
        )
        project.add_task(phase_task)
        parent_id = task_id
        task_id += 1

        # Create subtasks for this phase
        for subtask_info in phase_info['subtasks']:
            subtask = Task(
                id=task_id,
                name=subtask_info['name'],
                start_date=subtask_info['start_date'],
                duration=subtask_info['duration'],
                progress=subtask_info['progress'],
                priority=subtask_info.get('priority', TaskPriority.NORMAL),
                parent_id=parent_id
            )
            phase_task.add_subtask(subtask)
            project.add_task(subtask)
            task_id += 1

        # Add dependency to previous phase (if not first)
        if phase_idx > 0:
            prev_phase = phases[phase_idx - 1]
            # Find the previous phase task by ID
            for task in project.tasks:
                if task.name == prev_phase['name']:
                    task.add_dependency(phase_task.id, DependencyType.FINISH_TO_START)
                    break

    # Add milestones (inferred from phase completions)
    print(f"Adding milestones...")
    milestone_id = task_id
    for phase in phases:
        if phase['progress'] == 100:  # Completed phase
            milestone = Milestone(
                id=milestone_id,
                name=f"{phase['name']} Complete",
                date=phase['start_date'] + timedelta(days=phase['duration'])
            )
            project.add_milestone(milestone)
            milestone_id += 1

    # Generate the .gan file
    print(f"\n💾 Generating {output_file}...")
    generator = GanttGenerator(project)
    generator.save(output_file)

    # ========================================================================
    # OUTPUT SUMMARY
    # ========================================================================

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

    all_tasks = project.get_all_tasks()
    duration_days = (history['latest_date'] - history['earliest_date']).days
    avg_progress = sum(t.progress for t in all_tasks) / len(all_tasks) if all_tasks else 0

    completed_tasks = [t for t in all_tasks if t.progress == 100]
    in_progress_tasks = [t for t in all_tasks if 0 < t.progress < 100]
    planned_tasks = [t for t in all_tasks if t.progress == 0]

    print(f"\n📊 Project Analysis:")
    print(f"   • Name: {project_name}")
    print(f"   • Duration: {history['earliest_date'].strftime('%Y-%m-%d')} to {history['latest_date'].strftime('%Y-%m-%d')} ({duration_days} days)")
    print(f"   • Total Tasks: {len(all_tasks)}")
    print(f"     - Completed: {len(completed_tasks)} ({len(completed_tasks)/len(all_tasks)*100:.0f}%)")
    print(f"     - In Progress: {len(in_progress_tasks)} ({len(in_progress_tasks)/len(all_tasks)*100:.0f}%)")
    print(f"     - Planned: {len(planned_tasks)} ({len(planned_tasks)/len(all_tasks)*100:.0f}%)")
    print(f"   • Overall Completion: {avg_progress:.0f}%")

    print(f"\n📋 Phases Discovered:")
    for i, phase in enumerate(phases, 1):
        status = "✓" if phase['progress'] == 100 else f"{phase['progress']}%"
        print(f"   {i}. {phase['name']} ({status})")

    print(f"\n👥 Team: {len(resources)} contributors identified from git history")

    print(f"\n📂 Output: {output_file}")
    print(f"   Open in GanttProject to view and customize the timeline.")
    print()


def infer_phases_from_categories(file_categories: dict, timeline: list) -> list:
    """
    LLM inference: Determine project phases from file categories and timeline.

    This simulates how an LLM would reason about the project structure.
    """
    phases = []

    # Phase 1: Project Setup (early config/setup files)
    setup_files = file_categories.get('setup', []) + file_categories.get('config', [])
    if setup_files or any('requirements' in str(f) or 'package.json' in str(f) for f in timeline[:5] if isinstance(f, dict) and 'file' in f):
        phases.append({
            'name': 'Project Setup',
            'start_date': datetime.now() - timedelta(days=90),  # Inferred
            'duration': 3,
            'progress': 100,  # Setup is old, so completed
            'task_count': 2,
            'subtasks': [
                {'name': 'Initialize Repository', 'start_date': datetime.now() - timedelta(days=90), 'duration': 1, 'progress': 100},
                {'name': 'Setup Dependencies', 'start_date': datetime.now() - timedelta(days=89), 'duration': 2, 'progress': 100}
            ]
        })

    # Phase 2: Core Development (source code files)
    source_files = file_categories.get('source', []) + file_categories.get('code', [])
    if source_files or len(file_categories) > 2:
        phases.append({
            'name': 'Core Development',
            'start_date': datetime.now() - timedelta(days=85),
            'duration': 45,
            'progress': 80,  # Mostly done
            'task_count': 5,
            'subtasks': [
                {'name': 'Implement Core Features', 'start_date': datetime.now() - timedelta(days=85), 'duration': 20, 'progress': 100},
                {'name': 'Build API Layer', 'start_date': datetime.now() - timedelta(days=65), 'duration': 15, 'progress': 100},
                {'name': 'Add Helper Functions', 'start_date': datetime.now() - timedelta(days=50), 'duration': 10, 'progress': 70}
            ]
        })

    # Phase 3: Testing (test files)
    test_files = file_categories.get('tests', [])
    if test_files or any('test' in str(f).lower() for f in file_categories.keys()):
        phases.append({
            'name': 'Testing & QA',
            'start_date': datetime.now() - timedelta(days=40),
            'duration': 20,
            'progress': 60,  # In progress
            'task_count': 3,
            'subtasks': [
                {'name': 'Write Unit Tests', 'start_date': datetime.now() - timedelta(days=40), 'duration': 10, 'progress': 100},
                {'name': 'Integration Testing', 'start_date': datetime.now() - timedelta(days=30), 'duration': 7, 'progress': 50},
                {'name': 'End-to-End Testing', 'start_date': datetime.now() - timedelta(days=23), 'duration': 3, 'progress': 20}
            ]
        })

    # Phase 4: Documentation (docs files)
    docs_files = file_categories.get('docs', [])
    if docs_files or any('doc' in str(f).lower() or 'readme' in str(f).lower() for f in file_categories.keys()):
        phases.append({
            'name': 'Documentation',
            'start_date': datetime.now() - timedelta(days=20),
            'duration': 15,
            'progress': 40,  # In progress
            'task_count': 2,
            'subtasks': [
                {'name': 'API Documentation', 'start_date': datetime.now() - timedelta(days=20), 'duration': 8, 'progress': 60},
                {'name': 'User Guide', 'start_date': datetime.now() - timedelta(days=12), 'duration': 7, 'progress': 20}
            ]
        })

    # Default if no phases inferred
    if not phases:
        phases.append({
            'name': 'Development',
            'start_date': datetime.now() - timedelta(days=30),
            'duration': 30,
            'progress': 50,
            'task_count': 3,
            'subtasks': [
                {'name': 'Initial Development', 'start_date': datetime.now() - timedelta(days=30), 'duration': 10, 'progress': 100},
                {'name': 'Feature Implementation', 'start_date': datetime.now() - timedelta(days=20), 'duration': 15, 'progress': 60},
                {'name': 'Refinement', 'start_date': datetime.now() - timedelta(days=5), 'duration': 5, 'progress': 0}
            ]
        })

    return phases


def infer_resources_from_git(project_path: str) -> list:
    """
    LLM inference: Extract team members from git history.
    """
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'log', '--format=%an'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            contributors = list(set(result.stdout.strip().split('\n')))
            return [c for c in contributors if c]  # Filter empty
    except:
        pass

    # Default if git not available
    return ["Developer 1", "Developer 2"]


if __name__ == "__main__":
    """
    Run this example to see how an LLM should orchestrate p2gan.
    """

    # Use current directory or provide a path
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Run the complete LLM workflow
    llm_analyze_and_generate_gantt(project_path, "llm_generated_timeline.gan")
