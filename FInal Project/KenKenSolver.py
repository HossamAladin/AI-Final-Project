import random
from tkinter import *
from tkinter import messagebox
import time

class KenKenSolver:
    def __init__(self, n, cages):
        self.n = n
        self.board = [[0] * n for _ in range(n)]
        self.cages = cages

    def is_valid(self, row, col, num):
        # Check row
        if num in self.board[row]:
            return False
        # Check column
        if num in [self.board[r][col] for r in range(self.n)]:
            return False

        # Check cage constraints based on the current board state
        for cage in self.cages:
            if (row, col) in cage['cells']:
                values = [self.board[r][c] for r, c in cage['cells'] if self.board[r][c] != 0]
                values.append(num)
                if not self.check_cage(cage['target'], cage['operation'], values):
                    return False
        return True

    def check_cage(self, target, operation, values):
        # Handle cage constraints based on the operation
        if operation == '+':
            return sum(values) <= target
        elif operation == '-':
            # For subtraction, there must be exactly two values
            if len(values) == 2:
                return abs(values[0] - values[1]) == target
            return True
        elif operation == '*':
            product = 1
            for v in values:
                product *= v
            return product <= target
        elif operation == '/':
            # For division, there must be exactly two values
            if len(values) == 2:
                return (values[0] / values[1] == target or values[1] / values[0] == target)
            return True
        elif operation == '=':
            return len(values) == 1 and values[0] == target
        return False

    def find_empty(self):
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] == 0:
                    return r, c
        return None

    def solve(self):
        empty = self.find_empty()
        if not empty:
            return True  # Solved

        row, col = empty
        for num in range(1, self.n + 1):
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self.solve():
                    return True
                self.board[row][col] = 0  # Backtrack

        return False


class GeneticKenKenSolver:
    def __init__(self, n, cages, population_size=100, generations=500, mutation_rate=0.2):
        self.n = n
        self.cages = cages
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.board = None

    def generate_individual(self):
        individual = []
        for _ in range(self.n):
            row = list(range(1, self.n + 1))
            random.shuffle(row)
            individual.append(row)
        return individual

    def fitness(self, individual):
        score = 0
        for i in range(self.n):
            score += len(set(individual[i]))
            score += len(set([row[i] for row in individual]))

        for cage in self.cages:
            values = [individual[r][c] for r, c in cage['cells']]
            if self.check_cage(cage['target'], cage['operation'], values):
                score += len(values)

        return score

    def check_cage(self, target, operation, values):
        if operation == '+':
            return sum(values) == target
        elif operation == '-':
            return len(values) == 2 and abs(values[0] - values[1]) == target
        elif operation == '*':
            product = 1
            for v in values:
                product *= v
            return product == target
        elif operation == '/':
            return len(values) == 2 and (values[0] / values[1] == target or values[1] / values[0] == target)
        elif operation == '=':
            return len(values) == 1 and values[0] == target
        return False

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, self.n - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            row = random.randint(0, self.n - 1)
            col1, col2 = random.sample(range(self.n), 2)
            individual[row][col1], individual[row][col2] = individual[row][col2], individual[row][col1]

    def solve(self):
        population = [self.generate_individual() for _ in range(self.population_size)]

        for generation in range(self.generations):
            population = sorted(population, key=self.fitness, reverse=True)

            if self.fitness(population[0]) == self.n * self.n * 2:
                self.board = population[0]
                return True

            next_generation = population[:10]

            for _ in range(self.population_size - 10):
                parent1, parent2 = random.choices(population[:50], k=2)
                child = self.crossover(parent1, parent2)
                self.mutate(child)
                next_generation.append(child)

            population = next_generation

        return False


class KenKenSolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KenKen Solver")

        self.grid_size_var = IntVar(value=4)  # Default grid size
        self.algorithm_var = StringVar(value="Backtracking")
        self.cells = []  # Initialize cells here
        self.create_widgets()

        # Add a trace to update the grid when grid size changes
        self.grid_size_var.trace('w', self.update_grid)

    def create_widgets(self):
        Label(self.root, text="Select Algorithm:", font=("Arial", 14)).pack(pady=10)
        OptionMenu(self.root, self.algorithm_var, "Backtracking", "Genetic Algorithm").pack(pady=5)

        Label(self.root, text="Select Grid Size:", font=("Arial", 14)).pack(pady=10)
        OptionMenu(self.root, self.grid_size_var, 3, 4, 5).pack(pady=5)

        Label(self.root, text="KenKen Grid", font=("Arial", 16)).pack(pady=10)
        self.grid_frame = Frame(self.root)
        self.grid_frame.pack()

        self.update_grid()  # Initialize grid

        Button(self.root, text="Start Solving", command=self.start_solving).pack(pady=5)

    def update_grid(self, *args):
        # Clear previous cells if they exist
        for row in self.cells:
            for cell in row:
                cell.destroy()

        self.cells.clear()  # Clear the stored cell references
        selected_size = self.grid_size_var.get()  # Get current grid size from variable

        # Create new random cages for the selected grid size
        self.random_cages = self.generate_random_cages(selected_size)

        # Display cages in terminal
        print("Generated Cages:")
        for cage in self.random_cages:
            print(f"Target: {cage['target']}, Operation: {cage['operation']}, Cells: {cage['cells']}")

        # Create new grid based on selected size
        for r in range(selected_size):
            row_cells = []
            for c in range(selected_size):
                e = Entry(self.grid_frame, width=5, font=("Arial", 14), justify="center")
                e.grid(row=r, column=c, padx=5, pady=5)
                row_cells.append(e)
            self.cells.append(row_cells)

    def generate_random_cages(self, grid_size):
        cages = []
        operations = ['+', '-', '*', '/']
        visited = set()

        for _ in range(grid_size):  # Generate a number of cages equal to grid size
            # Start with a random number of cells for the cage (minimum 2 cells)
            num_cells = random.randint(2, grid_size)

            # Select random cells for the cage
            cage_cells = []
            while len(cage_cells) < num_cells:
                r, c = random.randint(0, grid_size-1), random.randint(0, grid_size-1)
                if (r, c) not in visited:
                    visited.add((r, c))
                    cage_cells.append((r, c))

            # Randomly select an operation for the cage
            operation = random.choice(operations)

            # Generate a valid target based on the operation and the selected cells
            if operation == '+':
                target = random.randint(num_cells, num_cells * 9)  # For addition, the target is a sum of the values in the cells
            elif operation == '-':
                target = random.randint(1, 9)  # For subtraction, target is a small number (usually the difference between two values)
            elif operation == '*':
                target = random.randint(1, num_cells * 9)  # For multiplication, target is a product of the values in the cells
            elif operation == '/':
                target = random.randint(1, 9)  # For division, target is a quotient between two numbers

            # Add the generated cage to the list
            cages.append({
                "cells": cage_cells,
                "operation": operation,
                "target": target
            })

        return cages

    def start_solving(self):
        grid_size = self.grid_size_var.get()
        selected_algorithm = self.algorithm_var.get()

        if selected_algorithm == "Backtracking":
            solver = KenKenSolver(grid_size, self.random_cages)
            if solver.solve():
                self.display_solution(solver.board)
            else:
                messagebox.showerror("Error", "No solution found.")
        else:
            solver = GeneticKenKenSolver(grid_size, self.random_cages)
            if solver.solve():
                self.display_solution(solver.board)
            else:
                messagebox.showerror("Error", "No solution found.")

    def display_solution(self, solution):
        for r in range(self.grid_size_var.get()):
            for c in range(self.grid_size_var.get()):
                self.cells[r][c].delete(0, END)
                self.cells[r][c].insert(0, solution[r][c])


def main():
    root = Tk()
    app = KenKenSolverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
