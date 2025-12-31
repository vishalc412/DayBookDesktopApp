"""
Python Syntax Validation Test
Compiles all Python files to check for syntax errors
"""

import py_compile
import os
import sys
from pathlib import Path

def test_file_syntax(file_path):
    """Test Python file syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def find_python_files(directory):
    """Find all Python files in directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files

def main():
    print("=" * 60)
    print("DAYBOOK V2.0 - PYTHON SYNTAX VALIDATION")
    print("=" * 60)
    print()

    # Get all Python files in app directory
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    python_files = find_python_files(app_dir)

    print(f"Found {len(python_files)} Python files to check")
    print()

    passed = 0
    failed = 0
    errors = []

    # New modules to highlight
    new_modules = [
        'security', 'calculations', 'savings',
        'precious_metals', 'expenses', 'models_registry'
    ]

    for file_path in sorted(python_files):
        relative_path = os.path.relpath(file_path, app_dir)

        # Check if it's a new module
        is_new = any(module in file_path for module in new_modules)
        prefix = "[NEW] " if is_new else "      "

        success, error = test_file_syntax(file_path)

        if success:
            print(f"✓ {prefix}{relative_path}")
            passed += 1
        else:
            print(f"✗ {prefix}{relative_path}")
            print(f"  Error: {error}")
            failed += 1
            errors.append((relative_path, error))

    print()
    print("=" * 60)
    print(f"SUMMARY: {passed}/{len(python_files)} files passed syntax check")

    if failed > 0:
        print(f"⚠ {failed} files FAILED")
        print()
        print("ERRORS:")
        for file, error in errors:
            print(f"\n{file}:")
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✓ ALL FILES PASSED - No syntax errors!")
        sys.exit(0)

if __name__ == "__main__":
    main()
