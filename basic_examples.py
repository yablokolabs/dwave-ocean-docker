#!/usr/bin/env python3
"""
Basic D-Wave Ocean SDK Examples
This file contains several basic examples demonstrating D-Wave Ocean SDK functionality.
"""

import dimod
from dwave.system import DWaveSampler, EmbeddingComposite
from dwave.samplers import SimulatedAnnealingSampler
import networkx as nx

# Try to import dwavebinarycsp, fall back if not available
try:
    import dwavebinarycsp
    CSP_AVAILABLE = True
except ImportError:
    CSP_AVAILABLE = False
    print("Note: dwavebinarycsp not available, skipping CSP example")


def example_1_basic_qubo():
    """
    Example 1: Basic QUBO (Quadratic Unconstrained Binary Optimization) problem
    This example shows how to define and solve a simple QUBO problem.
    """
    print("=== Example 1: Basic QUBO Problem ===")
    
    # Define a simple QUBO problem
    # Minimize: x0 - 2*x1 + 3*x0*x1
    Q = {('x0', 'x0'): 1, ('x1', 'x1'): -2, ('x0', 'x1'): 3}
    
    # Create a Binary Quadratic Model
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
    
    # Use the simulated annealing sampler (doesn't require actual quantum hardware)
    sampler = SimulatedAnnealingSampler()
    
    # Sample from the BQM
    sampleset = sampler.sample(bqm, num_reads=100)
    
    print(f"Best solution: {sampleset.first.sample}")
    print(f"Best energy: {sampleset.first.energy}")
    print(f"All samples:")
    for sample, energy, num_occurrences in sampleset.data(['sample', 'energy', 'num_occurrences']):
        print(f"  {sample} -> Energy: {energy}, Occurrences: {num_occurrences}")
    print()


def example_2_max_cut():
    """
    Example 2: Maximum Cut Problem
    This demonstrates solving a classic graph problem using quantum annealing.
    """
    print("=== Example 2: Maximum Cut Problem ===")
    
    # Create a simple graph
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)])
    
    # Convert the Max-Cut problem to a QUBO
    # For Max-Cut, we want to maximize the number of edges between different partitions
    Q = {}
    for edge in G.edges():
        u, v = edge
        Q[(u, u)] = Q.get((u, u), 0) + 1
        Q[(v, v)] = Q.get((v, v), 0) + 1
        Q[(u, v)] = Q.get((u, v), 0) - 2
    
    # Create BQM and solve
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=100)
    
    best_solution = sampleset.first.sample
    print(f"Graph edges: {list(G.edges())}")
    print(f"Best partition: {best_solution}")
    
    # Calculate the cut size
    cut_size = 0
    for edge in G.edges():
        u, v = edge
        if best_solution[u] != best_solution[v]:
            cut_size += 1
    
    print(f"Cut size: {cut_size}")
    print()


def example_3_constraint_satisfaction():
    """
    Example 3: Constraint Satisfaction Problem
    This example shows manual constraint satisfaction without dwavebinarycsp.
    """
    print("=== Example 3: Constraint Satisfaction Problem ===")
    
    if not CSP_AVAILABLE:
        print("dwavebinarycsp not available, using manual constraint implementation")
        
        # Manual implementation of AND constraint: a AND b = c
        # We want to minimize violations of the constraint a*b = c
        # Penalty for violation: |a*b - c|
        
        # Variables: a, b, c (binary)
        bqm = dimod.BinaryQuadraticModel('BINARY')
        
        # Add variables
        bqm.add_variable('a')
        bqm.add_variable('b') 
        bqm.add_variable('c')
        
        # Constraint: a*b = c
        # This can be written as: minimize (a*b - c)^2
        # Expanding: a*b*a*b - 2*a*b*c + c*c
        # Since a^2 = a and b^2 = b for binary variables:
        # = a*b - 2*a*b*c + c
        # = a*b + c - 2*a*b*c
        
        penalty = 10  # Penalty weight for constraint violations
        
        # Add terms for the constraint
        bqm.add_interaction('a', 'b', penalty)  # a*b term
        bqm.add_variable('c', penalty)  # c term
        
        # Add three-way interaction manually by adding it to pairs
        # For -2*a*b*c, we need to be creative since BQM only supports quadratic
        # We can approximate by heavily penalizing invalid states
        
        # Alternative: enumerate all possible states and set penalties
        # Valid states for a AND b = c: (0,0,0), (0,1,0), (1,0,0), (1,1,1)
        # Invalid states: (0,0,1), (0,1,1), (1,0,1), (1,1,0)
        
        # Add penalties for invalid combinations
        # If a=0, b=0, then c should be 0 (no additional penalty needed for valid case)
        # If a=0, b=0, c=1: penalize c
        # This is complex to encode directly in QUBO, so let's use a simpler approach
        
        # Simple encoding: minimize |a*b - c| by adding penalty terms
        bqm.add_interaction('a', 'b', 1)   # Encourage a*b
        bqm.add_variable('c', -1)          # Discourage c when not needed
        bqm.add_interaction('a', 'c', -1)  # Connect a and c
        bqm.add_interaction('b', 'c', -1)  # Connect b and c
        
        sampler = SimulatedAnnealingSampler()
        sampleset = sampler.sample(bqm, num_reads=100)
        
        print("Constraint: a AND b = c")
        print("Solutions found:")
        for sample, energy, num_occurrences in sampleset.data(['sample', 'energy', 'num_occurrences']):
            a, b, c = sample['a'], sample['b'], sample['c']
            valid = (a * b == c)
            print(f"  a={a}, b={b}, c={c} -> Valid: {valid}, Energy: {energy}, Count: {num_occurrences}")
        print()
        
    else:
        # Original CSP implementation
        csp = dwavebinarycsp.ConstraintSatisfactionProblem(dwavebinarycsp.BINARY)
        
        variables = ['a', 'b', 'c']
        for var in variables:
            csp.add_variable(var)
        
        def and_constraint(a, b, c):
            return a * b == c
        
        csp.add_constraint(and_constraint, ['a', 'b', 'c'])
        bqm = dwavebinarycsp.stitch(csp)
        
        sampler = SimulatedAnnealingSampler()
        sampleset = sampler.sample(bqm, num_reads=100)
        
        print("Constraint: a AND b = c")
        print("Valid solutions:")
        valid_solutions = csp.check(sampleset)
        for sample, is_valid in valid_solutions.items():
            if is_valid:
                print(f"  a={sample['a']}, b={sample['b']}, c={sample['c']}")
        print()


def example_4_ising_model():
    """
    Example 4: Ising Model
    This example demonstrates working with the Ising model formulation.
    """
    print("=== Example 4: Ising Model ===")
    
    # Define an Ising model
    # H = h1*s1 + h2*s2 + J12*s1*s2
    h = {0: -1, 1: -1}  # Linear biases
    J = {(0, 1): -1}    # Quadratic biases
    
    # Create BQM from Ising model
    bqm = dimod.BinaryQuadraticModel.from_ising(h, J)
    
    # Sample using simulated annealing
    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=100)
    
    print(f"Ising model - Linear biases: {h}")
    print(f"Ising model - Quadratic biases: {J}")
    print(f"Best solution: {sampleset.first.sample}")
    print(f"Best energy: {sampleset.first.energy}")
    print()


def check_dwave_hardware():
    """
    Check if D-Wave hardware is available (requires API token)
    This function will show how to connect to actual D-Wave hardware when available.
    """
    print("=== D-Wave Hardware Check ===")
    try:
        # This would require a D-Wave API token
        # sampler = DWaveSampler()
        # print(f"Connected to D-Wave system: {sampler.solver.name}")
        # print(f"Available qubits: {len(sampler.nodelist)}")
        print("Note: D-Wave hardware access requires an API token.")
        print("For hardware access, visit: https://cloud.dwavesys.com/")
        print("Set your token with: dwave config create")
    except Exception as e:
        print(f"D-Wave hardware not available: {e}")
    print()


if __name__ == "__main__":
    print("D-Wave Ocean SDK Basic Examples")
    print("=" * 50)
    
    # Run all examples
    example_1_basic_qubo()
    example_2_max_cut()
    example_3_constraint_satisfaction()
    example_4_ising_model()
    check_dwave_hardware()
    
    print("All examples completed!")