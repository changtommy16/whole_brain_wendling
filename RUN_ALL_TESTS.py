"""
Run All Tests - Complete Project Validation

Executes all stages automatically without GUI interruption.
"""

import subprocess
import sys
import time
from pathlib import Path

print("="*80)
print("WENDLING WHOLE-BRAIN NETWORK - COMPLETE TEST SUITE")
print("="*80)

base_dir = Path(__file__).parent

tests = [
    ("Stage 2: 6-nodes validation", "tests/2_six_nodes/test_03_complete_analysis.py"),
    ("Stage 3: 20-nodes modular", "tests/3_twenty_nodes/test_01_modular_network.py"),
    ("Stage 4: 80-nodes scalability", "tests/4_hcp_data/test_01_scalability.py"),
]

results = []
total_start = time.time()

for stage_name, test_path in tests:
    print(f"\n{'='*80}")
    print(f"Running: {stage_name}")
    print(f"Script: {test_path}")
    print(f"{'='*80}\n")
    
    test_file = base_dir / test_path
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        results.append((stage_name, "FAILED", "File not found"))
        continue
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max per test
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(result.stdout)
            results.append((stage_name, "PASSED", f"{elapsed:.1f}s"))
            print(f"\n✅ {stage_name} - PASSED ({elapsed:.1f}s)")
        else:
            print(result.stdout)
            print(result.stderr)
            results.append((stage_name, "FAILED", f"{elapsed:.1f}s"))
            print(f"\n❌ {stage_name} - FAILED")
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        results.append((stage_name, "TIMEOUT", f"{elapsed:.1f}s"))
        print(f"\n⏱️ {stage_name} - TIMEOUT (>{elapsed:.1f}s)")
        
    except Exception as e:
        elapsed = time.time() - start_time
        results.append((stage_name, "ERROR", str(e)))
        print(f"\n❌ {stage_name} - ERROR: {e}")

total_time = time.time() - total_start

# Summary
print("\n" + "="*80)
print("TEST SUITE SUMMARY")
print("="*80)

for stage_name, status, info in results:
    status_symbol = "✅" if status == "PASSED" else "❌"
    print(f"{status_symbol} {stage_name}: {status} ({info})")

print(f"\nTotal execution time: {total_time:.1f}s")

all_passed = all(status == "PASSED" for _, status, _ in results)

if all_passed:
    print("\n🎉 ALL TESTS PASSED! 🎉")
    print("Project is fully validated and ready to use.")
else:
    print("\n⚠️ Some tests failed. Please check the output above.")

print("="*80)

# Exit code
sys.exit(0 if all_passed else 1)
