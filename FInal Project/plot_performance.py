from ast import Import
import matplotlib.pyplot as plt
import time
import random
from KenKenSolver import KenKenSolver, GeneticKenKenSolver 


# Function to generate random cages
def generate_random_cages(grid_size):
    cages = []
    operations = ['+', '-', '*', '/']
    visited = set()

    for _ in range(grid_size):  # Generate a number of cages equal to grid size
        cage_cells = []
        while len(cage_cells) < 2:  # Minimum of 2 cells per cage
            row, col = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
            if (row, col) not in visited:
                cage_cells.append((row, col))
                visited.add((row, col))

        target = random.randint(1, grid_size * 2)  # Example target generation
        operation = random.choice(operations)
        cages.append({'cells': cage_cells, 'target': target, 'operation': operation})

    return cages

# Plotting function
def plot_performance():
    sizes = [3, 4, 5]  # Grid sizes to compare
    backtracking_times = []
    genetic_times = []

    for size in sizes:
        cages = generate_random_cages(size)

        # Measure Backtracking performance
        backtracking_solver = KenKenSolver(size, cages)
        start_time = time.time()
        backtracking_solver.solve()
        backtracking_times.append(time.time() - start_time)

        # Measure Genetic Algorithm performance
        genetic_solver = GeneticKenKenSolver(size, cages)
        start_time = time.time()
        genetic_solver.solve()
        genetic_times.append(time.time() - start_time)

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, backtracking_times, marker='o', label='Backtracking')
    plt.plot(sizes, genetic_times, marker='o', label='Genetic Algorithm')
    plt.title("Performance Comparison of KenKen Solvers")
    plt.xlabel("Grid Size")
    plt.ylabel("Time (seconds)")
    plt.legend()
    plt.grid(True)
    plt.show()

# Call the plotting function
if __name__ == "__main__":
    plot_performance()
