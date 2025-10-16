"""
DEBUG: Test Type1 behavior
"""

import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')
sys.path.insert(0, r'c:\Epilepsy_project\whole_brain_wendling\Validation_for_single_node')

import numpy as np
import matplotlib.pyplot as plt
from neurolib.models.wendling import WendlingModel
from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS

print("="*80)
print("DEBUG: Type1 (Background) Test")
print("="*80)

# Test 1: Single node, no coupling
print("\nTest 1: Single-node Type1 (should work)")
model1 = WendlingModel(Cmat=np.array([[0]]), Dmat=np.array([[0]]), heterogeneity=0.0, seed=42)
model1.params['duration'] = 5000
model1.params['dt'] = 0.1
model1.params['K_gl'] = 0.0

params_type1 = WENDLING_STANDARD_PARAMS['Type1']['params']
model1.params['B'] = params_type1['B']  # 50
model1.params['G'] = params_type1['G']  # 15
model1.params['p_sigma'] = params_type1['p_sigma']  # 30.0

print(f"  B={model1.params['B']}, G={model1.params['G']}, p_sigma={model1.params['p_sigma']}")
print(f"  Running...")
model1.run()

signal1 = model1.y1[0, :] - model1.y2[0, :] - model1.y3[0, :]
print(f"  Signal: mean={np.mean(signal1):.4f}, std={np.std(signal1):.4f}, min={np.min(signal1):.4f}, max={np.max(signal1):.4f}")

# Test 2: 2 nodes, with coupling
print("\nTest 2: 2-node Type1, K_gl=0.10")
Cmat2 = np.array([[0, 1.0], [1.0, 0]])
Dmat2 = np.array([[0, 30], [30, 0]])

model2 = WendlingModel(Cmat=Cmat2, Dmat=Dmat2, heterogeneity=0.0, seed=42)
model2.params['duration'] = 5000
model2.params['dt'] = 0.1
model2.params['K_gl'] = 0.10

model2.params['B'] = np.array([50.0, 50.0])
model2.params['G'] = np.array([15.0, 15.0])
model2.params['p_sigma'] = 30.0

print(f"  B={model2.params['B']}, G={model2.params['G']}, K_gl={model2.params['K_gl']}")
print(f"  Running...")
model2.run()

signal2_n0 = model2.y1[0, :] - model2.y2[0, :] - model2.y3[0, :]
signal2_n1 = model2.y1[1, :] - model2.y2[1, :] - model2.y3[1, :]
print(f"  Node 0: mean={np.mean(signal2_n0):.4f}, std={np.std(signal2_n0):.4f}, min={np.min(signal2_n0):.4f}, max={np.max(signal2_n0):.4f}")
print(f"  Node 1: mean={np.mean(signal2_n1):.4f}, std={np.std(signal2_n1):.4f}, min={np.min(signal2_n1):.4f}, max={np.max(signal2_n1):.4f}")

# Test 3: Try Type4 instead (should have clear oscillations)
print("\nTest 3: Single-node Type4 (Alpha) for comparison")
model3 = WendlingModel(Cmat=np.array([[0]]), Dmat=np.array([[0]]), heterogeneity=0.0, seed=42)
model3.params['duration'] = 5000
model3.params['dt'] = 0.1
model3.params['K_gl'] = 0.0

params_type4 = WENDLING_STANDARD_PARAMS['Type4']['params']
model3.params['B'] = params_type4['B']  # 10
model3.params['G'] = params_type4['G']  # 15
model3.params['p_sigma'] = params_type4['p_sigma']  # 30.0

print(f"  B={model3.params['B']}, G={model3.params['G']}, p_sigma={model3.params['p_sigma']}")
print(f"  Running...")
model3.run()

signal3 = model3.y1[0, :] - model3.y2[0, :] - model3.y3[0, :]
print(f"  Signal: mean={np.mean(signal3):.4f}, std={np.std(signal3):.4f}, min={np.min(signal3):.4f}, max={np.max(signal3):.4f}")

# Plot comparison
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Test 1
ax = axes[0]
window = 2000
idx = int(window / 0.1)
ax.plot(model1.t[:idx], signal1[:idx], linewidth=0.8)
ax.set_title(f'Test 1: Single-node Type1 (B=50, G=15) - std={np.std(signal1):.4f}', fontweight='bold')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('mV')
ax.grid(True, alpha=0.3)

# Test 2
ax = axes[1]
ax.plot(model2.t[:idx], signal2_n0[:idx], linewidth=0.8, label='Node 0')
ax.plot(model2.t[:idx], signal2_n1[:idx], linewidth=0.8, label='Node 1', alpha=0.7)
ax.set_title(f'Test 2: 2-node Type1 with coupling (K_gl=0.10) - std={np.std(signal2_n0):.4f}', fontweight='bold')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('mV')
ax.legend()
ax.grid(True, alpha=0.3)

# Test 3
ax = axes[2]
ax.plot(model3.t[:idx], signal3[:idx], linewidth=0.8, color='green')
ax.set_title(f'Test 3: Single-node Type4 (B=10, G=15) - std={np.std(signal3):.4f}', fontweight='bold')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('mV')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../../results/six_nodes/DEBUG_type1_test.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: ../../results/six_nodes/DEBUG_type1_test.png")
plt.close()

print("\n" + "="*80)
print("CONCLUSION:")
if np.std(signal1) < 0.1:
    print("  ❌ Type1 single-node does NOT oscillate (std too small)")
    print("  → Type1 parameters may be incorrect or need different p_sigma")
else:
    print(f"  ✅ Type1 single-node oscillates (std={np.std(signal1):.4f})")
    
if np.std(signal2_n0) < 0.1:
    print("  ❌ Type1 with coupling FAILS (std too small)")
    print("  → Coupling may suppress Type1 oscillations")
else:
    print(f"  ✅ Type1 with coupling works (std={np.std(signal2_n0):.4f})")

print("="*80)
