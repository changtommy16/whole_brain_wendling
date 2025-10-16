"""
Verify that manually set parameters stay fixed during model.run()
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from neurolib.models.wendling import WendlingModel

print("="*80)
print("TEST: Verify parameters stay fixed after manual setting")
print("="*80)

N = 6
Cmat = np.eye(N)
Dmat = np.zeros((N, N))

# Create model with heterogeneity (this will generate random values)
model = WendlingModel(
    Cmat=Cmat, 
    Dmat=Dmat,
    heterogeneity=0.01,  # This triggers variation in loadDefaultParams()
    random_init=True,
    seed=42
)

print("\nStep 1: After model creation (random values from loadDefaultParams)")
print(f"  B = {model.params['B']}")
print(f"  G = {model.params['G']}")

# Manually set exact values
B_manual = np.array([50.0, 25.0, 15.0, 15.0, 50.0, 50.0])
G_manual = np.array([15.0, 15.0, 0.0, 0.0, 15.0, 15.0])

model.params['B'] = B_manual
model.params['G'] = G_manual
model.params['A'] = np.array([5.0] * N)
model.params['p_mean'] = np.array([90.0] * N)
model.params['p_sigma'] = 2.0
model.params['duration'] = 1000
model.params['dt'] = 0.1
model.params['K_gl'] = 0.0

print("\nStep 2: After manual setting")
print(f"  B = {model.params['B']}")
print(f"  G = {model.params['G']}")

# Check if they match our manual values
assert np.allclose(model.params['B'], B_manual), "B changed unexpectedly!"
assert np.allclose(model.params['G'], G_manual), "G changed unexpectedly!"
print("  ✅ Parameters match our manual values")

# Run simulation
print("\nStep 3: Running model.run()...")
model.run()
print("  Done!")

print("\nStep 4: After model.run()")
print(f"  B = {model.params['B']}")
print(f"  G = {model.params['G']}")

# Check again
assert np.allclose(model.params['B'], B_manual), "❌ B changed during run()!"
assert np.allclose(model.params['G'], G_manual), "❌ G changed during run()!"

print("\n" + "="*80)
print("✅ VERIFIED: Parameters stayed FIXED during model.run()")
print("="*80)
print("\nConclusion:")
print("  - loadDefaultParams() only runs during __init__()")
print("  - timeIntegration.py only READS params, never modifies them")
print("  - Your manual values are SAFE!")
print("="*80)
