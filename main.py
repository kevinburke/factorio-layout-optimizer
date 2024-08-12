from ortools.sat.python import cp_model

def optimize_factory_layout(blocks, grid_size):
    model = cp_model.CpModel()

    # Variables for block positions
    positions = {}
    for i, (width, height) in enumerate(blocks):
        positions[i] = (model.NewIntVar(0, grid_size[0] - width, f'x_{i}'),
                        model.NewIntVar(0, grid_size[1] - height, f'y_{i}'))

    # Ensure blocks don't overlap
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            # We need at least one of these conditions to be true to avoid overlap
            x_no_overlap = model.NewBoolVar(f'x_no_overlap_{i}_{j}')
            y_no_overlap = model.NewBoolVar(f'y_no_overlap_{i}_{j}')

            model.Add(positions[i][0] + blocks[i][0] <= positions[j][0]).OnlyEnforceIf(x_no_overlap)
            model.Add(positions[j][0] + blocks[j][0] <= positions[i][0]).OnlyEnforceIf(x_no_overlap.Not())

            model.Add(positions[i][1] + blocks[i][1] <= positions[j][1]).OnlyEnforceIf(y_no_overlap)
            model.Add(positions[j][1] + blocks[j][1] <= positions[i][1]).OnlyEnforceIf(y_no_overlap.Not())

            model.AddBoolOr([x_no_overlap, y_no_overlap])

    # Objective: Spread out blocks (minimize maximum coordinate)
    max_x = model.NewIntVar(0, grid_size[0], 'max_x')
    max_y = model.NewIntVar(0, grid_size[1], 'max_y')
    for i in range(len(blocks)):
        model.Add(max_x >= positions[i][0] + blocks[i][0])
        model.Add(max_y >= positions[i][1] + blocks[i][1])
    model.Minimize(max_x + max_y)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    print(f"Solver status: {solver.StatusName(status)}")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Objective value: {solver.ObjectiveValue()}")
        return {i: (solver.Value(pos[0]), solver.Value(pos[1])) for i, pos in positions.items()}
    else:
        return None

# Example usage
blocks = [
    (5, 3),  # (width, height)
    (4, 2),
    (3, 3)
]
grid_size = (15, 15)

optimal_positions = optimize_factory_layout(blocks, grid_size)
if optimal_positions:
    for i, (x, y) in optimal_positions.items():
        print(f"Block {i}: position ({x}, {y})")
else:
    print("No solution found")

# Visualization (optional, requires matplotlib)
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_layout(blocks, optimal_positions, grid_size):
    fig, ax = plt.subplots()
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.invert_yaxis()

    for i, (x, y) in optimal_positions.items():
        width, height = blocks[i]
        rect = patches.Rectangle((x, y), width, height, fill=False)
        ax.add_patch(rect)
        ax.text(x + width/2, y + height/2, f'Block {i}', ha='center', va='center')

    plt.show()

if optimal_positions:
    visualize_layout(blocks, optimal_positions, grid_size)
