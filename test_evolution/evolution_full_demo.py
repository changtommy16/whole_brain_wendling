"""
Neurolib Evolution Demo - Wendling Model (Official Style)
==========================================================
使用 neurolib 原生 API 和視覺化

Usage:
    conda activate modeling
    python evolution_full_demo.py
"""

if __name__ == '__main__':
    import sys
    import os
    import logging
    import numpy as np
    
    logging.basicConfig(level=logging.INFO)
    
    sys.path.insert(0, r"C:\Epilepsy_project\Neurolib_desktop\Neurolib_package")
    
    from neurolib.models.wendling import WendlingModel
    from neurolib.utils.parameterSpace import ParameterSpace
    from neurolib.optimize.evolution import Evolution
    import neurolib.utils.functions as func
    
    from eval_function import evaluateSimulation, TARGET_FREQ
    
    # ============================================================
    # Setup
    # ============================================================
    print("=" * 60)
    print("Neurolib Evolution - Wendling Model")
    print("=" * 60)
    
    os.makedirs("./data/hdf", exist_ok=True)
    os.makedirs("./data/figures", exist_ok=True)
    
    # ============================================================
    # Parameter Space
    # ============================================================
    pars = ParameterSpace(
        ['B', 'G'], 
        [[5.0, 50.0], [0.0, 25.0]]
    )
    
    print(f"Parameter space: {pars.parameters}")
    print(f"Target frequency: {TARGET_FREQ} Hz")
    
    # ============================================================
    # Initialize Evolution (with multiprocessing!)
    # ============================================================
    wendling = WendlingModel()
    
    evolution = Evolution(
        evalFunction=evaluateSimulation,
        parameterSpace=pars,
        model=wendling,
        weightList=[-1.0],
        POP_INIT_SIZE=16,
        POP_SIZE=8,
        NGEN=4,
        filename="wendling_demo.hdf",
        ncores=4  # Multiprocessing enabled!
    )
    
    print(f"ncores: {evolution.ncores}")
    
    # ============================================================
    # Run Evolution (verbose=True for native plots)
    # ============================================================
    print("\nRunning evolution with verbose=True...")
    print("(Native neurolib plots will be generated each generation)")
    print("-" * 60)
    
    evolution.run(verbose=True)
    
    # ============================================================
    # Native Analysis Functions
    # ============================================================
    print("\n" + "=" * 60)
    print("Analysis using native neurolib functions")
    print("=" * 60)
    
    # evolution.dfPop() - Current population
    print("\n>>> evolution.dfPop():")
    print(evolution.dfPop())
    
    # evolution.dfEvolution() - All individuals
    print("\n>>> evolution.dfEvolution() (first 10 rows):")
    print(evolution.dfEvolution().head(10))
    
    # evolution.toolbox.selBest() - Best individuals
    print("\n>>> Best 3 individuals:")
    best_3 = evolution.toolbox.selBest(evolution.pop, k=3)
    for i, ind in enumerate(best_3):
        print(f"    #{i+1}: B={ind[0]:.2f}, G={ind[1]:.2f}, fitness={ind.fitness.values}")
    
    # evolution.info(plot=True) - Official visualization
    print("\n>>> evolution.info(plot=True):")
    evolution.info(plot=True)
    
    print("\n" + "=" * 60)
    print("Done! Check ./data/figures/ for plots")
    print("=" * 60)
