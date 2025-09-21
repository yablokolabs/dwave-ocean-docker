#!/usr/bin/env python3
"""
Quick Start Example for D-Wave Ocean SDK
This is a simple example to verify your D-Wave setup is working.
"""

import dimod
from dwave.samplers import SimulatedAnnealingSampler

def quick_test():
    """Run a quick test to verify D-Wave Ocean SDK is working."""
    print("🌊 D-Wave Ocean SDK Quick Start Test")
    print("=" * 40)
    
    try:
        # Create a simple QUBO: minimize x - y + xy
        Q = {('x', 'x'): 1, ('y', 'y'): -1, ('x', 'y'): 1}
        bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
        
        print(f"✓ Created BQM with {len(bqm.variables)} variables")
        
        # Solve using simulated annealing
        sampler = SimulatedAnnealingSampler()
        sampleset = sampler.sample(bqm, num_reads=100)
        
        print(f"✓ Solved with {len(sampleset)} samples")
        
        # Show best result
        best = sampleset.first
        print(f"✓ Best solution: x={best.sample['x']}, y={best.sample['y']}")
        print(f"✓ Best energy: {best.energy}")
        
        # Verify the result makes sense
        x, y = best.sample['x'], best.sample['y']
        expected_energy = x - y + x*y
        
        if abs(best.energy - expected_energy) < 1e-6:
            print("✓ Energy calculation verified")
            print("\n🎉 D-Wave Ocean SDK is working correctly!")
            return True
        else:
            print(f"✗ Energy mismatch: got {best.energy}, expected {expected_energy}")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🚀 Ready to explore quantum annealing!")
        print("   Try running: python basic_examples.py")
        print("   Or: python tsp_example.py")
    else:
        print("\n❌ Setup verification failed")