"""
Clean up debug files and organize 2_six_nodes directory
"""

import os
import shutil

# Current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create archive directory
archive_dir = os.path.join(current_dir, "archive_debug")
os.makedirs(archive_dir, exist_ok=True)

# Files to archive (debug files and temporary outputs)
files_to_archive = [
    "COMPARE_single_multi.py",
    "DEBUG_k_gl_zero.py",
    "DEBUG_param_override.py",
    "DEBUG_params_check.py",
    "DEBUG_type1.py",
    "SIMPLE_TEST.py",
    "TEST_type1_alone.py",
    "compare_result.txt",
    "debug_full.txt",
    "debug_output.txt",
    "debug_run.txt",
    "output.txt",
    "param_test.txt",
    "simple_10sec.txt",
    "simple_random_true.txt",
    "simple_test_output.txt",
    "type1_test.txt",
]

# Core test files to keep
core_files = [
    "test_00_unit_test_heterogeneity.py",
    "test_01_heterogeneity_sweep.py",
    "test_02_optimal_params.py",
    "test_03_complete_analysis_FIXED.py",
    "test_04_six_types_network.py",
    "README.md",
    "CLEANUP.py",
]

print("="*80)
print("Cleaning up 2_six_nodes directory")
print("="*80)

# Move debug files to archive
moved_count = 0
for filename in files_to_archive:
    src = os.path.join(current_dir, filename)
    if os.path.exists(src):
        dst = os.path.join(archive_dir, filename)
        shutil.move(src, dst)
        print(f"Moved: {filename} -> archive_debug/")
        moved_count += 1

print(f"\nMoved {moved_count} files to archive_debug/")

# List remaining files
print(f"\nRemaining core files:")
for filename in sorted(os.listdir(current_dir)):
    if filename != "archive_debug" and not filename.startswith('.'):
        filepath = os.path.join(current_dir, filename)
        if os.path.isfile(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  {filename:<45} ({size_kb:>6.1f} KB)")

print("\n" + "="*80)
print("Cleanup complete!")
print("="*80)
print("\nDirectory structure:")
print("  2_six_nodes/")
print("    ├── test_00_unit_test_heterogeneity.py")
print("    ├── test_01_heterogeneity_sweep.py")
print("    ├── test_02_optimal_params.py")
print("    ├── test_03_complete_analysis_FIXED.py  ⭐ Main analysis")
print("    ├── test_04_six_types_network.py")
print("    ├── README.md")
print("    └── archive_debug/                      (debug files)")
print("="*80)
