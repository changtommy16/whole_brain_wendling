"""
Check if vectorized B and G are correctly used
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from neurolib.models.wendling import WendlingModel

print("="*80)
print("DEBUG: Check Vectorized Parameters")
print("="*80)

N = 2
Cmat = np.array([[0, 1.0], [1.0, 0]])
Dmat = np.array([[0, 30], [30, 0]])

model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.0, seed=42, random_init=False)

# Set different B and G for each node
B_set = np.array([25.0, 15.0])
G_set = np.array([15.0, 0.0])

print(f"\nSetting parameters:")
print(f"  B_set = {B_set}")
print(f"  G_set = {G_set}")

model.params['B'] = B_set
model.params['G'] = G_set

print(f"\nAfter setting:")
print(f"  model.params['B'] = {model.params['B']}")
print(f"  model.params['G'] = {model.params['G']}")
print(f"  Type: B is {type(model.params['B'])}, shape={np.shape(model.params['B'])}")
print(f"  Type: G is {type(model.params['G'])}, shape={np.shape(model.params['G'])}")

# Check if they are scalar or vector
if np.isscalar(model.params['B']) or len(np.shape(model.params['B'])) == 0:
    print(f"\n  WARNING: B is scalar! Should be vector for N={N}")
elif len(model.params['B']) != N:
    print(f"\n  WARNING: B length ({len(model.params['B'])}) != N ({N})")
else:
    print(f"\n  OK: B is vector with correct length")

if np.isscalar(model.params['G']) or len(np.shape(model.params['G'])) == 0:
    print(f"\n  WARNING: G is scalar! Should be vector for N={N}")
elif len(model.params['G']) != N:
    print(f"\n  WARNING: G length ({len(model.params['G'])}) != N ({N})")
else:
    print(f"\n  OK: G is vector with correct length")

print("="*80)
