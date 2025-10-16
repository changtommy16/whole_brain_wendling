"""
Test if we can override parameters in heterogeneity mode
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from neurolib.models.wendling import WendlingModel

print("="*80)
print("TEST: Parameter Override in Heterogeneity Mode")
print("="*80)

N = 3
Cmat = np.eye(N)
Dmat = np.zeros((N, N))

# Test 1: heterogeneity=0.01
print("\nTest 1: Create model with heterogeneity=0.01")
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42, random_init=False)

print(f"  Initial B: {model.params['B']}")
print(f"  Initial G: {model.params['G']}")

# Try to override
B_new = np.array([50.0, 25.0, 15.0])
G_new = np.array([15.0, 15.0, 0.0])
A_new = np.array([5.0, 5.0, 5.0])
p_mean_new = np.array([90.0, 90.0, 90.0])

print(f"\nSetting new values:")
print(f"  B_new = {B_new}")
print(f"  G_new = {G_new}")

model.params['B'] = B_new
model.params['G'] = G_new
model.params['A'] = A_new
model.params['p_mean'] = p_mean_new

print(f"\nAfter assignment:")
print(f"  model.params['B'] = {model.params['B']}")
print(f"  model.params['G'] = {model.params['G']}")
print(f"  model.params['A'] = {model.params['A']}")
print(f"  model.params['p_mean'] = {model.params['p_mean']}")

# Check if they match
if np.allclose(model.params['B'], B_new):
    print(f"\n  OK: B was set correctly")
else:
    print(f"\n  ERROR: B mismatch!")
    print(f"    Expected: {B_new}")
    print(f"    Got: {model.params['B']}")

if np.allclose(model.params['G'], G_new):
    print(f"  OK: G was set correctly")
else:
    print(f"  ERROR: G mismatch!")
    print(f"    Expected: {G_new}")
    print(f"    Got: {model.params['G']}")

print("\n" + "="*80)
print("Running simulation to check if parameters persist...")
print("="*80)

model.params['duration'] = 1000
model.params['dt'] = 0.1
model.params['K_gl'] = 0.0
model.run()

print(f"\nAfter model.run():")
print(f"  model.params['B'] = {model.params['B']}")
print(f"  model.params['G'] = {model.params['G']}")

if np.allclose(model.params['B'], B_new):
    print(f"\n  OK: B persisted after run()")
else:
    print(f"\n  ERROR: B changed after run()!")
    print(f"    Expected: {B_new}")
    print(f"    Got: {model.params['B']}")

print("="*80)
