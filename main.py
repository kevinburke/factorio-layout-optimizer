import argparse
from itertools import product
import math
import random

from ortools.sat.python import cp_model
from matplotlib.offsetbox import AnchoredText
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

from factorio import Block, Connection, OneOf, blocks, connections, grid_size

rcu_constraints = []
combo_vars = []

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        # print(f"Solution {self.__solution_count}")
        # for v in self.__variables:
            # print(f'{v}={self.Value(v)}', end=' ')
        # print("\n")

    def solution_count(self):
        return self.__solution_count

def optimize_factory_layout(blocks, connections, grid_size, max_time, allow_rotation=True):
    model = cp_model.CpModel()

    # Variables for block positions and rotations
    # tuple of (x, y)
    positions = {}
    rotations = {}
    # tuple of (width, height)
    sizes = {}
    weights = {}
    all_vars = []

    x_starts = []
    x_sizes = []
    x_ends = []
    y_starts = []
    y_sizes = []
    y_ends = []
    x_intervals = []
    y_intervals = []

    i = 0
    for name, block_info in blocks.items():
        if isinstance(block_info, Block):
            width, height, weight = block_info.width, block_info.height, block_info.weight
        else:
            width, height = block_info
            weight = 1  # Default weight

        if isinstance(block_info, Block) and block_info.fixed_position():
            x1 = model.NewIntVar(block_info.fixed_x, block_info.fixed_x, f"x_start_fixed_{name}_({block_info.fixed_x})")
            y1 = model.NewIntVar(block_info.fixed_y, block_info.fixed_y, f"y_start_fixed_{name}_({block_info.fixed_y})")

            x_starts.append(x1)
            x_ends.append(model.NewConstant(block_info.fixed_x + width))
            x_size = model.NewConstant(width)
            x_sizes.append(x_size)

            y_starts.append(y1)
            y_ends.append(model.NewConstant(block_info.fixed_y + height))
            y_size = model.NewConstant(height)
            y_sizes.append(y_size)

        else:
            x1 = model.NewIntVar(0, grid_size[0] - min(width, height), f'x_start_{name}')
            model.add_hint(x1, math.ceil(grid_size[0]//2))
            if name == "Lab":
                print(x1.Proto())
            x_starts.append(x1)
            x_ends.append(model.NewIntVar(0+min(width, height), grid_size[0], f'x_end_{name}'))

            y1 = model.NewIntVar(0, grid_size[1] - min(width, height), f'y_start_{name}')
            model.add_hint(y1, math.ceil(grid_size[1]//2))
            if name == "Lab":
                print(y1.Proto())
            y_starts.append(y1)
            y_ends.append(model.NewIntVar(0+min(width, height), grid_size[1], f'y_end_{name}'))

            if allow_rotation:
                x_size = model.NewIntVarFromDomain(cp_model.Domain.FromValues([width, height]), f"x_size_{name}")
                x_sizes.append(x_size)
                y_size = model.NewIntVarFromDomain(cp_model.Domain.FromValues([width, height]), f"y_size_{name}")
                y_sizes.append(y_size)
                if name == "Lab":
                    print(x_size)
                    print(y_size)
                    print(cp_model.Domain.FromValues([width, height]))
                    print([width, height])
            else:
                x_size = model.NewConstant(width)
                x_sizes.append(x_size)
                y_size = model.NewConstant(height)
                y_sizes.append(y_size)
        positions[name] = (x1, y1)
        sizes[name] = (x_size, y_size)

        all_vars.extend(positions[name])
        xvar = model.new_interval_var(x_starts[i], x_sizes[i], x_ends[i], f"x_interval_{name}")
        yvar = model.new_interval_var(y_starts[i], y_sizes[i], y_ends[i], f"y_interval_{name}")
        x_intervals.append(xvar)
        y_intervals.append(yvar)
        i += 1

        # all_vars.append(rotations[name])
        # weights[name] = weight

    # is_used = []
    for name, block_info in blocks.items():
        if isinstance(block_info, Block):
            width, height, weight = block_info.width, block_info.height, block_info.weight
            fixed_position = block_info.fixed_position()
        else:
            fixed_position = False
            width, height = block_info
            weight = 1  # Default weight
        if allow_rotation and not fixed_position:
            no_rotation = model.new_bool_var(f"no_rotation_{name}")
            rotated = model.new_bool_var(f"rotated_{name}")
            model.add_exactly_one(no_rotation, rotated)
            rotations[name] = (no_rotation, rotated)

            model.Add(sizes[name][0] == width).OnlyEnforceIf(no_rotation).WithName(f"width of {name} should be {width} if no rotation")
            model.Add(sizes[name][1] == height).OnlyEnforceIf(no_rotation).WithName(f"height of {name} should be {height} if no rotation")
            model.Add(sizes[name][0] == height).OnlyEnforceIf(rotated).WithName(f"width of {name} should be {height} if no rotation")
            model.Add(sizes[name][1] == width).OnlyEnforceIf(rotated).WithName(f"height of {name} should be {width} if rotated")
        else:
            rotations[name] = (model.NewConstant(True), model.NewConstant(False))  # Not rotated
            # model.Add(sizes[name][0] == width)
            # model.Add(sizes[name][1] == height)


    # model.add_no_overlap_2d(x_intervals, y_intervals)

    # Ensure blocks don't overlap
    for name1, _ in blocks.items():
        for name2, _ in blocks.items():
            if name1 < name2:
                b1_left_of_b2 = model.new_bool_var(f'{name1}_left_of_{name2}')
                b2_left_of_b1 = model.new_bool_var(f'{name2}_left_of_{name1}')
                b1_above_b2 = model.new_bool_var(f'{name1}_above_{name2}')
                b2_above_b1 = model.new_bool_var(f'{name2}_above_{name1}')

                model.Add(positions[name1][0] + sizes[name1][0] <= positions[name2][0]).OnlyEnforceIf(b1_left_of_b2)
                model.Add(positions[name2][0] + sizes[name2][0] <= positions[name1][0]).OnlyEnforceIf(b2_left_of_b1)
                model.Add(positions[name1][1] + sizes[name1][1] <= positions[name2][1]).OnlyEnforceIf(b1_above_b2)
                model.Add(positions[name2][1] + sizes[name2][1] <= positions[name1][1]).OnlyEnforceIf(b2_above_b1)

                model.AddBoolOr([b1_left_of_b2, b2_left_of_b1, b1_above_b2, b2_above_b1])

    def get_connection_point(model, name, typ, pos, x, y, width, height, no_rotation, rotated):
        # Assert that all inputs are IntVars
        assert all(isinstance(var, cp_model.IntVar) for var in [x, y, width, height]), \
            "All inputs (x, y, width, height) must be IntVars"
        # return x, y

        # Helper function to create midpoint without division
        def create_midpoint(start, length, key):
            mid = model.NewIntVar(0, max(grid_size[0], grid_size[1]), f'mid_{key}_{name}_{typ}_{pos}')
            model.Add(2 * mid >= 2 * start + length - 1).WithName(f"midpoint of {name} should be > {start + length - 1}")
            model.Add(2 * mid <= 2 * start + length).WithName(f"midpoint of {name} should be <= {start + length}")
            return mid

        conns_x = []
        conns_y = []
        all_pos = []
        pos_bools = []
        if isinstance(pos, OneOf):
            all_pos = pos.conns
        else:
            all_pos = [pos]

        i = 0
        for pos in all_pos:
            i += 1
            conn_x = model.NewIntVar(0, grid_size[0], f'conn_x_{name}_{typ}_{pos}_{i}')
            conn_y = model.NewIntVar(0, grid_size[1], f'conn_y_{name}_{typ}_{pos}_{i}')
            pos_bool = model.new_bool_var(f"conn_{name}_{typ}_{pos}_inuse_{i}")
            pos_bools.append(pos_bool)
            conns_x.append(conn_x)
            conns_y.append(conn_y)
            for conn in connections:
                source_block = None
                try:
                    if isinstance(conn, Connection):
                        if conn.target == name:
                            source_block = blocks[conn.source]
                    else:
                        if conn[1] == name:
                            source_block = blocks[conn[0]]
                except KeyError:
                    continue

                if isinstance(source_block, Block) and source_block.fixed_position():
                    model.add_hint(conn_x, source_block.fixed_x)
                    model.add_hint(conn_y, source_block.fixed_y)
                    break

            mid_x = create_midpoint(x, width, 'x')
            mid_y = create_midpoint(y, height, 'y')
            if pos == "MM":
                model.Add(conn_x == mid_x).OnlyEnforceIf(pos_bool)
                model.Add(conn_y == mid_y).OnlyEnforceIf(pos_bool)
                continue
            else:
                # Define connection points for non-rotated and rotated states
                # Rotated is 90 degrees clockwise (top moves to the right.)
                positions = {
                    "TL": [(x, y), (x + width, y)],
                    "TM": [(mid_x, y), (x + width, mid_y)],
                    "TR": [(x + width, y), (x + width, y + height)],

                    "ML": [(x, mid_y), (mid_x, y)],
                    "LM": [(x, mid_y), (mid_x, y)],

                    "MR": [(x + width, mid_y), (mid_x, y + height)],
                    "RM": [(x + width, mid_y), (mid_x, y + height)],

                    "BL": [(x, y + height), (x, y)],
                    "BM": [(mid_x, y + height), (x, mid_y)],
                    "BR": [(x + width, y + height), (x, y + height)]
                }
                if pos in positions:
                    px_non_rotated, py_non_rotated = positions[pos][0]
                    px_rotated, py_rotated = positions[pos][1]
                    # if name1 == "Plastic" and name2 == "Red Circuit - RCU":
                        # print("appending constraints")
                        # rcu_constraints.append(conn_x)
                        # rcu_constraints.append(conn_y)
                        # rcu_constraints.append(x)
                        # rcu_constraints.append(mid_y)
                        # rcu_constraints.append(mid_x)
                        # rcu_constraints.append(y)
                        # rcu_constraints.append(px_non_rotated)
                        # rcu_constraints.append(py_non_rotated)
                        # rcu_constraints.append(px_rotated)
                        # rcu_constraints.append(py_rotated)
                        # rcu_constraints.append(pos_bool)
                        # rcu_constraints.append(no_rotation)
                        # rcu_constraints.append(rotated)

                    model.Add(conn_x == px_non_rotated).OnlyEnforceIf(no_rotation, pos_bool)
                    model.Add(conn_y == py_non_rotated).OnlyEnforceIf(no_rotation, pos_bool)
                    model.Add(conn_x == px_rotated).OnlyEnforceIf(rotated, pos_bool)
                    model.Add(conn_y == py_rotated).OnlyEnforceIf(rotated, pos_bool)

                    # Ensure conn_x and conn_y are not constrained when pos_bool is False
                    model.Add(conn_x != px_non_rotated).OnlyEnforceIf(pos_bool.Not())
                    model.Add(conn_y != py_non_rotated).OnlyEnforceIf(pos_bool.Not())
                    model.Add(conn_x != px_rotated).OnlyEnforceIf(pos_bool.Not())
                    model.Add(conn_y != py_rotated).OnlyEnforceIf(pos_bool.Not())
                else:
                    raise ValueError(f"unknown position {pos}")
        model.add_exactly_one(pos_bools)
        return conns_x, conns_y, pos_bools

        # rotated_position = get_rotated_position(pos, is_rotated)

        # if rotated_position == "LM" or rotated_position == "ML":
            # return x, model.NewIntVar(0, grid_size[1], f'{name}_{rotated_position}_y')
        # elif rotated_position == "TR" or rotated_position == "RT":
            # x_tr = model.NewIntVar(0, grid_size[0], f'{name}_{rotated_position}_x')
            # model.Add(x_tr == x + width)
            # return x_tr, y
        # elif rotated_position == "BL":
            # y_bl = model.NewIntVar(0, grid_size[1], f'{name}_{rotated_position}_y')
            # model.Add(y_bl == y + height)
            # return x, y_bl
        # elif rotated_position == "TL" or rotated_position == "LT":
            # return x, y
        # elif rotated_position == "BR":
            # x_br = model.NewIntVar(0, grid_size[0], f'{name}_{rotated_position}_x')
            # y_br = model.NewIntVar(0, grid_size[1], f'{name}_{rotated_position}_y')
            # model.Add(x_br == x + width)
            # model.Add(y_br == y + height)
            # return x_br, y_br
        # elif rotated_position == "RM" or rotated_position == "MR":
            # x_rm = model.NewIntVar(0, grid_size[0], f'{name}_{rotated_position}_x')
            # model.Add(x_rm == x + width)
            # return x_rm, model.NewIntVar(0, grid_size[1], f'{name}_{rotated_position}_y')
        # elif rotated_position == "TM":
            # return model.NewIntVar(0, grid_size[0], f'{name}_{rotated_position}_x'), y
        # elif rotated_position == "BM":
            # y_bm = model.NewIntVar(0, grid_size[1], f'{name}_{rotated_position}_y')
            # model.Add(y_bm == y + height)
            # return model.NewIntVar(0, grid_size[0], f'{name}_{rotated_position}_x'), y_bm
        # elif rotated_position == "MM":  # Default to center
            # return model.NewIntVar(0, grid_size[0], f'{name}_{rotated_position}_x'), model.NewIntVar(0, grid_size[1], f'{name}_{rotated_position}_y')
        # else:
            # raise KeyError(f"Unknown rotated_positionition {rotated_position}, double check variable entry")

    total_weighted_distance = model.NewIntVar(0, grid_size[0] * grid_size[1] * len(connections) * 100, 'total_weighted_distance')
    model.add_hint(total_weighted_distance, 55000)

    weighted_distances = []
    unweighted_distances = []
    connection_infos = []  # Store connection information
    debug_vars = []  # Store variables for debugging
    connection_details = []
    pos_bools = []

    for conn in connections:
        combination_vars = []
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

        (no_rotation1, rotated1) = rotations[name1]
        (no_rotation2, rotated2) = rotations[name2]

        starts_x, starts_y, pos_bools_start = get_connection_point(model, name1, 'start', pos1, x1, y1, w1, h1, no_rotation1, rotated1)
        ends_x, ends_y, ends_pos_bools = get_connection_point(model, name2, 'end', pos2, x2, y2, w2, h2, no_rotation2, rotated2)
        pos_bools.extend(pos_bools_start)
        pos_bools.extend(ends_pos_bools)

        start_indices = range(len(starts_x))
        end_indices = range(len(ends_x))

        for (start_index, start_x, start_y), (end_index, end_x, end_y) in product(
                zip(start_indices, starts_x, starts_y),
                zip(end_indices, ends_x, ends_y)
            ):

            # Create a boolean variable for this combination
            combination_var = model.new_bool_var(f'use_connection_{name1}_to_{name2}_{start_x}_{start_y}_to_{end_x}_{end_y}')
            start_combo_activated = pos_bools_start[start_index]
            end_combo_activated = ends_pos_bools[end_index]

            model.Add(combination_var <= start_combo_activated)
            model.Add(combination_var <= end_combo_activated)
            model.Add(combination_var >= start_combo_activated + end_combo_activated - 1)

            # Create variables and constraints for this combination
            dx = model.NewIntVar(-grid_size[0], grid_size[0], f'dx_{name1}_{name2}_{start_x}_{start_y}_{end_x}_{end_y}')
            dy = model.NewIntVar(-grid_size[1], grid_size[1], f'dy_{name1}_{name2}_{start_x}_{start_y}_{end_x}_{end_y}')

            model.Add(dx == end_x - start_x)
            model.Add(dy == end_y - start_y)

            abs_dx = model.NewIntVar(0, grid_size[0], f'abs_dx_{name1}_{name2}_{start_x}_{start_y}_{end_x}_{end_y}')
            abs_dy = model.NewIntVar(0, grid_size[1], f'abs_dy_{name1}_{name2}_{start_x}_{start_y}_{end_x}_{end_y}')

            # Replace AddAbsEquality with equivalent constraints
            model.Add(abs_dx >= dx)
            model.Add(abs_dx >= -dx)
            model.Add(abs_dy >= dy)
            model.Add(abs_dy >= -dy)


            manhattan_distance = model.NewIntVar(0, grid_size[0] + grid_size[1], f'manhattan_dist_{name1}_{name2}_{start_x}_{start_y}_{end_x}_{end_y}')

            model.Add(manhattan_distance == abs_dx + abs_dy).OnlyEnforceIf(combination_var)
            model.Add(manhattan_distance == 0).OnlyEnforceIf(combination_var.Not())

            # if name2 == "Red Circuit - RCU":
                # print(f"start_x: {start_x}")
                # print(f"end_x: {end_x}")
                # print(f"start_y: {start_y}")
                # print(f"end_y: {end_y}")
                # print()
                # rcu_constraints.add(combination_var)

            weighted_distance = model.NewIntVar(0, (grid_size[0] + grid_size[1]) * weight, f'weighted_dist_{name1}_{name2}_{start_x}_{start_y}_{end_x}_{end_y}')
            model.AddMultiplicationEquality(weighted_distance, manhattan_distance, weight)

            combination_vars.append(combination_var)
            # if name2 == "Red Circuit - RCU":
                # combo_vars.append(combination_var)
                # combo_vars.append(abs_dx)
                # combo_vars.append(abs_dy)
                # combo_vars.append(manhattan_distance)
                # combo_vars.append(weighted_distance)
            connection_details.append((combination_var, name1, name2, start_x, start_y, end_x, end_y))
            weighted_distances.append(weighted_distance)

        # Ensure exactly one combination is chosen
        model.AddExactlyOne(combination_vars)

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
    # print(model.Proto())
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time
    solver.parameters.num_search_workers = 16
    solver.parameters.log_search_progress = True
    solver.parameters.log_subsolver_statistics = True
    # solver.parameters.extra_subsolvers.append("lb_tree_search")
    # solver.parameters.ignore_subsolvers.append("reduced_costs")
    # solver.parameters.ignore_subsolvers.append("pseudo_costs")
    # solver.parameters.ignore_subsolvers.append("objective_shaving_search_max_lp")
    # solver.parameters.ignore_subsolvers.append("objective_shaving_search_no_lp")
    # solver.parameters.ignore_subsolvers.append("default_lp")
    # solver.parameters.optimize_with_lb_tree_search = True
    # solver.parameters.use_strong_propagation_in_disjunctive = True
    # solver.parameters.use_area_energetic_reasoning_in_no_overlap_2d = True
    # solver.parameters.use_energetic_reasoning_in_no_overlap_2d = True
    # solver.parameters.max_pairs_pairwise_reasoning_in_no_overlap_2d = True
    solver.parameters.randomize_search = True
    solver.parameters.random_seed = random.randint(0, 10000)  # Add randomness
    # solver.parameters.optimize_with_core = True
    # solver.parameters.optimize_with_lb_tree_search = True

    solution_printer = VarArraySolutionPrinter(all_vars)
    best_seen = None
    best_positions = None
    best_connection_details = None
    best_solver = None
    status = solver.Solve(model, solution_printer)

    print(f"Solver status: {solver.StatusName(status)}")
    if status == cp_model.INFEASIBLE:
        constraints = model.Proto().constraints
        print(f"assumptions leading to infeasibility: {solver.SufficientAssumptionsForInfeasibility()}")

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        total_weighted_distance_value = solver.Value(total_weighted_distance)
        if best_seen is None or total_weighted_distance_value < best_seen:
            best_solver = solver
            best_seen = total_weighted_distance_value
            best_positions = { name: (
                solver.Value(pos[0]),
                solver.Value(pos[1]),
                solver.BooleanValue(rotations[name][1]),
            ) for name, pos in positions.items() }
            best_connection_details = connection_details

        for bol in pos_bools:
            # if solver.BooleanValue(bol):
                # print(bol)
            # else:
                # print(f"not chosen: {bol}")
            pass

        for connection in connection_details:
            pass
            # print(f"connection: {connection}")
            # if solver.BooleanValue(connection[0]):
                # chosen_connections.append({
                    # 'start_x': solver.Value(connection[1]),
                    # 'start_y': solver.Value(connection[2]),
                    # 'end_x': solver.Value(connection[3]),
                    # 'end_y': solver.Value(connection[4])
                # })

        total_unweighted_distance = sum(solver.Value(d) for d in unweighted_distances)

        """
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
        """

    return best_solver, best_positions, best_seen, best_connection_details


def get_rotated_position(pos, is_rotated):
    """
    Rotate the connection position if the block is rotated.
    """
    if not is_rotated:
        return pos

    rotation_map = {
        "TL": "TR", "TM": "RM", "TR": "BR",
        "ML": "TM", "MM": "MM", "MR": "BM",
        "BL": "TL", "BM": "LM", "BR": "BL",
        "LT": "RT", "LM": "TM", "LB": "LT",
        "RT": "RB", "RM": "BM", "RB": "LB"
    }
    return rotation_map.get(pos, pos)

def get_connection_point(x, y, width, height, position, is_rotated):
    position = get_rotated_position(position, is_rotated)
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

def get_chosen_connections(solver, connection_details):
    chosen_connections = []
    for connection in connection_details:
        # print(f"connection: {connection}")
        if solver.BooleanValue(connection[0]):
            chosen_connections.append({
                'start_x': solver.Value(connection[3]),
                'start_y': solver.Value(connection[4]),
                'end_x': solver.Value(connection[5]),
                'end_y': solver.Value(connection[6])
            })
    return chosen_connections

def visualize_layout(solver, blocks, connection_details, optimal_positions, grid_size, total_distance):
    # for val in rcu_constraints:
        # print(val)
        # print(solver.Value(val))
    # print("combo_vars ===============================")
    # for var in combo_vars:
        # print(var)
        # print(solver.Value(var))
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
        # while len(wrapped_text) > 1:
            # estimated_height = estimate_text_height('\n'.join(wrapped_text), font_prop, width * 0.9)
            # if estimated_height <= height * 0.9:
                # break
            # wrapped_text = wrapped_text[:-1]
            # wrapped_text[-1] += '...'
            # best_text.set_text('\n'.join(wrapped_text))

    # Draw connections
    chosen_conns = get_chosen_connections(solver, connection_details)
    for conn in chosen_conns:
        start_x, start_y, end_x, end_y = conn['start_x'], conn['start_y'], conn['end_x'], conn['end_y']
        """
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
        start_x, start_y = get_connection_point(x1, y1, w1, h1, pos1, is_rotated1)
        end_x, end_y = get_connection_point(x2, y2, w2, h2, pos2, is_rotated2)
        """

        # Calculate vector and shorten the end point
        dx, dy = end_x - start_x, end_y - start_y
        # length = math.sqrt(dx**2 + dy**2)
        # shorten_factor = 5  # Pixels to shorten by
        # if length > shorten_factor:
            # end_x -= (dx / length) * shorten_factor
            # end_y -= (dy / length) * shorten_factor

        # Draw the arrow
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle='->', color='#FF9999', lw=1),
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
    parser.add_argument("--runs", type=int, default=5, help="Number of runs")
    args = parser.parse_args()

    if args.fast:
        max_time = 15
        runs = 1
    else:
        max_time = args.time
        runs = args.runs

    # print("Attempting to solve with rotation...")
    print(f"blocks: {blocks}")
    best_positions = None
    best_total_distance = None
    best_solver = None
    best_connection_details = None
    for i in range(runs):
        solver, optimal_positions, total_distance, connection_details = optimize_factory_layout(blocks, connections, grid_size, max_time / runs, allow_rotation=True)
        if best_total_distance is None or total_distance < best_total_distance:
            best_total_distance = total_distance
            best_positions = optimal_positions
            best_solver = solver
            best_connection_details = connection_details

    if best_positions:
        for name, (x, y, is_rotated) in best_positions.items():
            print(f"{name}: position ({x}, {y}), {'rotated' if is_rotated else 'not rotated'}")
        visualize_layout(best_solver, blocks, best_connection_details, best_positions, grid_size, best_total_distance)
    else:
        print("No solution found in either attempt.")

if __name__ == "__main__":
    main()
