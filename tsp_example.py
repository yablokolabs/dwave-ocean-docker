#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) using D-Wave Ocean SDK
This example demonstrates solving TSP using quantum annealing.
"""

import dimod
import numpy as np
from dwave.samplers import SimulatedAnnealingSampler
try:
    import itertools
except ImportError:
    print("Warning: itertools not available, brute force verification disabled")
    itertools = None


def create_tsp_bqm(distances, penalty=None):
    """
    Create a Binary Quadratic Model for the Traveling Salesman Problem.
    
    Args:
        distances: 2D array where distances[i][j] is the distance from city i to city j
        penalty: Penalty weight for constraint violations
    
    Returns:
        BQM representing the TSP problem
    """
    n_cities = len(distances)
    
    if penalty is None:
        penalty = max(map(max, distances)) * n_cities
    
    # Create binary variables x[i][j] where x[i][j] = 1 if city i is visited at time j
    bqm = dimod.BinaryQuadraticModel('BINARY')
    
    # Add variables
    for i in range(n_cities):
        for j in range(n_cities):
            bqm.add_variable(f'x_{i}_{j}')
    
    # Objective: minimize total distance
    for i in range(n_cities):
        for j in range(n_cities):
            for k in range(n_cities):
                if i != k:
                    # If city i is at position j and city k is at position j+1
                    next_pos = (j + 1) % n_cities
                    bqm.add_interaction(f'x_{i}_{j}', f'x_{k}_{next_pos}', distances[i][k])
    
    # Constraint 1: Each city must be visited exactly once
    # Sum over j: x[i][j] = 1 for each i
    # Penalty method: (sum - 1)^2 = sum^2 - 2*sum + 1
    for i in range(n_cities):
        # Add quadratic terms: penalty * sum^2
        for j1 in range(n_cities):
            bqm.add_variable(f'x_{i}_{j1}', penalty)  # Linear term
            for j2 in range(j1 + 1, n_cities):
                bqm.add_interaction(f'x_{i}_{j1}', f'x_{i}_{j2}', 2 * penalty)  # Quadratic term
        
        # Subtract 2*penalty*sum (linear terms)
        for j in range(n_cities):
            bqm.add_variable(f'x_{i}_{j}', -2 * penalty)
        
        # Add constant penalty (this gets absorbed into the offset)
        bqm.offset += penalty
    
    # Constraint 2: Each time slot must have exactly one city
    # Sum over i: x[i][j] = 1 for each j
    for j in range(n_cities):
        # Add quadratic terms: penalty * sum^2
        for i1 in range(n_cities):
            bqm.add_variable(f'x_{i1}_{j}', penalty)  # Linear term
            for i2 in range(i1 + 1, n_cities):
                bqm.add_interaction(f'x_{i1}_{j}', f'x_{i2}_{j}', 2 * penalty)  # Quadratic term
        
        # Subtract 2*penalty*sum (linear terms)
        for i in range(n_cities):
            bqm.add_variable(f'x_{i}_{j}', -2 * penalty)
        
        # Add constant penalty
        bqm.offset += penalty
    
    return bqm


def decode_solution(sample, n_cities):
    """
    Decode the binary solution back to a tour.
    
    Args:
        sample: Binary solution from the sampler
        n_cities: Number of cities
    
    Returns:
        List representing the tour order
    """
    tour = [None] * n_cities
    
    for i in range(n_cities):
        for j in range(n_cities):
            if sample.get(f'x_{i}_{j}', 0) == 1:
                tour[j] = i
    
    return [city for city in tour if city is not None]


def calculate_tour_distance(tour, distances):
    """Calculate the total distance of a tour."""
    total_distance = 0
    n_cities = len(tour)
    
    for i in range(n_cities):
        current_city = tour[i]
        next_city = tour[(i + 1) % n_cities]
        total_distance += distances[current_city][next_city]
    
    return total_distance


def solve_tsp_example():
    """
    Solve a small TSP instance as an example.
    """
    print("=== Traveling Salesman Problem Example ===")
    
    # Define a small 4-city problem
    # Cities: A(0), B(1), C(2), D(3)
    distances = [
        [0, 2, 9, 10],   # From A
        [1, 0, 6, 4],    # From B  
        [15, 7, 0, 8],   # From C
        [6, 3, 12, 0]    # From D
    ]
    
    print("Distance matrix:")
    print("   A  B  C  D")
    for i, row in enumerate(distances):
        print(f"{chr(65+i)}: {row}")
    print()
    
    # Create BQM for TSP
    bqm = create_tsp_bqm(distances)
    print(f"BQM created with {len(bqm.variables)} variables")
    
    # Solve using simulated annealing
    sampler = SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=1000)
    
    # Process results
    n_cities = len(distances)
    best_tours = []
    
    for sample, energy in sampleset.data(['sample', 'energy']):
        tour = decode_solution(sample, n_cities)
        
        # Check if we have a valid tour
        if len(tour) == n_cities and len(set(tour)) == n_cities:
            distance = calculate_tour_distance(tour, distances)
            best_tours.append((tour, distance, energy))
    
    if best_tours:
        # Sort by distance
        best_tours.sort(key=lambda x: x[1])
        
        print("Best valid tours found:")
        for i, (tour, distance, energy) in enumerate(best_tours[:5]):
            tour_cities = [chr(65 + city) for city in tour]
            print(f"  {i+1}. Tour: {' -> '.join(tour_cities)} -> {tour_cities[0]}")
            print(f"     Distance: {distance}, Energy: {energy}")
        
        # Calculate optimal solution by brute force for comparison
        if itertools:
            print("\nBrute force verification (for small instances):")
            all_tours = list(itertools.permutations(range(n_cities)))
            optimal_distance = float('inf')
            optimal_tour = None
            
            for tour in all_tours:
                distance = calculate_tour_distance(tour, distances)
                if distance < optimal_distance:
                    optimal_distance = distance
                    optimal_tour = tour
            
            optimal_cities = [chr(65 + city) for city in optimal_tour]
            print(f"Optimal tour: {' -> '.join(optimal_cities)} -> {optimal_cities[0]}")
            print(f"Optimal distance: {optimal_distance}")
            
            if best_tours[0][1] == optimal_distance:
                print("✓ Quantum annealing found the optimal solution!")
            else:
                print(f"✗ Quantum annealing solution differs by {best_tours[0][1] - optimal_distance}")
        else:
            print("\nBrute force verification not available (itertools missing)")
    else:
        print("No valid tours found. Try adjusting the penalty parameter or increasing num_reads.")


if __name__ == "__main__":
    solve_tsp_example()