import sys
sys.path.insert(0, r'c:\Epilepsy_project\Neurolib_desktop\Neurolib_package')
sys.path.insert(0, r'c:\Epilepsy_project\whole_brain_wendling\Validation_for_single_node')

import numpy as np
from neurolib.models.wendling import WendlingModel
from STANDARD_PARAMETERS import WENDLING_STANDARD_PARAMS

N = 6
NODE_TYPES = ['Type1', 'Type3', 'Type6', 'Type6', 'Type1', 'Type1']

Cmat = np.eye(N)
Dmat = np.zeros((N, N))

# Use heterogeneity=0.01 to trigger vector mode
model = WendlingModel(Cmat=Cmat, Dmat=Dmat, heterogeneity=0.01, seed=42, random_init=True)

# Prepare parameters
B_vals = np.zeros(N)
G_vals = np.zeros(N)
A_vals = np.zeros(N)
p_mean_vals = np.zeros(N)

for i, node_type in enumerate(NODE_TYPES):
    params = WENDLING_STANDARD_PARAMS[node_type]['params']
    B_vals[i] = params['B']
    G_vals[i] = params['G']
    A_vals[i] = params['A']
    p_mean_vals[i] = params['p_mean']

print("Target parameters:")
print(f"  B_vals = {B_vals}")
print(f"  G_vals = {G_vals}")

# Assign
model.params['B'] = B_vals
model.params['G'] = G_vals
model.params['A'] = A_vals
model.params['p_mean'] = p_mean_vals
model.params['p_sigma'] = 2.0
model.params['duration'] = 10000  # Use 10 seconds like complete_analysis
model.params['dt'] = 0.1
model.params['K_gl'] = 0.0

print("\nAfter assignment:")
print(f"  model.params['B'] = {model.params['B']}")
print(f"  model.params['G'] = {model.params['G']}")

print("\nRunning...")
model.run()

print("\nAfter run():")
print(f"  model.params['B'] = {model.params['B']}")
print(f"  model.params['G'] = {model.params['G']}")

# Check signals
signals = np.zeros((N, len(model.t)))
for i in range(N):
    signals[i, :] = model.y1[i, :] - model.y2[i, :] - model.y3[i, :]

discard = int(200 / 0.1)
for i in range(N):
    s = signals[i, discard:]
    print(f"\nNode {i} ({NODE_TYPES[i]}): B={model.params['B'][i]:.1f}, G={model.params['G'][i]:.1f}")
    print(f"  mean={np.mean(s):.2f}, std={np.std(s):.2f}")
