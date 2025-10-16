import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')

import numpy as np
from neurolib.models.wendling import WendlingModel

print("="*80)
print("Test: Type1 in multi-node with random_init=False")
print("="*80)

N = 3
Cmat = np.eye(N)
Dmat = np.zeros((N, N))

# Test: 3 nodes, all Type1
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42, random_init=False)

B_vals = np.array([50.0, 50.0, 50.0])
G_vals = np.array([15.0, 15.0, 15.0])
A_vals = np.array([5.0, 5.0, 5.0])
p_mean_vals = np.array([90.0, 90.0, 90.0])

model.params['B'] = B_vals
model.params['G'] = G_vals
model.params['A'] = A_vals
model.params['p_mean'] = p_mean_vals
model.params['p_sigma'] = 2.0
model.params['duration'] = 10000
model.params['dt'] = 0.1
model.params['K_gl'] = 0.0

print(f"\nParameters: B=50, G=15, p_sigma=2.0, random_init=False")
print(f"Running...")
model.run()

signals = np.zeros((N, len(model.t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

discard = int(2000 / 0.1)
for i in range(N):
    s = signals[i, discard:]
    print(f"\nNode {i}: mean={np.mean(s):.2f}, std={np.std(s):.4f}")

if np.std(signals[0, discard:]) < 0.1:
    print(f"\n❌ PROBLEM: Type1 has no oscillation in multi-node!")
    print(f"   This suggests the issue is with multi-node + Type1 + random_init=False")
else:
    print(f"\n✅ Type1 works fine in multi-node")

# Compare: Try with random_init=True
print(f"\n" + "="*80)
print("Comparing with random_init=True")
print("="*80)

model2 = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42, random_init=True)
model2.params['B'] = B_vals
model2.params['G'] = G_vals
model2.params['A'] = A_vals
model2.params['p_mean'] = p_mean_vals
model2.params['p_sigma'] = 2.0
model2.params['duration'] = 10000
model2.params['dt'] = 0.1
model2.params['K_gl'] = 0.0

print(f"Running with random_init=True...")
model2.run()

signals2 = np.zeros((N, len(model2.t)))
for i in range(N):
    signals2[i, :] = model2.y1[i, :] - model2.y2[i, :] - model2.y3[i, :]

for i in range(N):
    s = signals2[i, discard:]
    print(f"Node {i}: mean={np.mean(s):.2f}, std={np.std(s):.4f}")

print("="*80)
