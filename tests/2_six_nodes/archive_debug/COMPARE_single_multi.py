"""
Compare Type1 behavior in single-node vs multi-node
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from neurolib.models.wendling import WendlingModel

print("="*80)
print("Compare Type1: Single-node vs Multi-node")
print("="*80)

# Test 1: Single node (N=1)
print("\nTest 1: SINGLE NODE (N=1)")
print("  Parameters: B=50, G=15, p_sigma=2.0")

Cmat1 = np.array([[0]])
Dmat1 = np.array([[0]])

model1 = WendlingModel(Cmat=Cmat1, Dmat=Dmat1, heterogeneity=0.0, seed=42, random_init=False)
model1.params['B'] = 50.0
model1.params['G'] = 15.0
model1.params['A'] = 5.0
model1.params['p_mean'] = 90.0
model1.params['p_sigma'] = 2.0
model1.params['duration'] = 10000
model1.params['dt'] = 0.1
model1.params['K_gl'] = 0.0

print("  Running...")
model1.run()

signal1 = model1.y1[0, :] - model1.y2[0, :] - model1.y3[0, :]
discard = int(2000 / 0.1)
s1 = signal1[discard:]

print(f"\n  Result:")
print(f"    mean = {np.mean(s1):.4f}")
print(f"    std  = {np.std(s1):.4f}")
print(f"    min  = {np.min(s1):.4f}")
print(f"    max  = {np.max(s1):.4f}")

# Test 2: Multi-node (N=3, all Type1, K_gl=0)
print("\n" + "-"*80)
print("Test 2: MULTI-NODE (N=3, all Type1, K_gl=0)")
print("  Parameters: B=50, G=15, p_sigma=2.0, heterogeneity=0.01, random_init=True")

Cmat3 = np.eye(3)
Dmat3 = np.zeros((3, 3))

model3 = WendlingModel(Cmat=Cmat3, Dmat=Dmat3, heterogeneity=0.01, seed=42, random_init=True)
model3.params['B'] = np.array([50.0, 50.0, 50.0])
model3.params['G'] = np.array([15.0, 15.0, 15.0])
model3.params['A'] = np.array([5.0, 5.0, 5.0])
model3.params['p_mean'] = np.array([90.0, 90.0, 90.0])
model3.params['p_sigma'] = 2.0
model3.params['duration'] = 10000
model3.params['dt'] = 0.1
model3.params['K_gl'] = 0.0

print("  Running...")
model3.run()

signals3 = np.zeros((3, len(model3.t)))
for i in range(3):
    signals3[i, :] = model3.y1[i, :] - model3.y2[i, :] - model3.y3[i, :]

print(f"\n  Results:")
for i in range(3):
    s = signals3[i, discard:]
    print(f"    Node {i}: mean={np.mean(s):.4f}, std={np.std(s):.4f}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Single-node std:  {np.std(s1):.4f}")
print(f"Multi-node std:   {np.std(signals3[0, discard:]):.4f}")

if np.std(s1) > 0.1 and np.std(signals3[0, discard:]) < 0.1:
    print("\nPROBLEM: Type1 works in single-node but NOT in multi-node!")
    print("This suggests an issue with multi-node initialization or parameter handling")
elif np.std(s1) < 0.1 and np.std(signals3[0, discard:]) < 0.1:
    print("\nType1 (B=50, G=15, p_sigma=2.0) does NOT oscillate with random_init=False OR True")
    print("This may be the expected behavior - Type1 needs different p_sigma?")
else:
    print("\nType1 oscillates normally in both cases")

print("="*80)
