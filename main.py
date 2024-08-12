from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from factorio import blocks, connections, grid_size

def optimize_factory_layout(blocks, connections, grid_size):
    model = cp_model.CpModel()

    # Variables for block positions
    positions = {}
    for i, (name, width, height) in enumerate(blocks):
        positions[i] = (model.NewIntVar(0, grid_size[0] - width, f'x_{i}'),
                        model.NewIntVar(0, grid_size[1] - height, f'y_{i}'))

    # Ensure blocks don't overlap
    for i in range(len(blocks)):
        for j in range(i + 1, len(blocks)):
            # Block i is to the left of block j
            left = model.NewBoolVar(f'left_{i}_{j}')
            model.Add(positions[i][0] + blocks[i][1] <= positions[j][0]).OnlyEnforceIf(left)

            # Block i is to the right of block j
            right = model.NewBoolVar(f'right_{i}_{j}')
            model.Add(positions[j][0] + blocks[j][1] <= positions[i][0]).OnlyEnforceIf(right)

            # Block i is above block j
            above = model.NewBoolVar(f'above_{i}_{j}')
            model.Add(positions[i][1] + blocks[i][2] <= positions[j][1]).OnlyEnforceIf(above)

            # Block i is below block j
            below = model.NewBoolVar(f'below_{i}_{j}')
            model.Add(positions[j][1] + blocks[j][2] <= positions[i][1]).OnlyEnforceIf(below)

            # At least one of these must be true to avoid overlap
            model.AddBoolOr([left, right, above, below])

    # Calculate distances for connections
    total_distance = model.NewIntVar(0, grid_size[0] * grid_size[1] * len(connections), 'total_distance')
    distances = []
    for i, j in connections:
        dx = model.NewIntVar(0, grid_size[0], f'dx_{i}_{j}')
        dy = model.NewIntVar(0, grid_size[1], f'dy_{i}_{j}')

        # X-distance
        model.AddAbsEquality(dx, (positions[i][0] + blocks[i][1] // 2) - (positions[j][0] + blocks[j][1] // 2))

        # Y-distance
        model.AddAbsEquality(dy, (positions[i][1] + blocks[i][2] // 2) - (positions[j][1] + blocks[j][2] // 2))

        distances.append(dx + dy)  # Manhattan distance

    model.Add(total_distance == sum(distances))

    # Objective: Minimize total connection distance
    model.Minimize(total_distance)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0  # Limit solve time to 60 seconds
    status = solver.Solve(model)

    print(f"Solver status: {solver.StatusName(status)}")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Total distance: {solver.Value(total_distance)}")
        return {i: (solver.Value(pos[0]), solver.Value(pos[1])) for i, pos in positions.items()}
    else:
        return None

def visualize_layout(blocks, connections, optimal_positions, grid_size):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.invert_yaxis()

    for i, (name, width, height) in enumerate(blocks):
        x, y = optimal_positions[i]
        rect = patches.Rectangle((x, y), width, height, fill=False, edgecolor='blue')
        ax.add_patch(rect)
        ax.text(x + width/2, y + height/2, name, ha='center', va='center', wrap=True)

    for i, j in connections:
        x1, y1 = optimal_positions[i]
        x2, y2 = optimal_positions[j]
        w1, h1 = blocks[i][1], blocks[i][2]
        w2, h2 = blocks[j][1], blocks[j][2]
        ax.plot([x1 + w1/2, x2 + w2/2], [y1 + h1/2, y2 + h2/2], 'r-')

    plt.tight_layout()
    plt.show()

# Example usage with named blocks

optimal_positions = optimize_factory_layout(blocks, connections, grid_size)
if optimal_positions:
    for i, (x, y) in optimal_positions.items():
        print(f"{blocks[i][0]}: position ({x}, {y})")
else:
    print("No solution found")

if optimal_positions:
    visualize_layout(blocks, connections, optimal_positions, grid_size)
