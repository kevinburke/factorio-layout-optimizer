import argparse

from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from factorio import blocks, connections, grid_size

def optimize_factory_layout(max_time, blocks, connections, grid_size):
    model = cp_model.CpModel()

    # Create a list of block names for indexing
    block_names = list(blocks.keys())

    # Variables for block positions
    positions = {}
    for i, name in enumerate(block_names):
        width, height = blocks[name]
        positions[name] = (model.NewIntVar(0, grid_size[0] - width, f'x_{name}'),
                           model.NewIntVar(0, grid_size[1] - height, f'y_{name}'))

    # Ensure blocks don't overlap
    for i, name1 in enumerate(block_names):
        for j, name2 in enumerate(block_names[i+1:], i+1):
            width1, height1 = blocks[name1]
            width2, height2 = blocks[name2]

            # Block i is to the left of block j
            left = model.NewBoolVar(f'left_{name1}_{name2}')
            model.Add(positions[name1][0] + width1 <= positions[name2][0]).OnlyEnforceIf(left)

            # Block i is to the right of block j
            right = model.NewBoolVar(f'right_{name1}_{name2}')
            model.Add(positions[name2][0] + width2 <= positions[name1][0]).OnlyEnforceIf(right)

            # Block i is above block j
            above = model.NewBoolVar(f'above_{name1}_{name2}')
            model.Add(positions[name1][1] + height1 <= positions[name2][1]).OnlyEnforceIf(above)

            # Block i is below block j
            below = model.NewBoolVar(f'below_{name1}_{name2}')
            model.Add(positions[name2][1] + height2 <= positions[name1][1]).OnlyEnforceIf(below)

            # At least one of these must be true to avoid overlap
            model.AddBoolOr([left, right, above, below])

    # Calculate distances for connections
    total_distance = model.NewIntVar(0, grid_size[0] * grid_size[1] * len(connections), 'total_distance')
    distances = []
    for name1, name2 in connections:
        dx = model.NewIntVar(0, grid_size[0], f'dx_{name1}_{name2}')
        dy = model.NewIntVar(0, grid_size[1], f'dy_{name1}_{name2}')

        width1, height1 = blocks[name1]
        width2, height2 = blocks[name2]

        # X-distance
        model.AddAbsEquality(dx, (positions[name1][0] + width1 // 2) - (positions[name2][0] + width2 // 2))

        # Y-distance
        model.AddAbsEquality(dy, (positions[name1][1] + height1 // 2) - (positions[name2][1] + height2 // 2))

        distances.append(dx + dy)  # Manhattan distance

    model.Add(total_distance == sum(distances))

    # Objective: Minimize total connection distance
    model.Minimize(total_distance)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    status = solver.Solve(model)

    print(f"Solver status: {solver.StatusName(status)}")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Total distance: {solver.Value(total_distance)}")
        return {name: (solver.Value(pos[0]), solver.Value(pos[1])) for name, pos in positions.items()}
    else:
        return None

def visualize_layout(blocks, connections, optimal_positions, grid_size):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.invert_yaxis()

    # Draw blocks
    for name, (width, height) in blocks.items():
        x, y = optimal_positions[name]
        rect = patches.Rectangle((x, y), width, height, fill=False, edgecolor='blue')
        ax.add_patch(rect)
        ax.text(x + width/2, y + height/2, name, ha='center', va='center', wrap=True)

    # Draw directed connections
    for name1, name2 in connections:
        x1, y1 = optimal_positions[name1]
        x2, y2 = optimal_positions[name2]
        w1, h1 = blocks[name1]
        w2, h2 = blocks[name2]

        # Calculate the center points of the blocks
        start_x, start_y = x1 + w1/2, y1 + h1/2
        end_x, end_y = x2 + w2/2, y2 + h2/2

        # Draw an arrow from the center of name1 to the center of name2
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    )

    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Optimize Factorio factory layout")
    parser.add_argument("--fast", action="store_true", help="Use fast mode (15 seconds solver time)")
    args = parser.parse_args()

    # Set the solver time based on the --fast flag
    max_time = 15.0 if args.fast else 120.0

    # Example usage with named blocks
    optimal_positions = optimize_factory_layout(max_time, blocks, connections, grid_size)
    if optimal_positions:
        for name, (x, y) in optimal_positions.items():
            print(f"{name}: position ({x}, {y})")
    else:
        print("No solution found")

    if optimal_positions:
        visualize_layout(blocks, connections, optimal_positions, grid_size)

if __name__ == "__main__":
    main()
