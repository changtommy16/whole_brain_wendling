"""
Evaluation function for neurolib Evolution optimization.
Windows multiprocessing compatible - uses LAZY IMPORTS inside function.
"""

import numpy as np
import logging

# Constants (safe to define at module level)
TARGET_FREQ = 10.0  # Hz
PARAM_NAMES = ['B', 'G']

# Global evolution object - set by main script for single-core mode
evolution = None


def evaluateSimulation(traj):
    """
    Evaluation function for neurolib Evolution.
    Uses LAZY IMPORTS to support Windows multiprocessing (spawn mode).
    """
    global evolution
    
    # LAZY IMPORTS - critical for Windows multiprocessing!
    import sys
    sys.path.insert(0, r"C:\Epilepsy_project\Neurolib_desktop\Neurolib_package")
    from neurolib.models.wendling import WendlingModel
    import neurolib.utils.functions as func
    
    rid = traj.id
    logging.info(f"Running run id {rid}")
    
    # For multiprocessing: create fresh model and set params from traj.individual
    model = WendlingModel()
    individual = list(traj.individual)
    for i, param_name in enumerate(PARAM_NAMES):
        if i < len(individual):
            model.params[param_name] = individual[i]
    
    # Simulation parameters
    model.params['dt'] = 0.1
    model.params['duration'] = 2 * 1000.  # 2 seconds
    
    # Run
    model.run()
    
    # Power spectrum
    frs, powers = func.getPowerSpectrum(
        model.output[:, -int(1000/model.params['dt']):], 
        dt=model.params['dt']
    )
    
    # Peak frequency
    domfr = frs[np.argmax(powers)]
    
    # Fitness: distance to target (minimize)
    fitness = abs(domfr - TARGET_FREQ)
    
    return (fitness,), model.outputs
