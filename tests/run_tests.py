#!/usr/bin/env python3
"""
Test runner script for p2gan.
Can be used locally or in CI/CD pipelines.
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"❌ {description} failed!")
        return False

    print(f"✅ {description} passed!")
    return True


def main():
    """Run all tests and quality checks."""

    # Change to project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)

    print("\n" + "="*60)
    print("P2GAN TEST SUITE")
    print("="*60)

    all_passed = True

    # 1. Run pytest
    if not run_command(
        ["python", "-m", "pytest", "tests/", "-v"],
        "Unit Tests (pytest)"
    ):
        all_passed = False

    # 2. Run pytest with coverage
    if not run_command(
        ["python", "-m", "pytest", "tests/", "--cov=p2gan", "--cov-report=term-missing"],
        "Test Coverage"
    ):
        all_passed = False

    # 3. Check code formatting with black (check only)
    if not run_command(
        ["python", "-m", "black", "src/p2gan/", "tests/", "--check"],
        "Code Formatting (black)"
    ):
        print("Tip: Run 'black src/p2gan/ tests/' to auto-format")
        all_passed = False

    # 4. Run flake8 linting
    if not run_command(
        ["python", "-m", "flake8", "src/p2gan/", "--max-line-length=88", "--exclude=__pycache__"],
        "Linting (flake8)"
    ):
        all_passed = False

    # 5. Run type checking with mypy (if installed)
    try:
        import mypy
        if not run_command(
            ["python", "-m", "mypy", "src/p2gan/", "--ignore-missing-imports"],
            "Type Checking (mypy)"
        ):
            all_passed = False
    except ImportError:
        print("\n⚠️  Skipping mypy (not installed)")

    # 6. Check that package can be imported
    print("\n" + "="*60)
    print("Checking package import...")
    try:
        import p2gan
        print(f"✅ Successfully imported p2gan version {p2gan.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import package: {e}")
        all_passed = False

    # Final report
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues above before committing.")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())