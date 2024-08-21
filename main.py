import argparse
import math
import random

from ortools.sat.python import cp_model
from matplotlib.offsetbox import AnchoredText
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

from factorio import Block, Connection, blocks, connections, grid_size, rotatable_blocks

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        print(f"Solution {self.__solution_count}")
        for v in self.__variables:
            print(f'{v}={self.Value(v)}', end=' ')
        print("\n")

    def solution_count(self):
        return self.__solution_count

def optimize_factory_layout(blocks, connections, grid_size, rotatable_blocks, max_time, allow_rotation=True):
    model = cp_model.CpModel()

    # Variables for block positions and rotations
    # tuple of (x, y)
    positions = {}
    rotations = {}
    # tuple of (width, height)
    sizes = {}
    weights = {}
    all_vars = []
    for name, block_info in blocks.items():
        if isinstance(block_info, Block):
            width, height, weight = block_info.width, block_info.height, block_info.weight
        else:
            width, height = block_info
            weight = 1  # Default weight

        if isinstance(block_info, Block) and block_info.fixed_x is not None:
            positions[name] = (model.NewConstant(block_info.fixed_x), model.NewConstant(block_info.fixed_y))
        else:
            positions[name] = (model.NewIntVar(0, grid_size[0] - min(width, height), f'x_{name}'),
                               model.NewIntVar(0, grid_size[1] - min(width, height), f'y_{name}'))

        all_vars.extend(positions[name])
        if allow_rotation and name in rotatable_blocks:
            rotations[name] = model.NewBoolVar(f'rot_{name}')
            sizes[name] = (model.NewIntVar(min(width, height), max(width, height), f'w_{name}'),
                           model.NewIntVar(min(width, height), max(width, height), f'h_{name}'))
            model.Add(sizes[name][0] == width).OnlyEnforceIf(rotations[name].Not())
            model.Add(sizes[name][1] == height).OnlyEnforceIf(rotations[name].Not())
            model.Add(sizes[name][0] == height).OnlyEnforceIf(rotations[name])
            model.Add(sizes[name][1] == width).OnlyEnforceIf(rotations[name])
        else:
            rotations[name] = model.NewConstant(0)  # Not rotated
            sizes[name] = (model.NewConstant(width), model.NewConstant(height))
        all_vars.append(rotations[name])
        weights[name] = weight

    # Ensure blocks don't overlap
    for name1, _ in blocks.items():
        for name2, _ in blocks.items():
            if name1 < name2:
                b1_left_of_b2 = model.NewBoolVar(f'{name1}_left_of_{name2}')
                b2_left_of_b1 = model.NewBoolVar(f'{name2}_left_of_{name1}')
                b1_above_b2 = model.NewBoolVar(f'{name1}_above_{name2}')
                b2_above_b1 = model.NewBoolVar(f'{name2}_above_{name1}')

                model.Add(positions[name1][0] + sizes[name1][0] <= positions[name2][0]).OnlyEnforceIf(b1_left_of_b2)
                model.Add(positions[name2][0] + sizes[name2][0] <= positions[name1][0]).OnlyEnforceIf(b2_left_of_b1)
                model.Add(positions[name1][1] + sizes[name1][1] <= positions[name2][1]).OnlyEnforceIf(b1_above_b2)
                model.Add(positions[name2][1] + sizes[name2][1] <= positions[name1][1]).OnlyEnforceIf(b2_above_b1)

                model.AddBoolOr([b1_left_of_b2, b2_left_of_b1, b1_above_b2, b2_above_b1])

    def get_connection_point(model, name, pos, x, y, width, height):
        # Assert that all inputs are IntVars
        assert all(isinstance(var, cp_model.IntVar) for var in [x, y, width, height]), \
            "All inputs (x, y, width, height) must be IntVars"

        if pos == "LM" or pos == "ML":
            return x, model.NewIntVar(0, grid_size[1], f'{name}_{pos}_y')
        elif pos == "TR" or pos == "RT":
            x_tr = model.NewIntVar(0, grid_size[0], f'{name}_{pos}_x')
            model.Add(x_tr == x + width)
            return x_tr, y
        elif pos == "BL":
            y_bl = model.NewIntVar(0, grid_size[1], f'{name}_{pos}_y')
            model.Add(y_bl == y + height)
            return x, y_bl
        elif pos == "TL" or pos == "LT":
            return x, y
        elif pos == "BR":
            x_br = model.NewIntVar(0, grid_size[0], f'{name}_{pos}_x')
            y_br = model.NewIntVar(0, grid_size[1], f'{name}_{pos}_y')
            model.Add(x_br == x + width)
            model.Add(y_br == y + height)
            return x_br, y_br
        elif pos == "RM" or pos == "MR":
            x_rm = model.NewIntVar(0, grid_size[0], f'{name}_{pos}_x')
            model.Add(x_rm == x + width)
            return x_rm, model.NewIntVar(0, grid_size[1], f'{name}_{pos}_y')
        elif pos == "TM":
            return model.NewIntVar(0, grid_size[0], f'{name}_{pos}_x'), y
        elif pos == "BM":
            y_bm = model.NewIntVar(0, grid_size[1], f'{name}_{pos}_y')
            model.Add(y_bm == y + height)
            return model.NewIntVar(0, grid_size[0], f'{name}_{pos}_x'), y_bm
        elif pos == "MM":  # Default to center
            return model.NewIntVar(0, grid_size[0], f'{name}_{pos}_x'), model.NewIntVar(0, grid_size[1], f'{name}_{pos}_y')
        else:
            raise KeyError(f"Unknown position {pos}, double check variable entry")

    total_weighted_distance = model.NewIntVar(0, grid_size[0] * grid_size[1] * len(connections) * 100, 'total_weighted_distance')

    weighted_distances = []
    unweighted_distances = []
    connection_infos = []  # Store connection information
    debug_vars = []  # Store variables for debugging

    for conn in connections:
        if isinstance(conn, Connection):
            name1, name2, pos1, pos2, weight = conn.source, conn.target, conn.source_pos, conn.target_pos, conn.weight
        else:
            name1, name2, pos1, pos2 = conn
            weight = 1  # Default weight for tuple connections

        if name1 not in positions or name2 not in positions:
            continue
        connection_infos.append((f"{name1}-{name2}", weight))  # Store connection name and weight

        x1, y1 = positions[name1]
        x2, y2 = positions[name2]
        w1, h1 = sizes[name1]
        w2, h2 = sizes[name2]

        start_x, start_y = get_connection_point(model, name1, pos1, x1, y1, w1, h1)
        end_x, end_y = get_connection_point(model, name2, pos2, x2, y2, w2, h2)

        model.Add(start_x >= x1)
        model.Add(start_x <= x1 + w1)

        model.Add(end_x >= x2)
        model.Add(end_x <= x2 + w2)

        model.Add(start_y >= y1)
        model.Add(start_y <= y1 + h1)

        model.Add(end_y >= y2)
        model.Add(end_y <= y2 + h2)

        dx = model.NewIntVar(-grid_size[0], grid_size[0], f'dx_{name1}_{name2}')
        dy = model.NewIntVar(-grid_size[1], grid_size[1], f'dy_{name1}_{name2}')
        print(f"dx: {dx}, {end_x - start_x}")

        model.Add(dx == end_x - start_x)
        model.Add(dy == end_y - start_y)

        abs_dx = model.NewIntVar(0, grid_size[0], f'abs_dx_{name1}_{name2}')
        abs_dy = model.NewIntVar(0, grid_size[1], f'abs_dy_{name1}_{name2}')

        model.AddAbsEquality(abs_dx, dx)
        model.AddAbsEquality(abs_dy, dy)

        manhattan_distance = model.NewIntVar(0, grid_size[0] + grid_size[1], f'manhattan_dist_{name1}_{name2}')
        model.Add(manhattan_distance == abs_dx + abs_dy)

        weighted_distance = model.NewIntVar(0, (grid_size[0] + grid_size[1]) * 100, f'weighted_dist_{name1}_{name2}')
        model.AddMultiplicationEquality(weighted_distance, [manhattan_distance, weight])

        weighted_distances.append(weighted_distance)
        unweighted_distances.append(manhattan_distance)

        debug_vars.append({
            'name': f"{name1}-{name2}",
            'dx': dx,
            'dy': dy,
            'abs_dx': abs_dx,
            'abs_dy': abs_dy,
            'distance': manhattan_distance,
            'weighted_distance': weighted_distance,
            'center_x1': x1,
            'center_y1': y1,
            'center_x2': x2,
            'center_y2': y2
        })

    model.Add(total_weighted_distance == sum(weighted_distances))
    model.Minimize(total_weighted_distance)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    solver.parameters.num_search_workers = 8
    solver.parameters.log_search_progress = True
    solver.parameters.random_seed = random.randint(0, 10000)  # Add randomness

    solution_printer = VarArraySolutionPrinter(all_vars)
    status = solver.Solve(model, solution_printer)

    print(f"Solver status: {solver.StatusName(status)}")
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        total_weighted_distance_value = solver.Value(total_weighted_distance)
        total_unweighted_distance = sum(solver.Value(d) for d in unweighted_distances)
        print(f"Total weighted distance: {total_weighted_distance_value}")
        print(f"Total unweighted distance: {total_unweighted_distance}")

        print("Connection details:")
        for i, ((name, original_weight), weighted_dist, unweighted_dist) in enumerate(zip(connection_infos, weighted_distances, unweighted_distances)):
            name1, name2 = name.split('-')
            x1, y1 = solver.Value(positions[name1][0]), solver.Value(positions[name1][1])
            x2, y2 = solver.Value(positions[name2][0]), solver.Value(positions[name2][1])
            w1, h1 = solver.Value(sizes[name1][0]), solver.Value(sizes[name1][1])
            w2, h2 = solver.Value(sizes[name2][0]), solver.Value(sizes[name2][1])

            center_x1 = x1 + w1 // 2
            center_y1 = y1 + h1 // 2
            center_x2 = x2 + w2 // 2
            center_y2 = y2 + h2 // 2

            calc_dx = abs(center_x2 - center_x1)
            calc_dy = abs(center_y2 - center_y1)
            calc_distance = calc_dx + calc_dy

            unweighted_value = solver.Value(unweighted_dist)
            weighted_value = solver.Value(weighted_dist)

            print(f"  {name}:")
            print(f"    Block 1 ({name1}): position ({x1}, {y1}), size ({w1}, {h1}), center ({center_x1}, {center_y1})")
            print(f"    Block 2 ({name2}): position ({x2}, {y2}), size ({w2}, {h2}), center ({center_x2}, {center_y2})")
            print(f"    Calculated |dx|: {calc_dx}, |dy|: {calc_dy}")
            print(f"    Calculated distance: {calc_distance}")
            print(f"    Solver distance: {unweighted_value}")
            print(f"    Weight: {original_weight}")
            print(f"    Weighted distance: {weighted_value}")

            if calc_distance != unweighted_value:
                print(f"    WARNING: Calculated distance does not match solver distance!")
            if weighted_value != unweighted_value * original_weight:
                print(f"    WARNING: Weighted distance does not match unweighted distance * weight!")

        print("\nDetailed Debug Information:")
        for vars in debug_vars:
            print(f"Connection: {vars['name']}")
            print(f"  center_x1: {solver.Value(vars['center_x1'])}")
            print(f"  center_y1: {solver.Value(vars['center_y1'])}")
            print(f"  center_x2: {solver.Value(vars['center_x2'])}")
            print(f"  center_y2: {solver.Value(vars['center_y2'])}")
            print(f"  dx: {solver.Value(vars['dx'])}")
            print(f"  dy: {solver.Value(vars['dy'])}")
            print(f"  abs_dx: {solver.Value(vars['abs_dx'])}")
            print(f"  abs_dy: {solver.Value(vars['abs_dy'])}")
            print(f"  distance: {solver.Value(vars['distance'])}")
            print(f"  weighted_distance: {solver.Value(vars['weighted_distance'])}")
            print()

        return {name: (solver.Value(pos[0]), solver.Value(pos[1]), solver.BooleanValue(rotations[name]))
                for name, pos in positions.items()}, total_unweighted_distance
    else:
        print("No solution found within the time limit.")
        return None, None

def get_connection_point(x, y, width, height, position):
    if position == "LM" or position == "ML":
        return x, y + height / 2
    elif position == "TR" or position == "RT":
        return x + width, y
    elif position == "BL":
        return x, y + height
    elif position == "TL" or position == "LT":
        return x, y
    elif position == "BR" or position == "RB":
        return x + width, y + height
    elif position == "RM" or position == "MR":
        return x + width, y + height / 2
    elif position == "TM":
        return x + width / 2, y
    elif position == "BM":
        return x + width / 2, y + height
    elif position == "MM":
        return x + width / 2, y + height / 2  # Default to center
    else:
        raise KeyError(f"Unknown position {position}, double check variable entry")


def get_font_property(size):
    # Try to use Titillium Web first, then DejaVu Sans, then fall back to default sans-serif
    for font_name in ['DejaVu Sans', 'sans-serif']:
        try:
            return FontProperties(family=font_name, size=size)
        except:
            continue
    return FontProperties(family='sans-serif', size=size)

def estimate_text_height(text, font_prop, width):
    # Estimate text height based on font properties and width
    font_size = font_prop.get_size_in_points()
    char_width = font_size * 0.6  # Rough estimate of character width
    chars_per_line = max(1, int(width / char_width))
    lines = [text[i:i+chars_per_line] for i in range(0, len(text), chars_per_line)]
    return len(lines) * font_size * 1.2  # 1.2 for line spacing

def visualize_layout(blocks, connections, optimal_positions, grid_size, total_distance):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(0, grid_size[0])
    ax.set_ylim(0, grid_size[1])
    ax.invert_yaxis()

    ax.set_xticks(range(0, grid_size[0] + 1, 16))
    ax.set_yticks(range(0, grid_size[1] + 1, 16))
    ax.grid(which='both', color='lightgray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    # Draw blocks
    for name, block_info in blocks.items():
        if isinstance(block_info, Block):
            width, height = block_info.width, block_info.height
        else:
            width, height = block_info

        x, y, is_rotated = optimal_positions[name]
        if is_rotated:
            width, height = height, width
        rect = patches.Rectangle((x, y), width, height, fill=False, edgecolor='blue')
        ax.add_patch(rect)

        # Create text with auto-wrapping and size adjustment
        max_fontsize = 12
        min_fontsize = 6

        best_text = None
        best_fontsize = min_fontsize

        for fontsize in range(max_fontsize, min_fontsize-1, -1):
            font_prop = get_font_property(fontsize)
            estimated_height = estimate_text_height(name, font_prop, width * 0.9)

            if estimated_height <= height * 0.9:
                best_fontsize = fontsize
                break

        # Create the text with the best font size
        font_prop = get_font_property(best_fontsize)
        wrapped_text = wrap_text(name, width * 0.9, font_prop)
        best_text = ax.text(x + width/2, y + height/2, '\n'.join(wrapped_text),
                            ha='center', va='center', fontproperties=font_prop,
                            wrap=True)

        # Truncate text if it's still too tall
        while len(wrapped_text) > 1:
            estimated_height = estimate_text_height('\n'.join(wrapped_text), font_prop, width * 0.9)
            if estimated_height <= height * 0.9:
                break
            wrapped_text = wrapped_text[:-1]
            wrapped_text[-1] += '...'
            best_text.set_text('\n'.join(wrapped_text))

    # Draw connections
    for conn in connections:
        if isinstance(conn, Connection):
            name1, name2, pos1, pos2, weight = conn.source, conn.target, conn.source_pos, conn.target_pos, conn.weight
        else:
            name1, name2, pos1, pos2 = conn
        try:
            x1, y1, is_rotated1 = optimal_positions[name1]
            x2, y2, is_rotated2 = optimal_positions[name2]
        except KeyError:
            continue
        block_info = blocks[name1]
        if isinstance(block_info, Block):
            w1, h1 = block_info.width, block_info.height
        else:
            w1, h1 = block_info
        block_info = blocks[name2]
        if isinstance(block_info, Block):
            w2, h2 = block_info.width, block_info.height
        else:
            w2, h2 = block_info

        if is_rotated1:
            w1, h1 = h1, w1
        if is_rotated2:
            w2, h2 = h2, w2

        # Get start and end points based on specified positions
        start_x, start_y = get_connection_point(x1, y1, w1, h1, pos1)
        end_x, end_y = get_connection_point(x2, y2, w2, h2, pos2)

        # Calculate vector and shorten the end point
        dx, dy = end_x - start_x, end_y - start_y
        length = math.sqrt(dx**2 + dy**2)
        shorten_factor = 10  # Pixels to shorten by
        if length > shorten_factor:
            end_x -= (dx / length) * shorten_factor
            end_y -= (dy / length) * shorten_factor

        # Draw the arrow
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    annotation_clip=False)

    watermark_text = f"github.com/kevinburke/factorio-layout-optimizer\ndistance: {total_distance}"
    ax.text(0.99, 0.01, watermark_text,
            horizontalalignment='right',
            verticalalignment='bottom',
            transform=ax.transAxes,
            fontsize=8, alpha=0.7)

    plt.tight_layout()
    plt.show()

def wrap_text(text, max_width, font_prop):
    """Wrap text to fit within a given width."""
    words = text.split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = current_line + " " + word
        if estimate_text_height(test_line, font_prop, max_width) <= font_prop.get_size_in_points() * 1.2:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines

def main():
    parser = argparse.ArgumentParser(description="Optimize Factorio factory layout")
    parser.add_argument("--fast", action="store_true", help="Use fast mode (15 seconds solver time)")
    parser.add_argument("--time", type=int, default=240.0, help="Amount of time to run the solver for")
    args = parser.parse_args()

    # Set the solver time based on the --fast flag
    max_time = 15.0 if args.fast else args.time

    print("Attempting to solve without rotation...")
    optimal_positions, total_distance = optimize_factory_layout(blocks, connections, grid_size, rotatable_blocks, max_time, allow_rotation=False)

    if optimal_positions is None:
        print("No solution found without rotation. Attempting to solve with rotation...")
        optimal_positions, total_distance = optimize_factory_layout(blocks, connections, grid_size, rotatable_blocks, max_time // 2, allow_rotation=True)

    if optimal_positions:
        for name, (x, y, is_rotated) in optimal_positions.items():
            print(f"{name}: position ({x}, {y}), {'rotated' if is_rotated else 'not rotated'}")
        visualize_layout(blocks, connections, optimal_positions, grid_size, total_distance)
    else:
        print("No solution found in either attempt.")

if __name__ == "__main__":
    main()
